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
from utils import PIXELS_PER_INCH # PHOTO_SIZE_PIXELS will be derived from spec
from photo_specs import PhotoSpecification # Import for type hinting and creating mock spec

# For type hinting and spec for MagicMock if needed
# from gfpgan import GFPGANer
# import onnxruntime as ort
# import mediapipe as mp

# Helper to create a mock PhotoSpecification for tests
def create_mock_test_spec(
    photo_width_mm=50.8, photo_height_mm=50.8, dpi=300,
    head_min_mm=25.0, head_max_mm=35.0,
    eye_min_from_bottom_mm=28.0, eye_max_from_bottom_mm=35.0,
    background_color: str = "white" # Add background_color parameter
):
    spec = MagicMock(spec=PhotoSpecification)
    spec.country_code = "TestCountry"
    spec.document_name = "TestDoc"
    spec.photo_width_mm = photo_width_mm
    spec.photo_height_mm = photo_height_mm
    spec.dpi = dpi
    spec.MM_PER_INCH = 25.4 # Class variable, but good to have on mock for direct access if needed

    spec.photo_width_px = int(photo_width_mm / spec.MM_PER_INCH * dpi)
    spec.photo_height_px = int(photo_height_mm / spec.MM_PER_INCH * dpi)

    spec.head_min_mm = head_min_mm
    spec.head_max_mm = head_max_mm
    spec.head_min_px = int(head_min_mm / spec.MM_PER_INCH * dpi) if head_min_mm else None
    spec.head_max_px = int(head_max_mm / spec.MM_PER_INCH * dpi) if head_max_mm else None
    
    spec.eye_min_from_bottom_mm = eye_min_from_bottom_mm
    spec.eye_max_from_bottom_mm = eye_max_from_bottom_mm
    spec.eye_min_from_bottom_px = int(eye_min_from_bottom_mm / spec.MM_PER_INCH * dpi) if eye_min_from_bottom_mm else None
    spec.eye_max_from_bottom_px = int(eye_max_from_bottom_mm / spec.MM_PER_INCH * dpi) if eye_max_from_bottom_mm else None

    # For eye_from_top, derive from bottom if bottom is available
    if spec.eye_min_from_bottom_px and spec.eye_max_from_bottom_px:
        spec.eye_min_from_top_px = spec.photo_height_px - spec.eye_max_from_bottom_px
        spec.eye_max_from_top_px = spec.photo_height_px - spec.eye_min_from_bottom_px
    else:
        spec.eye_min_from_top_px = None
        spec.eye_max_from_top_px = None
        
    spec.distance_top_of_head_to_top_of_photo_min_mm = None # Can add if needed for specific tests
    spec.distance_top_of_head_to_top_of_photo_max_mm = None
    spec.distance_top_of_head_to_top_of_photo_min_px = None
    spec.distance_top_of_head_to_top_of_photo_max_px = None
    spec.background_color = background_color # Set the attribute

    return spec


