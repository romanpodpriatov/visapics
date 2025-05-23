# face_analyzer.py

import math
import logging
from utils import PIXELS_PER_INCH # PHOTO_SIZE_PIXELS will be replaced by photo_spec
from photo_specs import PhotoSpecification # Import for type hinting

# РАСШИРЕННЫЙ НАБОР АНАТОМИЧЕСКИХ ТОЧЕК для детального анализа лица
FACE_MESH_POINTS = {
    # === КОНТУР ЛИЦА И ГОЛОВЫ ===
    'forehead_top': [10, 151, 9, 10],  # Самая верхняя точка лба
    'forehead_center': [9, 10, 151],    # Центр лба
    'forehead_left': [68, 104, 69],     # Левая сторона лба  
    'forehead_right': [297, 333, 298],  # Правая сторона лба
    
    # === ВИСОЧНЫЕ ОБЛАСТИ (для понимания ширины головы) ===
    'temple_left': [21, 54, 103, 67],   # Левый висок
    'temple_right': [251, 284, 332, 297], # Правый висок
    
    # === БРОВИ ===
    'eyebrow_left_inner': [70, 63, 105], # Внутренняя часть левой брови
    'eyebrow_left_outer': [46, 53, 52],  # Внешняя часть левой брови
    'eyebrow_right_inner': [296, 334, 293], # Внутренняя часть правой брови
    'eyebrow_right_outer': [276, 283, 282], # Внешняя часть правой брови
    
    # === ГЛАЗА (детальный анализ) ===
    'left_eye_inner': [133, 173, 157],   # Внутренний угол левого глаза
    'left_eye_outer': [33, 7, 163],      # Внешний угол левого глаза
    'left_eye_top': [159, 158, 157],     # Верхнее веко левого глаза
    'left_eye_bottom': [144, 145, 153],  # Нижнее веко левого глаза
    'left_eye_center': [468, 469, 470, 471, 472], # Центр левого глаза (зрачок)
    
    'right_eye_inner': [362, 398, 384],  # Внутренний угол правого глаза
    'right_eye_outer': [263, 249, 390],  # Внешний угол правого глаза
    'right_eye_top': [386, 385, 384],    # Верхнее веко правого глаза
    'right_eye_bottom': [374, 373, 380], # Нижнее веко правого глаза
    'right_eye_center': [473, 474, 475, 476, 477], # Центр правого глаза (зрачок)
    
    # === НОС ===
    'nose_tip': [1, 2],                  # Кончик носа
    'nose_bridge_top': [6, 9, 10],       # Верх переносицы
    'nose_bridge_middle': [8, 9],        # Середина переносицы
    'nose_left': [31, 35, 36],           # Левая ноздря
    'nose_right': [261, 265, 266],       # Правая ноздря
    'nose_bottom': [2, 97, 99],          # Основание носа
    
    # === ЩЕКИ ===
    'cheek_left_high': [116, 117, 118],  # Верхняя часть левой щеки
    'cheek_left_mid': [123, 147, 213],   # Средняя часть левой щеки
    'cheek_right_high': [345, 346, 347], # Верхняя часть правой щеки
    'cheek_right_mid': [352, 376, 433],  # Средняя часть правой щеки
    
    # === ГУБЫ ===
    'lips_top': [12, 15, 16],            # Верхняя губа
    'lips_bottom': [17, 18, 200],        # Нижняя губа
    'lips_left': [61, 84, 17],           # Левый угол рта
    'lips_right': [291, 303, 267],       # Правый угол рта
    'lips_center': [13, 14, 269],        # Центр губ
    
    # === ПОДБОРОДОК И ЧЕЛЮСТЬ ===
    'chin_tip': [175, 199, 200],         # Кончик подбородка
    'chin_bottom': [175, 18, 175],       # Нижняя точка подбородка
    'jaw_left': [172, 136, 150],         # Левая сторона челюсти
    'jaw_right': [397, 365, 379],        # Правая сторона челюсти
    'jawline_left': [172, 136, 150, 149, 176], # Левая линия челюсти
    'jawline_right': [397, 365, 379, 378, 400], # Правая линия челюсти
    
    # === ШЕЯ (приблизительные точки - MediaPipe не всегда видит шею) ===
    'neck_left': [172, 136, 150],        # Левая сторона шеи (примерно)
    'neck_right': [397, 365, 379],       # Правая сторона шеи (примерно)
    'neck_center': [175, 199, 18],       # Центр шеи под подбородком
    
    # === КОНТУР ЛИЦА (полный периметр) ===
    'face_contour': [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 
                     397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 
                     172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109],
    
    # === ДОПОЛНИТЕЛЬНЫЕ РЕФЕРЕНСНЫЕ ТОЧКИ ===
    'face_center': [1, 2, 5, 6],         # Центр лица
    'face_width_left': [234, 93, 132],   # Левая граница лица
    'face_width_right': [454, 323, 361], # Правая граница лица
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
    
    def analyze_comprehensive_face_anatomy(self):
        """СУПЕР ДЕТАЛЬНЫЙ АНАЛИЗ ЛИЦЕВОЙ АНАТОМИИ - использует все точки для максимальной точности"""
        
        def get_region_center(region_name):
            """Получить центр региона лица"""
            if region_name not in self.normalized_points:
                return None
            points = self.normalized_points[region_name]
            center_x = sum([pt[0] for pt in points]) / len(points)
            center_y = sum([pt[1] for pt in points]) / len(points)
            return [center_x, center_y]
        
        def get_region_bounds(region_name, axis='y'):
            """Получить границы региона (min/max по оси)"""
            if region_name not in self.normalized_points:
                return None, None
            points = self.normalized_points[region_name]
            if axis == 'y':
                values = [pt[1] for pt in points]
            else:  # axis == 'x'
                values = [pt[0] for pt in points]
            return min(values), max(values)
        
        # === ОСНОВНЫЕ АНАТОМИЧЕСКИЕ ИЗМЕРЕНИЯ ===
        
        # Лоб и голова
        forehead_top_y = get_region_bounds('forehead_top', 'y')[0]
        forehead_center = get_region_center('forehead_center')
        forehead_width = abs(get_region_center('forehead_left')[0] - get_region_center('forehead_right')[0])
        
        # Глаза - детальный анализ
        left_eye_center = get_region_center('left_eye_center')
        right_eye_center = get_region_center('right_eye_center')
        if not left_eye_center:
            left_eye_center = get_region_center('left_eye_inner')
        if not right_eye_center:
            right_eye_center = get_region_center('right_eye_inner')
        
        eye_level = (left_eye_center[1] + right_eye_center[1]) / 2
        eye_distance = abs(right_eye_center[0] - left_eye_center[0])
        
        # Детальные измерения глаз
        left_eye_top_y = get_region_bounds('left_eye_top', 'y')[0]
        left_eye_bottom_y = get_region_bounds('left_eye_bottom', 'y')[1]
        eye_height = left_eye_bottom_y - left_eye_top_y
        
        # Брови
        left_eyebrow_center = get_region_center('eyebrow_left_inner')
        right_eyebrow_center = get_region_center('eyebrow_right_inner')
        eyebrow_level = (left_eyebrow_center[1] + right_eyebrow_center[1]) / 2
        
        # Нос
        nose_tip = get_region_center('nose_tip')
        nose_bridge_top = get_region_center('nose_bridge_top')
        nose_bottom = get_region_center('nose_bottom')
        nose_width = abs(get_region_center('nose_left')[0] - get_region_center('nose_right')[0])
        nose_length = nose_bottom[1] - nose_bridge_top[1]
        
        # Губы и рот
        lips_center = get_region_center('lips_center')
        lips_top_y = get_region_bounds('lips_top', 'y')[0]
        lips_bottom_y = get_region_bounds('lips_bottom', 'y')[1]
        mouth_width = abs(get_region_center('lips_left')[0] - get_region_center('lips_right')[0])
        
        # Подбородок и челюсть
        chin_tip = get_region_center('chin_tip')
        chin_bottom_y = get_region_bounds('chin_bottom', 'y')[1]
        jaw_left = get_region_center('jaw_left')
        jaw_right = get_region_center('jaw_right')
        jaw_width = abs(jaw_right[0] - jaw_left[0])
        
        # Щеки
        cheek_left_center = get_region_center('cheek_left_mid')
        cheek_right_center = get_region_center('cheek_right_mid')
        
        # Височные области (ширина головы)
        temple_left = get_region_center('temple_left')
        temple_right = get_region_center('temple_right')
        head_width_at_temples = abs(temple_right[0] - temple_left[0])
        
        # Общие размеры лица
        face_contour_left_x, face_contour_right_x = get_region_bounds('face_contour', 'x')
        face_contour_top_y, face_contour_bottom_y = get_region_bounds('face_contour', 'y')
        total_face_width = abs(face_contour_right_x - face_contour_left_x)
        total_face_height = abs(face_contour_bottom_y - face_contour_top_y)
        
        # === РАСЧЕТ ПРОПОРЦИЙ И СООТНОШЕНИЙ ===
        
        # Высотные пропорции лица
        forehead_height = eye_level - forehead_top_y
        eyes_to_nose_base = nose_bottom[1] - eye_level
        nose_to_lips = lips_center[1] - nose_bottom[1]
        lips_to_chin = chin_bottom_y - lips_bottom_y
        
        total_measured_height = chin_bottom_y - forehead_top_y
        
        # Пропорциональные соотношения
        forehead_ratio = forehead_height / total_measured_height if total_measured_height > 0 else 0
        mid_face_ratio = eyes_to_nose_base / total_measured_height if total_measured_height > 0 else 0
        lower_face_ratio = lips_to_chin / total_measured_height if total_measured_height > 0 else 0
        
        # Ширинные пропорции
        eye_to_face_width_ratio = eye_distance / total_face_width if total_face_width > 0 else 0
        nose_to_face_width_ratio = nose_width / total_face_width if total_face_width > 0 else 0
        mouth_to_face_width_ratio = mouth_width / total_face_width if total_face_width > 0 else 0
        
        # === АНАЛИЗ ТИПА ЛИЦА ===
        
        # Определение формы лица
        width_to_height_ratio = total_face_width / total_measured_height if total_measured_height > 0 else 0
        forehead_to_jaw_ratio = forehead_width / jaw_width if jaw_width > 0 else 0
        
        face_shape = "unknown"
        if width_to_height_ratio > 0.8:
            face_shape = "round"
        elif width_to_height_ratio < 0.65:
            face_shape = "long"
        elif forehead_to_jaw_ratio > 1.1:
            face_shape = "heart"
        elif forehead_to_jaw_ratio < 0.9:
            face_shape = "square"
        else:
            face_shape = "oval"
        
        # === АНАЛИЗ РЕАЛЬНОЙ ВЫСОТЫ ГОЛОВЫ (включая волосы) ===
        
        # MediaPipe не всегда точно определяет верх головы с волосами
        # Добавим эвристику для оценки реальной высоты
        hair_height_estimate = forehead_height * 0.2  # ~20% от высоты лба для волос
        estimated_hair_top = forehead_top_y - hair_height_estimate
        
        # === РАСЧЕТ ОПТИМАЛЬНЫХ ЗОН ДЛЯ КРОПА ===
        
        # Верхняя граница: должна включать волосы и лоб
        optimal_top_crop_zone = [
            estimated_hair_top - (forehead_height * 0.1),  # Минимум с учетом волос
            estimated_hair_top - (forehead_height * 0.4)   # Максимум с большим запасом
        ]
        
        # Нижняя граница: должна включать подбородок
        optimal_bottom_crop_zone = [
            chin_bottom_y + (lips_to_chin * 0.1),     # Минимум
            chin_bottom_y + (lips_to_chin * 0.3)      # Максимум
        ]
        
        # Боковые границы: симметрично от центра лица
        face_center_x = (face_contour_left_x + face_contour_right_x) / 2
        optimal_side_margin = total_face_width * 0.15  # 15% от ширины лица как отступ
        
        logging.info(f"🧠 АНАТОМИЧЕСКИЙ АНАЛИЗ:")
        logging.info(f"   Форма лица: {face_shape} (ratio: {width_to_height_ratio:.2f})")
        logging.info(f"   Пропорции: лоб={forehead_ratio:.2f}, середина={mid_face_ratio:.2f}, низ={lower_face_ratio:.2f}")
        logging.info(f"   Размеры: лицо={total_face_width:.0f}x{total_measured_height:.0f}px, глаза={eye_distance:.0f}px")
        logging.info(f"   Височная ширина: {head_width_at_temples:.0f}px, челюсть: {jaw_width:.0f}px")
        
        return {
            # Основные координаты
            'forehead_top': forehead_top_y,
            'estimated_hair_top': estimated_hair_top,
            'eye_level': eye_level,
            'chin_bottom': chin_bottom_y,
            'face_center_x': face_center_x,
            
            # Детальные измерения
            'total_face_height': total_measured_height,
            'total_face_width': total_face_width,
            'forehead_height': forehead_height,
            'forehead_width': forehead_width,
            'eye_distance': eye_distance,
            'eye_height': eye_height,
            'nose_length': nose_length,
            'nose_width': nose_width,
            'mouth_width': mouth_width,
            'jaw_width': jaw_width,
            'head_width_at_temples': head_width_at_temples,
            
            # Пропорции
            'forehead_ratio': forehead_ratio,
            'mid_face_ratio': mid_face_ratio,
            'lower_face_ratio': lower_face_ratio,
            'width_to_height_ratio': width_to_height_ratio,
            'eye_to_face_width_ratio': eye_to_face_width_ratio,
            'nose_to_face_width_ratio': nose_to_face_width_ratio,
            'mouth_to_face_width_ratio': mouth_to_face_width_ratio,
            
            # Анализ типа лица
            'face_shape': face_shape,
            'forehead_to_jaw_ratio': forehead_to_jaw_ratio,
            
            # Оптимальные зоны для кропа
            'optimal_top_crop_zone': optimal_top_crop_zone,
            'optimal_bottom_crop_zone': optimal_bottom_crop_zone,
            'optimal_side_margin': optimal_side_margin,
            
            # Детальные координаты ключевых точек
            'left_eye_center': left_eye_center,
            'right_eye_center': right_eye_center,
            'nose_tip': nose_tip,
            'lips_center': lips_center,
            'chin_tip': chin_tip,
            'jaw_left': jaw_left,
            'jaw_right': jaw_right,
            'temple_left': temple_left,
            'temple_right': temple_right,
            
            # Границы контура лица
            'face_contour_bounds': {
                'left': face_contour_left_x,
                'right': face_contour_right_x,
                'top': face_contour_top_y,
                'bottom': face_contour_bottom_y
            }
        }

def calculate_intelligent_crop_dimensions(face_landmarks, img_height: int, img_width: int, photo_spec: PhotoSpecification):
    """🚀 СУПЕР АЛГОРИТМ на базе детального анализа анатомии лица"""
    analyzer = FaceAnalyzer(face_landmarks, img_height, img_width)
    anatomy = analyzer.analyze_comprehensive_face_anatomy()
    
    # Target final photo dimensions
    target_photo_width_px = photo_spec.photo_width_px
    target_photo_height_px = photo_spec.photo_height_px
    
    # 🧠 SUPER ADAPTIVE SCALING на базе детального анализа анатомии
    # Используем все данные о лице для идеального масштабирования
    current_eye_level_px = anatomy['eye_level']
    current_forehead_top_px = anatomy['forehead_top'] 
    current_estimated_hair_top_px = anatomy['estimated_hair_top']  # ВАЖНО: учитываем волосы!
    current_chin_bottom_px = anatomy['chin_bottom']
    current_face_width_px = anatomy['total_face_width']
    face_shape = anatomy['face_shape']
    forehead_ratio = anatomy['forehead_ratio']
    
    # Пересчитываем высоту лица с учетом волос
    current_face_height_px = current_chin_bottom_px - current_estimated_hair_top_px
    
    # Calculate possible scale factors for different constraints
    scale_factors_candidates = []
    constraint_descriptions = []
    
    # 1. Head height constraints
    min_target_head_height_px = photo_spec.head_min_px
    max_target_head_height_px = photo_spec.head_max_px
    
    scale_for_min_head = min_target_head_height_px / current_face_height_px
    scale_for_max_head = max_target_head_height_px / current_face_height_px
    
    scale_factors_candidates.extend([scale_for_min_head, scale_for_max_head])
    constraint_descriptions.extend(["min_head_height", "max_head_height"])
    
    # 2. Eye position constraints (if specified)
    if photo_spec.eye_min_from_bottom_px is not None and photo_spec.eye_max_from_bottom_px is not None:
        # For each eye constraint, calculate what scale would be needed
        for target_eye_from_bottom in [photo_spec.eye_min_from_bottom_px, photo_spec.eye_max_from_bottom_px]:
            target_eye_from_top = target_photo_height_px - target_eye_from_bottom
            
            # We need to find scale such that when we position eyes correctly, head fits
            # This is more complex - we need to consider crop positioning too
            # For now, add eye-based scale candidates
            
            # Используем детальный анализ анатомии для точного расчета
            # Соотношение глаз к лбу основано на реальной анатомии
            eye_to_forehead_ratio = (current_eye_level_px - current_forehead_top_px) / current_face_height_px
            
            # После масштабирования и позиционирования глаза должны быть на target_eye_from_top
            # Учитываем анатомические пропорции для расчета требуемого размера лица
            required_face_height = target_eye_from_top / eye_to_forehead_ratio
            
            if required_face_height > 0:
                scale_for_eye = required_face_height / current_face_height_px
                if min_target_head_height_px <= required_face_height <= max_target_head_height_px:
                    scale_factors_candidates.append(scale_for_eye)
                    constraint_descriptions.append(f"eye_from_bottom_{target_eye_from_bottom}")
    
    elif photo_spec.eye_min_from_top_px is not None and photo_spec.eye_max_from_top_px is not None:
        # Similar logic for eye from top
        for target_eye_from_top in [photo_spec.eye_min_from_top_px, photo_spec.eye_max_from_top_px]:
            eye_to_forehead_ratio = (current_eye_level_px - current_forehead_top_px) / current_face_height_px
            required_face_height = target_eye_from_top / eye_to_forehead_ratio
            
            if required_face_height > 0:
                scale_for_eye = required_face_height / current_face_height_px
                if min_target_head_height_px <= required_face_height <= max_target_head_height_px:
                    scale_factors_candidates.append(scale_for_eye)
                    constraint_descriptions.append(f"eye_from_top_{target_eye_from_top}")
    
    # 3. УМНЫЕ ОГРАНИЧЕНИЯ на базе формы лица и анатомии
    # Адаптивные ограничения в зависимости от типа лица
    
    if face_shape == "round":
        # Круглые лица нужно немного вытянуть
        width_multiplier_min, width_multiplier_max = 1.3, 0.9
        height_multiplier_min, height_multiplier_max = 1.6, 0.7
    elif face_shape == "long":
        # Длинные лица нужно визуально расширить
        width_multiplier_min, width_multiplier_max = 1.6, 0.7
        height_multiplier_min, height_multiplier_max = 1.9, 0.5
    elif face_shape == "heart":
        # Сердцевидные лица (широкий лоб, узкий подбородок)
        width_multiplier_min, width_multiplier_max = 1.4, 0.8
        height_multiplier_min, height_multiplier_max = 1.7, 0.6
    elif face_shape == "square":
        # Квадратные лица нужно смягчить
        width_multiplier_min, width_multiplier_max = 1.5, 0.8
        height_multiplier_min, height_multiplier_max = 1.7, 0.6
    else:  # oval или unknown
        # Овальные лица - идеальная форма
        width_multiplier_min, width_multiplier_max = 1.4, 0.9
        height_multiplier_min, height_multiplier_max = 1.8, 0.6
    
    min_reasonable_scale = max(
        target_photo_width_px / (current_face_width_px * width_multiplier_min),
        target_photo_height_px / (current_face_height_px * height_multiplier_min)
    )
    max_reasonable_scale = min(
        target_photo_width_px / (current_face_width_px * width_multiplier_max),
        target_photo_height_px / (current_face_height_px * height_multiplier_max)
    )
    
    scale_factors_candidates.extend([min_reasonable_scale, max_reasonable_scale])
    constraint_descriptions.extend(["min_reasonable", "max_reasonable"])
    
    # OPTIMIZATION: Find the best scale factor that satisfies most constraints
    logging.info(f"📊 АНАЛИЗ МАСШТАБИРОВАНИЯ:")
    logging.info(f"   Текущий размер лица: {current_face_height_px:.1f}px")
    logging.info(f"   Целевой диапазон: {min_target_head_height_px:.1f}-{max_target_head_height_px:.1f}px")
    logging.info(f"   Разумные границы scale: {min_reasonable_scale:.3f}-{max_reasonable_scale:.3f}")
    
    valid_scales = []
    for i, scale in enumerate(scale_factors_candidates):
        # Check if this scale produces valid results
        test_face_height = current_face_height_px * scale
        
        # Проверяем все условия
        height_ok = min_target_head_height_px <= test_face_height <= max_target_head_height_px
        scale_ok = min_reasonable_scale <= scale <= max_reasonable_scale
        
        if height_ok and scale_ok:
            valid_scales.append((scale, constraint_descriptions[i]))
            logging.debug(f"   ✓ Scale {scale:.3f} ({constraint_descriptions[i]}): высота={test_face_height:.1f}px")
        else:
            reason = []
            if not height_ok:
                reason.append(f"высота {test_face_height:.1f}px вне диапазона")
            if not scale_ok:
                reason.append(f"scale {scale:.3f} вне разумных границ")
            logging.debug(f"   ✗ Scale {scale:.3f} ({constraint_descriptions[i]}): {', '.join(reason)}")
    
    if not valid_scales:
        # Fallback: use midpoint if no perfect solution
        scale_factor = (scale_for_min_head + scale_for_max_head) / 2
        logging.warning(f"No optimal scale found, using midpoint: {scale_factor:.3f}")
    else:
        # Choose the scale that best balances all constraints
        # Prefer scales that come from eye constraints if available
        eye_scales = [s for s, desc in valid_scales if "eye_" in desc]
        if eye_scales:
            scale_factor = sum(eye_scales) / len(eye_scales)
            logging.info(f"Using eye-optimized scale: {scale_factor:.3f}")
        else:
            # Use average of valid scales
            scale_factor = sum(s for s, _ in valid_scales) / len(valid_scales)
            logging.info(f"Using constraint-balanced scale: {scale_factor:.3f}")
    
    logging.info(f"🎯 Adaptive scaling: current_face={current_face_height_px:.1f}px, target_range={min_target_head_height_px:.1f}-{max_target_head_height_px:.1f}px, chosen_scale={scale_factor:.3f}")
    
    # Scale all face measurements using detailed anatomy
    scaled_forehead_top = anatomy['forehead_top'] * scale_factor
    scaled_estimated_hair_top = anatomy['estimated_hair_top'] * scale_factor  # ВАЖНО: масштабируем волосы
    scaled_chin_bottom = anatomy['chin_bottom'] * scale_factor
    scaled_eye_level = anatomy['eye_level'] * scale_factor
    scaled_face_center_x = anatomy['face_center_x'] * scale_factor
    scaled_face_height = current_face_height_px * scale_factor  # Используем пересчитанную высоту
    scaled_face_width = anatomy['total_face_width'] * scale_factor
    
    # Scale image dimensions
    scaled_img_width = img_width * scale_factor
    scaled_img_height = img_height * scale_factor
    
    # ADAPTIVE POSITIONING OPTIMIZATION
    # Try different positioning strategies and find the one that best satisfies all constraints
    positioning_candidates = []
    
    # Strategy 1: Eye-based positioning (if eye constraints exist)
    if photo_spec.eye_min_from_bottom_px is not None and photo_spec.eye_max_from_bottom_px is not None:
        # Генерируем больше кандидатов в диапазоне, не только крайние точки
        eye_range = photo_spec.eye_max_from_bottom_px - photo_spec.eye_min_from_bottom_px
        eye_candidates = [
            photo_spec.eye_min_from_bottom_px,  # Минимум
            photo_spec.eye_min_from_bottom_px + eye_range * 0.25,  # 25%
            photo_spec.eye_min_from_bottom_px + eye_range * 0.5,   # 50% (середина)
            photo_spec.eye_min_from_bottom_px + eye_range * 0.75,  # 75%
            photo_spec.eye_max_from_bottom_px   # Максимум
        ]
        
        for target_eye_from_bottom in eye_candidates:
            target_eye_from_top = target_photo_height_px - target_eye_from_bottom
            crop_top_candidate = scaled_eye_level - target_eye_from_top
            
            # ВАЖНО: Проверяем, не обрежется ли голова С УЧЕТОМ ВОЛОС
            test_hair_top = scaled_estimated_hair_top - crop_top_candidate
            if test_hair_top >= -5:  # Минимальный запас для волос
                positioning_candidates.append((crop_top_candidate, f"eye_from_bottom_{target_eye_from_bottom:.1f}"))
    
    elif photo_spec.eye_min_from_top_px is not None and photo_spec.eye_max_from_top_px is not None:
        eye_range = photo_spec.eye_max_from_top_px - photo_spec.eye_min_from_top_px
        eye_candidates = [
            photo_spec.eye_min_from_top_px,
            photo_spec.eye_min_from_top_px + eye_range * 0.25,
            photo_spec.eye_min_from_top_px + eye_range * 0.5,
            photo_spec.eye_min_from_top_px + eye_range * 0.75,
            photo_spec.eye_max_from_top_px
        ]
        
        for target_eye_from_top in eye_candidates:
            crop_top_candidate = scaled_eye_level - target_eye_from_top
            
            # Проверяем границы головы с учетом волос
            test_hair_top = scaled_estimated_hair_top - crop_top_candidate
            if test_hair_top >= -5:
                positioning_candidates.append((crop_top_candidate, f"eye_from_top_{target_eye_from_top:.1f}"))
    
    # Strategy 2: Head-top based positioning using detailed anatomy
    forehead_ratio = anatomy['forehead_ratio']
    face_shape = anatomy['face_shape']
    
    # АДАПТИВНЫЕ ОТСТУПЫ на базе формы лица и пропорций
    if face_shape == "round":
        # Круглые лица: больше места сверху для визуального удлинения
        top_space_ratios = [0.08, 0.12, 0.15, 0.18]
    elif face_shape == "long":
        # Длинные лица: меньше места сверху
        top_space_ratios = [0.04, 0.06, 0.08, 0.10]
    elif face_shape == "heart":
        # Сердцевидные: учитываем широкий лоб
        top_space_ratios = [0.06, 0.10, 0.12, 0.15]
    elif face_shape == "square":
        # Квадратные: стандартные пропорции
        top_space_ratios = [0.08, 0.10, 0.12, 0.14]
    else:  # oval или unknown
        # Овальные: классические пропорции с учетом лба
        if forehead_ratio > 0.4:  # Large forehead
            top_space_ratios = [0.10, 0.12, 0.15, 0.18]
        elif forehead_ratio > 0.3:  # Medium forehead
            top_space_ratios = [0.08, 0.10, 0.12, 0.15]
        else:  # Small forehead
            top_space_ratios = [0.05, 0.08, 0.10, 0.12]
    
    for top_space_ratio in top_space_ratios:
        top_space_px = target_photo_height_px * top_space_ratio
        crop_top_candidate = scaled_estimated_hair_top - top_space_px  # Используем hair_top!
        positioning_candidates.append((crop_top_candidate, f"proportional_{top_space_ratio:.2f}"))
    
    # Strategy 3: Center-based positioning with different balance points
    face_center_y = (scaled_forehead_top + scaled_chin_bottom) / 2
    for center_offset_ratio in [-0.05, 0, 0.05, 0.10]:  # Slightly above/below center
        center_offset = target_photo_height_px * center_offset_ratio
        crop_top_candidate = face_center_y - (target_photo_height_px / 2) + center_offset
        positioning_candidates.append((crop_top_candidate, f"center_offset_{center_offset_ratio:.2f}"))
    
    # EVALUATE ALL POSITIONING CANDIDATES
    best_score = -1
    best_crop_top = None
    best_description = ""
    
    for crop_top_candidate, description in positioning_candidates:
        score = 0
        penalties = 0
        
        # Calculate final positions with this crop_top
        final_hair_top = scaled_estimated_hair_top - crop_top_candidate  # ВАЖНО: позиция волос
        final_forehead_top = scaled_forehead_top - crop_top_candidate
        final_chin_bottom = scaled_chin_bottom - crop_top_candidate
        final_eye_level = scaled_eye_level - crop_top_candidate
        
        # Evaluate constraints satisfaction
        
        # 1. Head not cut off (critical) - проверяем ВОЛОСЫ!
        if final_hair_top >= 0:
            score += 50  # High score for not cutting hair/head top
            # Дополнительный бонус за хороший отступ сверху
            if final_hair_top > 20:
                score += 10
        else:
            penalties += abs(final_hair_top) * 3  # Усиленный штраф за обрезание волос
        
        if final_chin_bottom <= target_photo_height_px:
            score += 30  # Good score for not cutting chin
        else:
            penalties += (final_chin_bottom - target_photo_height_px) * 1.5
        
        # 2. Eye position compliance (if specified)
        if photo_spec.eye_min_from_bottom_px is not None and photo_spec.eye_max_from_bottom_px is not None:
            final_eye_from_bottom = target_photo_height_px - final_eye_level
            if photo_spec.eye_min_from_bottom_px <= final_eye_from_bottom <= photo_spec.eye_max_from_bottom_px:
                # Дополнительный бонус за позицию ближе к центру диапазона
                eye_range_center = (photo_spec.eye_min_from_bottom_px + photo_spec.eye_max_from_bottom_px) / 2
                distance_from_center = abs(final_eye_from_bottom - eye_range_center)
                max_distance = (photo_spec.eye_max_from_bottom_px - photo_spec.eye_min_from_bottom_px) / 2
                center_bonus = 50 * (1 - distance_from_center / max_distance)  # 0-50 баллов
                score += 100 + center_bonus  # 100-150 баллов
            else:
                # Penalty based on distance from range
                distance_from_range = min(abs(final_eye_from_bottom - photo_spec.eye_min_from_bottom_px),
                                        abs(final_eye_from_bottom - photo_spec.eye_max_from_bottom_px))
                penalties += distance_from_range * 3
        
        elif photo_spec.eye_min_from_top_px is not None and photo_spec.eye_max_from_top_px is not None:
            if photo_spec.eye_min_from_top_px <= final_eye_level <= photo_spec.eye_max_from_top_px:
                score += 100
            else:
                distance_from_range = min(abs(final_eye_level - photo_spec.eye_min_from_top_px),
                                        abs(final_eye_level - photo_spec.eye_max_from_top_px))
                penalties += distance_from_range * 3
        
        # 3. Aesthetic balance (forehead not too high or too low)
        forehead_position_ratio = final_forehead_top / target_photo_height_px
        
        # Адаптивные эстетические диапазоны в зависимости от формы лица
        if face_shape == "round":
            ideal_range = (0.08, 0.20)  # Немного выше для круглых лиц
            ideal_center = 0.14
        elif face_shape == "long":
            ideal_range = (0.04, 0.15)  # Ниже для длинных лиц
            ideal_center = 0.10
        elif face_shape == "heart":
            ideal_range = (0.06, 0.18)  # Учитываем широкий лоб
            ideal_center = 0.12
        else:  # oval, square, unknown
            ideal_range = (0.05, 0.25)  # Стандартный диапазон
            ideal_center = 0.15
        
        if ideal_range[0] <= forehead_position_ratio <= ideal_range[1]:
            score += 20
        else:
            penalties += abs(forehead_position_ratio - ideal_center) * 50
        
        # 4. Face proportions preserved
        if forehead_ratio > 0.35:  # Large forehead needs more space
            if forehead_position_ratio > 0.10:
                score += 10
        else:  # Small forehead can be positioned higher
            if forehead_position_ratio < 0.20:
                score += 10
        
        # 5. Специальная обработка для круглых лиц
        if face_shape == "round":
            # Круглые лица выглядят лучше с большим пространством сверху
            if 0.10 <= forehead_position_ratio <= 0.18:
                score += 25  # Бонус за оптимальное позиционирование
            # Штраф за слишком высокое позиционирование (голова прижата к верху)
            if forehead_position_ratio < 0.05:
                penalties += 30
        
        final_score = score - penalties
        
        if final_score > best_score:
            best_score = final_score
            best_crop_top = crop_top_candidate
            best_description = description
    
    crop_top = best_crop_top
    
    # Диагностика выбранного позиционирования
    final_hair_pos = (scaled_estimated_hair_top - crop_top) / target_photo_height_px
    final_forehead_pos = (scaled_forehead_top - crop_top) / target_photo_height_px
    final_eye_from_bottom = target_photo_height_px - (scaled_eye_level - crop_top)
    
    logging.info(f"📍 ПОЗИЦИОНИРОВАНИЕ:")
    logging.info(f"   Выбран: '{best_description}' (score: {best_score:.1f})")
    logging.info(f"   Волосы от верха: {final_hair_pos*100:.1f}% ({final_hair_pos*target_photo_height_px:.0f}px)")
    logging.info(f"   Лоб от верха: {final_forehead_pos*100:.1f}% ({final_forehead_pos*target_photo_height_px:.0f}px)")
    logging.info(f"   Глаза от низа: {final_eye_from_bottom:.0f}px (требование: {photo_spec.eye_min_from_bottom_px}-{photo_spec.eye_max_from_bottom_px}px)")
    
    # Calculate crop boundaries
    crop_bottom = crop_top + target_photo_height_px
    crop_left = scaled_face_center_x - (target_photo_width_px / 2)
    crop_right = crop_left + target_photo_width_px
    
    # Boundary adjustments
    if crop_top < 0:
        crop_bottom -= crop_top
        crop_top = 0
    if crop_bottom > scaled_img_height:
        crop_top -= (crop_bottom - scaled_img_height)
        crop_bottom = scaled_img_height
    if crop_left < 0:
        crop_right -= crop_left
        crop_left = 0
    if crop_right > scaled_img_width:
        crop_left -= (crop_right - scaled_img_width)
        crop_right = scaled_img_width
    
    # Final measurements using detailed anatomy
    final_hair_top_in_crop = scaled_estimated_hair_top - crop_top
    final_forehead_top_in_crop = scaled_forehead_top - crop_top
    final_chin_bottom_in_crop = scaled_chin_bottom - crop_top
    final_eye_level_in_crop = scaled_eye_level - crop_top
    
    # Validation - ПРОВЕРЯЕМ ВОЛОСЫ!
    head_not_cut_top = final_hair_top_in_crop >= 0  # Изменено: проверяем волосы, не лоб
    head_not_cut_bottom = final_chin_bottom_in_crop <= target_photo_height_px
    eye_in_bounds = 0 <= final_eye_level_in_crop <= target_photo_height_px
    
    positioning_success = head_not_cut_top and head_not_cut_bottom and eye_in_bounds
    
    if positioning_success:
        logging.info(f"✅ Intelligent positioning successful")
    else:
        logging.warning(f"⚠️ Positioning constraints: head_cut_top={not head_not_cut_top}, head_cut_bottom={not head_not_cut_bottom}, eye_out_bounds={not eye_in_bounds}")
    
    return {
        'scale_factor': float(scale_factor),
        'crop_top': int(round(crop_top)),
        'crop_bottom': int(round(crop_bottom)),
        'crop_left': int(round(crop_left)),
        'crop_right': int(round(crop_right)),
        'final_photo_width_px': target_photo_width_px,
        'final_photo_height_px': target_photo_height_px,
        'achieved_head_height_px': int(round(scaled_face_height)),
        'achieved_eye_level_from_top_px': int(round(final_eye_level_in_crop)),
        'positioning_success': positioning_success,
        'face_anatomy': anatomy
    }

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
    # For better compliance, aim for 75% of the range (closer to max) to ensure compliance
    target_head_percentage = 0.75  # Use 75% of range instead of 50%
    ideal_target_head_height_px = min_target_head_height_px + (max_target_head_height_px - min_target_head_height_px) * target_head_percentage
    scale_factor = ideal_target_head_height_px / original_head_height_px
    
    # Clamp scale factor: ensure scaled head is not too small or too large
    scale_factor = max(scale_factor, scale_for_min_head) 
    scale_factor = min(scale_factor, scale_for_max_head)

    # Store the head-compliant scale factor before applying dimension constraints
    head_compliant_scale_factor = scale_factor

    # Further constraints: the scaled image must be at least as large as the target photo dimensions
    # BUT prioritize head size compliance over image size
    dimension_scale_factor = scale_factor
    if int(img_width * scale_factor) < target_photo_width_px:
        scale_factor_for_width = target_photo_width_px / img_width
        dimension_scale_factor = max(dimension_scale_factor, scale_factor_for_width)
        
    if int(img_height * scale_factor) < target_photo_height_px:
        scale_factor_for_height = target_photo_height_px / img_height
        dimension_scale_factor = max(dimension_scale_factor, scale_factor_for_height)
    
    # Use the larger of head-compliant scale or dimension-required scale
    # This ensures head compliance is prioritized
    scale_factor = max(head_compliant_scale_factor, dimension_scale_factor)
    
    logging.debug(f"Chosen scale_factor: {scale_factor:.4f} (min_head_scale={scale_for_min_head:.4f}, max_head_scale={scale_for_max_head:.4f})")

    # --- Calculate dimensions after scaling ---
    scaled_img_width = int(img_width * scale_factor)
    scaled_img_height = int(img_height * scale_factor)
    
    scaled_head_top_px = original_head_top_px * scale_factor
    scaled_chin_bottom_px = original_chin_bottom_px * scale_factor
    scaled_eye_level_px = original_eye_level_px * scale_factor
    scaled_face_center_x_px = original_face_center_x_px * scale_factor
    scaled_face_height_px = scaled_chin_bottom_px - scaled_head_top_px


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
    
    # UNIVERSAL HEAD POSITIONING ALGORITHM
    # Define margins based on document type - more strict for official documents
    mm_per_pixel = PhotoSpecification.MM_PER_INCH / photo_spec.dpi
    
    # Use official spec margins if available, otherwise use defaults based on document type
    if photo_spec.distance_top_of_head_to_top_of_photo_min_mm is not None and photo_spec.distance_top_of_head_to_top_of_photo_max_mm is not None:
        # Use official specification values
        min_top_margin_mm = photo_spec.distance_top_of_head_to_top_of_photo_min_mm
        max_top_margin_mm = photo_spec.distance_top_of_head_to_top_of_photo_max_mm
        ideal_top_margin_mm = (min_top_margin_mm + max_top_margin_mm) / 2
        logging.info(f"Using official spec head margins: {min_top_margin_mm}-{max_top_margin_mm}mm")
    elif 'visa' in photo_spec.document_name.lower() or 'lottery' in photo_spec.document_name.lower():
        # Relaxed default for visa/lottery when no official spec available
        min_top_margin_mm = 1.0  
        max_top_margin_mm = 8.0  # More relaxed to avoid cutting heads
        ideal_top_margin_mm = 4.0
        logging.info(f"Using default visa/lottery margins: {min_top_margin_mm}-{max_top_margin_mm}mm")
    else:
        # Default for other documents
        min_top_margin_mm = 1.5
        max_top_margin_mm = 7.0
        ideal_top_margin_mm = 4.0
        logging.info(f"Using default margins: {min_top_margin_mm}-{max_top_margin_mm}mm")
    
    min_top_margin_px = min_top_margin_mm / mm_per_pixel
    max_top_margin_px = max_top_margin_mm / mm_per_pixel
    ideal_top_margin_px = ideal_top_margin_mm / mm_per_pixel
    
    # STRATEGY 1: Position head with ideal top margin (PRIORITY APPROACH)
    crop_top_by_margin = scaled_head_top_px - ideal_top_margin_px
    crop_bottom_by_margin = crop_top_by_margin + target_photo_height_px
    
    logging.debug(f"Margin-based positioning: crop_top={crop_top_by_margin:.1f}, head_top_margin={ideal_top_margin_mm:.1f}mm")
    
    # STRATEGY 2: Position by eye line (original approach)
    if photo_spec.eye_min_from_bottom_px is not None and photo_spec.eye_max_from_bottom_px is not None:
        target_eye_pos_from_top_px = target_photo_height_px - ( (photo_spec.eye_min_from_bottom_px + photo_spec.eye_max_from_bottom_px) / 2 )
        crop_top_by_eyes = scaled_eye_level_px - target_eye_pos_from_top_px
    elif photo_spec.eye_min_from_top_px is not None and photo_spec.eye_max_from_top_px is not None:
        target_eye_pos_from_top_px = (photo_spec.eye_min_from_top_px + photo_spec.eye_max_from_top_px) / 2
        crop_top_by_eyes = scaled_eye_level_px - target_eye_pos_from_top_px
    else:
        # Fallback: center the head
        scaled_head_center_y = (scaled_head_top_px + scaled_chin_bottom_px) / 2
        crop_top_by_eyes = scaled_head_center_y - (target_photo_height_px / 2)
    
    # HYBRID APPROACH: Choose the positioning that satisfies both constraints best
    # Check if margin-based positioning also satisfies eye constraints
    eye_pos_with_margin = scaled_eye_level_px - crop_top_by_margin
    eye_from_bottom_with_margin = target_photo_height_px - eye_pos_with_margin
    
    # Check if margin-based positioning satisfies eye requirements
    eye_compliant_with_margin = True
    if photo_spec.eye_min_from_bottom_px is not None and photo_spec.eye_max_from_bottom_px is not None:
        eye_compliant_with_margin = (photo_spec.eye_min_from_bottom_px <= eye_from_bottom_with_margin <= photo_spec.eye_max_from_bottom_px)
    
    if eye_compliant_with_margin:
        # Margin-based positioning satisfies both constraints - use it
        crop_top = crop_top_by_margin
        logging.debug(f"Using margin-based positioning (satisfies both constraints)")
    else:
        # Check if document has strict eye requirements
        has_eye_requirements = (photo_spec.eye_min_from_bottom_px is not None and 
                               photo_spec.eye_max_from_bottom_px is not None)
        
        if has_eye_requirements:
            # For documents with strict eye requirements: try to balance eye position and top margin
            crop_top = crop_top_by_eyes
            eye_pos_with_eyes = scaled_eye_level_px - crop_top_by_eyes
            eye_from_bottom_with_eyes = target_photo_height_px - eye_pos_with_eyes
            
            # Check if eye-based positioning creates excessive top margin
            head_top_with_eyes = scaled_head_top_px - crop_top_by_eyes
            top_margin_with_eyes = head_top_with_eyes * mm_per_pixel
            
            if top_margin_with_eyes > max_top_margin_mm:
                # Eye positioning creates too much top margin, try compromise
                allowed_head_top_px = max_top_margin_px
                compromise_crop_top = scaled_head_top_px - allowed_head_top_px
                
                # Check if compromise still satisfies eye requirements
                eye_pos_compromise = scaled_eye_level_px - compromise_crop_top
                eye_from_bottom_compromise = target_photo_height_px - eye_pos_compromise
                
                if (photo_spec.eye_min_from_bottom_px <= eye_from_bottom_compromise <= photo_spec.eye_max_from_bottom_px):
                    crop_top = compromise_crop_top
                    logging.info(f"Using compromise positioning for {photo_spec.document_name} - top margin: {max_top_margin_mm:.1f}mm, eye distance: {eye_from_bottom_compromise:.1f}px")
                else:
                    # Keep eye-based positioning even if margin is excessive
                    logging.warning(f"Using eye-based positioning with excessive top margin ({top_margin_with_eyes:.1f}mm) to satisfy eye requirements")
            else:
                logging.info(f"Using eye-based positioning for {photo_spec.document_name} - eye distance: {eye_from_bottom_with_eyes:.1f}px (req: {photo_spec.eye_min_from_bottom_px}-{photo_spec.eye_max_from_bottom_px}px)")
        elif 'visa' in photo_spec.document_name.lower() or 'lottery' in photo_spec.document_name.lower():
            # For visa/lottery without eye requirements: use margin-based positioning
            crop_top = crop_top_by_margin
            logging.info(f"Using margin-based positioning for {photo_spec.document_name} (no eye requirements)")
        else:
            # For other documents: allow some compromise
            weight_margin = 0.8  # 80% weight to margins
            weight_eyes = 0.2    # 20% weight to eyes
            
            optimal_crop_top = (crop_top_by_margin * weight_margin + crop_top_by_eyes * weight_eyes)
            crop_top = optimal_crop_top
            logging.debug(f"Using weighted compromise positioning (margin={weight_margin}, eyes={weight_eyes})")
    
    crop_bottom = crop_top + target_photo_height_px

    # Calculate head position in the cropped image for validation
    head_top_in_crop = scaled_head_top_px - crop_top
    head_bottom_in_crop = scaled_chin_bottom_px - crop_top
    
    min_bottom_margin_px = min_top_margin_px  # Same minimum for bottom
    
    # Check if head positioning violates margin requirements
    head_cut_off_top = head_top_in_crop < min_top_margin_px
    head_cut_off_bottom = head_bottom_in_crop > (target_photo_height_px - min_bottom_margin_px)
    excessive_top_margin = head_top_in_crop > max_top_margin_px
    
    # CRITICAL ADJUSTMENTS - Priority: prevent cutoff, then optimize margins
    if head_cut_off_top:
        # EMERGENCY: Head too close to top - must fix immediately
        required_adjustment = min_top_margin_px - head_top_in_crop + 3  # Add 3px safety buffer
        crop_top += required_adjustment
        crop_bottom += required_adjustment
        logging.warning(f"EMERGENCY: Adjusted crop down by {required_adjustment:.1f}px to prevent head cutoff at top")
        
        # Recalculate positions after emergency adjustment
        head_top_in_crop = scaled_head_top_px - crop_top
        head_bottom_in_crop = scaled_chin_bottom_px - crop_top
    
    elif head_cut_off_bottom:
        # EMERGENCY: Head too close to bottom - must fix immediately
        max_allowed_head_bottom = target_photo_height_px - min_bottom_margin_px
        required_adjustment = head_bottom_in_crop - max_allowed_head_bottom + 3  # Add 3px safety buffer
        crop_top += required_adjustment
        crop_bottom += required_adjustment
        logging.warning(f"EMERGENCY: Adjusted crop up by {required_adjustment:.1f}px to prevent head cutoff at bottom")
        
        # Recalculate positions after emergency adjustment
        head_top_in_crop = scaled_head_top_px - crop_top
        head_bottom_in_crop = scaled_chin_bottom_px - crop_top
    
    elif excessive_top_margin:
        # OPTIMIZATION: Too much top margin - try to reduce it to ideal
        current_top_margin = head_top_in_crop
        desired_reduction = current_top_margin - ideal_top_margin_px
        
        # Check if reduction would cause bottom issues
        new_head_bottom = head_bottom_in_crop + desired_reduction
        would_cut_bottom = new_head_bottom > (target_photo_height_px - min_bottom_margin_px)
        
        if not would_cut_bottom:
            # Safe to make full reduction
            crop_top -= desired_reduction
            crop_bottom -= desired_reduction
            logging.debug(f"Optimized: Reduced top margin by {desired_reduction:.1f}px to achieve ideal margin")
        else:
            # Make partial reduction to avoid bottom issues
            max_safe_reduction = (target_photo_height_px - min_bottom_margin_px) - head_bottom_in_crop - 3  # 3px buffer
            if max_safe_reduction > 0:
                crop_top -= max_safe_reduction
                crop_bottom -= max_safe_reduction
                logging.debug(f"Optimized: Partial reduction of {max_safe_reduction:.1f}px to balance top/bottom margins")
    
    # Final validation of head positioning
    head_top_in_crop_final = scaled_head_top_px - crop_top
    head_bottom_in_crop_final = scaled_chin_bottom_px - crop_top
    final_top_margin_mm = head_top_in_crop_final * mm_per_pixel  # FIXED: multiply, not divide
    final_bottom_margin_mm = (target_photo_height_px - head_bottom_in_crop_final) * mm_per_pixel  # FIXED: multiply, not divide
    
    logging.debug(f"Final head positioning: top_margin={final_top_margin_mm:.1f}mm, bottom_margin={final_bottom_margin_mm:.1f}mm")

    # Adjust vertical crop if it goes out of bounds
    original_crop_top = crop_top
    if crop_top < 0:
        crop_bottom -= crop_top # Shift crop_bottom
        crop_top = 0
        logging.warning(f"Crop adjusted from top boundary: shifted by {original_crop_top:.1f}px")
    if crop_bottom > scaled_img_height:
        adjustment = crop_bottom - scaled_img_height
        crop_top -= adjustment # Shift crop_top
        crop_bottom = scaled_img_height
        logging.warning(f"Crop adjusted from bottom boundary: shifted by {adjustment:.1f}px")

    # Final validation and logging
    head_top_in_crop_final = scaled_head_top_px - crop_top
    head_bottom_in_crop_final = scaled_chin_bottom_px - crop_top
    final_top_margin_mm = head_top_in_crop_final * mm_per_pixel
    final_bottom_margin_mm = (target_photo_height_px - head_bottom_in_crop_final) * mm_per_pixel
    
    # If head gets cut after boundary adjustments, try to fix it
    if head_top_in_crop_final < 0:
        # Head is cut at top, need to adjust crop_top up if possible
        needed_adjustment = -head_top_in_crop_final
        if crop_top >= needed_adjustment:
            crop_top -= needed_adjustment
            crop_bottom -= needed_adjustment
            # Recalculate after adjustment
            head_top_in_crop_final = scaled_head_top_px - crop_top
            head_bottom_in_crop_final = scaled_chin_bottom_px - crop_top
            final_top_margin_mm = head_top_in_crop_final * mm_per_pixel
            final_bottom_margin_mm = (target_photo_height_px - head_bottom_in_crop_final) * mm_per_pixel
            logging.info(f"Adjusted crop to prevent head cutoff: moved up by {needed_adjustment:.1f}px")
    
    # Check if final positioning meets requirements
    top_margin_ok = min_top_margin_mm <= final_top_margin_mm <= max_top_margin_mm
    head_not_cut_top = head_top_in_crop_final >= 0
    head_not_cut_bottom = head_bottom_in_crop_final <= target_photo_height_px
    
    if top_margin_ok and head_not_cut_top and head_not_cut_bottom:
        logging.info(f"✅ SUCCESS: Final positioning - top_margin={final_top_margin_mm:.1f}mm, bottom_margin={final_bottom_margin_mm:.1f}mm")
    else:
        logging.error(f"❌ FAILED: Final positioning - top_margin={final_top_margin_mm:.1f}mm (req: {min_top_margin_mm}-{max_top_margin_mm}mm), cutoff_top={not head_not_cut_top}, cutoff_bottom={not head_not_cut_bottom}")

    # Final sanitization of crop coordinates
    crop_top = max(0, min(int(crop_top), scaled_img_height - 1))
    crop_bottom = max(crop_top + 1, min(int(crop_bottom), scaled_img_height))
    crop_left = max(0, min(int(crop_left), scaled_img_width - 1))
    crop_right = max(crop_left + 1, min(int(crop_right), scaled_img_width))
    
    # Validate final crop dimensions
    final_crop_width = crop_right - crop_left
    final_crop_height = crop_bottom - crop_top
    
    if final_crop_width < target_photo_width_px * 0.8 or final_crop_height < target_photo_height_px * 0.8:
        logging.error(f"Final crop dimensions too small: {final_crop_width}x{final_crop_height} vs target {target_photo_width_px}x{target_photo_height_px}")

    # --- Final measurements on the cropped area (relative to crop_top, crop_left) ---
    # Eye level relative to the top of the *final cropped photo*
    final_eye_level_on_cropped_photo_px = scaled_eye_level_px - crop_top
    
    # Head height on the final photo is the scaled_face_height_px, assuming crop captures it.
    # More accurately, it's the portion of the scaled head visible in the crop.
    # However, the scaling was done to target head height, so scaled_face_height_px is what we aimed for.
    final_head_height_on_cropped_photo_px = scaled_face_height_px 
    
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
        'final_top_margin_mm': final_top_margin_mm,
        'final_bottom_margin_mm': final_bottom_margin_mm,
        'positioning_success': top_margin_ok and head_not_cut_top and head_not_cut_bottom,
    }
    # Note: 'eye_to_bottom' and 'head_height' in inches/mm for direct compliance check
    # will be calculated in VisaPhotoProcessor from these pixel values and spec's DPI.

    logging.debug(f"Final calculated crop_data: {crop_data}")
    return crop_data