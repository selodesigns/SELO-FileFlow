#!/usr/bin/env python3
"""
Simplified build script for SELO FileFlow.
Creates a standalone executable using PyInstaller directly.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_executable():
    """Build the executable package for SELO FileFlow."""
    print("Building SELO FileFlow executable...")

    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Prepare directories
    build_dir = Path("build")
    dist_dir = Path("dist")
    resources_dir = Path("resources")
    icon_path = resources_dir / "icon.ico"

    # Clean build and dist folders
    for dir_path in [build_dir, dist_dir]:
        if dir_path.exists():
            try:
                shutil.rmtree(str(dir_path))
            except PermissionError as e:
                print(f"Warning: Could not completely clean {dir_path} - some files may be in use.\n{e}")
        dir_path.mkdir(exist_ok=True)

    # Ensure resources/icon.ico exists
    if not resources_dir.exists():
        resources_dir.mkdir(exist_ok=True)
    if not icon_path.exists() or icon_path.stat().st_size == 0:
        print("Creating placeholder icon file...")
        icon_path.touch()

    # Ensure LICENSE exists
    license_file = Path("LICENSE")
    if not license_file.exists():
        print("Creating LICENSE file...")
        with open(license_file, "w") as f:
            f.write("MIT License\n\nCopyright (c) 2025 SELOdev\n\nPermission is hereby granted...")

    # PyInstaller build command
    print("Running PyInstaller...")
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "run_fileflow.py",
        "--name=SELO-FileFlow",
        "--windowed",
        "--clean",
        "--noconfirm",
        f"--add-data=config{os.pathsep}config",
        f"--add-data=LICENSE{os.pathsep}.",
        f"--icon={icon_path}"
    ]

    try:
        subprocess.check_call(cmd)
        exe_path = os.path.abspath("dist/SELO-FileFlow/SELO-FileFlow.exe")
        print(f"\n✅ Build completed successfully!")
        print(f"Executable available at: {exe_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building executable: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()
