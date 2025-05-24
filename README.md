# Automated Visa and Passport Photo Processor

## Description

This application helps users generate compliant photos for various official documents, such as passports and visas. It automates several processing steps to ensure the final photo meets the specific requirements of the selected document type. Key capabilities include automatic face detection, background removal and replacement, image enhancement, and compliance checks against document rules.

## Features

*   **Automated Photo Processing Pipeline:** Streamlined workflow from image upload to processed photo generation with AI-powered precision.
*   **Advanced Hair Detection System:**
    *   BiRefNet mask-based hair detection for accurate head boundary identification
    *   Eliminates unreliable percentage-based hair estimates with actual AI-generated segmentation data
    *   Achieves millimeter-precision measurements (30.2mm accuracy for US Visa Lottery specs)
*   **Dynamic Document Specification System:**
    *   Supports a growing list of countries and document types (e.g., US Passport, US Visa, Schengen Visa, Indian Passport, Canadian Passport).
    *   Users can select their target Country and Document Type via a user-friendly web interface.
    *   Processing logic dynamically adjusts to the selected document's rules, including photo dimensions (width, height, DPI), required head position and size, and eye line placement.
*   **Background Removal & Replacement:**
    *   Automatically segments the foreground (person) from the existing background using BiRefNet ONNX model.
    *   Replaces the original background with a compliant color (e.g., white, light grey) as specified by the selected document rules.
*   **Face Enhancement:**
    *   Utilizes GFPGAN to improve facial clarity, sharpness, and overall quality of the portrait.
*   **Compliance Feedback:**
    *   Provides users with information on whether the processed photo meets key geometric requirements (e.g., head height, eye position) of the selected document, comparing achieved values against specification ranges in millimeters.
    *   Real-time compliance validation with precise measurements preserved through entire pipeline.
*   **Printable Layout Generation:**
    *   Creates a standard 4x6 inch printable sheet containing multiple copies of the processed photo, suitable for printing at photo labs. The layout respects the specific dimensions and DPI of the processed photo.
*   **Web Interface:**
    *   A Flask-based web application provides an easy-to-use interface for uploading photos, selecting document specifications, and viewing/downloading results.
    *   Real-time processing status updates via SocketIO.

## Key Innovations

*   **Mask-Based Hair Detection:** Revolutionary approach using BiRefNet segmentation masks to eliminate the "double hair margin" problem that plagued traditional landmark-only methods. This ensures accurate head measurements that comply with strict document requirements.
*   **Precision Measurement Pipeline:** Measurements are preserved through the entire processing workflow, preventing measurement drift that occurred with re-analysis approaches.
*   **Backward Compatibility:** Graceful fallback to landmark-only detection when BiRefNet models are unavailable.

## Tech Stack

*   **Backend:** Python, Flask, Flask-SocketIO
*   **Image Processing:** OpenCV, Pillow, NumPy
*   **AI Models:**
    *   **Face Detection & Landmarks:** MediaPipe FaceMesh for facial landmark detection
    *   **Background Segmentation:** BiRefNet ONNX model for precise background removal and hair boundary detection
    *   **Face Enhancement:** GFPGAN for facial quality improvement
    *   **Mask-Based Hair Detection:** Integrated BiRefNet segmentation masks for accurate head measurements
*   **Frontend:** HTML, Tailwind CSS, JavaScript
*   **Configuration:** Custom system in `photo_specs.py` for document rules, allowing easy addition and modification of specifications.

## Project Structure

