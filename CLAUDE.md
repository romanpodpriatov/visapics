# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running Tests
```bash
# Run all tests
python -m unittest discover -s tests

# Run tests with verbose output
python -m unittest discover -s tests -v

# Run specific test file
python -m unittest tests.test_main
```

### Running the Application
```bash
# Start Flask development server
python main.py
# Access at http://127.0.0.1:8000
```

## Architecture Overview

This is a Flask-based web application for automated visa and passport photo processing. The system uses multiple AI models for face detection, background removal, and image enhancement.

### Core Processing Pipeline
1. **Image Upload & Validation** (`main.py`) - Handles file uploads and country/document selection
2. **Face Analysis** (`face_analyzer.py`) - MediaPipe FaceMesh for facial landmarks and geometric calculations
3. **Background Processing** (`background_remover.py`) - BiRefNet ONNX model for background segmentation
4. **Image Enhancement** (`image_processing.py`) - GFPGAN for facial enhancement and VisaPhotoProcessor orchestration
5. **Preview Generation** (`preview_creator.py`) - Creates watermarked previews with measurement overlays
6. **Print Layout** (`printable_creator.py`) - Generates 4x6 inch printable sheets

### Document Specifications System
- `photo_specs.py` contains PhotoSpecification dataclass and DOCUMENT_SPECIFICATIONS list
- Specifications define photo dimensions, DPI, head size requirements, eye positioning, and background colors
- Dynamic country/document selection in web interface drives processing parameters

### Dependency Injection Pattern
The application uses dependency injection for AI models initialized in `main.py`:
- `gfpganer_instance` (GFPGAN face enhancement)
- `ort_session_instance` (ONNX Runtime for background removal)
- `face_mesh_instance` (MediaPipe FaceMesh)

These instances are passed to VisaPhotoProcessor to avoid repeated model loading.

### Key Directories Structure
- `models/` - ONNX models (BiRefNet-portrait-epoch_150.onnx)
- `gfpgan/weights/` - GFPGAN model files (GFPGANv1.4.pth)
- `fonts/` - Font files for text rendering (Arial.ttf)
- `uploads/`, `processed/`, `previews/` - Runtime file storage (created automatically)
- `tests/` - Comprehensive test suite with integration tests
- `templates/` - Flask HTML templates
- `static/` - Frontend assets

### Real-time Communication
- Uses Flask-SocketIO for real-time processing status updates
- `process_with_updates()` method emits progress events during image processing

### Testing Strategy
- Unit tests for all major components
- Integration tests using sample portrait images
- Mock-based testing for AI model dependencies
- Test assets in `tests/test_assets/`

## Important Implementation Notes

### AI Model Requirements
- BiRefNet ONNX model must be manually downloaded and placed in `models/`
- GFPGAN model auto-downloads on first run if missing
- Models are initialized once at startup and reused via dependency injection

### File Processing Flow
- Temporary files use UUID prefixes for uniqueness
- Input files are cleaned up after successful processing
- Error handling includes automatic file cleanup

### Photo Specification Extensions
When adding new countries/documents:
1. Add PhotoSpecification entry to DOCUMENT_SPECIFICATIONS in `photo_specs.py`
2. Update COUNTRY_DISPLAY_NAMES mapping in `main.py` if needed
3. Ensure background_color maps to BACKGROUND_COLOR_MAP in `image_processing.py`