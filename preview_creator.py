# preview_creator.py

import os
import math
import logging
from PIL import Image, ImageDraw, ImageFont

# from face_analyzer import FaceAnalyzer # Removed as per plan
from utils import PIXELS_PER_INCH, PHOTO_SIZE_PIXELS

def draw_double_arrowed_line(draw, x_pos, y1, y2, text_label, font, color=(0,0,0,255), arrow_size=10, line_width=2):
    """
    Draws a vertical double-arrowed line with a text label.
    y1 and y2 can be in any order.
    """
    # Ensure y1 is less than y2 for consistent drawing
    if y1 > y2:
        y1, y2 = y2, y1

    # Line
    draw.line([(x_pos, y1), (x_pos, y2)], fill=color, width=line_width)

    # Arrowheads
    # Top arrow
    draw.line([(x_pos - arrow_size // 2, y1 + arrow_size), (x_pos, y1)], fill=color, width=line_width)
    draw.line([(x_pos + arrow_size // 2, y1 + arrow_size), (x_pos, y1)], fill=color, width=line_width)
    # Bottom arrow
    draw.line([(x_pos - arrow_size // 2, y2 - arrow_size), (x_pos, y2)], fill=color, width=line_width)
    draw.line([(x_pos + arrow_size // 2, y2 - arrow_size), (x_pos, y2)], fill=color, width=line_width)

    # Text
    # Calculate text size
    try:
        # Newer Pillow versions use getbbox
        text_bbox = draw.textbbox((0,0), text_label, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
    except AttributeError:
        # Older Pillow versions use textsize
        text_width, text_height = draw.textsize(text_label, font=font)
    
    text_x = x_pos + arrow_size # Offset from the arrow line
    text_y = y1 + (y2 - y1) / 2 - text_height / 2 # Centered vertically
    draw.text((text_x, text_y), text_label, fill=color, font=font)


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

    # --- Start of Measurement Drawing based on crop_data ---
    
    # Photo dimensions (should be 600x600 for the processed image)
    # img_width and img_height are already from Image.open(image_path)
    # Ensure these are used consistently as PHOTO_SIZE_PIXELS if image_path is guaranteed to be 600x600
    img_photo_width = img_width 
    img_photo_height = img_height

    # Calculate Y-coordinates on the 600x600 photo area (relative to top-left of photo)
    # crop_data['eye_to_bottom'] is in inches, convert to pixels from bottom of photo
    eye_level_from_bottom_photo_px = crop_data['eye_to_bottom'] * PIXELS_PER_INCH
    y_eye_on_photo = img_photo_height - eye_level_from_bottom_photo_px

    head_height_pixels_on_photo = crop_data['head_height'] * PIXELS_PER_INCH
    
    # Assuming eyes are 45% from the top of the head for visual representation
    # This is an estimation for drawing purposes.
    proportion_head_above_eyes = 0.45 
    y_head_top_on_photo = y_eye_on_photo - (head_height_pixels_on_photo * proportion_head_above_eyes)
    y_chin_on_photo = y_head_top_on_photo + head_height_pixels_on_photo

    # Adjust Y-coordinates for canvas (add margin_top)
    y_head_top_canvas = margin_top + y_head_top_on_photo
    y_eye_canvas = margin_top + y_eye_on_photo
    y_chin_canvas = margin_top + y_chin_on_photo
    y_photo_bottom_canvas = margin_top + img_photo_height # Bottom edge of the photo on canvas

    # Define X-coordinates for horizontal lines and vertical arrows
    # Horizontal lines will span across most of the photo width
    x_horizontal_lines_start = margin_left + int(img_photo_width * 0.1) # Indent slightly
    x_horizontal_lines_end = margin_left + img_photo_width - int(img_photo_width * 0.1) # Indent slightly from other side

    # Vertical measurement arrows will be to the right of the photo
    x_measurement_arrows = margin_left + img_photo_width + int(margin_right * 0.25)
    # Ensure arrow text does not go off canvas, adjust x_measurement_arrows if needed
    # A quick check: canvas_width - (arrow_text_width_approx)
    # For now, this position should be fine.

    line_color = (0, 0, 0, 255) # Black, opaque
    line_width_horizontal = 2
    
    # Draw Horizontal Lines on canvas
    draw_preview.line([(x_horizontal_lines_start, y_head_top_canvas), (x_horizontal_lines_end, y_head_top_canvas)], fill=line_color, width=line_width_horizontal)
    draw_preview.line([(x_horizontal_lines_start, y_eye_canvas), (x_horizontal_lines_end, y_eye_canvas)], fill=line_color, width=line_width_horizontal)
    draw_preview.line([(x_horizontal_lines_start, y_chin_canvas), (x_horizontal_lines_end, y_chin_canvas)], fill=line_color, width=line_width_horizontal)

    # Prepare text for measurements
    text_head_height = f"{crop_data['head_height']:.2f}\" Head"
    text_eye_to_bottom = f"{crop_data['eye_to_bottom']:.2f}\" Eye-Bottom"

    # Draw Measurement Arrows & Text using the helper function
    # Head Height measurement
    draw_double_arrowed_line(draw_preview, 
                             x_measurement_arrows, 
                             y_head_top_canvas, 
                             y_chin_canvas, 
                             text_head_height, 
                             measurement_font, 
                             color=line_color)

    # Eye-to-Bottom of Photo measurement
    draw_double_arrowed_line(draw_preview, 
                             x_measurement_arrows, 
                             y_eye_canvas, 
                             y_photo_bottom_canvas, 
                             text_eye_to_bottom, 
                             measurement_font, 
                             color=line_color)
    
    # --- End of Measurement Drawing ---

    # Сохранение превью
    preview = preview.convert('RGB')
    preview.save(preview_path, quality=95)
    logging.info(f"Preview saved at {preview_path}")