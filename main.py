# main.py

from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
import os
import uuid
import urllib.parse
import logging
import traceback
import ssl
import urllib.request
import requests

from flask_socketio import SocketIO, emit
from image_processing import VisaPhotoProcessor
from utils import allowed_file, is_allowed_file, clean_filename, ALLOWED_EXTENSIONS

# Imports for Dependency Injection
from gfpgan import GFPGANer
import onnxruntime as ort
# Imports for Document Specifications
from photo_specs import DOCUMENT_SPECIFICATIONS, PhotoSpecification, get_photo_specification # Added get_photo_specification
import mediapipe as mp

# Initialize Flask application
app = Flask(__name__, static_folder='static', template_folder='templates')
socketio = SocketIO(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, 'processed')
PREVIEW_FOLDER = os.path.join(BASE_DIR, 'previews')
FONTS_FOLDER = os.path.join(BASE_DIR, 'fonts')

# Create necessary directories
for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER, PREVIEW_FOLDER, FONTS_FOLDER]:
    os.makedirs(folder, exist_ok=True)
    logging.info(f"Created directory: {folder}")

# --- Initialize ML Models and Services ---
GFPGAN_MODEL_PATH = 'gfpgan/weights/GFPGANv1.4.pth'
ONNX_MODEL_PATH = os.path.join('models', 'BiRefNet-portrait-epoch_150.onnx')

def download_model_with_ssl_fix(url, output_path):
    """Download model with SSL certificate handling."""
    try:
        # Method 1: Use requests with SSL verification disabled for model downloads
        logging.info(f"Downloading model from {url}...")
        response = requests.get(url, verify=False, stream=True, timeout=300)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        if downloaded % (1024 * 1024) == 0:  # Log every MB
                            logging.info(f"Download progress: {progress:.1f}%")
        
        logging.info(f"Model downloaded successfully to {output_path}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to download with requests: {e}")
        
        # Method 2: Fallback to urllib with unverified SSL context
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(url, context=ssl_context, timeout=300) as response:
                with open(output_path, 'wb') as f:
                    f.write(response.read())
            
            logging.info(f"Model downloaded successfully to {output_path} (fallback method)")
            return True
            
        except Exception as fallback_error:
            logging.error(f"Fallback download also failed: {fallback_error}")
            return False

# Initialize GFPGANer
if not os.path.exists(GFPGAN_MODEL_PATH):
    logging.info(f"GFPGAN model not found at {GFPGAN_MODEL_PATH}. Downloading...")
    try:
        os.makedirs(os.path.dirname(GFPGAN_MODEL_PATH), exist_ok=True)
        success = download_model_with_ssl_fix(
            'https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth', 
            GFPGAN_MODEL_PATH
        )
        if not success:
            logging.error("All download methods failed for GFPGAN model")
    except Exception as e:
        logging.error(f"Failed to download GFPGAN model: {e}")

# Disable SSL warnings for model downloads
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    # Set environment variable to disable SSL verification for GFPGANer's internal downloads
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    
    gfpganer_instance = GFPGANer(
        model_path=GFPGAN_MODEL_PATH,
        upscale=1,
        arch='clean',
        channel_multiplier=2,
        bg_upsampler=None
    )
    logging.info("GFPGANer initialized successfully.")
except Exception as e:
    logging.error(f"Error initializing GFPGANer: {e}")
    # Try to fix SSL issues by temporarily disabling SSL verification
    try:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        
        gfpganer_instance = GFPGANer(
            model_path=GFPGAN_MODEL_PATH,
            upscale=1,
            arch='clean',
            channel_multiplier=2,
            bg_upsampler=None
        )
        logging.info("GFPGANer initialized successfully with SSL fix.")
    except Exception as ssl_fix_error:
        logging.error(f"GFPGANer initialization failed even with SSL fix: {ssl_fix_error}")
        gfpganer_instance = None # Ensure it's None if initialization fails

# Initialize ONNX Runtime Session for background removal
if not os.path.exists(ONNX_MODEL_PATH):
    logging.error(f"ONNX model not found at {ONNX_MODEL_PATH}. Background removal will fail.")
    # Depending on the application's needs, you might want to exit or raise an error here.
    ort_session_instance = None # Ensure it's None if model is missing
    # raise FileNotFoundError(f"ONNX model not found: {ONNX_MODEL_PATH}") # Alternative: stop app
else:
    try:
        ort_session_instance = ort.InferenceSession(ONNX_MODEL_PATH)
        logging.info("ONNX Runtime session initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing ONNX Runtime session: {e}")
        ort_session_instance = None

# Initialize MediaPipe FaceMesh
try:
    face_mesh_instance = mp.solutions.face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    logging.info("MediaPipe FaceMesh initialized successfully.")
