import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from .utils.logging import get_logger

logger = get_logger()

class EnhancedExifAnalyzer:
    """Enhanced EXIF data analyzer for content classification using multiple methods."""
    
    def __init__(self):
        self.has_exiftool = self._check_exiftool()
        self.has_pillow = self._check_pillow()
        
        # EXIF fields that might indicate content type
        self.suspicious_software = [
            'photoshop', 'gimp', 'paint.net', 'canva', 'pixlr', 'snapseed',
            'facetune', 'vsco', 'lightroom', 'afterlight', 'beauty', 'filter'
        ]
        
        self.camera_brands_professional = [
            'canon', 'nikon', 'sony', 'fujifilm', 'leica', 'hasselblad',
            'pentax', 'olympus', 'panasonic', 'sigma'
        ]
        
        # Keywords in EXIF that might indicate content type
        self.nsfw_exif_keywords = [
            'adult', 'nude', 'naked', 'sexy', 'erotic', 'porn', 'xxx',
            'boudoir', 'intimate', 'sensual', 'lingerie'
        ]
        
        self.sfw_exif_keywords = [
            'family', 'wedding', 'portrait', 'landscape', 'nature', 'travel',
            'vacation', 'business', 'professional', 'corporate', 'event'
        ]
    
    def _check_exiftool(self) -> bool:
        """Check if ExifTool is available."""
        try:
            result = subprocess.run(['exiftool', '-ver'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_pillow(self) -> bool:
        """Check if Pillow is available."""
        try:
            from PIL import Image, ExifTags
            return True
        except ImportError:
            return False
    
    def extract_exif_with_exiftool(self, file_path: Path) -> Dict[str, Any]:
        """Extract comprehensive EXIF data using ExifTool."""
        if not self.has_exiftool:
            return {}
        
        try:
            cmd = [
                'exiftool', '-json', '-all', '-coordFormat', '%.6f',
                '-dateFormat', '%Y-%m-%d %H:%M:%S', str(file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data[0] if data else {}
            else:
                logger.debug(f"ExifTool failed for {file_path}: {result.stderr}")
                return {}
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, 
                json.JSONDecodeError, IndexError) as e:
            logger.debug(f"ExifTool extraction failed for {file_path}: {e}")
            return {}
    
    def extract_exif_with_pillow(self, file_path: Path) -> Dict[str, Any]:
        """Extract EXIF data using Pillow (fallback method)."""
        if not self.has_pillow:
            return {}
        
        try:
            from PIL import Image, ExifTags
            import warnings
            
            # Suppress libpng warnings
            warnings.filterwarnings('ignore', category=UserWarning, module='PIL')
            
            with Image.open(file_path) as img:
                exif_data = {}
                
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    exif = img._getexif()
                    
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        
                        # Convert bytes to string if needed
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8', errors='ignore')
                            except:
                                value = str(value)
                        
                        # Handle nested EXIF data
                        if tag == 'ExifOffset' and isinstance(value, dict):
                            for sub_tag_id, sub_value in value.items():
                                sub_tag = ExifTags.TAGS.get(sub_tag_id, sub_tag_id)
                                exif_data[f'Exif_{sub_tag}'] = sub_value
                        else:
                            exif_data[tag] = value
                
                return exif_data
                
        except Exception as e:
            logger.debug(f"Pillow EXIF extraction failed for {file_path}: {e}")
            return {}
    
    def analyze_camera_settings(self, exif_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze camera settings for content classification clues."""
        analysis = {
            'is_professional': False,
            'is_edited': False,
            'is_smartphone': False,
            'has_location': False,
            'suspicious_settings': False,
            'content_hints': []
        }
        
        # Check camera make/model
        make = str(exif_data.get('Make', '')).lower()
        model = str(exif_data.get('Model', '')).lower()
        
        # Professional camera detection
        if any(brand in make for brand in self.camera_brands_professional):
            analysis['is_professional'] = True
            analysis['content_hints'].append('professional_camera')
        
        # Smartphone detection
        if any(phone in make.lower() or phone in model.lower() 
               for phone in ['iphone', 'samsung', 'pixel', 'oneplus', 'huawei']):
            analysis['is_smartphone'] = True
            analysis['content_hints'].append('smartphone')
        
        # Software/editing detection
        software = str(exif_data.get('Software', '')).lower()
        if any(editor in software for editor in self.suspicious_software):
            analysis['is_edited'] = True
            analysis['content_hints'].append(f'edited_with_{software}')
        
        # GPS/Location data
        if any(key in exif_data for key in ['GPSLatitude', 'GPSLongitude', 'GPS']):
            analysis['has_location'] = True
        
        # Camera settings analysis
        aperture = exif_data.get('FNumber', exif_data.get('ApertureValue'))
        iso = exif_data.get('ISO', exif_data.get('ISOSpeedRatings'))
        focal_length = exif_data.get('FocalLength')
        
        # Wide aperture (shallow depth of field) might indicate portrait/intimate photography
        if aperture:
            try:
                f_value = float(str(aperture).replace('f/', '').split()[0])
                if f_value <= 2.8:
                    analysis['content_hints'].append('wide_aperture_portrait')
            except (ValueError, AttributeError):
                pass
        
        # High ISO might indicate low-light conditions
        if iso:
            try:
                iso_value = int(str(iso).split()[0])
                if iso_value > 1600:
                    analysis['content_hints'].append('high_iso_low_light')
            except (ValueError, AttributeError):
                pass
        
        return analysis
    
    def analyze_exif_content_keywords(self, exif_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze EXIF data for content-related keywords."""
        analysis = {
            'nsfw_indicators': [],
            'sfw_indicators': [],
            'keyword_score': 0.0
        }
        
        # Fields to search for keywords
        searchable_fields = [
            'ImageDescription', 'UserComment', 'Artist', 'Copyright',
            'Keywords', 'Subject', 'Title', 'Description', 'Comment',
            'XPComment', 'XPSubject', 'XPTitle', 'XPKeywords'
        ]
        
        # Combine all text from searchable fields
        combined_text = ''
        for field in searchable_fields:
            if field in exif_data:
                value = str(exif_data[field]).lower()
                combined_text += f' {value}'
        
        # Check for NSFW keywords
        for keyword in self.nsfw_exif_keywords:
            if keyword in combined_text:
                analysis['nsfw_indicators'].append(keyword)
                analysis['keyword_score'] += 0.3
        
        # Check for SFW keywords
        for keyword in self.sfw_exif_keywords:
            if keyword in combined_text:
                analysis['sfw_indicators'].append(keyword)
                analysis['keyword_score'] -= 0.2  # Negative score for SFW
        
        return analysis
    
    def analyze_timestamp_patterns(self, exif_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze timestamp patterns for suspicious activity."""
        analysis = {
            'creation_time': None,
            'modification_time': None,
            'is_batch_processed': False,
            'unusual_timing': False
        }
        
        # Extract timestamps
        timestamp_fields = [
            'CreateDate', 'DateTimeOriginal', 'ModifyDate',
            'DateTime', 'DateTimeDigitized'
        ]
        
        timestamps = []
        for field in timestamp_fields:
            if field in exif_data:
                try:
                    # Try to parse timestamp
                    timestamp_str = str(exif_data[field])
                    # Handle different timestamp formats
                    for fmt in ['%Y:%m:%d %H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                        try:
                            timestamp = datetime.strptime(timestamp_str, fmt)
                            timestamps.append(timestamp)
                            break
                        except ValueError:
                            continue
                except:
                    pass
        
        if timestamps:
            analysis['creation_time'] = min(timestamps)
            analysis['modification_time'] = max(timestamps)
            
            # Check for unusual timing (late night/early morning)
            if analysis['creation_time']:
                hour = analysis['creation_time'].hour
                if hour >= 23 or hour <= 5:  # 11 PM to 5 AM
                    analysis['unusual_timing'] = True
        
        return analysis
    
    def calculate_exif_suspicion_score(self, file_path: Path) -> Dict[str, Any]:
        """Calculate comprehensive suspicion score based on EXIF analysis."""
        result = {
            'exif_score': 0.0,
            'confidence': 0.0,
            'analysis_details': {},
            'has_exif': False,
            'analysis_methods': []
        }
        
        # Try ExifTool first (more comprehensive)
        exif_data = {}
        if self.has_exiftool:
            exif_data = self.extract_exif_with_exiftool(file_path)
            if exif_data:
                result['analysis_methods'].append('exiftool')
        
        # Fallback to Pillow if ExifTool failed or unavailable
        if not exif_data and self.has_pillow:
            exif_data = self.extract_exif_with_pillow(file_path)
            if exif_data:
                result['analysis_methods'].append('pillow')
        
        if not exif_data:
            result['analysis_details']['error'] = 'No EXIF data available'
            return result
        
        result['has_exif'] = True
        
        # Analyze different aspects
        camera_analysis = self.analyze_camera_settings(exif_data)
        keyword_analysis = self.analyze_exif_content_keywords(exif_data)
        timestamp_analysis = self.analyze_timestamp_patterns(exif_data)
        
        result['analysis_details'] = {
            'camera': camera_analysis,
            'keywords': keyword_analysis,
            'timestamps': timestamp_analysis,
            'raw_exif_count': len(exif_data)
        }
        
        # Calculate combined score
        score = 0.0
        confidence = 0.3  # Base confidence for having EXIF data
        
        # Camera settings contribution
        if camera_analysis['is_edited']:
            score += 0.1
            confidence += 0.1
        
        if camera_analysis['is_smartphone'] and not camera_analysis['has_location']:
            score += 0.05  # Smartphone without location might be more suspicious
        
        if 'wide_aperture_portrait' in camera_analysis['content_hints']:
            score += 0.1
        
        if 'high_iso_low_light' in camera_analysis['content_hints']:
            score += 0.05
        
        # Keyword analysis contribution
        score += keyword_analysis['keyword_score']
        if keyword_analysis['nsfw_indicators']:
            confidence += 0.3
        if keyword_analysis['sfw_indicators']:
            confidence += 0.2
        
        # Timestamp analysis contribution
        if timestamp_analysis['unusual_timing']:
            score += 0.05
        
        # Normalize score and confidence
        result['exif_score'] = max(0.0, min(1.0, score))
        result['confidence'] = max(0.0, min(1.0, confidence))
        
        return result
    
    def get_exif_summary(self, file_path: Path) -> Dict[str, Any]:
        """Get a summary of EXIF data for display purposes."""
        if not self.has_exiftool and not self.has_pillow:
            return {'error': 'No EXIF extraction tools available'}
        
        exif_data = {}
        if self.has_exiftool:
            exif_data = self.extract_exif_with_exiftool(file_path)
        elif self.has_pillow:
            exif_data = self.extract_exif_with_pillow(file_path)
        
        if not exif_data:
            return {'error': 'No EXIF data found'}
        
        # Extract key information for summary
        summary = {
            'camera_make': exif_data.get('Make', 'Unknown'),
            'camera_model': exif_data.get('Model', 'Unknown'),
            'software': exif_data.get('Software', 'Unknown'),
            'date_taken': exif_data.get('DateTimeOriginal', exif_data.get('CreateDate', 'Unknown')),
            'image_size': f"{exif_data.get('ImageWidth', '?')}x{exif_data.get('ImageHeight', '?')}",
            'has_gps': any(key.startswith('GPS') for key in exif_data.keys()),
            'total_fields': len(exif_data)
        }
        
        return summary
