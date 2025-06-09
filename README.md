# Unofficial Retro Patch

Relive the classic visual style! This Unofficial Retro Patch brings back the beloved pixel art charm to [Stronghold: Definitive Edition](https://playstronghold.com/).

> **Disclaimer**
> 
> This project is not affiliated with or endorsed by [Firefly Studios](https://fireflyworlds.com/).
> The patch does not distribute any original files from Firefly Studios. It only modifies assets already present on the user's system or adds community-created content.

## Overview

The Unofficial Retro Patch (URP) is a modification tool designed to selectively pixelate textures in [Stronghold: Definitive Edition](https://playstronghold.com/), bringing back the nostalgic visual style of the original game while maintaining the benefits of the definitive edition.

## Features

- **Selective Pixelation**: Apply pixelation effects only to specific textures using mask files
- **Configurable Settings**: Adjust pixelation amount and target files via config.ini
- **Debug Mode**: Optional debug mode to save pixelated textures for verification

## Requirements

- Python 3.x
- Pip or Pipenv for dependency management
- [Stronghold: Definitive Edition](https://playstronghold.com/) game files

## Installation

1. Clone this repository:
    ```
    git clone https://github.com/BALOTIAS/urp.git
    cd urp
    ```
   
2. Install dependencies:
    ```
    pipenv install
    ```
    Or with pip:
    ```
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory (optional):
    ```
    cp .env.example .env
    ```

4. Configure the `.env` file with your game's file paths and pixelation settings.

## Usage

1. Make sure your game files are in the correct location as specified in your config.ini
2. Run the patch:
    ```
    python main.py
    ```

3. Launch the game and enjoy the retro visual style!

## Configuration

Edit `config.ini` to customize the patch:

```ini
[Stronghold Definitive Edition]
target_folder = downloads/Stronghold Definitive Edition
assets_folder = Stronghold Definitive Edition_Data/resources.assets
masks_folder = assets/masks/Stronghold Definitive Edition
debug_pixelated_folder = downloads/Stronghold Definitive Edition/pixelated
pixel_amount = 2
pixelate_files = resources.assets/texture1.png, resources.assets/texture2.png
```

- `target_folder`: Directory containing game files
- `assets_folder`: Path to game assets relative to target folder
- `masks_folder`: Directory containing mask files for selective pixelation
- `debug_pixelated_folder`: Directory to save debug output when debug mode is enabled
- `pixel_amount`: Level of pixelation (higher values = more pixelated)
- `pixelate_files`: Comma-separated list of texture files to pixelate

## Creating Masks

Masks are grayscale PNG files that control where pixelation is applied:
- White areas (255, 255, 255) will be pixelated
- Black areas (0, 0, 0) will remain unchanged
- Gray areas will be partially pixelated

Place mask files in the `masks` folder with the same folder structure as the original textures, e.g. `masks/Stronghold Definitive Edition/resources.assets/AllTileSprites.png`.

## License

See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Uses [UnityPy](https://github.com/K0lb3/UnityPy) for handling Unity assets
- Special thanks to [Firefly Studios](https://fireflyworlds.com/) for the creation of the Stronghold series ❤️❤️❤️