except Exception as e:
    logging.error(f"Error initializing MediaPipe FaceMesh: {e}")
    face_mesh_instance = None
# --- End of ML Models and Services Initialization ---

# Configure application settings
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit

# --- Country Display Names (can be moved to a config or photo_specs.py if it grows) ---
COUNTRY_DISPLAY_NAMES = {
    "US": "United States",
    "GB": "United Kingdom",
    "DE_schengen": "Germany (Schengen)", # Example, adapt as per actual country codes in photo_specs
    "IN": "India",
    "CA": "Canada",
    # Add more mappings if country_code in PhotoSpecification is just 'DE' for Schengen
}


@app.route('/')
def index():
    """
    Main page.
    """
    # Prepare unique list of countries for the dropdown
    # Each item in countries will be a tuple: (country_code, display_name)
    seen_country_codes = set()
    countries_for_dropdown = []
    for spec in DOCUMENT_SPECIFICATIONS:
        if spec.country_code not in seen_country_codes:
            display_name = COUNTRY_DISPLAY_NAMES.get(spec.country_code, spec.country_code.replace("_", " ").title())
            countries_for_dropdown.append((spec.country_code, display_name))
            seen_country_codes.add(spec.country_code)
    
    countries_for_dropdown.sort(key=lambda x: x[1]) # Sort by display name

    return render_template('index.html', countries=countries_for_dropdown)

@app.route('/get_document_types/<country_code>')
def get_document_types(country_code):
    """
    Returns a JSON list of document types for a given country code.
    """
    doc_types = sorted(list(set(
        spec.document_name 
        for spec in DOCUMENT_SPECIFICATIONS 
        if spec.country_code.lower() == country_code.lower()
    )))
    return jsonify(doc_types)

