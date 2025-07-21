import os
import sys
import shutil
import subprocess
import platform


def build_executable():
    print("Starting build process for Unofficial Retro Patch for Windows...")

    # Only allow building on Windows
    if platform.system() != "Windows":
        print("Error: This build script is designed to run only on Windows systems.")
        sys.exit(1)

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
    # If UnityPy uses a 'resources' directory or other data files, you must include them here.
    # Example (uncomment and adjust the path if needed):
    # cmd.append("--add-data=venv/Lib/site-packages/UnityPy/resources;UnityPy/resources")
    # If you get 'No module named UnityPy.resources' at runtime, locate the resources directory in your UnityPy installation and add it here.
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