```
.
├── main.py                   # Flask application, routes, main workflow orchestration
├── image_processing.py       # VisaPhotoProcessor class, core image processing pipeline
├── face_analyzer_mask.py     # Mask-based face analysis with BiRefNet integration
├── background_remover.py     # Background segmentation and replacement logic
├── photo_specs.py            # Dataclass for PhotoSpecification and list of document rules
├── preview_creator.py        # Generates preview images with watermarks and measurement lines
├── printable_creator.py      # Generates the 4x6 print layout
├── utils.py                  # Helper functions and constants
├── requirements.txt          # Python dependencies
├── .gitignore               # Git exclusion patterns for temporary files
├── CLAUDE.md                # Development guidance for Claude Code
├── templates/               # HTML templates (index.html)
├── fonts/                   # Font files (Arial.ttf)
├── models/                  # Directory for ONNX models
│   └── BiRefNet-portrait-epoch_150.onnx
├── gfpgan/                  # GFPGAN specific files
│   └── weights/
│       └── GFPGANv1.4.pth
├── uploads/                 # Runtime directory for uploaded images (auto-created)
├── processed/               # Runtime directory for processed images (auto-created)
├── previews/                # Runtime directory for preview images (auto-created)
└── tests/                   # Unit, integration, and application tests
    ├── test_assets/
    │   ├── sample_portrait.jpg # Sample image for integration testing
    │   └── IMG_5520.JPG       # Additional test image
    ├── test_image_processing.py
    ├── test_background_remover.py
    ├── test_main.py
    ├── test_preview_creator.py
    ├── test_printable_creator.py
    ├── test_integration_image_processing.py
    └── test_utils.py
```

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create and Activate a Python Virtual Environment:**
    ```bash
    python -m venv venv
    ```
    *   On macOS/Linux: `source venv/bin/activate`
    *   On Windows: `venv\Scripts\activate`

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download AI Models:**

    *   **BiRefNet (Background Segmentation):**
        *   The model `BiRefNet-portrait-epoch_150.onnx` is required.
        *   You need to acquire this model file and place it in the `models/` directory at the project root.
        *   *Note: A specific public download link for this exact pre-trained ONNX file is not provided here. You may need to find it from the official BiRefNet repository (if available as ONNX) or a trusted source for pre-trained computer vision models.*

    *   **GFPGAN (Face Enhancement):**
        *   The model `GFPGANv1.4.pth` is required.
        *   The application will attempt to download this model automatically if it's not found in the `gfpgan/weights/` directory during the first run (or on startup).
        *   Alternatively, you can download it manually from the official GFPGAN GitHub Releases page: [https://github.com/TencentARC/GFPGAN/releases](https://github.com/TencentARC/GFPGAN/releases) (look for v1.4 weights).
        *   Place the downloaded `.pth` file into the `gfpgan/weights/` directory.

5.  **Fonts:**
    *   Ensure the `fonts/` directory exists at the project root and contains `Arial.ttf`. If not, you will need to provide this font file for text rendering in previews and watermarks.

## Running the Application

1.  **Start the Flask Development Server:**
    From the project root directory:
    ```bash
    python main.py
    ```
2.  **Access in Web Browser:**
    Open your web browser and navigate to `http://127.0.0.1:8000` (or the address shown in the terminal).

## Usage

1.  **Select Country:** Choose the country for which the document photo is intended from the "Country" dropdown menu.
2.  **Select Document Type:** Once a country is selected, the "Document Type" dropdown will populate. Choose the specific document (e.g., Passport, Visa).
3.  **Upload Photo:** After both selections are made, the upload area will become active. Click to browse or drag & drop your photo onto the designated area. Supported formats are JPG, JPEG, and PNG. The maximum file size is 10MB.
4.  **Processing:** Wait for the application to process the photo. Real-time status updates will be shown on the screen.
5.  **Review and Download:**
    *   A preview of the processed photo, including measurement lines based on the selected specification, will be displayed.
    *   Detailed compliance feedback, including achieved head height and eye position in millimeters compared to the specification ranges, will be shown in a table.
    *   Download links will be available for:
        *   The processed photo (suitable for digital submission, respecting the document's DPI and pixel dimensions).
        *   A 4x6 inch printable sheet containing multiple copies of the processed photo, laid out according to the photo's specific dimensions.
    *   A preview of the 4x6 printable sheet layout is also displayed.

## Testing

To run the automated test suite:

1.  Ensure all development dependencies, including those for testing (e.g., `unittest`), are installed from `requirements.txt` (or a `requirements-dev.txt` if one exists).
2.  Make sure the necessary AI models are downloaded and placed in their respective directories (`models/` and `gfpgan/weights/`) as the integration tests might rely on them.
3.  A sample image `tests/test_assets/sample_portrait.jpg` is used for integration tests. A placeholder is created if missing, but a real portrait is recommended for meaningful testing.
4.  From the project root directory, execute:
    ```bash
    python -m unittest discover -s tests
    ```
    For more detailed output:
    ```bash
    python -m unittest discover -s tests -v
    ```

---

This README provides a comprehensive overview of the Automated Visa and Passport Photo Processor. For further details on specific modules, refer to the source code and inline comments.
