# main.py

# IMPORTANT: eventlet monkey patch must be first
import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, render_template, send_file, send_from_directory, abort
import os
import uuid
import urllib.parse
import logging
import traceback
import ssl
import urllib.request
import requests
import json

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from flask_socketio import SocketIO, emit
from image_processing import VisaPhotoProcessor
from utils import allowed_file, is_allowed_file, clean_filename, ALLOWED_EXTENSIONS

# Imports for Dependency Injection
from gfpgan import GFPGANer
import onnxruntime as ort
# Imports for Document Specifications
from photo_specs import DOCUMENT_SPECIFICATIONS, PhotoSpecification, get_photo_specification # Added get_photo_specification
import mediapipe as mp

# Payment system imports
from payment_service import StripePaymentService, PricingService
from models import Order, DatabaseManager
from email_service import EmailService, configure_mail

# Initialize Flask application
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Enhanced SocketIO configuration for production
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='eventlet',
    logger=False,
    engineio_logger=False,
    path='/socket.io/',
    allow_upgrades=True,
    ping_timeout=60,  # Production timeout
    ping_interval=25, # Standard interval
    socket_io_version='5.0.0',
    engine_io_version='4.0.0'
)

# Configure logging - INFO level for production
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# SocketIO event handlers
@socketio.on('connect')
def handle_connect():
    logging.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    logging.info(f"Client disconnected: {request.sid}")

@socketio.on_error_default
def default_error_handler(e):
    logging.error(f"SocketIO error: {e}")

# Payment system configuration
try:
    payment_service = StripePaymentService()
    logging.info("Stripe payment service initialized successfully")
except Exception as e:
    logging.warning(f"Stripe payment service initialization failed: {e}")
    payment_service = None

# Email configuration
try:
    mail = configure_mail(app)
    email_service = EmailService(mail)
    logging.info("Email service initialized successfully")
except Exception as e:
    logging.warning(f"Email service initialization failed: {e}")
    email_service = EmailService()  # Will work in demo mode

# Initialize database
try:
    db_manager = DatabaseManager()
    order_manager = Order(db_manager)
    logging.info("Database initialized successfully")
except Exception as e:
    logging.error(f"Database initialization failed: {e}")
    db_manager = None
    order_manager = None

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
        # Configure ONNX Runtime session options for better memory management
        sess_options = ort.SessionOptions()
        sess_options.enable_mem_pattern = False  # Disable memory pattern optimization
        sess_options.enable_cpu_mem_arena = False  # Disable CPU memory arena
        sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL  # Sequential execution
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
        
        # Set inter/intra thread counts for better resource control
        sess_options.inter_op_num_threads = 1
        sess_options.intra_op_num_threads = 2
        
        # Initialize session with options and explicit CPU provider
        ort_session_instance = ort.InferenceSession(
            ONNX_MODEL_PATH, 
            sess_options=sess_options,
            providers=['CPUExecutionProvider']
        )
        
        model_size_mb = os.path.getsize(ONNX_MODEL_PATH) / 1024 / 1024
        logging.info(f"ONNX Runtime session initialized successfully with optimizations. Model size: {model_size_mb:.1f}MB")
    except Exception as e:
        logging.error(f"Error initializing ONNX Runtime session: {e}")
        logging.error(f"Model path: {ONNX_MODEL_PATH}")
        logging.error(f"Model exists: {os.path.exists(ONNX_MODEL_PATH)}")
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


@app.route('/test-websocket')
def test_websocket():
    """Test page for WebSocket debugging"""
    return render_template('test_websocket.html')

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

