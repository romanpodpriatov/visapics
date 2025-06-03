# image_processing.py

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont  # Add ImageDraw and ImageFont here
import mediapipe as mp
import logging
from abc import ABC, abstractmethod
import torchvision

from gfpgan import GFPGANer # For type hinting if used, instance provided by DI
import onnxruntime as ort # For type hinting if used, instance provided by DI
# mediapipe is already imported as mp
from photo_specs import PhotoSpecification # Import for type hinting

from utils import clean_filename, is_allowed_file, PIXELS_PER_INCH # PHOTO_SIZE_PIXELS is not used directly here
from face_analyzer_mask import calculate_mask_based_crop_dimensions
from background_remover import remove_background_and_make_white
from preview_creator import create_preview_with_watermark
from printable_creator import create_printable_image, create_printable_preview

# Global initializations for gfpganer and ort_session are removed.
# They will be initialized in main.py and passed via DI.

# --- Background Color Mapping ---
BACKGROUND_COLOR_MAP = {
    "white": (255, 255, 255),
    "off-white": (245, 245, 245),
    "light_grey": (211, 211, 211),
    "light_gray": (211, 211, 211), # Alias
    "blue": (173, 216, 230) 
    # Add more as needed by PhotoSpecification entries
}

# Abstract base class
class ImageProcessor(ABC):
    def __init__(self, 
                 input_path, 
                 processed_path, 
                 preview_path, 
                 printable_path, 
                 printable_preview_path, 
                 fonts_folder):
        self.input_path = input_path
        self.processed_path = processed_path
        self.preview_path = preview_path
        self.printable_path = printable_path
        self.printable_preview_path = printable_preview_path
        self.fonts_folder = fonts_folder

    @abstractmethod
    def process(self):
        pass

