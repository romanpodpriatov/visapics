import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to sys.path to allow direct import of modules
# This is often necessary when running tests from a subfolder or an IDE
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from face_analyzer import calculate_crop_dimensions, FaceAnalyzer
from utils import PIXELS_PER_INCH, PHOTO_SIZE_PIXELS

class TestCalculateCropDimensions(unittest.TestCase):

    @patch('face_analyzer.FaceAnalyzer')
    def test_ideal_conditions(self, MockFaceAnalyzer):
        # Setup mock for FaceAnalyzer instance
        mock_analyzer_instance = MockFaceAnalyzer.return_value
        
        # Define ideal measurements in pixels for a 600x600 image
        # Target head height: 1.16 inches (approx 348 pixels at 300 DPI)
        # Target eye-to-bottom: 1.25 inches (eye level at 600 - 375 = 225px from top)
        
        ideal_head_height_px = 1.16 * PIXELS_PER_INCH
        ideal_eye_level_px = PHOTO_SIZE_PIXELS - (1.25 * PIXELS_PER_INCH) # from top
        
        # Simulate that FaceAnalyzer.get_head_measurements returns these ideal pixel values
        # head_top, chin_bottom, eye_level, face_center_x
        mock_analyzer_instance.get_head_measurements.return_value = (
            ideal_eye_level_px - (ideal_head_height_px * 0.45), # head_top (assuming 45% of head is above eyes)
            ideal_eye_level_px + (ideal_head_height_px * 0.55), # chin_bottom (assuming 55% of head is below eyes)
            ideal_eye_level_px,
            PHOTO_SIZE_PIXELS / 2  # face_center_x (perfectly centered)
        )

        mock_landmarks = MagicMock()  # face_landmarks are passed to FaceAnalyzer constructor, which is mocked
        img_height, img_width = PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS # 600, 600

        crop_data = calculate_crop_dimensions(mock_landmarks, img_height, img_width)

        # Assertions
        # Check head height (in inches)
        self.assertTrue(1.0 <= crop_data['head_height'] <= 1.375, 
                        f"Head height {crop_data['head_height']:.3f} out of range [1.0, 1.375]")
        self.assertAlmostEqual(crop_data['head_height'], 1.16, delta=0.05,
                               msg=f"Expected head height ~1.16, got {crop_data['head_height']:.3f}")

        # Check eye-to-bottom (in inches)
        self.assertTrue(1.125 <= crop_data['eye_to_bottom'] <= 1.375,
                        f"Eye-to-bottom {crop_data['eye_to_bottom']:.3f} out of range [1.125, 1.375]")
        self.assertAlmostEqual(crop_data['eye_to_bottom'], 1.25, delta=0.05,
                               msg=f"Expected eye-to-bottom ~1.25, got {crop_data['eye_to_bottom']:.3f}")
        
        # Check scale factor (should be close to 1.0 if input is already ideal sized)
        # The calculation might make minor adjustments, so delta is important.
        # If the mock input from get_head_measurements is already "perfect" for the target inches,
        # scale factor should be very close to 1.
        self.assertAlmostEqual(crop_data['scale_factor'], 1.0, delta=0.1,
                               msg=f"Expected scale factor ~1.0, got {crop_data['scale_factor']:.3f}")

        # Check crop box dimensions (should be 600x600)
        self.assertEqual(crop_data['crop_right'] - crop_data['crop_left'], PHOTO_SIZE_PIXELS,
                         "Crop width not equal to PHOTO_SIZE_PIXELS")
        self.assertEqual(crop_data['crop_bottom'] - crop_data['crop_top'], PHOTO_SIZE_PIXELS,
                         "Crop height not equal to PHOTO_SIZE_PIXELS")
        
        # Check if face is centered after crop (crop_left should be such that face_center_x is middle of 600px)
        # This requires knowing how face_center_x from get_head_measurements relates to final crop.
        # The current calculate_crop_dimensions centers the *derived* face bounding box.
        # If input face_center_x is 300, and scale is 1, crop_left should be 0.
        self.assertAlmostEqual(crop_data['crop_left'], 0, delta=5, # Allow small delta for float precision
                               msg=f"Expected crop_left ~0 for centered ideal input, got {crop_data['crop_left']}")
        self.assertAlmostEqual(crop_data['crop_right'], PHOTO_SIZE_PIXELS, delta=5,
                                msg=f"Expected crop_right ~{PHOTO_SIZE_PIXELS} for centered ideal input, got {crop_data['crop_right']}")

    @patch('face_analyzer.FaceAnalyzer')
    def test_face_too_small(self, MockFaceAnalyzer):
        mock_analyzer_instance = MockFaceAnalyzer.return_value
        
        # Small head: 100px height (target is ~300-412px)
        # Eye level at 250, head top 200, chin bottom 300
        mock_analyzer_instance.get_head_measurements.return_value = (
            200,  # head_top
            300,  # chin_bottom
            250,  # eye_level
            PHOTO_SIZE_PIXELS / 2   # face_center_x (centered)
        )

        mock_landmarks = MagicMock()
        img_height, img_width = PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS

        crop_data = calculate_crop_dimensions(mock_landmarks, img_height, img_width)

        # Assertions
        self.assertGreater(crop_data['scale_factor'], 1.0,
                           msg=f"Expected scale_factor > 1 for small face, got {crop_data['scale_factor']:.3f}")
        
        # Check head height (should be scaled up towards 1.0 inch minimum)
        self.assertTrue(1.0 <= crop_data['head_height'] <= 1.375, 
                        f"Head height {crop_data['head_height']:.3f} out of range [1.0, 1.375] after scaling")
        # It should be close to the minimum allowed (1.0 inch) because the original was very small
        self.assertAlmostEqual(crop_data['head_height'], 1.0, delta=0.1, # Allow some delta
                               msg=f"Expected head height ~1.0 for small face, got {crop_data['head_height']:.3f}")

        # Eye-to-bottom should also be scaled and be within valid range
        self.assertTrue(1.125 <= crop_data['eye_to_bottom'] <= 1.375,
                        f"Eye-to-bottom {crop_data['eye_to_bottom']:.3f} out of range [1.125, 1.375] after scaling")

        # Check crop box dimensions
        self.assertEqual(crop_data['crop_right'] - crop_data['crop_left'], PHOTO_SIZE_PIXELS,
                         "Crop width not equal to PHOTO_SIZE_PIXELS")
        self.assertEqual(crop_data['crop_bottom'] - crop_data['crop_top'], PHOTO_SIZE_PIXELS,
                         "Crop height not equal to PHOTO_SIZE_PIXELS")

    @patch('face_analyzer.FaceAnalyzer')
    def test_face_too_large(self, MockFaceAnalyzer):
        mock_analyzer_instance = MockFaceAnalyzer.return_value
        
        # Large head: 500px height (target is ~300-412px)
        # Eye level at 250, head top 0, chin bottom 500
        mock_analyzer_instance.get_head_measurements.return_value = (
            0,    # head_top
            500,  # chin_bottom
            250,  # eye_level (relative to original image)
            PHOTO_SIZE_PIXELS / 2   # face_center_x (centered)
        )

        mock_landmarks = MagicMock()
        img_height, img_width = PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS # input image is 600x600

        crop_data = calculate_crop_dimensions(mock_landmarks, img_height, img_width)

        # Assertions
        self.assertLess(crop_data['scale_factor'], 1.0,
                        msg=f"Expected scale_factor < 1 for large face, got {crop_data['scale_factor']:.3f}")
        
        # Check head height (should be scaled down towards 1.375 inches maximum)
        self.assertTrue(1.0 <= crop_data['head_height'] <= 1.375, 
                        f"Head height {crop_data['head_height']:.3f} out of range [1.0, 1.375] after scaling")
        self.assertAlmostEqual(crop_data['head_height'], 1.375, delta=0.1, # Allow some delta
                               msg=f"Expected head height ~1.375 for large face, got {crop_data['head_height']:.3f}")

        # Eye-to-bottom should also be scaled and be within valid range
        # This assertion is tricky because the function prioritizes head height.
        # If head is very large, eye position might be compromised to fit head.
        # However, it should still aim for the valid range if possible.
        self.assertTrue(1.125 <= crop_data['eye_to_bottom'] <= 1.375,
                        f"Eye-to-bottom {crop_data['eye_to_bottom']:.3f} out of range [1.125, 1.375] after scaling for large face")

        # Check crop box dimensions
        self.assertEqual(crop_data['crop_right'] - crop_data['crop_left'], PHOTO_SIZE_PIXELS,
                         "Crop width not equal to PHOTO_SIZE_PIXELS")
        self.assertEqual(crop_data['crop_bottom'] - crop_data['crop_top'], PHOTO_SIZE_PIXELS,
                         "Crop height not equal to PHOTO_SIZE_PIXELS")

    @patch('face_analyzer.FaceAnalyzer')
    def test_face_off_center(self, MockFaceAnalyzer):
        mock_analyzer_instance = MockFaceAnalyzer.return_value
        
        # Ideal head height and eye level, but face is off-center to the left
        ideal_head_height_px = 1.16 * PIXELS_PER_INCH
        ideal_eye_level_px = PHOTO_SIZE_PIXELS - (1.25 * PIXELS_PER_INCH)
        
        mock_analyzer_instance.get_head_measurements.return_value = (
            ideal_eye_level_px - (ideal_head_height_px * 0.45), 
            ideal_eye_level_px + (ideal_head_height_px * 0.55), 
            ideal_eye_level_px,
            PHOTO_SIZE_PIXELS / 4  # face_center_x significantly to the left (150px for a 600px image)
        )

        mock_landmarks = MagicMock()
        img_height, img_width = PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS

        crop_data = calculate_crop_dimensions(mock_landmarks, img_height, img_width)

        # Assertions
        # Head height and eye-to-bottom should still be fine as face size is ideal
        self.assertTrue(1.0 <= crop_data['head_height'] <= 1.375)
        self.assertAlmostEqual(crop_data['head_height'], 1.16, delta=0.05)
        self.assertTrue(1.125 <= crop_data['eye_to_bottom'] <= 1.375)
        self.assertAlmostEqual(crop_data['eye_to_bottom'], 1.25, delta=0.05)

        # Scale factor should be close to 1.0
        self.assertAlmostEqual(crop_data['scale_factor'], 1.0, delta=0.1)

        # Check crop box dimensions
        self.assertEqual(crop_data['crop_right'] - crop_data['crop_left'], PHOTO_SIZE_PIXELS,
                         "Crop width not equal to PHOTO_SIZE_PIXELS")
        self.assertEqual(crop_data['crop_bottom'] - crop_data['crop_top'], PHOTO_SIZE_PIXELS,
                         "Crop height not equal to PHOTO_SIZE_PIXELS")
        
        # Check centering:
        # The face_center_x_scaled should be at the center of the cropped image (300px).
        # face_center_x_scaled = (original_face_center_x * scale_factor)
        # desired_center_on_crop = PHOTO_SIZE_PIXELS / 2
        # crop_left = face_center_x_scaled - desired_center_on_crop
        # crop_right = face_center_x_scaled + desired_center_on_crop
        
        # Since scale_factor is ~1.0, original_face_center_x is 150.
        # Expected crop_left = 150 - (600/2) = 150 - 300 = -150.
        # However, crop_left cannot be negative, so it should be 0.
        # This means the face will be at the left edge of the output if it's too far off.
        # The function's logic ensures the face is centered as much as possible without creating negative crop coordinates.
        # So, if face_center_x_scaled - (PHOTO_SIZE_PIXELS / 2) < 0, then crop_left = 0
        # And crop_right = PHOTO_SIZE_PIXELS
        
        # Let's recalculate based on the function's actual centering logic:
        # scaled_face_center_x = (PHOTO_SIZE_PIXELS / 4) * crop_data['scale_factor']
        # expected_crop_left = scaled_face_center_x - (PHOTO_SIZE_PIXELS / 2)
        # expected_crop_right = scaled_face_center_x + (PHOTO_SIZE_PIXELS / 2)
        # If expected_crop_left < 0, it's adjusted.
        # If expected_crop_right > scaled_img_width, it's adjusted.
        
        # Given face_center_x = 150 and scale_factor ~1.0:
        # scaled_face_center_x = 150
        # crop_left would be 150 - 300 = -150. Since crop_left must be >=0, it becomes 0.
        # crop_right would be 0 + 600 = 600.
        # This effectively means the original left part of the image is used.
        # The face, originally centered at 150px, will now appear at 150px in the 600px output image.
        # This is not "centered" in the output if it's too far off. The function centers the *crop box*
        # around the scaled face center, as long as the crop box stays within the scaled image boundaries.

        # If the face is very off-center, the crop box will shift to include the face,
        # but the face itself might not be perfectly in the middle of the 600x600 output
        # if doing so would mean sampling outside the original image.
        
        # The current logic:
        # crop_left = scaled_face_center_x - half_crop_width
        # crop_right = scaled_face_center_x + half_crop_width
        # Then, adjustments are made if crop_left < 0 or crop_right > scaled_width
        
        scaled_face_center_x = (PHOTO_SIZE_PIXELS / 4) * crop_data['scale_factor'] # approx 150
        half_crop_width = PHOTO_SIZE_PIXELS / 2 # 300

        # crop_left would be 150 - 300 = -150. The code adjusts this:
        # if self.crop_left < 0:
        #     self.crop_right -= self.crop_left # self.crop_right = self.crop_right - (-150) = self.crop_right + 150
        #     self.crop_left = 0
        # So, crop_left becomes 0. crop_right becomes (150+300) + 150 = 600.
        self.assertAlmostEqual(crop_data['crop_left'], 0, delta=5,
                               msg=f"Expected crop_left to be 0 due to face being far left, got {crop_data['crop_left']}")
        self.assertAlmostEqual(crop_data['crop_right'], PHOTO_SIZE_PIXELS, delta=5,
                               msg=f"Expected crop_right to be {PHOTO_SIZE_PIXELS} due to adjustment, got {crop_data['crop_right']}")

    @patch('face_analyzer.FaceAnalyzer')
    def test_eye_level_high_in_head(self, MockFaceAnalyzer):
        # Scenario: Eyes are very high in the head (e.g., 20% from top, 80% from chin)
        # Head height is kept ideal (1.16 inches = 348px)
        # Eye level should push eye_to_bottom towards its lower allowed limit if not constrained by head top.
        mock_analyzer_instance = MockFaceAnalyzer.return_value
        
        head_height_px = 1.16 * PIXELS_PER_INCH # 348px
        eye_level_px = 100 #  Arbitrary eye level for the original large image
        head_top_px = eye_level_px - (head_height_px * 0.20) # Eyes high, so small distance to top
        chin_bottom_px = eye_level_px + (head_height_px * 0.80) # Large distance to chin

        mock_analyzer_instance.get_head_measurements.return_value = (
            head_top_px,
            chin_bottom_px,
            eye_level_px,
            PHOTO_SIZE_PIXELS / 2 # Centered
        )

        mock_landmarks = MagicMock()
        img_height, img_width = PHOTO_SIZE_PIXELS * 2, PHOTO_SIZE_PIXELS * 2 # Simulate larger image initially

        crop_data = calculate_crop_dimensions(mock_landmarks, img_height, img_width)

        # Assertions
        # Head height should be targeted
        self.assertTrue(1.0 <= crop_data['head_height'] <= 1.375)
        self.assertAlmostEqual(crop_data['head_height'], 1.16, delta=0.05)
        
        # Eye-to-bottom should be in range. With eyes high, it means more space below the eyes.
        # The function tries to place eye level at 1.125 + (1.375-1.125)/2 from bottom of photo if possible.
        # Or more precisely, it targets (PHOTO_SIZE_PIXELS - eye_level_on_photo_px) / PIXELS_PER_INCH
        # The logic for vertical positioning:
        # 1. Scale is determined by head height.
        # 2. Scaled eye_level is calculated.
        # 3. crop_top is set based on eye_level_scaled - (TARGET_EYE_TO_TOP_OF_HEAD_INCHES * PIXELS_PER_INCH)
        #    where TARGET_EYE_TO_TOP_OF_HEAD_INCHES is derived from (head_height_inches * proportion_above_eyes_target)
        #    This means the top of head position is prioritized based on average proportions.
        # 4. crop_bottom = crop_top + PHOTO_SIZE_PIXELS
        # 5. eye_to_bottom is then calculated based on this crop.
        
        # Given the logic, the final eye_to_bottom is more influenced by the target head proportions
        # than the initial raw eye_level_px if head height scaling is dominant.
        # It will attempt to place the scaled eye level such that the head fits the 1 to 1.375 inch requirement,
        # and the eye line is about 45% from top of head.
        # So, eye_to_bottom should be near the typical target (around 1.125 to 1.25)
        self.assertTrue(1.125 <= crop_data['eye_to_bottom'] <= 1.375,
                        f"Eye-to-bottom {crop_data['eye_to_bottom']:.3f} out of range for eyes high in head.")
        # We expect it to be closer to the lower end of the valid range, as the function tries to position
        # the chin based on the scaled head height, and eyes are high in that detected head.
        # The actual 'eye_to_bottom' is (PHOTO_SIZE_PIXELS - (scaled_eye_y - crop_data['crop_top'])) / PIXELS_PER_INCH
        # This test helps ensure that even with unusual initial proportions, the final crop is compliant.
        # A specific value is hard to predict without re-running the exact internal logic, but it must be in range.


    @patch('face_analyzer.FaceAnalyzer')
    def test_eye_level_low_in_head(self, MockFaceAnalyzer):
        # Scenario: Eyes are very low in the head (e.g., 80% from top, 20% from chin)
        mock_analyzer_instance = MockFaceAnalyzer.return_value
        
        head_height_px = 1.16 * PIXELS_PER_INCH # 348px
        eye_level_px = 300 # Arbitrary eye level
        head_top_px = eye_level_px - (head_height_px * 0.80) # Eyes low, so large distance to top
        chin_bottom_px = eye_level_px + (head_height_px * 0.20) # Small distance to chin
        
        mock_analyzer_instance.get_head_measurements.return_value = (
            head_top_px,
            chin_bottom_px,
            eye_level_px,
            PHOTO_SIZE_PIXELS / 2 # Centered
        )

        mock_landmarks = MagicMock()
        img_height, img_width = PHOTO_SIZE_PIXELS * 2, PHOTO_SIZE_PIXELS * 2

        crop_data = calculate_crop_dimensions(mock_landmarks, img_height, img_width)

        # Assertions
        self.assertTrue(1.0 <= crop_data['head_height'] <= 1.375)
        self.assertAlmostEqual(crop_data['head_height'], 1.16, delta=0.05)
        
        # With eyes low in the head, after scaling for head height,
        # the eye line in the final crop should still allow eye_to_bottom to be in range.
        # The function will position the head based on the target head height, and then derive
        # the eye line based on a typical proportion (e.g. 45% from top of head).
        # This means the original "low in head" feature might be less prominent in the final crop's measurements.
        self.assertTrue(1.125 <= crop_data['eye_to_bottom'] <= 1.375,
                        f"Eye-to-bottom {crop_data['eye_to_bottom']:.3f} out of range for eyes low in head.")


if __name__ == '__main__':
    unittest.main()
