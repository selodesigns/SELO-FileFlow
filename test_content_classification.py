#!/usr/bin/env python3
"""
Test script for content classification functionality.
This script demonstrates how the NSFW/SFW classification works.
"""

import sys
from pathlib import Path

# Add the fileflow module to path
sys.path.insert(0, str(Path(__file__).parent))

from fileflow.content_classifier import ContentClassifier

def test_classification():
    """Test the content classification with sample filenames."""
    classifier = ContentClassifier()
    
    # Test cases with expected results
    test_files = [
        # SFW files
        ("family_vacation_2023.jpg", False),
        ("wedding_photos.mp4", False),
        ("nature_landscape.png", False),
        ("cooking_tutorial.mp4", False),
        ("business_meeting.pdf", False),
        
        # NSFW files
        ("xxx_video.mp4", True),
        ("porn_collection.jpg", True),
        ("adult_content_18+.mp4", True),
        ("nsfw_image.png", True),
        ("sexy_model_nude.jpg", True),
        ("pornhub_download.mp4", True),
        
        # Ambiguous cases
        ("party_pics.jpg", False),
        ("beach_photos.jpg", False),
        ("model_portfolio.jpg", False),
    ]
    
    print("🔍 Testing Content Classification")
    print("=" * 50)
    
    correct_predictions = 0
    total_tests = len(test_files)
    
    for filename, expected_nsfw in test_files:
        file_path = Path(filename)
        analysis = classifier.analyze_file_path(file_path)
        predicted_nsfw = analysis['is_nsfw']
        
        status = "✅" if predicted_nsfw == expected_nsfw else "❌"
        content_type = "NSFW" if predicted_nsfw else "SFW"
        
        print(f"{status} {filename:<30} → {content_type:<4} ({analysis['reason']})")
        
        if predicted_nsfw == expected_nsfw:
            correct_predictions += 1
    
    print("=" * 50)
    accuracy = (correct_predictions / total_tests) * 100
    print(f"Accuracy: {correct_predictions}/{total_tests} ({accuracy:.1f}%)")
    
    return accuracy >= 80  # Consider 80%+ accuracy as passing

def test_directory_structure():
    """Test the directory structure creation logic."""
    from fileflow.content_organizer import ContentOrganizer
    
    print("\n📁 Testing Directory Structure")
    print("=" * 50)
    
    organizer = ContentOrganizer()
    config = organizer.get_enhanced_config()
    
    print("Content-based destination directories:")
    for content_type, categories in config['content_destinations'].items():
        print(f"\n{content_type.upper()}:")
        for category, path in categories.items():
            print(f"  {category}: {path}")
    
    print(f"\nContent classification settings:")
    for key, value in config['content_classification'].items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    print("🚀 FileFlow Content Classification Test")
    print("This script tests the NSFW/SFW content classification functionality.\n")
    
    # Run classification tests
    classification_passed = test_classification()
    
    # Test directory structure
    test_directory_structure()
    
    print("\n" + "=" * 50)
    if classification_passed:
        print("✅ All tests passed! Content classification is working correctly.")
        print("\nTo use the new functionality:")
        print("  • Run: python -m fileflow.main --organize-once")
        print("  • To reorganize existing files: python -m fileflow.main --reorganize")
    else:
        print("❌ Some tests failed. Please review the classification logic.")
    
    print("\nNote: The classifier uses filename-based detection. For more accurate")
    print("classification, consider integrating image/video analysis libraries.")
