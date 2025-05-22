# printable_creator.py

import os
import logging
from PIL import Image, ImageDraw, ImageFont

from utils import PIXELS_PER_INCH # Used for fixed canvas size, ensure it's compatible with spec.dpi for print
from photo_specs import PhotoSpecification # Import for type hinting

def create_printable_image(processed_image_path, printable_path, fonts_folder, 
                           rows=2, cols=2, photo_spec: Optional[PhotoSpecification] = None):
    """
    Создание изображения для печати с размещением нескольких копий фотографии.
    """
    # Use a default DPI if spec is not provided, or spec's DPI.
    # For canvas size, we use a fixed 300 DPI for a 4x6 inch paper.
    # The photo_spec.dpi will be used for saving the image.
    current_dpi = photo_spec.dpi if photo_spec else PIXELS_PER_INCH

    canvas_width = 4 * PIXELS_PER_INCH  # Standard 4x6 paper at 300 DPI for canvas calculations
    canvas_height = 6 * PIXELS_PER_INCH

    # Создание холста
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    draw = ImageDraw.Draw(canvas)

    # Загрузка обработанного изображения
    photo = Image.open(processed_image_path)

    # Photo dimensions should come from photo_spec
    photo_target_width_px = photo_spec.photo_width_px if photo_spec else (2 * PIXELS_PER_INCH)
    photo_target_height_px = photo_spec.photo_height_px if photo_spec else (2 * PIXELS_PER_INCH)

    if photo.size != (photo_target_width_px, photo_target_height_px):
        photo = photo.resize((photo_target_width_px, photo_target_height_px), Image.LANCZOS)
        logging.info(f"Resized photo for printable to {photo_target_width_px}x{photo_target_height_px}px.")

    # Фиксированный отступ между фотографиями (0.25 дюйма = 75 пикселей при 300 DPI for canvas)
    spacing = int(0.25 * PIXELS_PER_INCH)

    # Вычисление общей ширины и высоты группы фотографий с отступами
    # photo.width and photo.height are now correctly spec-defined photo sizes
    total_width = cols * photo.width + (cols - 1) * spacing
    total_height = rows * photo.height + (rows - 1) * spacing

    # Вычисление начальных координат для центрирования группы фотографий
    start_x = (canvas_width - total_width) // 2
    start_y = (canvas_height - total_height) // 2

    # Размещение фотографий
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (photo.width + spacing)
            y = start_y + row * (photo.height + spacing)
            canvas.paste(photo, (x, y))

    # Добавление пунктирных линий для обрезки
    dash_length = int(0.1 * PIXELS_PER_INCH)  # 0.1 inch dashes
    gap_length = int(0.1 * PIXELS_PER_INCH)   # 0.1 inch gaps
    line_color = (180, 180, 180)  # Светло-серый цвет

    # Горизонтальные линии
    for row in range(rows - 1):
        y = start_y + (row + 1) * photo.height + (row * spacing) + spacing // 2
        x = 0
        while x < canvas_width:
            x_end = min(x + dash_length, canvas_width)
            draw.line([(x, y), (x_end, y)], fill=line_color, width=1)
            x = x_end + gap_length

    # Вертикальные линии
    for col in range(cols - 1):
        x = start_x + (col + 1) * photo.width + (col * spacing) + spacing // 2
        y = 0
        while y < canvas_height:
            y_end = min(y + dash_length, canvas_height)
            draw.line([(x, y), (x, y_end)], fill=line_color, width=1)
            y = y_end + gap_length

    # Сохранение изображения
    canvas.save(printable_path, dpi=(current_dpi, current_dpi), quality=95)
    logging.info(f"Printable image saved at {printable_path} with DPI {current_dpi}")

def create_printable_preview(processed_image_path, printable_preview_path, fonts_folder, 
                             rows=2, cols=2, photo_spec: Optional[PhotoSpecification] = None):
    """
    Создание превью изображения для печати с водяным знаком.
    """
    current_dpi = photo_spec.dpi if photo_spec else PIXELS_PER_INCH
    
    canvas_width = 4 * PIXELS_PER_INCH # Standard 4x6 paper at 300 DPI for canvas
    canvas_height = 6 * PIXELS_PER_INCH

    # Создание холста
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    draw = ImageDraw.Draw(canvas)

    # Загрузка обработанного изображения
    photo = Image.open(processed_image_path)

    # Photo dimensions should come from photo_spec
    photo_target_width_px = photo_spec.photo_width_px if photo_spec else (2 * PIXELS_PER_INCH)
    photo_target_height_px = photo_spec.photo_height_px if photo_spec else (2 * PIXELS_PER_INCH)

    if photo.size != (photo_target_width_px, photo_target_height_px):
        photo = photo.resize((photo_target_width_px, photo_target_height_px), Image.LANCZOS)
        logging.info(f"Resized photo for printable preview to {photo_target_width_px}x{photo_target_height_px}px.")

    # Применение водяного знака
    watermarked_photo = apply_watermark_to_photo(photo, fonts_folder)

    # Фиксированный отступ между фотографиями (0.25 дюйма = 75 пикселей при 300 DPI for canvas)
    spacing = int(0.25 * PIXELS_PER_INCH)

    # Вычисление общей ширины и высоты группы фотографий с отступами
    # watermarked_photo.width and .height are now correctly spec-defined photo sizes
    total_width = cols * watermarked_photo.width + (cols - 1) * spacing
    total_height = rows * watermarked_photo.height + (rows - 1) * spacing

    # Вычисление начальных координат для центрирования группы фотографий
    start_x = (canvas_width - total_width) // 2
    start_y = (canvas_height - total_height) // 2

    # Размещение фотографий
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (photo.width + spacing)
            y = start_y + row * (photo.height + spacing)
            canvas.paste(watermarked_photo, (x, y))

    # Добавление тех же пунктирных линий для превью
    dash_length = int(0.1 * PIXELS_PER_INCH)
    gap_length = int(0.1 * PIXELS_PER_INCH)
    line_color = (180, 180, 180)

    # Горизонтальные линии
    for row in range(rows - 1):
        y = start_y + (row + 1) * photo.height + (row * spacing) + spacing // 2
        x = 0
        while x < canvas_width:
            x_end = min(x + dash_length, canvas_width)
            draw.line([(x, y), (x_end, y)], fill=line_color, width=1)
            x = x_end + gap_length

    # Вертикальные линии
    for col in range(cols - 1):
        x = start_x + (col + 1) * photo.width + (col * spacing) + spacing // 2
        y = 0
        while y < canvas_height:
            y_end = min(y + dash_length, canvas_height)
            draw.line([(x, y), (x, y_end)], fill=line_color, width=1)
            y = y_end + gap_length

    # Сохранение превью с водяным знаком
    canvas.save(printable_preview_path, dpi=(current_dpi, current_dpi), quality=95)
    logging.info(f"Printable preview saved at {printable_preview_path} with DPI {current_dpi}")

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
