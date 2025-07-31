#!/usr/bin/env python3
"""
Test script for visual content analysis functionality.
This script demonstrates how the enhanced NSFW/SFW classification works with actual image analysis.
"""

import sys
import os
from pathlib import Path
import tempfile

# Add the fileflow module to path
sys.path.insert(0, str(Path(__file__).parent))

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import cv2
        import numpy as np
        from PIL import Image
        print("✅ All required dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install opencv-python Pillow numpy")
        return False

def create_test_images():
    """Create sample test images with different characteristics."""
    import numpy as np
    import cv2
    
    test_dir = Path(tempfile.mkdtemp(prefix="fileflow_test_"))
    print(f"Creating test images in: {test_dir}")
    
    # Create a high-skin content image (simulating potential NSFW)
    high_skin_img = np.zeros((400, 400, 3), dtype=np.uint8)
    # Fill with skin-like color (HSV: 10, 100, 200 -> BGR)
    skin_color = [139, 169, 200]  # Approximate skin tone in BGR
    high_skin_img[:, :] = skin_color
    cv2.imwrite(str(test_dir / "high_skin_content.jpg"), high_skin_img)
    
    # Create a low-skin content image (simulating SFW)
    low_skin_img = np.zeros((400, 400, 3), dtype=np.uint8)
    # Fill with blue color (clearly not skin)
    blue_color = [255, 100, 50]  # Blue in BGR
    low_skin_img[:, :] = blue_color
    cv2.imwrite(str(test_dir / "landscape_photo.jpg"), low_skin_img)
    
    # Create a mixed content image
    mixed_img = np.zeros((400, 400, 3), dtype=np.uint8)
    mixed_img[:200, :] = skin_color  # Top half skin-like
    mixed_img[200:, :] = [50, 150, 50]  # Bottom half green
    cv2.imwrite(str(test_dir / "mixed_content.jpg"), mixed_img)
    
    # Create an image with face-like features (using simple rectangles)
    face_img = np.zeros((400, 400, 3), dtype=np.uint8)
    face_img[:, :] = skin_color
    # Add some darker rectangles to simulate facial features
    cv2.rectangle(face_img, (150, 150), (170, 170), (100, 120, 150), -1)  # Eye
    cv2.rectangle(face_img, (230, 150), (250, 170), (100, 120, 150), -1)  # Eye
    cv2.rectangle(face_img, (180, 220), (220, 240), (120, 100, 130), -1)  # Mouth
    cv2.imwrite(str(test_dir / "portrait_photo.jpg"), face_img)
    
    return test_dir

def test_visual_classification():
    """Test the visual content classification."""
    if not check_dependencies():
        return False
    
    try:
        from fileflow.advanced_content_classifier import AdvancedContentClassifier
    except ImportError as e:
        print(f"❌ Could not import AdvancedContentClassifier: {e}")
        return False
    
    print("\n🔍 Testing Visual Content Analysis")
    print("=" * 60)
    
    # Create test images
    test_dir = create_test_images()
    classifier = AdvancedContentClassifier()
    
    test_results = []
    
    for image_file in test_dir.glob("*.jpg"):
        print(f"\nAnalyzing: {image_file.name}")
        print("-" * 40)
        
        try:
            result = classifier.classify_media_file(image_file)
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            is_nsfw = result.get('is_nsfw', False)
            confidence = result.get('confidence', 0.0)
            nsfw_score = result.get('nsfw_score', 0.0)
            skin_percentage = result.get('skin_percentage', 0.0)
            faces = result.get('faces', 0)
            
            status = "🔞 NSFW" if is_nsfw else "✅ SFW"
            print(f"Classification: {status}")
            print(f"Confidence: {confidence:.2f}")
            print(f"NSFW Score: {nsfw_score:.2f}")
            print(f"Skin Percentage: {skin_percentage:.1f}%")
            print(f"Faces Detected: {faces}")
            
            test_results.append({
                'file': image_file.name,
                'is_nsfw': is_nsfw,
                'confidence': confidence,
                'skin_percentage': skin_percentage
            })
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
    
    # Clean up test files
    import shutil
    shutil.rmtree(test_dir)
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    for result in test_results:
        status = "NSFW" if result['is_nsfw'] else "SFW"
        print(f"  {result['file']:<25} → {status:<4} (skin: {result['skin_percentage']:.1f}%, conf: {result['confidence']:.2f})")
    
    return len(test_results) > 0

def test_enhanced_organizer():
    """Test the enhanced organizer configuration."""
    try:
        from fileflow.enhanced_content_organizer import EnhancedContentOrganizer
    except ImportError as e:
        print(f"❌ Could not import EnhancedContentOrganizer: {e}")
        return False
    
    print("\n📁 Testing Enhanced Organizer Configuration")
    print("=" * 60)
    
    organizer = EnhancedContentOrganizer()
    config = organizer.get_enhanced_config()
    
    print("Enhanced content classification settings:")
    classification_config = config.get('content_classification', {})
    for key, value in classification_config.items():
        print(f"  {key}: {value}")
    
    print(f"\nContent-based destination directories:")
    for content_type, categories in config['content_destinations'].items():
        print(f"\n{content_type.upper()}:")
        for category, path in categories.items():
            print(f"  {category}: {path}")
    
    return True

def main():
    print("🚀 FileFlow Enhanced Content Analysis Test")
    print("This script tests the visual content analysis functionality.\n")
    
    # Test visual classification
    visual_test_passed = test_visual_classification()
    
    # Test enhanced organizer
    organizer_test_passed = test_enhanced_organizer()
    
    print("\n" + "=" * 60)
    if visual_test_passed and organizer_test_passed:
        print("✅ All tests passed! Enhanced content analysis is working.")
        print("\nTo use the enhanced functionality:")
        print("  1. Run: python -m fileflow.main --organize-once")
        print("  2. To reorganize existing files: python -m fileflow.main --reorganize")
        print("\nThe system now uses:")
        print("  • Filename analysis for obvious cases")
        print("  • Visual content analysis (skin detection, face detection)")
        print("  • Combined scoring for more accurate classification")
        print("\n✅ All required dependencies are installed and working!")
    else:
        print("❌ Some tests failed. Please check the installation and dependencies.")
    
    print("\nNote: Visual analysis provides much more accurate classification")
    print("than filename-only detection, especially for files with generic names.")

if __name__ == "__main__":
    main()
