"""Test two-pass classification system for NSFW detection."""
import os
import sys
import json
from pathlib import Path
from unittest import TestCase, main
from tempfile import TemporaryDirectory
from shutil import copy2

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fileflow.robust_content_classifier import RobustContentClassifier

class TestTwoPassClassification(TestCase):    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(__file__).parent / 'test_data'
        self.test_dir.mkdir(exist_ok=True)
        
        # Create test files
        self.test_files = {
            'explicit_nsfw.txt': 'nsfw_porn_explicit_content.txt',
            'sfw_family.jpg': 'family_vacation_2023.jpg',
            'ambiguous_nude.jpg': 'artistic_nude_photography.jpg',
            'explicit_dir/explicit1.jpg': 'nsfw_content1.jpg',
            'sfw_dir/family1.jpg': 'family_pic1.jpg'
        }
        
        # Create test files
        for src, dest in self.test_files.items():
            path = self.test_dir / dest
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        
        # Initialize classifier
        self.classifier = RobustContentClassifier()
    
    def test_filename_analysis(self):
        """Test first pass (filename analysis)."""
        # Test explicit NSFW filename
        result = self.classifier.analyze_filename_only(self.test_dir / self.test_files['explicit_nsfw.txt'])
        self.assertTrue(result['is_potentially_nsfw'])
        self.assertGreaterEqual(result['confidence'], 0.5)
        
        # Test SFW filename
        result = self.classifier.analyze_filename_only(self.test_dir / self.test_files['sfw_family.jpg'])
        self.assertFalse(result['is_potentially_nsfw'])
        self.assertGreaterEqual(result['confidence'], 0.8)
        
        # Test ambiguous filename (should require content analysis)
        result = self.classifier.analyze_filename_only(self.test_dir / self.test_files['ambiguous_nude.jpg'])
        self.assertTrue(result['requires_content_analysis'])
    
    def test_content_analysis(self):
        """Test second pass (content analysis)."""
        # Test with explicit filename but SFW content
        filename = self.test_dir / self.test_files['explicit_nsfw.txt']
        filename_analysis = self.classifier.analyze_filename_only(filename)
        content_analysis = self.classifier.analyze_content(filename, filename_analysis)
        
        # Should still be marked NSFW due to explicit filename
        self.assertTrue(content_analysis['is_nsfw'])
        self.assertGreaterEqual(content_analysis['confidence'], 0.8)
    
    def test_full_classification(self):
        """Test full two-pass classification."""
        # Test explicit NSFW
        result = self.classifier.classify_media_file(self.test_dir / self.test_files['explicit_nsfw.txt'])
        self.assertTrue(result['is_nsfw'])
        self.assertIn('filename_analysis', result['analysis_methods'])
        self.assertIn('content_analysis', result['analysis_methods'])
        
        # Test SFW
        result = self.classifier.classify_media_file(self.test_dir / self.test_files['sfw_family.jpg'])
        self.assertFalse(result['is_nsfw'])
        self.assertIn('filename_analysis', result['analysis_methods'])
        
        # Test ambiguous case (requires content analysis)
        result = self.classifier.classify_media_file(self.test_dir / self.test_files['ambiguous_nude.jpg'])
        self.assertIn('content_analysis', result['analysis_methods'])
    
    def test_directory_handling(self):
        """Test that directory names are properly considered."""
        # Test NSFW directory
        result = self.classifier.classify_media_file(
            self.test_dir / 'explicit_dir' / 'explicit1.jpg'
        )
        self.assertTrue(result['is_nsfw'])
        self.assertIn('directory_analysis', result['analysis_methods'])
        
        # Test SFW directory
        result = self.classifier.classify_media_file(
            self.test_dir / 'sfw_dir' / 'family1.jpg'
        )
        self.assertFalse(result['is_nsfw'])
        self.assertIn('directory_analysis', result['analysis_methods'])
    
    def tearDown(self):
        """Clean up test files."""
        for path in self.test_dir.glob('**/*'):
            if path.is_file():
                path.unlink()
        
        # Remove empty directories
        for path in reversed(list(self.test_dir.glob('**'))):
            if path.is_dir() and path != self.test_dir:
                path.rmdir()
        
        if self.test_dir.exists() and not any(self.test_dir.iterdir()):
            self.test_dir.rmdir()

if __name__ == '__main__':
    main()
