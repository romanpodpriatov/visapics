# background_remover.py

import numpy as np
from PIL import Image
import logging
from typing import Tuple # For type hinting

def remove_background_and_make_white(image, ort_session, target_color_rgb: Tuple[int, int, int] = (255, 255, 255), return_mask: bool = False):
    """
    Remove image background and replace it with target_color_rgb using segmentation model.
    """
    # Original size
    original_size = image.size

    # Resize to model input size
    input_size = (1024, 1024)
    image_resized = image.resize(input_size, Image.LANCZOS)
    img = np.array(image_resized).astype(np.float32)

    # Normalization
    img = img / 255.0
    img = (img - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / \
          np.array([0.229, 0.224, 0.225], dtype=np.float32)

    # CHW format
    img = np.transpose(img, (2, 0, 1))

    # Add batch dimension
    img = np.expand_dims(img, axis=0).astype(np.float32)

    # Run through model
    ort_inputs = {ort_session.get_inputs()[0].name: img}
    ort_outs = ort_session.run(None, ort_inputs)
    pred = ort_outs[0][0]

    # Sigmoid and mask
    pred = 1 / (1 + np.exp(-pred))
    pred = np.squeeze(pred)

    # Resize mask to original size
    mask = Image.fromarray((pred * 255).astype(np.uint8)).resize(original_size, Image.BILINEAR)

    # Create background with specified color
    background_img = Image.new('RGB', original_size, target_color_rgb)

    # Ensure alpha channel presence
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Apply mask
    image.putalpha(mask)

    # Composite onto background
    result_image = Image.alpha_composite(background_img.convert('RGBA'), image)

    # Return mask if requested for hair detection
    if return_mask:
        # Convert mask to numpy array for face analyzer
        mask_array = np.array(mask)
        return result_image.convert('RGB'), mask_array
    else:
        return result_image.convert('RGB')