import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from face_analyzer import calculate_crop_dimensions, FaceAnalyzer
from utils import PIXELS_PER_INCH 
from photo_specs import PhotoSpecification # Import PhotoSpecification

# Helper to create a PhotoSpecification instance for tests
def create_test_spec(
    photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
    head_min_mm=25.0, head_max_mm=35.0,
    eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
    eye_min_from_top_mm=None, eye_max_from_top_mm=None
):
    spec = PhotoSpecification(
        country_code="Test", document_name="TestDoc",
        photo_width_mm=photo_width_mm, photo_height_mm=photo_height_mm, dpi=dpi,
        head_min_mm=head_min_mm, head_max_mm=head_max_mm,
        eye_min_from_bottom_mm=eye_min_from_bottom_mm, eye_max_from_bottom_mm=eye_max_from_bottom_mm,
        eye_min_from_top_mm=eye_min_from_top_mm, eye_max_from_top_mm=eye_max_from_top_mm
    )
    return spec

class TestCalculateCropDimensions(unittest.TestCase):

    def setUp(self):
        # Create a default spec for tests, typically 2x2 inch @ 300 DPI (600x600 px)
        self.default_spec = create_test_spec()
        # PHOTO_SIZE_PIXELS equivalent for this default spec
        self.PHOTO_SIZE_PIXELS_EQUIV = self.default_spec.photo_width_px 


    @patch('face_analyzer.FaceAnalyzer')
    def test_ideal_conditions(self, MockFaceAnalyzer):
        mock_analyzer_instance = MockFaceAnalyzer.return_value
        spec = self.default_spec

        # Input image dimensions (can be different from final photo spec)
        img_height, img_width = 800, 800 

        # Mock measurements from FaceAnalyzer, relative to input image size
        # Target head height in spec: (25mm to 35mm). Mid-point: 30mm.
        # 30mm @ 300 DPI = 30 / 25.4 * 300 = ~354px
        # Target eye level from bottom: (28mm to 35mm). Mid-point: 31.5mm
        # 31.5mm @ 300 DPI = ~372px from bottom.
        # Eye level from top on final 600px photo = 600 - 372 = 228px.
        
        # Let's assume the original head on the 800x800 input image is 2x the target pixel size
        # So, scale factor will be ~0.5
        original_head_height_px = spec.head_min_px * 2 # e.g., 25mm*300/25.4 * 2 = ~590px
        
        # Original eye level such that after scaling by ~0.5, it meets the spec on the 600px photo
        # Target eye from top on final photo: spec.photo_height_px - spec.eye_max_from_bottom_px (min eye from top)
        # or spec.photo_height_px - spec.eye_min_from_bottom_px (max eye from top)
        # Let's target mid-range for eye position on final photo
        target_eye_level_from_top_final_px = spec.photo_height_px - \
            ((spec.eye_min_from_bottom_px + spec.eye_max_from_bottom_px) / 2)

        original_eye_level_px = target_eye_level_from_top_final_px / 0.5 # Scaled back to original image size
        
        original_head_top_px = original_eye_level_px - (original_head_height_px * 0.45) # Assuming 45% of head is above eyes
        original_chin_bottom_px = original_head_top_px + original_head_height_px
        original_face_center_x_px = img_width / 2
        
        mock_analyzer_instance.get_head_measurements.return_value = (
            original_head_top_px, original_chin_bottom_px, original_eye_level_px, original_face_center_x_px
        )
        mock_landmarks = MagicMock()

        crop_data = calculate_crop_dimensions(mock_landmarks, img_height, img_width, spec)

        # Assertions
        self.assertEqual(crop_data['final_photo_width_px'], spec.photo_width_px)
        self.assertEqual(crop_data['final_photo_height_px'], spec.photo_height_px)

        self.assertTrue(spec.head_min_px <= crop_data['achieved_head_height_px'] <= spec.head_max_px,
                        f"Achieved head height {crop_data['achieved_head_height_px']}px out of spec range [{spec.head_min_px}, {spec.head_max_px}]px")
        
        achieved_eye_level_from_bottom_px = spec.photo_height_px - crop_data['achieved_eye_level_from_top_px']
        self.assertTrue(spec.eye_min_from_bottom_px <= achieved_eye_level_from_bottom_px <= spec.eye_max_from_bottom_px,
                        f"Achieved eye level from bottom {achieved_eye_level_from_bottom_px}px out of spec range [{spec.eye_min_from_bottom_px}, {spec.eye_max_from_bottom_px}]px")
        
        self.assertAlmostEqual(crop_data['scale_factor'], spec.head_min_px / original_head_height_px, delta=0.1) # Or some other target scale

        self.assertEqual(crop_data['crop_right'] - crop_data['crop_left'], spec.photo_width_px)
        self.assertEqual(crop_data['crop_bottom'] - crop_data['crop_top'], spec.photo_height_px)

    @patch('face_analyzer.FaceAnalyzer')
    def test_face_too_small(self, MockFaceAnalyzer):
        mock_analyzer_instance = MockFaceAnalyzer.return_value
        spec = self.default_spec
        img_height, img_width = spec.photo_height_px, spec.photo_width_px # Input image size same as target for simplicity

        # Small head on input: 50px height. Spec min is spec.head_min_px (e.g. ~300px)
        original_head_height_px = 50 
        original_eye_level_px = 100 
        original_head_top_px = original_eye_level_px - (original_head_height_px * 0.45) 
        original_chin_bottom_px = original_head_top_px + original_head_height_px
        original_face_center_x_px = img_width / 2

        mock_analyzer_instance.get_head_measurements.return_value = (
            original_head_top_px, original_chin_bottom_px, original_eye_level_px, original_face_center_x_px
        )
        mock_landmarks = MagicMock()

        crop_data = calculate_crop_dimensions(mock_landmarks, img_height, img_width, spec)

        self.assertGreater(crop_data['scale_factor'], 1.0)
        self.assertTrue(spec.head_min_px <= crop_data['achieved_head_height_px'] <= spec.head_max_px)
        self.assertAlmostEqual(crop_data['achieved_head_height_px'], spec.head_min_px, delta=5) # Should scale up to min

        achieved_eye_level_from_bottom_px = spec.photo_height_px - crop_data['achieved_eye_level_from_top_px']
        self.assertTrue(spec.eye_min_from_bottom_px <= achieved_eye_level_from_bottom_px <= spec.eye_max_from_bottom_px)

    @patch('face_analyzer.FaceAnalyzer')
    def test_face_too_large(self, MockFaceAnalyzer):
        mock_analyzer_instance = MockFaceAnalyzer.return_value
        spec = self.default_spec
        img_height, img_width = spec.photo_height_px, spec.photo_width_px

        # Large head on input: e.g. 500px. Spec max is spec.head_max_px (e.g. ~412px)
        original_head_height_px = spec.head_max_px + 100 
        original_eye_level_px = img_height / 2
        original_head_top_px = original_eye_level_px - (original_head_height_px * 0.45) 
        original_chin_bottom_px = original_head_top_px + original_head_height_px
        original_face_center_x_px = img_width / 2
        
        mock_analyzer_instance.get_head_measurements.return_value = (
            original_head_top_px, original_chin_bottom_px, original_eye_level_px, original_face_center_x_px
        )
        mock_landmarks = MagicMock()

        crop_data = calculate_crop_dimensions(mock_landmarks, img_height, img_width, spec)

        self.assertLess(crop_data['scale_factor'], 1.0)
        self.assertTrue(spec.head_min_px <= crop_data['achieved_head_height_px'] <= spec.head_max_px)
        self.assertAlmostEqual(crop_data['achieved_head_height_px'], spec.head_max_px, delta=5) # Should scale down to max

        achieved_eye_level_from_bottom_px = spec.photo_height_px - crop_data['achieved_eye_level_from_top_px']
        self.assertTrue(spec.eye_min_from_bottom_px <= achieved_eye_level_from_bottom_px <= spec.eye_max_from_bottom_px)

    @patch('face_analyzer.FaceAnalyzer')
    def test_face_off_center(self, MockFaceAnalyzer):
        mock_analyzer_instance = MockFaceAnalyzer.return_value
        spec = self.default_spec
        img_height, img_width = 800, 800 # Larger input image

        # Head size is ideal for spec after scaling (e.g. scale factor ~1 relative to spec pixel sizes)
        original_head_height_px = (spec.head_min_px + spec.head_max_px) / 2 
        original_eye_level_px = (spec.photo_height_px - ((spec.eye_min_from_bottom_px + spec.eye_max_from_bottom_px) / 2))
        original_head_top_px = original_eye_level_px - (original_head_height_px * 0.45)
        original_chin_bottom_px = original_head_top_px + original_head_height_px
        
        original_face_center_x_px = img_width / 4 # Face significantly to the left
        
        mock_analyzer_instance.get_head_measurements.return_value = (
            original_head_top_px, original_chin_bottom_px, original_eye_level_px, original_face_center_x_px
        )
        mock_landmarks = MagicMock()

        crop_data = calculate_crop_dimensions(mock_landmarks, img_height, img_width, spec)

        self.assertTrue(spec.head_min_px <= crop_data['achieved_head_height_px'] <= spec.head_max_px)
        achieved_eye_level_from_bottom_px = spec.photo_height_px - crop_data['achieved_eye_level_from_top_px']
        self.assertTrue(spec.eye_min_from_bottom_px <= achieved_eye_level_from_bottom_px <= spec.eye_max_from_bottom_px)
        
        # Check centering: crop_left should be 0 if face is too far left
        # and the final crop width matches spec.photo_width_px
        self.assertEqual(crop_data['crop_right'] - crop_data['crop_left'], spec.photo_width_px)
        # Exact crop_left value depends on detailed logic of how much it shifts.
        # If scaled face center is less than half target width, crop_left becomes 0.
        scaled_face_center_x = original_face_center_x_px * crop_data['scale_factor']
        if scaled_face_center_x < spec.photo_width_px / 2:
            self.assertAlmostEqual(crop_data['crop_left'], 0, delta=5)
        
    @patch('face_analyzer.FaceAnalyzer')
    def test_eye_level_high_in_head(self, MockFaceAnalyzer):
        mock_analyzer_instance = MockFaceAnalyzer.return_value
        spec = self.default_spec
        img_height, img_width = 800, 800 
        
        original_head_height_px = (spec.head_min_px + spec.head_max_px) / 2 / crop_data['scale_factor'] if 'scale_factor' in locals() else (spec.head_min_px + spec.head_max_px) / 2 # approx
        original_eye_level_px = img_height * 0.3 # Eyes relatively high on the input image
        original_head_top_px = original_eye_level_px - (original_head_height_px * 0.20) # Eyes high in head (20% from top of head)
        original_chin_bottom_px = original_head_top_px + original_head_height_px
        original_face_center_x_px = img_width / 2
        
        mock_analyzer_instance.get_head_measurements.return_value = (
            original_head_top_px, original_chin_bottom_px, original_eye_level_px, original_face_center_x_px
        )
        mock_landmarks = MagicMock()

        crop_data = calculate_crop_dimensions(mock_landmarks, img_height, img_width, spec)

        self.assertTrue(spec.head_min_px <= crop_data['achieved_head_height_px'] <= spec.head_max_px)
        achieved_eye_level_from_bottom_px = spec.photo_height_px - crop_data['achieved_eye_level_from_top_px']
        self.assertTrue(spec.eye_min_from_bottom_px <= achieved_eye_level_from_bottom_px <= spec.eye_max_from_bottom_px)

    @patch('face_analyzer.FaceAnalyzer')
    def test_eye_level_low_in_head(self, MockFaceAnalyzer):
        mock_analyzer_instance = MockFaceAnalyzer.return_value
        spec = self.default_spec
        img_height, img_width = 800, 800

        original_head_height_px = (spec.head_min_px + spec.head_max_px) / 2 / crop_data['scale_factor'] if 'scale_factor' in locals() else (spec.head_min_px + spec.head_max_px) / 2 # approx
        original_eye_level_px = img_height * 0.7 # Eyes relatively low
        original_head_top_px = original_eye_level_px - (original_head_height_px * 0.80) # Eyes low in head (80% from top of head)
        original_chin_bottom_px = original_head_top_px + original_head_height_px
        original_face_center_x_px = img_width / 2

        mock_analyzer_instance.get_head_measurements.return_value = (
            original_head_top_px, original_chin_bottom_px, original_eye_level_px, original_face_center_x_px
        )
        mock_landmarks = MagicMock()

        crop_data = calculate_crop_dimensions(mock_landmarks, img_height, img_width, spec)
        
        self.assertTrue(spec.head_min_px <= crop_data['achieved_head_height_px'] <= spec.head_max_px)
        achieved_eye_level_from_bottom_px = spec.photo_height_px - crop_data['achieved_eye_level_from_top_px']
        self.assertTrue(spec.eye_min_from_bottom_px <= achieved_eye_level_from_bottom_px <= spec.eye_max_from_bottom_px)

    @patch('face_analyzer.FaceAnalyzer')
    def test_calculate_crop_for_schengen_spec(self, MockFaceAnalyzer):
        mock_analyzer_instance = MockFaceAnalyzer.return_value
        # Schengen-like spec: 35x45mm photo, head 32-36mm, eye line 29-34mm from bottom.
        # Let's also include distance_top_of_head for completeness, though current calc may not use it directly.
        schengen_spec = create_test_spec(
            photo_width_mm=35, photo_height_mm=45, dpi=300,
            head_min_mm=32, head_max_mm=36,
            eye_min_from_bottom_mm=29, eye_max_from_bottom_mm=34
        )
        # Add distance_top_of_head if create_test_spec supports it, or set directly on mock
        schengen_spec.distance_top_of_head_to_top_of_photo_min_mm = 2.0
        schengen_spec.distance_top_of_head_to_top_of_photo_max_mm = 6.0
        schengen_spec.distance_top_of_head_to_top_of_photo_min_px = int(2.0 / 25.4 * 300)
        schengen_spec.distance_top_of_head_to_top_of_photo_max_px = int(6.0 / 25.4 * 300)


        img_height, img_width = 600, 500 # Sample input image size

        # Mock measurements from FaceAnalyzer (original image)
        # Target head: 32-36mm. Mid: 34mm. 34/25.4*300 = ~401px. Let original be 200px (needs scaling up)
        original_head_height_px = 200 
        # Target eye from bottom: 29-34mm. Mid: 31.5mm. 31.5/25.4*300 = ~372px from bottom.
        # Target eye from top on 45mm photo (45/25.4*300 = ~531px height): 531 - 372 = ~159px from top.
        # Let original eye level be 100px from top on 600px high image
        original_eye_level_px = 100 
        original_head_top_px = original_eye_level_px - (original_head_height_px * 0.45)
        original_chin_bottom_px = original_head_top_px + original_head_height_px
        original_face_center_x_px = img_width / 2
        
        mock_analyzer_instance.get_head_measurements.return_value = (
            original_head_top_px, original_chin_bottom_px, original_eye_level_px, original_face_center_x_px
        )
        mock_landmarks = MagicMock()

        crop_data = calculate_crop_dimensions(mock_landmarks, img_height, img_width, schengen_spec)

        # Assertions
        self.assertEqual(crop_data['final_photo_width_px'], schengen_spec.photo_width_px)
        self.assertEqual(crop_data['final_photo_height_px'], schengen_spec.photo_height_px)
        self.assertTrue(schengen_spec.head_min_px <= crop_data['achieved_head_height_px'] <= schengen_spec.head_max_px,
                        f"Schengen head height {crop_data['achieved_head_height_px']}px out of spec [{schengen_spec.head_min_px}, {schengen_spec.head_max_px}]px")
        
        achieved_eye_level_from_bottom_px = schengen_spec.photo_height_px - crop_data['achieved_eye_level_from_top_px']
        self.assertTrue(schengen_spec.eye_min_from_bottom_px <= achieved_eye_level_from_bottom_px <= schengen_spec.eye_max_from_bottom_px,
                        f"Schengen eye level {achieved_eye_level_from_bottom_px}px out of spec [{schengen_spec.eye_min_from_bottom_px}, {schengen_spec.eye_max_from_bottom_px}]px")

    @patch('face_analyzer.FaceAnalyzer')
    def test_calculate_crop_for_canada_spec(self, MockFaceAnalyzer):
        mock_analyzer_instance = MockFaceAnalyzer.return_value
        # Canada-like spec: 50x70mm photo, head 31-36mm. Eye line from top 17-23mm (placeholder).
        canada_spec = create_test_spec(
            photo_width_mm=50, photo_height_mm=70, dpi=300,
            head_min_mm=31, head_max_mm=36,
            eye_min_from_bottom_mm=None, eye_max_from_bottom_mm=None, # Using from_top for this test
            eye_min_from_top_mm=17, eye_max_from_top_mm=23 
        )
        # Recalculate px values for eye_from_top as create_test_spec might not do it if bottom is None
        canada_spec.eye_min_from_top_px = int(canada_spec.eye_min_from_top_mm / 25.4 * canada_spec.dpi)
        canada_spec.eye_max_from_top_px = int(canada_spec.eye_max_from_top_mm / 25.4 * canada_spec.dpi)


        img_height, img_width = 1000, 800 # Sample input image size

        # Mock measurements (original image)
        # Target head: 31-36mm. Mid: 33.5mm. 33.5/25.4*300 = ~395px. Let original be 700px (scale down)
        original_head_height_px = 700
        # Target eye from top: 17-23mm. Mid: 20mm. 20/25.4*300 = ~236px from top.
        # Let original eye level be 400px from top.
        original_eye_level_px = 400
        original_head_top_px = original_eye_level_px - (original_head_height_px * 0.45)
        original_chin_bottom_px = original_head_top_px + original_head_height_px
        original_face_center_x_px = img_width / 2

        mock_analyzer_instance.get_head_measurements.return_value = (
            original_head_top_px, original_chin_bottom_px, original_eye_level_px, original_face_center_x_px
        )
        mock_landmarks = MagicMock()

        crop_data = calculate_crop_dimensions(mock_landmarks, img_height, img_width, canada_spec)

        # Assertions
        self.assertEqual(crop_data['final_photo_width_px'], canada_spec.photo_width_px)
        self.assertEqual(crop_data['final_photo_height_px'], canada_spec.photo_height_px)
        self.assertTrue(canada_spec.head_min_px <= crop_data['achieved_head_height_px'] <= canada_spec.head_max_px,
                        f"Canada head height {crop_data['achieved_head_height_px']}px out of spec [{canada_spec.head_min_px}, {canada_spec.head_max_px}]px")
        
        # Assert eye line based on from_top_px for this spec
        self.assertTrue(canada_spec.eye_min_from_top_px <= crop_data['achieved_eye_level_from_top_px'] <= canada_spec.eye_max_from_top_px,
                        f"Canada eye level from top {crop_data['achieved_eye_level_from_top_px']}px out of spec [{canada_spec.eye_min_from_top_px}, {canada_spec.eye_max_from_top_px}]px")


if __name__ == '__main__':
    unittest.main()
