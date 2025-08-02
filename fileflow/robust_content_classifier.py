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
            'explicit': [
                'porn', 'xxx', 'sex', 'nude', 'naked', 'nsfw', 'adult', 'erotic',
                'bbc', 'interracial', 'creampie', 'orgy', 'gangbang', 'threesome',
                'cum', 'cumshot', 'facial', 'deepthroat', 'hardcore', 'softcore', 'amateur',
                'blacked', 'pawg', 'casting', 'taboo', 'incest', 'cuckold', 'swinger', 'dp',
                'double penetration', 'spitroast', 'gape', 'slut', 'whore', 'escort', 'bull'
            ],
            'body_parts': [
                'boobs', 'tits', 'ass', 'booty', 'dick', 'cock', 'pussy', 'vagina', 'penis',
                'clit', 'anus', 'butt', 'nipples', 'testicles', 'balls', 'cum', 'load'
            ],
            'actions': [
                'fuck', 'fucking', 'cumshot', 'cum', 'orgasm', 'masturbat', 'blowjob',
                'suck', 'lick', 'ride', 'spank', 'pegging', 'strapon', 'fisting', 'teabag',
                'rimming', '69', 'doggystyle', 'missionary', 'cowgirl', 'reverse cowgirl'
            ],
            'sites': [
                'pornhub', 'xvideos', 'xhamster', 'redtube', 'youporn', 'onlyfans', 'brazzers',
                'bangbros', 'naughtyamerica', 'realitykings', 'evilangel', 'teamskeet', 'spankbang'
            ],
            'categories': [
                'milf', 'teen', 'bdsm', 'fetish', 'anal', 'oral', 'lesbian', 'gay',
                'ebony', 'latina', 'asian', 'bbw', 'pawg', 'amateur', 'public', 'voyeur', 'exhibitionist'
            ]
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
        """
        Analyze filename and directory path for NSFW/SFW indicators.
        
        Returns:
            Dict containing:
            - is_explicit (bool): True if filename contains NSFW terms
            - is_sfw (bool): True if filename contains strong SFW indicators
            - reason (str): Explanation of the classification
            - confidence (float): Confidence score (0.0-1.0)
            - indicators (list): List of matched terms and their categories
        """
        filename = file_path.name.lower()
        parent_dirs = [p.lower() for p in file_path.parent.parts]
        
        result = {
            'is_explicit': False,
            'is_sfw': False,
            'confidence': 0.0,
            'reason': 'No explicit indicators found',
            'indicators': []
        }
        
        nsfw_matched = False
        for category, keywords in self.nsfw_keywords.items():
            for keyword in keywords:
                if keyword in filename or any(keyword in d for d in parent_dirs):
                    nsfw_matched = True
                    result['is_explicit'] = True
                    result['confidence'] = 0.95
                    result['reason'] = f"NSFW term ({category}): {keyword}"
                    result['indicators'].append((keyword, category))
        
        if not nsfw_matched:
            for keyword in self.sfw_indicators:
                if keyword in filename or any(keyword in d for d in parent_dirs):
                    result['is_sfw'] = True
                    result['confidence'] = 0.9
                    result['reason'] = f"SFW indicator: {keyword}"
        else:
            result['is_sfw'] = False
        
        return result
    
    def analyze_filename_only(self, file_path: Path) -> Dict:
        """
        First pass: Analyze only the filename for NSFW indicators.
        This is a quick check to identify potentially NSFW files before deeper analysis.
        
        Returns:
            Dict with 'is_potentially_nsfw' flag and confidence score
        """
        filename = file_path.name.lower()
        parent_dirs = [p.lower() for p in file_path.parent.parts]
        
        explicit_terms = [
            'porn', 'xxx', 'nsfw', 'adult', 'sex', 'fuck', 'dick', 'pussy', 'nude', 'naked',
            'bdsm', 'fetish', 'hentai', 'blowjob', 'handjob', 'cum', 'creampie', 'anal',
            'milf', 'lesbian', 'gay', 'shemale', 'tranny', 'futa', 'yiff', 'rule34',
            'cock', 'ass', 'boob', 'tits', 'titties', 'pornstar', 'xxxvideo', 'xxxpic',
            'hardcore', 'facial', 'orgy', 'threesome', 'gangbang', 'bukkake', 'bondage'
        ]
        
        sfw_indicators = [
            'family', 'kids', 'children', 'baby', 'wedding', 'graduation',
            'vacation', 'travel', 'nature', 'landscape', 'food', 'recipe',
            'tutorial', 'education', 'work', 'business', 'meeting'
        ]
        
        if any(term in filename or any(term in d for d in parent_dirs) for term in sfw_indicators):
            return {
                'is_potentially_nsfw': False,
                'confidence': 0.9,
                'reason': 'SFW indicators found in filename/path',
                'requires_content_analysis': False
            }
        
        nsfw_indicators = [term for term in explicit_terms 
                          if term in filename or any(term in d for d in parent_dirs)]
        
        if nsfw_indicators:
            return {
                'is_potentially_nsfw': True,
                'confidence': min(0.8, 0.5 + (len(nsfw_indicators) * 0.1)),
                'reason': f'Potential NSFW indicators: {", ".join(nsfw_indicators)}',
                'requires_content_analysis': True
            }
            
        return {
            'is_potentially_nsfw': False,
            'confidence': 0.7,
            'reason': 'No explicit indicators found',
            'requires_content_analysis': True  # Always require content analysis
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
        """Analyze video metadata for NSFW indicators."""
        if not self.has_ffmpeg:
            return {'error': 'FFmpeg not available for video analysis'}
        
        try:
            import subprocess
            import json
            
            # Get video metadata using FFprobe
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration:stream=width,height,bit_rate,duration',
                '-of', 'json',
                str(file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return {'error': f'FFprobe error: {result.stderr}'}
            
            metadata = json.loads(result.stdout)
            
            # Analyze video properties
            video_stream = next((s for s in metadata.get('streams', []) if s.get('codec_type') == 'video'), {})
            
            # Calculate suspicion score based on video properties
            suspicion_score = 0.0
            
            # Check for suspicious duration
            duration = float(metadata.get('format', {}).get('duration', 0))
            if 60 < duration < 300:  # 1-5 minute videos might be more likely to be NSFW
                suspicion_score += 0.2
                
            # Check for common NSFW video resolutions
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            if width > 0 and height > 0:
                if width == 1920 and height == 1080:  # Common HD resolution
                    suspicion_score += 0.1
                elif width == 1280 and height == 720:  # Common HD resolution
                    suspicion_score += 0.1
                    
            return {
                'duration': duration,
                'width': width,
                'height': height,
                'bitrate': int(video_stream.get('bit_rate', 0)) if video_stream.get('bit_rate') else None,
                'suspicion_score': min(suspicion_score, 1.0)
            }
            
        except Exception as e:
            logger.debug(f"Error analyzing video metadata: {e}")
            return {'error': str(e)}
            
    def analyze_video_frames(self, file_path: Path, sample_count: int = 5) -> List[Dict]:
        """Analyze sampled frames from a video for NSFW content."""
        if not self.has_ffmpeg or not self.has_opencv:
            return []
            
        try:
            import cv2
            import numpy as np
            import tempfile
            import subprocess
            import os
            
            # Get video duration
            duration = self.get_video_duration(file_path)
            if not duration or duration <= 0:
                return []
                
            # Calculate frame timestamps to sample
            timestamps = [i * (duration / (sample_count + 1)) for i in range(1, sample_count + 1)]
            
            frame_results = []
            
            # Extract and analyze frames at calculated timestamps
            for i, timestamp in enumerate(timestamps):
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_frame:
                    temp_path = temp_frame.name
                
                try:
                    # Extract frame using FFmpeg
                    cmd = [
                        'ffmpeg',
                        '-ss', str(timestamp),
                        '-i', str(file_path),
                        '-vframes', '1',
                        '-q:v', '2',
                        '-y',  # Overwrite output file if it exists
                        temp_path
                    ]
                    
                    subprocess.run(cmd, capture_output=True, check=True)
                    
                    # Analyze the extracted frame
                    frame_analysis = self.analyze_image_with_opencv(Path(temp_path))
                    
                    # Add frame position info
                    frame_analysis['timestamp'] = timestamp
                    frame_analysis['frame_number'] = i + 1
                    
                    # Only include successful analyses
                    if 'error' not in frame_analysis:
                        frame_results.append(frame_analysis)
                        
                except Exception as e:
                    logger.debug(f"Error analyzing video frame at {timestamp}s: {e}")
                finally:
                    # Clean up temporary frame file
                    try:
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                    except Exception as e:
                        logger.debug(f"Error cleaning up temp frame: {e}")
            
            return frame_results
            
        except Exception as e:
            logger.error(f"Error in analyze_video_frames: {e}")
            return []
    
    def get_video_duration(self, file_path: Path) -> float:
        """Get video duration in seconds using FFprobe."""
        try:
            import subprocess
            import json
            
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'json',
                str(file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return 0.0
                
            metadata = json.loads(result.stdout)
            return float(metadata.get('format', {}).get('duration', 0))
            
        except Exception as e:
            logger.debug(f"Error getting video duration: {e}")
            return 0.0
            
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
            'analysis_methods': exif_analysis.get('analysis_methods', [])
        }
    
    def analyze_filename_only(self, file_path: Path) -> Dict:
        """
        First pass: Analyze only the filename for NSFW indicators.
        This is a quick check to identify potentially NSFW files before deeper analysis.
        
        Returns:
            Dict with 'is_potentially_nsfw' flag and confidence score
        """
        filename = file_path.name.lower()
        parent_dirs = [p.lower() for p in file_path.parent.parts]
        
        # Check for explicit NSFW terms
        explicit_terms = [
            'porn', 'xxx', 'nsfw', 'adult', 'sex', 'fuck', 'dick', 'pussy', 'nude', 'naked',
            'bdsm', 'fetish', 'hentai', 'blowjob', 'handjob', 'cum', 'creampie', 'anal',
            'milf', 'lesbian', 'gay', 'shemale', 'tranny', 'futa', 'yiff', 'rule34',
            'cock', 'ass', 'boob', 'tits', 'titties', 'pornstar', 'xxxvideo', 'xxxpic',
            'hardcore', 'facial', 'orgy', 'threesome', 'gangbang', 'bukkake', 'bondage'
        ]
        
        # Check for SFW indicators that would override NSFW detection
        sfw_indicators = [
            'family', 'kids', 'children', 'baby', 'wedding', 'graduation',
            'vacation', 'travel', 'nature', 'landscape', 'food', 'recipe',
            'tutorial', 'education', 'work', 'business', 'meeting'
        ]
        
        # Check for SFW indicators first
        if any(term in filename or any(term in d for d in parent_dirs) for term in sfw_indicators):
            return {
                'is_potentially_nsfw': False,
                'confidence': 0.9,
                'reason': 'SFW indicators found in filename/path',
                'requires_content_analysis': False
            }
        
        # Check for NSFW indicators
        nsfw_indicators = [term for term in explicit_terms 
                          if term in filename or any(term in d for d in parent_dirs)]
        
        if nsfw_indicators:
            return {
                'is_potentially_nsfw': True,
                'confidence': min(0.8, 0.5 + (len(nsfw_indicators) * 0.1)),
                'reason': f'Potential NSFW indicators: {", ".join(nsfw_indicators)}',
                'requires_content_analysis': True
            }
            
        return {
            'is_potentially_nsfw': False,
            'confidence': 0.7,
            'reason': 'No explicit indicators found',
            'requires_content_analysis': True  # Always require content analysis
        }

    def analyze_content(self, file_path: Path, filename_analysis: Dict = None) -> Dict:
        """
        Second pass: Analyze file content to confirm/override filename analysis.
        """
        # Initialize result
        result = {
            'file_path': str(file_path),
            'file_type': '',
            'is_nsfw': False,
            'confidence': 0.0,
            'nsfw_score': 0.0,
            'analysis_methods': [],
            'details': {
                'filename_analysis': filename_analysis or {}
            }
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
            result['is_nsfw'] = False
            result['confidence'] = 1.0
            result['analysis_methods'] = ['non_media']
            return result
            
        # Analyze content based on file type
        if result['file_type'] == 'image':
            # Use OpenCV for image analysis
            opencv_analysis = self.analyze_image_with_opencv(file_path)
            if 'error' not in opencv_analysis:
                result['details']['opencv'] = opencv_analysis
                result['analysis_methods'].append('opencv')
                
                skin_percentage = opencv_analysis.get('skin_percentage', 0)
                visual_score = opencv_analysis.get('visual_score', 0)
                
                # High confidence NSFW detection
                if skin_percentage > 60 and visual_score > 0.7:  # Adjusted thresholds
                    result.update({
                        'is_nsfw': True,
                        'confidence': visual_score,
                        'nsfw_score': visual_score,
                        'details': {
                            **result['details'],
                            'reason': f'High confidence NSFW content (skin: {skin_percentage:.1f}%, score: {visual_score:.2f})'
                    }
                })
            else:
                result.update({
                    'is_nsfw': False,
                    'confidence': max(0.8, 1.0 - visual_score),  # Higher confidence for low NSFW scores
                    'nsfw_score': visual_score,
                    'details': {
                        **result['details'],
                        'reason': 'No NSFW content detected in image analysis'
                    }
                })
        
        elif result['file_type'] == 'video':
            # Analyze video metadata and sample frames
            video_analysis = self.analyze_video_metadata(file_path)
            result['details']['video_metadata'] = video_analysis
            result['analysis_methods'].append('video_metadata')
            
            # Sample and analyze frames
            frame_analysis = self.analyze_video_frames(file_path, sample_count=5)
            if frame_analysis:
                result['details']['frame_analysis'] = frame_analysis
                result['analysis_methods'].append('frame_analysis')
                
                # Get max NSFW score from frames
                nsfw_scores = [f.get('nsfw_score', 0) for f in frame_analysis]
                max_nsfw_score = max(nsfw_scores) if nsfw_scores else 0
                
                if max_nsfw_score > 0.8:  # High confidence threshold
                    result.update({
                        'is_nsfw': True,
                        'confidence': max_nsfw_score,
                        'nsfw_score': max_nsfw_score,
                        'details': {
                            **result['details'],
                            'reason': f'High confidence NSFW content in video frames (max score: {max_nsfw_score:.2f})'
                        }
                    })
                else:
                    result.update({
                        'is_nsfw': False,
                        'confidence': 0.9,
                        'nsfw_score': max_nsfw_score,
                        'details': {
                            **result['details'],
                            'reason': 'No NSFW content detected in video frames'
                        }
                    })
        
        return result

    def should_classify_file(self, file_path: Path) -> bool:
        """Check if a file should be content-classified.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if the file should be classified, False otherwise
        """
        extension = file_path.suffix.lower()
        supported_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff',  # Images
            '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'  # Videos
        }
        return extension in supported_extensions
        
    def classify_media_file(self, file_path: Path) -> Dict:
        """
        Classify a media file using a two-pass system:
        1. First pass: Quick filename analysis
        2. Second pass: Content analysis for all files
        """
        # Check cache first
        cached_result = self.get_cached_result(file_path)
        if cached_result:
            return cached_result
            
        # Initialize result with default values
        result = {
            'file_path': str(file_path),
            'file_type': 'other',
            'is_nsfw': False,
            'confidence': 0.5,  # Default confidence level
            'nsfw_score': 0.0,
            'analysis_methods': [],
            'details': {}
        }
        
        # First pass: Filename analysis
        filename_analysis = self.analyze_filename_only(file_path)
        result['details']['filename_analysis'] = filename_analysis
        result['analysis_methods'].append('filename_analysis')
        
        # Check file extension to determine type
        extension = file_path.suffix.lower()
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
        
        if extension in image_extensions:
            result['file_type'] = 'image'
        elif extension in video_extensions:
            result['file_type'] = 'video'
        else:
            result['file_type'] = 'other'
            result['is_nsfw'] = False  # Explicitly mark non-media as SFW
            result['confidence'] = 1.0
            result['analysis_methods'] = ['non_media']
            self.save_cached_result(file_path, result)
            return result  # Return SFW for non-media files
            
        # If filename analysis is very confident, we can skip content analysis for SFW
        if (not filename_analysis.get('is_potentially_nsfw', False) and 
            filename_analysis.get('confidence', 0) >= 0.9 and
            not filename_analysis.get('requires_content_analysis', True)):
            
            result.update({
                'is_nsfw': False,
                'confidence': filename_analysis.get('confidence', 0.9),
                'nsfw_score': 0.0,
                'details': {
                    **result['details'],
                    'reason': 'High confidence SFW from filename analysis'
                }
            })
            self.save_cached_result(file_path, result)
            return result
            
        # Perform full filename analysis
        filename_analysis = self.analyze_filename(file_path)
        result['details']['filename_analysis'] = filename_analysis
        
        # If we already have a cached result from analyze_filename_only, don't overwrite it
        if 'filename_analysis' not in result['analysis_methods']:
            result['analysis_methods'].append('filename_analysis')
        
        # 2. If filename is explicitly NSFW, set flag but do NOT return; always perform content analysis
        filename_is_explicit = filename_analysis.get('is_explicit', False)
        if filename_is_explicit:
            result['details']['reason'] = f'Explicit filename detected: {filename_analysis["reason"]}'
            result['analysis_methods'].append('explicit_filename')
        
        # 3. If filename is explicitly SFW, trust it unless content strongly suggests otherwise
        if filename_analysis.get('is_sfw', False):
            result['is_nsfw'] = False
            result['confidence'] = 0.9
            result['nsfw_score'] = 0.1
            result['details']['reason'] = f'Explicitly SFW filename: {filename_analysis["reason"]}'
            result['analysis_methods'].append('explicit_sfw_filename')
        
        # NSFW detection for images
        if result['file_type'] == 'image':
            # Analyze image with OpenCV
            opencv_analysis = self.analyze_image_with_opencv(file_path)
            if 'error' not in opencv_analysis:
                result['details']['opencv'] = opencv_analysis
                result['analysis_methods'].append('opencv')
                
                skin_percentage = opencv_analysis.get('skin_percentage', 0)
                visual_score = opencv_analysis.get('visual_score', 0)
                
                # If filename is explicit, require less visual evidence
                is_explicit_filename = filename_analysis.get('is_explicit', False)
                if is_explicit_filename:
                    if skin_percentage > 40 or visual_score > 0.6:
                        result['is_nsfw'] = True
                        result['confidence'] = 0.95
                        result['nsfw_score'] = max(visual_score, 0.8)  # High confidence for explicit filenames
                        result['details']['reason'] = f'Explicit filename with supporting visual evidence (skin: {skin_percentage:.1f}%, score: {visual_score:.2f})'
                    else:
                        result['is_nsfw'] = False
                        result['confidence'] = 0.8
                        result['nsfw_score'] = 0.2
                        result['details']['reason'] = 'Explicit filename but no supporting visual evidence'
                else:
                    # For normal filenames, require very strong visual evidence
                    if skin_percentage > 70 and visual_score > 0.85:
                        result['is_nsfw'] = True
                        result['confidence'] = 0.9
                        result['nsfw_score'] = visual_score
                        result['details']['reason'] = f'High confidence NSFW content (skin: {skin_percentage:.1f}%, score: {visual_score:.2f})'
                    else:
                        result['is_nsfw'] = False
                        result['confidence'] = 0.9
                        result['nsfw_score'] = 0.1
                        result['details']['reason'] = 'No NSFW content detected'
        
        # NSFW detection for videos
        elif result['file_type'] == 'video':
            # First check video metadata
            video_analysis = self.analyze_video_metadata(file_path)
            result['details']['video'] = video_analysis
            result['analysis_methods'].append('video_metadata')
            
            # Sample frames for visual analysis
            frame_analysis = self.analyze_video_frames(file_path, sample_count=5)
            if frame_analysis:
                result['details']['frame_analysis'] = frame_analysis
                result['analysis_methods'].append('frame_analysis')
                
                # Check if any sampled frame indicates NSFW content
                nsfw_frames = [f for f in frame_analysis if f.get('is_nsfw', False)]
                nsfw_confidence = max((f.get('nsfw_score', 0) for f in frame_analysis), default=0)
                
                # If filename is explicit, require less visual evidence
                is_explicit_filename = filename_analysis.get('is_explicit', False)
                if is_explicit_filename:
                    if nsfw_frames or nsfw_confidence > 0.5:
                        result['is_nsfw'] = True
                        result['confidence'] = max(0.9, nsfw_confidence)
                        result['nsfw_score'] = max(0.8, nsfw_confidence)
                        result['details']['reason'] = f'Explicit filename with {len(nsfw_frames)} NSFW frames (max confidence: {nsfw_confidence:.2f})'
                    else:
                        result['is_nsfw'] = False
                        result['confidence'] = 0.8
                        result['nsfw_score'] = 0.2
                        result['details']['reason'] = 'Explicit filename but no supporting visual evidence in frames'
                else:
                    # For normal filenames, require stronger evidence
                    if nsfw_frames and nsfw_confidence > 0.8:
                        result['is_nsfw'] = True
                        result['confidence'] = nsfw_confidence
                        result['nsfw_score'] = nsfw_confidence
                        result['details']['reason'] = f'High confidence NSFW content in {len(nsfw_frames)} frames (max confidence: {nsfw_confidence:.2f})'
                    else:
                        result['is_nsfw'] = False
                        result['confidence'] = 0.9
                        result['nsfw_score'] = 0.1
                        result['details']['reason'] = 'No NSFW content detected in sampled frames'
            else:
                # Fallback to metadata analysis if frame analysis fails
                result['is_nsfw'] = video_analysis.get('suspicion_score', 0) > 0.7
                result['confidence'] = 0.7
                result['nsfw_score'] = video_analysis.get('suspicion_score', 0)
                result['details']['reason'] = 'Using video metadata analysis only'
        
        # For other file types, use basic analysis
        else:
            # Basic analysis for non-media files
            result['is_nsfw'] = False
            result['confidence'] = 1.0
            result['nsfw_score'] = 0.0
            result['details']['reason'] = 'Non-media file - treated as SFW'
        
        # 2. File properties analysis
        try:
            properties_analysis = self.analyze_file_properties(file_path)
            if properties_analysis:
                result['details']['properties'] = properties_analysis
                result['analysis_methods'].append('properties')
                
                # Adjust score based on file properties
                if properties_analysis.get('suspicious_size', False):
                    result['nsfw_score'] += properties_analysis.get('size_score', 0)
        except Exception as e:
            result['details']['properties_error'] = str(e)
        
        # 3. Content-specific analysis
        try:
            if result['file_type'] == 'image':
                # Try Pillow analysis first (lightweight)
                if self.has_pillow:
                    pillow_analysis = self.analyze_image_with_pillow(file_path)
                    if 'error' not in pillow_analysis and pillow_analysis is not None:
                        result['details']['pillow'] = pillow_analysis
                        result['analysis_methods'].append('pillow')
                        
                        # Adjust score based on image properties
                        suspicion_score = pillow_analysis.get('suspicion_score', 0)
                        result['nsfw_score'] = max(result['nsfw_score'], suspicion_score)
                
                # Try OpenCV analysis if available (advanced)
                if self.has_opencv:
                    opencv_analysis = self.analyze_image_with_opencv(file_path)
                    if 'error' not in opencv_analysis and opencv_analysis is not None:
                        result['details']['opencv'] = opencv_analysis
                        result['analysis_methods'].append('opencv')
                        
                        # Use visual analysis to override or confirm filename analysis
                        visual_score = opencv_analysis.get('visual_score', 0)
                        skin_percentage = opencv_analysis.get('skin_percentage', 0)
                        
                        # Update NSFW score based on visual analysis
                        if skin_percentage > 0 or visual_score > 0:
                            # Weight visual analysis more heavily than other factors
                            result['nsfw_score'] = max(result['nsfw_score'], visual_score * 1.5)
                            
                            # Require BOTH high skin percentage and high visual score for NSFW
                            if skin_percentage > 60 and visual_score > 0.6:
                                result['is_nsfw'] = True
                                result['confidence'] = max(result['confidence'], 0.9)
                                result['details']['reason'] = 'Visual analysis indicates NSFW content'
                            # If visual analysis strongly suggests SFW
                            elif visual_score < 0.2 and skin_percentage < 10:
                                result['is_nsfw'] = False
                                result['confidence'] = max(result['confidence'], 0.8)
                                result['details']['reason'] = 'Visual analysis confirms SFW content'
            
            elif result['file_type'] == 'video':
                # First check video metadata
                video_analysis = self.analyze_video_metadata(file_path)
                if 'error' not in video_analysis and video_analysis is not None:
                    result['details']['video_metadata'] = video_analysis
                    result['analysis_methods'].append('video_metadata')
                    
                    # Adjust score based on video properties
                    suspicion_score = video_analysis.get('suspicion_score', 0)
                    result['nsfw_score'] = max(result['nsfw_score'], suspicion_score)
                
                # If OpenCV is available, analyze video frames
                if self.has_opencv:
                    frame_analysis = self.analyze_video_frames(file_path, sample_count=3)
                    if frame_analysis:
                        result['details']['frame_analysis'] = frame_analysis
                        result['analysis_methods'].append('frame_analysis')
                        
                        # Check if any sampled frame indicates NSFW content
                        nsfw_frames = [f for f in frame_analysis if f.get('is_nsfw', False)]
                        nsfw_confidence = max((f.get('nsfw_score', 0) for f in frame_analysis), default=0)
                        
                        if nsfw_frames and nsfw_confidence > 0.7:
                            result['is_nsfw'] = True
                            result['confidence'] = max(result['confidence'], nsfw_confidence)
                            result['nsfw_score'] = max(result['nsfw_score'], nsfw_confidence)
                            result['details']['reason'] = f'NSFW content detected in {len(nsfw_frames)} frames (max confidence: {nsfw_confidence:.2f})'
        
        except Exception as e:

        # Nuanced combination of filename and content analysis
        if filename_analysis.get('is_explicit', False):
            if result['nsfw_score'] > 0.6:
                result['is_nsfw'] = True
                result['confidence'] = max(result['confidence'], 0.97)
                result['nsfw_score'] = max(result['nsfw_score'], 0.9)
                result['details']['reason'] = 'Explicit filename and content both NSFW'
            elif result['nsfw_score'] < 0.3:
                result['is_nsfw'] = False
                result['confidence'] = min(result['confidence'], 0.6)
                result['nsfw_score'] = min(result['nsfw_score'], 0.2)
                result['details']['reason'] = 'Explicit NSFW filename but content clearly SFW'
            else:
                result['is_nsfw'] = True
                result['confidence'] = 0.7
                result['nsfw_score'] = max(result['nsfw_score'], 0.6)
                result['details']['reason'] = 'Explicit NSFW filename, content ambiguous'
        elif filename_analysis.get('is_sfw', False):
            # Only trust SFW markers if we don't have strong NSFW evidence
            if result['nsfw_score'] < 0.7:
                result['is_nsfw'] = False
                result['confidence'] = max(result['confidence'], 0.9)
                result['nsfw_score'] = min(result['nsfw_score'], 0.3)
                result['details']['reason'] = 'Explicit SFW markers in filename'
            else:
                result['is_nsfw'] = True
                result['confidence'] = max(result['confidence'], 0.8)
                result['details']['reason'] = 'SFW filename but content is strongly NSFW'
        else:
            # If we have no strong indicators either way, use the calculated score
            result['is_nsfw'] = result['nsfw_score'] > 0.6
            result['confidence'] = min(max(result['confidence'], result['nsfw_score'] * 1.2), 1.0)
            if 'reason' not in result['details']:
                result['details']['reason'] = 'Content analysis completed'
        # Cache and return the result
        self.save_cached_result(file_path, result)
        return result


# This line should be the end of the file
