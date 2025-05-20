import unittest
from unittest.mock import patch, MagicMock, call
from PIL import Image, ImageDraw, ImageFont
import os
import sys
import shutil # For rmtree

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from preview_creator import create_preview_with_watermark, draw_double_arrowed_line # draw_double_arrowed_line is also in preview_creator
from utils import PIXELS_PER_INCH, PHOTO_SIZE_PIXELS

class TestPreviewCreator(unittest.TestCase):

    def setUp(self):
        self.base_dir = 'test_temp_files'
        self.dummy_image_folder = os.path.join(self.base_dir, 'uploads')
        self.dummy_preview_folder = os.path.join(self.base_dir, 'previews')
        self.dummy_fonts_folder = os.path.join(self.base_dir, 'fonts')

        os.makedirs(self.dummy_image_folder, exist_ok=True)
        os.makedirs(self.dummy_preview_folder, exist_ok=True)
        os.makedirs(self.dummy_fonts_folder, exist_ok=True)

        self.dummy_image_path = os.path.join(self.dummy_image_folder, 'test_image.jpg')
        self.dummy_preview_path = os.path.join(self.dummy_preview_folder, 'test_preview.jpg')
        
        # Create a dummy 600x600 image
        img = Image.new('RGB', (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS), color='red')
        img.save(self.dummy_image_path)

        self.crop_data = {
            'head_height': 1.2,      # inches
            'eye_to_bottom': 1.25,   # inches
            # 'eye_level': 250       # Not directly used by current preview_creator logic, derived from eye_to_bottom
        }
        self.mock_face_landmarks = MagicMock() # Not used by current preview_creator logic for drawing measurements
        self.arial_font_path = os.path.join(self.dummy_fonts_folder, 'Arial.ttf')
        
        # Create a dummy font file to allow ImageFont.truetype to not fail immediately if not mocked sometimes
        # Though the plan is to mock it. This is a fallback.
        try:
            with open(self.arial_font_path, 'w') as f:
                f.write("dummy font")
        except IOError:
            pass


    def tearDown(self):
        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)

    @patch('preview_creator.ImageFont.truetype')
    @patch('preview_creator.ImageDraw.Draw')
    @patch('preview_creator.Image.open')
    @patch('preview_creator.Image.new') # Patch Image.new used for canvas and watermark overlay
    def test_basic_preview_creation(self, mock_image_new, mock_image_open, mock_draw_constructor, mock_font_truetype):
        # Setup Mocks
        mock_input_image = MagicMock(spec=Image.Image)
        mock_input_image.size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS)
        mock_input_image.mode = 'RGB'
        mock_image_open.return_value = mock_input_image

        mock_canvas_image = MagicMock(spec=Image.Image)
        mock_canvas_image.size = (int(PHOTO_SIZE_PIXELS * 1.4), int(PHOTO_SIZE_PIXELS * 1.4)) # Approximate based on margins
        mock_canvas_image.mode = 'RGBA'
        
        mock_watermark_overlay = MagicMock(spec=Image.Image)
        mock_watermark_overlay.mode = 'RGBA'
        
        # Image.new is called for canvas then for watermark_overlay
        mock_image_new.side_effect = [mock_canvas_image, mock_watermark_overlay]


        mock_draw_canvas = MagicMock(spec=ImageDraw.ImageDraw)
        mock_draw_watermark = MagicMock(spec=ImageDraw.ImageDraw)
        mock_draw_constructor.side_effect = [mock_draw_canvas, mock_draw_watermark, mock_draw_canvas] # Draw on canvas, then overlay, then canvas again

        mock_font = MagicMock(spec=ImageFont.FreeTypeFont)
        mock_font_truetype.return_value = mock_font

        # Call the function
        create_preview_with_watermark(
            self.dummy_image_path,
            self.dummy_preview_path,
            self.crop_data,
            self.mock_face_landmarks,
            self.dummy_fonts_folder
        )

        # Assertions
        mock_image_open.assert_called_once_with(self.dummy_image_path)

        # Canvas creation
        expected_canvas_width = PHOTO_SIZE_PIXELS + int(PHOTO_SIZE_PIXELS * 0.2) * 2 # margin_left + margin_right
        expected_canvas_height = PHOTO_SIZE_PIXELS + int(PHOTO_SIZE_PIXELS * 0.2) * 2 # margin_top + margin_bottom
        
        # Check call for canvas
        mock_image_new.assert_any_call('RGBA', (expected_canvas_width, expected_canvas_height), 'white')
        
        # Image paste
        margin_left = int(PHOTO_SIZE_PIXELS * 0.2)
        margin_top = int(PHOTO_SIZE_PIXELS * 0.2)
        mock_canvas_image.paste.assert_called_once_with(mock_input_image, (margin_left, margin_top))
        
        # Draw constructor calls
        self.assertIn(call(mock_canvas_image), mock_draw_constructor.call_args_list)
        self.assertIn(call(mock_watermark_overlay), mock_draw_constructor.call_args_list)

        # Watermark overlay creation
        mock_image_new.assert_any_call('RGBA', mock_canvas_image.size, (255,255,255,0))

        # Alpha composite for watermarks
        mock_canvas_image.alpha_composite.assert_called_once_with(mock_watermark_overlay)

        # Save call
        mock_canvas_image.convert.assert_called_once_with('RGB')
        # The object that convert is called on is the result of alpha_composite,
        # so we assume mock_canvas_image is what's ultimately saved after being updated by alpha_composite.
        # If alpha_composite returns a new image, then that new image's convert/save should be checked.
        # Let's assume alpha_composite modifies mock_canvas_image in place or returns it.
        # If create_preview_with_watermark reassigns `preview = Image.alpha_composite(...)`, then need to get that object.
        # For now, let's assume the mock_canvas_image is the one saved.
        # This might need adjustment based on actual return value of Image.alpha_composite if it wasn't mocked to return self.
        
        # To handle the preview variable reassignment:
        # If Image.alpha_composite is not mocked, it returns a new Image object.
        # Let's mock it to control its return value for robust testing.
        mock_final_preview_image = MagicMock(spec=Image.Image)
        mock_canvas_image.alpha_composite.return_value = mock_final_preview_image

        # Re-run with this refinement (not actually re-running, just noting for the assertion)
        # Then the assertions for convert and save should be on mock_final_preview_image
        # For this first pass, I'll assume the original mock_canvas_image has these methods called
        # and refine if the test structure makes it difficult.
        # The current code is: preview = Image.alpha_composite(preview, watermark_overlay)
        # So, convert and save are called on the result of alpha_composite.

        # Let's refine the mock_canvas_image to handle this.
        # It's simpler if mock_canvas_image.alpha_composite returns itself or the mock_final_preview_image.
        # The current mock_canvas_image.alpha_composite is a MagicMock by default.
        
        # Assert convert and save on the object returned by alpha_composite
        returned_from_alpha_composite = mock_canvas_image.alpha_composite.return_value 
        returned_from_alpha_composite.convert.assert_called_once_with('RGB')
        returned_from_alpha_composite.save.assert_called_once_with(self.dummy_preview_path, quality=95)

    @patch('preview_creator.ImageFont.load_default') # Mock load_default for the fallback test
    @patch('preview_creator.ImageFont.truetype')
    @patch('preview_creator.ImageDraw.Draw')
    @patch('preview_creator.Image.open')
    @patch('preview_creator.Image.new')
    def test_watermark_placement_and_font_loading(self, mock_image_new, mock_image_open, mock_draw_constructor, mock_font_truetype, mock_font_load_default):
        # --- Setup Mocks (similar to basic test) ---
        mock_input_image = MagicMock(spec=Image.Image)
        mock_input_image.size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS)
        mock_input_image.mode = 'RGB'
        mock_image_open.return_value = mock_input_image

        mock_canvas_image = MagicMock(spec=Image.Image)
        canvas_width = PHOTO_SIZE_PIXELS + int(PHOTO_SIZE_PIXELS * 0.2) * 2
        canvas_height = PHOTO_SIZE_PIXELS + int(PHOTO_SIZE_PIXELS * 0.2) * 2
        mock_canvas_image.size = (canvas_width, canvas_height)
        mock_canvas_image.mode = 'RGBA'
        
        mock_watermark_overlay = MagicMock(spec=Image.Image)
        mock_watermark_overlay.mode = 'RGBA'
        mock_image_new.side_effect = [mock_canvas_image, mock_watermark_overlay] # Canvas, then Watermark Overlay

        mock_draw_canvas = MagicMock(spec=ImageDraw.ImageDraw)
        mock_draw_watermark = MagicMock(spec=ImageDraw.ImageDraw)
        # Order of Draw creation: 1. On canvas (for image paste), 2. On watermark_overlay, 3. On canvas again (after alpha_composite, for measurements)
        mock_draw_constructor.side_effect = [mock_draw_canvas, mock_draw_watermark, mock_draw_canvas]

        mock_font_instance = MagicMock(spec=ImageFont.FreeTypeFont)
        mock_font_truetype.return_value = mock_font_instance
        mock_font_load_default.return_value = MagicMock(spec=ImageFont.ImageFont) # For fallback

        # --- Call the function ---
        create_preview_with_watermark(
            self.dummy_image_path, self.dummy_preview_path, self.crop_data,
            self.mock_face_landmarks, self.dummy_fonts_folder
        )

        # --- Assertions for Font Loading ---
        expected_watermark_font_size = int(canvas_width * 0.05)
        expected_measurement_font_size = int(canvas_width * 0.03)
        
        font_calls = [
            call(self.arial_font_path, expected_watermark_font_size),
            call(self.arial_font_path, expected_measurement_font_size)
        ]
        mock_font_truetype.assert_has_calls(font_calls, any_order=True)

        # --- Assertions for Watermark Text ---
        # Watermarks are drawn on mock_draw_watermark
        watermark_text = "PREVIEW"
        watermark_opacity = 128 
        watermark_fill = (0, 0, 0, watermark_opacity)
        
        # Check that text was called multiple times (exact number of watermarks = 6)
        self.assertEqual(mock_draw_watermark.text.call_count, 6)
        
        # Check a sample call to ensure parameters are correct
        # The positions are calculated, so we check other params on any call
        mock_draw_watermark.text.assert_any_call(
            unittest.mock.ANY, # Position can be ANY for this check
            watermark_text,
            fill=watermark_fill,
            font=mock_font_instance,
            anchor='mm'
        )

        # --- Test Font Fallback ---
        mock_font_truetype.reset_mock()
        mock_font_load_default.reset_mock()
        mock_draw_watermark.reset_mock() # Reset for text calls
        mock_draw_canvas.reset_mock() # Reset for measurement text calls which also use font
        
        # Simulate IOError for both font loading attempts
        mock_font_truetype.side_effect = IOError("Font file not found")

        create_preview_with_watermark(
            self.dummy_image_path, self.dummy_preview_path, self.crop_data,
            self.mock_face_landmarks, self.dummy_fonts_folder
        )
        
        # Assert load_default was called (once for watermark_font, once for measurement_font)
        self.assertEqual(mock_font_load_default.call_count, 2, "ImageFont.load_default should be called twice on IOError.")
        
        # Check that text was still called for watermarks, but with the default font
        default_font_instance = mock_font_load_default.return_value
        mock_draw_watermark.text.assert_any_call(
            unittest.mock.ANY, watermark_text,
            fill=watermark_fill, font=default_font_instance, anchor='mm'
        )
        # Also check for measurement text call with default font (on mock_draw_canvas)
        # The measurement text content will be checked in another test, here just font usage.
        mock_draw_canvas.text.assert_any_call(
            unittest.mock.ANY, unittest.mock.ANY, # Pos and text can be any
            fill=(0,0,0,255), font=default_font_instance # Measurement text color and default font
        )

    @patch('preview_creator.ImageFont.truetype') # Mock font loading
    @patch('preview_creator.ImageDraw.Draw')
    @patch('preview_creator.Image.open')
    @patch('preview_creator.Image.new')
    def test_measurement_lines_drawing(self, mock_image_new, mock_image_open, mock_draw_constructor, mock_font_truetype):
        # --- Setup Mocks ---
        mock_input_image = MagicMock(spec=Image.Image)
        mock_input_image.size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS) # 600x600
        mock_input_image.mode = 'RGB'
        mock_image_open.return_value = mock_input_image

        mock_canvas_image = MagicMock(spec=Image.Image)
        canvas_width = PHOTO_SIZE_PIXELS + int(PHOTO_SIZE_PIXELS * 0.2) * 2
        canvas_height = PHOTO_SIZE_PIXELS + int(PHOTO_SIZE_PIXELS * 0.2) * 2
        mock_canvas_image.size = (canvas_width, canvas_height)
        mock_canvas_image.mode = 'RGBA'
        
        mock_watermark_overlay = MagicMock(spec=Image.Image)
        mock_image_new.side_effect = [mock_canvas_image, mock_watermark_overlay]

        mock_draw_instance = MagicMock(spec=ImageDraw.ImageDraw)
        # ImageDraw.Draw is called for: 1. main canvas, 2. watermark overlay, 3. main canvas again for measurements
        mock_draw_constructor.side_effect = [MagicMock(), MagicMock(), mock_draw_instance] 

        mock_font_instance = MagicMock(spec=ImageFont.FreeTypeFont)
        mock_font_truetype.return_value = mock_font_instance
        
        # For text size calculation within draw_double_arrowed_line
        # It tries draw.textbbox first, then falls back to draw.textsize
        if hasattr(mock_draw_instance, 'textbbox'):
            mock_draw_instance.textbbox.return_value = (0,0,50,10) # l,t,r,b for a dummy text
        else:
            mock_draw_instance.textsize.return_value = (50,10) # w,h for a dummy text


        # --- Test Data ---
        test_crop_data = {
            'head_height': 1.25,  # inches
            'eye_to_bottom': 1.125, # inches
        }

        # --- Call the function ---
        create_preview_with_watermark(
            self.dummy_image_path, self.dummy_preview_path, test_crop_data,
            self.mock_face_landmarks, self.dummy_fonts_folder
        )

        # --- Calculate Expected Coordinates (as done in the function) ---
        img_photo_height = PHOTO_SIZE_PIXELS # 600
        img_photo_width = PHOTO_SIZE_PIXELS  # 600
        margin_top = int(img_photo_height * 0.2)
        margin_left = int(img_photo_width * 0.2)

        eye_level_from_bottom_photo_px = test_crop_data['eye_to_bottom'] * PIXELS_PER_INCH
        y_eye_on_photo = img_photo_height - eye_level_from_bottom_photo_px

        head_height_pixels_on_photo = test_crop_data['head_height'] * PIXELS_PER_INCH
        
        proportion_head_above_eyes = 0.45 
        y_head_top_on_photo = y_eye_on_photo - (head_height_pixels_on_photo * proportion_head_above_eyes)
        y_chin_on_photo = y_head_top_on_photo + head_height_pixels_on_photo

        y_head_top_canvas = margin_top + y_head_top_on_photo
        y_eye_canvas = margin_top + y_eye_on_photo
        y_chin_canvas = margin_top + y_chin_on_photo
        y_photo_bottom_canvas = margin_top + img_photo_height

        x_horizontal_lines_start = margin_left + int(img_photo_width * 0.1)
        x_horizontal_lines_end = margin_left + img_photo_width - int(img_photo_width * 0.1)
        
        x_measurement_arrows = margin_left + img_photo_width + int(int(img_photo_width * 0.2) * 0.25) # margin_right is also img_photo_width * 0.2

        line_color = (0, 0, 0, 255)
        line_width_horizontal = 2
        arrow_line_width = 2 # default in draw_double_arrowed_line
        arrow_size = 10      # default in draw_double_arrowed_line

        # --- Assertions for Horizontal Lines ---
        expected_calls_horizontal_lines = [
            call.line([(x_horizontal_lines_start, y_head_top_canvas), (x_horizontal_lines_end, y_head_top_canvas)], fill=line_color, width=line_width_horizontal),
            call.line([(x_horizontal_lines_start, y_eye_canvas), (x_horizontal_lines_end, y_eye_canvas)], fill=line_color, width=line_width_horizontal),
            call.line([(x_horizontal_lines_start, y_chin_canvas), (x_horizontal_lines_end, y_chin_canvas)], fill=line_color, width=line_width_horizontal),
        ]
        for expected_call in expected_calls_horizontal_lines:
            self.assertIn(expected_call, mock_draw_instance.method_calls)

        # --- Assertions for "Head Height" measurement arrow (via draw_double_arrowed_line) ---
        # Main vertical line
        self.assertIn(call.line([(x_measurement_arrows, y_head_top_canvas), (x_measurement_arrows, y_chin_canvas)], fill=line_color, width=arrow_line_width), mock_draw_instance.method_calls)
        # Arrowheads (top)
        self.assertIn(call.line([(x_measurement_arrows - arrow_size // 2, y_head_top_canvas + arrow_size), (x_measurement_arrows, y_head_top_canvas)], fill=line_color, width=arrow_line_width), mock_draw_instance.method_calls)
        self.assertIn(call.line([(x_measurement_arrows + arrow_size // 2, y_head_top_canvas + arrow_size), (x_measurement_arrows, y_head_top_canvas)], fill=line_color, width=arrow_line_width), mock_draw_instance.method_calls)
        # Arrowheads (bottom)
        self.assertIn(call.line([(x_measurement_arrows - arrow_size // 2, y_chin_canvas - arrow_size), (x_measurement_arrows, y_chin_canvas)], fill=line_color, width=arrow_line_width), mock_draw_instance.method_calls)
        self.assertIn(call.line([(x_measurement_arrows + arrow_size // 2, y_chin_canvas - arrow_size), (x_measurement_arrows, y_chin_canvas)], fill=line_color, width=arrow_line_width), mock_draw_instance.method_calls)
        # Text label for head height
        text_head_height = f"{test_crop_data['head_height']:.2f}\" Head"
        # Text position calculation is complex, so check core parameters
        found_head_height_text = any(
            c[0] == 'text' and c[1][1] == text_head_height and c[2].get('fill') == line_color and c[2].get('font') == mock_font_instance
            for c in mock_draw_instance.method_calls
        )
        self.assertTrue(found_head_height_text, f"Text call for '{text_head_height}' not found or parameters mismatch.")

        # --- Assertions for "Eye-Bottom" measurement arrow (via draw_double_arrowed_line) ---
        # Main vertical line
        self.assertIn(call.line([(x_measurement_arrows, y_eye_canvas), (x_measurement_arrows, y_photo_bottom_canvas)], fill=line_color, width=arrow_line_width), mock_draw_instance.method_calls)
        # Arrowheads (top) - for eye_canvas
        self.assertIn(call.line([(x_measurement_arrows - arrow_size // 2, y_eye_canvas + arrow_size), (x_measurement_arrows, y_eye_canvas)], fill=line_color, width=arrow_line_width), mock_draw_instance.method_calls)
        self.assertIn(call.line([(x_measurement_arrows + arrow_size // 2, y_eye_canvas + arrow_size), (x_measurement_arrows, y_eye_canvas)], fill=line_color, width=arrow_line_width), mock_draw_instance.method_calls)
        # Arrowheads (bottom) - for y_photo_bottom_canvas
        self.assertIn(call.line([(x_measurement_arrows - arrow_size // 2, y_photo_bottom_canvas - arrow_size), (x_measurement_arrows, y_photo_bottom_canvas)], fill=line_color, width=arrow_line_width), mock_draw_instance.method_calls)
        self.assertIn(call.line([(x_measurement_arrows + arrow_size // 2, y_photo_bottom_canvas - arrow_size), (x_measurement_arrows, y_photo_bottom_canvas)], fill=line_color, width=arrow_line_width), mock_draw_instance.method_calls)
        # Text label for eye-to-bottom
        text_eye_to_bottom = f"{test_crop_data['eye_to_bottom']:.2f}\" Eye-Bottom"
        found_eye_bottom_text = any(
            c[0] == 'text' and c[1][1] == text_eye_to_bottom and c[2].get('fill') == line_color and c[2].get('font') == mock_font_instance
            for c in mock_draw_instance.method_calls
        )
        self.assertTrue(found_eye_bottom_text, f"Text call for '{text_eye_to_bottom}' not found or parameters mismatch.")

    @patch('preview_creator.ImageFont.truetype') # Mock font loading
    @patch('preview_creator.ImageDraw.Draw')
    @patch('preview_creator.Image.open')
    @patch('preview_creator.Image.new')
    def test_measurement_text_content(self, mock_image_new, mock_image_open, mock_draw_constructor, mock_font_truetype):
        # --- Setup Mocks ---
        mock_input_image = MagicMock(spec=Image.Image)
        mock_input_image.size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS)
        mock_input_image.mode = 'RGB'
        mock_image_open.return_value = mock_input_image

        mock_canvas_image = MagicMock(spec=Image.Image)
        mock_canvas_image.size = (int(PHOTO_SIZE_PIXELS * 1.4), int(PHOTO_SIZE_PIXELS * 1.4))
        mock_canvas_image.mode = 'RGBA'
        
        mock_watermark_overlay = MagicMock(spec=Image.Image)
        mock_image_new.side_effect = [mock_canvas_image, mock_watermark_overlay]

        mock_draw_instance = MagicMock(spec=ImageDraw.ImageDraw)
        mock_draw_constructor.side_effect = [MagicMock(), MagicMock(), mock_draw_instance]

        mock_font_instance = MagicMock(spec=ImageFont.FreeTypeFont)
        mock_font_truetype.return_value = mock_font_instance
        
        if hasattr(mock_draw_instance, 'textbbox'):
            mock_draw_instance.textbbox.return_value = (0,0,50,10) 
        else:
            mock_draw_instance.textsize.return_value = (50,10)

        # --- Test Data with specific fractional values ---
        test_crop_data = {
            'head_height': 1.12345,  # inches
            'eye_to_bottom': 1.34567, # inches
        }

        # --- Call the function ---
        create_preview_with_watermark(
            self.dummy_image_path, self.dummy_preview_path, test_crop_data,
            self.mock_face_landmarks, self.dummy_fonts_folder
        )

        # --- Assertions for Text Content of Measurement Labels ---
        # Expected formatted text (to two decimal places)
        expected_text_head_height = f"{test_crop_data['head_height']:.2f}\" Head" # Should be "1.12" Head"
        expected_text_eye_to_bottom = f"{test_crop_data['eye_to_bottom']:.2f}\" Eye-Bottom" # Should be "1.35" Eye-Bottom"

        line_color = (0,0,0,255) # As used in the function for measurements

        # Check if draw.text was called with the correctly formatted head height text
        found_head_height_text_call = any(
            c.args[1] == expected_text_head_height and 
            c.kwargs.get('fill') == line_color and 
            c.kwargs.get('font') == mock_font_instance
            for c in mock_draw_instance.text.call_args_list
        )
        self.assertTrue(found_head_height_text_call, 
                        f"Formatted text call for '{expected_text_head_height}' not found or parameters mismatch. Calls: {mock_draw_instance.text.call_args_list}")

        # Check if draw.text was called with the correctly formatted eye-to-bottom text
        found_eye_to_bottom_text_call = any(
            c.args[1] == expected_text_eye_to_bottom and 
            c.kwargs.get('fill') == line_color and 
            c.kwargs.get('font') == mock_font_instance
            for c in mock_draw_instance.text.call_args_list
        )
        self.assertTrue(found_eye_to_bottom_text_call, 
                        f"Formatted text call for '{expected_text_eye_to_bottom}' not found or parameters mismatch. Calls: {mock_draw_instance.text.call_args_list}")


if __name__ == '__main__':
    unittest.main()
