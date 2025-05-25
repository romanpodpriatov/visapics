# printable_creator.py

import os
import logging
import math 
from typing import Optional, Tuple, Dict 
from PIL import Image, ImageDraw, ImageFont

from utils import PIXELS_PER_INCH 
from photo_specs import PhotoSpecification 

WATERMARK_TEXT = "visapicture" 
WATERMARK_COLOR_WITH_ALPHA = (128, 128, 128, 30) 

def _draw_tiled_watermark_for_printable(image: Image.Image, text: str, font: ImageFont.FreeTypeFont, 
                                       color_with_alpha: Tuple[int,int,int,int], angle: int = -30, density_factor: float = 0.15):
    original_mode = image.mode
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    draw = ImageDraw.Draw(image)
    width, height = image.size

    try:
        bbox = draw.textbbox((0,0), text, font=font, anchor="lt")
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        text_width, text_height = draw.textsize(text, font=font)

    if text_width == 0 or text_height == 0:
        if original_mode != 'RGBA' and original_mode != image.mode: image = image.convert(original_mode)
        return image

    proto_text_img = Image.new('RGBA', (text_width, text_height), (255,255,255,0))
    proto_draw = ImageDraw.Draw(proto_text_img)
    proto_draw.text((0,0), text, font=font, fill=color_with_alpha, anchor="lt")
    rotated_proto_text_img = proto_text_img.rotate(angle, expand=True, resample=Image.BICUBIC)
    stamp_w, stamp_h = rotated_proto_text_img.size
    
    step_x = int(stamp_w * (1 / (density_factor * 4 + 0.5))) 
    step_y = int(stamp_h * (1 / (density_factor * 4 + 0.5)))
    step_x = max(step_x, int(stamp_w * 0.75)) 
    step_y = max(step_y, int(stamp_h * 0.75))

    for x_base in range(-stamp_w, width + stamp_w, step_x):
        for y_base in range(-stamp_h, height + stamp_h, step_y):
            temp_render_size = (text_width + 4, text_height + 4)
            text_instance_img = Image.new('RGBA', temp_render_size, (255,255,255,0))
            text_instance_draw = ImageDraw.Draw(text_instance_img)
            text_instance_draw.text((2,2), text, font=font, fill=color_with_alpha, anchor="lt")
            rotated_text_instance_img = text_instance_img.rotate(angle, center=(temp_render_size[0]/2, temp_render_size[1]/2), expand=True, resample=Image.BICUBIC)
            paste_x = x_base - rotated_text_instance_img.width // 2
            paste_y = y_base - rotated_text_instance_img.height // 2
            image.paste(rotated_text_instance_img, (paste_x, paste_y), rotated_text_instance_img)
    
    if original_mode != 'RGBA' and original_mode != image.mode: image = image.convert(original_mode)
    return image


def _apply_watermark_to_single_photo_for_printable(photo: Image.Image, fonts_folder: str):
    watermarked_photo_rgba = photo.copy().convert('RGBA')
    try:
        arial_font_path = os.path.join(fonts_folder, 'Arial.ttf')
        font_size = int(photo.height * 0.10) 
        font = ImageFont.truetype(arial_font_path, font_size)
    except IOError:
        logging.warning(f"Arial font not found in printable_creator for {WATERMARK_TEXT}. Using default.")
        font = ImageFont.load_default()
    
    watermarked_photo_rgba = _draw_tiled_watermark_for_printable(
        watermarked_photo_rgba, WATERMARK_TEXT, font, 
        WATERMARK_COLOR_WITH_ALPHA, angle=-30, density_factor=0.20
    )
    return watermarked_photo_rgba

