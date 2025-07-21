"""
Tests for the file_handler module.
"""

import os
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.modules.file_handler import FileHandler

class TestFileHandler(unittest.TestCase):
    """Test cases for the FileHandler class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directories for testing
        self.temp_dir = TemporaryDirectory()
        self.source_dir = Path(self.temp_dir.name) / "downloads"
        self.source_dir.mkdir()
        
        # Create destination directories
        self.images_dir = Path(self.temp_dir.name) / "images"
        self.documents_dir = Path(self.temp_dir.name) / "documents"
        self.videos_dir = Path(self.temp_dir.name) / "videos"
        self.software_dir = Path(self.temp_dir.name) / "software"
        self.other_dir = Path(self.temp_dir.name) / "other"
        
        for dir_path in [self.images_dir, self.documents_dir, self.videos_dir, 
                         self.software_dir, self.other_dir]:
            dir_path.mkdir()
        
        # Create test config
        self.config = {
            'source_directory': str(self.source_dir),
            'destination_directories': {
                'images': str(self.images_dir),
                'documents': str(self.documents_dir),
                'videos': str(self.videos_dir),
                'software': str(self.software_dir),
                'other': str(self.other_dir)
            },
            'file_types': {
                'images': ['.jpg', '.png', '.gif'],
                'documents': ['.pdf', '.doc', '.txt'],
                'videos': ['.mp4', '.avi', '.mkv'],
                'software': ['.exe', '.msi', '.zip']
            },
            'move_files': True
        }
        
        # Create file handler
        self.file_handler = FileHandler(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
    
    def test_get_file_category(self):
        """Test get_file_category method."""
        # Test image file
        image_path = Path("test.jpg")
        self.assertEqual(self.file_handler.get_file_category(image_path), 'images')
        
        # Test document file
        doc_path = Path("test.pdf")
        self.assertEqual(self.file_handler.get_file_category(doc_path), 'documents')
        
        # Test video file
        video_path = Path("test.mp4")
        self.assertEqual(self.file_handler.get_file_category(video_path), 'videos')
        
        # Test software file
        software_path = Path("test.exe")
        self.assertEqual(self.file_handler.get_file_category(software_path), 'software')
        
        # Test other file
        other_path = Path("test.unknown")
        self.assertEqual(self.file_handler.get_file_category(other_path), 'other')
    
    def test_process_file(self):
        """Test process_file method."""
        # Create test files
        test_files = {
            'image.jpg': 'images',
            'document.pdf': 'documents',
            'video.mp4': 'videos',
            'software.exe': 'software',
            'other.xyz': 'other'
        }
        
        for filename, _ in test_files.items():
            file_path = self.source_dir / filename
            with open(file_path, 'w') as f:
                f.write("test content")
        
        # Process each file
        for filename, category in test_files.items():
            file_path = self.source_dir / filename
            self.assertTrue(self.file_handler.process_file(file_path))
            
            # Check if file was moved to correct category
            dest_dir = getattr(self, f"{category}_dir")
            dest_file = dest_dir / filename
            self.assertTrue(dest_file.exists())
            
            # Check if file is no longer in source directory
            self.assertFalse(file_path.exists())
    
    def test_process_file_copy_mode(self):
        """Test process_file method with copy mode."""
        # Set move_files to False
        self.file_handler.move_files = False
        
        # Create test file
        file_path = self.source_dir / "test.jpg"
        with open(file_path, 'w') as f:
            f.write("test content")
        
        # Process file
        self.assertTrue(self.file_handler.process_file(file_path))
        
        # Check if file was copied to images directory
        dest_file = self.images_dir / "test.jpg"
        self.assertTrue(dest_file.exists())
        
        # Check if file is still in source directory
        self.assertTrue(file_path.exists())
    
    def test_process_directory(self):
        """Test process_directory method."""
        # Create test files in source directory
        file_types = ['.jpg', '.pdf', '.mp4', '.exe', '.xyz']
        for i, ext in enumerate(file_types):
            file_path = self.source_dir / f"test{i}{ext}"
            with open(file_path, 'w') as f:
                f.write("test content")
        
        # Process directory
        processed_count = self.file_handler.process_directory(self.source_dir)
        
        # Check if all files were processed
        self.assertEqual(processed_count, len(file_types))
        
        # Check if source directory is empty
        self.assertEqual(len(list(self.source_dir.iterdir())), 0)


if __name__ == '__main__':
    unittest.main()
