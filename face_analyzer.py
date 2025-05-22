# face_analyzer.py

import math
import logging
from utils import PIXELS_PER_INCH # PHOTO_SIZE_PIXELS will be replaced by photo_spec
from photo_specs import PhotoSpecification # Import for type hinting

# Точки лицевых меток для анализа
FACE_MESH_POINTS = {
    'forehead_top': [10, 109, 338],
    'chin_bottom': [152, 377, 378],
    'left_eye': [33, 160, 159],
    'right_eye': [362, 385, 386],
}

class FaceAnalyzer:
    def __init__(self, landmarks, img_height, img_width):
        self.landmarks = landmarks
        self.img_height = img_height
        self.img_width = img_width
        self.normalized_points = self._normalize_landmarks()

    def _normalize_landmarks(self):
        normalized = {}
        for region, points in FACE_MESH_POINTS.items():
            normalized[region] = [
                (self.landmarks.landmark[p].x * self.img_width,
                 self.landmarks.landmark[p].y * self.img_height)
                for p in points
            ]
        logging.debug(f"Normalized landmarks for regions: {list(normalized.keys())}")
        return normalized

    def get_head_measurements(self):
        # Верх головы
        head_top = min([pt[1] for pt in self.normalized_points['forehead_top']])

        # Нижняя точка подбородка
        chin_bottom = max([pt[1] for pt in self.normalized_points['chin_bottom']])

        # Уровень глаз
        left_eye_y = sum([pt[1] for pt in self.normalized_points['left_eye']]) / len(self.normalized_points['left_eye'])
        right_eye_y = sum([pt[1] for pt in self.normalized_points['right_eye']]) / len(self.normalized_points['right_eye'])
        eye_level = (left_eye_y + right_eye_y) / 2

        # Центр лица по X
        all_x = [pt[0] for pts in self.normalized_points.values() for pt in pts]
        face_center_x = sum(all_x) / len(all_x)

        logging.debug(f"Head Top: {head_top}, Chin Bottom: {chin_bottom}, Eye Level: {eye_level}, Face Center X: {face_center_x}")
        return head_top, chin_bottom, eye_level, face_center_x

