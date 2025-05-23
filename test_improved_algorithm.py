#!/usr/bin/env python3
"""Тест улучшенного алгоритма позиционирования головы"""

import os
import cv2
import numpy as np
import logging
from face_analyzer_basic import calculate_basic_crop as calculate_crop_dimensions
from photo_specs import get_photo_specification
import mediapipe as mp

# Включить детальное логирование
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def test_improved_positioning():
    """Тест улучшенного алгоритма с IMG_5520"""
    print("🧪 ТЕСТИРОВАНИЕ УЛУЧШЕННОГО АЛГОРИТМА ПОЗИЦИОНИРОВАНИЯ")
    print("="*70)
    
    image_path = "tests/IMG_5520.JPG"
    if not os.path.exists(image_path):
        print("❌ Тестовый файл не найден")
        return
    
    # Получить спецификацию
    spec = get_photo_specification("US", "Visa Lottery")
    if not spec:
        print("❌ Спецификация не найдена")
        return
    
    print(f"📋 Спецификация: {spec.country_code} {spec.document_name}")
    print(f"📏 Требования к голове: {spec.head_min_mm}-{spec.head_max_mm}мм")
    print(f"👁️  Требования к глазам: {spec.eye_min_from_bottom_mm}-{spec.eye_max_from_bottom_mm}мм от низа")
    print(f"🎯 Целевые размеры: {spec.photo_width_px}x{spec.photo_height_px}px")
    
    # Загрузить изображение
    img = cv2.imread(image_path)
    img_height, img_width = img.shape[:2]
    print(f"📐 Исходное изображение: {img_width}x{img_height}px")
    
    # Получить landmarks
    face_mesh = mp.solutions.face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(img_rgb)
    
    if not results.multi_face_landmarks:
        print("❌ Лицо не обнаружено")
        return
    
    face_landmarks = results.multi_face_landmarks[0]
    
    # Тестируем улучшенный алгоритм
    print(f"\n🔧 РАСЧЕТ ОБРЕЗКИ С УЛУЧШЕННЫМ АЛГОРИТМОМ...")
    try:
        crop_data = calculate_crop_dimensions(face_landmarks, img_height, img_width, spec)
        
        print(f"\n📊 РЕЗУЛЬТАТЫ РАСЧЕТА:")
        print(f"   Масштаб: {crop_data['scale_factor']:.3f}")
        print(f"   Область обрезки: top={crop_data['crop_top']}, bottom={crop_data['crop_bottom']}")
        print(f"   Область обрезки: left={crop_data['crop_left']}, right={crop_data['crop_right']}")
        print(f"   Достигнутая высота головы: {crop_data['achieved_head_height_px']}px")
        
        # Конвертация в мм
        mm_per_pixel = spec.photo_height_mm / spec.photo_height_px
        achieved_head_mm = crop_data['achieved_head_height_px'] * mm_per_pixel
        achieved_eye_mm = (spec.photo_height_px - crop_data['achieved_eye_level_from_top_px']) * mm_per_pixel
        
        print(f"\n📏 ИЗМЕРЕНИЯ В ММ:")
        print(f"   Высота головы: {achieved_head_mm:.1f}мм (требование: {spec.head_min_mm}-{spec.head_max_mm}мм)")
        print(f"   Глаза от низа: {achieved_eye_mm:.1f}мм (требование: {spec.eye_min_from_bottom_mm}-{spec.eye_max_from_bottom_mm}мм)")
        
        # Проверка соответствия
        head_compliant = spec.head_min_mm <= achieved_head_mm <= spec.head_max_mm
        eye_compliant = spec.eye_min_from_bottom_mm <= achieved_eye_mm <= spec.eye_max_from_bottom_mm
        
        print(f"\n✅❌ СООТВЕТСТВИЕ:")
        print(f"   Высота головы: {'✅' if head_compliant else '❌'}")
        print(f"   Позиция глаз: {'✅' if eye_compliant else '❌'}")
        
        # Симуляция обрезки для проверки отступов
        scale_factor = crop_data['scale_factor']
        scaled_height = int(img_height * scale_factor)
        scaled_width = int(img_width * scale_factor)
        
        # Рассчитать позицию головы в обрезанном изображении
        # Нужно получить исходные позиции головы
        forehead_points = [10, 151, 9, 8, 7]
        chin_points = [175, 18, 175, 200, 199]
        
        forehead_y = min([face_landmarks.landmark[i].y * img_height for i in forehead_points])
        chin_y = max([face_landmarks.landmark[i].y * img_height for i in chin_points])
        
        # Масштабированные позиции
        scaled_forehead_y = forehead_y * scale_factor
        scaled_chin_y = chin_y * scale_factor
        
        # Позиции в обрезанном изображении
        head_top_in_crop = scaled_forehead_y - crop_data['crop_top']
        head_bottom_in_crop = scaled_chin_y - crop_data['crop_top']
        
        # Отступы в мм
        top_margin_mm = head_top_in_crop * mm_per_pixel
        bottom_margin_mm = (spec.photo_height_px - head_bottom_in_crop) * mm_per_pixel
        
        print(f"\n📐 ОТСТУПЫ:")
        print(f"   От верха: {top_margin_mm:.1f}мм (рекомендуется: 2.0-6.0мм)")
        print(f"   От низа: {bottom_margin_mm:.1f}мм")
        
        # Проверка отступов
        margin_ok = 2.0 <= top_margin_mm <= 6.0
        print(f"   Отступ сверху: {'✅' if margin_ok else '❌'}")
        
        if not margin_ok:
            if top_margin_mm < 2.0:
                print("   ⚠️  Отступ слишком маленький - голова может быть обрезана")
            else:
                print("   ⚠️  Отступ слишком большой - неэффективное использование пространства")
        
        print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ:")
        all_compliant = head_compliant and eye_compliant and margin_ok
        print(f"   Все требования выполнены: {'✅' if all_compliant else '❌'}")
        
        return crop_data
        
    except Exception as e:
        print(f"❌ Ошибка в расчете: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_improved_positioning()