@app.route('/static/<path:path>')
def send_static_files(path):
    """
    Serve static files.
    """
    return send_from_directory('static', path)

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload processing.
    """
    input_path = None
    processed_path = None
    preview_path = None
    printable_path = None
    printable_preview_path = None

    try:
        # Retrieve country and document selections
        country_code = request.form.get('country_code')
        document_name = request.form.get('document_name')
        
        logging.info(f"Received upload for Country: {country_code}, Document: {document_name}")

        if not country_code or not document_name:
            logging.warning("Country code or document name missing from upload request.")
            return jsonify({'error': 'Country and document type must be selected.'}), 400

        if 'file' not in request.files:
            logging.warning("No file part in the request")
            return jsonify({'error': 'No file in request'}), 400

        file = request.files['file']
        if file.filename == '':
            logging.warning("No selected file")
            return jsonify({'error': 'No file selected'}), 400

        if file and allowed_file(file.filename):
            base_filename = clean_filename(file.filename)
            unique_id = str(uuid.uuid4())

            unique_filename = f"{unique_id}_{base_filename}"
            processed_filename = f"processed_{unique_id}_{base_filename}"
            preview_filename = f"preview_processed_{unique_id}_{base_filename}"
            printable_filename = f"printable_{unique_id}_{base_filename}"
            printable_preview_filename = f"preview_printable_{unique_id}_{base_filename}"

            input_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
            preview_path = os.path.join(PREVIEW_FOLDER, preview_filename)
            printable_path = os.path.join(PROCESSED_FOLDER, printable_filename)
            printable_preview_path = os.path.join(PREVIEW_FOLDER, printable_preview_filename)

            file.save(input_path)
            logging.info(f"File saved at {input_path}")

            if os.path.getsize(input_path) > 10 * 1024 * 1024:
                raise ValueError("File size exceeds 10MB")

            # Get the PhotoSpecification object first for DV Lottery specific validation
            spec = get_photo_specification(country_code, document_name)
            if not spec:
                logging.error(f"No specification found for Country: {country_code}, Document: {document_name}")
                return jsonify({'error': f"Invalid document specification selected: {country_code} - {document_name}"}), 400

            # DV Lottery specific file size validation (processed file will be checked later)
            if document_name.lower() == "visa lottery":
                input_size_kb = os.path.getsize(input_path) / 1024
                if input_size_kb < 9.9:  # Allow slight margin for rounding
                    raise ValueError("DV Lottery photos must be at least 10KB in size")
                # Note: The 240KB upper limit will be checked on the processed file to ensure compliance

            # Emit an event to notify the client that the file is being processed
            socketio.emit('processing_status', {'status': 'Processing started'})

            # Use VisaPhotoProcessor class for image processing
            processor = VisaPhotoProcessor(
                input_path=input_path,
                processed_path=processed_path,
                preview_path=preview_path,
                printable_path=printable_path,
                printable_preview_path=printable_preview_path,
                fonts_folder=FONTS_FOLDER,
                photo_spec=spec, # Pass the spec object
                gfpganer_instance=gfpganer_instance,
                ort_session_instance=ort_session_instance,
                face_mesh_instance=face_mesh_instance
            )

            # Check if critical instances were initialized correctly
            if not ort_session_instance or not face_mesh_instance:
                logging.error("Critical ML models (ONNX or FaceMesh) failed to initialize. Aborting processing.")
                raise RuntimeError("Critical ML model initialization failed. Please check server logs.")
            
            if not gfpganer_instance:
                logging.warning("GFPGANer failed to initialize. Proceeding without image enhancement.")

            # Process image and emit status updates
            photo_info = processor.process_with_updates(socketio)

            # DV Lottery specific validation for processed file size
            if document_name.lower() == "visa lottery":
                processed_size_kb = os.path.getsize(processed_path) / 1024
                if processed_size_kb > 240:
                    logging.warning(f"DV Lottery processed file size ({processed_size_kb:.1f}KB) exceeds 240KB limit")
                    # For now, we'll log a warning but still allow the file to be processed
                    # In a production system, you might want to reprocess with higher compression
                    photo_info['dv_lottery_warning'] = f"File size ({processed_size_kb:.1f}KB) may exceed DV Lottery 240KB limit"
                elif processed_size_kb < 10:
                    raise ValueError("Processed DV Lottery photo is too small (less than 10KB)")
                else:
                    photo_info['dv_lottery_compliance'] = f"File size ({processed_size_kb:.1f}KB) meets DV Lottery requirements (10-240KB)"

            response_data = {
                'success': True,
                'preview_filename': os.path.basename(preview_path),
                'download_filename': os.path.basename(processed_path),
                'printable_filename': os.path.basename(printable_path),
                'printable_preview_filename': os.path.basename(printable_preview_path),
                'photo_info': photo_info,
                'message': 'File processed successfully'
            }

            logging.info("File processed successfully")

            # Clean up uploaded file after processing
            if input_path and os.path.exists(input_path):
                os.remove(input_path)
                logging.info(f"Cleaned up input file: {input_path}")

            return jsonify(response_data)

        else:
            logging.warning("Invalid file type uploaded")
            return jsonify({
                'error': 'Invalid file type',
                'message': 'Supported formats: JPG, JPEG, PNG'
            }), 400

    except Exception as e:
        logging.error(f"Error during file upload: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")

        # Clean up files in case of error
        for path in [input_path, processed_path, preview_path, printable_path, printable_preview_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    logging.info(f"Removed file: {path}")
                except Exception as cleanup_error:
                    logging.error(f"Error cleaning up file {path}: {cleanup_error}")

        return jsonify({
            'error': 'Error processing image',
            'message': str(e)
        }), 500

@app.route('/previews/<filename>')
def get_preview(filename):
    """
    Get preview image.
    """
    try:
        # URL decoding and filename cleaning
        decoded_filename = urllib.parse.unquote(filename)
        clean_filename_var = clean_filename(decoded_filename)
        preview_path = os.path.join(PREVIEW_FOLDER, clean_filename_var)

        # Check if file exists
        if not os.path.exists(preview_path):
            logging.warning(f"Preview not found: {filename}")
            return jsonify({'error': 'Preview not found'}), 404

        # Check file extension for security
        if not is_allowed_file(preview_path):
            logging.warning(f"Attempt to access disallowed file type: {filename}")
            return jsonify({'error': 'Invalid file type'}), 400

        logging.info(f"Serving preview: {preview_path}")
        return send_file(preview_path, mimetype='image/jpeg', max_age=300)
    except Exception as e:
        logging.error(f"Preview error: {str(e)}")
        return jsonify({'error': 'Error occurred while getting preview'}), 500

@app.route('/previews/printable/<filename>')
def get_printable_preview(filename):
    """
    Get preview for printable image.
    """
    try:
        # URL decoding and filename cleaning
        decoded_filename = urllib.parse.unquote(filename)
        clean_filename_var = clean_filename(decoded_filename)
        preview_path = os.path.join(PREVIEW_FOLDER, clean_filename_var)

        # Check if file exists
        if not os.path.exists(preview_path):
            logging.warning(f"Printable preview not found: {filename}")
            return jsonify({'error': 'Preview not found'}), 404

        # Check file extension for security
        if not is_allowed_file(preview_path):
            logging.warning(f"Attempt to access disallowed file type: {filename}")
            return jsonify({'error': 'Invalid file type'}), 400

        logging.info(f"Serving printable preview: {preview_path}")
        return send_file(preview_path, mimetype='image/jpeg', max_age=300)
    except Exception as e:
        logging.error(f"Printable preview error: {str(e)}")
        return jsonify({'error': 'Error occurred while getting printable preview'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """
    Download processed file.
    """
    try:
        # URL decoding and filename cleaning
        decoded_filename = urllib.parse.unquote(filename)
        clean_filename_var = clean_filename(decoded_filename)
        file_path = os.path.join(PROCESSED_FOLDER, clean_filename_var)

        # Check if file exists
        if not os.path.exists(file_path):
            logging.warning(f"Processed file not found: {filename}")
            return jsonify({'error': 'File not found'}), 404

        # Check file extension for security
        if not is_allowed_file(file_path):
            logging.warning(f"Attempt to download disallowed file type: {filename}")
            return jsonify({'error': 'Invalid file type'}), 400

        response = send_file(
            file_path,
            as_attachment=True,
            download_name="visa_photo.jpg",
            mimetype='image/jpeg'
        )

        # Disable caching
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        logging.info(f"Serving download: {file_path}")
        return response
    except Exception as e:
        logging.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Error occurred while downloading file'}), 500

@app.route('/download_printable/<filename>')
def download_printable(filename):
    """
    Download 4x6" printable image.
    """
    try:
        # URL decoding and filename cleaning
        decoded_filename = urllib.parse.unquote(filename)
        clean_filename_var = clean_filename(decoded_filename)
        file_path = os.path.join(PROCESSED_FOLDER, clean_filename_var)

        # Check if file exists
        if not os.path.exists(file_path):
            logging.warning(f"Printable file not found: {filename}")
            return jsonify({'error': 'File not found'}), 404

        # Check file extension for security
        if not is_allowed_file(file_path):
            logging.warning(f"Attempt to download disallowed file type: {filename}")
            return jsonify({'error': 'Invalid file type'}), 400

        response = send_file(
            file_path,
            as_attachment=True,
            download_name="printable_photo.jpg",
            mimetype='image/jpeg'
        )

        # Disable caching
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        logging.info(f"Serving printable download: {file_path}")
        return response
    except Exception as e:
        logging.error(f"Download printable error: {str(e)}")
        return jsonify({'error': 'Error occurred while downloading printable file'}), 500

@app.route('/debug_preview')
def debug_preview_page():
    """Debug page for testing preview generation."""
    return render_template('debug_preview.html')

@app.route('/debug_preview/<filename>')
def debug_preview_image(filename):
    """Generate debug preview for a specific processed image."""
    try:
        processed_path = os.path.join(PROCESSED_FOLDER, filename)
        if not os.path.exists(processed_path):
            return jsonify({'error': 'Processed file not found'}), 404
            
        # Create preview filename
        preview_filename = f"debug_preview_{filename}"
        preview_path = os.path.join(PREVIEW_FOLDER, preview_filename)
        
        # Get image dimensions for calculations
        from PIL import Image
        img = Image.open(processed_path)
        img_width, img_height = img.size
        
        # Import for mock data generation
        from photo_specs import get_photo_specification
        
        # Mock preview drawing data (use US Passport as default)
        spec = get_photo_specification("US", "Passport")
        if not spec:
            return jsonify({'error': 'Default specification not found'}), 500
            
        # Calculate mock measurements based on image size
        photo_height_px = int(spec.photo_height_inches * spec.dpi)
        photo_width_px = int(spec.photo_width_inches * spec.dpi)
        
        # Mock face detection data
        mock_head_top_y = int(photo_height_px * 0.15)  # 15% from top
        mock_eye_level_y = int(photo_height_px * 0.45)  # 45% from top  
        mock_head_height = int(photo_height_px * 0.6)   # 60% of photo height
        
        preview_drawing_data = {
            'photo_spec': spec,
            'photo_width_px': photo_width_px,
            'photo_height_px': photo_height_px,
            'achieved_head_top_y_on_photo_px': mock_head_top_y,
            'achieved_eye_level_y_on_photo_px': mock_eye_level_y,
            'achieved_head_height_px': mock_head_height
        }
        
        # Import and use preview creator
        from preview_creator import create_preview_with_watermark
        create_preview_with_watermark(processed_path, preview_path, preview_drawing_data, FONTS_FOLDER)
        
        return jsonify({
            'success': True,
            'preview_filename': preview_filename,
            'original_filename': filename,
            'mock_data': {
                'head_top_y': mock_head_top_y,
                'eye_level_y': mock_eye_level_y,
                'head_height': mock_head_height
            }
        })
        
    except Exception as e:
        logging.error(f"Debug preview error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8000, allow_unsafe_werkzeug=True)