def calculate_crop_dimensions(face_landmarks, img_height: int, img_width: int, photo_spec: PhotoSpecification):
    analyzer = FaceAnalyzer(face_landmarks, img_height, img_width)
    # These are measurements on the original, unscaled image
    original_head_top_px, original_chin_bottom_px, original_eye_level_px, original_face_center_x_px = analyzer.get_head_measurements()

    original_head_height_px = original_chin_bottom_px - original_head_top_px
    if original_head_height_px <= 0:
        raise ValueError("Calculated head height is zero or negative. Check landmarks.")

    # Target dimensions from photo_spec (these are the final desired photo dimensions in pixels)
    target_photo_width_px = photo_spec.photo_width_px
    target_photo_height_px = photo_spec.photo_height_px

    # Target head height in pixels from spec
    min_target_head_height_px = photo_spec.head_min_px
    max_target_head_height_px = photo_spec.head_max_px

    if min_target_head_height_px is None or max_target_head_height_px is None:
        # Fallback or error if spec doesn't define head height in pixels
        # For this example, we'll assume they are always available if needed by a spec.
        # Or use a default proportion of photo_height_px if that's a valid fallback.
        logging.warning(f"Head height pixel specs not fully defined for {photo_spec.country_code} - {photo_spec.document_name}. Using fallback if possible.")
        # Example fallback: min 50%, max 70% of photo height
        min_target_head_height_px = min_target_head_height_px or int(target_photo_height_px * 0.50) 
        max_target_head_height_px = max_target_head_height_px or int(target_photo_height_px * 0.69)


    # --- Scale Factor Calculation ---
    # Scale factor to make the original head fit within the target head height range
    scale_for_min_head = min_target_head_height_px / original_head_height_px
    scale_for_max_head = max_target_head_height_px / original_head_height_px
    
    # Initial scale: try to make head height a mid-point of the allowed range
    # This is a heuristic; could be average of min/max, or just aim for min.
    # Let's aim for the middle of the allowed head height range.
    ideal_target_head_height_px = (min_target_head_height_px + max_target_head_height_px) / 2
    scale_factor = ideal_target_head_height_px / original_head_height_px
    
    # Clamp scale factor: ensure scaled head is not too small or too large
    scale_factor = max(scale_factor, scale_for_min_head) 
    scale_factor = min(scale_factor, scale_for_max_head)

    # Further constraints: the scaled image must be at least as large as the target photo dimensions
    if int(img_width * scale_factor) < target_photo_width_px:
        scale_factor_for_width = target_photo_width_px / img_width
        scale_factor = max(scale_factor, scale_factor_for_width)
        
    if int(img_height * scale_factor) < target_photo_height_px:
        scale_factor_for_height = target_photo_height_px / img_height
        scale_factor = max(scale_factor, scale_factor_for_height)
    
    logging.debug(f"Chosen scale_factor: {scale_factor:.4f} (min_head_scale={scale_for_min_head:.4f}, max_head_scale={scale_for_max_head:.4f})")

    # --- Calculate dimensions after scaling ---
    scaled_img_width = int(img_width * scale_factor)
    scaled_img_height = int(img_height * scale_factor)
    
    scaled_head_top_px = original_head_top_px * scale_factor
    scaled_chin_bottom_px = original_chin_bottom_px * scale_factor
    scaled_eye_level_px = original_eye_level_px * scale_factor
    scaled_face_center_x_px = original_face_center_x_px * scale_factor
    scaled_head_height_px = scaled_chin_bottom_px - scaled_head_top_px


    # --- Cropping Logic ---
    # Horizontal cropping: Center the face
    crop_left = scaled_face_center_x_px - (target_photo_width_px / 2)
    crop_right = scaled_face_center_x_px + (target_photo_width_px / 2)

    # Adjust horizontal crop if it goes out of bounds of the scaled image
    if crop_left < 0:
        crop_right -= crop_left # Shift crop_right by the amount crop_left is negative
        crop_left = 0
    if crop_right > scaled_img_width:
        crop_left -= (crop_right - scaled_img_width) # Shift crop_left
        crop_right = scaled_img_width
    
    # Ensure crop width is maintained if adjustments made it too small (e.g. face too close to edge)
    # This might happen if scaled_img_width < target_photo_width_px, which should be prevented by scale_factor logic.
    # If after adjustments, crop_right - crop_left < target_photo_width_px, it implies an issue.
    # For now, assume scale_factor logic handles this.

    # Vertical cropping: Position eye line according to spec
    # Default to centering the head if no specific eye line rules are given,
    # or if eye line rules are complex to satisfy simultaneously with head height.
    # This part is complex and has many strategies.
    # Strategy:
    # 1. Prioritize head height (already done by scale_factor).
    # 2. Try to meet eye line specs.
    # 3. If specific eye line specs (from bottom/top) are available:
    #    Calculate crop_top based on placing the scaled_eye_level_px at the desired position within the target_photo_height_px.
    #    Example: If spec says eye_min_from_bottom_px to eye_max_from_bottom_px.
    #    Target eye_y_on_final_photo_from_top = target_photo_height_px - (eye_min_from_bottom_px + eye_max_from_bottom_px) / 2
    #    crop_top = scaled_eye_level_px - target_eye_y_on_final_photo_from_top
    
    # Using eye line from bottom spec:
    if photo_spec.eye_min_from_bottom_px is not None and photo_spec.eye_max_from_bottom_px is not None:
        # Target position of eye line from the top of the *final cropped photo*
        target_eye_pos_from_top_px = target_photo_height_px - ( (photo_spec.eye_min_from_bottom_px + photo_spec.eye_max_from_bottom_px) / 2 )
        crop_top = scaled_eye_level_px - target_eye_pos_from_top_px
    elif photo_spec.eye_min_from_top_px is not None and photo_spec.eye_max_from_top_px is not None:
        target_eye_pos_from_top_px = (photo_spec.eye_min_from_top_px + photo_spec.eye_max_from_top_px) / 2
        crop_top = scaled_eye_level_px - target_eye_pos_from_top_px
    else:
        # Fallback: if no specific eye line, try to center the head vertically.
        # This means the center of the scaled head should be at the center of the target photo height.
        scaled_head_center_y = (scaled_head_top_px + scaled_chin_bottom_px) / 2
        crop_top = scaled_head_center_y - (target_photo_height_px / 2)

    crop_bottom = crop_top + target_photo_height_px

    # Adjust vertical crop if it goes out of bounds
    if crop_top < 0:
        crop_bottom -= crop_top # Shift crop_bottom
        crop_top = 0
    if crop_bottom > scaled_img_height:
        crop_top -= (crop_bottom - scaled_img_height) # Shift crop_top
        crop_bottom = scaled_img_height

    # Final check: Ensure crop dimensions are not negative or larger than scaled image
    # This should ideally be handled by robust adjustment logic above.
    crop_top = max(0, int(crop_top))
    crop_bottom = min(scaled_img_height, int(crop_bottom))
    crop_left = max(0, int(crop_left))
    crop_right = min(scaled_img_width, int(crop_right))

    # --- Final measurements on the cropped area (relative to crop_top, crop_left) ---
    # Eye level relative to the top of the *final cropped photo*
    final_eye_level_on_cropped_photo_px = scaled_eye_level_px - crop_top
    
    # Head height on the final photo is the scaled_head_height_px, assuming crop captures it.
    # More accurately, it's the portion of the scaled head visible in the crop.
    # However, the scaling was done to target head height, so scaled_head_height_px is what we aimed for.
    final_head_height_on_cropped_photo_px = scaled_head_height_px 
    
    # Convert pixel measurements to spec units (e.g., inches or mm) for photo_info later
    # This conversion is better done in VisaPhotoProcessor where DPI is unambiguously from spec.
    # Here, we return pixel values relative to the final crop.

    crop_data = {
        'scale_factor': float(scale_factor),
        'crop_top': crop_top,
        'crop_bottom': crop_bottom,
        'crop_left': crop_left,
        'crop_right': crop_right,
        'final_photo_width_px': target_photo_width_px, # Store target dims for reference
        'final_photo_height_px': target_photo_height_px,
        'achieved_head_height_px': int(round(final_head_height_on_cropped_photo_px)),
        'achieved_eye_level_from_top_px': int(round(final_eye_level_on_cropped_photo_px)),
    }
    # Note: 'eye_to_bottom' and 'head_height' in inches/mm for direct compliance check
    # will be calculated in VisaPhotoProcessor from these pixel values and spec's DPI.

    logging.debug(f"Final calculated crop_data: {crop_data}")
    return crop_data