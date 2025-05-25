import os
import warnings
import UnityPy
import configparser


def unpack_all_assets(source_folder: str, destination_folder: str):
    if not os.path.exists(source_folder):
        raise FileNotFoundError(f"Source folder '{source_folder}' does not exist.")

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder, exist_ok=True)
        print(f"Destination folder '{destination_folder}' created.")

    # iterate over all files in source folder
    for root, dirs, files in os.walk(source_folder):
        for file_name in files:
            # generate file_path
            file_path = os.path.join(root, file_name)
            # load that file via UnityPy.load
            env = UnityPy.load(file_path)

            # iterate over internal objects
            for obj in env.objects:
                # process specific object types
                if obj.type.name in ["Texture2D"]:
                    # parse the object data
                    data = obj.read()

                    # create destination path
                    if hasattr(data, "name"):
                        # if the object has a name attribute, use it
                        name = data.name
                    elif hasattr(data, "m_Name"):
                        # if the object has a m_Name attribute, use it
                        name = data.m_Name
                    else:
                        # fallback to a generic name
                        name = "unknown_asset"

                    try:
                        dest = os.path.join(destination_folder, f"{file_name}/{name}")
                        os.makedirs(os.path.dirname(dest), exist_ok=True)

                        # make sure that the extension is correct
                        # you probably only want to do so with images/textures
                        dest, ext = os.path.splitext(dest)
                        dest = dest + ".png"

                        img = data.image
                        img.save(dest)
                        print(f"Unpacked {name} from {file_name}")
                    except Exception as e:
                        warnings.warn(f"Failed to unpack {name} from {file_name}: {e}")


def main():
    print("\n[DEBUG UNPACK ASSETS] Unpacking assets...")

    config = configparser.ConfigParser()
    config.read("config.ini")

    source_folder = config.get(
        "Stronghold Definitive Edition",
        "debug_source_folder",
        fallback="downloads/Stronghold Definitive Edition",
    )
    destination_folder = config.get(
        "Stronghold Definitive Edition",
        "debug_unpacked_folder",
        fallback="downloads/unpacked",
    )

    unpack_all_assets(source_folder, destination_folder)

    print("\n[DEBUG UNPACK ASSETS] Unpacking completed.")


if __name__ == "__main__":
    main()
