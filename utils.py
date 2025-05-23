# utils.py

import os
from werkzeug.utils import secure_filename
from PIL import Image

# Константы
PIXELS_PER_INCH = 300
PHOTO_SIZE_PIXELS = 600  # 2 дюйма * 300 пикселей на дюйм

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """
    Проверка допустимого расширения файла.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_allowed_file(filepath):
    """
    Проверка, является ли файл допустимым по расширению.
    """
    file_ext = os.path.splitext(filepath)[1].lower().lstrip('.')
    return file_ext in ALLOWED_EXTENSIONS

def clean_filename(filename):
    """
    Очистка имени файла от нежелательных символов.
    """
    # Handle special cases first
    if not filename:
        return filename
    
    # Special case for files starting with dot (like .jpg)
    if filename.startswith('.') and filename.count('.') == 1:
        return filename  # Return as-is for extension-only files
    
    # Use secure_filename to handle basic sanitization
    cleaned = secure_filename(filename)
    
    # If secure_filename stripped everything except extension, use original with basic cleaning
    if cleaned and '.' in filename:
        original_name, original_ext = os.path.splitext(filename)
        if original_name and cleaned == original_ext.lstrip('.'):
            # secure_filename removed the name part, use original with manual cleaning
            cleaned = filename.replace(' ', '_')
            # Remove dangerous characters but keep Unicode
            dangerous_chars = '<>:"/\\|?*'
            for char in dangerous_chars:
                cleaned = cleaned.replace(char, '_')
        else:
            # secure_filename worked normally, just replace spaces
            cleaned = cleaned.replace(' ', '_')
    elif not cleaned:
        # Empty result, use original with basic cleaning
        cleaned = filename.replace(' ', '_')
    else:
        # Just replace spaces in the secure result
        cleaned = cleaned.replace(' ', '_')
    
    # Additional cleaning: replace dots in filename (but not extension) with underscores
    if '.' in cleaned:
        name, ext = os.path.splitext(cleaned)
        name = name.replace('.', '_')
        cleaned = f"{name}{ext}"
    
    return cleaned

def create_image_with_padding(image, target_size=(600, 600), padding_color=(255, 255, 255)):
    """
    Изменение размера изображения с сохранением соотношения сторон и добавлением отступов до нужного размера.
    """
    width, height = image.size
    target_width, target_height = target_size

    # Расчет коэффициента масштабирования
    ratio = min(target_width / width, target_height / height)
    new_width = int(width * ratio)
    new_height = int(height * ratio)
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    # Создание нового изображения с отступами
    new_image = Image.new('RGB', target_size, padding_color)
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    new_image.paste(resized_image, (paste_x, paste_y))

    return new_image