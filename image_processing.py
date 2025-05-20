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

from utils import clean_filename, is_allowed_file, PIXELS_PER_INCH, PHOTO_SIZE_PIXELS
from face_analyzer import calculate_crop_dimensions
from background_remover import remove_background_and_make_white
from preview_creator import create_preview_with_watermark
from printable_creator import create_printable_image, create_printable_preview

# Global initializations for gfpganer and ort_session are removed.
# They will be initialized in main.py and passed via DI.

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
                 face_mesh_instance):
        super().__init__(input_path, processed_path, preview_path, printable_path, printable_preview_path, fonts_folder)
        self.gfpganer = gfpganer_instance
        self.ort_session = ort_session_instance
        self.face_mesh = face_mesh_instance

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
        crop_data = calculate_crop_dimensions(face_landmarks, img_height, img_width)

        if socketio:
            socketio.emit('processing_status', {'status': 'Cropping and scaling image'})
        processed_img = self._crop_and_scale_image(img_cv, crop_data)

        if socketio:
            socketio.emit('processing_status', {'status': 'Removing background'})
        # Pass the injected ort_session instance
        processed_img = remove_background_and_make_white(processed_img, self.ort_session) 

        if socketio:
            socketio.emit('processing_status', {'status': 'Enhancing image'})
        processed_img = self._enhance_image(processed_img) # Will use self.gfpganer

        if socketio:
            socketio.emit('processing_status', {'status': 'Saving processed image'})
        processed_img.save(self.processed_path, dpi=(PIXELS_PER_INCH, PIXELS_PER_INCH), quality=95)

        if socketio:
            socketio.emit('processing_status', {'status': 'Creating preview'})
        create_preview_with_watermark(
            self.processed_path,
            self.preview_path,
            crop_data,
            face_landmarks,
            self.fonts_folder
        )

        if socketio:
            socketio.emit('processing_status', {'status': 'Creating printable image'})
        create_printable_image(
            self.processed_path,
            self.printable_path,
            self.fonts_folder,
            rows=2,
            cols=2
        )

        if socketio:
            socketio.emit('processing_status', {'status': 'Creating printable preview'})
        create_printable_preview(
            self.processed_path,
            self.printable_preview_path,
            self.fonts_folder,
            rows=2,
            cols=2
        )

        if socketio:
            socketio.emit('processing_status', {'status': 'Processing complete'})

        photo_info = {
            'head_height': round(crop_data['head_height'], 2),
            'eye_to_bottom': round(crop_data['eye_to_bottom'], 2),
            'file_size_kb': round(os.path.getsize(self.processed_path) / 1024, 2),
            'quality': 95,
            'compliance': {
                'head_height': 1.0 <= crop_data['head_height'] <= 1.375,
                'eye_to_bottom': 1.125 <= crop_data['eye_to_bottom'] <= 1.375
            }
        }

        return photo_info

    def _crop_and_scale_image(self, img_cv, crop_data):
        # Scaling
        scale = crop_data['scale_factor']
        scaled_width = int(img_cv.shape[1] * scale)
        scaled_height = int(img_cv.shape[0] * scale)
        scaled_img = cv2.resize(img_cv, (scaled_width, scaled_height), interpolation=cv2.INTER_LINEAR)

        # Cropping
        crop_top = max(0, crop_data['crop_top'])
        crop_bottom = min(scaled_height, crop_data['crop_bottom'])
        crop_left = max(0, crop_data['crop_left'])
        crop_right = min(scaled_width, crop_data['crop_right'])

        logging.debug(f"Scaling Image to: {scaled_width}x{scaled_height}")
        logging.debug(f"Cropping to: Left={crop_left}, Right={crop_right}, Top={crop_top}, Bottom={crop_bottom}")

        cropped = scaled_img[crop_top:crop_bottom, crop_left:crop_right]

        # Changing size with padding if necessary
        if cropped.shape[0] != PHOTO_SIZE_PIXELS or cropped.shape[1] != PHOTO_SIZE_PIXELS:
            from utils import create_image_with_padding
            cropped_pil = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
            cropped_pil = create_image_with_padding(cropped_pil, target_size=(PHOTO_SIZE_PIXELS, PHOTO_SIZE_PIXELS), padding_color=(255, 255, 255))
            cropped = cv2.cvtColor(np.array(cropped_pil), cv2.COLOR_RGB2BGR)
            logging.debug(f"Image resized with padding to {PHOTO_SIZE_PIXELS}x{PHOTO_SIZE_PIXELS}")

        pil_img = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
        return pil_img

    def _enhance_image(self, image):
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

