import os
import sys
import shutil
import subprocess
import platform
import importlib.util


def build_executable():
    print("Starting build process for Unofficial Retro Patch for Windows...")

    # Only allow building on Windows (relaxed for testing on other OS)
    if platform.system() != "Windows":
        print("Warning: This build script is designed for Windows output, but running on non-Windows system. Output may not be runnable on this OS.")

    # Make sure PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version {PyInstaller.__version__} found")
    except ImportError:
        print("PyInstaller is not installed. Installing it now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        import PyInstaller
        print(f"PyInstaller version {PyInstaller.__version__} installed")

    icon_path = os.path.join("assets", "icon", "urp.ico")
    cmd = [sys.executable, "-m", "PyInstaller"]
    cmd.extend([
        "--name=UnofficialRetroPatch",
        "--onefile",
        "--windowed",
        "--clean",
        f"--icon={icon_path}",
        "--target-arch=x86_64",
        "--uac-admin",
        "--add-data=config.ini;.",
        "--add-data=assets;assets",
    ])
    if os.path.exists("README.md"):
        cmd.append("--add-data=README.md;.")

    # --- UNITYPY RESOURCES PATCH ---
    # Dynamically find UnityPy resources directory and add to PyInstaller if it exists
    unitypy_spec = importlib.util.find_spec("UnityPy")
    if unitypy_spec and unitypy_spec.submodule_search_locations:
        unitypy_dir = unitypy_spec.submodule_search_locations[0]
        resources_dir = os.path.join(unitypy_dir, "resources")
        if os.path.exists(resources_dir):
            # Use correct path separator for PyInstaller
            sep = ";" if platform.system() == "Windows" else ":"
            cmd.append(f"--add-data={resources_dir}{sep}UnityPy/resources")
            print(f"Added UnityPy resources: {resources_dir}")
        else:
            print("Warning: UnityPy resources directory not found. If you get 'No module named UnityPy.resources' at runtime, check your UnityPy installation.")
    else:
        print("Warning: UnityPy package not found in current environment. Make sure it is installed.")
    # --------------------------------

    cmd.append("gui.py")
    print(f"Running command: {' '.join(cmd)}")
    os.makedirs("dist", exist_ok=True)
    try:
        subprocess.check_call(cmd)
        print("\nBuild process completed successfully!")
        print(f"Executable created at: {os.path.abspath(os.path.join('dist', 'UnofficialRetroPatch.exe'))}")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild process failed with error code {e.returncode}")
        print("Please check the error message above.")
        sys.exit(1)

    # Create a distribution package with all required files
    create_distribution_package()

def create_distribution_package():
    print("\nCreating Windows distribution package...")
    dist_dir = "distribution"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    exe_name = "UnofficialRetroPatch.exe"
    exe_path = os.path.join("dist", exe_name)
    shutil.copy2(exe_path, dist_dir)
    # Copy config
    if os.path.exists("config.ini"):
        shutil.copy2("config.ini", dist_dir)
    # Copy README
    if os.path.exists("README.md"):
        shutil.copy2("README.md", dist_dir)
    # Copy assets
    if os.path.exists("assets"):
        shutil.copytree("assets", os.path.join(dist_dir, "assets"))
    print(f"Distribution package created at: {os.path.abspath(dist_dir)}")

if __name__ == "__main__":
    build_executable()
