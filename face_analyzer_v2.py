# face_analyzer_v2.py
# НОВЫЙ ПОДХОД: Простой, надежный, гарантированно работающий

import logging
import numpy as np
from photo_specs import PhotoSpecification

# Упрощенный набор ключевых точек - только самые важные
ESSENTIAL_FACE_POINTS = {
    'forehead': [10, 151, 9],      # Верх лба
    'eyes': [33, 133, 362, 263],   # Центры глаз
    'nose_tip': [1, 2],            # Кончик носа
    'chin': [152, 175],            # Низ подбородка
    'face_outline': [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 
                     397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 
                     172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
}

class SimpleFaceAnalyzer:
    """Простой и надежный анализатор лица"""
    
    def __init__(self, landmarks, img_height, img_width):
        self.landmarks = landmarks
        self.img_height = img_height
        self.img_width = img_width
    
    def get_face_bounds(self):
        """Получить границы лица с запасом на волосы"""
        # Находим самые крайние точки
        all_x = []
        all_y = []
        
        for i, landmark in enumerate(self.landmarks.landmark):
            x = landmark.x * self.img_width
            y = landmark.y * self.img_height
            all_x.append(x)
            all_y.append(y)
        
        # Базовые границы
        face_left = min(all_x)
        face_right = max(all_x)
        face_bottom = max(all_y)
        
        # Для верха берем минимум из точек лба
        forehead_points = []
        for idx in ESSENTIAL_FACE_POINTS['forehead']:
            if idx < len(self.landmarks.landmark):
                y = self.landmarks.landmark[idx].y * self.img_height
                forehead_points.append(y)
        
        if forehead_points:
            forehead_top = min(forehead_points)
        else:
            forehead_top = min(all_y)
        
        # КРИТИЧНО: Добавляем запас для волос
        # Волосы обычно занимают 15-25% от высоты лица
        face_height = face_bottom - forehead_top
        hair_margin = face_height * 0.25  # 25% запас для волос
        
        estimated_head_top = forehead_top - hair_margin
        
        # Глаза
        eye_points = []
        for idx in ESSENTIAL_FACE_POINTS['eyes']:
            if idx < len(self.landmarks.landmark):
                y = self.landmarks.landmark[idx].y * self.img_height
                eye_points.append(y)
        
        eye_level = np.mean(eye_points) if eye_points else (forehead_top + face_bottom) / 2
        
        return {
            'head_top': estimated_head_top,      # С учетом волос!
            'forehead_top': forehead_top,
            'eye_level': eye_level,
            'chin_bottom': face_bottom,
            'face_left': face_left,
            'face_right': face_right,
            'face_center_x': (face_left + face_right) / 2,
            'face_height_with_hair': face_bottom - estimated_head_top,
            'face_height_visible': face_bottom - forehead_top,
            'hair_margin': hair_margin
        }


def calculate_simple_crop_dimensions(face_landmarks, img_height: int, img_width: int, photo_spec: PhotoSpecification):
    """
    НОВЫЙ АЛГОРИТМ: Простой, предсказуемый, надежный
    
    Принципы:
    1. Всегда оставляем достаточно места для волос
    2. Приоритет безопасности над идеальным позиционированием
    3. Если есть сомнения - добавляем больше пространства
    """
    
    analyzer = SimpleFaceAnalyzer(face_landmarks, img_height, img_width)
    bounds = analyzer.get_face_bounds()
    
    logging.info(f"🎯 НОВЫЙ АЛГОРИТМ - Границы лица:")
    logging.info(f"   Видимое лицо: {bounds['face_height_visible']:.1f}px")
    logging.info(f"   С учетом волос: {bounds['face_height_with_hair']:.1f}px")
    logging.info(f"   Запас на волосы: {bounds['hair_margin']:.1f}px")
    
    # Целевые размеры фото
    target_width = photo_spec.photo_width_px
    target_height = photo_spec.photo_height_px
    
    # ШАГ 1: Определяем масштаб
    # Целевая высота головы должна быть в пределах спецификации
    min_head_height = photo_spec.head_min_px
    max_head_height = photo_spec.head_max_px
    
    # УМНОЕ МАСШТАБИРОВАНИЕ: начинаем с минимального требования
    # Это даст максимальный размер головы при соблюдении требований
    target_head_height = min_head_height * 1.1  # +10% запас от минимума
    
    # Масштабируем по высоте головы С УЧЕТОМ ВОЛОС
    initial_scale = target_head_height / bounds['face_height_with_hair']
    
    # Проверяем, поместится ли голова с таким масштабом
    scaled_head_height = bounds['face_height_with_hair'] * initial_scale
    scaled_head_width = (bounds['face_right'] - bounds['face_left']) * initial_scale
    
    # Добавляем запас 10% к размерам головы для безопасности
    if scaled_head_height * 1.1 > target_height or scaled_head_width * 1.1 > target_width:
        # Не поместится - уменьшаем масштаб
        scale_by_height = target_height / (bounds['face_height_with_hair'] * 1.1)
        scale_by_width = target_width / ((bounds['face_right'] - bounds['face_left']) * 1.1)
        scale_factor = min(scale_by_height, scale_by_width)
        logging.info(f"⚠️ Голова не помещается с минимальным размером, уменьшаем масштаб до {scale_factor:.3f}")
    else:
        scale_factor = initial_scale
        
    # Проверяем что голова не станет слишком большой
    if bounds['face_height_with_hair'] * scale_factor > max_head_height:
        scale_factor = max_head_height / bounds['face_height_with_hair']
        logging.info(f"⚠️ Ограничиваем масштаб максимальным размером головы: {scale_factor:.3f}")
    
    # Проверяем, что масштаб разумный
    min_scale = 0.5
    max_scale = 2.0
    
    if scale_factor < min_scale:
        logging.warning(f"Scale {scale_factor:.3f} слишком мал, используем {min_scale}")
        scale_factor = min_scale
    elif scale_factor > max_scale:
        logging.warning(f"Scale {scale_factor:.3f} слишком велик, используем {max_scale}")
        scale_factor = max_scale
    
    # Вычисляем финальный размер головы для диагностики
    final_head_height_px = bounds['face_height_with_hair'] * scale_factor
    final_head_height_mm = final_head_height_px / photo_spec.dpi * 25.4  # px to mm
    
    logging.info(f"📏 Масштабирование: {scale_factor:.3f}")
    logging.info(f"   Финальная высота головы: {final_head_height_px:.1f}px ({final_head_height_mm:.1f}mm)")
    logging.info(f"   Требуемый диапазон: {min_head_height}px-{max_head_height}px ({min_head_height/photo_spec.dpi*25.4:.1f}mm-{max_head_height/photo_spec.dpi*25.4:.1f}mm)")
    
    # ШАГ 2: Масштабируем все измерения
    scaled_head_top = bounds['head_top'] * scale_factor
    scaled_chin_bottom = bounds['chin_bottom'] * scale_factor
    scaled_eye_level = bounds['eye_level'] * scale_factor
    scaled_face_center_x = bounds['face_center_x'] * scale_factor
    scaled_face_height = bounds['face_height_with_hair'] * scale_factor
    
    # ШАГ 3: Позиционирование
    # Если есть требования к глазам - используем их
    if photo_spec.eye_min_from_bottom_px and photo_spec.eye_max_from_bottom_px:
        # Целевая позиция глаз - ЦЕНТР диапазона (безопасно)
        target_eye_from_bottom = (photo_spec.eye_min_from_bottom_px + photo_spec.eye_max_from_bottom_px) / 2
        target_eye_from_top = target_height - target_eye_from_bottom
        
        # Позиционируем по глазам
        crop_top = scaled_eye_level - target_eye_from_top
        
        # ВАЖНО: Проверяем, не обрезается ли голова
        head_margin_top = scaled_head_top - crop_top
        head_margin_bottom = (crop_top + target_height) - scaled_chin_bottom
        
        if head_margin_top < 10:  # Меньше 10px от края - опасно!
            # Сдвигаем вниз, чтобы голова поместилась
            needed_margin = 20  # Минимум 20px отступ сверху
            shift_down = needed_margin - head_margin_top
            crop_top = scaled_head_top - needed_margin
            
            # Проверяем, не выйдем ли мы за нижнюю границу
            new_eye_from_bottom = target_height - (scaled_eye_level - crop_top)
            if photo_spec.eye_min_from_bottom_px and new_eye_from_bottom < photo_spec.eye_min_from_bottom_px:
                # Компромисс: минимальный допустимый отступ
                crop_top = scaled_head_top - 10
                logging.warning(f"⚠️ Компромисс: минимальный отступ сверху 10px для соблюдения требований к глазам")
            else:
                logging.warning(f"Корректировка позиции для защиты головы, сдвиг вниз на {shift_down:.1f}px")
    else:
        # Нет требований к глазам - просто центрируем с хорошим отступом
        # Оставляем 10% высоты фото как отступ сверху
        top_margin = target_height * 0.10
        crop_top = scaled_head_top - top_margin
    
    # Вычисляем границы кропа
    crop_bottom = crop_top + target_height
    crop_left = scaled_face_center_x - (target_width / 2)
    crop_right = crop_left + target_width
    
    # ШАГ 4: Корректировка границ изображения
    scaled_img_height = img_height * scale_factor
    scaled_img_width = img_width * scale_factor
    
    # Вертикальная корректировка
    if crop_top < 0:
        # Сдвигаем вниз
        crop_bottom -= crop_top
        crop_top = 0
        logging.warning("Корректировка: сдвиг вниз из-за выхода за верх")
    
    if crop_bottom > scaled_img_height:
        # Сдвигаем вверх
        crop_top -= (crop_bottom - scaled_img_height)
        crop_bottom = scaled_img_height
        logging.warning("Корректировка: сдвиг вверх из-за выхода за низ")
    
    # Горизонтальная корректировка
    if crop_left < 0:
        crop_right -= crop_left
        crop_left = 0
    
    if crop_right > scaled_img_width:
        crop_left -= (crop_right - scaled_img_width)
        crop_right = scaled_img_width
    
    # ФИНАЛЬНАЯ ПРОВЕРКА
    final_head_position = scaled_head_top - crop_top
    final_chin_position = scaled_chin_bottom - crop_top
    final_eye_position = scaled_eye_level - crop_top
    final_eye_from_bottom = target_height - final_eye_position
    
    logging.info(f"📍 ФИНАЛЬНАЯ ПОЗИЦИЯ:")
    logging.info(f"   Голова от верха: {final_head_position:.1f}px ({final_head_position/target_height*100:.1f}%)")
    logging.info(f"   Подбородок: {final_chin_position:.1f}px")
    logging.info(f"   Глаза от низа: {final_eye_from_bottom:.1f}px")
    
    # Проверка успешности
    success = True
    warnings = []
    
    if final_head_position < 5:
        warnings.append("⚠️ Голова слишком близко к верхнему краю!")
        success = False
    
    if final_chin_position > target_height:
        warnings.append("⚠️ Подбородок обрезан!")
        success = False
    
    if photo_spec.eye_min_from_bottom_px and photo_spec.eye_max_from_bottom_px:
        if not (photo_spec.eye_min_from_bottom_px <= final_eye_from_bottom <= photo_spec.eye_max_from_bottom_px):
            warnings.append(f"⚠️ Глаза вне диапазона: {final_eye_from_bottom:.1f}px")
            # Это предупреждение, но не критическая ошибка
    
    if warnings:
        for w in warnings:
            logging.warning(w)
    else:
        logging.info("✅ Позиционирование успешно!")
    
    # Важная корректировка для achieved_head_height_px
    # Нужно учитывать реальную видимую высоту головы в финальном кропе
    visible_head_height = min(scaled_chin_bottom - crop_top, target_height) - max(scaled_head_top - crop_top, 0)
    
    return {
        'scale_factor': float(scale_factor),
        'crop_top': int(round(crop_top)),
        'crop_bottom': int(round(crop_bottom)),
        'crop_left': int(round(crop_left)),
        'crop_right': int(round(crop_right)),
        'final_photo_width_px': target_width,
        'final_photo_height_px': target_height,
        'achieved_head_height_px': int(round(visible_head_height)),
        'achieved_eye_level_from_top_px': int(round(final_eye_position)),
        'positioning_success': success,
        'warnings': warnings
    }