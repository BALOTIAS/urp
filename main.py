import os
import warnings
import UnityPy
import configparser
from dotenv import load_dotenv
from unitypy_fixes import patch_unitypy
from pixelation import process_image
import gc
import time
import psutil


load_dotenv()
DEBUG_ENABLED = os.getenv("DEBUG_ENABLED", "False").lower() in ("true", "1", "yes")


patch_unitypy()


def log_memory_usage(logger=None):
    """Log current memory usage for debugging."""
    if logger is None:
        logger = print
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        logger(f"[UNOFFICIAL RETRO PATCH] Memory usage: {memory_mb:.1f} MB")
    except ImportError:
        pass  # psutil not available

def is_file_locked(filepath):
    """Check if file is locked by another process."""
    try:
        with open(filepath, 'r+b'):
            return False
    except (PermissionError, OSError):
        return True

def pixelate_edition(edition_name: str, logger=None, black_shadows=False):
    if logger is None:
        logger = print
    config = configparser.ConfigParser()
    config.read("config.ini")

    logger(f"\n[UNOFFICIAL RETRO PATCH] Pixelating edition: {edition_name}")
    log_memory_usage(logger)

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
        edition_name, "masks_folder", fallback=f"assets/masks/{edition_name}"
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
        pixelate_files = config.get(edition_name, "pixelate_files", fallback="")

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
        logger(f"[UNOFFICIAL RETRO PATCH] No files to pixelate for {edition_name}.")
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
                ),  # e.g. assets/masks/Stronghold Definitive Edition/resources.assets/texture_name.png
            }
        )

    # Calculate total textures across all asset files for overall progress
    total_textures_across_files = 0
    for asset_file in pixelate_asset_files:
        total_textures_across_files += len(pixelate_asset_files[asset_file])
    
    processed_textures_total = 0
    logger(f"[UNOFFICIAL RETRO PATCH] Total textures to process: {total_textures_across_files}")
    log_memory_usage(logger)

    # Store pairs of (original_file, temp_file) to process after the loop
    files_to_replace = []

    for asset_file in pixelate_asset_files:
        try:
            # --- Restore latest backup if it exists ---
            backup_no = 1
            backup_file = f"{asset_file}.backup{backup_no:03}"
            latest_backup = None
            while os.path.exists(backup_file):
                latest_backup = backup_file
                backup_no += 1
                backup_file = f"{asset_file}.backup{backup_no:03}"
            if latest_backup:
                logger(f"[UNOFFICIAL RETRO PATCH] Restoring latest backup before pixelation: {latest_backup}")
                if os.path.exists(asset_file):
                    os.remove(asset_file)
                os.rename(latest_backup, asset_file)

            env = UnityPy.load(asset_file)
            total_textures = sum(1 for obj in env.objects if obj.type.name == "Texture2D")
            processed_textures = 0

            # Get total number of textures to process across all asset files
            total_asset_files = len(pixelate_asset_files)
            current_asset_file_index = list(pixelate_asset_files.keys()).index(asset_file) + 1
            
            logger(f"[UNOFFICIAL RETRO PATCH] Processing asset file {current_asset_file_index}/{total_asset_files}: {os.path.basename(asset_file)}")

            # Prepare data for parallel processing
            texture_data_list = []
            for obj in env.objects:
                if obj.type.name == "Texture2D":
                    # Check if this object matches any of the textures we need to process
                    for pixelate_entry in pixelate_asset_files[asset_file]:
                        asset_dir, asset, asset_name, asset_ext, mask_file = (
                            pixelate_entry.values()
                        )
                        texture_data_list.append((obj, pixelate_entry, asset_file))

            # Process textures sequentially for now (simpler and more reliable)
            processed_textures = 0
            modified_objects = []  # Track which objects were modified
            
            for obj, pixelate_entry, asset_file in texture_data_list:
                asset_dir, asset, asset_name, asset_ext, mask_file = pixelate_entry.values()
                
                try:
                    data = obj.read()
                    
                    if not hasattr(data, "m_Name") or not data.m_Name == asset_name:
                        continue
                    
                    if hasattr(data, "image"):
                        processed_textures_total += 1
                        processed_textures += 1
                        logger(f"[UNOFFICIAL RETRO PATCH] Pixelating texture {processed_textures_total}/{total_textures_across_files}: {asset_name}")
                        
                        data.image = process_image(
                            image=data.image,
                            resize_amount=resize_amount,
                            mask_file=mask_file,
                            asset_name=asset_name,
                            black_shadows=black_shadows,
                        )
                        data.save()
                        modified_objects.append(obj)  # Track that this object was modified
                        
                        logger(f"[UNOFFICIAL RETRO PATCH] Successfully pixelated {asset_name} in {asset_file}")
                        
                        if DEBUG_ENABLED:
                            debug_path = os.path.join(
                                debug_pixelated_folder, asset_dir, asset
                            )
                            os.makedirs(
                                os.path.dirname(debug_path), exist_ok=True
                            )
                            data.image.save(debug_path)
                            logger(f"[UNOFFICIAL RETRO PATCH | DEBUG] Successfully exported pixelated {asset_name} in {debug_path}")
                    else:
                        warnings.warn(f"[UNOFFICIAL RETRO PATCH] {asset_name} in {asset_file} does not have an image attribute.")
                except Exception as e:
                    warnings.warn(f"Failed to pixelate {asset_name} in {asset_file}: {e}")
            
            if processed_textures == 0:
                logger(f"[UNOFFICIAL RETRO PATCH] No textures to process in {asset_file}")
            else:
                logger(f"[UNOFFICIAL RETRO PATCH] Modified {len(modified_objects)} objects in {asset_file}")

            # Save the modified asset file to temp location
            modified_asset_file = asset_file + ".tmp"
            try:
                logger(f"[UNOFFICIAL RETRO PATCH] Saving modified asset file to: {modified_asset_file}")
                with open(modified_asset_file, "wb") as f:
                    f.write(env.file.save())
                
                # Verify the temp file was created
                if os.path.exists(modified_asset_file):
                    file_size = os.path.getsize(modified_asset_file)
                    logger(f"[UNOFFICIAL RETRO PATCH] Temporary file created: {modified_asset_file} ({file_size} bytes)")
                    # Store the files for later processing
                    files_to_replace.append((asset_file, modified_asset_file))
                else:
                    raise Exception("Temporary file was not created")

                logger(
                    f"[UNOFFICIAL RETRO PATCH] Prepared modified asset file for replacement: {asset_file}"
                )
                log_memory_usage(logger)
            except Exception as e:
                warnings.warn(f"Failed to save modified asset file '{asset_file}': {e}")
                continue
        except Exception as e:
            warnings.warn(
                f"[UNOFFICIAL RETRO PATCH] Failed to load asset file '{asset_file}': {e}"
            )
            continue

    return files_to_replace

