import unittest
from unittest.mock import patch, MagicMock, mock_open, call
import os
import sys
import shutil
import json
from io import BytesIO
import tempfile
import logging

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

# Set environment variable to indicate test mode for main.py (if main.py uses it)
# os.environ['FLASK_ENV'] = 'testing' # Or a custom one like 'APP_TESTING_MODE'

# It's important that main.py is imported AFTER the environment variable is set,
# if main.py has logic that branches on such a variable at import time.
# For this setup, we assume main.py can be imported directly and configured in setUp.
from main import app, socketio 

# Disable werkzeug logging for tests to keep output clean
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


class TestAppRoutes(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
        app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for forms if any are used directly

        self.client = app.test_client()

        self.temp_dir = tempfile.mkdtemp()
        app.config['UPLOAD_FOLDER'] = os.path.join(self.temp_dir, 'uploads')
        app.config['PROCESSED_FOLDER'] = os.path.join(self.temp_dir, 'processed')
        app.config['PREVIEW_FOLDER'] = os.path.join(self.temp_dir, 'previews')
        
        # Create these dirs
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
        os.makedirs(app.config['PREVIEW_FOLDER'], exist_ok=True)
        
        # Store original config values to restore them in tearDown if necessary,
        # though for temp dirs, new ones are made each time.
        self.original_configs = {
            'UPLOAD_FOLDER': app.config['UPLOAD_FOLDER'],
            'PROCESSED_FOLDER': app.config['PROCESSED_FOLDER'],
            'PREVIEW_FOLDER': app.config['PREVIEW_FOLDER'],
        }
        # No actual file is created in FONTS_FOLDER by main.py, so not strictly needed for temp.
        # app.config['FONTS_FOLDER'] remains pointing to project's fonts/

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        # Restore original config if modified beyond temp dirs, though not strictly needed here
        # For example, if we changed app.config['FONTS_FOLDER'] to a temp one.

    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Assuming 'Visa Photo Assistant' is a unique title or string in index.html
        self.assertIn(b'Visa Photo Assistant', response.data) 
        # A more specific unique string from index.html is better:
        # e.g., find a comment or a specific element ID:
        # self.assertIn(b'id="upload-form"', response.data) # Example

    @patch('main.os.remove') # To check file cleanup
    @patch.object(socketio, 'emit')
    @patch('main.VisaPhotoProcessor')
    def test_upload_file_success(self, MockVisaPhotoProcessor, mock_socketio_emit, mock_os_remove):
        # Configure the mock processor
        mock_processor_instance = MockVisaPhotoProcessor.return_value
        sample_photo_info = {
            'head_height': 1.2,
            'eye_to_bottom': 1.3,
            'file_size_kb': 150.5,
            'quality': 95,
            'compliance': {'head_height': True, 'eye_to_bottom': True}
        }
        mock_processor_instance.process_with_updates.return_value = sample_photo_info

        # Prepare file data for upload
        data = {'file': (BytesIO(b"dummy image data for a jpeg"), 'test_photo.jpg')}
        
        response = self.client.post('/upload', data=data, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data)
        
        self.assertTrue(json_response['success'])
        self.assertIn('preview_filename', json_response)
        self.assertIn('download_filename', json_response)
        self.assertIn('printable_filename', json_response)
        self.assertIn('printable_preview_filename', json_response)
        self.assertEqual(json_response['photo_info'], sample_photo_info)
        self.assertEqual(json_response['message'], 'File successfully processed')

        # Check that VisaPhotoProcessor was instantiated and its method called
        MockVisaPhotoProcessor.assert_called_once() # Check instantiation
        # Get the arguments passed to the constructor
        constructor_args = MockVisaPhotoProcessor.call_args[1] # kwargs
        self.assertIn('input_path', constructor_args)
        self.assertTrue(constructor_args['input_path'].endswith('test_photo.jpg'))
        self.assertEqual(constructor_args['fonts_folder'], app.config['FONTS_FOLDER']) # Real fonts folder used

        mock_processor_instance.process_with_updates.assert_called_once_with(socketio)
        
        # Check socketio emit calls (at least the completion one)
        mock_socketio_emit.assert_any_call('processing_status', {'status': 'Processing complete'})
        # Check that the initial file was removed
        mock_os_remove.assert_called_once_with(constructor_args['input_path'])

    def test_upload_no_file_part(self):
        response = self.client.post('/upload', data={})
        self.assertEqual(response.status_code, 400)
        json_response = json.loads(response.data)
        self.assertIn('No file in request', json_response['error'])

    def test_upload_no_selected_file(self):
        data = {'file': (BytesIO(b""), '')} # Empty filename
        response = self.client.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        json_response = json.loads(response.data)
        self.assertIn('No file selected', json_response['error'])

    def test_upload_invalid_file_type(self):
        data = {'file': (BytesIO(b"this is a plain text file"), 'test_document.txt')}
        response = self.client.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        json_response = json.loads(response.data)
        self.assertIn('Invalid file type', json_response['error'])
        self.assertIn('Supported formats: JPG, JPEG, PNG', json_response['message'])

    @patch.object(socketio, 'emit') # Patch socketio for this test too
    @patch('main.VisaPhotoProcessor')
    def test_upload_processor_error(self, MockVisaPhotoProcessor, mock_socketio_emit):
        # Configure the mock processor to raise an error
        error_message = "Simulated face detection failure"
        mock_processor_instance = MockVisaPhotoProcessor.return_value
        mock_processor_instance.process_with_updates.side_effect = ValueError(error_message)

        data = {'file': (BytesIO(b"dummy image data for a jpeg"), 'test_photo.jpg')}
        response = self.client.post('/upload', data=data, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 500)
        json_response = json.loads(response.data)
        self.assertFalse(json_response.get('success', True)) # Should not have 'success: true'
        self.assertIn('Error processing image', json_response['error'])
        self.assertIn(error_message, json_response['message'])
        
        # Check that VisaPhotoProcessor was instantiated and its method called
        MockVisaPhotoProcessor.assert_called_once()
        mock_processor_instance.process_with_updates.assert_called_once_with(socketio)
        
        # Check that socketio emitted the initial status before the error
        mock_socketio_emit.assert_any_call('processing_status', {'status': 'Processing started'})

    # --- Tests for /previews/<filename> ---
    def test_get_preview_success(self):
        dummy_filename = 'test_preview.jpg'
        dummy_filepath = os.path.join(app.config['PREVIEW_FOLDER'], dummy_filename)
        with open(dummy_filepath, 'wb') as f:
            f.write(b"dummy jpeg data")
        
        response = self.client.get(f'/previews/{dummy_filename}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'image/jpeg')
        self.assertEqual(response.data, b"dummy jpeg data")

    def test_get_preview_not_found(self):
        response = self.client.get('/previews/non_existent_preview.jpg')
        self.assertEqual(response.status_code, 404)
        json_response = json.loads(response.data)
        self.assertIn('Preview not found', json_response['error'])

    def test_get_preview_disallowed_type(self):
        # Attempt to access a .txt file as if it's a preview
        dummy_filename = 'dangerous_document.txt'
        dummy_filepath = os.path.join(app.config['PREVIEW_FOLDER'], dummy_filename)
        with open(dummy_filepath, 'w') as f:
            f.write("this is not an image")

        response = self.client.get(f'/previews/{dummy_filename}')
        self.assertEqual(response.status_code, 400) # Based on is_allowed_file check
        json_response = json.loads(response.data)
        self.assertIn('Invalid file type', json_response['error'])
        
    # --- Tests for /download/<filename> ---
    def test_download_file_success(self):
        dummy_filename = 'processed_file.jpg'
        dummy_filepath = os.path.join(app.config['PROCESSED_FOLDER'], dummy_filename)
        with open(dummy_filepath, 'wb') as f:
            f.write(b"processed dummy jpeg data")

        response = self.client.get(f'/download/{dummy_filename}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'image/jpeg')
        self.assertEqual(response.data, b"processed dummy jpeg data")
        self.assertIn('attachment; filename=visa_photo.jpg', response.headers['Content-Disposition'])

    def test_download_file_not_found(self):
        response = self.client.get('/download/non_existent_processed.jpg')
        self.assertEqual(response.status_code, 404)
        json_response = json.loads(response.data)
        self.assertIn('File not found', json_response['error'])

    # --- Tests for /previews/printable/<filename> ---
    def test_get_printable_preview_success(self):
        dummy_filename = 'test_printable_preview.jpg'
        dummy_filepath = os.path.join(app.config['PREVIEW_FOLDER'], dummy_filename) # Printable previews also go to PREVIEW_FOLDER
        with open(dummy_filepath, 'wb') as f:
            f.write(b"dummy printable preview data")
        
        response = self.client.get(f'/previews/printable/{dummy_filename}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'image/jpeg')
        self.assertEqual(response.data, b"dummy printable preview data")

    def test_get_printable_preview_not_found(self):
        response = self.client.get('/previews/printable/non_existent_printable_preview.jpg')
        self.assertEqual(response.status_code, 404)
        json_response = json.loads(response.data)
        self.assertIn('Preview not found', json_response['error']) # Same error message as regular preview

    # --- Tests for /download_printable/<filename> ---
    def test_download_printable_success(self):
        dummy_filename = 'printable_output.jpg'
        dummy_filepath = os.path.join(app.config['PROCESSED_FOLDER'], dummy_filename) # Printable files go to PROCESSED_FOLDER
        with open(dummy_filepath, 'wb') as f:
            f.write(b"dummy printable file data")

        response = self.client.get(f'/download_printable/{dummy_filename}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'image/jpeg')
        self.assertEqual(response.data, b"dummy printable file data")
        self.assertIn('attachment; filename=printable_photo.jpg', response.headers['Content-Disposition'])

    def test_download_printable_not_found(self):
        response = self.client.get('/download_printable/non_existent_printable.jpg')
        self.assertEqual(response.status_code, 404)
        json_response = json.loads(response.data)
        self.assertIn('File not found', json_response['error'])


if __name__ == '__main__':
    unittest.main()
