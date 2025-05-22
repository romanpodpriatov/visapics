import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from PIL import Image
import sys
import os

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from background_remover import remove_background_and_make_white
import onnxruntime as ort # For type hinting and spec for MagicMock

class TestBackgroundRemover(unittest.TestCase):

    def create_dummy_image(self, size=(300, 300), color1=(255, 0, 0), color2=None):
        """Helper to create a simple PIL Image."""
        img = Image.new('RGB', size, color1)
        if color2: # Create a two-color image if color2 is specified
            draw = ImageDraw.Draw(img)
            draw.rectangle([0, 0, size[0]//2, size[1]], fill=color1)
            draw.rectangle([size[0]//2, 0, size[0], size[1]], fill=color2)
        return img

    def test_remove_background_basic_flow(self):
        dummy_input_image = self.create_dummy_image(size=(300,300), color1='blue')
        
        mock_ort_session = MagicMock(spec=ort.InferenceSession)
        
        # Mock for ort_session.get_inputs()[0].name
        mock_input_meta = MagicMock()
        mock_input_meta.name = 'input_tensor_name'
        mock_ort_session.get_inputs.return_value = [mock_input_meta]
        
        # Mock output from ort_session.run
        # This should be the raw output before sigmoid, so logits
        # Let's make a mask that has clear foreground and background areas
        # Model input is 1024x1024
        logit_output = np.zeros((1, 1, 1024, 1024), dtype=np.float32)
        logit_output[:, :, :512, :] = -10  # Background (will be near 0 after sigmoid)
        logit_output[:, :, 512:, :] = 10   # Foreground (will be near 1 after sigmoid)
        mock_ort_session.run.return_value = [logit_output]

        # Call the function with default white background
        output_image = remove_background_and_make_white(dummy_input_image, mock_ort_session, target_color_rgb=(255,255,255))

        # Assertions
        mock_ort_session.run.assert_called_once()
        self.assertIsInstance(output_image, Image.Image)
        self.assertEqual(output_image.mode, 'RGB')
        self.assertEqual(output_image.size, dummy_input_image.size) # Should be same as original input

        # Check pixel values
        # Convert to numpy array for easier pixel checking
        output_array = np.array(output_image)
        
        # Background area (top half of original image, mapped from logit_output[:512,:])
        # The mask is resized from 1024x1024 to 300x300.
        # So, the top half of the 300x300 output should correspond to the top half of the 1024x1024 mask.
        top_half_output = output_array[:150, :, :]
        # Check if a significant portion of the top half is white
        # Taking a sample pixel from the middle of the top-left quadrant
        self.assertTrue(np.all(output_array[75, 75] == [255, 255, 255]), "Pixel in expected background area is not white.")

        # Foreground area (bottom half of original image)
        # Taking a sample pixel from the middle of the bottom-right quadrant
        # This pixel should NOT be white. It should be 'blue' from the original dummy image.
        # Exact color matching can be tricky due to resizing artifacts if any, but it should be close to blue.
        self.assertFalse(np.all(output_array[225, 225] == [255, 255, 255]), "Pixel in expected foreground area is white.")
        # A more lenient check for "not white"
        self.assertTrue(np.any(output_array[225, 225] != [255, 255, 255]), "Pixel in expected foreground area is white (checked with any).")

    @patch('PIL.Image.Image.resize') # Patch the resize method of Image instances
    def test_image_preprocessing_and_model_input(self, mock_image_resize):
        dummy_input_image_size = (200, 250) # Non-square, different from model input size
        dummy_input_image = self.create_dummy_image(size=dummy_input_image_size, color1='green')

        # Mock the return of resize to be an image of the target size, so rest of the function can proceed
        mock_resized_img = MagicMock(spec=Image.Image)
        mock_resized_img.size = (1024, 1024)
        mock_resized_img.mode = 'RGB' # Assume resize preserves mode or it's handled
        mock_image_resize.return_value = mock_resized_img
        
        mock_ort_session = MagicMock(spec=ort.InferenceSession)
        mock_input_meta = MagicMock()
        mock_input_meta.name = 'actual_input_name' # Should match what the code expects
        mock_ort_session.get_inputs.return_value = [mock_input_meta]
        
        # Dummy output for the model run
        logit_output = np.zeros((1, 1, 1024, 1024), dtype=np.float32)
        mock_ort_session.run.return_value = [logit_output]

        # Call the function with default white background
        remove_background_and_make_white(dummy_input_image, mock_ort_session, target_color_rgb=(255,255,255))

        # Assertions for preprocessing
        # 1. Check if input image was resized to (1024, 1024)
        mock_image_resize.assert_called_once_with((1024, 1024), Image.LANCZOS)
        
        # Assertions for model input
        # 2. Check ort_session.run was called
        mock_ort_session.run.assert_called_once()
        
        # 3. Check the input passed to ort_session.run
        # The first argument to 'run' is None (for all output names), 
        # the second is the input dictionary.
        call_args = mock_ort_session.run.call_args
        self.assertIsNotNone(call_args, "ort_session.run was not called with arguments.")
        
        input_feed_dict = call_args[0][1] # Get the input dictionary
        self.assertIn(mock_input_meta.name, input_feed_dict)
        model_input_array = input_feed_dict[mock_input_meta.name]
        
        self.assertIsInstance(model_input_array, np.ndarray)
        self.assertEqual(model_input_array.shape, (1, 3, 1024, 1024), "Model input array shape is incorrect.")
        self.assertEqual(model_input_array.dtype, np.float32, "Model input array dtype is incorrect.")

    def test_mask_processing_and_compositing(self):
        original_width, original_height = 200, 200
        color_left = (255, 0, 0)  # Red
        color_right = (0, 0, 255) # Blue
        
        # Create an image with left half red, right half blue
        dummy_input_image = Image.new('RGB', (original_width, original_height))
        draw = ImageDraw.Draw(dummy_input_image)
        draw.rectangle([0, 0, original_width // 2, original_height], fill=color_left)
        draw.rectangle([original_width // 2, 0, original_width, original_height], fill=color_right)

        mock_ort_session = MagicMock(spec=ort.InferenceSession)
        mock_input_meta = MagicMock()
        mock_input_meta.name = 'input_name'
        mock_ort_session.get_inputs.return_value = [mock_input_meta]

        # Prepare mock model output (logits)
        # Model's internal processing size is 1024x1024
        logit_values = np.zeros((1, 1024, 1024), dtype=np.float32) 
        # Left half of the mask should be background (low logit values -> close to 0 after sigmoid)
        logit_values[0, :, :512] = -10.0  # Strong background
        # Right half of the mask should be foreground (high logit values -> close to 1 after sigmoid)
        logit_values[0, :, 512:] = 10.0   # Strong foreground
        
        # The function expects ort_outs[0][0] to be the (1, H, W) logit mask
        mock_ort_session.run.return_value = [[logit_values]] 

        # Call the function with default white background
        output_image = remove_background_and_make_white(dummy_input_image, mock_ort_session, target_color_rgb=(255,255,255))

        # Assertions
        self.assertEqual(output_image.size, (original_width, original_height))
        self.assertEqual(output_image.mode, 'RGB')

        output_array = np.array(output_image)

        # Check left half of the output image (should be white)
        # Taking sample pixels from the left-center quarter
        sample_pixel_left_x = original_width // 4
        sample_pixel_left_y = original_height // 2
        self.assertTrue(np.all(output_array[sample_pixel_left_y, sample_pixel_left_x] == [255, 255, 255]),
                        f"Pixel ({sample_pixel_left_x},{sample_pixel_left_y}) in left half is not white: {output_array[sample_pixel_left_y, sample_pixel_left_x]}")

        # Check a few more pixels in the left half
        self.assertTrue(np.all(output_array[original_height // 4, original_width // 4] == [255, 255, 255]))
        self.assertTrue(np.all(output_array[3 * original_height // 4, original_width // 4] == [255, 255, 255]))


        # Check right half of the output image (should be original color_right - blue)
        # Taking sample pixels from the right-center quarter
        sample_pixel_right_x = original_width * 3 // 4
        sample_pixel_right_y = original_height // 2
        
        # Allow for minor differences due to image processing (e.g. alpha blending at edges)
        # For a strong foreground mask, it should be very close to original.
        self.assertTrue(np.allclose(output_array[sample_pixel_right_y, sample_pixel_right_x], color_right, atol=5),
                        f"Pixel ({sample_pixel_right_x},{sample_pixel_right_y}) in right half is not close to original blue {color_right}: {output_array[sample_pixel_right_y, sample_pixel_right_x]}")

        # Check a few more pixels in the right half
        self.assertTrue(np.allclose(output_array[original_height // 4, 3 * original_width // 4], color_right, atol=5))
        self.assertTrue(np.allclose(output_array[3 * original_height // 4, 3 * original_width // 4], color_right, atol=5))

    def test_remove_background_custom_color(self):
        custom_bg_color_rgb = (211, 211, 211) # Light grey
        foreground_color = (0, 128, 0) # Green

        dummy_input_image = self.create_dummy_image(size=(200,200), color1=foreground_color) # Single color foreground
        
        mock_ort_session = MagicMock(spec=ort.InferenceSession)
        mock_input_meta = MagicMock()
        mock_input_meta.name = 'input_tensor_name'
        mock_ort_session.get_inputs.return_value = [mock_input_meta]
        
        # Mask: top half background, bottom half foreground
        logit_output = np.zeros((1, 1, 1024, 1024), dtype=np.float32)
        logit_output[:, :, :512, :] = -10  # Background
        logit_output[:, :, 512:, :] = 10   # Foreground
        mock_ort_session.run.return_value = [logit_output]

        # Call the function with custom background color
        output_image = remove_background_and_make_white(dummy_input_image, mock_ort_session, target_color_rgb=custom_bg_color_rgb)

        # Assertions
        self.assertEqual(output_image.mode, 'RGB')
        self.assertEqual(output_image.size, dummy_input_image.size)

        output_array = np.array(output_image)
        
        # Check background area (top half) - should be custom_bg_color_rgb
        # Sample pixel from top-middle
        self.assertTrue(np.all(output_array[50, 100] == custom_bg_color_rgb), 
                        f"Pixel in expected background area is not custom color {custom_bg_color_rgb}. Got {output_array[50,100]}")

        # Check foreground area (bottom half) - should be foreground_color (green)
        # Sample pixel from bottom-middle
        self.assertTrue(np.allclose(output_array[150, 100], foreground_color, atol=5),
                        f"Pixel in expected foreground area is not original color {foreground_color}. Got {output_array[150,100]}")
        # Ensure it's not the background color
        self.assertFalse(np.all(output_array[150, 100] == custom_bg_color_rgb))


if __name__ == '__main__':
    # Need to import ImageDraw for the helper, but only if tests are run directly
    from PIL import ImageDraw 
    unittest.main()
