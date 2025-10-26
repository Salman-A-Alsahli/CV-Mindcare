"""
Build Script for CV-Mindcare Windows Executable
----------------------------------------------
Creates a standalone Windows executable using PyInstaller.
"""

import PyInstaller.__main__
import os
import sys
import shutil
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"

# Launcher entry point
LAUNCHER_SCRIPT = PROJECT_ROOT / "launcher" / "launcher.py"

# Application metadata
APP_NAME = "CV-Mindcare"
VERSION = "0.1.0"
AUTHOR = "Salman A. Alsahli"

def clean_build_dirs():
    """Clean previous build artifacts."""
    print("Cleaning previous builds...")
    
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    
    # Remove spec file if exists
    spec_file = PROJECT_ROOT / f"{APP_NAME}.spec"
    if spec_file.exists():
        os.remove(spec_file)
    
    print("✓ Build directories cleaned")


def collect_data_files():
    """Collect additional data files to include in executable."""
    data_files = []
    
    # Include backend files
    backend_dir = PROJECT_ROOT / "backend"
    data_files.append((str(backend_dir / "*.py"), "backend"))
    data_files.append((str(backend_dir / "sensors"), "backend/sensors"))
    
    # Include frontend files
    frontend_dir = PROJECT_ROOT / "frontend"
    data_files.append((str(frontend_dir / "index.html"), "frontend"))
    data_files.append((str(frontend_dir / "css"), "frontend/css"))
    data_files.append((str(frontend_dir / "js"), "frontend/js"))
    
    # Include docs
    docs_dir = PROJECT_ROOT / "docs"
    if docs_dir.exists():
        data_files.append((str(docs_dir), "docs"))
    
    return data_files


def build_executable():
    """Build the executable using PyInstaller."""
    print(f"Building {APP_NAME} v{VERSION}...")
    
    # PyInstaller arguments
    pyinstaller_args = [
        str(LAUNCHER_SCRIPT),
        
        # Output options
        f"--name={APP_NAME}",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        
        # Single file vs directory
        "--onedir",  # Use --onefile for single exe (slower startup)
        
        # Windows options
        "--windowed",  # No console window (use --console for debugging)
        f"--icon={PROJECT_ROOT / 'assets' / 'icon.ico'}" if (PROJECT_ROOT / "assets" / "icon.ico").exists() else "",
        
        # Hidden imports (modules not detected automatically)
        "--hidden-import=customtkinter",
        "--hidden-import=cv2",
        "--hidden-import=sounddevice",
        "--hidden-import=psutil",
        "--hidden-import=fastapi",
        "--hidden-import=uvicorn",
        "--hidden-import=pydantic",
        "--hidden-import=PIL",
        "--hidden-import=PIL._tkinter_finder",
        
        # Collect all submodules
        "--collect-all=customtkinter",
        "--collect-all=uvicorn",
        
        # Additional data files
        f"--add-data={PROJECT_ROOT / 'backend'};backend",
        f"--add-data={PROJECT_ROOT / 'frontend'};frontend",
        f"--add-data={PROJECT_ROOT / 'README.md'};.",
        f"--add-data={PROJECT_ROOT / 'LICENSE'};.",
        
        # Exclude unnecessary modules to reduce size
        "--exclude-module=matplotlib",
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        
        # Clean build
        "--clean",
        
        # Logging
        "--log-level=INFO",
    ]
    
    # Remove empty arguments
    pyinstaller_args = [arg for arg in pyinstaller_args if arg]
    
    print("PyInstaller arguments:")
    for arg in pyinstaller_args:
        print(f"  {arg}")
    
    # Run PyInstaller
    try:
        PyInstaller.__main__.run(pyinstaller_args)
        print(f"\n✓ Build complete! Executable located at: {DIST_DIR / APP_NAME}")
        return True
    except Exception as e:
        print(f"\n✗ Build failed: {e}")
        return False


def create_readme():
    """Create README for distribution."""
    dist_readme = DIST_DIR / APP_NAME / "README.txt"
    
    content = f"""
{APP_NAME} v{VERSION}
{'=' * (len(APP_NAME) + len(VERSION) + 3)}

Thank you for downloading CV-Mindcare!

Quick Start:
1. Run {APP_NAME}.exe
2. The launcher will perform system checks
3. Click "Start Dashboard" to launch the application
4. Your browser will open with the dashboard

System Requirements:
- Windows 10 or Windows 11
- Webcam (optional)
- Microphone (optional)
- 4GB RAM minimum
- 2GB free disk space

The application will:
- Monitor your workspace environment
- Detect faces and emotions
- Measure ambient noise levels
- Track greenery in camera view
- Display real-time statistics

For more information, documentation, and support:
https://github.com/Salman-A-Alsahli/CV-Mindcare

Created by: {AUTHOR}
License: MIT
Version: {VERSION}
"""
    
    with open(dist_readme, 'w') as f:
        f.write(content)
    
    print(f"✓ README created at: {dist_readme}")


def post_build_cleanup():
    """Cleanup after build."""
    # Optionally remove build directory to save space
    # if BUILD_DIR.exists():
    #     shutil.rmtree(BUILD_DIR)
    pass


def main():
    """Main build process."""
    print(f"\n{'=' * 60}")
    print(f"  {APP_NAME} Build Script v{VERSION}")
    print(f"{'=' * 60}\n")
    
    # Check if launcher script exists
    if not LAUNCHER_SCRIPT.exists():
        print(f"✗ Error: Launcher script not found at {LAUNCHER_SCRIPT}")
        sys.exit(1)
    
    # Step 1: Clean previous builds
    clean_build_dirs()
    
    # Step 2: Build executable
    if not build_executable():
        print("\n✗ Build failed!")
        sys.exit(1)
    
    # Step 3: Create distribution README
    create_readme()
    
    # Step 4: Post-build cleanup
    post_build_cleanup()
    
    print(f"\n{'=' * 60}")
    print(f"  Build Complete!")
    print(f"{'=' * 60}")
    print(f"\nExecutable location: {DIST_DIR / APP_NAME / f'{APP_NAME}.exe'}")
    print(f"Distribution folder: {DIST_DIR / APP_NAME}")
    print(f"\nTo distribute:")
    print(f"  1. Zip the entire '{APP_NAME}' folder")
    print(f"  2. Share the zip file with users")
    print(f"  3. Users extract and run {APP_NAME}.exe")
    print()


if __name__ == "__main__":
    main()
