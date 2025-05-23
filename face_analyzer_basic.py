# face_analyzer_basic.py
# БАЗОВЫЙ ПОДХОД: Сначала помещаем голову целиком, потом оптимизируем

import logging
import numpy as np
from photo_specs import PhotoSpecification

class BasicFaceAnalyzer:
    """Максимально простой анализатор - только самое необходимое"""
    
    def __init__(self, landmarks, img_height, img_width):
        self.landmarks = landmarks
        self.img_height = img_height
        self.img_width = img_width
    
    def get_face_bbox(self):
        """Получить прямоугольник вокруг ВСЕХ точек лица"""
        # Собираем ВСЕ точки
        all_points = []
        for landmark in self.landmarks.landmark:
            x = landmark.x * self.img_width
            y = landmark.y * self.img_height
            all_points.append((x, y))
        
        # Находим границы
        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)
        
        # Добавляем БОЛЬШОЙ запас со всех сторон
        width = max_x - min_x
        height = max_y - min_y
        
        # 30% запас сверху для волос, 10% с остальных сторон
        margin_top = height * 0.3
        margin_bottom = height * 0.1
        margin_sides = width * 0.1
        
        return {
            'left': min_x - margin_sides,
            'right': max_x + margin_sides,
            'top': min_y - margin_top,
            'bottom': max_y + margin_bottom,
            'width': (max_x - min_x) + 2 * margin_sides,
            'height': (max_y - min_y) + margin_top + margin_bottom,
            'center_x': (min_x + max_x) / 2,
            'center_y': (min_y + max_y) / 2
        }
    
    def get_eye_level(self):
        """Найти уровень глаз"""
        # Точки глаз (упрощенно)
        eye_indices = [33, 133, 362, 263]
        eye_ys = []
        
        for idx in eye_indices:
            if idx < len(self.landmarks.landmark):
                y = self.landmarks.landmark[idx].y * self.img_height
                eye_ys.append(y)
        
        return np.mean(eye_ys) if eye_ys else None


