# face_analyzer_mask.py
# MASK-BASED APPROACH: Using BiRefNet segmentation for accurate hair detection

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
                    # For FaceMesh, we don't check visibility/presence as they're often 0
                    # Just use the landmarks directly
                    region_coords.append(
                        (landmark.x * self.img_width,
                         landmark.y * self.img_height)
                    )
                else:
                    logging.warning(f"Index {p_idx} for region {region} out of bounds ({max_landmark_idx}).")
            
            if region_coords: 
                normalized[region] = region_coords

        # Critical fallbacks
        if 'face_contour' in normalized:
            normalized['face_contour_top'] = [min(normalized['face_contour'], key=lambda pt: pt[1])]
            normalized['face_contour_bottom'] = [max(normalized['face_contour'], key=lambda pt: pt[1])]

        # Ensure critical regions exist
        critical_regions_fallbacks = {
            'forehead_top': 'face_contour_top',
            'chin_bottom': 'face_contour_bottom',
        }
        
        for region, fallback_key in critical_regions_fallbacks.items():
            if region not in normalized and fallback_key in normalized:
                normalized[region] = normalized[fallback_key]
                logging.warning(f"Fallback: Used '{fallback_key}' for '{region}'.")
        
        # Debug what regions we have
        logging.debug(f"Available normalized regions: {list(normalized.keys())}")
        
        if 'forehead_top' not in normalized: 
            logging.error(f"Failed to find forehead_top. Available regions: {list(normalized.keys())}")
            raise ValueError("Essential 'forehead_top' cannot be determined.")
        if 'chin_bottom' not in normalized: 
            logging.error(f"Failed to find chin_bottom. Available regions: {list(normalized.keys())}")
            raise ValueError("Essential 'chin_bottom' cannot be determined.")

        # Eye center fallbacks
        for eye_side in ['left', 'right']:
            center_key = f'{eye_side}_eye_center'
            inner_key = f'{eye_side}_eye_inner'
            outer_key = f'{eye_side}_eye_outer'
            if center_key not in normalized and inner_key in normalized and outer_key in normalized:
                p_in = normalized[inner_key][0]
                p_out = normalized[outer_key][0]
                normalized[center_key] = [((p_in[0] + p_out[0])/2, (p_in[1] + p_out[1])/2)]
                logging.warning(f"Fallback: Used inner/outer for '{center_key}'.")
        
        if 'left_eye_center' not in normalized or 'right_eye_center' not in normalized:
            logging.error("CRITICAL: Eye landmarks for eye_level missing even with fallbacks.")

        logging.debug(f"Normalized {len(normalized)} landmark regions.")
        return normalized
        
    def _determine_actual_head_top(self):
        """
        Determines actual head top using segmentation mask if available.
        This is the KEY improvement - using BiRefNet output for accurate hair detection.
        """
        # Start with landmark-based forehead top as baseline
        landmark_forehead_top_y = min(pt[1] for pt in self.normalized_points['forehead_top'])
        self.refined_actual_head_top_y = landmark_forehead_top_y  # Default to landmark

        if self.segmentation_mask is not None and isinstance(self.segmentation_mask, np.ndarray):
            logging.info("🎯 Refining head top using BiRefNet segmentation mask.")
            
            mask_h, mask_w = self.segmentation_mask.shape[:2]
            if mask_h != self.img_height or mask_w != self.img_width:
                logging.warning(f"Mask dimensions ({mask_w}x{mask_h}) differ from image ({self.img_width}x{self.img_height}). This may cause issues.")

            # Determine horizontal ROI based on face landmarks
            face_x_coords = []
            
            # Use temple points for face width if available
            for region in ['temple_left', 'temple_right', 'face_contour']:
                if region in self.normalized_points:
                    face_x_coords.extend([pt[0] for pt in self.normalized_points[region]])
            
            if not face_x_coords:
                logging.warning("No face X coordinates for mask ROI. Using full image width.")
                search_x_start, search_x_end = 0, self.img_width
            else:
                min_face_x = min(face_x_coords)
                max_face_x = max(face_x_coords)
                face_width = max_face_x - min_face_x
                padding_x = face_width * 0.15  # 15% padding on each side
                search_x_start = max(0, int(min_face_x - padding_x))
                search_x_end = min(self.img_width, int(max_face_x + padding_x))
            
            if search_x_start >= search_x_end:
                search_x_start, search_x_end = 0, self.img_width
                logging.warning("Corrected invalid horizontal mask search ROI to full width.")

            # Vertical ROI: Scan from top of image down to below landmark
            scan_y_upper_limit = 0  # Top of image
            scan_y_lower_limit = int(landmark_forehead_top_y + (self.img_height * 0.05))  # 5% below landmark
            scan_y_lower_limit = min(scan_y_lower_limit, self.img_height)

            # Extract ROI from mask
            roi_mask = self.segmentation_mask[scan_y_upper_limit:scan_y_lower_limit, search_x_start:search_x_end]
            
            # Find all foreground pixels (person/hair) in the ROI
            foreground_pixels_y_in_roi, _ = np.where(roi_mask > 0)

            if foreground_pixels_y_in_roi.size > 0:
                # Find the topmost foreground pixel (minimum Y)
                mask_refined_head_top_y = float(np.min(foreground_pixels_y_in_roi) + scan_y_upper_limit)
                
                logging.info(f"   Mask-refined head top: {mask_refined_head_top_y:.1f}px")
                logging.info(f"   Landmark head top: {landmark_forehead_top_y:.1f}px")
                
                # Use the higher point (smaller Y value) - this includes hair
                self.refined_actual_head_top_y = min(landmark_forehead_top_y, mask_refined_head_top_y)
                
                hair_difference = landmark_forehead_top_y - mask_refined_head_top_y
                if hair_difference > 5:  # Significant hair detected
                    logging.info(f"   📏 Hair detected: {hair_difference:.1f}px above landmark forehead")
                else:
                    logging.info(f"   📏 Minimal hair: {hair_difference:.1f}px difference")
            else:
                logging.warning("No foreground pixels found in mask ROI. Using landmark-based head top.")
        else:
            logging.info("🎯 No segmentation mask provided. Using landmark-based head top.")
        
        logging.info(f"✅ Final head top Y: {self.refined_actual_head_top_y:.1f}px")

    def analyze_face_dimensions(self):
        """Analyze face dimensions using the refined head top from mask analysis"""
        if self.refined_actual_head_top_y is None:
            raise RuntimeError("refined_actual_head_top_y was not set.")
            
        actual_head_top_y = self.refined_actual_head_top_y
        chin_bottom_y = max(pt[1] for pt in self.normalized_points['chin_bottom'])

        # Eye Level calculation
        if 'left_eye_center' in self.normalized_points and 'right_eye_center' in self.normalized_points:
            left_eye_y = np.mean([pt[1] for pt in self.normalized_points['left_eye_center']])
            right_eye_y = np.mean([pt[1] for pt in self.normalized_points['right_eye_center']])
            eye_level_y = (left_eye_y + right_eye_y) / 2
        else: 
            logging.error("Eye center landmarks missing. Estimating eye_level_y.")
            eye_level_y = actual_head_top_y + (chin_bottom_y - actual_head_top_y) * 0.40
            
        # Face Center X & Width
        if 'face_contour' in self.normalized_points and self.normalized_points['face_contour']:
            face_contour_x_coords = [pt[0] for pt in self.normalized_points['face_contour']]
            face_min_x, face_max_x = min(face_contour_x_coords), max(face_contour_x_coords)
            face_center_x = (face_min_x + face_max_x) / 2
            face_width_px = face_max_x - face_min_x
        else:
            logging.warning("Face contour not available. Using image center and estimated width.")
            face_center_x = self.img_width / 2
            face_width_px = self.img_width * 0.6 

        # CRITICAL: Head height now uses mask-refined top
        actual_head_height_px = chin_bottom_y - actual_head_top_y
        
        if actual_head_height_px <= 1:
            raise ValueError(f"Invalid head height: {actual_head_height_px:.2f} (Top: {actual_head_top_y:.2f}, Chin: {chin_bottom_y:.2f}).")

        logging.info(f"📏 Face dimensions: Head={actual_head_height_px:.1f}px, Width={face_width_px:.1f}px")
        logging.info(f"📍 Positions: Top={actual_head_top_y:.1f}px, Eyes={eye_level_y:.1f}px, Chin={chin_bottom_y:.1f}px")

        return {
            'actual_head_top_y': actual_head_top_y,
            'chin_bottom_y': chin_bottom_y,
            'eye_level_y': eye_level_y,
            'face_center_x': face_center_x,
            'actual_head_height_px': actual_head_height_px,
            'face_width_px': face_width_px
        }


