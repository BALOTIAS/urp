# Unofficial Retro Patch - Refactored Version

A professional, well-structured Python application for applying pixelation effects to Stronghold game textures.

## 🏗️ Architecture Overview

The application has been completely refactored with a professional, modular architecture:

### Core Structure
```
src/
├── __init__.py                 # Package initialization
├── main.py                     # CLI entry point
├── gui_main.py                 # GUI entry point
├── cli_main.py                 # Alternative CLI entry point
├── config/                     # Configuration management
│   ├── __init__.py
│   ├── settings.py             # Application settings and constants
│   └── config_manager.py       # Configuration file management
├── core/                       # Core application logic
│   ├── __init__.py
│   └── application.py          # Main application coordinator
├── game/                       # Game-specific operations
│   ├── __init__.py
│   ├── asset_manager.py        # Asset file management
│   └── unity_processor.py      # Unity asset processing
├── gui/                        # GUI components
│   ├── __init__.py
│   ├── main_window.py          # Main window
│   └── components.py           # Reusable GUI components
├── processing/                 # Image processing
│   ├── __init__.py
│   ├── image_processor.py      # Image processing operations
│   └── pixelation_processor.py # Pixelation workflow
└── utils/                      # Utility functions
    ├── __init__.py
    ├── file_utils.py           # File operations
    ├── memory_utils.py         # Memory management
    └── validation_utils.py     # Validation functions
```

## 🚀 Key Improvements

### 1. **Separation of Concerns**
- **Configuration**: Centralized settings management with environment variable support
- **Processing**: Dedicated image processing pipeline
- **GUI**: Modular, reusable components
- **Game Logic**: Specialized Unity asset handling
- **Utilities**: Common functionality extracted into utility classes

### 2. **Type Hints & Documentation**
- Full type annotations throughout the codebase
- Comprehensive docstrings for all classes and methods
- Clear parameter and return type documentation

### 3. **Error Handling & Validation**
- Robust validation at multiple levels
- Proper error recovery mechanisms
- Detailed error messages and logging

### 4. **Memory Management**
- Automatic memory monitoring and cleanup
- Garbage collection optimization
- Memory usage logging

### 5. **Modular Design**
- Each component has a single responsibility
- Easy to test individual components
- Simple to extend with new features

## 🛠️ Usage

### GUI Mode
```bash
python -m src.gui_main
```

### CLI Mode
```bash
# Process default edition
python -m src.cli_main

# Process specific edition
python -m src.cli_main --edition "Stronghold Crusader Definitive Edition"

# Apply black shadows
python -m src.cli_main --black-shadows

# List available editions
python -m src.cli_main --list-editions
```

### Programmatic Usage
```python
from src.core.application import Application

app = Application()
files_to_replace = app.pixelate_edition("Stronghold Definitive Edition", black_shadows=True)
app.replace_files(files_to_replace)
```

## 🔧 Configuration

The application uses a hierarchical configuration system:

1. **Default Settings**: Hardcoded in `src/config/settings.py`
2. **Configuration File**: `config.ini` for edition-specific settings
3. **Environment Variables**: Override any setting at runtime

### Environment Variables
- `DEBUG_ENABLED`: Enable debug mode
- `{EDITION}_TARGET_FOLDER`: Override target folder for specific edition
- `{EDITION}_RESIZE_AMOUNT`: Override pixelation amount
- `{EDITION}_PIXELATE_FILES`: Override files to pixelate

## 🧪 Testing

The modular design makes testing straightforward:

```python
from src.processing.image_processor import ImageProcessor
from src.utils.validation_utils import ValidationUtils

# Test image processing
result = ImageProcessor.pixelate_image(test_image, 0.5)

# Test validation
is_valid, errors = ValidationUtils.validate_game_directory(path, edition)
```

## 📦 Building

Use the new build script for the refactored version:

```bash
python build_refactored.py
```

## 🔄 Migration from Old Version

The refactored version maintains full compatibility with existing:
- Configuration files (`config.ini`)
- Asset files and masks
- Game installations

No changes to existing setups are required.

## 🎯 Benefits of Refactoring

1. **Maintainability**: Clear structure makes it easy to understand and modify
2. **Testability**: Each component can be tested in isolation
3. **Extensibility**: Easy to add new features or game editions
4. **Reliability**: Better error handling and validation
5. **Performance**: Optimized memory management and processing
6. **Documentation**: Comprehensive type hints and docstrings

## 🏛️ Design Patterns Used

- **Factory Pattern**: Application class creates and coordinates components
- **Strategy Pattern**: Different processing strategies for different image types
- **Observer Pattern**: GUI components observe and react to state changes
- **Command Pattern**: CLI commands are encapsulated in separate entry points
- **Singleton Pattern**: Settings and configuration managers

## 📈 Performance Improvements

- **Memory Management**: Automatic cleanup and monitoring
- **File Operations**: Optimized backup and restore operations
- **Image Processing**: Efficient pixelation algorithms
- **GUI Responsiveness**: Threaded operations prevent UI freezing

This refactored version represents a professional, production-ready codebase that follows Python best practices and modern software engineering principles.