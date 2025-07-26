import os
import warnings
import UnityPy
import configparser
from dotenv import load_dotenv
from unitypy_fixes import patch_unitypy
from pixelation import process_image
import gc
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
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


def pixelate_edition(edition_name: str, logger=None):
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
                    for pixelate_entry in pixelate_asset_files[asset_file]:
                        asset_dir, asset, asset_name, asset_ext, mask_file = (
                            pixelate_entry.values()
                        )
                        texture_data_list.append((obj, pixelate_entry, asset_file))

            # Process textures in parallel with progress callback
            def progress_callback(current, total):
                nonlocal processed_textures_total
                # Calculate the base count for this asset file
                base_count = processed_textures_total
                # Update with current progress within this asset file
                current_total = base_count + current
                logger(f"[UNOFFICIAL RETRO PATCH] Pixelating texture {current_total}/{total_textures_across_files}")
            
            processed_results = process_texture_batch(
                texture_data_list, 
                resize_amount, 
                logger, 
                progress_callback
            )
            
            processed_textures = len(processed_results)
            processed_textures_total += processed_textures

            # Save the modified asset file
            modified_asset_file = asset_file + ".tmp"
            with open(modified_asset_file, "wb") as f:
                f.write(env.file.save())

            # Explicitly release UnityPy objects and collect garbage
            del env
            gc.collect()
            
            # Small delay to allow memory to be freed
            time.sleep(0.1)

            # Backup original and replace
            backup_no = 1
            backup_file = f"{asset_file}.backup{backup_no:03}"
            while os.path.exists(backup_file):
                backup_no += 1
                backup_file = f"{asset_file}.backup{backup_no:03}"

            os.rename(asset_file, backup_file)
            os.rename(modified_asset_file, asset_file)

            logger(
                f"[UNOFFICIAL RETRO PATCH] Successfully saved modified asset file: {asset_file}"
            )
            log_memory_usage(logger)
        except Exception as e:
            warnings.warn(
                f"[UNOFFICIAL RETRO PATCH] Failed to load asset file '{asset_file}': {e}"
            )
            continue


def process_texture_batch(texture_data_list, resize_amount, logger=None, progress_callback=None):
    """
    Process a batch of textures in parallel.
    
    Args:
        texture_data_list: List of tuples (obj, pixelate_entry, asset_file)
        resize_amount: Resize amount for pixelation
        logger: Logger function
        progress_callback: Callback for progress updates
    
    Returns:
        List of processed texture data
    """
    if logger is None:
        logger = print
    
    processed_count = 0
    total_count = len(texture_data_list)
    results = []
    
    def process_single_texture(texture_data):
        obj, pixelate_entry, asset_file = texture_data
        asset_dir, asset, asset_name, asset_ext, mask_file = pixelate_entry.values()
        
        try:
            data = obj.read()
            
            if not hasattr(data, "m_Name") or not data.m_Name == asset_name:
                return None
            
            if hasattr(data, "image"):
                data.image = process_image(
                    image=data.image,
                    resize_amount=resize_amount,
                    mask_file=mask_file,
                    asset_name=asset_name,
                )
                data.save()
                return (obj, asset_name, asset_file)
            else:
                warnings.warn(f"[UNOFFICIAL RETRO PATCH] {asset_name} in {asset_file} does not have an image attribute.")
                return None
        except Exception as e:
            warnings.warn(f"Failed to pixelate {asset_name} in {asset_file}: {e}")
            return None
        finally:
            # Force garbage collection after each texture to manage memory
            gc.collect()
    
    # Use ThreadPoolExecutor for parallel processing
    # Limit workers to avoid memory issues - reduce for large textures
    max_workers = min(2, total_count)  # Reduced to 2 workers to manage memory better
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_texture = {
            executor.submit(process_single_texture, texture_data): texture_data 
            for texture_data in texture_data_list
        }
        
        # Process completed tasks
        for future in as_completed(future_to_texture):
            result = future.result()
            processed_count += 1
            
            if result:
                obj, asset_name, asset_file = result
                results.append((obj, asset_name, asset_file))
                logger(f"[UNOFFICIAL RETRO PATCH] Successfully pixelated {asset_name} in {asset_file}")
            
            # Update progress every few textures to avoid GUI spam
            if processed_count % max(1, total_count // 10) == 0 or processed_count == total_count:
                if progress_callback:
                    progress_callback(processed_count, total_count)
    
    return results


def main():
    print("\n[UNOFFICIAL RETRO PATCH] Starting pixelation process...")
    pixelate_edition("Stronghold Definitive Edition")
    print("\n[UNOFFICIAL RETRO PATCH] Finished pixelation process.")


if __name__ == "__main__":
    main()
