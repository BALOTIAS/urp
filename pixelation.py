from PIL import Image
import os


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


def process_image(image, resize_amount, mask_file=None, asset_name=None):
    """
    Process an image with pixelation, offset correction, and optional masking.

    Args:
        image: PIL Image object (RGBA)
        resize_amount: Float between 0 and 1
        mask_file: Path to mask file or None
        asset_name: Name of the asset (for logging)

    Returns:
        Processed PIL Image
    """
    # Extract alpha mask
    alpha_mask = image.split()[-1].convert("L")

    # Apply pixelation
    pixelated = pixelate_image(image, resize_amount)

    # Apply offset correction
    corrected = apply_offset_correction(pixelated, resize_amount)

    # Apply mask if it exists
    if mask_file and os.path.exists(mask_file):
        custom_mask = Image.open(mask_file).convert("L")
        final_image = Image.composite(corrected, image, custom_mask)
        print(
            f"[UNOFFICIAL RETRO PATCH] Pixelates {asset_name or os.path.basename(mask_file)} with mask..."
        )
    else:
        final_image = corrected
        if asset_name:
            print(f"[UNOFFICIAL RETRO PATCH] Pixelates {asset_name} without mask...")

    # Restore original alpha
    final_image.putalpha(alpha_mask)

    return final_image
