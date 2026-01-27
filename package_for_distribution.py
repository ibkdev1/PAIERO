#!/usr/bin/env python3
"""
PAIERO Distribution Packager
Creates distribution packages for macOS and Windows
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

VERSION = "1.0.0"

def get_platform():
    """Get current platform"""
    if sys.platform == 'darwin':
        return 'mac'
    elif sys.platform == 'win32':
        return 'windows'
    else:
        return 'linux'

def clean_dist():
    """Clean distribution folder"""
    print("Cleaning old distribution files...")
    dist_dir = Path('dist')
    if dist_dir.exists():
        # Keep the app/exe, remove old zips
        for f in dist_dir.glob('*.zip'):
            f.unlink()
            print(f"  Removed {f.name}")

def build_app():
    """Build the application"""
    print("\nBuilding application...")
    result = subprocess.run([sys.executable, 'build_app.py'], capture_output=False)
    return result.returncode == 0

def create_mac_package():
    """Create macOS distribution package"""
    print("\nCreating macOS distribution package...")

    dist_dir = Path('dist')
    package_dir = dist_dir / 'PAIERO-Mac'
    app_path = dist_dir / 'PAIERO.app'

    if not app_path.exists():
        print("  Error: PAIERO.app not found. Run build first.")
        return False

    # Create package directory
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)

    # Copy app
    print("  Copying PAIERO.app...")
    shutil.copytree(app_path, package_dir / 'PAIERO.app')

    # Copy installer files
    installer_dir = Path('installer')
    if installer_dir.exists():
        print("  Adding installer scripts...")
        for f in ['install_mac.command', 'install_mac.sh', 'README_INSTALL.txt']:
            src = installer_dir / f
            if src.exists():
                shutil.copy2(src, package_dir / f)
                # Make shell scripts executable
                if f.endswith(('.sh', '.command')):
                    os.chmod(package_dir / f, 0o755)

    # Create zip
    print("  Creating PAIERO-Mac.zip...")
    zip_path = dist_dir / f'PAIERO-Mac-v{VERSION}'
    shutil.make_archive(str(zip_path), 'zip', dist_dir, 'PAIERO-Mac')

    # Get size
    zip_file = Path(f'{zip_path}.zip')
    size_mb = zip_file.stat().st_size / (1024 * 1024)

    print(f"  Created: {zip_file.name} ({size_mb:.1f} MB)")
    return True

def create_windows_package():
    """Create Windows distribution package"""
    print("\nCreating Windows distribution package...")

    dist_dir = Path('dist')
    package_dir = dist_dir / 'PAIERO-Windows'
    exe_path = dist_dir / 'PAIERO.exe'
    internal_dir = dist_dir / '_internal'

    if not exe_path.exists():
        print("  Error: PAIERO.exe not found. Run build first.")
        return False

    # Create package directory
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)

    # Copy exe
    print("  Copying PAIERO.exe...")
    shutil.copy2(exe_path, package_dir / 'PAIERO.exe')

    # Copy _internal if exists (PyInstaller dependencies)
    if internal_dir.exists():
        print("  Copying dependencies...")
        shutil.copytree(internal_dir, package_dir / '_internal')

    # Copy installer files
    installer_dir = Path('installer')
    if installer_dir.exists():
        print("  Adding installer scripts...")
        for f in ['install_windows.bat', 'uninstall_windows.bat', 'README_INSTALL.txt']:
            src = installer_dir / f
            if src.exists():
                shutil.copy2(src, package_dir / f)

    # Create zip
    print("  Creating PAIERO-Windows.zip...")
    zip_path = dist_dir / f'PAIERO-Windows-v{VERSION}'
    shutil.make_archive(str(zip_path), 'zip', dist_dir, 'PAIERO-Windows')

    # Get size
    zip_file = Path(f'{zip_path}.zip')
    size_mb = zip_file.stat().st_size / (1024 * 1024)

    print(f"  Created: {zip_file.name} ({size_mb:.1f} MB)")
    return True

def main():
    """Main packaging process"""
    print("=" * 60)
    print("PAIERO Distribution Packager")
    print(f"Version: {VERSION}")
    print(f"Platform: {get_platform()}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    platform = get_platform()

    # Check if we should build
    if '--skip-build' not in sys.argv:
        if not build_app():
            print("\nBuild failed!")
            sys.exit(1)

    # Clean old packages
    clean_dist()

    # Create platform-specific package
    if platform == 'mac':
        success = create_mac_package()
    elif platform == 'windows':
        success = create_windows_package()
    else:
        print(f"\nUnsupported platform: {platform}")
        sys.exit(1)

    if not success:
        print("\nPackaging failed!")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("PACKAGING COMPLETE!")
    print("=" * 60)

    dist_dir = Path('dist')
    print("\nDistribution files created:")
    for f in dist_dir.glob('*.zip'):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.name} ({size_mb:.1f} MB)")

    print("\nNext steps:")
    print("  1. Test the package on a clean machine")
    print("  2. Upload to your distribution platform")
    print("  3. Share the download link with users")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
