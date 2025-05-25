# face_analyzer_mask.py

import math
import logging
import numpy as np
from photo_specs import PhotoSpecification

# MediaPipe FaceMesh landmarks mapping
FACE_MESH_POINTS = {
    'forehead_top': [10],
    'forehead_center': [9, 10, 151],
    'temple_left': [234, 127, 162], 
    'temple_right': [454, 356, 389],
    'left_eye_center': [468, 470], 
    'right_eye_center': [473, 475],
    'left_eye_inner': [133],
    'left_eye_outer': [33],
    'right_eye_inner': [362],
    'right_eye_outer': [263],
    'chin_bottom': [152],
    'face_contour': [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                     397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                     172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109],
}

class MaskBasedFaceAnalyzer:
    """Face analyzer that uses BiRefNet segmentation mask for accurate hair detection"""
    
    def __init__(self, landmarks, img_height, img_width, segmentation_mask=None):
        if landmarks is None or not hasattr(landmarks, 'landmark') or not landmarks.landmark:
            raise ValueError("Landmarks are invalid or empty.")
        if img_height <= 0 or img_width <= 0:
            raise ValueError("Image height and width must be positive.")

        self.landmarks = landmarks
        self.img_height = img_height
        self.img_width = img_width
        self.segmentation_mask = segmentation_mask 
        self.normalized_points = self._normalize_landmarks()
        self.refined_actual_head_top_y = None
        self._determine_actual_head_top()

    def _normalize_landmarks(self):
        """Convert normalized MediaPipe landmarks to pixel coordinates"""
        normalized = {}
        max_landmark_idx = len(self.landmarks.landmark) - 1
        
        for region, points_indices in FACE_MESH_POINTS.items():
            region_coords = []
            for p_idx in points_indices:
                if 0 <= p_idx <= max_landmark_idx:
                    landmark = self.landmarks.landmark[p_idx]
                    region_coords.append(
                        (landmark.x * self.img_width,
                         landmark.y * self.img_height)
                    )
                else:
                    logging.warning(f"Index {p_idx} for region {region} out of bounds ({max_landmark_idx}).")
            
            if region_coords: 
                normalized[region] = region_coords

        if 'face_contour' in normalized and normalized['face_contour']: # check if not empty
            normalized['face_contour_top'] = [min(normalized['face_contour'], key=lambda pt: pt[1])]
            normalized['face_contour_bottom'] = [max(normalized['face_contour'], key=lambda pt: pt[1])]
        else: # Fallback if face_contour is missing or empty
            logging.warning("Face contour data missing or empty, attempting to use other fallbacks for top/bottom.")
            # Attempt to use forehead_top and chin_bottom directly if they exist from points
            # This part is tricky if face_contour itself is the source for these.
            # The critical_regions_fallbacks below will handle if these are still missing.

        critical_regions_fallbacks = {
            'forehead_top': 'face_contour_top',
            'chin_bottom': 'face_contour_bottom',
        }
        
        for region, fallback_key in critical_regions_fallbacks.items():
            if region not in normalized:
                if fallback_key in normalized:
                    normalized[region] = normalized[fallback_key]
                    logging.warning(f"Fallback: Used '{fallback_key}' for '{region}'.")
                else: # If fallback_key itself is missing (e.g. face_contour_top)
                    # This situation should be caught by the checks below
                    pass 
        
        if 'forehead_top' not in normalized or not normalized['forehead_top']: 
            logging.error(f"Failed to find forehead_top. Available regions: {list(n for n in normalized if normalized[n])}")
            raise ValueError("Essential 'forehead_top' cannot be determined.")
        if 'chin_bottom' not in normalized or not normalized['chin_bottom']: 
            logging.error(f"Failed to find chin_bottom. Available regions: {list(n for n in normalized if normalized[n])}")
            raise ValueError("Essential 'chin_bottom' cannot be determined.")

        for eye_side in ['left', 'right']:
            center_key = f'{eye_side}_eye_center'
            inner_key = f'{eye_side}_eye_inner'
            outer_key = f'{eye_side}_eye_outer'
            if center_key not in normalized and inner_key in normalized and outer_key in normalized and \
               normalized[inner_key] and normalized[outer_key]: # check if lists are not empty
                p_in = normalized[inner_key][0]
                p_out = normalized[outer_key][0]
                normalized[center_key] = [((p_in[0] + p_out[0])/2, (p_in[1] + p_out[1])/2)]
                logging.warning(f"Fallback: Used inner/outer for '{center_key}'.")
        
        if ('left_eye_center' not in normalized or not normalized['left_eye_center']) or \
           ('right_eye_center' not in normalized or not normalized['right_eye_center']):
            logging.error("CRITICAL: Eye landmarks for eye_level missing even with fallbacks.")
            # Depending on strictness, could raise ValueError here
            # raise ValueError("Essential eye landmarks for eye_level cannot be determined.")


        logging.debug(f"Normalized {len(normalized)} landmark regions.")
        return normalized
        
    def _determine_actual_head_top(self):
        landmark_forehead_top_y = min(pt[1] for pt in self.normalized_points['forehead_top'])
        self.refined_actual_head_top_y = landmark_forehead_top_y 

        if self.segmentation_mask is not None and isinstance(self.segmentation_mask, np.ndarray):
            logging.info("🎯 Refining head top using BiRefNet segmentation mask.")
            mask_h, mask_w = self.segmentation_mask.shape[:2]
            if mask_h != self.img_height or mask_w != self.img_width:
                logging.warning(f"Mask dimensions ({mask_w}x{mask_h}) differ from image ({self.img_width}x{self.img_height}).")

            face_x_coords = []
            for region_key in ['temple_left', 'temple_right', 'face_contour']:
                if region_key in self.normalized_points and self.normalized_points[region_key]:
                    face_x_coords.extend([pt[0] for pt in self.normalized_points[region_key]])
            
            if not face_x_coords:
                search_x_start, search_x_end = 0, self.img_width
            else:
                min_face_x, max_face_x = min(face_x_coords), max(face_x_coords)
                face_width = max_face_x - min_face_x
                padding_x = face_width * 0.25 # Increased padding for wider hair search
                search_x_start = max(0, int(min_face_x - padding_x))
                search_x_end = min(self.img_width, int(max_face_x + padding_x))
            
            if search_x_start >= search_x_end:
                search_x_start, search_x_end = 0, self.img_width

            scan_y_upper_limit = 0 
            scan_y_lower_limit = int(landmark_forehead_top_y + (self.img_height * 0.10)) # Scan a bit lower
            scan_y_lower_limit = min(scan_y_lower_limit, self.img_height)

            roi_mask = self.segmentation_mask[scan_y_upper_limit:scan_y_lower_limit, search_x_start:search_x_end]
            foreground_pixels_y_in_roi, _ = np.where(roi_mask > 128) # Threshold mask if it's not binary

            if foreground_pixels_y_in_roi.size > 0:
                mask_refined_head_top_y = float(np.min(foreground_pixels_y_in_roi) + scan_y_upper_limit)
                logging.info(f"   Mask-refined head top: {mask_refined_head_top_y:.1f}px; Landmark head top: {landmark_forehead_top_y:.1f}px")
                self.refined_actual_head_top_y = min(landmark_forehead_top_y, mask_refined_head_top_y)
                if landmark_forehead_top_y - mask_refined_head_top_y > 5:
                    logging.info(f"   📏 Hair detected: {(landmark_forehead_top_y - mask_refined_head_top_y):.1f}px above landmark forehead")
            else:
                logging.warning("No foreground pixels found in mask ROI. Using landmark-based head top.")
        else:
            logging.info("🎯 No segmentation mask. Using landmark-based head top.")
        logging.info(f"✅ Final head top Y: {self.refined_actual_head_top_y:.1f}px")

    def analyze_face_dimensions(self):
        if self.refined_actual_head_top_y is None:
            raise RuntimeError("refined_actual_head_top_y was not set.")
            
        actual_head_top_y = self.refined_actual_head_top_y
        chin_bottom_y = max(pt[1] for pt in self.normalized_points['chin_bottom'])

        if ('left_eye_center' in self.normalized_points and self.normalized_points['left_eye_center']) and \
           ('right_eye_center' in self.normalized_points and self.normalized_points['right_eye_center']):
            left_eye_y = np.mean([pt[1] for pt in self.normalized_points['left_eye_center']])
            right_eye_y = np.mean([pt[1] for pt in self.normalized_points['right_eye_center']])
            eye_level_y = (left_eye_y + right_eye_y) / 2
        else: 
            logging.warning("Eye center landmarks missing. Estimating eye_level_y as 40% down from head top to chin.") # Changed to warning
            eye_level_y = actual_head_top_y + (chin_bottom_y - actual_head_top_y) * 0.40 
            
        if 'face_contour' in self.normalized_points and self.normalized_points['face_contour']:
            face_contour_x_coords = [pt[0] for pt in self.normalized_points['face_contour']]
            face_min_x, face_max_x = min(face_contour_x_coords), max(face_contour_x_coords)
            face_center_x = (face_min_x + face_max_x) / 2
            face_width_px = face_max_x - face_min_x
        else:
            logging.warning("Face contour not available for width. Using image center and estimated width.")
            face_center_x = self.img_width / 2
            face_width_px = self.img_width * 0.5 # Estimate, can be tuned

        actual_head_height_px = chin_bottom_y - actual_head_top_y
        if actual_head_height_px <= 1:
            raise ValueError(f"Invalid head height: {actual_head_height_px:.2f} (Top: {actual_head_top_y:.2f}, Chin: {chin_bottom_y:.2f}).")

        logging.info(f"📏 Face dimensions: Head={actual_head_height_px:.1f}px, Width={face_width_px:.1f}px")
        logging.info(f"📍 Positions: Top={actual_head_top_y:.1f}px, Eyes={eye_level_y:.1f}px, Chin={chin_bottom_y:.1f}px")
        return {'actual_head_top_y': actual_head_top_y, 'chin_bottom_y': chin_bottom_y, 
                'eye_level_y': eye_level_y, 'face_center_x': face_center_x,
                'actual_head_height_px': actual_head_height_px, 'face_width_px': face_width_px}


