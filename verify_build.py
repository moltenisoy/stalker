"""
Verification script to check that the build artifacts are correct.

Usage:
    python verify_build.py

This script checks:
- Executable exists
- Checksum file exists and matches
- BUILD_INFO file exists
- File sizes are reasonable
"""
import sys
from pathlib import Path
import hashlib


def calculate_checksum(filepath, algorithm='sha256'):
    """Calculate checksum of a file."""
    hash_func = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def verify_build():
    """Verify the build artifacts."""
    import platform
    
    dist_dir = Path('dist')
    # Use platform-appropriate executable extension
    exe_name = 'Stalker.exe' if platform.system() == 'Windows' else 'Stalker'
    exe_file = dist_dir / exe_name
    checksum_file = dist_dir / f'{exe_name}.checksums.txt'
    build_info_file = dist_dir / 'BUILD_INFO.txt'
    
    print("=" * 60)
    print("Stalker Build Verification")
    print("=" * 60)
    print()
    
    # Check if dist directory exists
    if not dist_dir.exists():
        print("❌ dist/ directory not found!")
        print("   Run 'python build_exe.py' to create the build")
        return False
    
    # Check if executable exists
    print("Checking for executable...")
    if not exe_file.exists():
        print("❌ Stalker.exe not found in dist/")
        return False
    
    exe_size = exe_file.stat().st_size / (1024 * 1024)
    print(f"✅ Stalker.exe found ({exe_size:.2f} MB)")
    
    # Check file size is reasonable (should be > 10 MB and < 500 MB)
    if exe_size < 10:
        print(f"⚠️  Warning: Executable size seems too small ({exe_size:.2f} MB)")
        print("   Expected size: 100-200 MB")
    elif exe_size > 500:
        print(f"⚠️  Warning: Executable size seems too large ({exe_size:.2f} MB)")
        print("   Expected size: 100-200 MB")
    
    # Check if checksum file exists
    print("\nChecking checksums...")
    if not checksum_file.exists():
        print("❌ Checksum file not found!")
        return False
    
    print("✅ Checksum file found")
    
    # Verify checksums
    print("   Verifying SHA-256...")
    calculated_sha256 = calculate_checksum(exe_file, 'sha256')
    
    print("   Verifying MD5...")
    calculated_md5 = calculate_checksum(exe_file, 'md5')
    
    # Read checksums from file
    checksum_content = checksum_file.read_text()
    
    # Extract checksums from file
    stored_sha256 = None
    stored_md5 = None
    for line in checksum_content.split('\n'):
        if line.startswith('SHA-256:'):
            stored_sha256 = line.split(':', 1)[1].strip()
        elif line.startswith('MD5:'):
            stored_md5 = line.split(':', 1)[1].strip()
    
    # Verify SHA-256
    if stored_sha256:
        if calculated_sha256 == stored_sha256:
            print(f"   ✅ SHA-256 matches: {calculated_sha256[:16]}...")
        else:
            print(f"   ❌ SHA-256 mismatch!")
            print(f"      Calculated: {calculated_sha256}")
            print(f"      Stored:     {stored_sha256}")
            return False
    else:
        print("   ⚠️  SHA-256 not found in checksum file")
    
    # Verify MD5
    if stored_md5:
        if calculated_md5 == stored_md5:
            print(f"   ✅ MD5 matches: {calculated_md5[:16]}...")
        else:
            print(f"   ❌ MD5 mismatch!")
            print(f"      Calculated: {calculated_md5}")
            print(f"      Stored:     {stored_md5}")
            return False
    else:
        print("   ⚠️  MD5 not found in checksum file")
    
    # Check BUILD_INFO file
    print("\nChecking BUILD_INFO...")
    if not build_info_file.exists():
        print("⚠️  BUILD_INFO.txt not found (optional)")
    else:
        print("✅ BUILD_INFO.txt found")
        info_content = build_info_file.read_text()
        print("\n   Build Information:")
        for line in info_content.split('\n')[:3]:  # Show first 3 lines
            if line.strip():
                print(f"   {line}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("✅ Build verification PASSED")
    print("=" * 60)
    print("\nBuild artifacts are ready for distribution!")
    print(f"\nExecutable: {exe_file}")
    print(f"Size: {exe_size:.2f} MB")
    print(f"SHA-256: {calculated_sha256}")
    print(f"MD5: {calculated_md5}")
    
    return True


def main():
    """Main verification process."""
    try:
        success = verify_build()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
