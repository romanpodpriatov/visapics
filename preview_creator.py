# preview_creator.py

import os
import math
import logging
from PIL import Image, ImageDraw, ImageFont

from face_analyzer import FaceAnalyzer
from utils import PIXELS_PER_INCH

def create_preview_with_watermark(image_path, preview_path, crop_data, face_landmarks, fonts_folder):
    """
    Создание превью с водяным знаком и измерительными линиями.
    """
    img = Image.open(image_path)
    img_width, img_height = img.size

    # Отступы
    margin_top = int(img_height * 0.2)
    margin_bottom = int(img_height * 0.2)
    margin_left = int(img_width * 0.2)
    margin_right = int(img_width * 0.2)

    # Создание холста
    canvas_width = img_width + margin_left + margin_right
    canvas_height = img_height + margin_top + margin_bottom
    preview = Image.new('RGBA', (canvas_width, canvas_height), 'white')

    # Вставка изображения
    preview.paste(img, (margin_left, margin_top))

    draw_preview = ImageDraw.Draw(preview)

    # Загрузка шрифтов
    try:
        arial_font_path = os.path.join(fonts_folder, 'Arial.ttf')
        logging.info(f"Loaded font from {arial_font_path}")
        watermark_font_size = int(canvas_width * 0.05)
        watermark_font = ImageFont.truetype(arial_font_path, watermark_font_size)
        measurement_font_size = int(canvas_width * 0.03)
        measurement_font = ImageFont.truetype(arial_font_path, measurement_font_size)
    except IOError:
        logging.warning("Arial font not found. Using default font.")
        watermark_font = ImageFont.load_default()
        measurement_font = ImageFont.load_default()
        watermark_font_size = 50
        measurement_font_size = 25   

    # Добавление водяных знаков
    watermark_text = "PREVIEW"
    watermark_opacity = 128

    # Позиции водяных знаков
    watermark_positions = [
        (canvas_width * 0.25, canvas_height * 0.33),
        (canvas_width * 0.75, canvas_height * 0.33),
        (canvas_width * 0.5, canvas_height * 0.5),
        (canvas_width * 0.25, canvas_height * 0.67),
        (canvas_width * 0.75, canvas_height * 0.67),
        (canvas_width * 0.5, canvas_height * 0.8)
    ]

    # Создание слоя для водяных знаков
    watermark_overlay = Image.new('RGBA', preview.size, (255, 255, 255, 0))
    watermark_draw = ImageDraw.Draw(watermark_overlay)

    for pos in watermark_positions:
        x, y = pos
        watermark_draw.text(
            (x, y),
            watermark_text,
            fill=(0, 0, 0, watermark_opacity),
            font=watermark_font,
            anchor='mm'
        )

    # Наложение водяных знаков
    preview = Image.alpha_composite(preview, watermark_overlay)

    # Обновление контекста рисования
    draw_preview = ImageDraw.Draw(preview)

    # Измерения
    analyzer = FaceAnalyzer(face_landmarks, img_height, img_width)
    head_top, chin_bottom, eye_level, _ = analyzer.get_head_measurements()

    head_top_y = int(head_top) + margin_top
    chin_bottom_y = int(chin_bottom) + margin_top
    eye_y = int(eye_level) + margin_top

    # Преобразование в дюймы
    head_height_pixels = chin_bottom_y - head_top_y - margin_top
    head_height_inches = head_height_pixels / PIXELS_PER_INCH
    eye_to_bottom_pixels = (img_height + margin_top) - eye_y
    eye_to_bottom_inches = eye_to_bottom_pixels / PIXELS_PER_INCH

    # Линии и текст
    line_color = (0, 0, 0, 255)
    line_width = 2
    arrow_size = 10

    # Функции для рисования стрелок и измерений опущены для краткости

    # Сохранение превью
    preview = preview.convert('RGB')
    preview.save(preview_path, quality=95)
    logging.info(f"Preview saved at {preview_path}")