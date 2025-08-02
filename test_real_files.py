#!/usr/bin/env python3
"""Test content analysis with real image files."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fileflow.robust_content_classifier import RobustContentClassifier

def test_real_files():
    """Test with actual image files."""
    classifier = RobustContentClassifier()
    
    # Test with some real image files
    test_files = [
        "/home/sean/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/share/doc/rust/html/static.files/favicon-32x32-6580c154.png",
        "/home/sean/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/share/doc/rust/html/book/2018-edition/img/trpl14-02.png"
    ]
    
    for test_file in test_files:
        file_path = Path(test_file)
        if not file_path.exists():
            print(f"File not found: {test_file}")
            continue
            
        print(f"\n=== Testing: {file_path.name} ===")
        
        # Test full classification
        result = classifier.classify_media_file(file_path)
        
        print(f"Classification result:")
        print(f"  is_nsfw: {result.get('is_nsfw')}")
        print(f"  confidence: {result.get('confidence')}")
        print(f"  file_type: {result.get('file_type')}")
        print(f"  analysis_methods: {result.get('analysis_methods', [])}")
        
        details = result.get('details', {})
        print(f"  reason: {details.get('reason', 'No reason')}")
        
        # Show content analysis details
        if 'opencv' in details:
            opencv = details['opencv']
            print(f"  OpenCV - skin: {opencv.get('skin_percentage', 0):.1f}%, visual_score: {opencv.get('visual_score', 0):.2f}")
            
        if 'filename_analysis' in details:
            filename = details['filename_analysis']
            print(f"  Filename - explicit: {filename.get('is_explicit')}, sfw: {filename.get('is_sfw')}, confidence: {filename.get('confidence', 0):.2f}")

if __name__ == "__main__":
    test_real_files()
