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
from utils import PIXELS_PER_INCH, PHOTO_SIZE_PIXELS # PHOTO_SIZE_PIXELS is 600

class TestPrintableCreator(unittest.TestCase):

    def setUp(self):
        self.base_dir = 'test_temp_printable_files'
        self.dummy_processed_folder = os.path.join(self.base_dir, 'processed')
        self.dummy_preview_folder = os.path.join(self.base_dir, 'previews') # For printable_preview
        self.dummy_fonts_folder = os.path.join(self.base_dir, 'fonts')

        os.makedirs(self.dummy_processed_folder, exist_ok=True)
        os.makedirs(self.dummy_preview_folder, exist_ok=True)
        os.makedirs(self.dummy_fonts_folder, exist_ok=True)

        self.dummy_processed_image_path = os.path.join(self.dummy_processed_folder, 'processed_image.jpg')
        self.dummy_printable_image_path = os.path.join(self.dummy_processed_folder, 'printable_image.jpg')
        self.dummy_printable_preview_path = os.path.join(self.dummy_preview_folder, 'printable_preview.jpg')
        
        # Create a dummy 600x600 image (standard processed photo size)
        img = Image.new('RGB', (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS), color='blue')
        img.save(self.dummy_processed_image_path)

        self.arial_font_path = os.path.join(self.dummy_fonts_folder, 'Arial.ttf')
        try: # Dummy font file for ImageFont.truetype to not fail if not mocked
            with open(self.arial_font_path, 'w') as f: f.write("dummy font")
        except IOError: pass

    def tearDown(self):
        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)

    # --- Tests for apply_watermark_to_photo ---
    @patch('printable_creator.ImageFont.load_default')
    @patch('printable_creator.ImageFont.truetype')
    @patch('printable_creator.ImageDraw.Draw')
    @patch('printable_creator.Image.alpha_composite') # Mock this to control its return
    @patch('printable_creator.Image.new') # Mock Image.new for the overlay
    def test_apply_watermark_photo_basic(self, mock_image_new_overlay, mock_alpha_composite, mock_draw_constructor, mock_font_truetype, mock_font_load_default):
        mock_input_image = MagicMock(spec=Image.Image)
        mock_input_image.size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS)
        mock_input_image.mode = 'RGB'

        mock_rgba_image = MagicMock(spec=Image.Image)
        mock_input_image.copy.return_value.convert.return_value = mock_rgba_image # img.copy().convert('RGBA')

        mock_overlay = MagicMock(spec=Image.Image)
        mock_image_new_overlay.return_value = mock_overlay # For Image.new('RGBA', ...)

        mock_draw = MagicMock(spec=ImageDraw.ImageDraw)
        mock_draw_constructor.return_value = mock_draw

        mock_font = MagicMock(spec=ImageFont.FreeTypeFont)
        mock_font_truetype.return_value = mock_font

        mock_composited_image = MagicMock(spec=Image.Image)
        mock_alpha_composite.return_value = mock_composited_image

        mock_final_rgb_image = MagicMock(spec=Image.Image)
        mock_composited_image.convert.return_value = mock_final_rgb_image
        
        # Call the function
        result_image = apply_watermark_to_photo(mock_input_image, self.dummy_fonts_folder)

        # Assertions
        mock_input_image.copy.assert_called_once()
        mock_input_image.copy.return_value.convert.assert_called_once_with('RGBA')
        
        mock_image_new_overlay.assert_called_once_with('RGBA', mock_rgba_image.size, (255,255,255,0))
        mock_draw_constructor.assert_called_once_with(mock_overlay) # Draw on the overlay

        expected_font_size = int(PHOTO_SIZE_PIXELS * 0.1) # Based on logic in apply_watermark
        mock_font_truetype.assert_called_once_with(self.arial_font_path, expected_font_size)
        
        # Text drawing assertions
        text_width, text_height = PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS # Dummy values for textbbox/textsize if needed for anchor calc
        if hasattr(mock_draw, 'textbbox'):
            mock_draw.textbbox.return_value = (0,0, text_width, text_height)
        else:
             mock_draw.textsize.return_value = (text_width, text_height)

        watermark_text = "PREVIEW"
        text_x = (mock_rgba_image.size[0] - text_width) / 2
        text_y = (mock_rgba_image.size[1] - text_height) / 2
        
        # Check the draw.text call on the overlay's draw instance
        # The actual text position depends on textsize, which is hard to mock perfectly without deeper PIL internals.
        # We'll check for the text content, font, fill, and that it was called.
        # The anchor 'mm' in the actual code simplifies positioning.
        mock_draw.text.assert_called_once_with(
            (mock_rgba_image.size[0] / 2, mock_rgba_image.size[1] / 2), # Position with anchor 'mm'
            watermark_text,
            font=mock_font,
            fill=(0, 0, 0, 64), # Opacity 64
            anchor='mm'
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
        mock_input_image.size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS)
        mock_input_image.mode = 'RGB'
        mock_rgba_image = MagicMock(spec=Image.Image)
        mock_input_image.copy.return_value.convert.return_value = mock_rgba_image
        mock_overlay = MagicMock(spec=Image.Image); mock_image_new_overlay.return_value = mock_overlay
        mock_draw = MagicMock(spec=ImageDraw.ImageDraw); mock_draw_constructor.return_value = mock_draw
        
        mock_font_truetype.side_effect = IOError("Font not found") # Simulate error
        mock_default_font = MagicMock(spec=ImageFont.ImageFont)
        mock_font_load_default.return_value = mock_default_font

        mock_composited_image = MagicMock(spec=Image.Image); mock_alpha_composite.return_value = mock_composited_image
        mock_final_rgb_image = MagicMock(spec=Image.Image); mock_composited_image.convert.return_value = mock_final_rgb_image

        # Call the function
        result_image = apply_watermark_to_photo(mock_input_image, self.dummy_fonts_folder)

        # Assertions
        expected_font_size = int(PHOTO_SIZE_PIXELS * 0.1)
        mock_font_truetype.assert_called_once_with(self.arial_font_path, expected_font_size)
        mock_font_load_default.assert_called_once() # Fallback was used

        # Check that text was drawn with the default font
        mock_draw.text.assert_called_once_with(
            (mock_rgba_image.size[0] / 2, mock_rgba_image.size[1] / 2),
            "PREVIEW",
            font=mock_default_font, # Check default font usage
            fill=(0, 0, 0, 64),
            anchor='mm'
        )
        self.assertEqual(result_image, mock_final_rgb_image)

    # --- Tests for create_printable_image ---
    @patch('printable_creator.ImageFont.truetype') # Though not directly used by create_printable_image, it's good to have if any text was added
    @patch('printable_creator.ImageDraw.Draw')
    @patch('printable_creator.Image.open')
    @patch('printable_creator.Image.new')
    def test_create_printable_image_layout(self, mock_image_new_canvas, mock_image_open, mock_draw_constructor, mock_font_truetype):
        mock_input_photo = MagicMock(spec=Image.Image)
        mock_input_photo.size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS)
        mock_input_photo.mode = 'RGB'
        mock_image_open.return_value = mock_input_photo
        
        mock_canvas = MagicMock(spec=Image.Image)
        mock_image_new_canvas.return_value = mock_canvas
        
        mock_draw = MagicMock(spec=ImageDraw.ImageDraw)
        mock_draw_constructor.return_value = mock_draw

        rows, cols = 2, 2
        create_printable_image(
            self.dummy_processed_image_path,
            self.dummy_printable_image_path,
            self.dummy_fonts_folder, # Not directly used by this function but passed
            rows=rows,
            cols=cols
        )

        # Assertions
        mock_image_open.assert_called_once_with(self.dummy_processed_image_path)

        # Canvas creation (4x6 inches at 300 DPI)
        expected_canvas_width = 4 * PIXELS_PER_INCH
        expected_canvas_height = 6 * PIXELS_PER_INCH
        mock_image_new_canvas.assert_called_once_with('RGB', (expected_canvas_width, expected_canvas_height), 'white')
        mock_draw_constructor.assert_called_once_with(mock_canvas)

        # Photo pasting
        self.assertEqual(mock_input_photo.resize.call_count, 0) # Should not be resized as it's already 600x600

        spacing_pixels = int(0.25 * PIXELS_PER_INCH) # 75 pixels
        photo_width_px = PHOTO_SIZE_PIXELS # 600
        photo_height_px = PHOTO_SIZE_PIXELS # 600

        expected_paste_calls = []
        for r in range(rows):
            for c in range(cols):
                # Top-left corner of the 2x2 inch photo area for this photo
                x_offset_photo_area = c * (photo_width_px + spacing_pixels)
                y_offset_photo_area = r * (photo_height_px + spacing_pixels)
                
                # Centering the photo within its 2x2 inch area on the 4x6 sheet
                # The photo itself is 2x2 inches (600x600px), so it should fill its slot.
                # The create_printable_image places photos directly.
                # Let's re-check the logic in create_printable_image for x,y paste coords.
                # It seems to be:
                # x = c * photo_width_px + (c + 1) * spacing_pixels
                # y = r * photo_height_px + (r + 1) * spacing_pixels
                # This means spacing is also applied before the first photo in each row/col.
                
                # Corrected based on typical grid layout with spacing around items:
                # Assuming spacing is between photos and around the block of photos.
                # The problem description implies photos are 2x2 inches.
                # A 4x6 sheet can fit two 2x2 photos side-by-side (4 inches) and two rows (4 inches).
                # This leaves 2 inches of height on a 4x6 sheet, which is unusual if using it fully.
                # The function code uses:
                # page_width = cols * photo_width_px + (cols + 1) * spacing_pixels
                # page_height = rows * photo_height_px + (rows + 1) * spacing_pixels
                # This defines the total size of the canvas.
                # For 2x2 photos (600x600px) and 2x2 grid, spacing 75px:
                # page_width = 2*600 + 3*75 = 1200 + 225 = 1425 (approx 4.75 inches)
                # page_height = 2*600 + 3*75 = 1425 (approx 4.75 inches)
                # This is different from the fixed 4x6 inch (1200x1800) canvas.
                # The problem description says "4x6 inch canvas (4 * PIXELS_PER_INCH, 6 * PIXELS_PER_INCH)"
                # This means the fixed canvas size test is correct.
                # The paste coordinates in create_printable_image must be relative to this fixed canvas.
                # The code uses:
                # x = (canvas_width - (cols * photo_width_px + (cols - 1) * spacing_pixels)) // 2 + c * (photo_width_px + spacing_pixels)
                # y = (canvas_height - (rows * photo_height_px + (rows - 1) * spacing_pixels)) // 2 + r * (photo_height_px + spacing_pixels)
                # This centers the block of photos.

                block_width = cols * photo_width_px + (cols - 1) * spacing_pixels
                block_height = rows * photo_height_px + (rows - 1) * spacing_pixels
                start_x_block = (expected_canvas_width - block_width) // 2
                start_y_block = (expected_canvas_height - block_height) // 2
                
                x = start_x_block + c * (photo_width_px + spacing_pixels)
                y = start_y_block + r * (photo_height_px + spacing_pixels)
                expected_paste_calls.append(call(mock_input_photo, (x, y)))
        
        for ec in expected_paste_calls:
            self.assertIn(ec, mock_canvas.paste.call_args_list)
        self.assertEqual(mock_canvas.paste.call_count, rows * cols)

        # Save call
        mock_canvas.save.assert_called_once_with(
            self.dummy_printable_image_path,
            dpi=(PIXELS_PER_INCH, PIXELS_PER_INCH),
            quality=95
        )

    @patch('printable_creator.ImageDraw.Draw') # Mock Draw for cutting lines, not focus of this test
    @patch('printable_creator.Image.open')
    @patch('printable_creator.Image.new')
    def test_create_printable_image_resizes_input(self, mock_image_new_canvas, mock_image_open, mock_draw_constructor):
        mock_small_photo = MagicMock(spec=Image.Image)
        mock_small_photo.size = (300, 300) # Smaller than PHOTO_SIZE_PIXELS
        mock_small_photo.mode = 'RGB'
        mock_image_open.return_value = mock_small_photo
        
        mock_resized_photo = MagicMock(spec=Image.Image)
        mock_resized_photo.size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS)
        mock_small_photo.resize.return_value = mock_resized_photo # IMPORTANT: mock the resize return

        mock_canvas = MagicMock(spec=Image.Image)
        mock_image_new_canvas.return_value = mock_canvas
        mock_draw_constructor.return_value = MagicMock(spec=ImageDraw.ImageDraw)


        create_printable_image(
            self.dummy_processed_image_path,
            self.dummy_printable_image_path,
            self.dummy_fonts_folder,
            rows=1, cols=1 # Simpler layout for this test
        )
        mock_image_open.assert_called_once_with(self.dummy_processed_image_path)
        mock_small_photo.resize.assert_called_once_with((PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS), Image.LANCZOS)
        
        # Verify that the resized photo is pasted
        # Calculations for paste coordinates (1x1 grid on 4x6 canvas)
        expected_canvas_width = 4 * PIXELS_PER_INCH
        expected_canvas_height = 6 * PIXELS_PER_INCH
        block_width = PHOTO_SIZE_PIXELS
        block_height = PHOTO_SIZE_PIXELS
        start_x_block = (expected_canvas_width - block_width) // 2 # (1200 - 600)//2 = 300
        start_y_block = (expected_canvas_height - block_height) // 2 # (1800 - 600)//2 = 600
        
        mock_canvas.paste.assert_called_once_with(mock_resized_photo, (start_x_block, start_y_block))

    @patch('printable_creator.ImageDraw.Draw')
    @patch('printable_creator.Image.open')
    @patch('printable_creator.Image.new')
    def test_create_printable_image_cutting_lines(self, mock_image_new_canvas, mock_image_open, mock_draw_constructor):
        mock_input_photo = MagicMock(spec=Image.Image)
        mock_input_photo.size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS)
        mock_input_photo.mode = 'RGB'
        mock_image_open.return_value = mock_input_photo
        
        mock_canvas = MagicMock(spec=Image.Image)
        mock_image_new_canvas.return_value = mock_canvas
        
        mock_draw = MagicMock(spec=ImageDraw.ImageDraw)
        mock_draw_constructor.return_value = mock_draw

        rows, cols = 2, 2
        create_printable_image(
            self.dummy_processed_image_path,
            self.dummy_printable_image_path,
            self.dummy_fonts_folder,
            rows=rows,
            cols=cols
        )
        
        # --- Calculate expected line coordinates ---
        canvas_width = 4 * PIXELS_PER_INCH
        canvas_height = 6 * PIXELS_PER_INCH
        photo_width_px = PHOTO_SIZE_PIXELS
        photo_height_px = PHOTO_SIZE_PIXELS
        spacing_pixels = int(0.25 * PIXELS_PER_INCH)
        line_color = (200, 200, 200) 
        line_width = 1 
        dash_length = 10

        block_width = cols * photo_width_px + (cols - 1) * spacing_pixels
        block_height = rows * photo_height_px + (rows - 1) * spacing_pixels
        start_x_block = (canvas_width - block_width) // 2
        start_y_block = (canvas_height - block_height) // 2

        actual_line_calls = mock_draw.line.call_args_list
        
        # Horizontal cutting lines (between rows)
        for r in range(1, rows): # Lines between rows
            y_line = start_y_block + r * photo_height_px + (r -1) * spacing_pixels + spacing_pixels / 2
            # Line should span the width of the photo block
            x_start_line = start_x_block 
            x_end_line = start_x_block + block_width
            
            # Check for dashed line segments
            num_dashes = int((x_end_line - x_start_line) / (dash_length * 2))
            self.assertTrue(any(
                # Check one segment of the dashed line
                c == call([(x_start_line, y_line), (x_start_line + dash_length, y_line)], fill=line_color, width=line_width)
                for c in actual_line_calls if abs(c[0][0][1] - y_line) < 1 # Compare y-coord due to potential float issues
            ), f"Horizontal dashed line at y={y_line} not found or segment mismatch.")

        # Vertical cutting lines (between columns)
        for c in range(1, cols): # Lines between columns
            x_line = start_x_block + c * photo_width_px + (c - 1) * spacing_pixels + spacing_pixels / 2
            y_start_line = start_y_block
            y_end_line = start_y_block + block_height

            self.assertTrue(any(
                c == call([(x_line, y_start_line), (x_line, y_start_line + dash_length)], fill=line_color, width=line_width)
                for c in actual_line_calls if abs(c[0][0][0] - x_line) < 1 # Compare x-coord
            ), f"Vertical dashed line at x={x_line} not found or segment mismatch.")
            
        # Ensure at least some lines were drawn (simplistic check for brevity)
        # For 2x2, expect 1 horizontal and 1 vertical dashed "logical" line
        # Each logical dashed line consists of multiple small segments.
        # The number of mock_draw.line calls will be (num_dashes_h * 1) + (num_dashes_v * 1)
        # This is a bit complex to assert exactly without running the loop logic from the source.
        # A simpler check is that draw.line was called multiple times.
        self.assertGreater(mock_draw.line.call_count, (rows-1 + cols-1) * 2) # At least a few segments per line

    # --- Tests for create_printable_preview ---
    @patch('printable_creator.apply_watermark_to_photo') # Key mock for this test
    @patch('printable_creator.ImageDraw.Draw') # For cutting lines
    @patch('printable_creator.Image.open')
    @patch('printable_creator.Image.new')
    def test_create_printable_preview_calls_apply_watermark(self, mock_image_new_canvas, mock_image_open, mock_draw_constructor, mock_apply_watermark):
        mock_input_photo = MagicMock(spec=Image.Image)
        mock_input_photo.size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS)
        mock_input_photo.mode = 'RGB'
        mock_image_open.return_value = mock_input_photo
        
        mock_watermarked_photo_instance = MagicMock(spec=Image.Image)
        mock_watermarked_photo_instance.size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS)
        mock_apply_watermark.return_value = mock_watermarked_photo_instance

        mock_canvas = MagicMock(spec=Image.Image)
        mock_image_new_canvas.return_value = mock_canvas
        mock_draw_constructor.return_value = MagicMock(spec=ImageDraw.ImageDraw) # For cutting lines

        rows, cols = 2, 3
        create_printable_preview(
            self.dummy_processed_image_path,
            self.dummy_printable_preview_path,
            self.dummy_fonts_folder,
            rows=rows,
            cols=cols
        )

        # Assertions
        mock_image_open.assert_called_once_with(self.dummy_processed_image_path)
        
        # apply_watermark_to_photo should be called for each photo in the grid
        self.assertEqual(mock_apply_watermark.call_count, rows * cols)
        mock_apply_watermark.assert_called_with(mock_input_photo, self.dummy_fonts_folder) # Check args on one call

        # Ensure the result from apply_watermark_to_photo is what's pasted
        self.assertEqual(mock_canvas.paste.call_count, rows * cols)
        # Verify that the object returned by mock_apply_watermark was passed to paste
        # This requires checking the arguments of mock_canvas.paste calls
        for paste_call_args in mock_canvas.paste.call_args_list:
            self.assertIs(paste_call_args[0][0], mock_watermarked_photo_instance) # Check if the first arg to paste is the watermarked image

        mock_canvas.save.assert_called_once_with(self.dummy_printable_preview_path, quality=95)


    @patch('printable_creator.apply_watermark_to_photo') # Mock this to control what's pasted
    @patch('printable_creator.ImageDraw.Draw')
    @patch('printable_creator.Image.open')
    @patch('printable_creator.Image.new')
    def test_create_printable_preview_layout_and_save(self, mock_image_new_canvas, mock_image_open, mock_draw_constructor, mock_apply_watermark):
        mock_input_photo_opened = MagicMock(spec=Image.Image)
        mock_input_photo_opened.size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS)
        mock_input_photo_opened.mode = 'RGB'
        mock_image_open.return_value = mock_input_photo_opened
        
        # Mock the return of apply_watermark_to_photo
        mock_watermarked_photo = MagicMock(spec=Image.Image)
        mock_watermarked_photo.size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS) # Should be same size
        mock_apply_watermark.return_value = mock_watermarked_photo

        mock_canvas = MagicMock(spec=Image.Image)
        mock_image_new_canvas.return_value = mock_canvas
        
        mock_draw = MagicMock(spec=ImageDraw.ImageDraw)
        mock_draw_constructor.return_value = mock_draw

        rows, cols = 2, 2
        create_printable_preview(
            self.dummy_processed_image_path,
            self.dummy_printable_preview_path,
            self.dummy_fonts_folder,
            rows=rows,
            cols=cols
        )

        # Assertions
        mock_image_open.assert_called_once_with(self.dummy_processed_image_path)
        self.assertEqual(mock_apply_watermark.call_count, rows * cols) # Should be called for each cell

        # Canvas creation (4x6 inches at 300 DPI)
        expected_canvas_width = 4 * PIXELS_PER_INCH
        expected_canvas_height = 6 * PIXELS_PER_INCH
        mock_image_new_canvas.assert_called_once_with('RGB', (expected_canvas_width, expected_canvas_height), 'white')
        mock_draw_constructor.assert_called_once_with(mock_canvas)

        # Photo pasting (using the watermarked photo)
        spacing_pixels = int(0.25 * PIXELS_PER_INCH)
        photo_width_px = PHOTO_SIZE_PIXELS
        photo_height_px = PHOTO_SIZE_PIXELS

        block_width = cols * photo_width_px + (cols - 1) * spacing_pixels
        block_height = rows * photo_height_px + (rows - 1) * spacing_pixels
        start_x_block = (expected_canvas_width - block_width) // 2
        start_y_block = (expected_canvas_height - block_height) // 2
        
        expected_paste_calls = []
        for r_idx in range(rows):
            for c_idx in range(cols):
                x = start_x_block + c_idx * (photo_width_px + spacing_pixels)
                y = start_y_block + r_idx * (photo_height_px + spacing_pixels)
                expected_paste_calls.append(call(mock_watermarked_photo, (x, y)))
        
        for ec in expected_paste_calls:
            self.assertIn(ec, mock_canvas.paste.call_args_list)
        self.assertEqual(mock_canvas.paste.call_count, rows * cols)

        # Cutting lines (check if draw.line was called, similar to create_printable_image test)
        self.assertGreater(mock_draw.line.call_count, (rows-1 + cols-1) * 2) 

        # Save call
        mock_canvas.save.assert_called_once_with(
            self.dummy_printable_preview_path,
            quality=95 # Default quality for preview is 95
        )


if __name__ == '__main__':
    unittest.main()