def calculate_mask_based_crop_dimensions(face_landmarks, img_height: int, img_width: int, 
                                        photo_spec: PhotoSpecification, 
                                        segmentation_mask: np.ndarray = None):
    logging.info(f"🎯 Starting MASK-BASED crop calculation for {photo_spec.country_code} {photo_spec.document_name}")
    logging.info(f"   Image: {img_width}x{img_height}, Mask provided: {segmentation_mask is not None}")
    
    try:
        analyzer = MaskBasedFaceAnalyzer(face_landmarks, img_height, img_width, segmentation_mask)
        dims = analyzer.analyze_face_dimensions()
    except ValueError as e:
        logging.error(f"Error during MaskBasedFaceAnalysis: {e}")
        # Return a structure indicating failure
        return { 'positioning_success': False, 'warnings': [f"Face analysis error: {e}"], 
                 'scale_factor': 1.0, 'crop_top': 0, 'crop_bottom': photo_spec.photo_height_px,
                 'crop_left': 0, 'crop_right': photo_spec.photo_width_px,
                 'final_photo_width_px': photo_spec.photo_width_px, 
                 'final_photo_height_px': photo_spec.photo_height_px,
                 'achieved_head_height_px': 0, 'achieved_eye_level_from_top_px': 0,
                 'achieved_head_top_from_crop_top_px': 0 }


    original_actual_head_height_px = dims['actual_head_height_px']
    target_photo_width_px = photo_spec.photo_width_px
    target_photo_height_px = photo_spec.photo_height_px

    if not (photo_spec.head_min_px and photo_spec.head_max_px):
        logging.error("Head min/max px not defined in photo_spec.")
        return { 'positioning_success': False, 'warnings': ["Head pixel specs missing."], # ... (plus other default fields)
                'scale_factor': 1.0, 'crop_top': 0, 'crop_bottom': photo_spec.photo_height_px,
                 'crop_left': 0, 'crop_right': photo_spec.photo_width_px,
                 'final_photo_width_px': photo_spec.photo_width_px, 
                 'final_photo_height_px': photo_spec.photo_height_px,
                 'achieved_head_height_px': 0, 'achieved_eye_level_from_top_px': 0,
                 'achieved_head_top_from_crop_top_px': 0}


    if original_actual_head_height_px <= 0:
        logging.error(f"Invalid original_actual_head_height_px: {original_actual_head_height_px}")
        return { 'positioning_success': False, 'warnings': ["Invalid original head height."], # ...
                 'scale_factor': 1.0, 'crop_top': 0, 'crop_bottom': photo_spec.photo_height_px,
                 'crop_left': 0, 'crop_right': photo_spec.photo_width_px,
                 'final_photo_width_px': photo_spec.photo_width_px, 
                 'final_photo_height_px': photo_spec.photo_height_px,
                 'achieved_head_height_px': 0, 'achieved_eye_level_from_top_px': 0,
                 'achieved_head_top_from_crop_top_px': 0}

    # --- REVISED SCALE FACTOR LOGIC ---
    ideal_target_head_px = (photo_spec.head_min_px + photo_spec.head_max_px) / 2.0
    
    # Try to aim for ideal size first
    scale_factor = ideal_target_head_px / original_actual_head_height_px
    logging.info(f"📏 Scale for ideal head ({ideal_target_head_px:.1f}px from original {original_actual_head_height_px:.1f}px): {scale_factor:.4f}")

    current_scaled_head_height = original_actual_head_height_px * scale_factor

    # Priority 1: Ensure head is not LARGER than max_px
    if current_scaled_head_height > photo_spec.head_max_px:
        scale_factor = photo_spec.head_max_px / original_actual_head_height_px
        logging.info(f"   Adjusted scale to meet head_max_px ({photo_spec.head_max_px:.1f}px). New scale: {scale_factor:.4f}")
        current_scaled_head_height = original_actual_head_height_px * scale_factor # Update current height

    # Priority 2: Ensure head is not SMALLER than min_px (if possible without violating max_px)
    if current_scaled_head_height < photo_spec.head_min_px:
        scale_for_min_head = photo_spec.head_min_px / original_actual_head_height_px
        # Check if scaling for min_head would make it exceed max_head
        if original_actual_head_height_px * scale_for_min_head <= photo_spec.head_max_px:
            scale_factor = scale_for_min_head
            logging.info(f"   Adjusted scale to meet head_min_px ({photo_spec.head_min_px:.1f}px). New scale: {scale_factor:.4f}")
        else:
            # Cannot meet min_px without exceeding max_px. Prioritize not exceeding max_px.
            # scale_factor is already set to respect max_px (or was for ideal and within range).
            logging.warning(f"   Cannot meet head_min_px ({photo_spec.head_min_px:.1f}px) without exceeding head_max_px. "
                            f"Using current scale {scale_factor:.4f} (head: {current_scaled_head_height:.1f}px).")

    # Global scale limits (e.g., to prevent extreme upscaling of tiny faces or extreme downscaling)
    # These limits should generally not override the spec-driven scaling unless absolutely necessary.
    # Let's make these limits a bit wider or conditional.
    MIN_ACCEPTABLE_SCALE = 0.10 # Allow more aggressive downscaling if needed for large heads
    MAX_ACCEPTABLE_SCALE = 4.0  # Allow more upscaling for small heads

    if scale_factor < MIN_ACCEPTABLE_SCALE:
        # If scale is very small, it's because original head was huge and we respected head_max_px.
        # So, we should generally keep this small scale.
        logging.warning(f"   Scale {scale_factor:.4f} is below MIN_ACCEPTABLE_SCALE ({MIN_ACCEPTABLE_SCALE}). "
                        f"Keeping it as it's spec-driven.")
    elif scale_factor > MAX_ACCEPTABLE_SCALE:
        logging.warning(f"   Scale {scale_factor:.4f} is above MAX_ACCEPTABLE_SCALE ({MAX_ACCEPTABLE_SCALE}). Clamping.")
        scale_factor = MAX_ACCEPTABLE_SCALE
    
    # Final check on scale_factor if it was clamped by MIN_ACCEPTABLE_SCALE when it shouldn't have been
    # The logic above tries to preserve spec-driven scales even if they are outside reasonable_scale
    # So, just log the final scale.
    
    scaled_actual_head_height_px = original_actual_head_height_px * scale_factor
    logging.info(f"📏 Final scale factor: {scale_factor:.4f}, Resulting head height: {scaled_actual_head_height_px:.1f}px")
    logging.info(f"   Photo Spec head range: {photo_spec.head_min_px}-{photo_spec.head_max_px}px")
    # --- END OF REVISED SCALE FACTOR LOGIC ---


    # Scale all coordinates
    scaled_img_width = img_width * scale_factor
    scaled_img_height = img_height * scale_factor

    scaled_actual_head_top_y = dims['actual_head_top_y'] * scale_factor
    scaled_chin_bottom_y = dims['chin_bottom_y'] * scale_factor
    scaled_eye_level_y = dims['eye_level_y'] * scale_factor
    scaled_face_center_x = dims['face_center_x'] * scale_factor
    
    # --- 2. VERTICAL POSITIONING ---
    crop_top = 0
    positioning_method = "NotSet"

    schengen_spec_active = "DE_SCHENGEN" in photo_spec.country_code.upper()

    if schengen_spec_active and \
       photo_spec.eye_min_from_bottom_px is not None and \
       photo_spec.eye_max_from_bottom_px is not None and \
       photo_spec.distance_top_of_head_to_top_of_photo_min_px is not None and \
       photo_spec.distance_top_of_head_to_top_of_photo_max_px is not None:
        
        logging.info("   Applying Schengen-specific positioning logic.")
        # Step 1: Position by eyes first
        target_eye_from_bottom_px = (photo_spec.eye_min_from_bottom_px + 
                                    photo_spec.eye_max_from_bottom_px) / 2.0
        target_eye_from_top_px = target_photo_height_px - target_eye_from_bottom_px
        crop_top = scaled_eye_level_y - target_eye_from_top_px
        positioning_method = f"SchengenEyePriority (target eye_from_top: {target_eye_from_top_px:.1f}px)"
        logging.info(f"      Initial crop_top for ideal eye pos: {crop_top:.1f}px")

        # Step 2: Check and adjust head top distance
        current_head_top_dist = scaled_actual_head_top_y - crop_top
        min_req_head_top_dist = photo_spec.distance_top_of_head_to_top_of_photo_min_px
        max_req_head_top_dist = photo_spec.distance_top_of_head_to_top_of_photo_max_px
        
        logging.info(f"      Current head top dist: {current_head_top_dist:.1f}px (Spec: {min_req_head_top_dist}-{max_req_head_top_dist}px)")

        adjustment_needed = False
        if current_head_top_dist < min_req_head_top_dist:
            # Head too close to top or cropped. Need to move crop_top DOWN (increase).
            adjustment = min_req_head_top_dist - current_head_top_dist
            crop_top += adjustment
            logging.info(f"      Adjusted crop_top DOWN by {adjustment:.1f}px to meet min head top distance. New crop_top: {crop_top:.1f}px")
            adjustment_needed = True
        elif current_head_top_dist > max_req_head_top_dist:
            # Head too far from top. Need to move crop_top UP (decrease).
            adjustment = current_head_top_dist - max_req_head_top_dist
            crop_top -= adjustment
            logging.info(f"      Adjusted crop_top UP by {adjustment:.1f}px to meet max head top distance. New crop_top: {crop_top:.1f}px")
            adjustment_needed = True
        
        if adjustment_needed:
            positioning_method += " +SchengenHeadTopFineTune"
        else:
            positioning_method += " (HeadTop OK after EyePos)"
            
    else: # Standard logic for non-Schengen or incomplete Schengen specs
        gc_style_head_top_min_px = photo_spec.head_top_min_dist_from_photo_top_px
        gc_style_head_top_max_px = photo_spec.head_top_max_dist_from_photo_top_px
        
        if gc_style_head_top_min_px is not None and gc_style_head_top_max_px is not None:
            target_dist_px = (gc_style_head_top_min_px + gc_style_head_top_max_px) / 2.0
            crop_top = scaled_actual_head_top_y - target_dist_px
            positioning_method = f"GCStyleHeadTopDistance ({target_dist_px:.1f}px)"
            logging.info(f"   Positioning (Non-Schengen): GC-style head top. Target: {target_dist_px:.1f}px. crop_top: {crop_top:.1f}px")
        elif (photo_spec.eye_min_from_bottom_px is not None and 
              photo_spec.eye_max_from_bottom_px is not None):
            target_eye_from_bottom_px = (photo_spec.eye_min_from_bottom_px + 
                                        photo_spec.eye_max_from_bottom_px) / 2.0
            target_eye_from_top_px = target_photo_height_px - target_eye_from_bottom_px
            crop_top = scaled_eye_level_y - target_eye_from_top_px
            positioning_method = f"EyeFromBottom ({target_eye_from_bottom_px:.1f}px target_from_bottom, {target_eye_from_top_px:.1f}px target_from_top)"
            logging.info(f"   Positioning (Non-Schengen): Eyes from bottom. Target eye_from_top: {target_eye_from_top_px:.1f}px. crop_top: {crop_top:.1f}px")
        elif (photo_spec.eye_min_from_top_px is not None and photo_spec.eye_max_from_top_px is not None):
            target_eye_from_top_px = (photo_spec.eye_min_from_top_px + photo_spec.eye_max_from_top_px) / 2.0
            crop_top = scaled_eye_level_y - target_eye_from_top_px
            positioning_method = f"EyeFromTop ({target_eye_from_top_px:.1f}px target_from_top)"
            logging.info(f"   Positioning (Non-Schengen): Eyes from top. Target eye_from_top: {target_eye_from_top_px:.1f}px. crop_top: {crop_top:.1f}px")
        else: 
            default_margin_percent = getattr(photo_spec, 'default_head_top_margin_percent', 0.12)
            default_margin_px = target_photo_height_px * default_margin_percent
            crop_top = scaled_actual_head_top_y - default_margin_px
            positioning_method = f"DefaultMargin ({default_margin_px:.1f}px)"
            logging.info(f"   Positioning (Non-Schengen): DefaultMargin. Margin: {default_margin_px:.1f}px. crop_top: {crop_top:.1f}px")
    
    logging.info(f"📍 Positioning by {positioning_method}, initial crop_top: {crop_top:.1f}")

    # --- 3. HORIZONTAL POSITIONING ---
    crop_left = scaled_face_center_x - (target_photo_width_px / 2.0)

    # --- 4. MARGIN CORRECTIONS (Generic final safety checks) ---
    # For Schengen, min_visual_head_margin_px = 0, min_visual_chin_margin_px = 0 (from spec)
    # These corrections are now mainly for safety against negative margins.
    min_head_margin_px = getattr(photo_spec, 'min_visual_head_margin_px', 0) 
    min_chin_margin_px = getattr(photo_spec, 'min_visual_chin_margin_px', 0) 
    
    # A. Generic Head margin correction (ensure head top is not negative)
    current_head_margin_final_check = scaled_actual_head_top_y - crop_top
    if current_head_margin_final_check < min_head_margin_px:
        adjustment = min_head_margin_px - current_head_margin_final_check
        crop_top -= adjustment 
        logging.info(f"   Adjusted crop_top by {-adjustment:.1f}px for final GENERIC head margin (target: {min_head_margin_px}px, was: {current_head_margin_final_check:.1f}px). New crop_top: {crop_top:.1f}px.")
        positioning_method += " +FinalGenericHeadMarginFix"

    # B. Generic Chin margin correction
    current_chin_margin_final_check = (crop_top + target_photo_height_px) - scaled_chin_bottom_y
    if current_chin_margin_final_check < min_chin_margin_px:
        adjustment = min_chin_margin_px - current_chin_margin_final_check
        crop_top += adjustment 
        logging.info(f"   Adjusted crop_top by {adjustment:.1f}px for final GENERIC chin margin (target: {min_chin_margin_px}px, was: {current_chin_margin_final_check:.1f}px). New crop_top: {crop_top:.1f}px.")
        positioning_method += " +FinalGenericChinMarginFix"

    # Rollback logic removed - the new Schengen hierarchy should handle conflicts more explicitly


    # --- 5. BOUNDARY ADJUSTMENTS (ensure crop window is within scaled image) ---
    # Crop coordinates must be integers for slicing
    crop_top_i = int(round(crop_top))
    crop_left_i = int(round(crop_left))
    
    # Ensure crop window doesn't go outside the scaled image boundaries
    if crop_top_i < 0:
        logging.info(f"   Adjusting crop_top from {crop_top_i} to 0 (was outside top boundary).")
        crop_top_i = 0
    if crop_left_i < 0:
        logging.info(f"   Adjusting crop_left from {crop_left_i} to 0 (was outside left boundary).")
        crop_left_i = 0
    
    if crop_top_i + target_photo_height_px > int(round(scaled_img_height)):
        new_crop_top = int(round(scaled_img_height)) - target_photo_height_px
        logging.info(f"   Adjusting crop_top from {crop_top_i} to {new_crop_top} (was outside bottom boundary).")
        crop_top_i = max(0, new_crop_top) # Ensure it doesn't become negative if photo is too short
        
    if crop_left_i + target_photo_width_px > int(round(scaled_img_width)):
        new_crop_left = int(round(scaled_img_width)) - target_photo_width_px
        logging.info(f"   Adjusting crop_left from {crop_left_i} to {new_crop_left} (was outside right boundary).")
        crop_left_i = max(0, new_crop_left) # Ensure it doesn't become negative

    crop_bottom_i = crop_top_i + target_photo_height_px
    crop_right_i = crop_left_i + target_photo_width_px

    # --- 6. FINAL CALCULATIONS AND VALIDATION ---
    # All these are relative to the *final crop window* (target_photo_width_px x target_photo_height_px)
    final_head_top_from_crop_top_px = scaled_actual_head_top_y - crop_top_i
    final_chin_bottom_from_crop_top_px = scaled_chin_bottom_y - crop_top_i
    final_eye_level_from_crop_top_px = scaled_eye_level_y - crop_top_i
    
    # Eye level from bottom of *final photo*
    final_eye_from_bottom_px = target_photo_height_px - final_eye_level_from_crop_top_px

    # Visible head height in the final cropped photo
    # Head top relative to crop is final_head_top_from_crop_top_px. If negative, part of head is cut.
    # Chin bottom relative to crop is final_chin_bottom_from_crop_top_px. If > target_photo_height_px, part of chin is cut.
    
    visible_head_top_in_crop = max(0, final_head_top_from_crop_top_px)
    visible_chin_bottom_in_crop = min(target_photo_height_px, final_chin_bottom_from_crop_top_px)
    achieved_head_height_px = max(0, visible_chin_bottom_in_crop - visible_head_top_in_crop)

    logging.info(f"📍 Final crop window (on scaled img): T:{crop_top_i}, L:{crop_left_i}, B:{crop_bottom_i}, R:{crop_right_i}")
    logging.info(f"   Head pos in crop: Top={final_head_top_from_crop_top_px:.1f}px, Chin={final_chin_bottom_from_crop_top_px:.1f}px")
    logging.info(f"   Eye pos in crop: FromTop={final_eye_level_from_crop_top_px:.1f}px, FromBottom={final_eye_from_bottom_px:.1f}px")
    logging.info(f"📏 Achieved VISIBLE head height in crop: {achieved_head_height_px:.1f}px (Spec: {photo_spec.head_min_px}-{photo_spec.head_max_px}px)")

    warnings = []
    positioning_success = True # Assume success, falsify on error

    # Head size compliance (based on visible head height)
    if not (photo_spec.head_min_px <= achieved_head_height_px <= photo_spec.head_max_px):
        warnings.append(f"Head height {achieved_head_height_px:.1f}px (visible) outside spec ({photo_spec.head_min_px}-{photo_spec.head_max_px}px). Scaled head was {scaled_actual_head_height_px:.1f}px.")
        positioning_success = False # This is a critical failure

    # Eye positioning compliance
    eye_pos_compliant = True
    if photo_spec.eye_min_from_bottom_px is not None and photo_spec.eye_max_from_bottom_px is not None:
        if not (photo_spec.eye_min_from_bottom_px <= final_eye_from_bottom_px <= photo_spec.eye_max_from_bottom_px):
            warnings.append(f"Eyes from bottom {final_eye_from_bottom_px:.1f}px outside spec ({photo_spec.eye_min_from_bottom_px}-{photo_spec.eye_max_from_bottom_px}px).")
            eye_pos_compliant = False
    elif photo_spec.eye_min_from_top_px is not None and photo_spec.eye_max_from_top_px is not None: # Check from top if bottom not specified
         if not (photo_spec.eye_min_from_top_px <= final_eye_level_from_crop_top_px <= photo_spec.eye_max_from_top_px):
            warnings.append(f"Eyes from top {final_eye_level_from_crop_top_px:.1f}px outside spec ({photo_spec.eye_min_from_top_px}-{photo_spec.eye_max_from_top_px}px).")
            eye_pos_compliant = False
            
    if not eye_pos_compliant and (photo_spec.eye_min_from_bottom_px or photo_spec.eye_min_from_top_px): # If eye spec exists and not compliant
        positioning_success = False # Eye position is also critical

    # Head-top distance compliance
    if hasattr(photo_spec, 'head_top_min_dist_from_photo_top_px') and photo_spec.head_top_min_dist_from_photo_top_px is not None:
        # This check is on final_head_top_from_crop_top_px
        if not (photo_spec.head_top_min_dist_from_photo_top_px <= final_head_top_from_crop_top_px <= photo_spec.head_top_max_dist_from_photo_top_px):
            warnings.append(f"Head-top distance {final_head_top_from_crop_top_px:.1f}px outside spec ({photo_spec.head_top_min_dist_from_photo_top_px}-{photo_spec.head_top_max_dist_from_photo_top_px}px).")
            # This might be a non-critical warning for some specs, but can be critical for others like Green Card.
            # For now, let's assume it's critical if specified.
            positioning_success = False


    if warnings:
        logging.warning("Compliance warnings:")
        for w in warnings: logging.warning(f"   {w}")

    if positioning_success:
        logging.info("✅ Mask-based positioning successful!")
    else:
        logging.error("❌ Mask-based positioning failed one or more critical requirements.")

    return {
        'scale_factor': float(scale_factor),
        'crop_top': crop_top_i, # Use integer rounded values for slicing
        'crop_bottom': crop_bottom_i,
        'crop_left': crop_left_i,
        'crop_right': crop_right_i,
        'final_photo_width_px': target_photo_width_px,
        'final_photo_height_px': target_photo_height_px,
        'achieved_head_height_px': int(round(achieved_head_height_px)), # Visible head height
        'achieved_eye_level_from_top_px': int(round(final_eye_level_from_crop_top_px)),
        'achieved_eye_level_from_bottom_px': int(round(final_eye_from_bottom_px)),
        'achieved_head_top_from_crop_top_px': int(round(final_head_top_from_crop_top_px)),
        'positioning_method': positioning_method,
        'positioning_success': positioning_success,
        'warnings': warnings
    }