def _generate_layout_on_fixed_canvas(
    photo_to_place: Image.Image, 
    photo_spec: PhotoSpecification,
    target_canvas_width_px: int,
    target_canvas_height_px: int
) -> Image.Image:
    canvas = Image.new('RGB', (target_canvas_width_px, target_canvas_height_px), 'white')
    draw = ImageDraw.Draw(canvas)

    photo_w_px = photo_spec.photo_width_px
    photo_h_px = photo_spec.photo_height_px

    num_cols = 0
    if photo_w_px <= target_canvas_width_px:
        num_cols = 1
        if photo_w_px * 2 <= target_canvas_width_px:
            num_cols = 2
    
    num_rows = 0
    if photo_h_px <= target_canvas_height_px:
        num_rows = 1
        if photo_h_px * 2 <= target_canvas_height_px:
            num_rows = 2
    
    if num_cols == 0 or num_rows == 0:
        logging.warning(f"Cannot fit even one photo {photo_w_px}x{photo_h_px} on canvas {target_canvas_width_px}x{target_canvas_height_px}. Returning empty canvas.")
        return canvas

    spacing_x = 0
    if num_cols > 1:
        # Distribute remaining space for (num_cols - 1) gaps between photos
        # and 2 edge margins. Total (num_cols + 1) "gaps" for spacing.
        available_for_all_spacings_x = target_canvas_width_px - num_cols * photo_w_px
        if available_for_all_spacings_x >= 0:
             spacing_x = available_for_all_spacings_x / (num_cols + 1)
             spacing_x = int(round(spacing_x))
        else: # Photos don't fit even when adjacent, this shouldn't happen due to checks above
            spacing_x = 0 
            num_cols = 1 # Switch to one column if calculation is incorrect
    
    spacing_y = 0
    if num_rows > 1:
        available_for_all_spacings_y = target_canvas_height_px - num_rows * photo_h_px
        if available_for_all_spacings_y >=0:
            spacing_y = available_for_all_spacings_y / (num_rows + 1)
            spacing_y = int(round(spacing_y))
        else:
            spacing_y = 0
            num_rows = 1 # Switch to one row

    # Initial coordinates - first margin from edge
    start_x = spacing_x
    start_y = spacing_y
    
    # Inter-photo spacing equals edge spacing in this calculation
    photo_spacing_for_loop_x = spacing_x
    photo_spacing_for_loop_y = spacing_y


    logging.info(f"Printable layout: {num_rows}r x {num_cols}c. Photo: {photo_w_px}x{photo_h_px}. Calculated spacing X:{spacing_x}, Y:{spacing_y}. Start: {start_x},{start_y}")

    photo_count = 0
    for r_idx in range(num_rows):
        for c_idx in range(num_cols):
            x = start_x + c_idx * (photo_w_px + photo_spacing_for_loop_x)
            y = start_y + r_idx * (photo_h_px + photo_spacing_for_loop_y)
            
            if x + photo_w_px <= target_canvas_width_px + 1 and \
               y + photo_h_px <= target_canvas_height_px + 1:
                 canvas.paste(photo_to_place, (x, y))
                 photo_count += 1
            else:
                logging.warning(f"Photo {r_idx},{c_idx} at ({x},{y}) calculated outside canvas. Photo: {photo_w_px}x{photo_h_px}. Skipping.")
    
    if photo_count > 0:
        line_color = (200, 200, 200)
        line_width = 1
        
        # Horizontal lines (between rows)
        if num_rows > 1:
             for r_idx in range(num_rows - 1):
                 # Line is drawn AFTER r_idx-th row, before next spacing_y
                 y_line = start_y + (r_idx + 1) * photo_h_px + r_idx * photo_spacing_for_loop_y + photo_spacing_for_loop_y // 2
                 if photo_spacing_for_loop_y == 0: # If no spacing, line at photo boundary
                     y_line = start_y + (r_idx + 1) * photo_h_px
                 
                 line_start_x = start_x 
                 line_end_x = start_x + num_cols * photo_w_px + max(0, num_cols - 1) * photo_spacing_for_loop_x
                 draw.line([(line_start_x, y_line), (line_end_x, y_line)], fill=line_color, width=line_width)
        
        # Vertical lines (between columns)
        if num_cols > 1:
            for c_idx in range(num_cols - 1):
                 x_line = start_x + (c_idx + 1) * photo_w_px + c_idx * photo_spacing_for_loop_x + photo_spacing_for_loop_x // 2
                 if photo_spacing_for_loop_x == 0:
                     x_line = start_x + (c_idx + 1) * photo_w_px

                 line_start_y = start_y
                 line_end_y = start_y + num_rows * photo_h_px + max(0, num_rows - 1) * photo_spacing_for_loop_y
                 draw.line([(x_line, line_start_y), (x_line, line_end_y)], fill=line_color, width=line_width)

    logging.info(f"Pasted {photo_count} photos on fixed canvas with cutting lines.")
    return canvas


