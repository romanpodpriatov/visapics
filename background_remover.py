# background_remover.py

import numpy as np
from PIL import Image
import logging

def remove_background_and_make_white(image, ort_session):
    """
    Удаление фона изображения и замена его на белый цвет с использованием модели сегментации.
    """
    # Оригинальный размер
    original_size = image.size

    # Изменение размера до входного размера модели
    input_size = (1024, 1024)
    image_resized = image.resize(input_size, Image.LANCZOS)
    img = np.array(image_resized).astype(np.float32)

    # Нормализация
    img = img / 255.0
    img = (img - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / \
          np.array([0.229, 0.224, 0.225], dtype=np.float32)

    # Формат CHW
    img = np.transpose(img, (2, 0, 1))

    # Добавление batch dimension
    img = np.expand_dims(img, axis=0).astype(np.float32)

    # Прогон через модель
    ort_inputs = {ort_session.get_inputs()[0].name: img}
    ort_outs = ort_session.run(None, ort_inputs)
    pred = ort_outs[0][0]

    # Сигмоида и маска
    pred = 1 / (1 + np.exp(-pred))
    pred = np.squeeze(pred)

    # Изменение размера маски до оригинального
    mask = Image.fromarray((pred * 255).astype(np.uint8)).resize(original_size, Image.BILINEAR)

    # Создание белого фона
    white_bg = Image.new('RGB', original_size, (255, 255, 255))

    # Обеспечение наличия альфа-канала
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Применение маски
    image.putalpha(mask)

    # Наложение на белый фон
    result_image = Image.alpha_composite(white_bg.convert('RGBA'), image)

    return result_image.convert('RGB')