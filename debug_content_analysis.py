#!/usr/bin/env python3
"""Debug script to test content analysis functionality."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fileflow.robust_content_classifier import RobustContentClassifier

def test_content_analysis():
    """Test the content analysis functionality."""
    classifier = RobustContentClassifier()
    
    print("=== Dependency Check ===")
    print(f"has_pillow: {classifier.has_pillow}")
    print(f"has_opencv: {classifier.has_opencv}")
    print(f"has_exiftool: {classifier.has_exiftool}")
    print(f"has_ffmpeg: {classifier.has_ffmpeg}")
    
    # Find a test image file
    test_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi']:
        files = list(Path('.').rglob(f'*{ext}'))
        if files:
            test_files.extend(files[:2])  # Take first 2 of each type
            
    if not test_files:
        print("No test media files found in current directory")
        return
        
    print(f"\n=== Testing {len(test_files)} files ===")
    
    for test_file in test_files[:3]:  # Test first 3 files
        print(f"\n--- Testing: {test_file} ---")
        
        # Test if file should be classified
        should_classify = classifier.should_classify_file(test_file)
        print(f"Should classify: {should_classify}")
        
        if should_classify:
            # Test individual analysis methods
            if test_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff']:
                print("Testing OpenCV analysis...")
                opencv_result = classifier.analyze_image_with_opencv(test_file)
                print(f"OpenCV result: {opencv_result}")
                
                print("Testing Pillow analysis...")
                pillow_result = classifier.analyze_image_with_pillow(test_file)
                print(f"Pillow result: {pillow_result}")
                
            elif test_file.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                print("Testing video metadata analysis...")
                video_result = classifier.analyze_video_metadata(test_file)
                print(f"Video metadata result: {video_result}")
                
                if classifier.has_ffmpeg:
                    print("Testing video frame analysis...")
                    frame_result = classifier.analyze_video_frames(test_file, sample_count=2)
                    print(f"Frame analysis result: {frame_result}")
            
            # Test full classification
            print("Testing full classification...")
            full_result = classifier.classify_media_file(test_file)
            print(f"Full classification result:")
            print(f"  is_nsfw: {full_result.get('is_nsfw')}")
            print(f"  confidence: {full_result.get('confidence')}")
            print(f"  reason: {full_result.get('details', {}).get('reason', 'No reason')}")
            print(f"  analysis_methods: {full_result.get('analysis_methods', [])}")

if __name__ == "__main__":
    test_content_analysis()
