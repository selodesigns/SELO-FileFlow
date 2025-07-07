import unittest
import tempfile
import shutil
from pathlib import Path
from unittest import mock

from fileflow.organizer import get_category_for_file, organize_files

class TestOrganizer(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.src = Path(self.tempdir.name) / 'Downloads'
        self.img_dst = Path(self.tempdir.name) / 'Pictures'
        self.doc_dst = Path(self.tempdir.name) / 'Documents'
        self.other_dst = Path(self.tempdir.name) / 'Other'
        self.src.mkdir()
        self.img_dst.mkdir()
        self.doc_dst.mkdir()
        self.other_dst.mkdir()

        self.config = {
            'source_directories': [str(self.src)],
            'destination_directories': {
                'images': str(self.img_dst),
                'documents': str(self.doc_dst),
                'other': str(self.other_dst)
            },
            'file_types': {
                'images': ['.jpg', '.png'],
                'documents': ['.pdf', '.txt'],
                'other': []
            },
            'notify_on_move': False
        }

    def tearDown(self):
        self.tempdir.cleanup()

    def test_get_category_for_file(self):
        types = self.config['file_types']
        self.assertEqual(get_category_for_file('photo.jpg', types), 'images')
        self.assertEqual(get_category_for_file('doc.pdf', types), 'documents')
        self.assertEqual(get_category_for_file('weird.xyz', types), 'other')

    @mock.patch('fileflow.organizer.load_config')
    @mock.patch('fileflow.organizer.send_notification')
    def test_organize_files_moves_files(self, mock_notify, mock_load_config):
        mock_load_config.return_value = self.config
        img_file = self.src / 'test.jpg'
        doc_file = self.src / 'test.pdf'
        other_file = self.src / 'foo.xyz'
        img_file.write_bytes(b'img')
        doc_file.write_bytes(b'doc')
        other_file.write_bytes(b'other')

        organize_files()

        self.assertFalse(img_file.exists())
        self.assertFalse(doc_file.exists())
        self.assertFalse(other_file.exists())
        self.assertTrue((self.img_dst / 'test.jpg').exists())
        self.assertTrue((self.doc_dst / 'test.pdf').exists())
        self.assertTrue((self.other_dst / 'foo.xyz').exists())

if __name__ == '__main__':
    unittest.main()
