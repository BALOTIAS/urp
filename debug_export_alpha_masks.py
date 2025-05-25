import configparser
import os


def debug_export_alpha_masks(
    source_folder: str, destination_folder: str, fuzzy: bool = False
):
    if not os.path.exists(source_folder):
        raise FileNotFoundError(f"Source folder '{source_folder}' does not exist.")

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder, exist_ok=True)
        print(f"Destination folder '{destination_folder}' created.")

    # iterate over all files in source folder and extract alpha masks
    for root, dirs, files in os.walk(source_folder):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            # load the image
            try:
                from PIL import Image

                img = Image.open(file_path).convert("RGBA")
            except Exception as e:
                print(f"Failed to load image {file_name}: {e}")
                continue

            # create a mask from the alpha channel
            try:
                mask = img.split()[-1]  # Get the alpha channel
                if fuzzy:
                    mask = mask.point(lambda p: 255 if p > 0 else 0)

            except Exception as e:
                print(f"Failed to create mask for {file_name}: {e}")
                continue

            # save the mask
            try:
                # use same path structure as the source folder
                dest = os.path.join(
                    destination_folder, os.path.relpath(file_path, source_folder)
                )
                dest, ext = os.path.splitext(dest)
                dest = dest + ".png"
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                mask.save(dest)

                print(f"Generated mask for {file_name} at {dest}")
            except Exception as e:
                print(f"Failed to save mask for {file_name}: {e}")


def main():
    print("\n[DEBUG EXPORT ALPHA MASKS] Generating masks...")

    config = configparser.ConfigParser()
    config.read("config.ini")

    source_folder = config.get(
        "Stronghold Definitive Edition",
        "debug_unpacked_folder",
        fallback="dev/unpacked/Stronghold Definitive Edition",
    )
    destination_folder = config.get(
        "Stronghold Definitive Edition",
        "debug_exported_alpha_masks_folder",
        fallback="dev/debug_exported_alpha_masks_folder/Stronghold Definitive Edition",
    )

    debug_export_alpha_masks(source_folder, destination_folder)

    print("\n[DEBUG EXPORT ALPHA MASKS] Finished generating masks.")


if __name__ == "__main__":
    main()
