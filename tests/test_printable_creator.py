import unittest
from unittest.mock import patch, MagicMock, call
from PIL import Image, ImageDraw, ImageFont
import os
import sys
import shutil # For rmtree

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from printable_creator import create_printable_image, create_printable_preview, apply_watermark_to_photo
from utils import PIXELS_PER_INCH # Retain for fixed 4x6 canvas size logic
from photo_specs import PhotoSpecification # Import for type hinting and creating mock spec

# Helper to create a mock PhotoSpecification for printable tests
def create_mock_printable_spec(photo_width_mm=50.8, photo_height_mm=50.8, dpi=300):
    spec = MagicMock(spec=PhotoSpecification)
    spec.photo_width_mm = photo_width_mm
    spec.photo_height_mm = photo_height_mm
    spec.dpi = dpi
    spec.MM_PER_INCH = 25.4

    spec.photo_width_px = int(photo_width_mm / spec.MM_PER_INCH * dpi)
    spec.photo_height_px = int(photo_height_mm / spec.MM_PER_INCH * dpi)
    return spec

class TestPrintableCreator(unittest.TestCase):

    def setUp(self):
        self.base_dir = 'test_temp_printable_files'
        self.dummy_processed_folder = os.path.join(self.base_dir, 'processed')
        self.dummy_preview_folder = os.path.join(self.base_dir, 'previews')
        self.dummy_fonts_folder = os.path.join(self.base_dir, 'fonts')

        os.makedirs(self.dummy_processed_folder, exist_ok=True)
        os.makedirs(self.dummy_preview_folder, exist_ok=True)
        os.makedirs(self.dummy_fonts_folder, exist_ok=True)

        self.dummy_processed_image_path = os.path.join(self.dummy_processed_folder, 'processed_image.jpg')
        self.dummy_printable_image_path = os.path.join(self.dummy_processed_folder, 'printable_image.jpg')
        self.dummy_printable_preview_path = os.path.join(self.dummy_preview_folder, 'printable_preview.jpg')
        
        self.mock_spec_2x2_300dpi = create_mock_printable_spec(dpi=300) # 600x600px
        self.mock_spec_35x45_300dpi = create_mock_printable_spec(photo_width_mm=35, photo_height_mm=45, dpi=300)


        # Create a dummy image based on default spec for most tests
        img = Image.new('RGB', (self.mock_spec_2x2_300dpi.photo_width_px, self.mock_spec_2x2_300dpi.photo_height_px), color='blue')
        img.save(self.dummy_processed_image_path)

        self.arial_font_path = os.path.join(self.dummy_fonts_folder, 'Arial.ttf')
        try: 
            with open(self.arial_font_path, 'w') as f: f.write("dummy font")
        except IOError: pass

    def tearDown(self):
        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)

    # --- Tests for apply_watermark_to_photo ---
    @patch('printable_creator.ImageFont.load_default')
    @patch('printable_creator.ImageFont.truetype')
    @patch('printable_creator.ImageDraw.Draw')
    @patch('printable_creator.Image.alpha_composite') 
    @patch('printable_creator.Image.new') 
    def test_apply_watermark_photo_basic(self, mock_image_new_overlay, mock_alpha_composite, mock_draw_constructor, mock_font_truetype, mock_font_load_default):
        mock_input_image = MagicMock(spec=Image.Image)
        mock_input_image.size = (self.mock_spec_2x2_300dpi.photo_width_px, self.mock_spec_2x2_300dpi.photo_height_px)
        mock_input_image.mode = 'RGB'

        mock_rgba_image = MagicMock(spec=Image.Image)
        mock_input_image.copy.return_value.convert.return_value = mock_rgba_image
        mock_rgba_image.size = mock_input_image.size # Ensure size is propagated

        mock_overlay = MagicMock(spec=Image.Image)
        mock_image_new_overlay.return_value = mock_overlay 

        mock_draw = MagicMock(spec=ImageDraw.ImageDraw)
        mock_draw_constructor.return_value = mock_draw

        mock_font = MagicMock(spec=ImageFont.FreeTypeFont)
        mock_font_truetype.return_value = mock_font

        mock_composited_image = MagicMock(spec=Image.Image)
        mock_alpha_composite.return_value = mock_composited_image

        mock_final_rgb_image = MagicMock(spec=Image.Image)
        mock_composited_image.convert.return_value = mock_final_rgb_image
        
        result_image = apply_watermark_to_photo(mock_input_image, self.dummy_fonts_folder)

        mock_input_image.copy.assert_called_once()
        mock_input_image.copy.return_value.convert.assert_called_once_with('RGBA')
        
        mock_image_new_overlay.assert_called_once_with('RGBA', mock_rgba_image.size, (255,255,255,0))
        mock_draw_constructor.assert_called_once_with(mock_overlay)

        expected_font_size = int(mock_input_image.size[0] * 0.15) 
        mock_font_truetype.assert_called_once_with(self.arial_font_path, expected_font_size)
        
        mock_draw.text.assert_called_once_with(
            (mock_rgba_image.size[0] / 2, mock_rgba_image.size[1] / 2), 
            "PREVIEW", font=mock_font, fill=(0, 0, 0, 64), anchor='mm'
        )
        mock_alpha_composite.assert_called_once_with(mock_rgba_image, mock_overlay)
        mock_composited_image.convert.assert_called_once_with('RGB')
        self.assertEqual(result_image, mock_final_rgb_image)
        mock_font_load_default.assert_not_called()

    @patch('printable_creator.ImageFont.load_default')
    @patch('printable_creator.ImageFont.truetype')
    @patch('printable_creator.ImageDraw.Draw')
    @patch('printable_creator.Image.alpha_composite')
    @patch('printable_creator.Image.new')
    def test_apply_watermark_font_fallback(self, mock_image_new_overlay, mock_alpha_composite, mock_draw_constructor, mock_font_truetype, mock_font_load_default):
        mock_input_image = MagicMock(spec=Image.Image)
        mock_input_image.size = (self.mock_spec_2x2_300dpi.photo_width_px, self.mock_spec_2x2_300dpi.photo_height_px)
        mock_input_image.mode = 'RGB'
        mock_rgba_image = MagicMock(spec=Image.Image); mock_rgba_image.size = mock_input_image.size
        mock_input_image.copy.return_value.convert.return_value = mock_rgba_image
        mock_overlay = MagicMock(spec=Image.Image); mock_image_new_overlay.return_value = mock_overlay
        mock_draw = MagicMock(spec=ImageDraw.ImageDraw); mock_draw_constructor.return_value = mock_draw
        
        mock_font_truetype.side_effect = IOError("Font not found")
        mock_default_font = MagicMock(spec=ImageFont.ImageFont)
        mock_font_load_default.return_value = mock_default_font

        mock_composited_image = MagicMock(spec=Image.Image); mock_alpha_composite.return_value = mock_composited_image
        mock_final_rgb_image = MagicMock(spec=Image.Image); mock_composited_image.convert.return_value = mock_final_rgb_image

        result_image = apply_watermark_to_photo(mock_input_image, self.dummy_fonts_folder)

        expected_font_size = int(mock_input_image.size[0] * 0.15)
        mock_font_truetype.assert_called_once_with(self.arial_font_path, expected_font_size)
        mock_font_load_default.assert_called_once() 

        mock_draw.text.assert_called_once_with(
            (mock_rgba_image.size[0] / 2, mock_rgba_image.size[1] / 2),
            "PREVIEW", font=mock_default_font, fill=(0, 0, 0, 64), anchor='mm'
        )
        self.assertEqual(result_image, mock_final_rgb_image)

    # --- Tests for create_printable_image ---
    @patch('printable_creator.ImageDraw.Draw')
    @patch('printable_creator.Image.open')
    @patch('printable_creator.Image.new')
    def test_create_printable_image_layout_and_dpi(self, mock_image_new_canvas, mock_image_open, mock_draw_constructor):
        spec_to_test = self.mock_spec_35x45_300dpi # Use a non-default spec
        
        mock_input_photo = MagicMock(spec=Image.Image)
        # Assume input photo from processed_image_path already matches spec dimensions
        mock_input_photo.size = (spec_to_test.photo_width_px, spec_to_test.photo_height_px)
        mock_input_photo.mode = 'RGB'
        mock_image_open.return_value = mock_input_photo
        
        mock_canvas = MagicMock(spec=Image.Image)
        mock_image_new_canvas.return_value = mock_canvas
        mock_draw = MagicMock(spec=ImageDraw.ImageDraw); mock_draw_constructor.return_value = mock_draw

        rows, cols = 2, 2
        create_printable_image(
            self.dummy_processed_image_path, self.dummy_printable_image_path,
            self.dummy_fonts_folder, rows=rows, cols=cols, photo_spec=spec_to_test
        )

        mock_image_open.assert_called_once_with(self.dummy_processed_image_path)
        mock_input_photo.resize.assert_not_called() # Should not resize if size matches spec

        # Canvas is fixed at 4x6 inches @ 300 DPI (utils.PIXELS_PER_INCH)
        expected_canvas_width = 4 * PIXELS_PER_INCH 
        expected_canvas_height = 6 * PIXELS_PER_INCH
        mock_image_new_canvas.assert_called_once_with('RGB', (expected_canvas_width, expected_canvas_height), 'white')
        
        spacing = int(0.25 * PIXELS_PER_INCH)
        photo_w, photo_h = spec_to_test.photo_width_px, spec_to_test.photo_height_px
        
        total_photo_block_width = cols * photo_w + (cols - 1) * spacing
        total_photo_block_height = rows * photo_h + (rows - 1) * spacing
        start_x = (expected_canvas_width - total_photo_block_width) // 2
        start_y = (expected_canvas_height - total_photo_block_height) // 2

        expected_paste_calls = []
        for r_idx in range(rows):
            for c_idx in range(cols):
                x_pos = start_x + c_idx * (photo_w + spacing)
                y_pos = start_y + r_idx * (photo_h + spacing)
                expected_paste_calls.append(call(mock_input_photo, (x_pos, y_pos)))
        
        mock_canvas.paste.assert_has_calls(expected_paste_calls, any_order=False)
        self.assertEqual(mock_canvas.paste.call_count, rows * cols)

        mock_canvas.save.assert_called_once_with(
            self.dummy_printable_image_path, dpi=(spec_to_test.dpi, spec_to_test.dpi), quality=95
        )

    @patch('printable_creator.ImageDraw.Draw')
    @patch('printable_creator.Image.open')
    @patch('printable_creator.Image.new')
    def test_create_printable_image_resizes_input_if_needed(self, mock_image_new_canvas, mock_image_open, mock_draw_constructor):
        spec_to_test = self.mock_spec_2x2_300dpi # 600x600px target

        # Input photo is smaller than spec
        mock_opened_photo = MagicMock(spec=Image.Image)
        mock_opened_photo.size = (300, 300) 
        mock_opened_photo.mode = 'RGB'
        mock_image_open.return_value = mock_opened_photo
        
        mock_resized_photo = MagicMock(spec=Image.Image)
        mock_resized_photo.size = (spec_to_test.photo_width_px, spec_to_test.photo_height_px)
        mock_opened_photo.resize.return_value = mock_resized_photo

        mock_canvas = MagicMock(spec=Image.Image)
        mock_image_new_canvas.return_value = mock_canvas
        mock_draw_constructor.return_value = MagicMock()

        create_printable_image(
            self.dummy_processed_image_path, self.dummy_printable_image_path,
            self.dummy_fonts_folder, rows=1, cols=1, photo_spec=spec_to_test
        )
        mock_opened_photo.resize.assert_called_once_with(
            (spec_to_test.photo_width_px, spec_to_test.photo_height_px), Image.LANCZOS
        )
        mock_canvas.paste.assert_called_once()
        # Ensure the resized photo instance is what's pasted
        self.assertIs(mock_canvas.paste.call_args[0][0], mock_resized_photo)


    # --- Tests for create_printable_preview ---
    @patch('printable_creator.apply_watermark_to_photo') 
    @patch('printable_creator.ImageDraw.Draw') 
    @patch('printable_creator.Image.open')
    @patch('printable_creator.Image.new')
    def test_create_printable_preview_uses_spec(self, mock_image_new_canvas, mock_image_open, mock_draw_constructor, mock_apply_watermark):
        spec_to_test = self.mock_spec_35x45_300dpi
        
        mock_input_photo = MagicMock(spec=Image.Image)
        mock_input_photo.size = (spec_to_test.photo_width_px, spec_to_test.photo_height_px) # Assume it's already correct size
        mock_input_photo.mode = 'RGB'
        mock_image_open.return_value = mock_input_photo
        
        mock_watermarked_photo = MagicMock(spec=Image.Image)
        mock_watermarked_photo.size = (spec_to_test.photo_width_px, spec_to_test.photo_height_px)
        mock_apply_watermark.return_value = mock_watermarked_photo

        mock_canvas = MagicMock(spec=Image.Image)
        mock_image_new_canvas.return_value = mock_canvas
        mock_draw = MagicMock(spec=ImageDraw.ImageDraw); mock_draw_constructor.return_value = mock_draw

        rows, cols = 1, 1
        create_printable_preview(
            self.dummy_processed_image_path, self.dummy_printable_preview_path,
            self.dummy_fonts_folder, rows=rows, cols=cols, photo_spec=spec_to_test
        )

        mock_image_open.assert_called_once_with(self.dummy_processed_image_path)
        mock_input_photo.resize.assert_not_called() # Not called if size matches spec
        mock_apply_watermark.assert_called_once_with(mock_input_photo, self.dummy_fonts_folder)
        
        # Check that the watermarked photo (which should be spec size) is pasted
        self.assertEqual(mock_canvas.paste.call_count, rows*cols)
        paste_arg_img = mock_canvas.paste.call_args[0][0]
        self.assertIs(paste_arg_img, mock_watermarked_photo)
        self.assertEqual(paste_arg_img.width, spec_to_test.photo_width_px)
        self.assertEqual(paste_arg_img.height, spec_to_test.photo_height_px)

        mock_canvas.save.assert_called_once_with(
            self.dummy_printable_preview_path, dpi=(spec_to_test.dpi, spec_to_test.dpi), quality=95
        )

if __name__ == '__main__':
    unittest.main()
