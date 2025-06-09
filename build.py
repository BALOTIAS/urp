import os
import sys
import shutil
import subprocess
import platform


def build_executable():
    print("Starting build process for Unofficial Retro Patch for Windows...")

    # Check if we're on Windows
    if platform.system() != "Windows":
        print("Error: This build script is designed to run only on Windows systems.")
        print("Please run this script on a Windows machine to create the executable.")
        return

    # Make sure PyInstaller is installed
    try:
        import PyInstaller

        print(f"PyInstaller version {PyInstaller.__version__} found")
    except ImportError:
        print("PyInstaller is not installed. Installing it now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        import PyInstaller

        print(f"PyInstaller version {PyInstaller.__version__} installed")

    # Define platform-neutral path separators for the command
    icon_path = os.path.join("assets", "icon", "urp.ico")

    # Define PyInstaller command for Windows
    cmd = [sys.executable, "-m", "PyInstaller"]

    # Build options
    cmd.extend(
        [
            "--name=UnofficialRetroPatch",
            "--onefile",
            "--windowed",
            "--clean",
            f"--icon={icon_path}",
            "--target-arch=x86_64",
            "--uac-admin",
            "--add-data=config.ini;.",
            "--add-data=assets;assets",
        ]
    )

    # Include README.md file if it exists
    if os.path.exists("README.md"):
        cmd.append("--add-data=README.md;.")

    # Main script to execute
    cmd.append("gui.py")

    print(f"Running command: {' '.join(cmd)}")

    # Make sure dist directory exists
    os.makedirs("dist", exist_ok=True)

    # Run PyInstaller
    try:
        subprocess.check_call(cmd)
        print("\nBuild process completed successfully!")
        print(
            f"Executable created at: {os.path.abspath(os.path.join('dist', 'UnofficialRetroPatch.exe'))}"
        )
    except subprocess.CalledProcessError as e:
        print(f"\nBuild process failed with error code {e.returncode}")
        print("Please check the error message above.")
        return

    # Check if we should make a full distribution package
    make_dist_package = (
        input(
            "Would you like to create a distribution package with all required files? (y/n): "
        )
        .lower()
        .strip()
    )

    if make_dist_package == "y" or make_dist_package == "yes":
        create_distribution_package()


def create_distribution_package():
    print("\nCreating Windows distribution package...")

    # Create distribution directory
    dist_dir = "distribution"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)

    os.makedirs(dist_dir)

    # Copy executable
    exe_name = "UnofficialRetroPatch.exe"
    exe_path = os.path.join("dist", exe_name)

    if not os.path.exists(exe_path):
        print(
            f"Warning: Could not find '{exe_path}'. The build process may have failed."
        )
        return

    shutil.copy(exe_path, dist_dir)

    # Copy essential files
    if os.path.exists("config.ini"):
        shutil.copy("config.ini", dist_dir)

    # Copy assets folder
    if os.path.exists("assets"):
        shutil.copytree("assets", os.path.join(dist_dir, "assets"))

    # Copy README.md if it exists
    if os.path.exists("README.md"):
        shutil.copy("README.md", dist_dir)

    # Create empty directories that might be needed
    os.makedirs(os.path.join(dist_dir, "downloads"), exist_ok=True)

    print(f"\nDistribution package created at: {os.path.abspath(dist_dir)}")
    print("You can distribute this folder to end users.")


if __name__ == "__main__":
    build_executable()
