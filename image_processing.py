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
from face_analyzer import calculate_crop_dimensions
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

# Абстрактный базовый класс
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
        self.process_with_updates(None)

    def process_with_updates(self, socketio):
        if socketio:
            socketio.emit('processing_status', {'status': 'Loading image'})
        img_cv = cv2.imread(self.input_path)
        if img_cv is None:
            raise ValueError("Failed to read the uploaded image")

        if socketio:
            socketio.emit('processing_status', {'status': 'Detecting face landmarks'})
        # mp_face_mesh module is still available via 'import mediapipe as mp'
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

        face_landmarks = None
        # The loop with detection_configs is removed. Using the single injected face_mesh instance.
        results = self.face_mesh.process(img_rgb)
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            logging.info("Face landmarks detected with injected FaceMesh instance.")
        
        if not face_landmarks:
            raise ValueError("Не удалось обнаружить лицо. Пожалуйста, убедитесь, что лицо хорошо видно")

        if socketio:
            socketio.emit('processing_status', {'status': 'Calculating crop dimensions'})
        img_height, img_width = img_cv.shape[:2]
        # Ensure self.photo_spec is passed to calculate_crop_dimensions
        crop_data = calculate_crop_dimensions(face_landmarks, img_height, img_width, self.photo_spec)

        if socketio:
            socketio.emit('processing_status', {'status': 'Cropping and scaling image'})
        processed_img = self._crop_and_scale_image(img_cv, crop_data) # crop_data is from the new calculate_crop_dimensions

        if socketio:
            socketio.emit('processing_status', {'status': 'Removing background'})
        
        # Determine target background color from spec
        target_bg_color_name = self.photo_spec.background_color.lower()
        target_bg_rgb = BACKGROUND_COLOR_MAP.get(target_bg_color_name)
        if target_bg_rgb is None:
            logging.warning(f"Background color '{self.photo_spec.background_color}' not in BACKGROUND_COLOR_MAP. Defaulting to white.")
            target_bg_rgb = (255, 255, 255)
            
        processed_img = remove_background_and_make_white(processed_img, self.ort_session, target_bg_rgb)

        if socketio:
            socketio.emit('processing_status', {'status': 'Enhancing image'})
        processed_img = self._enhance_image(processed_img) # Will use self.gfpganer

        if socketio:
            socketio.emit('processing_status', {'status': 'Saving processed image'})
        # Use DPI from photo_spec for saving
        processed_img.save(self.processed_path, dpi=(self.photo_spec.dpi, self.photo_spec.dpi), quality=95)

        # --- Calculate final measurements in mm for photo_info and compliance check ---
        mm_per_pixel = PhotoSpecification.MM_PER_INCH / self.photo_spec.dpi
        
        achieved_head_height_mm = crop_data['achieved_head_height_px'] * mm_per_pixel
        achieved_eye_level_from_top_mm = crop_data['achieved_eye_level_from_top_px'] * mm_per_pixel
        achieved_eye_level_from_bottom_mm = self.photo_spec.photo_height_mm - achieved_eye_level_from_top_mm

        # --- Compliance Checks ---
        compliance = {}
        spec_head_range_mm_str = "N/A"
        if self.photo_spec.head_min_mm is not None and self.photo_spec.head_max_mm is not None:
            compliance['head_height'] = (self.photo_spec.head_min_mm <= achieved_head_height_mm <= self.photo_spec.head_max_mm)
            spec_head_range_mm_str = f"{self.photo_spec.head_min_mm:.1f} - {self.photo_spec.head_max_mm:.1f} mm"
        elif self.photo_spec.head_min_px is not None and self.photo_spec.head_max_px is not None: # Fallback to px if mm not directly in spec
            compliance['head_height'] = (self.photo_spec.head_min_px <= crop_data['achieved_head_height_px'] <= self.photo_spec.head_max_px)
            spec_head_range_mm_str = f"Approx {self.photo_spec.head_min_px * mm_per_pixel:.1f} - {self.photo_spec.head_max_px * mm_per_pixel:.1f} mm"
        else:
            compliance['head_height'] = "N/A (No spec range)"

        spec_eye_range_mm_str = "N/A"
        if self.photo_spec.eye_min_from_bottom_mm is not None and self.photo_spec.eye_max_from_bottom_mm is not None:
            compliance['eye_position'] = (self.photo_spec.eye_min_from_bottom_mm <= achieved_eye_level_from_bottom_mm <= self.photo_spec.eye_max_from_bottom_mm)
            spec_eye_range_mm_str = f"{self.photo_spec.eye_min_from_bottom_mm:.1f} - {self.photo_spec.eye_max_from_bottom_mm:.1f} mm (from bottom)"
        elif self.photo_spec.eye_min_from_top_mm is not None and self.photo_spec.eye_max_from_top_mm is not None:
            compliance['eye_position'] = (self.photo_spec.eye_min_from_top_mm <= achieved_eye_level_from_top_mm <= self.photo_spec.eye_max_from_top_mm)
            spec_eye_range_mm_str = f"{self.photo_spec.eye_min_from_top_mm:.1f} - {self.photo_spec.eye_max_from_top_mm:.1f} mm (from top)"
        else:
            compliance['eye_position'] = "N/A (No spec range)"
            
        photo_info = {
            'achieved_head_height_mm': round(achieved_head_height_mm, 2),
            'spec_head_height_range_mm': spec_head_range_mm_str,
            'achieved_eye_level_from_bottom_mm': round(achieved_eye_level_from_bottom_mm, 2),
            'spec_eye_level_range_from_bottom_mm': spec_eye_range_mm_str,
            'file_size_kb': round(os.path.getsize(self.processed_path) / 1024, 2),
            'photo_dimensions_px': f"{self.photo_spec.photo_width_px}x{self.photo_spec.photo_height_px} @ {self.photo_spec.dpi} DPI",
            'compliance': compliance,
            'spec_country': self.photo_spec.country_code,
            'spec_document_name': self.photo_spec.document_name,
        }

        # Prepare data for preview_creator (expects inches for head_height and eye_to_bottom)
        preview_crop_data_for_drawing = {
            'head_height': achieved_head_height_mm / PhotoSpecification.MM_PER_INCH, 
            'eye_to_bottom': achieved_eye_level_from_bottom_mm / PhotoSpecification.MM_PER_INCH,
        }
        
        if socketio:
            socketio.emit('processing_status', {'status': 'Creating preview'})
        create_preview_with_watermark(
            self.processed_path,
            self.preview_path,
            preview_crop_data_for_drawing, # Use the adapted crop_data for preview
            face_landmarks,    # face_landmarks might be needed by preview_creator if it uses FaceAnalyzer
            self.fonts_folder
        )

        if socketio:
            socketio.emit('processing_status', {'status': 'Creating printable image'})
        # Pass photo_spec to printable creators if they need DPI or physical dimensions
        create_printable_image(
            self.processed_path,
            self.printable_path,
            self.fonts_folder, # Fonts folder for any text on printable
            rows=2, # Example, could be dynamic based on paper size / photo size
            cols=2, # Example
            photo_spec=self.photo_spec # Pass spec for DPI, dimensions
        )

        if socketio:
            socketio.emit('processing_status', {'status': 'Creating printable preview'})
        create_printable_preview(
            self.processed_path, # Source image for the small photos in preview
            self.printable_preview_path,
            self.fonts_folder, # For watermarks or text on preview
            rows=2, # Match create_printable_image
            cols=2, # Match create_printable_image
            photo_spec=self.photo_spec # Pass spec for DPI, dimensions
        )

        if socketio:
            socketio.emit('processing_status', {'status': 'Processing complete'})
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
        # Enhancing the image with GFPGAN
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

