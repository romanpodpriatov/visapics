import unittest
from PIL import Image
import sys
import os

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from utils import (
    allowed_file, 
    is_allowed_file, 
    clean_filename, 
    create_image_with_padding, 
    PHOTO_SIZE_PIXELS, # Assuming this is used by tests or the function
    ALLOWED_EXTENSIONS # Used for verifying behavior
)

class TestUtils(unittest.TestCase):

    # Tests for allowed_file
    def test_allowed_file_valid_extensions(self):
        self.assertTrue(allowed_file('photo.jpg'))
        self.assertTrue(allowed_file('image.PNG'))
        self.assertTrue(allowed_file('document.JPEG'))
        self.assertTrue(allowed_file('test.jpeg')) # Ensure all from ALLOWED_EXTENSIONS work

    def test_allowed_file_invalid_extensions(self):
        self.assertFalse(allowed_file('archive.zip'))
        self.assertFalse(allowed_file('text.txt'))
        self.assertFalse(allowed_file('image.gif'))

    def test_allowed_file_no_extension(self):
        self.assertFalse(allowed_file('filename'))

    def test_allowed_file_hidden_file_with_extension(self):
        self.assertTrue(allowed_file('.hidden.png'))

    def test_allowed_file_empty_filename(self):
        self.assertFalse(allowed_file(''))

    # Tests for is_allowed_file (similar to allowed_file but takes full path)
    def test_is_allowed_file_valid(self):
        self.assertTrue(is_allowed_file('path/to/photo.jpg'))
        self.assertTrue(is_allowed_file('another/path/image.PNG'))
        self.assertTrue(is_allowed_file('/abs/path/document.JPEG'))
        if 'jpeg' in ALLOWED_EXTENSIONS: # from problem description
             self.assertTrue(is_allowed_file('some.jpeg'))

    def test_is_allowed_file_invalid(self):
        self.assertFalse(is_allowed_file('path/to/archive.zip'))
        self.assertFalse(is_allowed_file('another/document.txt'))
        self.assertFalse(is_allowed_file('no_ext_in_path'))

    def test_is_allowed_file_no_extension_in_path(self):
        self.assertFalse(is_allowed_file('path/to/filename'))

    # Tests for clean_filename
    def test_clean_filename_simple(self):
        self.assertEqual(clean_filename('simple_name.jpg'), 'simple_name.jpg')

    def test_clean_filename_with_spaces(self):
        self.assertEqual(clean_filename('my image file.png'), 'my_image_file.png')

    def test_clean_filename_with_special_chars(self):
        # werkzeug.utils.secure_filename behavior
        self.assertEqual(clean_filename('../secret/image.jpeg'), 'secret_image.jpeg')
        self.assertEqual(clean_filename('test!@#$%^&*.png'), 'test.png') # Most special chars are removed
        self.assertEqual(clean_filename('file with %20 space.jpg'), 'file_with_20_space.jpg')

    def test_clean_filename_with_multiple_dots(self):
        self.assertEqual(clean_filename('file.name.with.dots.jpg'), 'file_name_with_dots.jpg')

    def test_clean_filename_leading_trailing_spaces(self):
        self.assertEqual(clean_filename('  leading_trailing.jpg  '), 'leading_trailing.jpg')

    def test_clean_filename_unicode(self):
        # secure_filename typically converts unicode to ASCII
        self.assertEqual(clean_filename('файл_тест.jpg'), 'файл_тест.jpg') # secure_filename handles unicode by default

    def test_clean_filename_empty(self):
        self.assertEqual(clean_filename('.jpg'), '.jpg') # secure_filename keeps leading dot if it's the only thing before ext
        self.assertEqual(clean_filename(''), '')

    # Helper for checking padding color
    def check_padding_color(self, image, expected_color, padded_area_only=False, inner_rect=None):
        """
        Checks the padding color of an image.
        If padded_area_only is True and inner_rect is provided,
        it will only check pixels outside the inner_rect.
        inner_rect is (left, top, right, bottom) of the non-padded area.
        """
        width, height = image.size
        if not padded_area_only or not inner_rect:
            # Check corners by default if not checking specific padded areas
            self.assertEqual(image.getpixel((0, 0)), expected_color, "Top-left corner color mismatch.")
            self.assertEqual(image.getpixel((width - 1, 0)), expected_color, "Top-right corner color mismatch.")
            self.assertEqual(image.getpixel((0, height - 1)), expected_color, "Bottom-left corner color mismatch.")
            self.assertEqual(image.getpixel((width - 1, height - 1)), expected_color, "Bottom-right corner color mismatch.")
        else:
            # Check representative pixels in padded areas
            # Top padding
            if inner_rect[1] > 0:
                self.assertEqual(image.getpixel((inner_rect[0] + (inner_rect[2]-inner_rect[0])//2, inner_rect[1]//2)), expected_color, "Top padding color mismatch.")
            # Bottom padding
            if inner_rect[3] < height:
                self.assertEqual(image.getpixel((inner_rect[0] + (inner_rect[2]-inner_rect[0])//2, inner_rect[3] + (height - inner_rect[3])//2)), expected_color, "Bottom padding color mismatch.")
            # Left padding
            if inner_rect[0] > 0:
                self.assertEqual(image.getpixel((inner_rect[0]//2, inner_rect[1] + (inner_rect[3]-inner_rect[1])//2)), expected_color, "Left padding color mismatch.")
            # Right padding
            if inner_rect[2] < width:
                self.assertEqual(image.getpixel((inner_rect[2] + (width - inner_rect[2])//2, inner_rect[1] + (inner_rect[3]-inner_rect[1])//2)), expected_color, "Right padding color mismatch.")


    # Tests for create_image_with_padding
    def test_create_image_with_padding_square_to_square(self):
        original_img = Image.new('RGB', (300, 300), 'black')
        target_size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS) # (600, 600)
        padding_color = (255, 255, 255) # White

        padded_img = create_image_with_padding(original_img, target_size, padding_color)

        self.assertEqual(padded_img.size, target_size)
        
        # Original image (300x300) should be scaled to 600x600 (ratio=2)
        # So, the black image should fill the whole 600x600 space. No padding visible.
        # Let's check a few pixels from the center of the original image area
        # The original image is black, scaled up.
        self.assertEqual(padded_img.getpixel((300, 300)), (0,0,0), "Center pixel of scaled image should be black")
        self.assertEqual(padded_img.getpixel((0,0)), (0,0,0), "Top-left pixel of scaled image should be black")


    def test_create_image_with_padding_rect_to_square_height_dominant(self):
        original_img = Image.new('RGB', (200, 400), 'blue')
        target_size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS) # (600, 600)
        padding_color = (255, 0, 0) # Red padding

        padded_img = create_image_with_padding(original_img, target_size, padding_color)
        self.assertEqual(padded_img.size, target_size)

        # Height is dominant: 400px -> 600px (scale = 1.5)
        # Width becomes 200px * 1.5 = 300px
        # So, the blue image (300x600) is placed in a 600x600 canvas.
        # Padding should be horizontal.
        expected_width_scaled = 300
        expected_height_scaled = 600
        paste_x = (target_size[0] - expected_width_scaled) // 2 # (600 - 300) // 2 = 150
        paste_y = (target_size[1] - expected_height_scaled) // 2 # (600 - 600) // 2 = 0

        # Check padding color in padded areas (left and right of the blue image)
        self.check_padding_color(padded_img, padding_color, padded_area_only=True, 
                                 inner_rect=(paste_x, paste_y, paste_x + expected_width_scaled, paste_y + expected_height_scaled))
        
        # Check center of the original image content
        center_x_on_padded = paste_x + (expected_width_scaled // 2)
        center_y_on_padded = paste_y + (expected_height_scaled // 2)
        self.assertEqual(padded_img.getpixel((center_x_on_padded, center_y_on_padded)), (0, 0, 255)) # Blue


    def test_create_image_with_padding_rect_to_square_width_dominant(self):
        original_img = Image.new('RGB', (400, 200), 'green')
        target_size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS) # (600, 600)
        padding_color = (0, 0, 255) # Blue padding

        padded_img = create_image_with_padding(original_img, target_size, padding_color)
        self.assertEqual(padded_img.size, target_size)

        # Width is dominant: 400px -> 600px (scale = 1.5)
        # Height becomes 200px * 1.5 = 300px
        # So, the green image (600x300) is placed in a 600x600 canvas.
        # Padding should be vertical.
        expected_width_scaled = 600
        expected_height_scaled = 300
        paste_x = (target_size[0] - expected_width_scaled) // 2 # (600 - 600) // 2 = 0
        paste_y = (target_size[1] - expected_height_scaled) // 2 # (600 - 300) // 2 = 150

        self.check_padding_color(padded_img, padding_color, padded_area_only=True,
                                 inner_rect=(paste_x, paste_y, paste_x + expected_width_scaled, paste_y + expected_height_scaled))
        
        center_x_on_padded = paste_x + (expected_width_scaled // 2)
        center_y_on_padded = paste_y + (expected_height_scaled // 2)
        self.assertEqual(padded_img.getpixel((center_x_on_padded, center_y_on_padded)), (0, 128, 0)) # Green


    def test_create_image_with_padding_no_padding_needed(self):
        original_img = Image.new('RGB', (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS), 'magenta')
        target_size = (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS)
        padding_color = (0,0,0) # Black padding (should not be used)

        padded_img = create_image_with_padding(original_img, target_size, padding_color)

        self.assertEqual(padded_img.size, target_size)
        # Image should be identical, no padding applied.
        self.assertEqual(padded_img.getpixel((0,0)), (255,0,255)) # Magenta
        self.assertEqual(padded_img.getpixel((PHOTO_SIZE_PIXELS-1, PHOTO_SIZE_PIXELS-1)), (255,0,255))


    def test_create_image_with_padding_custom_color(self):
        original_img = Image.new('RGB', (100,100), 'yellow')
        target_size = (200,200)
        custom_padding_color = (10,20,30)

        padded_img = create_image_with_padding(original_img, target_size, custom_padding_color)
        self.assertEqual(padded_img.size, target_size)

        # Original 100x100 scaled to 200x200. No padding visible.
        # Oh, wait. If original is 100x100 and target is 200x200, scale is 2.
        # The image is resized to 200x200. No padding color should be visible.
        # The function is create_image_WITH_PADDING. If aspect ratio is same, it just resizes.
        # Let's test with different aspect ratio to ensure custom padding color is used.
        
        original_img_aspect = Image.new('RGB', (50,100), 'yellow') # tall image
        padded_img_aspect = create_image_with_padding(original_img_aspect, target_size, custom_padding_color)
        self.assertEqual(padded_img_aspect.size, target_size)

        # Height is dominant: 100 -> 200 (scale = 2)
        # Width becomes 50*2 = 100
        # So, yellow image (100x200) in a 200x200 canvas. Padding horizontal.
        expected_width_scaled = 100
        expected_height_scaled = 200
        paste_x = (target_size[0] - expected_width_scaled) // 2 # (200-100)//2 = 50
        paste_y = (target_size[1] - expected_height_scaled) // 2 # (200-200)//2 = 0
        
        self.check_padding_color(padded_img_aspect, custom_padding_color, padded_area_only=True,
                                 inner_rect=(paste_x, paste_y, paste_x + expected_width_scaled, paste_y + expected_height_scaled))
        self.assertEqual(padded_img_aspect.getpixel((paste_x + 10, paste_y + 10)), (255,255,0)) # Yellow


if __name__ == '__main__':
    unittest.main()
