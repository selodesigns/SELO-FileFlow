import os
import hashlib
import json
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import subprocess
import tempfile
from .utils.logging import get_logger
from .enhanced_exif_analyzer import EnhancedExifAnalyzer

# Suppress libpng warnings globally
warnings.filterwarnings('ignore', message='.*iCCP.*')
warnings.filterwarnings('ignore', message='.*sRGB.*')
warnings.filterwarnings('ignore', category=UserWarning, module='PIL')

logger = get_logger()

class RobustContentClassifier:
    """Robust content classifier using multiple analysis methods without heavy dependencies."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the robust content classifier.
        
        Args:
            cache_dir: Directory to store analysis cache. If None, uses default location.
        """
        self.cache_dir = cache_dir or (Path.home() / '.cache' / 'selo-fileflow' / 'content_analysis')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # NSFW indicators for filename analysis
        self.nsfw_keywords = {
            'explicit': ['porn', 'xxx', 'sex', 'nude', 'naked', 'nsfw', 'adult', 'erotic'],
            'body_parts': ['boobs', 'tits', 'ass', 'dick', 'cock', 'pussy', 'vagina', 'penis'],
            'actions': ['fuck', 'fucking', 'cumshot', 'cum', 'orgasm', 'masturbat', 'blowjob'],
            'sites': ['pornhub', 'xvideos', 'xhamster', 'redtube', 'youporn', 'onlyfans'],
            'categories': ['milf', 'teen', 'bdsm', 'fetish', 'anal', 'oral', 'lesbian', 'gay']
        }
        
        # SFW indicators (override NSFW detection)
        self.sfw_indicators = [
            'family', 'kids', 'children', 'baby', 'wedding', 'graduation',
            'vacation', 'travel', 'nature', 'landscape', 'food', 'recipe',
            'tutorial', 'education', 'work', 'business', 'meeting'
        ]
        
        # Check for available analysis tools
        self.has_pillow = self._check_pillow()
        self.has_opencv = self._check_opencv()
        self.has_exiftool = self._check_exiftool()
        
        # Initialize enhanced EXIF analyzer
        self.exif_analyzer = EnhancedExifAnalyzer()
    
    def _check_pillow(self) -> bool:
        """Check if Pillow is available for image analysis."""
        try:
            from PIL import Image, ExifTags
            return True
        except ImportError:
            logger.debug("Pillow not available - basic image analysis disabled")
            return False
    
    def _check_opencv(self) -> bool:
        """Check if OpenCV is available for advanced image analysis."""
        try:
            import cv2
            import numpy as np
            return True
        except ImportError:
            logger.debug("OpenCV not available - advanced visual analysis disabled")
            return False
    
    def _check_exiftool(self) -> bool:
        """Check if exiftool is available for metadata extraction."""
        try:
            subprocess.run(['exiftool', '-ver'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.debug("exiftool not available - advanced metadata analysis disabled")
            return False
    
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
    
    def analyze_filename(self, file_path: Path) -> Dict:
        """Analyze filename and directory path for NSFW indicators."""
        filename = file_path.name.lower()
        parent_dirs = [p.name.lower() for p in file_path.parents if p.name]
        
        # Check for SFW indicators first
        for indicator in self.sfw_indicators:
            if indicator in filename:
                return {
                    'is_nsfw': False,
                    'confidence': 0.8,
                    'reason': f"SFW indicator: {indicator}",
                    'method': 'filename_sfw'
                }
        
        # Check for NSFW keywords
        for category, keywords in self.nsfw_keywords.items():
            for keyword in keywords:
                if keyword in filename:
                    return {
                        'is_nsfw': True,
                        'confidence': 0.9,
                        'reason': f"NSFW keyword ({category}): {keyword}",
                        'method': 'filename_nsfw'
                    }
        
        # Check parent directories
        for dir_name in parent_dirs[:3]:
            for category, keywords in self.nsfw_keywords.items():
                for keyword in keywords:
                    if keyword in dir_name:
                        return {
                            'is_nsfw': True,
                            'confidence': 0.7,
                            'reason': f"NSFW directory ({category}): {keyword}",
                            'method': 'directory_nsfw'
                        }
        
        return {
            'is_nsfw': False,
            'confidence': 0.3,
            'reason': "No obvious indicators in filename",
            'method': 'filename_neutral'
        }
    
    def analyze_file_properties(self, file_path: Path) -> Dict:
        """Analyze basic file properties for suspicious characteristics."""
        try:
            stat = file_path.stat()
            properties = {
                'size_mb': stat.st_size / (1024 * 1024),
                'extension': file_path.suffix.lower(),
                'creation_time': stat.st_ctime,
                'modification_time': stat.st_mtime
            }
            
            # Analyze file size patterns
            size_score = 0.0
            if properties['extension'] in ['.jpg', '.jpeg', '.png']:
                # Very large images might be high-resolution adult content
                if properties['size_mb'] > 10:
                    size_score += 0.2
                elif properties['size_mb'] > 5:
                    size_score += 0.1
            elif properties['extension'] in ['.mp4', '.avi', '.mov', '.mkv']:
                # Very large videos might be adult content
                if properties['size_mb'] > 1000:  # > 1GB
                    size_score += 0.3
                elif properties['size_mb'] > 500:  # > 500MB
                    size_score += 0.2
            
            return {
                'properties': properties,
                'size_score': size_score,
                'suspicious_size': size_score > 0.1
            }
            
        except Exception as e:
            logger.debug(f"Failed to analyze file properties for {file_path}: {e}")
            return {'properties': {}, 'size_score': 0.0, 'suspicious_size': False}
    
    def analyze_image_with_pillow(self, file_path: Path) -> Dict:
        """Analyze image using Pillow (lightweight image analysis)."""
        if not self.has_pillow:
            return {'error': 'Pillow not available'}
        
        try:
            from PIL import Image, ExifTags
            
            with Image.open(file_path) as img:
                analysis = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height
                }
                
                # Analyze image characteristics
                aspect_ratio = img.width / img.height if img.height > 0 else 1.0
                total_pixels = img.width * img.height
                
                # Calculate suspicion score based on image properties
                suspicion_score = 0.0
                
                # Very high resolution might indicate professional adult content
                if total_pixels > 8000000:  # > 8MP
                    suspicion_score += 0.2
                elif total_pixels > 4000000:  # > 4MP
                    suspicion_score += 0.1
                
                # Extreme aspect ratios might indicate cropped/edited content
                if aspect_ratio > 3.0 or aspect_ratio < 0.33:
                    suspicion_score += 0.1
                
                # Use enhanced EXIF analysis
                exif_analysis = self.exif_analyzer.calculate_exif_suspicion_score(file_path)
                exif_score = exif_analysis.get('exif_score', 0.0)
                exif_confidence = exif_analysis.get('confidence', 0.0)
                exif_details = exif_analysis.get('analysis_details', {})
                
                analysis.update({
                    'aspect_ratio': aspect_ratio,
                    'total_pixels': total_pixels,
                    'suspicion_score': suspicion_score + exif_score,  # Combine scores
                    'exif_analysis': exif_analysis,
                    'exif_score': exif_score,
                    'exif_confidence': exif_confidence,
                    'exif_details': exif_details
                })
                
                return analysis
                
        except Exception as e:
            logger.debug(f"Failed to analyze image with Pillow: {e}")
            return {'error': str(e)}
    
    def analyze_image_with_opencv(self, file_path: Path) -> Dict:
        """Analyze image using OpenCV (advanced visual analysis)."""
        if not self.has_opencv:
            return {'error': 'OpenCV not available'}
        
        try:
            import cv2
            import numpy as np
            
            # Load image
            image = cv2.imread(str(file_path))
            if image is None:
                return {'error': 'Could not load image'}
            
            # Resize for faster processing
            height, width = image.shape[:2]
            if width > 800:
                scale = 800 / width
                new_width = 800
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
            
            # Basic color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Skin color detection (simple HSV range)
            skin_lower = np.array([0, 20, 70], dtype=np.uint8)
            skin_upper = np.array([20, 255, 255], dtype=np.uint8)
            skin_mask = cv2.inRange(hsv, skin_lower, skin_upper)
            
            skin_pixels = cv2.countNonZero(skin_mask)
            total_pixels = image.shape[0] * image.shape[1]
            skin_percentage = (skin_pixels / total_pixels) * 100 if total_pixels > 0 else 0.0
            
            # Brightness and contrast analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Calculate visual suspicion score with stricter thresholds
            visual_score = 0.0
            if skin_percentage > 60:
                visual_score += 0.6  # Strong NSFW indicator
            elif skin_percentage > 40:
                visual_score += 0.3  # Moderate suspicion
            elif skin_percentage > 20:
                visual_score += 0.1  # Low suspicion
            # skin_percentage <= 20% adds no visual suspicion
            
            # Very dark or very bright images might be suspicious (but much less weight)
            if brightness < 50 or brightness > 200:
                visual_score += 0.05  # Reduced from 0.1 to prevent false positives
            
            return {
                'skin_percentage': skin_percentage,
                'brightness': float(brightness),
                'contrast': float(contrast),
                'visual_score': visual_score,
                'image_shape': image.shape
            }
            
        except Exception as e:
            logger.debug(f"Failed to analyze image with OpenCV: {e}")
            return {'error': str(e)}
    
    def analyze_video_metadata(self, file_path: Path) -> Dict:
        """Analyze video file metadata."""
        try:
            # Try to get basic video info using ffprobe if available
            try:
                cmd = [
                    'ffprobe', '-v', 'quiet', '-print_format', 'json',
                    '-show_format', '-show_streams', str(file_path)
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    import json
                    metadata = json.loads(result.stdout)
                    
                    # Extract relevant information
                    format_info = metadata.get('format', {})
                    duration = float(format_info.get('duration', 0))
                    size_mb = int(format_info.get('size', 0)) / (1024 * 1024)
                    
                    # Calculate suspicion based on video characteristics
                    suspicion_score = 0.0
                    
                    # Very long videos might be adult content
                    if duration > 3600:  # > 1 hour
                        suspicion_score += 0.2
                    elif duration > 1800:  # > 30 minutes
                        suspicion_score += 0.1
                    
                    # High bitrate for duration might indicate high-quality adult content
                    if duration > 0:
                        bitrate = (size_mb * 8) / (duration / 60)  # Mbps
                        if bitrate > 10:
                            suspicion_score += 0.1
                    
                    return {
                        'duration': duration,
                        'size_mb': size_mb,
                        'suspicion_score': suspicion_score,
                        'has_metadata': True
                    }
                    
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                logger.debug(f"ffprobe not available or failed for {file_path}")
            
            # Fallback to basic file analysis
            stat = file_path.stat()
            size_mb = stat.st_size / (1024 * 1024)
            
            suspicion_score = 0.0
            if size_mb > 1000:  # > 1GB
                suspicion_score += 0.3
            elif size_mb > 500:  # > 500MB
                suspicion_score += 0.2
            
            return {
                'size_mb': size_mb,
                'suspicion_score': suspicion_score,
                'has_metadata': False
            }
            
        except Exception as e:
            logger.debug(f"Failed to analyze video metadata: {e}")
            return {'error': str(e)}
    
    def get_comprehensive_exif_analysis(self, file_path: Path) -> Dict:
        """Get comprehensive EXIF analysis for display and debugging purposes."""
        if not file_path.exists():
            return {'error': 'File not found'}
        
        # Get enhanced EXIF analysis
        exif_analysis = self.exif_analyzer.calculate_exif_suspicion_score(file_path)
        
        # Get EXIF summary for display
        exif_summary = self.exif_analyzer.get_exif_summary(file_path)
        
        return {
            'file_path': str(file_path),
            'exif_analysis': exif_analysis,
            'exif_summary': exif_summary,
            'analysis_methods': exif_analysis.get('analysis_methods', []),
            'has_exif': exif_analysis.get('has_exif', False),
            'exif_score': exif_analysis.get('exif_score', 0.0),
            'confidence': exif_analysis.get('confidence', 0.0)
        }
    
    def classify_media_file(self, file_path: Path) -> Dict:
        """Classify a media file using all available analysis methods."""
        # Check cache first
        cached_result = self.get_cached_result(file_path)
        if cached_result:
            logger.debug(f"Using cached result for {file_path.name}")
            return cached_result
        
        # Initialize result
        result = {
            'file_path': str(file_path),
            'file_type': 'unknown',
            'is_nsfw': False,
            'confidence': 0.0,
            'nsfw_score': 0.0,
            'analysis_methods': [],
            'details': {}
        }
        
        # Determine file type
        extension = file_path.suffix.lower()
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
        
        if extension in image_extensions:
            result['file_type'] = 'image'
        elif extension in video_extensions:
            result['file_type'] = 'video'
        else:
            result['file_type'] = 'other'
        
        # 1. Filename analysis (always available)
        filename_analysis = self.analyze_filename(file_path)
        result['details']['filename'] = filename_analysis
        result['analysis_methods'].append('filename')
        
        # Start with filename analysis results
        result['is_nsfw'] = filename_analysis['is_nsfw']
        result['confidence'] = filename_analysis['confidence']
        result['nsfw_score'] = 0.8 if filename_analysis['is_nsfw'] else 0.2
        
        # 2. File properties analysis
        properties_analysis = self.analyze_file_properties(file_path)
        result['details']['properties'] = properties_analysis
        result['analysis_methods'].append('properties')
        
        # Adjust score based on file properties
        if properties_analysis.get('suspicious_size', False):
            result['nsfw_score'] += properties_analysis.get('size_score', 0)
        
        # 3. Content-specific analysis
        if result['file_type'] == 'image':
            # Try Pillow analysis first (lightweight)
            pillow_analysis = self.analyze_image_with_pillow(file_path)
            if 'error' not in pillow_analysis:
                result['details']['pillow'] = pillow_analysis
                result['analysis_methods'].append('pillow')
                
                # Adjust score based on image properties
                suspicion_score = pillow_analysis.get('suspicion_score', 0)
                result['nsfw_score'] += suspicion_score
            
            # Try OpenCV analysis if available (advanced)
            opencv_analysis = self.analyze_image_with_opencv(file_path)
            if 'error' not in opencv_analysis:
                result['details']['opencv'] = opencv_analysis
                result['analysis_methods'].append('opencv')
                
                # Use visual analysis to override or confirm filename analysis
                visual_score = opencv_analysis.get('visual_score', 0)
                skin_percentage = opencv_analysis.get('skin_percentage', 0)

                # Revised: Require BOTH high skin percentage and high visual score for NSFW
                # Only mark NSFW if skin_percentage > 60 and visual_score > 0.6
                if skin_percentage > 60 and visual_score > 0.6:
                    result['is_nsfw'] = True
                    result['confidence'] = max(result['confidence'], 0.9)
                    result['nsfw_score'] = max(result['nsfw_score'], visual_score)
                # If visual analysis strongly suggests SFW and filename was uncertain
                elif visual_score < 0.2 and skin_percentage < 10 and result['confidence'] < 0.7:
                    result['is_nsfw'] = False
                    result['confidence'] = 0.7
                    result['nsfw_score'] = min(result['nsfw_score'], visual_score)
                # Otherwise, do not override filename-based or other analysis
                # (prevents false positives for normal photos with some skin tones)
        
        elif result['file_type'] == 'video':
            video_analysis = self.analyze_video_metadata(file_path)
            if 'error' not in video_analysis:
                result['details']['video'] = video_analysis
                result['analysis_methods'].append('video_metadata')
                
                # Adjust score based on video properties
                suspicion_score = video_analysis.get('suspicion_score', 0)
                result['nsfw_score'] += suspicion_score
        
        # Final classification based on combined score
        result['nsfw_score'] = min(result['nsfw_score'], 1.0)
        
        # If no strong filename indicators, use combined analysis
        if filename_analysis['method'] == 'filename_neutral':
            result['is_nsfw'] = result['nsfw_score'] > 0.6
            result['confidence'] = min(result['nsfw_score'] * 1.2, 1.0)
        
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
