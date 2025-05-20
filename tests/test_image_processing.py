import unittest
from unittest.mock import patch, MagicMock, call
import numpy as np
from PIL import Image
import os
import sys
import shutil # For rmtree
import cv2 # For imread, cvtColor in functions being tested

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from image_processing import VisaPhotoProcessor
from utils import PHOTO_SIZE_PIXELS, PIXELS_PER_INCH

# For type hinting and spec for MagicMock if needed, though instances are directly mocked
# from gfpgan import GFPGANer 
# import onnxruntime as ort
# import mediapipe as mp

class TestVisaPhotoProcessor(unittest.TestCase):

    def setUp(self):
        self.mock_gfpganer = MagicMock()
        self.mock_ort_session = MagicMock()
        self.mock_face_mesh = MagicMock()

        self.base_dir = 'test_temp_image_processing'
        self.dummy_input_folder = os.path.join(self.base_dir, 'uploads')
        self.dummy_processed_folder = os.path.join(self.base_dir, 'processed')
        self.dummy_preview_folder = os.path.join(self.base_dir, 'previews')
        self.dummy_fonts_folder = os.path.join(self.base_dir, 'fonts')

        for folder in [self.dummy_input_folder, self.dummy_processed_folder, self.dummy_preview_folder, self.dummy_fonts_folder]:
            os.makedirs(folder, exist_ok=True)

        self.input_path = os.path.join(self.dummy_input_folder, 'test_input.jpg')
        self.processed_path = os.path.join(self.dummy_processed_folder, 'test_processed.jpg')
        self.preview_path = os.path.join(self.dummy_preview_folder, 'test_preview.jpg')
        self.printable_path = os.path.join(self.dummy_processed_folder, 'test_printable.jpg')
        self.printable_preview_path = os.path.join(self.dummy_preview_folder, 'test_printable_preview.jpg')
        
        # Create a dummy input image file (needed for cv2.imread)
        # Using PIL to create, then cv2 can read it if needed, or we mock imread.
        dummy_pil_image = Image.new('RGB', (800, 600), 'black')
        dummy_pil_image.save(self.input_path)

        self.processor = VisaPhotoProcessor(
            input_path=self.input_path,
            processed_path=self.processed_path,
            preview_path=self.preview_path,
            printable_path=self.printable_path,
            printable_preview_path=self.printable_preview_path,
            fonts_folder=self.dummy_fonts_folder,
            gfpganer_instance=self.mock_gfpganer,
            ort_session_instance=self.mock_ort_session,
            face_mesh_instance=self.mock_face_mesh
        )

    def tearDown(self):
        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)

    @patch('image_processing.printable_creator.create_printable_preview')
    @patch('image_processing.printable_creator.create_printable_image')
    @patch('image_processing.preview_creator.create_preview_with_watermark')
    @patch('PIL.Image.Image.save') # To mock the save method of the processed PIL image
    @patch.object(VisaPhotoProcessor, '_enhance_image')
    @patch('image_processing.remove_background_and_make_white')
    @patch.object(VisaPhotoProcessor, '_crop_and_scale_image')
    @patch('image_processing.calculate_crop_dimensions')
    @patch('cv2.imread')
    @patch('os.path.getsize')
    def test_process_successful_run(self, mock_getsize, mock_cv2_imread, mock_calculate_crop, 
                                     mock_crop_scale, mock_remove_bg, mock_enhance, mock_pil_save,
                                     mock_create_preview, mock_create_printable, mock_create_printable_preview):
        
        # --- Configure Mocks ---
        mock_socketio = MagicMock()
        
        mock_img_cv_array = np.zeros((600, 800, 3), dtype=np.uint8) # Mock cv2.imread output
        mock_cv2_imread.return_value = mock_img_cv_array

        mock_face_results = MagicMock()
        mock_face_results.multi_face_landmarks = [MagicMock()] # Simulate one face found
        self.mock_face_mesh.process.return_value = mock_face_results

        mock_crop_data = {
            'head_height': 1.2, 'eye_to_bottom': 1.25, 'scale_factor': 1.0,
            'crop_top': 0, 'crop_bottom': 600, 'crop_left': 0, 'crop_right': 600
        }
        mock_calculate_crop.return_value = mock_crop_data

        mock_pil_img_after_crop = MagicMock(spec=Image.Image)
        mock_crop_scale.return_value = mock_pil_img_after_crop

        mock_pil_img_after_bg_remove = MagicMock(spec=Image.Image)
        mock_remove_bg.return_value = mock_pil_img_after_bg_remove

        mock_pil_img_after_enhance = MagicMock(spec=Image.Image)
        mock_enhance.return_value = mock_pil_img_after_enhance
        # PIL.Image.Image.save is directly patched, will be called on mock_pil_img_after_enhance

        mock_getsize.return_value = 500 * 1024 # 500 KB

        # --- Call the method under test ---
        photo_info = self.processor.process_with_updates(mock_socketio)

        # --- Assertions ---
        mock_cv2_imread.assert_called_once_with(self.input_path)
        self.mock_face_mesh.process.assert_called_once() # Check input array if needed (cv2.cvtColor(mock_img_cv_array, cv2.COLOR_BGR2RGB))
        
        # Get the actual numpy array passed to face_mesh.process
        actual_img_rgb_for_facemesh = self.mock_face_mesh.process.call_args[0][0]
        self.assertEqual(actual_img_rgb_for_facemesh.shape, mock_img_cv_array.shape)
        # cv2.cvtColor is not mocked, so it runs. Could check if a BGR vs RGB results in different first/last channel if needed.

        mock_calculate_crop.assert_called_once_with(
            mock_face_results.multi_face_landmarks[0], 
            mock_img_cv_array.shape[0], 
            mock_img_cv_array.shape[1]
        )
        mock_crop_scale.assert_called_once_with(mock_img_cv_array, mock_crop_data)
        mock_remove_bg.assert_called_once_with(mock_pil_img_after_crop, self.mock_ort_session)
        mock_enhance.assert_called_once_with(mock_pil_img_after_bg_remove)
        
        # Check save call on the mock object returned by _enhance_image
        mock_pil_img_after_enhance.save.assert_called_once_with(
            self.processed_path, dpi=(PIXELS_PER_INCH, PIXELS_PER_INCH), quality=95
        )

        mock_create_preview.assert_called_once_with(
            self.processed_path, self.preview_path, mock_crop_data, 
            mock_face_results.multi_face_landmarks[0], self.dummy_fonts_folder
        )
        mock_create_printable.assert_called_once_with(
            self.processed_path, self.printable_path, self.dummy_fonts_folder, rows=2, cols=2
        )
        mock_create_printable_preview.assert_called_once_with(
            self.processed_path, self.printable_preview_path, self.dummy_fonts_folder, rows=2, cols=2
        )

        # Assert photo_info structure
        self.assertEqual(photo_info['head_height'], round(mock_crop_data['head_height'], 2))
        self.assertEqual(photo_info['eye_to_bottom'], round(mock_crop_data['eye_to_bottom'], 2))
        self.assertEqual(photo_info['file_size_kb'], round(mock_getsize.return_value / 1024, 2))
        self.assertTrue(photo_info['compliance']['head_height']) # Based on mock_crop_data
        self.assertTrue(photo_info['compliance']['eye_to_bottom'])

        # Assert socketio calls
        expected_emits = [
            call('processing_status', {'status': 'Loading image'}),
            call('processing_status', {'status': 'Detecting face landmarks'}),
            call('processing_status', {'status': 'Calculating crop dimensions'}),
            call('processing_status', {'status': 'Cropping and scaling image'}),
            call('processing_status', {'status': 'Removing background'}),
            call('processing_status', {'status': 'Enhancing image'}),
            call('processing_status', {'status': 'Saving processed image'}),
            call('processing_status', {'status': 'Creating preview'}),
            call('processing_status', {'status': 'Creating printable image'}),
            call('processing_status', {'status': 'Creating printable preview'}),
            call('processing_status', {'status': 'Processing complete'}),
        ]
        mock_socketio.emit.assert_has_calls(expected_emits)

    @patch('cv2.imread') # Patch cv2.imread specifically for this test
    def test_process_no_face_detected(self, mock_cv2_imread_no_face):
        mock_socketio = MagicMock()
        
        mock_img_cv_array = np.zeros((600, 800, 3), dtype=np.uint8)
        mock_cv2_imread_no_face.return_value = mock_img_cv_array

        # Simulate no face landmarks found
        mock_face_results_no_face = MagicMock()
        mock_face_results_no_face.multi_face_landmarks = None # Key part for this test
        self.mock_face_mesh.process.return_value = mock_face_results_no_face

        with self.assertRaisesRegex(ValueError, "Не удалось обнаружить лицо. Пожалуйста, убедитесь, что лицо хорошо видно"):
            self.processor.process_with_updates(mock_socketio)
        
        # Ensure that socketio status for 'Detecting face landmarks' was emitted before failure
        mock_socketio.emit.assert_any_call('processing_status', {'status': 'Detecting face landmarks'})
        # Check that it didn't proceed much further (e.g. no crop calculation attempt)
        # This depends on where calculate_crop_dimensions is patched. If globally, it might not be called.
        # For this test, we primarily care about the ValueError.


    @patch('cv2.imread')
    def test_process_input_image_read_fail(self, mock_cv2_imread_fail):
        mock_socketio = MagicMock()
        mock_cv2_imread_fail.return_value = None # Simulate image read failure

        with self.assertRaisesRegex(ValueError, "Failed to read the uploaded image"):
            self.processor.process_with_updates(mock_socketio)

        # Ensure socketio status for 'Loading image' was emitted before failure
        mock_socketio.emit.assert_any_call('processing_status', {'status': 'Loading image'})

    # --- Tests for _crop_and_scale_image ---
    @patch('image_processing.utils.create_image_with_padding') # To check if padding is called
    def test_crop_and_scale_logic(self, mock_create_image_with_padding):
        # Input numpy array (simulating cv2 image)
        input_cv_img = np.random.randint(0, 255, size=(800, 1000, 3), dtype=np.uint8)
        
        # Define crop_data that requires scaling and cropping
        crop_data = {
            'scale_factor': 0.5, # Scale down
            'crop_top': 50,      # Top Y after scaling
            'crop_bottom': 350,  # Bottom Y after scaling (height = 300)
            'crop_left': 100,    # Left X after scaling
            'crop_right': 400    # Right X after scaling (width = 300)
        }
        # Scaled image size: 1000*0.5=500 width, 800*0.5=400 height
        # Cropped image size (from scaled): 300x300 (width x height)

        # If cropped is not PHOTO_SIZE_PIXELS (600), create_image_with_padding will be called.
        # In this case, 300x300 will be padded to 600x600.
        mock_padded_image = MagicMock(spec=Image.Image)
        mock_padded_image.size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS)
        mock_create_image_with_padding.return_value = mock_padded_image

        result_pil_img = self.processor._crop_and_scale_image(input_cv_img, crop_data)

        self.assertIsInstance(result_pil_img, Image.Image)
        
        # Check if create_image_with_padding was called, since our crop (300x300) != PHOTO_SIZE_PIXELS (600x600)
        mock_create_image_with_padding.assert_called_once()
        # The first argument to create_image_with_padding should be a PIL image of the cropped dimensions
        call_args_padding = mock_create_image_with_padding.call_args[0]
        pil_image_to_pad = call_args_padding[0]
        self.assertIsInstance(pil_image_to_pad, Image.Image)
        self.assertEqual(pil_image_to_pad.size, (crop_data['crop_right'] - crop_data['crop_left'], crop_data['crop_bottom'] - crop_data['crop_top']))

        # The result of _crop_and_scale_image should be the result from create_image_with_padding
        self.assertEqual(result_pil_img.size, (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS))
        self.assertIs(result_pil_img, mock_padded_image)

    def test_crop_and_scale_no_padding_needed(self):
        # Input numpy array
        input_cv_img = np.random.randint(0, 255, size=(1200, 1200, 3), dtype=np.uint8) # Large enough
        
        # Define crop_data that results in a PHOTO_SIZE_PIXELS crop directly
        crop_data = {
            'scale_factor': 0.5, # Scale to 600x600
            'crop_top': 0,
            'crop_bottom': 600, 
            'crop_left': 0,
            'crop_right': 600
        }
        # Scaled image size: 1200*0.5 = 600 width, 1200*0.5 = 600 height
        # Cropped image size (from scaled): 600x600

        with patch('image_processing.utils.create_image_with_padding') as mock_no_padding_call:
            result_pil_img = self.processor._crop_and_scale_image(input_cv_img, crop_data)
            mock_no_padding_call.assert_not_called() # Padding should not be called

        self.assertIsInstance(result_pil_img, Image.Image)
        self.assertEqual(result_pil_img.size, (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS))


    # --- Tests for _enhance_image ---
    def test_enhance_image_calls_gfpgan(self):
        mock_input_pil_image = MagicMock(spec=Image.Image)
        # Simulate properties that cv2.cvtColor(np.array(image)) would access
        mock_input_pil_image.size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS)
        mock_input_pil_image.mode = 'RGB' 
        # np.array(mock_input_pil_image) will work if it has basic PIL attributes liketobytes, mode, size

        mock_restored_cv2_array = np.zeros((PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS, 3), dtype=np.uint8)
        mock_restored_cv2_array[:,:,0] = 50 # Make it a bit different, e.g., blueish
        
        self.mock_gfpganer.enhance.return_value = (None, None, mock_restored_cv2_array)

        result_pil_img = self.processor._enhance_image(mock_input_pil_image)

        self.mock_gfpganer.enhance.assert_called_once()
        # Check the first argument passed to gfpganer.enhance (the numpy image)
        enhance_call_args = self.mock_gfpganer.enhance.call_args[0]
        input_array_to_enhance = enhance_call_args[0]
        self.assertIsInstance(input_array_to_enhance, np.ndarray)
        self.assertEqual(input_array_to_enhance.shape, (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS, 3))
        
        self.assertIsInstance(result_pil_img, Image.Image)
        self.assertEqual(result_pil_img.size, (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS))
        # Optionally, check content if necessary by converting result_pil_img back to array
        # result_array = np.array(result_pil_img)
        # self.assertTrue(np.array_equal(result_array, cv2.cvtColor(mock_restored_cv2_array, cv2.COLOR_BGR2RGB)))


if __name__ == '__main__':
    unittest.main()