class VisaPhotoProcessor(ImageProcessor):
    def __init__(self, 
                 input_path, 
                 processed_path, 
                 preview_path, 
                 printable_path, 
                 printable_preview_path, 
                 fonts_folder,
                 gfpganer_instance, 
                 ort_session_instance, 
                 face_mesh_instance,
                 photo_spec: PhotoSpecification): # Add photo_spec parameter
        super().__init__(input_path, processed_path, preview_path, printable_path, printable_preview_path, fonts_folder)
        self.gfpganer = gfpganer_instance
        self.ort_session = ort_session_instance
        self.face_mesh = face_mesh_instance
        self.photo_spec = photo_spec # Store the photo_spec

    def process(self):
        # Call the process_with_updates method with a dummy socketio object
        # if you want to keep the process method for compatibility
        return self.process_with_updates(None)

    def process_with_updates(self, socketio, session_id=None):
        def emit_status(status):
            """Helper function to emit status to specific session or globally"""
            if socketio:
                if session_id:
                    socketio.emit('processing_status', {'status': status}, room=session_id)
                else:
                    socketio.emit('processing_status', {'status': status})
        
        emit_status('Loading image')
        img_cv = cv2.imread(self.input_path)
        if img_cv is None:
            raise ValueError("Failed to read the uploaded image")

        emit_status('Detecting face landmarks')
        # mp_face_mesh module is still available via 'import mediapipe as mp'
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

        face_landmarks = None
        # The loop with detection_configs is removed. Using the single injected face_mesh instance.
        results = self.face_mesh.process(img_rgb)
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            logging.info("Face landmarks detected with injected FaceMesh instance.")
        
        if not face_landmarks:
            raise ValueError("Failed to detect face. Please ensure the face is clearly visible.")

        emit_status('Getting segmentation mask for hair detection')
        
        # Step 1: Get segmentation mask from original image for hair detection
        img_height, img_width = img_cv.shape[:2]
        segmentation_mask = None
        
        # Determine target background color from spec (needed for both mask generation and final background removal)
        target_bg_color_name = self.photo_spec.background_color.lower()
        target_bg_rgb = BACKGROUND_COLOR_MAP.get(target_bg_color_name)
        if target_bg_rgb is None:
            logging.warning(f"Background color '{self.photo_spec.background_color}' not in BACKGROUND_COLOR_MAP. Defaulting to white.")
            target_bg_rgb = (255, 255, 255)
        
        if self.ort_session is not None:
            # Convert CV2 to PIL for background removal
            img_pil_temp = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
            
            # Get segmentation mask for hair detection
            _, segmentation_mask = remove_background_and_make_white(img_pil_temp, self.ort_session, target_bg_rgb, return_mask=True)
            logging.info(f"📏 Segmentation mask obtained: {segmentation_mask.shape}")
        else:
            logging.warning("No ONNX session available for segmentation mask. Using landmark-only hair detection.")

        emit_status('Calculating crop dimensions with mask-based hair detection')
        
        # Step 2: Calculate crop dimensions using mask-based hair detection
        crop_data = calculate_mask_based_crop_dimensions(face_landmarks, img_height, img_width, self.photo_spec, segmentation_mask)

        emit_status('Cropping and scaling image')
        processed_img = self._crop_and_scale_image(img_cv, crop_data)

        emit_status('Removing background')
        
        # Step 3: Apply background removal to the cropped image (if ONNX session available)
        if self.ort_session is not None:
            processed_img = remove_background_and_make_white(processed_img, self.ort_session, target_bg_rgb)
        else:
            logging.warning("No ONNX session available. Skipping background removal.")

        emit_status('Enhancing image')
        processed_img = self._enhance_image(processed_img) # Will use self.gfpganer

        emit_status('Saving processed image')
        # Use DPI from photo_spec for saving
        processed_img.save(self.processed_path, dpi=(self.photo_spec.dpi, self.photo_spec.dpi), quality=95)

        # --- Calculate final measurements in mm for photo_info and compliance check ---
        # Initialize variables with safe defaults
        mm_per_pixel = PhotoSpecification.MM_PER_INCH / self.photo_spec.dpi
        achieved_head_height_mm = 0.0
        achieved_eye_level_from_bottom_mm = 0.0
        achieved_eye_level_from_top_mm = 0.0
        
        # Use crop_data measurements which include BiRefNet mask-based hair detection
        # This is more accurate than re-analyzing the final image with landmarks only
        if crop_data and 'achieved_head_height_px' in crop_data:
            achieved_head_height_mm = crop_data['achieved_head_height_px'] * mm_per_pixel
            
            # Calculate eye positions from crop_data
            if 'achieved_eye_level_from_bottom_px' in crop_data:
                achieved_eye_level_from_bottom_mm = crop_data['achieved_eye_level_from_bottom_px'] * mm_per_pixel
            elif 'achieved_eye_level_from_top_px' in crop_data:
                achieved_eye_level_from_top_mm = crop_data['achieved_eye_level_from_top_px'] * mm_per_pixel
                achieved_eye_level_from_bottom_mm = self.photo_spec.photo_height_mm - achieved_eye_level_from_top_mm
            else:
                # Fallback calculation
                achieved_eye_level_from_bottom_mm = (self.photo_spec.eye_min_from_bottom_mm + self.photo_spec.eye_max_from_bottom_mm) / 2 if self.photo_spec.eye_min_from_bottom_mm and self.photo_spec.eye_max_from_bottom_mm else 35.0
                
            achieved_eye_level_from_top_mm = self.photo_spec.photo_height_mm - achieved_eye_level_from_bottom_mm
            
            logging.info(f"✅ Using mask-based measurements from crop_data:")
            logging.info(f"   Head: {achieved_head_height_mm:.1f}mm (from {crop_data['achieved_head_height_px']}px)")
            logging.info(f"   Eyes: {achieved_eye_level_from_bottom_mm:.1f}mm from bottom")
            logging.info(f"   DPI: {self.photo_spec.dpi}, mm_per_pixel: {mm_per_pixel:.6f}")
        else:
            # Last resort: set basic defaults based on photo spec
            achieved_head_height_mm = (self.photo_spec.head_min_mm + self.photo_spec.head_max_mm) / 2 if self.photo_spec.head_min_mm and self.photo_spec.head_max_mm else 30.0
            achieved_eye_level_from_bottom_mm = (self.photo_spec.eye_min_from_bottom_mm + self.photo_spec.eye_max_from_bottom_mm) / 2 if self.photo_spec.eye_min_from_bottom_mm and self.photo_spec.eye_max_from_bottom_mm else 35.0
            achieved_eye_level_from_top_mm = self.photo_spec.photo_height_mm - achieved_eye_level_from_bottom_mm
            logging.error("Both re-analysis and theoretical measurements failed - using fallback defaults")

        # --- Compliance Checks ---
        compliance = {}
        spec_head_range_mm_str = "N/A"
        if self.photo_spec.head_min_mm is not None and self.photo_spec.head_max_mm is not None:
            compliance['head_height'] = bool(self.photo_spec.head_min_mm <= achieved_head_height_mm <= self.photo_spec.head_max_mm)
            spec_head_range_mm_str = f"{self.photo_spec.head_min_mm:.1f} - {self.photo_spec.head_max_mm:.1f} mm"
        elif self.photo_spec.head_min_px is not None and self.photo_spec.head_max_px is not None: # Fallback to px if mm not directly in spec
            compliance['head_height'] = bool(self.photo_spec.head_min_px <= crop_data['achieved_head_height_px'] <= self.photo_spec.head_max_px)
            spec_head_range_mm_str = f"Approx {self.photo_spec.head_min_px * mm_per_pixel:.1f} - {self.photo_spec.head_max_px * mm_per_pixel:.1f} mm"
        else:
            compliance['head_height'] = "N/A (No spec range)"

        spec_eye_range_mm_str = "N/A"
        if self.photo_spec.eye_min_from_bottom_mm is not None and self.photo_spec.eye_max_from_bottom_mm is not None:
            eye_compliant = bool(self.photo_spec.eye_min_from_bottom_mm <= achieved_eye_level_from_bottom_mm <= self.photo_spec.eye_max_from_bottom_mm)
            compliance['eye_position'] = eye_compliant
            compliance['eye_to_bottom'] = eye_compliant
            spec_eye_range_mm_str = f"{self.photo_spec.eye_min_from_bottom_mm:.1f} - {self.photo_spec.eye_max_from_bottom_mm:.1f} mm (from bottom)"
        elif self.photo_spec.eye_min_from_top_mm is not None and self.photo_spec.eye_max_from_top_mm is not None:
            eye_compliant = bool(self.photo_spec.eye_min_from_top_mm <= achieved_eye_level_from_top_mm <= self.photo_spec.eye_max_from_top_mm)
            compliance['eye_position'] = eye_compliant
            compliance['eye_to_bottom'] = eye_compliant
            spec_eye_range_mm_str = f"{self.photo_spec.eye_min_from_top_mm:.1f} - {self.photo_spec.eye_max_from_top_mm:.1f} mm (from top)"
        else:
            compliance['eye_position'] = "N/A (No spec range)"
            compliance['eye_to_bottom'] = "N/A (No spec range)"
        
        # Add compliance information output
        logging.info(f"📊 COMPLIANCE ANALYSIS:")
        logging.info(f"   Head Height: {achieved_head_height_mm:.2f}mm (requirement: {spec_head_range_mm_str})")
        logging.info(f"   Head Compliance: {'✅ COMPLIANT' if compliance.get('head_height', False) else '❌ NON-COMPLIANT'}")
        logging.info(f"   Eye Distance: {achieved_eye_level_from_bottom_mm:.2f}mm (requirement: {spec_eye_range_mm_str})")
        logging.info(f"   Eye Compliance: {'✅ COMPLIANT' if compliance.get('eye_to_bottom', False) else '❌ NON-COMPLIANT'}")
            
        # Ensure all values are defined before creating photo_info
        try:
            file_size_kb = round(os.path.getsize(self.processed_path) / 1024, 2) if os.path.exists(self.processed_path) else 0.0
        except Exception as e:
            logging.error(f"Error calculating file size: {e}")
            file_size_kb = 0.0
            
        # Calculate values in inches for visafoto-style display
        achieved_head_height_inches = achieved_head_height_mm / PhotoSpecification.MM_PER_INCH
        achieved_eye_level_from_bottom_inches = achieved_eye_level_from_bottom_mm / PhotoSpecification.MM_PER_INCH
        achieved_eye_level_from_top_inches = (self.photo_spec.photo_height_mm - achieved_eye_level_from_bottom_mm) / PhotoSpecification.MM_PER_INCH

        # Image definition parameters string for visafoto style
        img_def_params = (
            f"Head height (up to the top of the hair): {achieved_head_height_inches:.2f}in; "
            f"Distance from the bottom of the photo to the eye line: {achieved_eye_level_from_bottom_inches:.2f}in"
        )
        
        compliance_overall_success = crop_data.get('positioning_success', False)
        compliance_warnings = crop_data.get('warnings', [])
        
        head_height_compliant = False
        achieved_head_height_px = crop_data.get('achieved_head_height_px', 0)
        if self.photo_spec.head_min_px is not None and self.photo_spec.head_max_px is not None:
            head_height_compliant = self.photo_spec.head_min_px <= achieved_head_height_px <= self.photo_spec.head_max_px
        
        # Default eye position compliance to True if no eye requirements are specified
        eye_position_compliant = True
        achieved_eye_level_from_bottom_px = crop_data.get('achieved_eye_level_from_bottom_px', 0)
        achieved_eye_level_from_top_px = self.photo_spec.photo_height_px - achieved_eye_level_from_bottom_px
        
        # Only check eye position if requirements are specified
        if self.photo_spec.eye_min_from_bottom_px is not None and self.photo_spec.eye_max_from_bottom_px is not None:
            eye_position_compliant = self.photo_spec.eye_min_from_bottom_px <= achieved_eye_level_from_bottom_px <= self.photo_spec.eye_max_from_bottom_px
        elif self.photo_spec.eye_min_from_top_px is not None and self.photo_spec.eye_max_from_top_px is not None:
            eye_position_compliant = self.photo_spec.eye_min_from_top_px <= achieved_eye_level_from_top_px <= self.photo_spec.eye_max_from_top_px

        photo_info = {
            'spec_country': self.photo_spec.country_code,
            'spec_document_name': self.photo_spec.document_name,
            'photo_size_str': f"Width: {self.photo_spec.photo_width_inches:.2f}in, Height: {self.photo_spec.photo_height_inches:.2f}in ({self.photo_spec.photo_width_px}x{self.photo_spec.photo_height_px}px, {self.photo_spec.photo_width_mm:.0f}x{self.photo_spec.photo_height_mm:.0f}mm)",
            'image_definition_parameters': img_def_params,
            'required_size_kb_str': self.photo_spec.required_size_kb_str,
            'result_size_kb': f"{file_size_kb:.0f} KB",
            'background_color_name': self.photo_spec.background_color.replace("_", " ").title(),
            'background_color_rgb': target_bg_rgb, # For UI color swatch
            'resolution_dpi': self.photo_spec.dpi,
            'printable': "Yes",
            'suitable_for_online_submission': "Yes",
            'source_urls': self.photo_spec.source_urls or ([self.photo_spec.source_url] if self.photo_spec.source_url else []),
            'compliance_overall': compliance_overall_success,
            'compliance_warnings': compliance_warnings,
            # For preview drawing, pass necessary pixel values relative to the *final processed photo*
            'achieved_head_height_inches': achieved_head_height_inches, # For label text
            'achieved_eye_level_from_bottom_inches': achieved_eye_level_from_bottom_inches, # For label text
            'head_height_compliant': head_height_compliant, # For potential conditional styling (not used by drawing directly)
            'eye_position_compliant': eye_position_compliant # For potential conditional styling
        }
        
        preview_drawing_data = {
            'photo_spec': self.photo_spec, # Full spec object
            'achieved_head_top_y_on_photo_px': crop_data['achieved_head_top_from_crop_top_px'],
            'achieved_eye_level_y_on_photo_px': achieved_eye_level_from_top_px, 
            'achieved_head_height_px': achieved_head_height_px,
            'photo_width_px': self.photo_spec.photo_width_px,
            'photo_height_px': self.photo_spec.photo_height_px,
        }
        
        emit_status('Creating preview')
        create_preview_with_watermark(
            self.processed_path,
            self.preview_path,
            preview_drawing_data,
            self.fonts_folder
        )

        emit_status('Creating printable image')
        # Pass photo_spec to printable creators if they need DPI or physical dimensions
        create_printable_image(
            self.processed_path,
            self.printable_path,
            self.fonts_folder, # Fonts folder for any text on printable
            photo_spec=self.photo_spec # Pass spec for DPI, dimensions
        )

        emit_status('Creating printable preview')
        logging.info("About to call create_printable_preview with new signature")
        create_printable_preview(
            self.processed_path, # Source image for the small photos in preview
            self.printable_preview_path,
            self.fonts_folder, # For watermarks or text on preview
            photo_spec=self.photo_spec # Pass spec for DPI, dimensions
        )

        emit_status('Processing complete')
        return photo_info

    def _crop_and_scale_image(self, img_cv, crop_data_from_analyzer):
        # Scaling
        scale = crop_data_from_analyzer['scale_factor']
        scaled_width = int(img_cv.shape[1] * scale)
        scaled_height = int(img_cv.shape[0] * scale)
        scaled_img = cv2.resize(img_cv, (scaled_width, scaled_height), interpolation=cv2.INTER_LINEAR)

        # Cropping coordinates from analyzer are relative to the scaled image
        crop_top = crop_data_from_analyzer['crop_top']
        crop_bottom = crop_data_from_analyzer['crop_bottom']
        crop_left = crop_data_from_analyzer['crop_left']
        crop_right = crop_data_from_analyzer['crop_right']
        
        # The actual width/height of the cropped area before padding
        # cropped_actual_width = crop_right - crop_left # Not used directly below
        # cropped_actual_height = crop_bottom - crop_top # Not used directly below

        logging.debug(f"Scaling Image to: {scaled_width}x{scaled_height}")
        logging.debug(f"Cropping from scaled to: Left={crop_left}, Right={crop_right}, Top={crop_top}, Bottom={crop_bottom}")
        logging.debug(f"Analyzer's intended final photo size (pixels): {crop_data_from_analyzer.get('final_photo_width_px')}x{crop_data_from_analyzer.get('final_photo_height_px')}")


        cropped_img_cv = scaled_img[crop_top:crop_bottom, crop_left:crop_right]

        # Target dimensions for the final photo (from spec)
        target_final_width_px = self.photo_spec.photo_width_px
        target_final_height_px = self.photo_spec.photo_height_px
        
        # If the cropped image (from analyzer's perspective) is not already the exact target size,
        # apply padding to make it so. This step ensures the output image strictly matches spec dimensions.
        if cropped_img_cv.shape[1] != target_final_width_px or cropped_img_cv.shape[0] != target_final_height_px:
            from utils import create_image_with_padding # Keep import local
            
            # Log difference if any
            if cropped_img_cv.shape[1] != crop_data_from_analyzer.get('final_photo_width_px') or \
               cropped_img_cv.shape[0] != crop_data_from_analyzer.get('final_photo_height_px'):
                logging.warning(f"Cropped image size ({cropped_img_cv.shape[1]}x{cropped_img_cv.shape[0]}) "
                                f"differs from analyzer's intended final size "
                                f"({crop_data_from_analyzer.get('final_photo_width_px')}x{crop_data_from_analyzer.get('final_photo_height_px')}). "
                                f"Will pad to spec size: {target_final_width_px}x{target_final_height_px}.")

            cropped_pil = Image.fromarray(cv2.cvtColor(cropped_img_cv, cv2.COLOR_BGR2RGB))
            padded_pil = create_image_with_padding(
                cropped_pil, 
                target_size=(target_final_width_px, target_final_height_px), 
                padding_color=(255, 255, 255) # Default white padding
            )
            logging.debug(f"Image after padding (if applied) to {target_final_width_px}x{target_final_height_px}")
            return padded_pil # Return the PIL image that has been padded
        else:
            # If no padding needed, just convert the successfully cropped CV2 image to PIL
            pil_img = Image.fromarray(cv2.cvtColor(cropped_img_cv, cv2.COLOR_BGR2RGB))
            return pil_img


    def _enhance_image(self, image: Image.Image): # Expects PIL Image
        # Enhancing the image with GFPGAN if available
        if self.gfpganer is None:
            logging.warning("GFPGANer not available. Skipping image enhancement.")
            return image  # Return original image without enhancement
        
        img_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        # Use the injected gfpganer instance
        _, _, restored_img = self.gfpganer.enhance( 
            img_np,
            has_aligned=False,
            only_center_face=False,
            paste_back=True
        )
        restored_pil = Image.fromarray(cv2.cvtColor(restored_img, cv2.COLOR_BGR2RGB))
        return restored_pil

    def _analyze_final_image_compliance(self):
        """
        Re-analyze the actual processed image to get accurate compliance measurements.
        Returns dict with actual measurements or None if analysis fails.
        """
        try:
            import mediapipe as mp
            
            # Load the processed image
            if not os.path.exists(self.processed_path):
                logging.warning("Processed image not found for compliance re-analysis")
                return None
            
            img = Image.open(self.processed_path)
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            h, w = img_cv.shape[:2]
            
            # Initialize MediaPipe Face Mesh
            face_mesh = mp.solutions.face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            # Process image
            img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(img_rgb)
            
            if not results.multi_face_landmarks:
                logging.warning("No face detected in processed image for compliance re-analysis")
                return None
            
            landmarks = results.multi_face_landmarks[0]
            
            # Key landmark indices for measurements
            forehead_points = [10, 151, 9, 8, 7]  # Top center forehead area
            chin_points = [175, 18, 175, 200, 199]  # Bottom chin area
            left_eye_center = [159, 158, 157, 173]
            right_eye_center = [386, 385, 384, 398]
            
            # Calculate positions
            forehead_y = min([landmarks.landmark[i].y * h for i in forehead_points])
            chin_y = max([landmarks.landmark[i].y * h for i in chin_points])
            
            left_eye_y = np.mean([landmarks.landmark[i].y * h for i in left_eye_center])
            right_eye_y = np.mean([landmarks.landmark[i].y * h for i in right_eye_center])
            eye_line_y = (left_eye_y + right_eye_y) / 2
            
            # Convert to mm
            mm_per_pixel = self.photo_spec.photo_height_mm / h
            
            head_height_mm = (chin_y - forehead_y) * mm_per_pixel
            eye_from_bottom_mm = (h - eye_line_y) * mm_per_pixel
            
            return {
                'head_height_mm': head_height_mm,
                'eye_from_bottom_mm': eye_from_bottom_mm,
                'forehead_y_px': forehead_y,
                'chin_y_px': chin_y,
                'eye_line_y_px': eye_line_y
            }
            
        except Exception as e:
            logging.error(f"Error in compliance re-analysis: {e}")
            return None

    def _create_printable_preview(self):
        # Open the printable image
        printable_image = Image.open(self.printable_path)

        # Resize for preview
        preview_size = (600, 900)
        printable_preview = printable_image.resize(preview_size, Image.LANCZOS)

        # Add watermark to the preview
        watermark_text = "PREVIEW"
        draw = ImageDraw.Draw(printable_preview)
        font_size = int(preview_size[0] * 0.05)
        try:
            arial_font_path = os.path.join(self.fonts_folder, 'Arial.ttf')
            watermark_font = ImageFont.truetype(arial_font_path, font_size)
        except IOError:
            logging.warning("Arial font not found. Using default font.")
            watermark_font = ImageFont.load_default()

        # Position for watermark
        watermark_positions = [
            (preview_size[0] * 0.25, preview_size[1] * 0.33),
            (preview_size[0] * 0.75, preview_size[1] * 0.33),
            (preview_size[0] * 0.5, preview_size[1] * 0.5),
            (preview_size[0] * 0.25, preview_size[1] * 0.67),
            (preview_size[0] * 0.75, preview_size[1] * 0.67),
            (preview_size[0] * 0.5, preview_size[1] * 0.8)
        ]

        for pos in watermark_positions:
            draw.text(
                pos,
                watermark_text,
                fill=(0, 0, 0),  # Ensure the fill color is visible
                font=watermark_font,
                anchor='mm'
            )

        # Save the preview with watermark
        printable_preview.save(self.printable_preview_path, quality=85)
        logging.info(f"Printable preview saved at {self.printable_preview_path}")

