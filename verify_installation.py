#!/usr/bin/env python3
"""
FileFlow Installation Verification Script
Checks all dependencies and system requirements for optimal performance.
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (compatible)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (requires Python 3.8+)")
        return False

def check_python_dependency(package_name, min_version=None):
    """Check if a Python package is installed and optionally verify version."""
    try:
        module = importlib.import_module(package_name)
        if hasattr(module, '__version__'):
            version = module.__version__
            print(f"   ✅ {package_name}: {version}")
        else:
            print(f"   ✅ {package_name}: installed (version unknown)")
        return True
    except ImportError:
        print(f"   ❌ {package_name}: not installed")
        return False

def check_system_dependency(command, name):
    """Check if a system command is available."""
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"   ✅ {name}: {version_line}")
            return True
        else:
            print(f"   ❌ {name}: command failed")
            return False
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        print(f"   ❌ {name}: not found")
        return False

def check_exiftool():
    """Check ExifTool specifically."""
    try:
        result = subprocess.run(['exiftool', '-ver'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✅ ExifTool: {version}")
            return True
        else:
            print(f"   ❌ ExifTool: command failed")
            return False
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        print(f"   ❌ ExifTool: not found")
        return False

def test_fileflow_imports():
    """Test FileFlow module imports."""
    print("\n🔧 Testing FileFlow module imports...")
    
    modules_to_test = [
        'fileflow.robust_content_classifier',
        'fileflow.enhanced_exif_analyzer', 
        'fileflow.enhanced_content_organizer',
        'fileflow.ui.app'
    ]
    
    all_passed = True
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module}: {e}")
            all_passed = False
    
    return all_passed

def test_functionality():
    """Test core functionality."""
    print("\n⚡ Testing core functionality...")
    
    try:
        # Test robust classifier initialization
        from fileflow.robust_content_classifier import RobustContentClassifier
        classifier = RobustContentClassifier()
        print(f"   ✅ RobustContentClassifier initialized")
        
        # Test EXIF analyzer
        from fileflow.enhanced_exif_analyzer import EnhancedExifAnalyzer
        exif_analyzer = EnhancedExifAnalyzer()
        print(f"   ✅ EnhancedExifAnalyzer initialized")
        
        # Test enhanced organizer
        from fileflow.enhanced_content_organizer import EnhancedContentOrganizer
        organizer = EnhancedContentOrganizer()
        print(f"   ✅ EnhancedContentOrganizer initialized")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Functionality test failed: {e}")
        return False

def main():
    """Run comprehensive installation verification."""
    print("🚀 FileFlow Installation Verification")
    print("=" * 50)
    
    all_checks = []
    
    # Python version check
    all_checks.append(check_python_version())
    
    # Core Python dependencies
    print("\n📦 Checking core Python dependencies...")
    core_deps = [
        'yaml',      # PyYAML
        'watchdog',
        'PyQt5',
        'pytest'
    ]
    
    for dep in core_deps:
        all_checks.append(check_python_dependency(dep))
    
    # Enhanced analysis dependencies
    print("\n🔬 Checking enhanced analysis dependencies...")
    analysis_deps = [
        'cv2',       # opencv-python
        'PIL',       # Pillow
        'numpy'
    ]
    
    for dep in analysis_deps:
        all_checks.append(check_python_dependency(dep))
    
    # System dependencies
    print("\n🖥️  Checking system dependencies...")
    all_checks.append(check_exiftool())
    all_checks.append(check_system_dependency('ffmpeg', 'FFmpeg'))
    
    # FileFlow module imports
    all_checks.append(test_fileflow_imports())
    
    # Functionality tests
    all_checks.append(test_functionality())
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(all_checks)
    total = len(all_checks)
    
    if passed == total:
        print(f"🎉 All checks passed! ({passed}/{total})")
        print("\n✅ FileFlow is ready for optimal performance with:")
        print("   • Advanced visual content analysis")
        print("   • Comprehensive EXIF metadata extraction")
        print("   • Video metadata analysis")
        print("   • Multi-layered content classification")
        print("\n🚀 You can now run: python3 -m fileflow.main --ui")
        return True
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("\n📋 Missing dependencies will result in reduced functionality:")
        print("   • FileFlow will still work with basic features")
        print("   • Install missing dependencies for full capabilities")
        print("   • See INSTALLATION.md for detailed setup instructions")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
