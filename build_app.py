#!/usr/bin/env python3
"""
PAIERO Application Builder
Builds standalone application for distribution
"""

import sys
import subprocess
import os
import shutil
from pathlib import Path

def clean_build():
    """Remove old build artifacts"""
    print("🧹 Cleaning old build files...")
    dirs_to_remove = ['build', 'dist']
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")

def build_app():
    """Build the application using PyInstaller"""
    print("\n🔨 Building PAIERO application...")

    # PyInstaller command with optimizations
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "PAIERO.spec"
    ]

    print(f"   Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)

    if result.returncode != 0:
        print("\n❌ Build failed!")
        return False

    return True

def verify_build():
    """Verify the build was successful"""
    print("\n✅ Verifying build...")

    if sys.platform == 'darwin':
        app_path = 'dist/PAIERO.app'
        if os.path.exists(app_path):
            size = get_folder_size(app_path) / (1024 * 1024)
            print(f"   ✓ PAIERO.app created ({size:.1f} MB)")
            return True
    elif sys.platform == 'win32':
        exe_path = 'dist/PAIERO.exe'
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"   ✓ PAIERO.exe created ({size:.1f} MB)")
            return True

    print("   ❌ Application not found in dist/")
    return False

def get_folder_size(folder_path):
    """Calculate total size of folder"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size

def main():
    """Main build process"""
    print("="*60)
    print("PAIERO Application Builder")
    print("="*60)

    # Step 1: Clean
    clean_build()

    # Step 2: Build
    if not build_app():
        sys.exit(1)

    # Step 3: Verify
    if not verify_build():
        sys.exit(1)

    print("\n" + "="*60)
    print("✅ BUILD SUCCESSFUL!")
    print("="*60)

    if sys.platform == 'darwin':
        print("\n📦 Application location:")
        print("   dist/PAIERO.app")
        print("\n🚀 To run:")
        print("   Double-click dist/PAIERO.app")
        print("   Or: open dist/PAIERO.app")
    elif sys.platform == 'win32':
        print("\n📦 Application location:")
        print("   dist\\PAIERO.exe")
        print("\n🚀 To run:")
        print("   Double-click dist\\PAIERO.exe")

    print("\n💡 To share with others:")
    print("   Zip the dist/PAIERO.app (or .exe) and share")
    print("="*60)

if __name__ == '__main__':
    main()
