"""
Build script for Stalker executable using PyInstaller.

This script packages the application into a single executable file with:
- Onefile mode for easy distribution
- Optional icon support
- Exclusion of test files
- Default config.json bundled
- First-run migration to user home directory

Usage:
    python build_exe.py [--icon path/to/icon.ico]
"""
import sys
import os
import shutil
import subprocess
import hashlib
from pathlib import Path
import argparse


def calculate_checksum(filepath, algorithm='sha256'):
    """Calculate checksum of a file."""
    hash_func = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def get_version():
    """Extract version from code or use default."""
    version_file = Path(__file__).parent / "core" / "__init__.py"
    if version_file.exists():
        with open(version_file, 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    return "2.0.0"


def clean_build_dirs():
    """Clean build and dist directories."""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"Cleaning {dir_name}/ directory...")
            shutil.rmtree(dir_path)


def build_executable(icon_path=None):
    """Build the executable using PyInstaller."""
    print("=" * 60)
    print("Building Stalker Executable")
    print("=" * 60)
    
    version = get_version()
    print(f"Version: {version}")
    
    # Determine path separator for PyInstaller's --add-data
    # PyInstaller uses ; on Windows, : on Unix-like systems
    path_sep = ';' if os.name == 'nt' else ':'
    
    # Base PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',  # No console window
        '--name', 'Stalker',
        '--clean',
        '--noconfirm',
        
        # Exclude test directories and files
        '--exclude-module', 'tests',
        '--exclude-module', 'pytest',
        '--exclude-module', 'unittest',
        
        # Add hooks directory
        '--additional-hooks-dir', 'hooks',
        
        # Add data files (use platform-appropriate path separator)
        '--add-data', f'config.default.json{path_sep}.',
        
        # Hidden imports that might be needed
        '--hidden-import', 'PySide6.QtCore',
        '--hidden-import', 'PySide6.QtGui',
        '--hidden-import', 'PySide6.QtWidgets',
        '--hidden-import', 'keyboard',
        '--hidden-import', 'mouse',
        '--hidden-import', 'psutil',
        '--hidden-import', 'watchdog',
        
        # Entry point
        'main.py'
    ]
    
    # Add icon if provided
    if icon_path and Path(icon_path).exists():
        cmd.extend(['--icon', icon_path])
        print(f"Using icon: {icon_path}")
    else:
        print("No icon specified or icon file not found")
    
    print("\nRunning PyInstaller...")
    print(" ".join(cmd))
    print()
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print("\n✅ Build successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error: {e}")
        return False


def generate_checksums():
    """Generate checksum files for the executable."""
    dist_dir = Path('dist')
    exe_file = dist_dir / 'Stalker.exe'
    
    if not exe_file.exists():
        print("❌ Executable not found!")
        return False
    
    print("\nGenerating checksums...")
    
    # Calculate checksums
    sha256_hash = calculate_checksum(exe_file, 'sha256')
    md5_hash = calculate_checksum(exe_file, 'md5')
    
    # Write checksums to file
    checksum_file = dist_dir / 'Stalker.exe.checksums.txt'
    with open(checksum_file, 'w') as f:
        f.write(f"File: Stalker.exe\n")
        f.write(f"SHA-256: {sha256_hash}\n")
        f.write(f"MD5: {md5_hash}\n")
    
    print(f"SHA-256: {sha256_hash}")
    print(f"MD5: {md5_hash}")
    print(f"Checksums saved to: {checksum_file}")
    
    return True


def create_build_info():
    """Create a build info file with version and build details."""
    from datetime import datetime
    
    dist_dir = Path('dist')
    version = get_version()
    
    info_file = dist_dir / 'BUILD_INFO.txt'
    with open(info_file, 'w') as f:
        f.write(f"Stalker v{version}\n")
        f.write(f"Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Python Version: {sys.version}\n")
        f.write("\nRuntime Requirements:\n")
        f.write("- Windows 10/11 (64-bit)\n")
        f.write("- Microsoft Visual C++ Redistributable (usually pre-installed)\n")
        f.write("\nFor more information, see README.md\n")
    
    print(f"Build info saved to: {info_file}")


def main():
    """Main build process."""
    parser = argparse.ArgumentParser(description='Build Stalker executable')
    parser.add_argument('--icon', help='Path to icon file (.ico)', default=None)
    parser.add_argument('--no-clean', action='store_true', help='Skip cleaning build directories')
    args = parser.parse_args()
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Clean build directories unless --no-clean is specified
    if not args.no_clean:
        clean_build_dirs()
    
    # Build executable
    success = build_executable(args.icon)
    if not success:
        sys.exit(1)
    
    # Generate checksums
    if not generate_checksums():
        sys.exit(1)
    
    # Create build info
    create_build_info()
    
    print("\n" + "=" * 60)
    print("✅ Build completed successfully!")
    print("=" * 60)
    print("\nOutput files:")
    dist_dir = Path('dist')
    for file in dist_dir.iterdir():
        if file.is_file():
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"  - {file.name} ({size_mb:.2f} MB)")
    print()


if __name__ == '__main__':
    main()
