# printable_creator.py

import os
import logging
from PIL import Image, ImageDraw, ImageFont

from utils import PIXELS_PER_INCH

def create_printable_image(processed_image_path, printable_path, fonts_folder, rows=2, cols=2):
    """
    Создание изображения для печати с размещением нескольких копий фотографии.
    """
    canvas_width = 4 * PIXELS_PER_INCH
    canvas_height = 6 * PIXELS_PER_INCH

    # Создание холста
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')

    # Загрузка обработанного изображения
    photo = Image.open(processed_image_path)

    # Проверка размера
    expected_size = (2 * PIXELS_PER_INCH, 2 * PIXELS_PER_INCH)
    if photo.size != expected_size:
        photo = photo.resize(expected_size, Image.LANCZOS)

    # Отступы
    margin_x = (canvas_width - (cols * photo.width)) // (cols + 1)
    margin_y = (canvas_height - (rows * photo.height)) // (rows + 1)

    # Размещение фотографий
    for row in range(rows):
        for col in range(cols):
            x = margin_x + col * (photo.width + margin_x)
            y = margin_y + row * (photo.height + margin_y)
            canvas.paste(photo, (x, y))

    # Сохранение изображения без водяного знака
    canvas.save(printable_path, dpi=(PIXELS_PER_INCH, PIXELS_PER_INCH), quality=95)
    logging.info(f"Printable image saved at {printable_path}")

def create_printable_preview(processed_image_path, printable_preview_path, fonts_folder, rows=2, cols=2):
    """
    Создание превью изображения для печати с водяным знаком.
    """
    canvas_width = 4 * PIXELS_PER_INCH
    canvas_height = 6 * PIXELS_PER_INCH

    # Создание холста
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')

    # Загрузка обработанного изображения
    photo = Image.open(processed_image_path)

    # Проверка размера
    expected_size = (2 * PIXELS_PER_INCH, 2 * PIXELS_PER_INCH)
    if photo.size != expected_size:
        photo = photo.resize(expected_size, Image.LANCZOS)

    # Применение водяного знака
    watermarked_photo = apply_watermark_to_photo(photo, fonts_folder)

    # Отступы
    margin_x = (canvas_width - (cols * photo.width)) // (cols + 1)
    margin_y = (canvas_height - (rows * photo.height)) // (rows + 1)

    # Размещение фотографий
    for row in range(rows):
        for col in range(cols):
            x = margin_x + col * (photo.width + margin_x)
            y = margin_y + row * (photo.height + margin_y)
            canvas.paste(watermarked_photo, (x, y))

    # Сохранение превью с водяным знаком
    canvas.save(printable_preview_path, dpi=(PIXELS_PER_INCH, PIXELS_PER_INCH), quality=95)
    logging.info(f"Printable preview saved at {printable_preview_path}")

def apply_watermark_to_photo(photo, fonts_folder):
    """
    Применение водяного знака к фотографии.
    """
    watermarked_photo = photo.copy().convert('RGBA')
    draw = ImageDraw.Draw(watermarked_photo)

    try:
        arial_font_path = os.path.join(fonts_folder, 'Arial.ttf')
        watermark_font_size = int(watermarked_photo.width * 0.15)
        watermark_font = ImageFont.truetype(arial_font_path, watermark_font_size)
    except IOError:
        logging.warning("Arial font not found. Using default font.")
        watermark_font = ImageFont.load_default()
        watermark_font_size = 50

    watermark_text = "PREVIEW"
    watermark_opacity = 128

    # Позиция
    position = (watermarked_photo.width / 2, watermarked_photo.height / 2)

    # Слой для водяного знака
    watermark_overlay = Image.new('RGBA', watermarked_photo.size, (255, 255, 255, 0))
    watermark_draw = ImageDraw.Draw(watermark_overlay)

    watermark_draw.text(
        position,
        watermark_text,
        fill=(0, 0, 0, watermark_opacity),
        font=watermark_font,
        anchor='mm'
    )

    # Наложение водяного знака
    watermarked_photo = Image.alpha_composite(watermarked_photo, watermark_overlay)

    # Конвертация обратно в RGB
    watermarked_photo = watermarked_photo.convert('RGB')

    return watermarked_photo
