import os
import warnings
import UnityPy
import configparser
from PIL import Image
from dotenv import load_dotenv
from monkeypatch.compress_etcpak import compress_etcpak

load_dotenv()
DEBUG_ENABLED = os.getenv("DEBUG_ENABLED", "False").lower() in ("true", "1", "yes")

# As of UnityPy 1.22.3, the compress_etcpak function has an issue with the bc7 compression,
# as it passes `None` as the second argument to `etcpak.compress_bc7`, which is not supported.
# (even though it should be supported according to the etcpak documentation)
try:
    from UnityPy.export import Texture2DConverter

    Texture2DConverter.compress_etcpak = compress_etcpak
    print("[UNOFFICIAL RETRO PATCH] Successfully monkey patched compress_etcpak.")
except (AttributeError, ImportError) as e:
    warnings.warn(
        f"[UNOFFICIAL RETRO PATCH] Failed to monkey patch compress_etcpak: {e}. Ensure UnityPy structure is as expected."
    )


def pixelate_edition(edition_name: str):
    config = configparser.ConfigParser()
    config.read("config.ini")

    print(f"\n[UNOFFICIAL RETRO PATCH] Pixelating edition: {edition_name}")

    target_folder = os.getenv(
        f"{edition_name.upper().replace(' ', '_')}_TARGET_FOLDER"
    ) or config.get(edition_name, "target_folder", fallback=f"downloads/{edition_name}")
    if not os.path.exists(target_folder):
        raise FileNotFoundError(f"Target folder '{target_folder}' does not exist.")

    assets_folder = config.get(
        edition_name, "assets_folder", fallback=f"{edition_name}_Data/resources.assets"
    )
    if not os.path.exists(os.path.join(target_folder, assets_folder)):
        raise FileNotFoundError(
            f"Assets folder '{assets_folder}' does not exist in target folder '{target_folder}'."
        )

    masks_folder = config.get(
        edition_name, "masks_folder", fallback=f"masks/{edition_name}"
    )
    if not os.path.exists(masks_folder):
        raise FileNotFoundError(f"Masks folder '{masks_folder}' does not exist.")

    debug_pixelated_folder = config.get(
        edition_name,
        "debug_pixelated_folder",
        fallback=f"downloads/{edition_name}/pixelated",
    )

    if os.getenv(f"{edition_name.upper().replace(' ', '_')}_RESIZE_AMOUNT"):
        resize_amount = float(
            os.getenv(f"{edition_name.upper().replace(' ', '_')}_RESIZE_AMOUNT")
        )
    else:
        resize_amount = config.getfloat(edition_name, "resize_amount", fallback=0.5)

    if os.getenv(f"{edition_name.upper().replace(' ', '_')}_PIXELATE_FILES"):
        pixelate_files = os.getenv(
            f"{edition_name.upper().replace(' ', '_')}_PIXELATE_FILES"
        )
    else:
        pixelate_files = config.get(
            edition_name, "pixelate_files", fallback=""
        )


    # Get the list of files to pixelate from the config
    pixelate_files = list(
        filter(
            None,
            map(
                str.strip,
                pixelate_files.split(","),
            ),
        )
    )
    if len(pixelate_files) == 0:
        print(f"[UNOFFICIAL RETRO PATCH] No files to pixelate for {edition_name}.")
        return

    # Group pixelate_files by their directory,
    # so we can process them by the asset file (to avoid loading all asset files via UnityPy)
    pixelate_asset_files = {}
    for pixelate_file in pixelate_files:
        asset_dir = os.path.dirname(pixelate_file)

        # e.g. system/Stronghold Definitive Edition/Stronghold Definitive Edition_Data/resources.assets
        asset_file = os.path.join(target_folder, assets_folder, asset_dir)
        if not os.path.exists(asset_file):
            warnings.warn(
                f"[UNOFFICIAL RETRO PATCH] Asset file directory '{asset_file}' does not exist. Skipping pixelation for {pixelate_file}."
            )
            continue

        # e.g. texture_name.png
        pixelate_file = os.path.basename(pixelate_file)
        [name, extension] = os.path.splitext(pixelate_file)

        if asset_file not in pixelate_asset_files:
            # e.g. resources.assets
            pixelate_asset_files[asset_file] = []

        pixelate_asset_files[asset_file].append(
            {
                "asset_dir": asset_dir,  # e.g. resources.assets
                "asset": pixelate_file,  # e.g. texture_name.png
                "asset_name": name,  # e.g. texture_name
                "asset_ext": extension,  # e.g. .png
                "mask_file": os.path.join(
                    masks_folder, f"{asset_dir}/{pixelate_file}"
                ),  # e.g. masks/Stronghold Definitive Edition/resources.assets/texture_name.png
            }
        )

    for asset_file in pixelate_asset_files:
        try:
            env = UnityPy.load(asset_file)

            for obj in env.objects:
                if obj.type.name == "Texture2D":
                    pixelate_entries = pixelate_asset_files[asset_file]

                    for pixelate_entry in pixelate_entries:
                        asset_dir, asset, asset_name, asset_ext, mask_file = (
                            pixelate_entry.values()
                        )

                        try:
                            data = obj.read()

                            if (
                                not hasattr(data, "m_Name")
                                or not data.m_Name == asset_name
                            ):
                                continue

                            if hasattr(data, "image"):
                                # Load the asset image
                                asset_image = data.image.convert("RGBA")

                                # Extract the alpha mask from the image
                                asset_alpha_mask = asset_image.split()[-1].convert("L")

                                # Pixelate the image, using a simple pixelation effect.
                                # Create a pixelated version of the image
                                pixelated_image = asset_image.resize(
                                    (
                                        round(asset_image.width * resize_amount),
                                        round(asset_image.height * resize_amount),
                                    ),
                                    Image.Resampling.NEAREST,
                                )
                                # Scale it back up to the original size
                                pixelated_image = pixelated_image.resize(
                                    (asset_image.width, asset_image.height),
                                    Image.Resampling.NEAREST,
                                )

                                # Apply a mask if it exists;
                                # use the mask to apply the pixelation only where the mask is white.
                                if os.path.exists(mask_file):
                                    # Load the mask
                                    custom_mask = Image.open(mask_file).convert("L")

                                    # Combine the pixelated image with the original image using the custom mask,
                                    # so that the pixelated image is only visible where the mask is white.
                                    final_image = Image.composite(
                                        pixelated_image, asset_image, custom_mask
                                    )

                                    print(
                                        f"[UNOFFICIAL RETRO PATCH] Pixelates {asset_name} with mask..."
                                    )
                                else:
                                    print(
                                        f"[UNOFFICIAL RETRO PATCH] Pixelates {asset_name} without mask..."
                                    )
                                    final_image = pixelated_image

                                # Apply the original alpha mask to the final image,
                                # so that the transparency is preserved.
                                # This is important as otherwise the final image might create artifacts in game.
                                final_image.putalpha(asset_alpha_mask)

                                # Save the pixelated image back to the asset
                                data.image = final_image

                                if DEBUG_ENABLED:
                                    # Save the pixelated image to a file for debugging
                                    debug_path = os.path.join(
                                        debug_pixelated_folder, asset_dir, asset
                                    )
                                    os.makedirs(
                                        os.path.dirname(debug_path), exist_ok=True
                                    )
                                    final_image.save(debug_path)
                                    print(
                                        f"[UNOFFICIAL RETRO PATCH | DEBUG] Successfully pixelated {asset_name} in {debug_path}"
                                    )
                                else:
                                    # Save the modified asset back to the asset file
                                    data.save()
                                    print(
                                        f"[UNOFFICIAL RETRO PATCH] Successfully pixelated {asset_name} in {asset_file}"
                                    )
                            else:
                                warnings.warn(
                                    f"[UNOFFICIAL RETRO PATCH] {asset_name} in {asset_file} does not have an image attribute."
                                )
                        except Exception as e:
                            warnings.warn(f"Failed to pixelate {asset_file}: {e}")

        except Exception as e:
            warnings.warn(
                f"[UNOFFICIAL RETRO PATCH] Failed to load asset file '{asset_file}': {e}"
            )
            continue


def main():
    print("\n[UNOFFICIAL RETRO PATCH] Starting pixelation process...")
    pixelate_edition("Stronghold Definitive Edition")
    print("\n[UNOFFICIAL RETRO PATCH] Finished pixelation process.")


if __name__ == "__main__":
    main()