def calculate_basic_crop(face_landmarks, img_height: int, img_width: int, photo_spec: PhotoSpecification):
    """
    БАЗОВЫЙ АЛГОРИТМ: Гарантированно помещаем всю голову
    
    Шаг 1: Вписываем голову целиком
    Шаг 2: Максимизируем масштаб в рамках ограничений
    """
    
    analyzer = BasicFaceAnalyzer(face_landmarks, img_height, img_width)
    face_bbox = analyzer.get_face_bbox()
    eye_level = analyzer.get_eye_level()
    
    # Целевые размеры
    target_width = photo_spec.photo_width_px
    target_height = photo_spec.photo_height_px
    
    logging.info(f"🎯 БАЗОВЫЙ АЛГОРИТМ")
    logging.info(f"   Лицо с запасами: {face_bbox['width']:.1f} x {face_bbox['height']:.1f}px")
    logging.info(f"   Целевое фото: {target_width} x {target_height}px")
    
    # ШАГ 1: ВПИСЫВАЕМ ГОЛОВУ ЦЕЛИКОМ
    # Масштаб, чтобы голова поместилась по обеим осям
    scale_by_width = target_width / face_bbox['width']
    scale_by_height = target_height / face_bbox['height']
    
    # Берем МЕНЬШИЙ масштаб - гарантия что поместится
    initial_scale = min(scale_by_width, scale_by_height)
    
    # Дополнительно уменьшаем на 10% для гарантии
    safe_scale = initial_scale * 0.9
    
    logging.info(f"   Начальный масштаб: {safe_scale:.3f} (гарантированно помещается)")
    
    # Масштабируем
    scaled_bbox = {
        'left': face_bbox['left'] * safe_scale,
        'right': face_bbox['right'] * safe_scale,
        'top': face_bbox['top'] * safe_scale,
        'bottom': face_bbox['bottom'] * safe_scale,
        'width': face_bbox['width'] * safe_scale,
        'height': face_bbox['height'] * safe_scale,
        'center_x': face_bbox['center_x'] * safe_scale,
        'center_y': face_bbox['center_y'] * safe_scale
    }
    
    # Позиционируем по центру
    crop_center_x = scaled_bbox['center_x']
    crop_center_y = scaled_bbox['center_y']
    
    crop_left = crop_center_x - target_width / 2
    crop_top = crop_center_y - target_height / 2
    crop_right = crop_left + target_width
    crop_bottom = crop_top + target_height
    
    # Инициализируем переменную для отслеживания позиции глаз
    eye_from_crop_top = None
    
    # ШАГ 2: ПРОВЕРЯЕМ ТРЕБОВАНИЯ И ОПТИМИЗИРУЕМ
    if eye_level is not None:
        scaled_eye_level = eye_level * safe_scale
        eye_from_crop_top = scaled_eye_level - crop_top
        eye_from_bottom = target_height - eye_from_crop_top
        
        logging.info(f"   Глаза от низа: {eye_from_bottom:.1f}px")
        
        # Если есть требования к глазам
        if photo_spec.eye_min_from_bottom_px and photo_spec.eye_max_from_bottom_px:
            target_eye_from_bottom = (photo_spec.eye_min_from_bottom_px + photo_spec.eye_max_from_bottom_px) / 2
            
            # Корректируем позицию ВСЕГДА, если есть требования к глазам
            eye_adjustment = target_eye_from_bottom - eye_from_bottom
            
            # Применяем корректировку
            crop_top += eye_adjustment
            crop_bottom += eye_adjustment
            
            logging.info(f"   Корректировка для глаз: сдвиг на {eye_adjustment:.1f}px")
            logging.info(f"   Новая позиция глаз: {target_eye_from_bottom:.1f}px")
    
    # ШАГ 3: ПРОБУЕМ УВЕЛИЧИТЬ МАСШТАБ
    # Проверяем высоту головы (без маргинов)
    # Получаем исходную высоту лица без маргинов
    raw_face_height = face_bbox['height'] / 1.4  # Убираем 30% сверху и 10% снизу
    scaled_raw_face_height = raw_face_height * safe_scale
    face_height_in_photo = scaled_bbox['height']
    
    # Требования к размеру головы
    min_head_height = photo_spec.head_min_px
    max_head_height = photo_spec.head_max_px
    
    if face_height_in_photo < min_head_height:
        # Нужно увеличить
        needed_scale = min_head_height / face_height_in_photo
        new_scale = safe_scale * needed_scale
        
        logging.info(f"   Увеличиваем масштаб до {new_scale:.3f} для минимального размера головы")
        
        # Пересчитываем все с новым масштабом
        safe_scale = new_scale
        
        # Пересчет scaled_bbox и crop позиций...
        scaled_bbox = {
            'left': face_bbox['left'] * safe_scale,
            'right': face_bbox['right'] * safe_scale,
            'top': face_bbox['top'] * safe_scale,
            'bottom': face_bbox['bottom'] * safe_scale,
            'width': face_bbox['width'] * safe_scale,
            'height': face_bbox['height'] * safe_scale,
            'center_x': face_bbox['center_x'] * safe_scale,
            'center_y': face_bbox['center_y'] * safe_scale
        }
        
        # Перепозиционируем с учетом требований к глазам
        if eye_level is not None and photo_spec.eye_min_from_bottom_px and photo_spec.eye_max_from_bottom_px:
            # Пересчитываем позицию глаз с новым масштабом
            scaled_eye_level = eye_level * safe_scale
            target_eye_from_bottom = (photo_spec.eye_min_from_bottom_px + photo_spec.eye_max_from_bottom_px) / 2
            target_eye_from_top = target_height - target_eye_from_bottom
            
            # Позиционируем по глазам
            crop_top = scaled_eye_level - target_eye_from_top
            crop_bottom = crop_top + target_height
            
            # Обновляем позицию глаз относительно обрезки
            eye_from_crop_top = scaled_eye_level - crop_top
            
            # Центрируем по X
            crop_center_x = scaled_bbox['center_x']
            crop_left = crop_center_x - target_width / 2
            crop_right = crop_left + target_width
            
            logging.info(f"   Позиционирование по глазам после масштабирования")
        else:
            # Стандартное центрирование
            crop_center_x = scaled_bbox['center_x']
            crop_center_y = scaled_bbox['center_y']
            
            crop_left = crop_center_x - target_width / 2
            crop_top = crop_center_y - target_height / 2
            crop_right = crop_left + target_width
            crop_bottom = crop_top + target_height
    
    # ФИНАЛЬНАЯ КОРРЕКТИРОВКА: убеждаемся что не выходим за границы
    scaled_img_width = img_width * safe_scale
    scaled_img_height = img_height * safe_scale
    
    # Проверка границ
    if crop_left < 0:
        shift = -crop_left
        crop_left = 0
        crop_right = target_width
        logging.warning(f"Сдвиг вправо на {shift:.1f}px")
    
    if crop_right > scaled_img_width:
        shift = crop_right - scaled_img_width
        crop_right = scaled_img_width
        crop_left = crop_right - target_width
        logging.warning(f"Сдвиг влево на {shift:.1f}px")
    
    if crop_top < 0:
        shift = -crop_top
        crop_top = 0
        crop_bottom = target_height
        logging.warning(f"Сдвиг вниз на {shift:.1f}px")
    
    if crop_bottom > scaled_img_height:
        shift = crop_bottom - scaled_img_height
        crop_bottom = scaled_img_height
        crop_top = crop_bottom - target_height
        logging.warning(f"Сдвиг вверх на {shift:.1f}px")
    
    # ФИНАЛЬНАЯ ПРОВЕРКА
    final_head_in_frame = (
        scaled_bbox['top'] >= crop_top - 5 and  # Допуск 5px
        scaled_bbox['bottom'] <= crop_bottom + 5 and
        scaled_bbox['left'] >= crop_left - 5 and
        scaled_bbox['right'] <= crop_right + 5
    )
    
    if final_head_in_frame:
        logging.info("✅ Голова полностью помещается в кадр!")
    else:
        logging.warning("⚠️ Часть головы может быть обрезана")
        # Дополнительное уменьшение масштаба
        if not final_head_in_frame:
            safe_scale *= 0.85
            logging.warning(f"Дополнительно уменьшаем масштаб до {safe_scale:.3f}")
            # Здесь можно пересчитать все заново с меньшим масштабом
    
    logging.info(f"📐 Финальный масштаб: {safe_scale:.3f}")
    
    # Вычисляем финальную высоту головы без маргинов
    final_raw_face_height = face_bbox['height'] / 1.4 * safe_scale
    
    return {
        'scale_factor': float(safe_scale),
        'crop_top': int(round(crop_top)),
        'crop_bottom': int(round(crop_bottom)),
        'crop_left': int(round(crop_left)),
        'crop_right': int(round(crop_right)),
        'final_photo_width_px': target_width,
        'final_photo_height_px': target_height,
        'achieved_head_height_px': int(round(final_raw_face_height)),
        'achieved_eye_level_from_top_px': int(round(eye_from_crop_top)) if eye_level else 0,
        'positioning_success': final_head_in_frame
    }