def calculate_mask_based_crop_dimensions(face_landmarks, img_height: int, img_width: int, 
                                        photo_spec: PhotoSpecification, 
                                        segmentation_mask: np.ndarray = None):
    """
    Calculate crop dimensions using BiRefNet segmentation mask for accurate hair detection.
    This replaces hair margin heuristics with actual mask-based detection.
    """
    logging.info(f"🎯 Starting MASK-BASED crop calculation for {photo_spec.country_code} {photo_spec.document_name}")
    logging.info(f"   Image: {img_width}x{img_height}, Mask provided: {segmentation_mask is not None}")
    
    try:
        analyzer = MaskBasedFaceAnalyzer(face_landmarks, img_height, img_width, segmentation_mask)
        dims = analyzer.analyze_face_dimensions()
    except ValueError as e:
        logging.error(f"Error during MaskBasedFaceAnalysis: {e}")
        return { 
            'scale_factor': 1.0, 'crop_top': 0, 'crop_bottom': photo_spec.photo_height_px,
            'crop_left': 0, 'crop_right': photo_spec.photo_width_px,
            'final_photo_width_px': photo_spec.photo_width_px, 
            'final_photo_height_px': photo_spec.photo_height_px,
            'achieved_head_height_px': 0, 'achieved_eye_level_from_top_px': 0,
            'achieved_head_top_from_crop_top_px': 0,
            'positioning_method': "Error",
            'positioning_success': False, 'warnings': [f"Critical error: {e}"]
        }

    # Extract dimensions
    original_actual_head_top_y = dims['actual_head_top_y']
    original_chin_bottom_y = dims['chin_bottom_y']
    original_eye_level_y = dims['eye_level_y']
    original_face_center_x = dims['face_center_x']
    original_actual_head_height_px = dims['actual_head_height_px']

    target_photo_width_px = photo_spec.photo_width_px
    target_photo_height_px = photo_spec.photo_height_px

    # --- 1. SCALE FACTOR CALCULATION ---
    # Target middle of head size range for optimal results
    ideal_target_head_px = (photo_spec.head_min_px + photo_spec.head_max_px) / 2.0
    
    if original_actual_head_height_px <= 0:
        logging.error("Original head height is zero/negative.")
        return {
            'scale_factor': 1.0, 'crop_top': 0, 'crop_bottom': target_photo_height_px,
            'crop_left': 0, 'crop_right': target_photo_width_px,
            'final_photo_width_px': target_photo_width_px,
            'final_photo_height_px': target_photo_height_px,
            'achieved_head_height_px': 0, 'achieved_eye_level_from_top_px': 0,
            'achieved_head_top_from_crop_top_px': 0,
            'positioning_method': "Error", 'positioning_success': False,
            'warnings': ["Invalid head height detected."]
        }

    scale_factor = ideal_target_head_px / original_actual_head_height_px
    logging.info(f"📏 Initial scale for ideal head ({ideal_target_head_px:.1f}px): {scale_factor:.3f}")

    # Constrain to specification limits
    if original_actual_head_height_px * scale_factor < photo_spec.head_min_px:
        scale_factor = photo_spec.head_min_px / original_actual_head_height_px
        logging.info(f"   Adjusted to meet min_head_px: {scale_factor:.3f}")
    if original_actual_head_height_px * scale_factor > photo_spec.head_max_px:
        scale_factor = photo_spec.head_max_px / original_actual_head_height_px
        logging.info(f"   Adjusted to meet max_head_px: {scale_factor:.3f}")
    
    # Ensure scale factor is reasonable
    scale_factor = max(0.25, min(3.0, scale_factor))
    
    scaled_actual_head_height_px = original_actual_head_height_px * scale_factor
    logging.info(f"📏 Final scale: {scale_factor:.3f}, head height: {scaled_actual_head_height_px:.1f}px")
    logging.info(f"   Specification: {photo_spec.head_min_px}-{photo_spec.head_max_px}px")

    # Scale all coordinates
    scaled_img_width = img_width * scale_factor
    scaled_img_height = img_height * scale_factor
    scaled_actual_head_top_y = original_actual_head_top_y * scale_factor
    scaled_chin_bottom_y = original_chin_bottom_y * scale_factor
    scaled_eye_level_y = original_eye_level_y * scale_factor
    scaled_face_center_x = original_face_center_x * scale_factor
    
    # --- 2. VERTICAL POSITIONING ---
    crop_top = 0
    positioning_method = "DefaultMargin"
    
    # Priority 1: Head-top distance specification (Green Card style)
    if (hasattr(photo_spec, 'head_top_min_dist_from_photo_top_px') and 
        hasattr(photo_spec, 'head_top_max_dist_from_photo_top_px') and
        photo_spec.head_top_min_dist_from_photo_top_px is not None and 
        photo_spec.head_top_max_dist_from_photo_top_px is not None):
        
        target_dist_px = (photo_spec.head_top_min_dist_from_photo_top_px + 
                         photo_spec.head_top_max_dist_from_photo_top_px) / 2.0
        crop_top = scaled_actual_head_top_y - target_dist_px
        positioning_method = f"HeadTopDistance ({target_dist_px:.1f}px)"
        
    # Priority 2: Eye positioning
    elif (photo_spec.eye_min_from_bottom_px is not None and 
          photo_spec.eye_max_from_bottom_px is not None):
        
        target_eye_from_bottom_px = (photo_spec.eye_min_from_bottom_px + 
                                    photo_spec.eye_max_from_bottom_px) / 2.0
        target_eye_from_top_px = target_photo_height_px - target_eye_from_bottom_px
        crop_top = scaled_eye_level_y - target_eye_from_top_px
        positioning_method = f"EyeFromBottom ({target_eye_from_bottom_px:.1f}px)"
        
    # Priority 3: Default margin
    else:
        default_margin_percent = getattr(photo_spec, 'default_head_top_margin_percent', 0.12)
        default_margin_px = target_photo_height_px * default_margin_percent
        crop_top = scaled_actual_head_top_y - default_margin_px
        positioning_method = f"DefaultMargin ({default_margin_px:.1f}px)"
    
    logging.info(f"📍 Positioning by {positioning_method}, initial crop_top: {crop_top:.1f}")

    # --- 3. HORIZONTAL POSITIONING ---
    crop_left = scaled_face_center_x - (target_photo_width_px / 2.0)

    # --- 4. MARGIN CORRECTIONS ---
    min_head_margin_px = getattr(photo_spec, 'min_visual_head_margin_px', 5)
    min_chin_margin_px = getattr(photo_spec, 'min_visual_chin_margin_px', 5)
    
    # Ensure minimum head margin
    current_head_margin = scaled_actual_head_top_y - crop_top
    if current_head_margin < min_head_margin_px:
        adjustment = min_head_margin_px - current_head_margin
        crop_top -= adjustment
        logging.warning(f"   Adjusted crop_top by {-adjustment:.1f}px for head margin")
        positioning_method += " +HeadMarginFix"

    # Ensure minimum chin margin
    current_chin_margin = (crop_top + target_photo_height_px) - scaled_chin_bottom_y
    if current_chin_margin < min_chin_margin_px:
        adjustment = min_chin_margin_px - current_chin_margin
        crop_top += adjustment
        logging.warning(f"   Adjusted crop_top by {adjustment:.1f}px for chin margin")
        positioning_method += " +ChinMarginFix"

    # --- 5. BOUNDARY ADJUSTMENTS ---
    crop_bottom = crop_top + target_photo_height_px
    crop_right = crop_left + target_photo_width_px

    # Keep within scaled image bounds
    if crop_top < 0:
        crop_top = 0
    if crop_left < 0:
        crop_left = 0
    if crop_bottom > scaled_img_height:
        crop_top = max(0, scaled_img_height - target_photo_height_px)
    if crop_right > scaled_img_width:
        crop_left = max(0, scaled_img_width - target_photo_width_px)

    # Recalculate final boundaries
    crop_bottom = crop_top + target_photo_height_px
    crop_right = crop_left + target_photo_width_px

    # --- 6. FINAL CALCULATIONS AND VALIDATION ---
    final_head_top_from_crop_top_px = scaled_actual_head_top_y - crop_top
    final_chin_bottom_from_crop_top_px = scaled_chin_bottom_y - crop_top
    final_eye_level_from_crop_top_px = scaled_eye_level_y - crop_top
    final_eye_from_bottom_px = target_photo_height_px - final_eye_level_from_crop_top_px

    # Calculate visible head height in final crop
    visible_head_top = max(0, final_head_top_from_crop_top_px)
    visible_chin_bottom = min(target_photo_height_px, final_chin_bottom_from_crop_top_px)
    achieved_head_height_px = max(0, visible_chin_bottom - visible_head_top)

    logging.info(f"📍 Final positions: Head={final_head_top_from_crop_top_px:.1f}px, Eyes={final_eye_level_from_crop_top_px:.1f}px")
    logging.info(f"📏 Achieved head height: {achieved_head_height_px:.1f}px")

    # Validation
    warnings = []
    positioning_success = True

    # Check head size compliance
    if not (photo_spec.head_min_px <= achieved_head_height_px <= photo_spec.head_max_px):
        warnings.append(f"Head height {achieved_head_height_px:.1f}px outside spec ({photo_spec.head_min_px}-{photo_spec.head_max_px}px)")
        positioning_success = False

    # Check eye positioning if specified
    if (photo_spec.eye_min_from_bottom_px is not None and 
        photo_spec.eye_max_from_bottom_px is not None):
        if not (photo_spec.eye_min_from_bottom_px <= final_eye_from_bottom_px <= photo_spec.eye_max_from_bottom_px):
            warnings.append(f"Eyes {final_eye_from_bottom_px:.1f}px outside spec ({photo_spec.eye_min_from_bottom_px}-{photo_spec.eye_max_from_bottom_px}px)")

    # Check head-top distance if specified
    if (hasattr(photo_spec, 'head_top_min_dist_from_photo_top_px') and
        photo_spec.head_top_min_dist_from_photo_top_px is not None):
        if not (photo_spec.head_top_min_dist_from_photo_top_px <= final_head_top_from_crop_top_px <= photo_spec.head_top_max_dist_from_photo_top_px):
            warnings.append(f"Head-top distance {final_head_top_from_crop_top_px:.1f}px outside spec ({photo_spec.head_top_min_dist_from_photo_top_px}-{photo_spec.head_top_max_dist_from_photo_top_px}px)")

    if warnings:
        logging.warning("Compliance warnings:")
        for w in warnings:
            logging.warning(f"   {w}")

    if positioning_success:
        logging.info("✅ Mask-based positioning successful!")
    else:
        logging.error("❌ Mask-based positioning failed critical requirements.")

    return {
        'scale_factor': float(scale_factor),
        'crop_top': int(round(crop_top)),
        'crop_bottom': int(round(crop_bottom)),
        'crop_left': int(round(crop_left)),
        'crop_right': int(round(crop_right)),
        'final_photo_width_px': target_photo_width_px,
        'final_photo_height_px': target_photo_height_px,
        'achieved_head_height_px': int(round(achieved_head_height_px)),
        'achieved_eye_level_from_top_px': int(round(final_eye_level_from_crop_top_px)),
        'achieved_eye_level_from_bottom_px': int(round(final_eye_from_bottom_px)),
        'achieved_head_top_from_crop_top_px': int(round(final_head_top_from_crop_top_px)),
        'positioning_method': positioning_method,
        'positioning_success': positioning_success,
        'warnings': warnings
    }