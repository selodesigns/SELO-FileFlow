import os
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import hashlib
import json
from PIL import Image, ExifTags
import subprocess
import tempfile
from .utils.logging import get_logger

logger = get_logger()

class AdvancedContentClassifier:
    """Advanced content classifier using computer vision and ML techniques."""
    
    def __init__(self):
        self.cache_dir = Path.home() / '.cache' / 'selo-fileflow' / 'content_analysis'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Skin detection parameters (HSV color space)
        self.skin_lower = np.array([0, 20, 70], dtype=np.uint8)
        self.skin_upper = np.array([20, 255, 255], dtype=np.uint8)
        
        # Alternative skin range for different lighting
        self.skin_lower2 = np.array([0, 40, 60], dtype=np.uint8)
        self.skin_upper2 = np.array([25, 255, 255], dtype=np.uint8)
        
        # Initialize face detection
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
        except Exception as e:
            logger.warning(f"Could not load OpenCV cascades: {e}")
            self.face_cascade = None
            self.body_cascade = None
    
    def get_file_hash(self, file_path: Path) -> str:
        """Generate a hash for the file to use for caching."""
        stat = file_path.stat()
        content = f"{file_path.name}_{stat.st_size}_{stat.st_mtime}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_result(self, file_path: Path) -> Optional[Dict]:
        """Get cached analysis result if available."""
        file_hash = self.get_file_hash(file_path)
        cache_file = self.cache_dir / f"{file_hash}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.debug(f"Failed to read cache for {file_path.name}: {e}")
        return None
    
    def save_cached_result(self, file_path: Path, result: Dict):
        """Save analysis result to cache."""
        file_hash = self.get_file_hash(file_path)
        cache_file = self.cache_dir / f"{file_hash}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(result, f)
        except Exception as e:
            logger.debug(f"Failed to save cache for {file_path.name}: {e}")
    
    def detect_skin_percentage(self, image: np.ndarray) -> float:
        """Detect the percentage of skin-colored pixels in an image."""
        if image is None or image.size == 0:
            return 0.0
        
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Create skin mask using two different ranges
        mask1 = cv2.inRange(hsv, self.skin_lower, self.skin_upper)
        mask2 = cv2.inRange(hsv, self.skin_lower2, self.skin_upper2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Apply morphological operations to reduce noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Calculate skin percentage
        skin_pixels = cv2.countNonZero(mask)
        total_pixels = image.shape[0] * image.shape[1]
        
        return (skin_pixels / total_pixels) * 100 if total_pixels > 0 else 0.0
    
    def detect_faces_and_bodies(self, image: np.ndarray) -> Dict[str, int]:
        """Detect faces and bodies in an image."""
        if image is None or self.face_cascade is None:
            return {'faces': 0, 'bodies': 0}
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        # Detect bodies (less reliable, so we use it as supplementary info)
        bodies = []
        if self.body_cascade is not None:
            bodies = self.body_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=3, minSize=(50, 50)
            )
        
        return {'faces': len(faces), 'bodies': len(bodies)}
    
    def analyze_image_brightness_contrast(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze image brightness and contrast characteristics."""
        if image is None or image.size == 0:
            return {'brightness': 0.0, 'contrast': 0.0}
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate brightness (mean pixel value)
        brightness = np.mean(gray)
        
        # Calculate contrast (standard deviation)
        contrast = np.std(gray)
        
        return {'brightness': float(brightness), 'contrast': float(contrast)}
    
    def extract_video_frames(self, video_path: Path, num_frames: int = 5) -> List[np.ndarray]:
        """Extract sample frames from a video for analysis."""
        frames = []
        
        try:
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                return frames
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                return frames
            
            # Extract frames at regular intervals
            frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret and frame is not None:
                    frames.append(frame)
            
            cap.release()
            
        except Exception as e:
            logger.error(f"Failed to extract frames from {video_path}: {e}")
        
        return frames
    
    def get_image_metadata(self, image_path: Path) -> Dict:
        """Extract metadata from image file."""
        metadata = {}
        
        try:
            with Image.open(image_path) as img:
                # Get basic image info
                metadata['format'] = img.format
                metadata['mode'] = img.mode
                metadata['size'] = img.size
                
                # Get EXIF data
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    exif = img._getexif()
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                
                metadata['exif'] = exif_data
                
        except Exception as e:
            logger.debug(f"Failed to extract metadata from {image_path}: {e}")
        
        return metadata
    
    def analyze_image_content(self, image_path: Path) -> Dict:
        """Comprehensive analysis of image content."""
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                return {'error': 'Could not load image', 'is_nsfw': False, 'confidence': 0.0}
            
            # Resize image for faster processing (maintain aspect ratio)
            height, width = image.shape[:2]
            if width > 800:
                scale = 800 / width
                new_width = 800
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
            
            analysis = {}
            
            # Skin detection
            skin_percentage = self.detect_skin_percentage(image)
            analysis['skin_percentage'] = skin_percentage
            
            # Face and body detection
            detection_results = self.detect_faces_and_bodies(image)
            analysis.update(detection_results)
            
            # Brightness and contrast analysis
            brightness_contrast = self.analyze_image_brightness_contrast(image)
            analysis.update(brightness_contrast)
            
            # Get image metadata
            metadata = self.get_image_metadata(image_path)
            analysis['metadata'] = metadata
            
            # Calculate NSFW probability based on multiple factors
            nsfw_score = self.calculate_nsfw_score(analysis)
            analysis['nsfw_score'] = nsfw_score
            analysis['is_nsfw'] = nsfw_score > 0.6  # Threshold for NSFW classification
            analysis['confidence'] = min(nsfw_score * 1.5, 1.0)  # Confidence based on score
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze image {image_path}: {e}")
            return {'error': str(e), 'is_nsfw': False, 'confidence': 0.0}
    
    def analyze_video_content(self, video_path: Path) -> Dict:
        """Analyze video content by sampling frames."""
        try:
            # Extract sample frames
            frames = self.extract_video_frames(video_path, num_frames=3)
            
            if not frames:
                return {'error': 'Could not extract frames', 'is_nsfw': False, 'confidence': 0.0}
            
            frame_analyses = []
            total_skin = 0
            total_faces = 0
            total_bodies = 0
            
            for i, frame in enumerate(frames):
                # Analyze each frame
                skin_percentage = self.detect_skin_percentage(frame)
                detection_results = self.detect_faces_and_bodies(frame)
                brightness_contrast = self.analyze_image_brightness_contrast(frame)
                
                frame_analysis = {
                    'frame_index': i,
                    'skin_percentage': skin_percentage,
                    **detection_results,
                    **brightness_contrast
                }
                
                frame_analyses.append(frame_analysis)
                total_skin += skin_percentage
                total_faces += detection_results['faces']
                total_bodies += detection_results['bodies']
            
            # Calculate averages
            num_frames = len(frames)
            analysis = {
                'num_frames_analyzed': num_frames,
                'avg_skin_percentage': total_skin / num_frames,
                'total_faces': total_faces,
                'total_bodies': total_bodies,
                'frame_analyses': frame_analyses
            }
            
            # Calculate NSFW probability
            nsfw_score = self.calculate_nsfw_score(analysis)
            analysis['nsfw_score'] = nsfw_score
            analysis['is_nsfw'] = nsfw_score > 0.6
            analysis['confidence'] = min(nsfw_score * 1.5, 1.0)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze video {video_path}: {e}")
            return {'error': str(e), 'is_nsfw': False, 'confidence': 0.0}
    
    def calculate_nsfw_score(self, analysis: Dict) -> float:
        """Calculate NSFW probability score based on analysis results."""
        score = 0.0
        
        # Skin percentage factor (higher skin = higher NSFW probability)
        skin_percentage = analysis.get('skin_percentage', analysis.get('avg_skin_percentage', 0))
        if skin_percentage > 30:
            score += 0.4
        elif skin_percentage > 20:
            score += 0.2
        elif skin_percentage > 10:
            score += 0.1
        
        # Face detection factor
        faces = analysis.get('faces', analysis.get('total_faces', 0))
        if faces > 0:
            # Multiple faces might indicate group content
            if faces > 2:
                score += 0.1
            # Single face with high skin might be portrait
            elif faces == 1 and skin_percentage > 25:
                score += 0.2
        
        # Body detection factor
        bodies = analysis.get('bodies', analysis.get('total_bodies', 0))
        if bodies > 0:
            score += 0.1
        
        # Brightness factor (very dark or very bright images might be suspicious)
        brightness = analysis.get('brightness', 128)
        if brightness < 50 or brightness > 200:
            score += 0.1
        
        # Contrast factor (low contrast might indicate poor quality/amateur content)
        contrast = analysis.get('contrast', 50)
        if contrast < 30:
            score += 0.1
        
        return min(score, 1.0)
    
    def classify_media_file(self, file_path: Path) -> Dict:
        """Classify a media file using advanced content analysis."""
        # Check cache first
        cached_result = self.get_cached_result(file_path)
        if cached_result:
            logger.debug(f"Using cached result for {file_path.name}")
            return cached_result
        
        # Determine file type
        extension = file_path.suffix.lower()
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
        
        result = {}
        
        if extension in image_extensions:
            result = self.analyze_image_content(file_path)
            result['file_type'] = 'image'
        elif extension in video_extensions:
            result = self.analyze_video_content(file_path)
            result['file_type'] = 'video'
        else:
            result = {
                'file_type': 'unsupported',
                'is_nsfw': False,
                'confidence': 0.0,
                'error': f'Unsupported file type: {extension}'
            }
        
        result['file_path'] = str(file_path)
        result['analysis_timestamp'] = os.path.getmtime(file_path)
        
        # Cache the result
        self.save_cached_result(file_path, result)
        
        return result
    
    def should_classify_file(self, file_path: Path) -> bool:
        """Check if a file should be content-classified."""
        extension = file_path.suffix.lower()
        supported_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff',  # Images
            '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'  # Videos
        }
        return extension in supported_extensions
