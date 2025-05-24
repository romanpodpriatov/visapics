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
        
        # ИСПРАВЛЕНО: Landmark 10 уже включает волосы (это физический верх головы)
        # Поэтому не добавляем дополнительный hair_margin
        # Только для случаев, когда forehead_top может быть линией роста волос
        forehead_skin_landmarks = [151, 9]  # Исключаем landmark 10
        forehead_skin_points = []
        for idx in forehead_skin_landmarks:
            if idx < len(self.landmarks.landmark):
                y = self.landmarks.landmark[idx].y * self.img_height
                forehead_skin_points.append(y)
        
        if forehead_skin_points:
            forehead_skin_top = min(forehead_skin_points)
            # Landmark 10 vs forehead skin - выбираем минимум (физический верх)
            actual_head_top = min(forehead_top, forehead_skin_top)
            # Если landmark 10 существенно выше линии лба, то это уже включает волосы
            if forehead_top < forehead_skin_top - 20:  # 20px разница
                hair_margin = 0  # Landmark 10 уже включает волосы
                estimated_head_top = forehead_top
            else:
                # Если разница небольшая, добавляем небольшой запас
                face_height = face_bottom - forehead_skin_top
                hair_margin = face_height * 0.10  # Только 10% запас
                estimated_head_top = forehead_top - hair_margin
        else:
            # Fallback - используем все точки
            hair_margin = 0  # Landmark 10 уже на макушке
            estimated_head_top = forehead_top
        
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
    УЛУЧШЕННЫЙ АЛГОРИТМ: Более робастное масштабирование и позиционирование.
    
    Принципы:
    1. Масштабирование для соответствия требованиям к размеру головы.
    2. Приоритетное позиционирование (спецификация > глаза > по умолчанию).
    3. Гарантия, что голова не обрезана и есть минимальные отступы.
    4. Подробное логирование для диагностики.
    """
    
    # Предполагается, что SimpleFaceAnalyzer.get_face_bounds() возвращает КОРРЕКТНЫЕ
    # bounds['head_top'] (физический верх головы) и 
    # bounds['face_height_with_hair'] (физическая высота головы).
    analyzer = SimpleFaceAnalyzer(face_landmarks, img_height, img_width)
    bounds = analyzer.get_face_bounds()
    
    logging.info(f"🎯 УЛУЧШЕННЫЙ АЛГОРИТМ - Исходные границы лица (до масштабирования):")
    logging.info(f"   Верх головы (head_top): {bounds['head_top']:.1f}px")
    logging.info(f"   Низ подбородка (chin_bottom): {bounds['chin_bottom']:.1f}px")
    logging.info(f"   Высота лица с волосами (face_height_with_hair): {bounds['face_height_with_hair']:.1f}px")
    logging.info(f"   Видимая высота лица (face_height_visible): {bounds['face_height_visible']:.1f}px")
    logging.info(f"   Центр лица X: {bounds['face_center_x']:.1f}px")
    logging.info(f"   Уровень глаз: {bounds['eye_level']:.1f}px")

    target_width = photo_spec.photo_width_px
    target_height = photo_spec.photo_height_px

    # ШАГ 1: ОПРЕДЕЛЕНИЕ МАСШТАБА
    # Цель: голова должна быть в диапазоне [head_min_px, head_max_px]
    # и умещаться в кадр.

    if bounds['face_height_with_hair'] <= 0: # Предотвращение деления на ноль
        logging.error("Ошибка: Высота головы с волосами равна нулю или отрицательна. Невозможно рассчитать масштаб.")
        # Возвращаем "неудачный" результат или вызываем исключение
        return {
            'scale_factor': 0, 'crop_top': 0, 'crop_bottom': target_height, 
            'crop_left': 0, 'crop_right': target_width,
            'final_photo_width_px': target_width, 'final_photo_height_px': target_height,
            'achieved_head_height_px': 0, 'achieved_eye_level_from_top_px': 0,
            'positioning_success': False, 'warnings': ["Критическая ошибка: некорректная высота головы."]
        }

    # Попытка нацелиться на середину допустимого диапазона размера головы
    ideal_target_head_photo_px = (photo_spec.head_min_px + photo_spec.head_max_px) / 2.0
    # Ограничиваем целью в рамках спецификации
    target_head_photo_px = max(photo_spec.head_min_px, min(ideal_target_head_photo_px, photo_spec.head_max_px))
    
    scale_factor = target_head_photo_px / bounds['face_height_with_hair']
    logging.info(f"   Начальный масштаб для целевого размера головы ({target_head_photo_px:.1f}px): {scale_factor:.3f}")

    # Проверка, не слишком ли широким становится лицо
    face_pixel_width = bounds['face_right'] - bounds['face_left']
    if face_pixel_width * scale_factor > target_width * 0.98: # Оставляем мин 1% отступа с каждой стороны
        new_scale_factor = (target_width * 0.98) / face_pixel_width
        logging.info(f"   Масштаб уменьшен с {scale_factor:.3f} до {new_scale_factor:.3f} чтобы лицо поместилось по ширине.")
        scale_factor = new_scale_factor

    # Проверка, не слишком ли высокой становится голова для самой фотографии
    if bounds['face_height_with_hair'] * scale_factor > target_height * 0.98: # Оставляем мин 1% отступа сверху/снизу для всей головы
        new_scale_factor = (target_height * 0.98) / bounds['face_height_with_hair']
        logging.info(f"   Масштаб уменьшен с {scale_factor:.3f} до {new_scale_factor:.3f} чтобы голова поместилась по высоте фото.")
        scale_factor = new_scale_factor
        
    # Финальная коррекция масштаба, чтобы голова точно соответствовала min/max требованиям
    current_scaled_head_height = bounds['face_height_with_hair'] * scale_factor
    if current_scaled_head_height < photo_spec.head_min_px:
        logging.warning(f"   Масштаб {scale_factor:.3f} дает слишком маленькую голову ({current_scaled_head_height:.1f}px). Увеличиваем до min ({photo_spec.head_min_px}px).")
        scale_factor = photo_spec.head_min_px / bounds['face_height_with_hair']
    elif current_scaled_head_height > photo_spec.head_max_px:
        logging.warning(f"   Масштаб {scale_factor:.3f} дает слишком большую голову ({current_scaled_head_height:.1f}px). Уменьшаем до max ({photo_spec.head_max_px}px).")
        scale_factor = photo_spec.head_max_px / bounds['face_height_with_hair']

    # Ограничение на минимальный и максимальный масштаб
    min_allowed_scale, max_allowed_scale = 0.25, 3.0 # Более широкий диапазон, если необходимо
    if scale_factor < min_allowed_scale:
        logging.warning(f"   Итоговый масштаб {scale_factor:.3f} слишком мал, используем {min_allowed_scale}.")
        scale_factor = min_allowed_scale
    elif scale_factor > max_allowed_scale:
        logging.warning(f"   Итоговый масштаб {scale_factor:.3f} слишком велик, используем {max_allowed_scale}.")
        scale_factor = max_allowed_scale
    
    final_head_height_px = bounds['face_height_with_hair'] * scale_factor
    final_head_height_mm = final_head_height_px / photo_spec.dpi * 25.4
    
    logging.info(f"📏 Масштабирование: {scale_factor:.3f}")
    logging.info(f"   Финальная расчетная высота головы: {final_head_height_px:.1f}px ({final_head_height_mm:.1f}mm)")
    logging.info(f"   Требуемый диапазон: {photo_spec.head_min_px}px-{photo_spec.head_max_px}px ({photo_spec.head_min_px/photo_spec.dpi*25.4:.1f}mm-{photo_spec.head_max_px/photo_spec.dpi*25.4:.1f}mm)")

    # ШАГ 2: МАСШТАБИРОВАНИЕ КООРДИНАТ
    scaled_head_top = bounds['head_top'] * scale_factor
    scaled_chin_bottom = bounds['chin_bottom'] * scale_factor
    scaled_eye_level = bounds['eye_level'] * scale_factor
    scaled_face_center_x = bounds['face_center_x'] * scale_factor

    # ШАГ 3: ПОЗИЦИОНИРОВАНИЕ (ВЕРТИКАЛЬНОЕ)
    crop_top_y = 0 # Y-координата верхнего края кадрирования относительно масштабированного изображения

    # Минимальные визуальные отступы
    min_head_margin_px = getattr(photo_spec, 'min_visual_head_margin_px', 5)
    min_chin_margin_px = getattr(photo_spec, 'min_visual_chin_margin_px', 5)

    # Приоритеты позиционирования:
    # 1. Спецификация по положению верха головы (head_top_dist_from_photo_top)
    # 2. Спецификация по уровню глаз (eye_level_from_bottom)
    # 3. Позиционирование по умолчанию

    positioned_by = "не определено"

    if hasattr(photo_spec, 'head_top_min_dist_from_photo_top_px') and \
       hasattr(photo_spec, 'head_top_max_dist_from_photo_top_px') and \
       photo_spec.head_top_min_dist_from_photo_top_px is not None and \
       photo_spec.head_top_max_dist_from_photo_top_px is not None:
        # Цель - середина диапазона отступа верха головы от верха фото
        target_head_dist_from_top = (photo_spec.head_top_min_dist_from_photo_top_px + 
                                     photo_spec.head_top_max_dist_from_photo_top_px) / 2.0
        crop_top_y = scaled_head_top - target_head_dist_from_top
        positioned_by = f"спец. отступу верха головы ({target_head_dist_from_top:.1f}px)"
        logging.info(f"   Позиционирование по {positioned_by}.")
    
    elif photo_spec.eye_min_from_bottom_px is not None and \
         photo_spec.eye_max_from_bottom_px is not None:
        # Цель - середина диапазона уровня глаз от низа фото
        target_eye_from_bottom = (photo_spec.eye_min_from_bottom_px + photo_spec.eye_max_from_bottom_px) / 2.0
        target_eye_from_top_photo = target_height - target_eye_from_bottom
        crop_top_y = scaled_eye_level - target_eye_from_top_photo
        positioned_by = f"уровню глаз ({target_eye_from_bottom:.1f}px от низа)"
        logging.info(f"   Позиционирование по {positioned_by}.")

    else:
        # Позиционирование по умолчанию: отступ сверху
        default_head_top_margin_percent = getattr(photo_spec, 'default_head_top_margin_percent', 0.12)
        default_top_margin = target_height * default_head_top_margin_percent
        effective_top_margin = max(min_head_margin_px, default_top_margin)
        crop_top_y = scaled_head_top - effective_top_margin
        positioned_by = f"отступу по умолчанию ({effective_top_margin:.1f}px сверху)"
        logging.info(f"   Позиционирование по {positioned_by}.")

    # Коррекция crop_top_y, чтобы гарантировать видимость головы
    # Проверка верха головы
    if scaled_head_top - crop_top_y < min_head_margin_px:
        new_crop_top_y = scaled_head_top - min_head_margin_px
        logging.warning(f"   Коррекция верха: crop_top_y изменен с {crop_top_y:.1f} на {new_crop_top_y:.1f} для обеспечения мин. отступа головы ({min_head_margin_px}px). Исходный метод: {positioned_by}.")
        crop_top_y = new_crop_top_y
        positioned_by += " + коррекция верха головы"

    # Проверка низа подбородка
    if (scaled_chin_bottom - crop_top_y) > (target_height - min_chin_margin_px):
        new_crop_top_y = scaled_chin_bottom - (target_height - min_chin_margin_px)
        # Эта коррекция может поднять голову слишком высоко. Проверим это.
        if scaled_head_top - new_crop_top_y < min_head_margin_px:
            # Конфликт: не можем удовлетворить и отступ подбородка, и отступ головы.
            # Приоритет - не обрезать голову сверху.
            crop_top_y_alt = scaled_head_top - min_head_margin_px
            logging.warning(f"   Конфликт отступов! Попытка сдвинуть crop_top_y для подбородка ({new_crop_top_y:.1f}) нарушает верхний отступ головы. "
                            f"Приоритет у верхнего отступа. crop_top_y остается {crop_top_y_alt:.1f}.")
            crop_top_y = scaled_head_top - min_head_margin_px # Переустановка для безопасности верха
            if (scaled_chin_bottom - crop_top_y) > (target_height - min_chin_margin_px):
                 logging.warning(f"   Подбородок может быть слишком близко к нижнему краю или обрезан из-за конфликта отступов.")
            positioned_by += " + конфликт с подбородком"

        else: # Коррекция для подбородка возможна
            logging.warning(f"   Коррекция низа: crop_top_y изменен с {crop_top_y:.1f} на {new_crop_top_y:.1f} для обеспечения мин. отступа подбородка ({min_chin_margin_px}px). Исходный метод: {positioned_by}.")
            crop_top_y = new_crop_top_y
            positioned_by += " + коррекция низа подбородка"

    # Горизонтальное центрирование
    crop_left_x = scaled_face_center_x - (target_width / 2)

    # ШАГ 4: КОРРЕКТИРОВКА ГРАНИЦ ОТНОСИТЕЛЬНО МАСШТАБИРОВАННОГО ИЗОБРАЖЕНИЯ
    scaled_img_height = img_height * scale_factor
    scaled_img_width = img_width * scale_factor
    
    # Вертикальная корректировка (если кроп выходит за пределы масштабированного изображения)
    if crop_top_y < 0:
        logging.warning(f"   Коррекция выхода за ВЕРХ: crop_top_y был {crop_top_y:.1f}, стал 0.")
        crop_top_y = 0
    if crop_top_y + target_height > scaled_img_height:
        new_top = scaled_img_height - target_height
        logging.warning(f"   Коррекция выхода за НИЗ: crop_top_y был {crop_top_y:.1f}, стал {new_top:.1f}.")
        crop_top_y = new_top
        if crop_top_y < 0 : # Если фото меньше чем crop_height, фото будет спозиционировано вверху
             logging.warning(f"   Фото меньше чем высота кадрирования, crop_top_y установлен в 0 после коррекции выхода за НИЗ.")
             crop_top_y = 0

    # Горизонтальная корректировка
    if crop_left_x < 0:
        logging.warning(f"   Коррекция выхода за ЛЕВЫЙ КРАЙ: crop_left_x был {crop_left_x:.1f}, стал 0.")
        crop_left_x = 0
    if crop_left_x + target_width > scaled_img_width:
        new_left = scaled_img_width - target_width
        logging.warning(f"   Коррекция выхода за ПРАВЫЙ КРАЙ: crop_left_x был {crop_left_x:.1f}, стал {new_left:.1f}.")
        crop_left_x = new_left
        if crop_left_x < 0: # Если фото меньше чем crop_width
            logging.warning(f"   Фото меньше чем ширина кадрирования, crop_left_x установлен в 0 после коррекции выхода за ПРАВЫЙ КРАЙ.")
            crop_left_x = 0

    crop_bottom_y = crop_top_y + target_height
    crop_right_x = crop_left_x + target_width

    # ШАГ 5: ФИНАЛЬНАЯ ПРОВЕРКА И РЕЗУЛЬТАТЫ
    # Позиции элементов лица относительно ВЕРХНЕГО КРАЯ КАДРА (crop_top_y)
    final_head_pos_from_crop_top = scaled_head_top - crop_top_y
    final_chin_pos_from_crop_top = scaled_chin_bottom - crop_top_y
    final_eye_pos_from_crop_top = scaled_eye_level - crop_top_y
    
    final_eye_pos_from_bottom_crop = target_height - final_eye_pos_from_crop_top
    
    # Реальная видимая высота головы в кадре
    visible_head_top_in_crop = max(0, final_head_pos_from_crop_top)
    visible_chin_bottom_in_crop = min(target_height, final_chin_pos_from_crop_top)
    achieved_head_height_px = max(0, visible_chin_bottom_in_crop - visible_head_top_in_crop)

    logging.info(f"📍 ФИНАЛЬНАЯ ПОЗИЦИЯ (относительно кадра):")
    logging.info(f"   Верх головы от верха кадра: {final_head_pos_from_crop_top:.1f}px ({final_head_pos_from_crop_top/target_height*100:.1f}%)")
    logging.info(f"   Подбородок от верха кадра: {final_chin_pos_from_crop_top:.1f}px")
    logging.info(f"   Глаза от верха кадра: {final_eye_pos_from_crop_top:.1f}px")
    logging.info(f"   Глаза от низа кадра: {final_eye_pos_from_bottom_crop:.1f}px")
    logging.info(f"   Достигнутая видимая высота головы в кадре: {achieved_head_height_px:.1f}px")

    success = True
    warnings = []

    # Проверка отступов
    if final_head_pos_from_crop_top < min_head_margin_px - 0.5: # -0.5 для учета округления
        warnings.append(f"⚠️ Голова слишком близко к верхнему краю ({final_head_pos_from_crop_top:.1f}px < {min_head_margin_px}px)!")
    
    if final_chin_pos_from_crop_top > target_height - (min_chin_margin_px - 0.5):
        warnings.append(f"⚠️ Подбородок слишком близко к нижнему краю или обрезан ({final_chin_pos_from_crop_top:.1f}px в кадре высотой {target_height}px)!")
        success = False
    
    if final_chin_pos_from_crop_top <= visible_head_top_in_crop : # подбородок выше макушки или они совпадают
        warnings.append(f"⚠️ Подбородок обрезан полностью или ошибка в определении головы!")
        success = False

    # Проверка размера головы
    if not (photo_spec.head_min_px <= achieved_head_height_px <= photo_spec.head_max_px):
        warnings.append(f"⚠️ Финальный размер головы ({achieved_head_height_px:.1f}px) вне диапазона ({photo_spec.head_min_px}-{photo_spec.head_max_px}px).")

    # Проверка положения глаз
    if photo_spec.eye_min_from_bottom_px and photo_spec.eye_max_from_bottom_px:
        if not (photo_spec.eye_min_from_bottom_px <= final_eye_pos_from_bottom_crop <= photo_spec.eye_max_from_bottom_px):
            warnings.append(f"⚠️ Глаза ({final_eye_pos_from_bottom_crop:.1f}px) вне диапазона от низа ({photo_spec.eye_min_from_bottom_px}-{photo_spec.eye_max_from_bottom_px}px).")

    # Проверка положения верха головы (если задано)
    if hasattr(photo_spec, 'head_top_min_dist_from_photo_top_px') and \
       hasattr(photo_spec, 'head_top_max_dist_from_photo_top_px') and \
       photo_spec.head_top_min_dist_from_photo_top_px is not None and \
       photo_spec.head_top_max_dist_from_photo_top_px is not None:
        if not (photo_spec.head_top_min_dist_from_photo_top_px <= final_head_pos_from_crop_top <= photo_spec.head_top_max_dist_from_photo_top_px):
            warnings.append(f"⚠️ Верх головы ({final_head_pos_from_crop_top:.1f}px) вне диапазона от верха фото ({photo_spec.head_top_min_dist_from_photo_top_px}-{photo_spec.head_top_max_dist_from_photo_top_px}px).")

    # Определяем общий успех на основе наиболее критичных моментов
    if not (photo_spec.head_min_px <= achieved_head_height_px <= photo_spec.head_max_px) or \
       final_chin_pos_from_crop_top > target_height + 1 or \
       final_head_pos_from_crop_top < -1 : # +1/-1 пиксель на погрешность обрезки
        success = False

    if warnings:
        logging.warning("Обнаружены следующие проблемы:")
        for w in warnings:
            logging.warning(f"   {w}")
    if success:
        logging.info("✅ Позиционирование успешно!")
    else:
        logging.error("❌ Позиционирование НЕ успешно из-за критических нарушений.")

    return {
        'scale_factor': float(scale_factor),
        'crop_top': int(round(crop_top_y)),
        'crop_bottom': int(round(crop_bottom_y)),
        'crop_left': int(round(crop_left_x)),
        'crop_right': int(round(crop_right_x)),
        'final_photo_width_px': target_width,
        'final_photo_height_px': target_height,
        'achieved_head_height_px': int(round(achieved_head_height_px)),
        'achieved_eye_level_from_top_px': int(round(final_eye_pos_from_crop_top)), # От верха кадра
        'achieved_eye_level_from_bottom_px': int(round(final_eye_pos_from_bottom_crop)), # От низа кадра
        'achieved_head_top_from_crop_top_px': int(round(final_head_pos_from_crop_top)), # От верха кадра
        'positioning_success': success,
        'warnings': warnings
    }