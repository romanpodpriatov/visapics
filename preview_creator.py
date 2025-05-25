import os
import logging
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, Tuple

from photo_specs import PhotoSpecification  # For type hinting

# Watermark and default measurement colors
WATERMARK_TEXT = "visapicture"
WATERMARK_COLOR_WITH_ALPHA = (225, 225, 225, 225)
PHOTO_BORDER_COLOR = (200, 200, 200, 255)

# Two distinct colors for the two right‑side measurements
HEAD_MEASUREMENT_COLOR = (0, 128, 0, 255)       # Green for head height
EYE_MEASUREMENT_COLOR  = (0, 0, 255, 255)       # Blue for eyes→bottom

# Text colors matching the measurement line colors
HEAD_TEXT_COLOR = HEAD_MEASUREMENT_COLOR # Text color for head measurement (can be made distinct if needed)
EYE_TEXT_COLOR  = EYE_MEASUREMENT_COLOR  # Text color for eye measurement (can be made distinct if needed)

# Helper functions (draw_tiled_watermark, draw_filled_arrowhead, draw_rotated_text_on_canvas)
# ... (они остаются такими же, как в вашем предыдущем коде) ...
# Я включу их в конце для полноты, если нужно будет скопировать весь файл.

def draw_tiled_watermark(
    image: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont,
    color_with_alpha: Tuple[int, int, int, int],
    angle: int = -30,
    density_factor: float = 0.15,
) -> Image.Image:
    """Tiles a semi‑transparent watermark text over the image."""
    orig_mode = image.mode
    if orig_mode != 'RGBA':
        image = image.convert('RGBA')
    # Используем временный ImageDraw для измерения, чтобы не изменять исходное изображение преждевременно
    # Однако, если draw используется только для textbbox, можно и на целевом, т.к. оно не меняется
    # Для консистентности с draw_rotated_text_on_canvas, можно создать dummy Image.
    # Но в данном случае это не критично, т.к. draw.textbbox не рисует.
    measure_draw = ImageDraw.Draw(image) # или ImageDraw.Draw(Image.new('RGBA', (1,1)))
    w, h = image.size

    # measure the watermark text
    try:
        bbox = measure_draw.textbbox((0, 0), text, font=font, anchor="lt")
        tw_f = bbox[2] - bbox[0]
        th_f = bbox[3] - bbox[1]
    except AttributeError: # Pillow < 9.2.0
        tw_f, th_f = map(float, measure_draw.textsize(text, font=font))

    tw = int(round(tw_f))
    th = int(round(th_f))
    if tw == 0 or th == 0:
        if orig_mode != 'RGBA':
            image = image.convert(orig_mode)
        return image

    # one rotated stamp for step calculation
    proto = Image.new('RGBA', (tw, th), (255,255,255,0))
    pd = ImageDraw.Draw(proto)
    # Рисуем текст на прототипе относительно его bbox[0],bbox[1] если они не 0,0
    # но т.к. anchor="lt", bbox[0] и bbox[1] должны быть близки к 0.
    # Для простоты, как в оригинале, предполагаем, что текст хорошо ложится с (0,0) на этом прототипе.
    pd.text((0, 0), text, font=font, fill=color_with_alpha)
    stamp = proto.rotate(angle, expand=True, resample=Image.BICUBIC)
    sw, sh = stamp.size

    # tile steps
    step_x = max(1, int(round(sw * 0.75)), int(round(sw / (density_factor * 4 + 0.5))))
    step_y = max(1, int(round(sh * 0.75)), int(round(sh / (density_factor * 4 + 0.5))))

    # create and rotate the actual tile once
    pad_val = 4 # Renamed from 'pad' to avoid conflict with 'pad' in main function
    tile_w = tw + pad_val
    tile_h = th + pad_val
    tile = Image.new('RGBA', (tile_w, tile_h), (255,255,255,0))
    td = ImageDraw.Draw(tile)
    # Центрируем текст на tile, если bbox учитывался бы, или с небольшим отступом как ранее
    # bbox[0],bbox[1] от textbbox ранее не использовались для смещения на tile.
    # Проще всего рисовать с (pad_val/2, pad_val/2) или как в оригинале (2,2) для паддинга в 4.
    # Оригинал: td.text((2,2), ...). bbox[0], bbox[1] для textbbox с anchor='lt' обычно (0,0) или близки.
    td.text((pad_val//2, pad_val//2), text, font=font, fill=color_with_alpha)

    rot_tile = tile.rotate(
        angle,
        center=(tile_w//2, tile_h//2),
        expand=True,
        resample=Image.BICUBIC
    )
    rtw, rth = rot_tile.size

    # paste tiles across
    # Используем основной ImageDraw для 실제 рисования
    main_draw = ImageDraw.Draw(image) # Не создавали его ранее, теперь он нужен для paste
    for x_center in range(-sw, w + sw, step_x): # Renamed x to x_center
        for y_center in range(-sh, h + sh, step_y): # Renamed y to y_center
            # Координаты для paste - это верхний левый угол
            paste_x = x_center - rtw//2
            paste_y = y_center - rth//2
            image.paste(rot_tile, (paste_x, paste_y), rot_tile)

    if orig_mode != 'RGBA':
        image = image.convert(orig_mode)
    return image


def draw_filled_arrowhead(
    draw: ImageDraw.ImageDraw,
    tip: Tuple[int,int],
    direction: str,
    size: int,
    color: Tuple[int,int,int,int],
) -> None:
    """Draws a filled triangular arrowhead."""
    x, y = tip
    if direction == 'up':
        pts = [(x,y), (x-size//2,y+size), (x+size//2,y+size)]
    elif direction == 'down':
        pts = [(x,y), (x-size//2,y-size), (x+size//2,y-size)]
    elif direction == 'left':
        pts = [(x,y), (x+size,y-size//2), (x+size,y+size//2)]
    elif direction == 'right':
        pts = [(x,y), (x-size,y-size//2), (x-size,y+size//2)]
    else:
        return
    draw.polygon(pts, fill=color)


def draw_rotated_text_on_canvas(
    canvas: Image.Image,
    text: str,
    center: Tuple[int,int],
    font: ImageFont.FreeTypeFont,
    fill: Tuple[int,int,int,int],
    angle: float,
) -> Image.Image:
    """Draws (multi‑line) text rotated by angle, centered at `center`."""
    if canvas.mode != 'RGBA':
        canvas = canvas.convert('RGBA')

    dummy = ImageDraw.Draw(Image.new('L',(1,1)))
    is_ml = '\n' in text
    try:
        # Pillow 9.2.0+ textbbox includes an 'anchor' parameter.
        # Pillow 10.0.0+ multiline_textbbox includes 'anchor' and 'align'.
        # For older versions, these might not be available or behave differently.
        # The original code's try-except handles textbbox/textsize.
        if is_ml:
            bbox = dummy.multiline_textbbox((0,0), text, font=font, align='center')
        else:
            bbox = dummy.textbbox((0,0), text, font=font) # anchor default is 'la' or related to font itself for textbbox
        
        tw_f = bbox[2] - bbox[0]
        th_f = bbox[3] - bbox[1]
    except AttributeError: # Older Pillow or specific method version
        if is_ml:
            size = dummy.multiline_textsize(text, font=font) # No align here
        else:
            size = dummy.textsize(text, font=font)
        tw_f, th_f = float(size[0]), float(size[1])
        # Define bbox[0], bbox[1] as 0 for this path for consistency in td.text/multiline_text call
        bbox = (0.0, 0.0, tw_f, th_f) # This makes (-bbox[0], -bbox[1]) into (0,0)

    tw, th = int(round(tw_f)), int(round(th_f))
    if tw == 0 or th == 0:
        return canvas

    txt_img = Image.new('RGBA', (tw, th), (255,255,255,0))
    td = ImageDraw.Draw(txt_img)
    # (-bbox[0], -bbox[1]) correctly positions text if its own bounding box doesn't start at (0,0)
    if is_ml:
        td.multiline_text((-bbox[0], -bbox[1]), text, font=font, fill=fill, align='center')
    else:
        td.text((-bbox[0], -bbox[1]), text, font=font, fill=fill)

    rot = txt_img.rotate(angle, expand=True, resample=Image.BICUBIC)
    px = center[0] - rot.width//2
    py = center[1] - rot.height//2
    canvas.paste(rot, (px,py), rot)
    return canvas

def create_preview_with_watermark(
    image_path: str,
    preview_path: str,
    preview_drawing_data: Dict[str,Any],
    fonts_folder: str,
) -> None:
    spec: PhotoSpecification = preview_drawing_data['photo_spec']
    w_px = int(round(preview_drawing_data['photo_width_px']))
    h_px = int(round(preview_drawing_data['photo_height_px']))

    img = Image.open(image_path)
    if img.size != (w_px, h_px):
        img = img.resize((w_px, h_px), Image.LANCZOS)

    # load fonts
    try:
        arial = os.path.join(fonts_folder, 'Arial.ttf')
        wm_fs   = max(1, int(round(h_px * 0.1)))
        # Уменьшаем шрифт для размеров (был 0.026)
        meas_fs = max(1, int(round(h_px * 0.020))) # <--- ИЗМЕНЕНИЕ: шрифт меньше
        dim_fs  = max(1, int(round(h_px * 0.036)))
        wm_font   = ImageFont.truetype(arial, wm_fs)
        meas_font = ImageFont.truetype(arial, meas_fs)
        dim_font  = ImageFont.truetype(arial, dim_fs)
    except IOError:
        logging.warning("Arial.ttf missing; using default font")
        wm_font = meas_font = dim_font = ImageFont.load_default()

    # watermark
    img_rgba = img.convert('RGBA')
    img_rgba = draw_tiled_watermark(img_rgba, WATERMARK_TEXT, wm_font, WATERMARK_COLOR_WITH_ALPHA)

    # measure sample text for margins
    dummy = ImageDraw.Draw(Image.new('L',(1,1)))
    sample = "2.00in"
    try:
        sb = dummy.textbbox((0,0), sample, font=dim_font)
        tx_w_f = sb[2] - sb[0]
        tx_h_f = sb[3] - sb[1]
    except AttributeError:
        _tw, _th = dummy.textsize(sample, font=dim_font)
        tx_w_f, tx_h_f = float(_tw), float(_th)

    arrow = max(4, int(round(h_px * 0.012)))
    pad   = int(round(h_px * 0.01)) # Базовый отступ

    margin_left   = int(round(tx_w_f + arrow + pad + w_px * 0.02))
    margin_top    = int(round(h_px * 0.05))
    margin_bottom = int(round(tx_h_f + arrow + pad + h_px * 0.02))

    # compute labels
    ratio = spec.photo_height_inches / h_px if h_px else 0.0
    head_px = int(round(preview_drawing_data['achieved_head_height_px']))
    head_in = head_px * ratio
    head_label = f"{head_in:.2f}in\n({spec.head_min_inches:.2f}–{spec.head_max_inches:.2f}in)"

    eye_py = int(round(preview_drawing_data['achieved_eye_level_y_on_photo_px']))
    eye_to_bot_px = h_px - eye_py
    eye_to_bot_in = eye_to_bot_px * ratio
    eye_label = f"{eye_to_bot_in:.2f}in\n({spec.eye_min_from_bottom_inches:.2f}–{spec.eye_max_from_bottom_inches:.2f}in)"

    # compute text heights (which become widths when rotated) for right margin calculation
    try:
        b1 = dummy.multiline_textbbox((0,0), head_label, font=meas_font, align='center')
        # h1_f это высота не повернутого текста (станет шириной повернутого)
        rotated_head_label_width_f = b1[3] - b1[1] 
    except AttributeError:
        _, _h1 = dummy.multiline_textsize(head_label, font=meas_font)
        rotated_head_label_width_f = _h1 * 1.2 # Original factor
    
    try:
        b2 = dummy.multiline_textbbox((0,0), eye_label, font=meas_font, align='center')
        rotated_eye_label_width_f = b2[3] - b2[1]
    except AttributeError:
        _, _h2 = dummy.multiline_textsize(eye_label, font=meas_font)
        rotated_eye_label_width_f = _h2 * 1.2 # Original factor

    rotated_head_label_width = int(round(rotated_head_label_width_f))
    rotated_eye_label_width = int(round(rotated_eye_label_width_f))

    # --- ИЗМЕНЕНИЕ: Расчет позиций для правой колонки ---
    initial_gap_from_photo_edge = int(round(w_px * 0.03)) # Отступ от края фото до первой линии
    line_to_text_gap = pad                               # Отступ от вертикальной линии до ее текста
    text_block_spacing = pad * 2                         # Горизонтальный отступ между первым текстом и второй линией
    final_right_padding = pad                            # Финальный отступ справа на холсте

    # Координаты для измерения высоты головы (зеленый)
    xr_head_line = margin_left + w_px + initial_gap_from_photo_edge # X для верт. линии
    head_label_center_x = xr_head_line + line_to_text_gap + rotated_head_label_width // 2
    head_label_block_end_x = xr_head_line + line_to_text_gap + rotated_head_label_width

    # Координаты для измерения от глаз до низа (синий)
    xr_eye_line = head_label_block_end_x + text_block_spacing # X для верт. линии
    eye_label_center_x = xr_eye_line + line_to_text_gap + rotated_eye_label_width // 2
    eye_label_block_end_x = xr_eye_line + line_to_text_gap + rotated_eye_label_width
    
    # Пересчитываем margin_right на основе новых позиций
    # margin_right - это ширина области справа от фотографии (x0+w_px)
    # до правого края холста.
    # (eye_label_block_end_x - (margin_left + w_px)) это расстояние от края фото до конца второго лейбла
    margin_right = (eye_label_block_end_x - (margin_left + w_px)) + final_right_padding
    # --- Конец ИЗМЕНЕНИЯ для правой колонки ---

    # create canvas
    canvas_w = margin_left + w_px + margin_right # Общая ширина холста
    canvas_h = margin_top + h_px + margin_bottom # Общая высота холста
    canvas = Image.new('RGBA', (canvas_w, canvas_h), (255,255,255,255))

    # x0, y0 - это верхний левый угол самой фотографии на холсте
    x0, y0 = margin_left, margin_top 
    canvas.paste(img_rgba, (x0,y0), img_rgba)
    dr = ImageDraw.Draw(canvas)

    # border & horizontal guides
    dr.rectangle((x0-1, y0-1, x0+w_px, y0+h_px), outline=PHOTO_BORDER_COLOR, width=1)
    top_y  = y0 + int(round(preview_drawing_data['achieved_head_top_y_on_photo_px']))
    eye_y  = y0 + eye_py
    chin_y = top_y + head_px
    bot_y  = y0 + h_px

    # Основные горизонтальные линии через фото (теперь одним цветом, можно изменить если нужно)
    main_guide_color = HEAD_MEASUREMENT_COLOR # или общий (200,200,200,255)
    for yy_coord in (top_y, eye_y, chin_y):
        dr.line([(x0, yy_coord), (x0+w_px, yy_coord)], fill=main_guide_color, width=1)

    # left (photo height)
    dr.line([(x0, y0), (x0, bot_y)], fill=HEAD_MEASUREMENT_COLOR, width=1)
    draw_filled_arrowhead(dr, (x0,y0), 'up', arrow, HEAD_MEASUREMENT_COLOR)
    draw_filled_arrowhead(dr, (x0,bot_y), 'down', arrow, HEAD_MEASUREMENT_COLOR)
    canvas = draw_rotated_text_on_canvas(
        canvas,
        f"{spec.photo_height_inches:.2f}in",
        (x0 - line_to_text_gap - int(round(tx_w_f/2)), y0 + h_px//2), # Используем line_to_text_gap вместо pad
        dim_font,
        HEAD_TEXT_COLOR, # Цвет текста для размеров слева/снизу
        90
    )

    # bottom (photo width)
    dr.line([(x0, bot_y), (x0+w_px, bot_y)], fill=HEAD_MEASUREMENT_COLOR, width=1)
    draw_filled_arrowhead(dr, (x0,bot_y), 'left', arrow, HEAD_MEASUREMENT_COLOR)
    draw_filled_arrowhead(dr, (x0+w_px,bot_y), 'right', arrow, HEAD_MEASUREMENT_COLOR)
    canvas = draw_rotated_text_on_canvas(
        canvas,
        f"{spec.photo_width_inches:.2f}in",
        (x0 + w_px//2, bot_y + line_to_text_gap + int(round(tx_h_f/2))), # Используем line_to_text_gap
        dim_font,
        HEAD_TEXT_COLOR, # Цвет текста для размеров слева/снизу
        0
    )

    # --- ИЗМЕНЕНИЕ: правая колонка с двумя линиями ---
    # 1. Head measurement (Green)
    dr.line([(xr_head_line, top_y), (xr_head_line, chin_y)], fill=HEAD_MEASUREMENT_COLOR, width=1)
    draw_filled_arrowhead(dr, (xr_head_line,top_y), 'up', arrow, HEAD_MEASUREMENT_COLOR)
    draw_filled_arrowhead(dr, (xr_head_line,chin_y), 'down', arrow, HEAD_MEASUREMENT_COLOR)
    # Горизонтальные соединительные линии от фото к размерной линии
    dr.line([(x0+w_px, top_y), (xr_head_line - arrow//2, top_y)], fill=HEAD_MEASUREMENT_COLOR, width=1)
    dr.line([(x0+w_px, chin_y), (xr_head_line - arrow//2, chin_y)], fill=HEAD_MEASUREMENT_COLOR, width=1)
    canvas = draw_rotated_text_on_canvas(
        canvas,
        head_label,
        (head_label_center_x, (top_y+chin_y)//2), # Новый X центр
        meas_font,
        HEAD_TEXT_COLOR,
        -90
    )

    # 2. Eye-to-bottom measurement (Blue)
    dr.line([(xr_eye_line, eye_y), (xr_eye_line, bot_y)], fill=EYE_MEASUREMENT_COLOR, width=1)
    draw_filled_arrowhead(dr, (xr_eye_line,eye_y), 'up', arrow, EYE_MEASUREMENT_COLOR)
    draw_filled_arrowhead(dr, (xr_eye_line,bot_y), 'down', arrow, EYE_MEASUREMENT_COLOR)
    # Горизонтальные соединительные линии
    dr.line([(x0+w_px, eye_y), (xr_eye_line - arrow//2, eye_y)], fill=EYE_MEASUREMENT_COLOR, width=1)
    dr.line([(x0+w_px, bot_y), (xr_eye_line - arrow//2, bot_y)], fill=EYE_MEASUREMENT_COLOR, width=1)
    canvas = draw_rotated_text_on_canvas(
        canvas,
        eye_label,
        (eye_label_center_x, (eye_y+bot_y)//2), # Новый X центр
        meas_font,
        EYE_TEXT_COLOR,
        -90
    )
    # --- Конец ИЗМЕНЕНИЯ для правой колонки ---

    # save with integer DPI
    final = canvas.convert('RGB')
    try:
        dpi_val = float(spec.dpi) # Убедимся, что это число
        dpi_tuple = (int(round(dpi_val)), int(round(dpi_val)))
    except (ValueError, TypeError, AttributeError): # AttributeError если spec.dpi None и float() не может обработать
        logging.warning(f"Invalid DPI value '{spec.dpi if hasattr(spec, 'dpi') else 'MISSING'}'. Using default 72 DPI.")
        dpi_tuple = (72,72)
    final.save(preview_path, dpi=dpi_tuple, quality=90)
    logging.info(f"Preview saved to {preview_path}")