def create_printable_image(processed_image_path, printable_path, fonts_folder, 
                           photo_spec: Optional[PhotoSpecification] = None): # Removed rows, cols
    if photo_spec is None:
        logging.error("PhotoSpecification is required for create_printable_image.")
        Image.new('RGB', (1200,1800), 'white').save(printable_path)
        return

    try:
        source_photo_pil = Image.open(processed_image_path)
    except FileNotFoundError:
        logging.error(f"Processed image not found at {processed_image_path}")
        Image.new('RGB', (1200,1800), 'white').save(printable_path)
        return
    
    if source_photo_pil.size != (photo_spec.photo_width_px, photo_spec.photo_height_px):
        source_photo_pil = source_photo_pil.resize((photo_spec.photo_width_px, photo_spec.photo_height_px), Image.LANCZOS)

    canvas_width_px = 4 * PIXELS_PER_INCH
    canvas_height_px = 6 * PIXELS_PER_INCH

    final_canvas = _generate_layout_on_fixed_canvas(
        photo_to_place=source_photo_pil,
        photo_spec=photo_spec,
        target_canvas_width_px=canvas_width_px,
        target_canvas_height_px=canvas_height_px
    )
    
    final_canvas.save(printable_path, dpi=(photo_spec.dpi, photo_spec.dpi), quality=95)
    logging.info(f"Printable image (strict photo size on 4x6) saved at {printable_path}.")


def create_printable_preview(processed_image_path, printable_preview_path, fonts_folder, 
                             photo_spec: Optional[PhotoSpecification] = None): # Removed rows, cols
    if photo_spec is None:
        logging.error("PhotoSpecification is required for create_printable_preview.")
        Image.new('RGB', (1200,1800), 'white').save(printable_preview_path)
        return

    try:
        source_photo_pil = Image.open(processed_image_path)
    except FileNotFoundError:
        logging.error(f"Processed image not found at {processed_image_path}")
        Image.new('RGB', (1200,1800), 'white').save(printable_preview_path)
        return

    if source_photo_pil.size != (photo_spec.photo_width_px, photo_spec.photo_height_px):
        source_photo_pil = source_photo_pil.resize((photo_spec.photo_width_px, photo_spec.photo_height_px), Image.LANCZOS)

    watermarked_single_photo_rgba = _apply_watermark_to_single_photo_for_printable(source_photo_pil, fonts_folder)
    
    photo_to_paste_on_sheet = watermarked_single_photo_rgba
    if watermarked_single_photo_rgba.mode == 'RGBA':
        temp_bg_for_paste = Image.new('RGB', watermarked_single_photo_rgba.size, (255,255,255))
        temp_bg_for_paste.paste(watermarked_single_photo_rgba, (0,0), watermarked_single_photo_rgba)
        photo_to_paste_on_sheet = temp_bg_for_paste
    else:
        photo_to_paste_on_sheet = watermarked_single_photo_rgba.convert('RGB')
    
    canvas_width_px = 4 * PIXELS_PER_INCH
    canvas_height_px = 6 * PIXELS_PER_INCH

    final_canvas = _generate_layout_on_fixed_canvas(
        photo_to_place=photo_to_paste_on_sheet,
        photo_spec=photo_spec,
        target_canvas_width_px=canvas_width_px,
        target_canvas_height_px=canvas_height_px
    )

    final_canvas.save(printable_preview_path, dpi=(photo_spec.dpi, photo_spec.dpi), quality=90)
    logging.info(f"Printable preview (strict photo size on 4x6) saved at {printable_preview_path}.")