def process_image_background(task_id, input_path, processed_path, preview_path, 
                           printable_path, printable_preview_path, spec, 
                           country_code, document_name):
    """Background task for image processing to avoid Cloudflare timeouts"""
    try:
        with app.app_context():
            logging.info(f"Starting background processing for task {task_id}")
            socketio.emit('processing_status', {'task_id': task_id, 'status': 'Processing started'})
            
            # Check if critical instances were initialized correctly
            if not ort_session_instance or not face_mesh_instance:
                logging.error("Critical ML models (ONNX or FaceMesh) failed to initialize.")
                socketio.emit('processing_error', {
                    'task_id': task_id, 
                    'error': 'Critical ML model initialization failed'
                })
                return
            
            if not gfpganer_instance:
                logging.warning("GFPGANer failed to initialize. Proceeding without image enhancement.")
            
            # Use VisaPhotoProcessor class for image processing
            processor = VisaPhotoProcessor(
                input_path=input_path,
                processed_path=processed_path,
                preview_path=preview_path,
                printable_path=printable_path,
                printable_preview_path=printable_preview_path,
                fonts_folder=FONTS_FOLDER,
                photo_spec=spec,
                gfpganer_instance=gfpganer_instance,
                ort_session_instance=ort_session_instance,
                face_mesh_instance=face_mesh_instance
            )
            
            # Process image with progress updates
            photo_info = processor.process_with_updates(socketio)
            
            # DV Lottery specific validation for processed file size
            if document_name.lower() == "visa lottery":
                processed_size_kb = os.path.getsize(processed_path) / 1024
                if processed_size_kb > 240:
                    logging.warning(f"DV Lottery processed file size ({processed_size_kb:.1f}KB) exceeds 240KB limit")
                    photo_info['dv_lottery_warning'] = f"File size ({processed_size_kb:.1f}KB) may exceed DV Lottery 240KB limit"
                elif processed_size_kb < 10:
                    raise ValueError("Processed DV Lottery photo is too small (less than 10KB)")
                else:
                    photo_info['dv_lottery_compliance'] = f"File size ({processed_size_kb:.1f}KB) meets DV Lottery requirements (10-240KB)"
            
            # Emit completion event
            socketio.emit('processing_complete', {
                'task_id': task_id,
                'success': True,
                'preview_filename': os.path.basename(preview_path),
                'download_filename': os.path.basename(processed_path),
                'printable_filename': os.path.basename(printable_path),
                'printable_preview_filename': os.path.basename(printable_preview_path),
                'photo_info': photo_info,
                'message': 'File processed successfully'
            })
            
            logging.info(f"Background processing completed for task {task_id}")
            
            # Clean up uploaded file after processing
            if input_path and os.path.exists(input_path):
                os.remove(input_path)
                logging.info(f"Cleaned up input file: {input_path}")
                
    except Exception as e:
        logging.error(f"Error during background processing for task {task_id}: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        
        # Clean up files in case of error
        for path in [input_path, processed_path, preview_path, printable_path, printable_preview_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    logging.info(f"Removed file: {path}")
                except Exception as cleanup_error:
                    logging.error(f"Error cleaning up file {path}: {cleanup_error}")
        
        # Emit error event
        socketio.emit('processing_error', {
            'task_id': task_id,
            'error': str(e),
            'message': 'Processing failed'
        })

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

            # Return immediately with task info - processing will happen in background
            task_id = unique_id
            
            # Start background processing
            socketio.start_background_task(
                target=process_image_background,
                task_id=task_id,
                input_path=input_path,
                processed_path=processed_path,
                preview_path=preview_path,
                printable_path=printable_path,
                printable_preview_path=printable_preview_path,
                spec=spec,
                country_code=country_code,
                document_name=document_name
            )
            
            # Return immediate response to avoid Cloudflare timeout
            return jsonify({
                'success': True,
                'task_id': task_id,
                'message': 'File uploaded successfully. Processing started.',
                'status': 'processing'
            }), 202

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

@app.route('/payment')
def payment_page():
    """Payment page for purchasing photo downloads."""
    return render_template('payment.html')

@app.route('/payment-success')
def payment_success_page():
    """Payment success confirmation page."""
    return render_template('payment-success.html')

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

# === PAYMENT SYSTEM ROUTES ===

@app.route('/api/pricing')
def get_pricing():
    """Get available pricing options."""
    return jsonify(PricingService.get_all_pricing())

@app.route('/api/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """Create payment intent for order."""
    try:
        if not payment_service or not order_manager:
            return jsonify({'error': 'Payment system not available'}), 503
        
        data = request.get_json()
        email = data.get('email')
        processed_filename = data.get('processed_filename')
        printable_filename = data.get('printable_filename')
        product_type = data.get('product_type', 'single_photo')
        photo_info = data.get('photo_info')
        
        if not email or not processed_filename:
            return jsonify({'error': 'Email and processed filename required'}), 400
        
        # Get pricing
        pricing = PricingService.get_price(product_type)
        
        # Create order
        order_number = order_manager.create_order(
            email=email,
            processed_filename=processed_filename,
            printable_filename=printable_filename,
            amount_cents=pricing['amount_cents'],
            currency=pricing['currency'],
            photo_info=json.dumps(photo_info) if photo_info else None
        )
        
        # Create payment intent
        payment_intent = payment_service.create_payment_intent(
            order_number=order_number,
            email=email,
            amount_cents=pricing['amount_cents'],
            currency=pricing['currency']
        )
        
        return jsonify({
            'client_secret': payment_intent['client_secret'],
            'order_number': order_number,
            'amount': pricing['amount_cents'],
            'currency': pricing['currency'],
            'publishable_key': payment_service.get_publishable_key()
        })
        
    except Exception as e:
        logging.error(f"Payment intent creation error: {str(e)}")
        return jsonify({'error': 'Failed to create payment intent'}), 500

@app.route('/api/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks - endpoint for Stripe to send events."""
    try:
        if not payment_service:
            logging.error("Payment service not available for webhook")
            return jsonify({'error': 'Payment service not available'}), 503
        
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        if not webhook_secret:
            logging.error("STRIPE_WEBHOOK_SECRET not configured")
            return jsonify({'error': 'Webhook not configured'}), 500
        
        logging.info(f"Received webhook with signature: {sig_header[:20]}...")
        
        payment_service.handle_webhook(payload, sig_header, webhook_secret)
        
        logging.info("Webhook processed successfully")
        return jsonify({'received': True}), 200
        
    except ValueError as e:
        logging.error(f"Webhook payload error: {str(e)}")
        return jsonify({'error': 'Invalid payload'}), 400
    except Exception as e:
        logging.error(f"Webhook processing error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 400

@app.route('/download/<order_number>/<file_type>')
def download_paid_file(order_number, file_type):
    """Download file after payment verification."""
    try:
        if not order_manager:
            return jsonify({'error': 'Order system not available'}), 503
        
        # Verify order and payment
        can_download, message = order_manager.can_download(order_number)
        if not can_download:
            return jsonify({'error': message}), 403
        
        # Get order details
        order = order_manager.get_order(order_number)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Determine file path
        if file_type == 'processed':
            filename = order['processed_filename']
            file_path = os.path.join(PROCESSED_FOLDER, filename)
            download_name = "visa_photo_final.jpg"
        elif file_type == 'printable':
            filename = order['printable_filename']
            if not filename:
                return jsonify({'error': 'Printable file not available'}), 404
            file_path = os.path.join(PROCESSED_FOLDER, filename)
            download_name = "visa_photo_printable_4x6.jpg"
        else:
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Check if file exists
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
        
        # Log download attempt
        order_manager.increment_download_count(
            order_number, 
            file_type,
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        # Send file
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='image/jpeg'
        )
        
        # Disable caching
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        logging.info(f"Served paid download: {file_path} for order {order_number}")
        return response
        
    except Exception as e:
        logging.error(f"Paid download error: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/order/<order_number>')
def get_order_status(order_number):
    """Get order status and details."""
    try:
        if not order_manager:
            return jsonify({'error': 'Order system not available'}), 503
        
        order = order_manager.get_order(order_number)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Don't expose sensitive information
        safe_order = {
            'order_number': order['order_number'],
            'payment_status': order['payment_status'],
            'amount_cents': order['amount_cents'],
            'currency': order['currency'],
            'created_at': order['created_at'],
            'download_count': order['download_count'],
            'max_downloads': order['max_downloads']
        }
        
        if order['download_expires_at']:
            safe_order['download_expires_at'] = order['download_expires_at']
        
        return jsonify(safe_order)
        
    except Exception as e:
        logging.error(f"Order status error: {str(e)}")
        return jsonify({'error': 'Failed to get order status'}), 500

# Admin routes (protect these in production!)
@app.route('/admin/orders')
def admin_orders():
    """Admin view of all orders (protect in production!)."""
    if not db_manager:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT order_number, email, payment_status, amount_cents, 
                       currency, created_at, download_count 
                FROM orders 
                ORDER BY created_at DESC 
                LIMIT 50
            ''')
            orders = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            orders_list = [dict(zip(columns, row)) for row in orders]
        
        return jsonify(orders_list)
        
    except Exception as e:
        logging.error(f"Admin orders error: {str(e)}")
        return jsonify({'error': 'Failed to fetch orders'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Docker"""
    return jsonify({
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }), 200

if __name__ == '__main__':
    # Production configuration
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_ENV') != 'production'
    socketio.run(app, debug=debug, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)