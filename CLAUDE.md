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

This is a Flask-based web application for automated visa and passport photo processing. The system uses multiple AI models for face detection, background removal, and image enhancement, with a revolutionary mask-based hair detection approach for millimeter-precision measurements.

### Core Processing Pipeline
1. **Image Upload & Validation** (`main.py`) - Handles file uploads and country/document selection
2. **Mask-Based Face Analysis** (`face_analyzer_mask.py`) - MaskBasedFaceAnalyzer with BiRefNet integration for precise hair detection
3. **Background Processing** (`background_remover.py`) - BiRefNet ONNX model for background segmentation and mask generation
4. **Image Enhancement** (`image_processing.py`) - GFPGAN for facial enhancement and VisaPhotoProcessor orchestration
5. **Preview Generation** (`preview_creator.py`) - Creates watermarked previews with measurement overlays
6. **Print Layout** (`printable_creator.py`) - Generates 4x6 inch printable sheets

### Document Specifications System
- `photo_specs.py` contains PhotoSpecification dataclass and DOCUMENT_SPECIFICATIONS list
- Enhanced specifications with head positioning control fields (head_top_min_dist_from_photo_top_mm, default_head_top_margin_percent, min_visual_head_margin_px)
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
- `uploads/`, `processed/`, `previews/` - Runtime file storage (created automatically, excluded from git)
- `tests/` - Comprehensive test suite with integration tests
- `templates/` - Flask HTML templates

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

### Mask-Based Hair Detection System
The core innovation of this system:
- **MaskBasedFaceAnalyzer** class in `face_analyzer_mask.py` implements `_determine_actual_head_top()` method
- Uses BiRefNet segmentation masks when available for precise hair boundary detection
- Eliminates "double hair margin" problem where 25% hair margin was added to landmark 10 (which already includes hair)
- Achieves millimeter precision (30.2mm accuracy vs previous 19.1mm errors)
- Falls back gracefully to landmark-only detection when ONNX session unavailable
- Measurements preserved through entire pipeline via crop_data to prevent re-analysis drift

### Compliance Optimization Algorithm
Advanced coefficient-based system for automatic compliance adjustment:
- **Intelligent Priority System**: Eye position > Head size > Head margins > Safety margins
- **Coefficient-Based Corrections**: 95% adjustment for eye positioning, 70% for head margins
- **Multi-Stage Processing**: Initial positioning → compliance analysis → intelligent adjustment
- **Safety Mechanisms**: Prevents head/chin cropping with 5px safety margins
- **Adaptive Logic**: Different strategies for different photo specifications (Schengen vs standard)
- **Real-time Feedback**: Detailed logging of adjustment reasons and amounts
- **Performance Metrics**: Tracks adjustment success rates and compliance improvements

### Enhanced Eye Detection System
Advanced eye landmark detection for improved positioning accuracy:
- **176 eye-specific landmarks** across 20 regions (vs previous 4 basic points)
- **Hierarchical landmark selection**: pupil → iris → contour → center with quality scoring
- **Detailed eye regions**: iris, pupil, upper/lower lids, eyebrows, complete contours
- **Quality assessment**: `_analyze_eye_detection_quality()` scores available landmarks
- **MediaPipe optimization**: `static_image_mode=True`, `refine_landmarks=True`, lowered confidence thresholds
- **Face centering refinement**: uses detailed eye landmarks to correct face center positioning
- **Improved robustness**: better handling of glasses, makeup, partial occlusion, and various angles

### Enhanced Head Contour Detection System
Comprehensive head boundary detection with 429 total landmarks for millimeter precision:
- **217 head contour landmarks** across 20 regions (vs previous basic face contour)
- **Detailed forehead mapping**: 28 landmarks including left/right boundaries, temples, complete contour
- **Precise chin/jaw detection**: 21 landmarks covering center, left/right jaw, angles, complete jawline
- **Cheekbone and temple areas**: 10+ landmarks each for left/right cheekbones and detailed temple regions
- **Hierarchical boundary selection**: complete head contour → detailed regions → basic fallbacks
- **Multi-region face width calculation**: head_contour_complete → cheekbones → eye span weighting
- **Enhanced mask integration**: 30% larger search areas with detailed landmark-guided boundaries
- **Improved positioning algorithms**: separate forehead and chin detection with weighted center correction

### Photo Specification Extensions
The application now supports 249 countries and document types with enhanced compliance validation.

When adding new countries/documents:
1. Add PhotoSpecification entry to DOCUMENT_SPECIFICATIONS in `photo_specs.py`
2. Update COUNTRY_DISPLAY_NAMES mapping in `main.py` if needed
3. Ensure background_color maps to BACKGROUND_COLOR_MAP in `image_processing.py`
4. Consider adding head positioning control fields for fine-tuning mask-based detection
5. Use official government sources for source_urls to ensure authenticity