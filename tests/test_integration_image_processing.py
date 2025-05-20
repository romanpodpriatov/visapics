import unittest
from unittest.mock import patch, MagicMock, call
import numpy as np
from PIL import Image, ImageDraw # ImageDraw for creating sample image if needed by tests
import os
import sys
import shutil # For rmtree
import cv2 

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from image_processing import VisaPhotoProcessor
from utils import PHOTO_SIZE_PIXELS, PIXELS_PER_INCH
from gfpgan import GFPGANer
import onnxruntime as ort
import mediapipe as mp
import wget # For GFPGAN download logic
import logging

# Configure logging for tests (optional, but can be helpful)
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TestIntegrationVisaPhotoProcessor(unittest.TestCase):

    gfpganer = None
    ort_session = None
    face_mesh = None
    fonts_folder = None
    
    # Define model paths (relative to project root)
    # These should match the paths used in main.py for consistency
    GFPGAN_MODEL_DIR = os.path.join(PROJECT_ROOT, 'gfpgan', 'weights')
    GFPGAN_MODEL_PATH = os.path.join(GFPGAN_MODEL_DIR, 'GFPGANv1.4.pth')
    
    MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')
    ONNX_MODEL_PATH = os.path.join(MODELS_DIR, 'BiRefNet-portrait-epoch_150.onnx')


    @classmethod
    def setUpClass(cls):
        # Ensure model directories exist
        os.makedirs(cls.GFPGAN_MODEL_DIR, exist_ok=True)
        os.makedirs(cls.MODELS_DIR, exist_ok=True)

        # Initialize GFPGANer
        try:
            if not os.path.exists(cls.GFPGAN_MODEL_PATH):
                logging.info(f"GFPGAN model not found at {cls.GFPGAN_MODEL_PATH}. Downloading...")
                wget.download('https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth', cls.GFPGAN_MODEL_PATH)
                logging.info(f"GFPGAN model downloaded successfully to {cls.GFPGAN_MODEL_PATH}.")
            
            cls.gfpganer = GFPGANer(
                model_path=cls.GFPGAN_MODEL_PATH,
                upscale=1, arch='clean', channel_multiplier=2, bg_upsampler=None
            )
            logging.info("GFPGANer initialized successfully for integration tests.")
        except Exception as e:
            logging.error(f"Failed to initialize GFPGANer: {e}")
            raise unittest.SkipTest(f"Skipping integration tests: GFPGANer initialization failed - {e}")

        # Initialize ONNX Runtime Session for background removal
        try:
            if not os.path.exists(cls.ONNX_MODEL_PATH):
                 raise FileNotFoundError(f"ONNX model not found at {cls.ONNX_MODEL_PATH}")
            cls.ort_session = ort.InferenceSession(cls.ONNX_MODEL_PATH)
            logging.info("ONNX Runtime session initialized successfully for integration tests.")
        except Exception as e:
            logging.error(f"Failed to initialize ONNX Runtime session: {e}")
            raise unittest.SkipTest(f"Skipping integration tests: ONNX session initialization failed - {e}")

        # Initialize MediaPipe FaceMesh
        try:
            cls.face_mesh = mp.solutions.face_mesh.FaceMesh(
                max_num_faces=1, refine_landmarks=True, 
                min_detection_confidence=0.5, min_tracking_confidence=0.5
            )
            logging.info("MediaPipe FaceMesh initialized successfully for integration tests.")
        except Exception as e:
            logging.error(f"Failed to initialize MediaPipe FaceMesh: {e}")
            raise unittest.SkipTest(f"Skipping integration tests: FaceMesh initialization failed - {e}")
        
        cls.fonts_folder = os.path.join(PROJECT_ROOT, 'fonts')
        if not os.path.exists(cls.fonts_folder):
            # If fonts are critical and not mocked, this might be a skip condition too.
            # For now, assume preview/printable creators are mocked, so font files themselves aren't strictly needed by processor.
            logging.warning(f"Fonts folder not found at {cls.fonts_folder}. Tests might proceed if font usage is mocked.")
            # os.makedirs(cls.fonts_folder) # Or create if necessary for some tests

        # Prepare a dummy input image for tests to use (if not already present)
        # This is a placeholder - the actual test will use 'tests/test_assets/sample_portrait.jpg'
        cls.sample_image_dir = os.path.join(PROJECT_ROOT, 'tests', 'test_assets')
        os.makedirs(cls.sample_image_dir, exist_ok=True)
        cls.sample_image_path = os.path.join(cls.sample_image_dir, 'sample_portrait.jpg')
        if not os.path.exists(cls.sample_image_path):
            try:
                logging.info(f"Creating a placeholder for sample_portrait.jpg at {cls.sample_image_path}")
                placeholder_img = Image.new('RGB', (600,800), 'gray') # A simple placeholder
                draw = ImageDraw.Draw(placeholder_img)
                # Draw a "face" like area
                draw.ellipse((150,100, 450,500), fill='lightgray') # Head
                draw.ellipse((200,200, 280,250), fill='white') # Eye 1
                draw.ellipse((320,200, 400,250), fill='white') # Eye 2
                placeholder_img.save(cls.sample_image_path)
                logging.info("Placeholder sample_portrait.jpg created. Replace with a real portrait for meaningful integration testing.")
            except Exception as e_img:
                logging.warning(f"Could not create placeholder sample image: {e_img}. Test will rely on existing image.")


    @classmethod
    def tearDownClass(cls):
        if cls.face_mesh:
            cls.face_mesh.close()
        # No need to delete downloaded models, they can be reused.

    def setUp(self):
        # Ensure services were loaded by setUpClass
        if not self.gfpganer or not self.ort_session or not self.face_mesh:
            self.skipTest("Required ML models not loaded in setUpClass.")

        self.base_output_dir = os.path.join(PROJECT_ROOT, 'tests', 'test_integration_outputs')
        os.makedirs(self.base_output_dir, exist_ok=True)

        self.input_image_path = self.sample_image_path 
        
        # Define output paths for the processor
        self.processed_path = os.path.join(self.base_output_dir, 'processed_integration.jpg')
        self.preview_path = os.path.join(self.base_output_dir, 'preview_integration.jpg')
        self.printable_path = os.path.join(self.base_output_dir, 'printable_integration.jpg')
        self.printable_preview_path = os.path.join(self.base_output_dir, 'printable_preview_integration.jpg')

        self.processor = VisaPhotoProcessor(
            input_path=self.input_image_path,
            processed_path=self.processed_path,
            preview_path=self.preview_path,
            printable_path=self.printable_path,
            printable_preview_path=self.printable_preview_path,
            fonts_folder=self.fonts_folder, # Real path, but functions using it are mocked
            gfpganer_instance=self.gfpganer,
            ort_session_instance=self.ort_session,
            face_mesh_instance=self.face_mesh
        )

    def tearDown(self):
        # Clean up output files created by the processor IF save wasn't mocked
        # Since save will be mocked, this might not be strictly necessary for these files.
        # However, the output directory itself can be removed.
        if os.path.exists(self.base_output_dir):
            shutil.rmtree(self.base_output_dir)
        # Do not remove self.sample_image_path here as it's a shared test asset.

    @patch.object(Image.Image, 'save') # Patch PIL.Image.Image.save to capture the processed image
    @patch('image_processing.preview_creator.create_preview_with_watermark')
    @patch('image_processing.printable_creator.create_printable_image')
    @patch('image_processing.printable_creator.create_printable_preview')
    @patch('os.path.getsize')
    def test_process_sample_image_successfully(self, 
                                             mock_os_getsize, 
                                             mock_create_printable_preview,
                                             mock_create_printable_image, 
                                             mock_create_preview, 
                                             mock_pil_image_save): # Order matters for decorators

        mock_socketio = MagicMock()
        mock_os_getsize.return_value = 123456 # Dummy file size in bytes

        # --- Call the method under test ---
        try:
            photo_info = self.processor.process_with_updates(mock_socketio)
        except Exception as e:
            # If an error occurs here, it might be due to the sample image or model processing.
            # For example, if no face is detected in 'sample_portrait.jpg'.
            self.fail(f"processor.process_with_updates raised an unexpected exception: {e}\n"
                      f"Ensure 'tests/test_assets/sample_portrait.jpg' is a suitable image with a clear face.")

        # --- Assertions ---
        
        # 1. photo_info content
        self.assertIsNotNone(photo_info)
        self.assertIn('head_height', photo_info)
        self.assertIn('eye_to_bottom', photo_info)
        self.assertIn('file_size_kb', photo_info)
        self.assertIn('compliance', photo_info)
        self.assertIn('head_height', photo_info['compliance'])
        self.assertIn('eye_to_bottom', photo_info['compliance'])
        
        # Check for plausible numbers (actual compliance depends on sample_portrait.jpg)
        self.assertGreaterEqual(photo_info['head_height'], 0) 
        self.assertGreaterEqual(photo_info['eye_to_bottom'], 0)
        self.assertEqual(photo_info['file_size_kb'], round(123456 / 1024, 2))

        # 2. Processed PIL Image (captured from mock_pil_image_save)
        self.assertTrue(mock_pil_image_save.called, "PIL Image.save() was not called on the processed image.")
        # The first argument to the first call of save() is the Image instance itself
        processed_pil_image = mock_pil_image_save.call_args[0][0] 
        
        self.assertIsInstance(processed_pil_image, Image.Image)
        self.assertEqual(processed_pil_image.size, (PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS))
        self.assertEqual(processed_pil_image.mode, 'RGB')

        # 3. Background Check (sample a few pixels)
        # These checks assume the background removal was effective.
        # Top-left corner
        bg_sample_tl = processed_pil_image.getpixel((10, 10))
        self.assertTrue(all(c > 220 for c in bg_sample_tl), f"Top-left background not white enough: {bg_sample_tl}")
        # Top-right corner
        bg_sample_tr = processed_pil_image.getpixel((PHOTO_SIZE_PIXELS - 11, 10))
        self.assertTrue(all(c > 220 for c in bg_sample_tr), f"Top-right background not white enough: {bg_sample_tr}")
        # Bottom-left corner
        bg_sample_bl = processed_pil_image.getpixel((10, PHOTO_SIZE_PIXELS - 11))
        self.assertTrue(all(c > 220 for c in bg_sample_bl), f"Bottom-left background not white enough: {bg_sample_bl}")
        # Bottom-right corner
        bg_sample_br = processed_pil_image.getpixel((PHOTO_SIZE_PIXELS - 11, PHOTO_SIZE_PIXELS - 11))
        self.assertTrue(all(c > 220 for c in bg_sample_br), f"Bottom-right background not white enough: {bg_sample_br}")

        # 4. Assert mocked output functions were called
        # Crop data is dynamic based on the image, so use ANY or a more complex check if needed
        mock_create_preview.assert_called_once_with(
            self.processed_path, self.preview_path, unittest.mock.ANY, # crop_data
            unittest.mock.ANY, # face_landmarks
            self.fonts_folder
        )
        mock_create_printable_image.assert_called_once_with(
            self.processed_path, self.printable_path, self.fonts_folder, rows=2, cols=2
        )
        mock_create_printable_preview.assert_called_once_with(
            self.processed_path, self.printable_preview_path, self.fonts_folder, rows=2, cols=2
        )
        
        # 5. Assert socketio calls (basic check for completion)
        mock_socketio.emit.assert_any_call('processing_status', {'status': 'Processing complete'})


if __name__ == '__main__':
    unittest.main()