class TestVisaPhotoProcessor(unittest.TestCase):

    def setUp(self):
        self.mock_gfpganer = MagicMock()
        self.mock_ort_session = MagicMock()
        self.mock_face_mesh = MagicMock()
        
        # Create a default mock PhotoSpecification for the processor
        # Let's use "light_grey" for testing the background color change
        self.mock_spec = create_mock_test_spec(background_color="light_grey") 

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
            photo_spec=self.mock_spec, # Pass the mock spec
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

        # Mock crop_data returned by the refactored calculate_crop_dimensions
        mock_crop_data_returned_by_analyzer = {
            'scale_factor': 1.0,
            'crop_top': 0, 'crop_bottom': self.mock_spec.photo_height_px, 
            'crop_left': 0, 'crop_right': self.mock_spec.photo_width_px,
            'final_photo_width_px': self.mock_spec.photo_width_px,
            'final_photo_height_px': self.mock_spec.photo_height_px,
            'achieved_head_height_px': int((self.mock_spec.head_min_px + self.mock_spec.head_max_px) / 2), # e.g. 356px
            'achieved_eye_level_from_top_px': self.mock_spec.photo_height_px - \
                                           int((self.mock_spec.eye_min_from_bottom_px + self.mock_spec.eye_max_from_bottom_px) / 2) # e.g. 228px
        }
        mock_calculate_crop.return_value = mock_crop_data_returned_by_analyzer

        mock_pil_img_after_crop = MagicMock(spec=Image.Image)
        mock_pil_img_after_crop.size = (self.mock_spec.photo_width_px, self.mock_spec.photo_height_px) # Ensure it has a size
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
            mock_img_cv_array.shape[1],
            self.mock_spec # Ensure spec is passed
        )
        mock_crop_scale.assert_called_once_with(mock_img_cv_array, mock_crop_data_returned_by_analyzer)
        
        # Define expected RGB for "light_grey" (must match BACKGROUND_COLOR_MAP in image_processing.py)
        expected_light_grey_rgb = (211, 211, 211) 
        mock_remove_bg.assert_called_once_with(mock_pil_img_after_crop, self.mock_ort_session, expected_light_grey_rgb)
        
        mock_enhance.assert_called_once_with(mock_pil_img_after_bg_remove)
        
        # Check save call on the mock object returned by _enhance_image
        mock_pil_img_after_enhance.save.assert_called_once_with(
            self.processed_path, dpi=(self.mock_spec.dpi, self.mock_spec.dpi), quality=95
        )

        # Prepare expected preview_crop_data (in inches)
        mm_per_pixel = PhotoSpecification.MM_PER_INCH / self.mock_spec.dpi
        achieved_head_height_mm_for_preview = mock_crop_data_returned_by_analyzer['achieved_head_height_px'] * mm_per_pixel
        achieved_eye_level_from_top_mm_for_preview = mock_crop_data_returned_by_analyzer['achieved_eye_level_from_top_px'] * mm_per_pixel
        achieved_eye_level_from_bottom_mm_for_preview = self.mock_spec.photo_height_mm - achieved_eye_level_from_top_mm_for_preview
        
        expected_preview_data = {
            'head_height': achieved_head_height_mm_for_preview / PhotoSpecification.MM_PER_INCH,
            'eye_to_bottom': achieved_eye_level_from_bottom_mm_for_preview / PhotoSpecification.MM_PER_INCH,
        }

        mock_create_preview.assert_called_once_with(
            self.processed_path, self.preview_path, 
            expected_preview_data, # Check the content of this
            mock_face_results.multi_face_landmarks[0], 
            self.dummy_fonts_folder
        )
        mock_create_printable.assert_called_once_with(
            self.processed_path, self.printable_path, self.dummy_fonts_folder, 
            rows=2, cols=2, photo_spec=self.mock_spec
        )
        mock_create_printable_preview.assert_called_once_with(
            self.processed_path, self.printable_preview_path, self.dummy_fonts_folder, 
            rows=2, cols=2, photo_spec=self.mock_spec
        )

        # Assert photo_info structure (new structure)
        self.assertIn('achieved_head_height_mm', photo_info)
        self.assertIn('spec_head_height_range_mm', photo_info)
        self.assertIn('achieved_eye_level_from_bottom_mm', photo_info)
        self.assertIn('spec_eye_level_range_from_bottom_mm', photo_info)
        self.assertEqual(photo_info['file_size_kb'], round(mock_getsize.return_value / 1024, 2))
        self.assertEqual(photo_info['photo_dimensions_px'], f"{self.mock_spec.photo_width_px}x{self.mock_spec.photo_height_px} @ {self.mock_spec.dpi} DPI")
        self.assertTrue(photo_info['compliance']['head_height']) # Based on mock_crop_data and mock_spec
        self.assertTrue(photo_info['compliance']['eye_position'])

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
    def test_crop_and_scale_logic_with_padding(self, mock_create_image_with_padding):
        input_cv_img = np.random.randint(0, 255, size=(800, 1000, 3), dtype=np.uint8)
        
        # crop_data_from_analyzer should reflect what calculate_crop_dimensions returns
        crop_data_from_analyzer = {
            'scale_factor': 0.5, 
            'crop_top': 50, 'crop_bottom': 350,  # Results in 300 height
            'crop_left': 100, 'crop_right': 400, # Results in 300 width
            'final_photo_width_px': 300, # Analyzer intended this before padding
            'final_photo_height_px': 300
        }
        
        # self.mock_spec is 600x600px. Since 300x300 != 600x600, padding will be called.
        mock_padded_image = MagicMock(spec=Image.Image)
        mock_padded_image.size = (self.mock_spec.photo_width_px, self.mock_spec.photo_height_px)
        mock_create_image_with_padding.return_value = mock_padded_image

        result_pil_img = self.processor._crop_and_scale_image(input_cv_img, crop_data_from_analyzer)

        self.assertIsInstance(result_pil_img, Image.Image)
        
        mock_create_image_with_padding.assert_called_once()
        call_args_padding = mock_create_image_with_padding.call_args[0]
        pil_image_to_pad = call_args_padding[0]
        self.assertIsInstance(pil_image_to_pad, Image.Image)
        # Size of image passed to padding should be the cropped size
        self.assertEqual(pil_image_to_pad.size, 
                         (crop_data_from_analyzer['crop_right'] - crop_data_from_analyzer['crop_left'], 
                          crop_data_from_analyzer['crop_bottom'] - crop_data_from_analyzer['crop_top']))
        
        # Target size for padding should be from spec
        self.assertEqual(mock_create_image_with_padding.call_args[1]['target_size'], 
                         (self.mock_spec.photo_width_px, self.mock_spec.photo_height_px))

        self.assertEqual(result_pil_img.size, (self.mock_spec.photo_width_px, self.mock_spec.photo_height_px))
        self.assertIs(result_pil_img, mock_padded_image)

    def test_crop_and_scale_no_padding_needed(self):
        input_cv_img = np.random.randint(0, 255, size=(1200, 1200, 3), dtype=np.uint8)
        
        # crop_data results in a crop that matches spec's final photo dimensions
        crop_data_from_analyzer = {
            'scale_factor': 0.5, # Scales 1200x1200 to 600x600
            'crop_top': 0, 'crop_bottom': self.mock_spec.photo_height_px, 
            'crop_left': 0, 'crop_right': self.mock_spec.photo_width_px,
            'final_photo_width_px': self.mock_spec.photo_width_px, # Analyzer intended this
            'final_photo_height_px': self.mock_spec.photo_height_px 
        }

        with patch('image_processing.utils.create_image_with_padding') as mock_no_padding_call:
            result_pil_img = self.processor._crop_and_scale_image(input_cv_img, crop_data_from_analyzer)
            mock_no_padding_call.assert_not_called()

        self.assertIsInstance(result_pil_img, Image.Image)
        self.assertEqual(result_pil_img.size, (self.mock_spec.photo_width_px, self.mock_spec.photo_height_px))


    # --- Tests for _enhance_image ---
    def test_enhance_image_calls_gfpgan(self):
        # Create a mock PIL Image that matches spec dimensions
        mock_input_pil_image = MagicMock(spec=Image.Image)
        mock_input_pil_image.size = (self.mock_spec.photo_width_px, self.mock_spec.photo_height_px)
        mock_input_pil_image.mode = 'RGB' 

        mock_restored_cv2_array = np.zeros((self.mock_spec.photo_height_px, self.mock_spec.photo_width_px, 3), dtype=np.uint8)
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

    @patch('image_processing.printable_creator.create_printable_preview')
    @patch('image_processing.printable_creator.create_printable_image')
    @patch('image_processing.preview_creator.create_preview_with_watermark')
    @patch('PIL.Image.Image.save')
    @patch.object(VisaPhotoProcessor, '_enhance_image')
    @patch('image_processing.remove_background_and_make_white')
    @patch.object(VisaPhotoProcessor, '_crop_and_scale_image')
    @patch('image_processing.calculate_crop_dimensions')
    @patch('cv2.imread')
    @patch('os.path.getsize')
    def test_process_with_schengen_spec_non_compliant_head(self, mock_getsize, mock_cv2_imread, 
                                                        mock_calculate_crop, mock_crop_scale, 
                                                        mock_remove_bg, mock_enhance, mock_pil_save,
                                                        mock_create_preview, mock_create_printable, 
                                                        mock_create_printable_preview):
        mock_socketio = MagicMock()
        
        # 1. Create Schengen Spec (35x45mm, head 32-36mm, light_grey bg)
        schengen_spec = create_mock_test_spec(
            photo_width_mm=35, photo_height_mm=45, dpi=300,
            head_min_mm=32, head_max_mm=36, # approx 378px to 425px at 300DPI for 45mm height photo
            eye_min_from_bottom_mm=29, eye_max_from_bottom_mm=34, # approx 342px to 401px
            background_color="light_grey"
        )
        self.processor.photo_spec = schengen_spec # Override default spec for this test

        # 2. Configure Mocks
        mock_cv2_imread.return_value = np.zeros((600, 800, 3), dtype=np.uint8)
        mock_face_results = MagicMock(); mock_face_results.multi_face_landmarks = [MagicMock()]
        self.mock_face_mesh.process.return_value = mock_face_results
        
        # Mock crop_data: head height too small (e.g., 30mm / ~354px)
        # 30mm * 300dpi / 25.4 mm/inch = 354.33 px. Spec min is 32mm = 377.95px
        achieved_head_height_px_non_compliant = int(30 * schengen_spec.dpi / PhotoSpecification.MM_PER_INCH) 
        
        # Eye position compliant (mid-range of 29-34mm from bottom)
        # Mid eye from bottom = 31.5mm. Eye from top on 45mm photo = 45-31.5 = 13.5mm
        # 13.5mm * 300dpi / 25.4 mm/inch = ~159px from top
        achieved_eye_level_from_top_px_compliant = int( (schengen_spec.photo_height_mm - \
            ((schengen_spec.eye_min_from_bottom_mm + schengen_spec.eye_max_from_bottom_mm) / 2) ) \
            * schengen_spec.dpi / PhotoSpecification.MM_PER_INCH )

        mock_crop_data_returned = {
            'scale_factor': 1.0, 'crop_top': 0, 'crop_bottom': schengen_spec.photo_height_px, 
            'crop_left': 0, 'crop_right': schengen_spec.photo_width_px,
            'final_photo_width_px': schengen_spec.photo_width_px,
            'final_photo_height_px': schengen_spec.photo_height_px,
            'achieved_head_height_px': achieved_head_height_px_non_compliant,
            'achieved_eye_level_from_top_px': achieved_eye_level_from_top_px_compliant
        }
        mock_calculate_crop.return_value = mock_crop_data_returned
        
        mock_pil_img_after_crop = MagicMock(spec=Image.Image); mock_pil_img_after_crop.size = (schengen_spec.photo_width_px, schengen_spec.photo_height_px)
        mock_crop_scale.return_value = mock_pil_img_after_crop
        mock_remove_bg.return_value = MagicMock(spec=Image.Image)
        mock_enhance.return_value = MagicMock(spec=Image.Image)
        mock_getsize.return_value = 100 * 1024

        # 3. Call process_with_updates
        photo_info = self.processor.process_with_updates(mock_socketio)

        # 4. Assertions
        self.assertFalse(photo_info['compliance']['head_height'], "Head height should be non-compliant")
        self.assertTrue(photo_info['compliance']['eye_position'], "Eye position should be compliant")
        
        expected_light_grey_rgb = (211, 211, 211) # From BACKGROUND_COLOR_MAP
        mock_remove_bg.assert_called_once_with(mock_pil_img_after_crop, self.mock_ort_session, expected_light_grey_rgb)

    @patch('image_processing.printable_creator.create_printable_preview')
    @patch('image_processing.printable_creator.create_printable_image')
    @patch('image_processing.preview_creator.create_preview_with_watermark')
    @patch('PIL.Image.Image.save')
    @patch.object(VisaPhotoProcessor, '_enhance_image')
    @patch('image_processing.remove_background_and_make_white')
    @patch.object(VisaPhotoProcessor, '_crop_and_scale_image')
    @patch('image_processing.calculate_crop_dimensions')
    @patch('cv2.imread')
    @patch('os.path.getsize')
    def test_process_with_canada_spec_non_compliant_eyes(self, mock_getsize, mock_cv2_imread, 
                                                       mock_calculate_crop, mock_crop_scale, 
                                                       mock_remove_bg, mock_enhance, mock_pil_save,
                                                       mock_create_preview, mock_create_printable, 
                                                       mock_create_printable_preview):
        mock_socketio = MagicMock()

        # 1. Create Canada Spec (50x70mm, head 31-36mm, white bg, eye from top 17-23mm (example))
        # For this test, we'll use eye_min_from_top_mm and eye_max_from_top_mm
        # Let's ensure create_mock_test_spec is adapted or we set these directly
        canada_spec = create_mock_test_spec(
            photo_width_mm=50, photo_height_mm=70, dpi=300,
            head_min_mm=31, head_max_mm=36,
            eye_min_from_bottom_mm=None, eye_max_from_bottom_mm=None, # Clear bottom specs
            background_color="white"
        )
        # Set eye_from_top explicitly for Canada spec test
        canada_spec.eye_min_from_top_mm = 17.0 
        canada_spec.eye_max_from_top_mm = 23.0
        canada_spec.eye_min_from_top_px = int(17.0 / 25.4 * 300) # approx 200px
        canada_spec.eye_max_from_top_px = int(23.0 / 25.4 * 300) # approx 271px
        self.processor.photo_spec = canada_spec

        # 2. Configure Mocks
        mock_cv2_imread.return_value = np.zeros((1000, 800, 3), dtype=np.uint8)
        mock_face_results = MagicMock(); mock_face_results.multi_face_landmarks = [MagicMock()]
        self.mock_face_mesh.process.return_value = mock_face_results
        
        # Mock crop_data: head height compliant, eye position non-compliant (too high from top)
        achieved_head_height_px_compliant = int((canada_spec.head_min_mm + canada_spec.head_max_mm) / 2 * canada_spec.dpi / PhotoSpecification.MM_PER_INCH)
        # Eye level too high (e.g., 15mm from top, spec is 17-23mm)
        achieved_eye_level_from_top_px_non_compliant = int(15.0 * canada_spec.dpi / PhotoSpecification.MM_PER_INCH)

        mock_crop_data_returned = {
            'scale_factor': 0.8, 'crop_top': 0, 'crop_bottom': canada_spec.photo_height_px,
            'crop_left': 0, 'crop_right': canada_spec.photo_width_px,
            'final_photo_width_px': canada_spec.photo_width_px,
            'final_photo_height_px': canada_spec.photo_height_px,
            'achieved_head_height_px': achieved_head_height_px_compliant,
            'achieved_eye_level_from_top_px': achieved_eye_level_from_top_px_non_compliant
        }
        mock_calculate_crop.return_value = mock_crop_data_returned
        
        mock_pil_img_after_crop = MagicMock(spec=Image.Image); mock_pil_img_after_crop.size = (canada_spec.photo_width_px, canada_spec.photo_height_px)
        mock_crop_scale.return_value = mock_pil_img_after_crop
        mock_remove_bg.return_value = MagicMock(spec=Image.Image)
        mock_enhance.return_value = MagicMock(spec=Image.Image)
        mock_getsize.return_value = 200 * 1024

        # 3. Call process_with_updates
        photo_info = self.processor.process_with_updates(mock_socketio)

        # 4. Assertions
        self.assertTrue(photo_info['compliance']['head_height'], "Head height should be compliant")
        self.assertFalse(photo_info['compliance']['eye_position'], "Eye position should be non-compliant")
        
        expected_white_rgb = (255, 255, 255) # From BACKGROUND_COLOR_MAP for "white"
        mock_remove_bg.assert_called_once_with(mock_pil_img_after_crop, self.mock_ort_session, expected_white_rgb)


if __name__ == '__main__':
    unittest.main()
