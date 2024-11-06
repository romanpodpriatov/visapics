# face_analyzer.py

import math
import logging
from utils import PIXELS_PER_INCH, PHOTO_SIZE_PIXELS

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

def calculate_crop_dimensions(face_landmarks, img_height, img_width):
    analyzer = FaceAnalyzer(face_landmarks, img_height, img_width)
    head_top, chin_bottom, eye_level, face_center_x = analyzer.get_head_measurements()

    head_height_pixels = chin_bottom - head_top
    head_height_inches = head_height_pixels / PIXELS_PER_INCH

    # Коэффициенты масштабирования
    min_head_height_inches = 1.0
    max_head_height_inches = 1.375
    min_head_height_pixels = min_head_height_inches * PIXELS_PER_INCH
    max_head_height_pixels = max_head_height_inches * PIXELS_PER_INCH

    scale_lower_bound = min_head_height_pixels / head_height_pixels
    scale_upper_bound = max_head_height_pixels / head_height_pixels

    # Определение масштаба
    scale_width = PHOTO_SIZE_PIXELS / img_width
    scale_height = PHOTO_SIZE_PIXELS / img_height
    scale = min(scale_width, scale_height, scale_upper_bound)
    scale = max(scale, scale_lower_bound)

    logging.debug(f"Scale bounds: lower={scale_lower_bound}, upper={scale_upper_bound}, chosen scale={scale}")

    scaled_face_center_x = int(face_center_x * scale)
    scaled_width = int(img_width * scale)
    scaled_height = int(img_height * scale)

    scaled_chin_bottom = int(chin_bottom * scale)

    # Размеры обрезки
    crop_bottom = scaled_chin_bottom + int(PHOTO_SIZE_PIXELS * 0.25)
    crop_top = crop_bottom - PHOTO_SIZE_PIXELS
    crop_left = scaled_face_center_x - (PHOTO_SIZE_PIXELS // 2)
    crop_right = crop_left + PHOTO_SIZE_PIXELS

    # Корректировки
    if crop_left < 0:
        crop_left = 0
        crop_right = PHOTO_SIZE_PIXELS
    elif crop_right > scaled_width:
        crop_right = scaled_width
        crop_left = scaled_width - PHOTO_SIZE_PIXELS

    if crop_top < 0:
        crop_top = 0
        crop_bottom = PHOTO_SIZE_PIXELS
    elif crop_bottom > scaled_height:
        crop_bottom = scaled_height
        crop_top = scaled_height - PHOTO_SIZE_PIXELS

    final_head_height = (head_height_pixels * scale) / PIXELS_PER_INCH
    eye_to_bottom = (PHOTO_SIZE_PIXELS - (int(eye_level * scale) - crop_top)) / PIXELS_PER_INCH

    crop_data = {
        'scale_factor': float(scale),
        'crop_top': int(crop_top),
        'crop_bottom': int(crop_bottom),
        'crop_left': int(crop_left),
        'crop_right': int(crop_right),
        'eye_level': int(int(eye_level * scale) - crop_top),
        'head_height': float(final_head_height),
        'eye_to_bottom': float(eye_to_bottom)
    }

    logging.debug(f"Crop Data: {crop_data}")

    return crop_data