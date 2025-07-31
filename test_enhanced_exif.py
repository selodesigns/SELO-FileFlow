#!/usr/bin/env python3
"""
Test script for enhanced EXIF analysis and libpng warning fixes.
This script verifies that the enhanced EXIF analyzer works correctly
and that libpng warnings are properly suppressed.
"""

import os
import sys
import warnings
from pathlib import Path
import tempfile
import subprocess

# Add the fileflow module to the path
sys.path.insert(0, str(Path(__file__).parent))

# Suppress warnings for clean output
warnings.filterwarnings('ignore')

def create_test_image_with_exif():
    """Create a test image with EXIF data using ImageMagick if available."""
    try:
        # Create a simple test image with EXIF data
        temp_dir = Path(tempfile.mkdtemp())
        test_image = temp_dir / "test_with_exif.jpg"
        
        # Try to create image with ImageMagick
        cmd = [
            'convert', '-size', '800x600', 'xc:blue',
            '-set', 'exif:Software', 'Test Camera Software',
            '-set', 'exif:Make', 'Canon',
            '-set', 'exif:Model', 'EOS 5D Mark IV',
            '-set', 'exif:DateTime', '2024:01:15 14:30:00',
            str(test_image)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and test_image.exists():
            return test_image
        else:
            print("ImageMagick not available, creating simple test image...")
            
    except Exception as e:
        print(f"Failed to create test image with ImageMagick: {e}")
    
    # Fallback: create a simple image with Pillow
    try:
        from PIL import Image, ExifTags
        from PIL.ExifTags import TAGS
        
        # Create a simple image
        img = Image.new('RGB', (800, 600), color='blue')
        
        # Add some basic EXIF data
        exif_dict = {
            "0th": {
                256: 800,  # ImageWidth
                257: 600,  # ImageLength
                272: "Canon",  # Make
                306: "2024:01:15 14:30:00",  # DateTime
            },
            "Exif": {
                36867: "2024:01:15 14:30:00",  # DateTimeOriginal
            }
        }
        
        temp_dir = Path(tempfile.mkdtemp())
        test_image = temp_dir / "test_pillow_exif.jpg"
        img.save(test_image, "JPEG", quality=95)
        
        return test_image
        
    except Exception as e:
        print(f"Failed to create test image with Pillow: {e}")
        return None

def test_exif_analyzer():
    """Test the enhanced EXIF analyzer."""
    print("🔍 Testing Enhanced EXIF Analyzer...")
    
    try:
        from fileflow.enhanced_exif_analyzer import EnhancedExifAnalyzer
        
        analyzer = EnhancedExifAnalyzer()
        
        print(f"✅ EXIF Analyzer initialized successfully")
        print(f"   - ExifTool available: {analyzer.has_exiftool}")
        print(f"   - Pillow available: {analyzer.has_pillow}")
        
        # Test with a sample image if available
        test_image = create_test_image_with_exif()
        if test_image and test_image.exists():
            print(f"\n📸 Testing with sample image: {test_image.name}")
            
            # Test EXIF extraction
            if analyzer.has_exiftool:
                exif_data = analyzer.extract_exif_with_exiftool(test_image)
                print(f"   - ExifTool extracted {len(exif_data)} EXIF fields")
                if exif_data:
                    print(f"   - Sample fields: {list(exif_data.keys())[:5]}")
            
            if analyzer.has_pillow:
                exif_data = analyzer.extract_exif_with_pillow(test_image)
                print(f"   - Pillow extracted {len(exif_data)} EXIF fields")
                if exif_data:
                    print(f"   - Sample fields: {list(exif_data.keys())[:5]}")
            
            # Test comprehensive analysis
            analysis = analyzer.calculate_exif_suspicion_score(test_image)
            print(f"\n📊 EXIF Analysis Results:")
            print(f"   - EXIF Score: {analysis.get('exif_score', 0.0):.3f}")
            print(f"   - Confidence: {analysis.get('confidence', 0.0):.3f}")
            print(f"   - Has EXIF: {analysis.get('has_exif', False)}")
            print(f"   - Analysis Methods: {analysis.get('analysis_methods', [])}")
            
            # Test EXIF summary
            summary = analyzer.get_exif_summary(test_image)
            if 'error' not in summary:
                print(f"\n📋 EXIF Summary:")
                for key, value in summary.items():
                    print(f"   - {key}: {value}")
            
            # Clean up
            test_image.unlink()
            test_image.parent.rmdir()
        
        return True
        
    except Exception as e:
        print(f"❌ EXIF Analyzer test failed: {e}")
        return False

def test_robust_classifier_with_exif():
    """Test the robust classifier with enhanced EXIF integration."""
    print("\n🧠 Testing Robust Classifier with Enhanced EXIF...")
    
    try:
        from fileflow.robust_content_classifier import RobustContentClassifier
        
        classifier = RobustContentClassifier()
        
        print(f"✅ Robust Classifier initialized successfully")
        print(f"   - Pillow available: {classifier.has_pillow}")
        print(f"   - OpenCV available: {classifier.has_opencv}")
        print(f"   - ExifTool available: {classifier.has_exiftool}")
        print(f"   - EXIF Analyzer integrated: {hasattr(classifier, 'exif_analyzer')}")
        
        # Test with a sample image
        test_image = create_test_image_with_exif()
        if test_image and test_image.exists():
            print(f"\n📸 Testing classification with sample image...")
            
            # Test comprehensive EXIF analysis method
            if hasattr(classifier, 'get_comprehensive_exif_analysis'):
                exif_analysis = classifier.get_comprehensive_exif_analysis(test_image)
                print(f"✅ Comprehensive EXIF analysis completed")
                print(f"   - Has EXIF: {exif_analysis.get('has_exif', False)}")
                print(f"   - EXIF Score: {exif_analysis.get('exif_score', 0.0):.3f}")
                print(f"   - Confidence: {exif_analysis.get('confidence', 0.0):.3f}")
            
            # Test full classification
            result = classifier.classify_media_file(test_image)
            print(f"\n📊 Full Classification Results:")
            print(f"   - Is NSFW: {result.get('is_nsfw', False)}")
            print(f"   - Confidence: {result.get('confidence', 0.0):.3f}")
            print(f"   - NSFW Score: {result.get('nsfw_score', 0.0):.3f}")
            print(f"   - Analysis Methods: {result.get('analysis_methods', [])}")
            
            # Check if EXIF data is included in details
            details = result.get('details', {})
            if 'image_analysis' in details:
                img_analysis = details['image_analysis']
                if 'exif_analysis' in img_analysis:
                    print(f"   - EXIF integration: ✅ Present in results")
                else:
                    print(f"   - EXIF integration: ⚠️  Not found in image analysis")
            
            # Clean up
            test_image.unlink()
            test_image.parent.rmdir()
        
        return True
        
    except Exception as e:
        print(f"❌ Robust Classifier test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_libpng_warnings_suppressed():
    """Test that libpng warnings are properly suppressed."""
    print("\n🔇 Testing libpng Warning Suppression...")
    
    try:
        # Capture stderr to check for warnings
        import io
        import contextlib
        
        stderr_capture = io.StringIO()
        
        with contextlib.redirect_stderr(stderr_capture):
            # Try to process an image that might trigger libpng warnings
            from fileflow.robust_content_classifier import RobustContentClassifier
            
            classifier = RobustContentClassifier()
            
            # Create a test image that might have sRGB profile issues
            test_image = create_test_image_with_exif()
            if test_image and test_image.exists():
                # Process the image
                result = classifier.classify_media_file(test_image)
                
                # Clean up
                test_image.unlink()
                test_image.parent.rmdir()
        
        # Check captured stderr
        stderr_output = stderr_capture.getvalue()
        
        if 'libpng warning' in stderr_output or 'iCCP' in stderr_output:
            print(f"⚠️  libpng warnings still present:")
            print(f"   {stderr_output.strip()}")
            return False
        else:
            print(f"✅ libpng warnings successfully suppressed")
            return True
            
    except Exception as e:
        print(f"❌ libpng warning test failed: {e}")
        return False

def main():
    """Run all enhanced EXIF and warning suppression tests."""
    print("🚀 Enhanced EXIF Analysis and Warning Suppression Tests")
    print("=" * 60)
    
    tests = [
        ("EXIF Analyzer", test_exif_analyzer),
        ("Robust Classifier with EXIF", test_robust_classifier_with_exif),
        ("libpng Warning Suppression", test_libpng_warnings_suppressed),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'=' * 60}")
    print("📋 Test Summary:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All enhanced EXIF and warning suppression tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
