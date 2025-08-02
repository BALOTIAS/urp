from PIL import Image
import os
import numpy as np

def pixelate_image(image, resize_amount):
    """
    Apply pixelation effect to an image with the specified resize amount.

    Args:
        image: PIL Image object
        resize_amount: Float between 0 and 1, smaller values mean more pixelation

    Returns:
        PIL Image with pixelation effect applied
    """
    # Downscale the image
    small_image = image.resize(
        (
            round(image.width * resize_amount),
            round(image.height * resize_amount),
        ),
        Image.Resampling.NEAREST,
    )
    # Upscale back to original size
    return small_image.resize(
        (image.width, image.height),
        Image.Resampling.NEAREST,
    )


def apply_black_shadows(image, shadow_color=(0, 0, 0, 255)):
    """
    Apply black shadows to an image by replacing semi-transparent areas with solid black.

    Args:
        image: PIL Image object (RGBA)
        shadow_color: Tuple of (R, G, B, A) for shadow color, defaults to black

    Returns:
        PIL Image with black shadows applied
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Convert to numpy array for faster pixel operations
    img_array = np.array(image)

    # Create boolean mask for pixels that should be replaced
    # Semi-transparent black pixels (shadow-like) (R=0, G=0, B=0, 127 < A < 255)
    mask = (
        (img_array[:, :, 0] == 0) &  # R = 0
        (img_array[:, :, 1] == 0) &  # G = 0
        (img_array[:, :, 2] == 0) &  # B = 0
        (img_array[:, :, 3] > 127) &  # A > 127
        (img_array[:, :, 3] < 255)  # A < 255
    )

    # Apply shadow color to masked pixels
    img_array[mask] = shadow_color

    # Convert back to PIL Image
    return Image.fromarray(img_array, 'RGBA')


def apply_offset_correction(pixelated_image, resize_amount):
    """
    Apply pixel offset correction based on resize amount to fix spillover issues.

    Args:
        pixelated_image: PIL Image object that has been pixelated
        resize_amount: Float between 0 and 1, used to calculate the offset

    Returns:
        PIL Image with offset correction applied
    """
    # Calculate required offset
    pixel_offset = round((1 / resize_amount) / 2)

    if pixel_offset <= 0:
        return pixelated_image

    width, height = pixelated_image.size
    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Main image with offset
    result.paste(pixelated_image, (pixel_offset, pixel_offset))

    # Fix right edge
    right_strip = pixelated_image.crop((0, 0, 1, height))
    for i in range(pixel_offset):
        result.paste(right_strip, (width - 1 - i, pixel_offset))

    # Fix bottom edge
    bottom_strip = pixelated_image.crop((0, 0, width, 1))
    for i in range(pixel_offset):
        result.paste(bottom_strip, (pixel_offset, height - 1 - i))

    # Fix corner pixels
    corner_pixel = pixelated_image.crop((0, 0, 1, 1))
    for i in range(pixel_offset):
        for j in range(pixel_offset):
            result.paste(corner_pixel, (width - 1 - i, height - 1 - j))

    return result


def process_image(image, resize_amount, mask_file=None, asset_name=None, black_shadows=False):
    """
    Process an image with pixelation, offset correction, optional masking, and black shadows.

    Args:
        image: PIL Image object (RGBA)
        resize_amount: Float between 0 and 1
        mask_file: Path to mask file or None
        asset_name: Name of the asset (for logging)
        black_shadows: Boolean to enable black shadows feature

    Returns:
        Processed PIL Image
    """
    import warnings

    file_name = asset_name or os.path.basename(mask_file)

    # Extract alpha mask
    alpha_mask = image.split()[-1].convert("L")
    hard_alpha_mask = alpha_mask.point(lambda p: 255 if p > 0 else 0)

    # Apply pixelation
    pixelated = pixelate_image(image, resize_amount)

    # Apply black shadows if enabled
    if black_shadows:
        pixelated = apply_black_shadows(pixelated)
        if asset_name:
            print(f"[UNOFFICIAL RETRO PATCH] Applied black shadows to {file_name}")

    # Apply offset correction
    # Doesn't work well as of now, so it's commented out
    # corrected = apply_offset_correction(pixelated, resize_amount)

    # Apply mask if it exists, otherwise generate from alpha
    if mask_file and os.path.exists(mask_file):
        custom_mask = Image.open(mask_file).convert("L")
        custom_mask.paste(hard_alpha_mask, (0, 0)) # Paste the original hard alpha mask
        final_image = Image.composite(pixelated, image, custom_mask)
        print(
            f"[UNOFFICIAL RETRO PATCH] Pixelates {file_name} with mask..."
        )
    else:
        # Use the alpha channel as a smooth mask for blending
        final_image = Image.composite(pixelated, image, hard_alpha_mask)
        if asset_name:
            warnings.warn(f"[UNOFFICIAL RETRO PATCH] Pixelates {file_name} without custom mask, using alpha channel as mask.")

    # If black shadows are enabled, we want to have the pixelated shadow areas, so we can't simply use the alpha mask
    if black_shadows:
        # Restore original alpha
        pixelated_mask = pixelated.split()[-1].convert("L")

        # combine the alpha mask with the pixelated mask, ensuring the alpha mask uses pixelated mask,
        # this will pixelate the shadow areas
        alpha_mask = Image.composite(pixelated_mask, alpha_mask, hard_alpha_mask)

    final_image.putalpha(alpha_mask)

    return final_image