def replace_files(files_to_replace, logger=None):
    # Process all file replacements after the loop to ensure no asset files are being accessed
    logger(f"[UNOFFICIAL RETRO PATCH] Processing {len(files_to_replace)} file replacements...")
    for original_file, temp_file in files_to_replace:
        max_wait = 30  # seconds
        wait_time = 0
        while is_file_locked(original_file) and wait_time < max_wait:
            logger(f"[UNOFFICIAL RETRO PATCH] File locked, waiting... ({wait_time}s)")
            time.sleep(2)
            wait_time += 2

        if is_file_locked(original_file):
            warnings.warn(f"File still locked after {max_wait}s: {original_file}")
            continue

        try:
            # Create backup
            backup_no = 1
            backup_file = f"{original_file}.backup{backup_no:03}"
            while os.path.exists(backup_file):
                backup_no += 1
                backup_file = f"{original_file}.backup{backup_no:03}"

            logger(f"[UNOFFICIAL RETRO PATCH] Creating backup: {original_file} -> {backup_file}")
            os.rename(original_file, backup_file)

            logger(f"[UNOFFICIAL RETRO PATCH] Replacing original with modified file: {temp_file} -> {original_file}")
            os.rename(temp_file, original_file)

            logger(f"[UNOFFICIAL RETRO PATCH] Successfully replaced asset file: {original_file}")
        except Exception as e:
            warnings.warn(f"Failed to replace asset file '{original_file}': {e}")
            # Try to restore original if backup was created
            if os.path.exists(backup_file) and not os.path.exists(original_file):
                try:
                    os.rename(backup_file, original_file)
                    logger(f"[UNOFFICIAL RETRO PATCH] Restored original file from backup: {original_file}")
                except Exception as restore_e:
                    warnings.warn(f"Failed to restore original file '{original_file}': {restore_e}")

def main():
    print("\n[UNOFFICIAL RETRO PATCH] Starting pixelation process...")
    pixelate_edition("Stronghold Definitive Edition")
    print("\n[UNOFFICIAL RETRO PATCH] Finished pixelation process.")


if __name__ == "__main__":
    main()
