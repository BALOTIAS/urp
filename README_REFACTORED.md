# Unofficial Retro Patch - Refactored Version

A professional Python application for applying pixelation effects to Stronghold game textures, creating a nostalgic retro experience.

## 🏗️ Project Structure

The codebase has been completely refactored into a professional, modular structure:

```
src/
├── __init__.py                 # Main package
├── main.py                     # CLI entry point
├── gui_app.py                  # GUI entry point
├── core/                       # Core business logic
│   ├── __init__.py
│   ├── config.py               # Configuration management
│   ├── unity_processor.py      # Unity asset processing
│   └── file_utils.py           # File operations and utilities
├── image_processing/           # Image manipulation
│   ├── __init__.py
│   └── pixelation.py           # Pixelation effects
├── gui/                        # User interface
│   ├── __init__.py
│   └── main_window.py          # Main GUI window
└── utils/                      # Utilities and patches
    ├── __init__.py
    └── unitypy_patch.py        # UnityPy fixes

# Entry points
run_gui.py                      # GUI launcher
run_cli.py                      # CLI launcher
build_refactored.py             # Build script for new structure
```

## 🚀 Quick Start

### Running the GUI
```bash
python run_gui.py
```

### Running the CLI
```bash
python run_cli.py
```

### Building the Executable
```bash
python build_refactored.py
```

## 📦 Key Improvements

### 1. **Modular Architecture**
- **Separation of Concerns**: Each module has a single responsibility
- **Clean Interfaces**: Well-defined APIs between components
- **Testability**: Each module can be tested independently

### 2. **Configuration Management**
- **Centralized Config**: All settings managed in `src/core/config.py`
- **Environment Variables**: Support for environment variable overrides
- **Validation**: Automatic validation of configuration and paths

### 3. **Image Processing**
- **Dedicated Module**: All image operations in `src/image_processing/`
- **Reusable Functions**: Clean, documented image processing functions
- **Type Hints**: Full type annotations for better IDE support

### 4. **Unity Asset Processing**
- **Professional Class**: `UnityProcessor` handles all Unity operations
- **Error Handling**: Comprehensive error handling and recovery
- **Progress Tracking**: Built-in progress reporting

### 5. **GUI Improvements**
- **Component-Based**: GUI split into logical components
- **Thread Safety**: Proper threading for long operations
- **Responsive Design**: Non-blocking UI during processing

## 🔧 Development

### Adding New Features

1. **Configuration**: Add new settings to `src/core/config.py`
2. **Business Logic**: Implement in appropriate `src/core/` module
3. **UI Components**: Add to `src/gui/` if needed
4. **Image Processing**: Extend `src/image_processing/` for new effects

### Testing

```bash
# Run tests (when implemented)
python -m pytest tests/

# Run linting
python -m flake8 src/
python -m mypy src/
```

### Code Style

The refactored code follows professional Python standards:
- **Type Hints**: Full type annotations
- **Docstrings**: Comprehensive documentation
- **Error Handling**: Proper exception handling
- **Logging**: Structured logging throughout

## 📋 Migration Guide

### From Old Structure to New

| Old File | New Location | Purpose |
|----------|--------------|---------|
| `main.py` | `src/main.py` | CLI entry point |
| `gui.py` | `src/gui/main_window.py` | Main GUI window |
| `pixelation.py` | `src/image_processing/pixelation.py` | Image processing |
| `unitypy_fixes.py` | `src/utils/unitypy_patch.py` | UnityPy patches |

### Entry Points

| Old | New |
|-----|-----|
| `python main.py` | `python run_cli.py` |
| `python gui.py` | `python run_gui.py` |
| `python build.py` | `python build_refactored.py` |

## 🛠️ Dependencies

The refactored version maintains the same dependencies but with better organization:

```txt
UnityPy>=1.22.3
Pillow>=9.0.0
numpy>=1.21.0
psutil>=5.8.0
python-dotenv>=0.19.0
```

## 🎯 Benefits of Refactoring

1. **Maintainability**: Code is easier to understand and modify
2. **Extensibility**: New features can be added without affecting existing code
3. **Testing**: Each component can be tested independently
4. **Documentation**: Clear module structure with comprehensive docstrings
5. **Type Safety**: Full type hints for better IDE support and error catching
6. **Error Handling**: Robust error handling throughout the application
7. **Logging**: Structured logging for better debugging

## 🔍 Code Quality Features

- **Type Annotations**: Full type hints for all functions and classes
- **Documentation**: Comprehensive docstrings for all public APIs
- **Error Handling**: Proper exception handling with meaningful error messages
- **Logging**: Structured logging with consistent message format
- **Configuration**: Centralized configuration management
- **Validation**: Input validation and path checking
- **Thread Safety**: Proper threading for GUI operations

## 📝 Contributing

When contributing to the refactored codebase:

1. **Follow the Structure**: Place code in appropriate modules
2. **Add Type Hints**: Include type annotations for all functions
3. **Write Docstrings**: Document all public functions and classes
4. **Handle Errors**: Implement proper error handling
5. **Test Changes**: Ensure compatibility with existing functionality

## 🚨 Important Notes

- The refactored version maintains full backward compatibility with existing configuration files
- All existing functionality is preserved but organized better
- The new structure makes it easier to add new game editions or features
- Build process has been updated to work with the new structure

## 📄 License

This project maintains the same license as the original codebase.