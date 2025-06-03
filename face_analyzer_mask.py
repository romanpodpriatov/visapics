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
    
    # Расширенные лендмарки для левого глаза
    'left_eye_center': [468, 470],  # Центр радужки
    'left_eye_pupil': [468],        # Центр зрачка
    'left_eye_iris': [468, 469, 470, 471, 472],  # Контур радужки
    'left_eye_inner': [133],
    'left_eye_outer': [33],
    'left_eye_upper_lid': [157, 158, 159, 160, 161, 163, 144, 145, 153, 154, 155],  # Верхнее веко
    'left_eye_lower_lid': [173, 133, 155, 154, 153, 145, 144, 163, 7],              # Нижнее веко
    'left_eye_contour': [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246],  # Полный контур
    'left_eyebrow': [46, 53, 52, 51, 48, 115, 131, 134, 102, 49, 220, 285, 336],  # Бровь (исправлено)
    
    # Расширенные лендмарки для правого глаза
    'right_eye_center': [473, 475], # Центр радужки
    'right_eye_pupil': [473],       # Центр зрачка
    'right_eye_iris': [473, 474, 475, 476, 477],  # Контур радужки
    'right_eye_inner': [362],
    'right_eye_outer': [263],
    'right_eye_upper_lid': [384, 385, 386, 387, 388, 390, 373, 374, 380, 381, 382],  # Верхнее веко
    'right_eye_lower_lid': [398, 362, 382, 381, 380, 374, 373, 390, 249],              # Нижнее веко
    'right_eye_contour': [263, 249, 390, 373, 374, 380, 381, 382, 362, 398, 384, 385, 386, 387, 388, 466],  # Полный контур
    'right_eyebrow': [276, 283, 282, 281, 278, 344, 360, 363, 331, 279, 440],  # Бровь (исправлено)
    
    # Дополнительные детализированные области вокруг глаз (только валидные индексы)
    'left_eye_detailed': [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246, 
                         468, 469, 470, 471, 472, 130, 25, 110, 24, 23, 22, 26, 112, 243],
    'right_eye_detailed': [263, 249, 390, 373, 374, 380, 381, 382, 362, 398, 384, 385, 386, 387, 388, 466,
                          473, 474, 475, 476, 477, 359, 255, 339, 254, 253, 252, 256, 341, 463],
    
    # Расширенные лендмарки контуров головы
    
    # МАКУШКА И ЛОБ (детализированная верхняя граница)
    'forehead_top_detailed': [9, 10, 151],  # Центральная ось
    'forehead_left_boundary': [68, 104, 69, 108, 71, 139, 34, 127],  # Левая граница лба
    'forehead_right_boundary': [299, 333, 298, 337, 301, 368, 264, 356],  # Правая граница лба
    'forehead_temples': [21, 54, 103, 67, 109, 338, 297, 332, 284],  # Височные области
    'forehead_complete': [9, 10, 151, 68, 104, 69, 108, 71, 139, 34, 127, 299, 333, 298, 337, 301, 368, 264, 356, 21, 54, 103, 67, 109, 338, 297, 332, 284],  # Полный контур лба
    
    # ПОДБОРОДОК И ЧЕЛЮСТЬ (детализированная нижняя граница)
    'chin_bottom': [152],  # Основная точка подбородка (для совместимости)
    'chin_center_detailed': [152, 175, 199, 200, 171],  # Центральный подбородок
    'jaw_left': [172, 136, 150, 149, 176, 148],  # Левая челюсть
    'jaw_right': [377, 400, 378, 379, 365, 397],  # Правая челюсть
    'jaw_angles': [172, 132, 162, 397, 361, 323],  # Углы челюсти
    'jaw_complete': [152, 175, 199, 200, 171, 172, 136, 150, 149, 176, 148, 377, 400, 378, 379, 365, 397, 132, 162, 361, 323],  # Полная челюсть
    
    # БОКОВЫЕ КОНТУРЫ (скулы и височные области)
    'cheekbone_left': [123, 116, 117, 118, 119, 120, 121, 128, 126, 142],  # Левые скулы
    'cheekbone_right': [352, 345, 346, 347, 348, 349, 350, 451, 452, 453],  # Правые скулы
    'temple_left_detailed': [234, 127, 162, 21, 54, 103, 67, 109],  # Левый висок детализированный
    'temple_right_detailed': [454, 356, 389, 251, 284, 332, 297, 338],  # Правый висок детализированный
    
    # ПОЛНЫЙ КОНТУР ГОЛОВЫ (объединенный)
    'head_contour_complete': [
        # Верхняя часть (лоб)
        9, 10, 151, 68, 104, 69, 108, 71, 139, 34, 127, 299, 333, 298, 337, 301, 368, 264, 356,
        # Боковые части
        234, 127, 162, 21, 54, 103, 67, 109, 454, 356, 389, 251, 284, 332, 297, 338,
        # Скулы
        123, 116, 117, 118, 119, 120, 121, 128, 352, 345, 346, 347, 348, 349, 350, 451,
        # Нижняя часть (челюсть)
        152, 175, 199, 200, 171, 172, 136, 150, 149, 176, 148, 377, 400, 378, 379, 365, 397, 361, 323
    ],
    
    # Исходный face_contour для совместимости
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
        self.eye_detection_quality = self._analyze_eye_detection_quality()
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

        # Улучшенное определение центра глаз с приоритетом радужки/зрачка
        for eye_side in ['left', 'right']:
            center_key = f'{eye_side}_eye_center'
            pupil_key = f'{eye_side}_eye_pupil'
            iris_key = f'{eye_side}_eye_iris'
            inner_key = f'{eye_side}_eye_inner'
            outer_key = f'{eye_side}_eye_outer'
            
            if center_key not in normalized:
                # Приоритет 1: Зрачок (самая точная точка)
                if pupil_key in normalized and normalized[pupil_key]:
                    normalized[center_key] = normalized[pupil_key]
                    logging.info(f"Enhanced: Used pupil for '{center_key}'.")
                # Приоритет 2: Центр радужки
                elif iris_key in normalized and normalized[iris_key] and len(normalized[iris_key]) >= 2:
                    iris_points = normalized[iris_key]
                    center_x = np.mean([pt[0] for pt in iris_points])
                    center_y = np.mean([pt[1] for pt in iris_points])
                    normalized[center_key] = [(center_x, center_y)]
                    logging.info(f"Enhanced: Used iris center for '{center_key}'.")
                # Приоритет 3: Исходный fallback через inner/outer
                elif inner_key in normalized and outer_key in normalized and \
                     normalized[inner_key] and normalized[outer_key]:
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
    
    def _analyze_eye_detection_quality(self):
        """Анализ качества детекции глаз для выбора оптимальных лендмарков"""
        quality = {
            'left_eye_quality': 0,
            'right_eye_quality': 0,
            'overall_confidence': 0,
            'available_landmarks': []
        }
        
        # Проверка наличия различных типов лендмарков глаз
        eye_landmarks_priority = [
            ('detailed', ['left_eye_detailed', 'right_eye_detailed']),
            ('iris', ['left_eye_iris', 'right_eye_iris']),
            ('pupil', ['left_eye_pupil', 'right_eye_pupil']),
            ('contour', ['left_eye_contour', 'right_eye_contour']),
            ('center', ['left_eye_center', 'right_eye_center'])
        ]
        
        for landmark_type, (left_key, right_key) in eye_landmarks_priority:
            left_available = left_key in self.normalized_points and self.normalized_points[left_key]
            right_available = right_key in self.normalized_points and self.normalized_points[right_key]
            
            if left_available:
                quality['left_eye_quality'] += 1
                quality['available_landmarks'].append(left_key)
            if right_available:
                quality['right_eye_quality'] += 1
                quality['available_landmarks'].append(right_key)
        
        # Дополнительные баллы за наличие бровей и век
        additional_features = [
            'left_eyebrow', 'right_eyebrow',
            'left_eye_upper_lid', 'right_eye_upper_lid',
            'left_eye_lower_lid', 'right_eye_lower_lid'
        ]
        
        for feature in additional_features:
            if feature in self.normalized_points and self.normalized_points[feature]:
                quality['overall_confidence'] += 0.5
                quality['available_landmarks'].append(feature)
        
        # Общая уверенность в детекции
        total_possible = len(eye_landmarks_priority) * 2 + len(additional_features) * 0.5
        total_actual = quality['left_eye_quality'] + quality['right_eye_quality'] + quality['overall_confidence']
        quality['overall_confidence'] = min(1.0, total_actual / total_possible)
        
        logging.info(f"👁️ Качество детекции глаз: L={quality['left_eye_quality']}/5, R={quality['right_eye_quality']}/5, "
                    f"Общее={quality['overall_confidence']:.2f}, Доступно лендмарков: {len(quality['available_landmarks'])}")
        
        return quality
        
    def _determine_actual_head_top(self):
        # Усовершенствованное определение верхней границы головы с использованием детализированных лендмарков
        
        # Приоритет 1: Детализированный контур лба
        if 'forehead_complete' in self.normalized_points and self.normalized_points['forehead_complete']:
            forehead_y_coords = [pt[1] for pt in self.normalized_points['forehead_complete']]
            landmark_forehead_top_y = min(forehead_y_coords)
            logging.info(f"🔝 Используется детализированный контур лба ({len(forehead_y_coords)} точек)")
        elif 'forehead_top_detailed' in self.normalized_points and self.normalized_points['forehead_top_detailed']:
            forehead_y_coords = [pt[1] for pt in self.normalized_points['forehead_top_detailed']]
            landmark_forehead_top_y = min(forehead_y_coords)
            logging.info(f"🔝 Используется детализированная макушка ({len(forehead_y_coords)} точек)")
        else:
            # Fallback к базовой точке
            landmark_forehead_top_y = min(pt[1] for pt in self.normalized_points['forehead_top'])
            logging.info("🔝 Используется базовая точка лба")
            
        self.refined_actual_head_top_y = landmark_forehead_top_y 

        if self.segmentation_mask is not None and isinstance(self.segmentation_mask, np.ndarray):
            logging.info("🎯 Refining head top using BiRefNet segmentation mask with enhanced landmarks.")
            mask_h, mask_w = self.segmentation_mask.shape[:2]
            if mask_h != self.img_height or mask_w != self.img_width:
                logging.warning(f"Mask dimensions ({mask_w}x{mask_h}) differ from image ({self.img_width}x{self.img_height}).")

            # Улучшенное определение области поиска с использованием детализированных контуров
            face_x_coords = []
            search_regions = [
                'temple_left_detailed', 'temple_right_detailed', 
                'forehead_left_boundary', 'forehead_right_boundary',
                'head_contour_complete', 'face_contour'
            ]
            
            for region_key in search_regions:
                if region_key in self.normalized_points and self.normalized_points[region_key]:
                    face_x_coords.extend([pt[0] for pt in self.normalized_points[region_key]])
                    break  # Используем первый доступный регион по приоритету
            
            if not face_x_coords:
                search_x_start, search_x_end = 0, self.img_width
                logging.info("   Используется полная ширина изображения для поиска")
            else:
                min_face_x, max_face_x = min(face_x_coords), max(face_x_coords)
                face_width = max_face_x - min_face_x
                padding_x = face_width * 0.30  # Увеличено для лучшего покрытия волос
                search_x_start = max(0, int(min_face_x - padding_x))
                search_x_end = min(self.img_width, int(max_face_x + padding_x))
                logging.info(f"   Область поиска: X[{search_x_start}:{search_x_end}] (ширина лица: {face_width:.1f}px)")
            
            if search_x_start >= search_x_end:
                search_x_start, search_x_end = 0, self.img_width

            scan_y_upper_limit = 0 
            scan_y_lower_limit = int(landmark_forehead_top_y + (self.img_height * 0.12))  # Увеличена область сканирования
            scan_y_lower_limit = min(scan_y_lower_limit, self.img_height)

            roi_mask = self.segmentation_mask[scan_y_upper_limit:scan_y_lower_limit, search_x_start:search_x_end]
            foreground_pixels_y_in_roi, _ = np.where(roi_mask > 128)

            if foreground_pixels_y_in_roi.size > 0:
                mask_refined_head_top_y = float(np.min(foreground_pixels_y_in_roi) + scan_y_upper_limit)
                logging.info(f"   Mask-refined head top: {mask_refined_head_top_y:.1f}px; Landmark head top: {landmark_forehead_top_y:.1f}px")
                self.refined_actual_head_top_y = min(landmark_forehead_top_y, mask_refined_head_top_y)
                if landmark_forehead_top_y - mask_refined_head_top_y > 5:
                    logging.info(f"   📏 Hair detected: {(landmark_forehead_top_y - mask_refined_head_top_y):.1f}px above landmark forehead")
            else:
                logging.warning("No foreground pixels found in mask ROI. Using enhanced landmark-based head top.")
        else:
            logging.info("🎯 No segmentation mask. Using enhanced landmark-based head top.")
        logging.info(f"✅ Final head top Y: {self.refined_actual_head_top_y:.1f}px")

    def analyze_face_dimensions(self):
        if self.refined_actual_head_top_y is None:
            raise RuntimeError("refined_actual_head_top_y was not set.")
            
        actual_head_top_y = self.refined_actual_head_top_y
        
        # Усовершенствованное определение нижней границы подбородка
        if 'jaw_complete' in self.normalized_points and self.normalized_points['jaw_complete']:
            chin_y_coords = [pt[1] for pt in self.normalized_points['jaw_complete']]
            chin_bottom_y = max(chin_y_coords)
            logging.info(f"📍 Используется полная челюсть ({len(chin_y_coords)} точек) для определения подбородка")
        elif 'chin_center_detailed' in self.normalized_points and self.normalized_points['chin_center_detailed']:
            chin_y_coords = [pt[1] for pt in self.normalized_points['chin_center_detailed']]
            chin_bottom_y = max(chin_y_coords)
            logging.info(f"📍 Используется детализированный центр подбородка ({len(chin_y_coords)} точек)")
        else:
            # Fallback к базовой точке
            chin_bottom_y = max(pt[1] for pt in self.normalized_points['chin_bottom'])
            logging.info("📍 Используется базовая точка подбородка")

        # Улучшенное определение позиции глаз с использованием дополнительных лендмарков
        left_eye_y = None
        right_eye_y = None
        
        # Попытка 1: Использование детализированных лендмарков для более точного расчета
        if 'left_eye_detailed' in self.normalized_points and self.normalized_points['left_eye_detailed']:
            left_eye_contour_y = [pt[1] for pt in self.normalized_points['left_eye_detailed']]
            left_eye_y = np.mean(left_eye_contour_y)
            logging.info(f"   Левый глаз: используются детализированные лендмарки ({len(left_eye_contour_y)} точек)")
        elif 'left_eye_contour' in self.normalized_points and self.normalized_points['left_eye_contour']:
            left_eye_contour_y = [pt[1] for pt in self.normalized_points['left_eye_contour']]
            left_eye_y = np.mean(left_eye_contour_y)
            logging.info(f"   Левый глаз: используется контур ({len(left_eye_contour_y)} точек)")
        elif 'left_eye_center' in self.normalized_points and self.normalized_points['left_eye_center']:
            left_eye_y = np.mean([pt[1] for pt in self.normalized_points['left_eye_center']])
            logging.info("   Левый глаз: используется базовый центр")
        
        if 'right_eye_detailed' in self.normalized_points and self.normalized_points['right_eye_detailed']:
            right_eye_contour_y = [pt[1] for pt in self.normalized_points['right_eye_detailed']]
            right_eye_y = np.mean(right_eye_contour_y)
            logging.info(f"   Правый глаз: используются детализированные лендмарки ({len(right_eye_contour_y)} точек)")
        elif 'right_eye_contour' in self.normalized_points and self.normalized_points['right_eye_contour']:
            right_eye_contour_y = [pt[1] for pt in self.normalized_points['right_eye_contour']]
            right_eye_y = np.mean(right_eye_contour_y)
            logging.info(f"   Правый глаз: используется контур ({len(right_eye_contour_y)} точек)")
        elif 'right_eye_center' in self.normalized_points and self.normalized_points['right_eye_center']:
            right_eye_y = np.mean([pt[1] for pt in self.normalized_points['right_eye_center']])
            logging.info("   Правый глаз: используется базовый центр")
        
        if left_eye_y is not None and right_eye_y is not None:
            eye_level_y = (left_eye_y + right_eye_y) / 2
            logging.info(f"📍 Позиция глаз: Левый={left_eye_y:.1f}px, Правый={right_eye_y:.1f}px, Средний={eye_level_y:.1f}px")
        else:
            logging.warning("Eye landmarks missing. Estimating eye_level_y as 40% down from head top to chin.")
            eye_level_y = actual_head_top_y + (chin_bottom_y - actual_head_top_y) * 0.40 
            
        # Значительно улучшенное определение ширины лица с использованием детализированных лендмарков
        face_width_regions = [
            'head_contour_complete',  # Приоритет 1: Полный контур головы
            'face_contour',           # Приоритет 2: Базовый контур лица
        ]
        
        face_contour_x_coords = []
        used_region = None
        
        for region in face_width_regions:
            if region in self.normalized_points and self.normalized_points[region]:
                face_contour_x_coords = [pt[0] for pt in self.normalized_points[region]]
                used_region = region
                break
        
        if face_contour_x_coords:
            face_min_x, face_max_x = min(face_contour_x_coords), max(face_contour_x_coords)
            face_center_x = (face_min_x + face_max_x) / 2
            face_width_px = face_max_x - face_min_x
            logging.info(f"📏 Ширина лица определена по {used_region} ({len(face_contour_x_coords)} точек)")
            
            # Дополнительные корректировки с использованием скул и височных областей
            if ('cheekbone_left' in self.normalized_points and self.normalized_points['cheekbone_left'] and
                'cheekbone_right' in self.normalized_points and self.normalized_points['cheekbone_right']):
                
                left_cheek_x_coords = [pt[0] for pt in self.normalized_points['cheekbone_left']]
                right_cheek_x_coords = [pt[0] for pt in self.normalized_points['cheekbone_right']]
                cheek_min_x = min(left_cheek_x_coords)
                cheek_max_x = max(right_cheek_x_coords)
                cheek_based_center_x = (cheek_min_x + cheek_max_x) / 2
                cheek_width = cheek_max_x - cheek_min_x
                
                # Корректировка с учетом скул
                face_center_x = (face_center_x + cheek_based_center_x) / 2
                face_width_px = max(face_width_px, cheek_width)  # Используем максимальную ширину
                logging.info(f"📏 Корректировка на основе скул: ширина {cheek_width:.1f}px")
            
            # Дополнительная валидация с использованием глазных областей
            if ('left_eye_detailed' in self.normalized_points and self.normalized_points['left_eye_detailed'] and 
                'right_eye_detailed' in self.normalized_points and self.normalized_points['right_eye_detailed']):
                left_eye_x_coords = [pt[0] for pt in self.normalized_points['left_eye_detailed']]
                right_eye_x_coords = [pt[0] for pt in self.normalized_points['right_eye_detailed']]
                eye_span_min_x = min(left_eye_x_coords + right_eye_x_coords)
                eye_span_max_x = max(left_eye_x_coords + right_eye_x_coords)
                eye_based_center_x = (eye_span_min_x + eye_span_max_x) / 2
                
                # Финальная корректировка центра лица на основе позиции глаз
                face_center_x = (face_center_x * 0.7 + eye_based_center_x * 0.3)  # Взвешенное среднее
                logging.info(f"📏 Финальная корректировка центра лица на основе детализированных глазных лендмарков")
                
        else:
            logging.warning("Enhanced face contours not available. Using image center and estimated width.")
            face_center_x = self.img_width / 2
            face_width_px = self.img_width * 0.5

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
    
    # --- 2. VERTICAL POSITIONING WITH COMPLIANCE ADJUSTMENT ---
    crop_top = 0
    positioning_method = "NotSet"
    compliance_adjustment_applied = False
    compliance_adjustment = 0.0

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

    # --- COMPLIANCE OPTIMIZATION ALGORITHM ---
    def apply_compliance_adjustment(current_crop_top, eye_pos_y, head_top_y, chin_bottom_y, photo_spec, target_height, target_width):
        """
        Оптимальный алгоритм коррекции комплаенса с коэффициентом
        Приоритет: позиция глаз > размер головы > отступы головы
        """
        adjusted_crop_top = current_crop_top
        adjustment_reasons = []
        
        # Предварительный расчет позиций
        temp_eye_from_bottom = target_height - (eye_pos_y - current_crop_top)
        temp_head_top_margin = head_top_y - current_crop_top
        temp_chin_bottom_margin = (current_crop_top + target_height) - chin_bottom_y
        
        # Приоритет 1: Коррекция позиции глаз (критичная)
        if photo_spec.eye_min_from_bottom_px is not None and photo_spec.eye_max_from_bottom_px is not None:
            eye_target_center = (photo_spec.eye_min_from_bottom_px + photo_spec.eye_max_from_bottom_px) / 2.0
            eye_deviation = temp_eye_from_bottom - eye_target_center
            
            # Адаптивный коэффициент коррекции для глаз
            # Для российских документов с жесткими требованиями используем 100% коррекцию
            if photo_spec.country_code == 'RU':
                EYE_CORRECTION_COEFFICIENT = 1.0  # 100% для всех российских документов
            else:
                EYE_CORRECTION_COEFFICIENT = 0.95  # 95% для остальных документов
            
            if temp_eye_from_bottom < photo_spec.eye_min_from_bottom_px:
                # Глаза слишком близко к низу - нужно сдвинуть crop_top вниз
                # Адаптивная буферная зона: меньше для российских документов с точными требованиями
                if photo_spec.country_code == 'RU':
                    SAFETY_BUFFER_PX = 2  # Минимальный буфер для всех российских документов
                else:
                    SAFETY_BUFFER_PX = 10  # Стандартный буфер
                target_eye_position = photo_spec.eye_min_from_bottom_px + SAFETY_BUFFER_PX
                needed_adjustment = target_eye_position - temp_eye_from_bottom
                eye_adjustment = needed_adjustment * EYE_CORRECTION_COEFFICIENT
                adjusted_crop_top += eye_adjustment
                adjustment_reasons.append(f"EyeTooLow: +{eye_adjustment:.1f}px (target min+buffer: {target_eye_position:.1f}px)")
                
            elif temp_eye_from_bottom > photo_spec.eye_max_from_bottom_px:
                # Глаза слишком далеко от низа - нужно сдвинуть crop_top вверх
                needed_adjustment = temp_eye_from_bottom - photo_spec.eye_max_from_bottom_px
                eye_adjustment = needed_adjustment * EYE_CORRECTION_COEFFICIENT
                adjusted_crop_top -= eye_adjustment
                adjustment_reasons.append(f"EyeTooHigh: -{eye_adjustment:.1f}px (target max: {photo_spec.eye_max_from_bottom_px:.1f}px)")
        
        # Приоритет 2: Коррекция отступов головы (если есть спецификация)
        if hasattr(photo_spec, 'head_top_min_dist_from_photo_top_px') and photo_spec.head_top_min_dist_from_photo_top_px is not None:
            # Пересчет после коррекции глаз
            temp_head_top_margin = head_top_y - adjusted_crop_top
            
            # Адаптивный коэффициент коррекции для отступов головы
            # Для российских документов с точными требованиями используем 95% коррекцию
            if photo_spec.country_code == 'RU':
                HEAD_MARGIN_CORRECTION_COEFFICIENT = 0.95  # 95% для всех российских документов
            else:
                HEAD_MARGIN_CORRECTION_COEFFICIENT = 0.7  # 70% для остальных документов
            
            if temp_head_top_margin < photo_spec.head_top_min_dist_from_photo_top_px:
                # Голова слишком близко к верху
                needed_adjustment = photo_spec.head_top_min_dist_from_photo_top_px - temp_head_top_margin
                head_adjustment = needed_adjustment * HEAD_MARGIN_CORRECTION_COEFFICIENT
                adjusted_crop_top -= head_adjustment
                adjustment_reasons.append(f"HeadTooClose: -{head_adjustment:.1f}px (target min: {photo_spec.head_top_min_dist_from_photo_top_px:.1f}px)")
                
            elif hasattr(photo_spec, 'head_top_max_dist_from_photo_top_px') and photo_spec.head_top_max_dist_from_photo_top_px is not None:
                if temp_head_top_margin > photo_spec.head_top_max_dist_from_photo_top_px:
                    # Голова слишком далеко от верха
                    needed_adjustment = temp_head_top_margin - photo_spec.head_top_max_dist_from_photo_top_px
                    head_adjustment = needed_adjustment * HEAD_MARGIN_CORRECTION_COEFFICIENT
                    adjusted_crop_top += head_adjustment
                    adjustment_reasons.append(f"HeadTooFar: +{head_adjustment:.1f}px (target max: {photo_spec.head_top_max_dist_from_photo_top_px:.1f}px)")
        
        # Приоритет 3: Защитные коррекции (предотвращение обрезания)
        SAFETY_MARGIN = 5  # Минимальный защитный отступ в пикселях
        
        # Проверка, что голова не обрезается сверху
        final_head_top_margin = head_top_y - adjusted_crop_top
        if final_head_top_margin < SAFETY_MARGIN:
            safety_adjustment = SAFETY_MARGIN - final_head_top_margin
            adjusted_crop_top -= safety_adjustment
            adjustment_reasons.append(f"SafetyTop: -{safety_adjustment:.1f}px")
        
        # Проверка, что подбородок не обрезается снизу
        final_chin_margin = (adjusted_crop_top + target_height) - chin_bottom_y
        if final_chin_margin < SAFETY_MARGIN:
            safety_adjustment = SAFETY_MARGIN - final_chin_margin
            adjusted_crop_top += safety_adjustment
            adjustment_reasons.append(f"SafetyBottom: +{safety_adjustment:.1f}px")
        
        total_adjustment = adjusted_crop_top - current_crop_top
        return adjusted_crop_top, total_adjustment, adjustment_reasons
    
    # Применяем алгоритм коррекции комплаенса
    adjusted_crop_top, compliance_adjustment, adjustment_reasons = apply_compliance_adjustment(
        crop_top, scaled_eye_level_y, scaled_actual_head_top_y, scaled_chin_bottom_y, 
        photo_spec, target_photo_height_px, target_photo_width_px
    )
    
    if abs(compliance_adjustment) > 1.0:  # Применяем коррекцию только если она значительная
        crop_top = adjusted_crop_top
        compliance_adjustment_applied = True
        positioning_method += f" +ComplianceAdj({compliance_adjustment:+.1f}px)"
        logging.info(f"🎯 COMPLIANCE ADJUSTMENT applied: {compliance_adjustment:+.1f}px")
        for reason in adjustment_reasons:
            logging.info(f"   📝 {reason}")
    else:
        logging.info(f"🎯 No significant compliance adjustment needed ({compliance_adjustment:+.1f}px)")

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

    # Head size compliance (based on visible head height) with tolerance
    head_tolerance = 5.0  # 5px tolerance for floating point precision and positioning variations
    head_min_allowed = photo_spec.head_min_px - head_tolerance
    head_max_allowed = photo_spec.head_max_px + head_tolerance
    
    if not (head_min_allowed <= achieved_head_height_px <= head_max_allowed):
        warnings.append(f"Head height {achieved_head_height_px:.1f}px (visible) outside spec ({photo_spec.head_min_px}-{photo_spec.head_max_px}px). Scaled head was {scaled_actual_head_height_px:.1f}px.")
        positioning_success = False # This is a critical failure

    # Eye positioning compliance with tolerance
    eye_pos_compliant = True
    eye_tolerance = 20.0  # 20px tolerance for eye positioning variations
    
    if photo_spec.eye_min_from_bottom_px is not None and photo_spec.eye_max_from_bottom_px is not None:
        eye_min_allowed = photo_spec.eye_min_from_bottom_px - eye_tolerance
        eye_max_allowed = photo_spec.eye_max_from_bottom_px + eye_tolerance
        
        if not (eye_min_allowed <= final_eye_from_bottom_px <= eye_max_allowed):
            warnings.append(f"Eyes from bottom {final_eye_from_bottom_px:.1f}px outside spec ({photo_spec.eye_min_from_bottom_px}-{photo_spec.eye_max_from_bottom_px}px).")
            eye_pos_compliant = False
    elif photo_spec.eye_min_from_top_px is not None and photo_spec.eye_max_from_top_px is not None: # Check from top if bottom not specified
        eye_min_allowed_top = photo_spec.eye_min_from_top_px - eye_tolerance
        eye_max_allowed_top = photo_spec.eye_max_from_top_px + eye_tolerance
        
        if not (eye_min_allowed_top <= final_eye_level_from_crop_top_px <= eye_max_allowed_top):
            warnings.append(f"Eyes from top {final_eye_level_from_crop_top_px:.1f}px outside spec ({photo_spec.eye_min_from_top_px}-{photo_spec.eye_max_from_top_px}px).")
            eye_pos_compliant = False
            
    if not eye_pos_compliant and (photo_spec.eye_min_from_bottom_px or photo_spec.eye_min_from_top_px): # If eye spec exists and not compliant
        positioning_success = False # Eye position is also critical

    # Head-top distance compliance with tolerance for rounding errors
    # Check both head_top_min_dist_from_photo_top_px and distance_top_of_head_to_top_of_photo_min_px
    head_top_distance_checked = False
    
    if hasattr(photo_spec, 'head_top_min_dist_from_photo_top_px') and photo_spec.head_top_min_dist_from_photo_top_px is not None:
        # Add 30px tolerance to account for rounding errors and positioning variations
        tolerance_px = 30.0
        min_allowed = photo_spec.head_top_min_dist_from_photo_top_px - tolerance_px
        max_allowed = photo_spec.head_top_max_dist_from_photo_top_px + tolerance_px
        
        if not (min_allowed <= final_head_top_from_crop_top_px <= max_allowed):
            warnings.append(f"Head-top distance {final_head_top_from_crop_top_px:.1f}px outside spec ({photo_spec.head_top_min_dist_from_photo_top_px}-{photo_spec.head_top_max_dist_from_photo_top_px}px).")
            positioning_success = False
        head_top_distance_checked = True
    
    # Also check distance_top_of_head_to_top_of_photo fields if not already checked
    if not head_top_distance_checked and photo_spec.distance_top_of_head_to_top_of_photo_min_px is not None:
        tolerance_px = 30.0
        min_allowed = photo_spec.distance_top_of_head_to_top_of_photo_min_px - tolerance_px
        max_allowed = photo_spec.distance_top_of_head_to_top_of_photo_max_px + tolerance_px
        
        if not (min_allowed <= final_head_top_from_crop_top_px <= max_allowed):
            warnings.append(f"Head-top distance {final_head_top_from_crop_top_px:.1f}px outside spec ({photo_spec.distance_top_of_head_to_top_of_photo_min_px}-{photo_spec.distance_top_of_head_to_top_of_photo_max_px}px).")
            positioning_success = False


    if warnings:
        logging.warning("Compliance warnings:")
        for w in warnings: logging.warning(f"   {w}")

    if positioning_success:
        if compliance_adjustment_applied:
            logging.info("✅ Mask-based positioning successful with compliance optimization!")
        else:
            logging.info("✅ Mask-based positioning successful!")
    else:
        if compliance_adjustment_applied:
            logging.warning("⚠️ Mask-based positioning with compliance adjustment still has issues.")
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
        'warnings': warnings,
        'compliance_adjustment_applied': compliance_adjustment_applied,
        'compliance_adjustment_px': float(compliance_adjustment)
    }