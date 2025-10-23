import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from .utils.logging import get_logger

logger = get_logger()

class ContentClassifier:
    """Classifies media content as NSFW or SFW based on filename patterns and metadata."""
    
    def __init__(self):
        # Common NSFW keywords and patterns
        self.nsfw_keywords = {
            'explicit': ['porn', 'xxx', 'sex', 'nude', 'naked', 'nsfw', 'adult', 'erotic'],
            'body_parts': ['boobs', 'tits', 'ass', 'dick', 'cock', 'pussy', 'vagina', 'penis'],
            'actions': ['fuck', 'fucking', 'cumshot', 'cum', 'orgasm', 'masturbat', 'blowjob'],
            'sites': ['pornhub', 'xvideos', 'xhamster', 'redtube', 'youporn', 'onlyfans'],
            'categories': ['milf', 'teen', 'bdsm', 'fetish', 'anal', 'oral', 'lesbian', 'gay']
        }
        
        # Patterns that might indicate NSFW content
        self.nsfw_patterns = [
            r'\b(18\+|21\+)\b',  # Age restrictions
            r'\b(r18|r21)\b',    # Rating patterns
            r'\b(hentai|doujin)\b',  # Anime adult content
            r'\b(cam|webcam).*\b(girl|boy|show)\b',  # Cam content
            r'\b(strip|stripper|escort)\b',  # Adult services
            r'\b(playboy|penthouse)\b',  # Adult magazines
        ]
        
        # SFW indicators (these override NSFW detection for ambiguous cases)
        self.sfw_indicators = [
            'family', 'kids', 'children', 'baby', 'wedding', 'graduation',
            'vacation', 'travel', 'nature', 'landscape', 'food', 'recipe',
            'tutorial', 'education', 'work', 'business', 'meeting'
        ]
    
    def is_nsfw_filename(self, filename: str) -> Tuple[bool, str]:
        """
        Analyze filename for NSFW content indicators.
        Returns (is_nsfw, reason)
        """
        filename_lower = filename.lower()
        
        # Check for SFW indicators first (they take precedence)
        for indicator in self.sfw_indicators:
            if indicator in filename_lower:
                return False, f"SFW indicator: {indicator}"
        
        # Check explicit keywords
        for category, keywords in self.nsfw_keywords.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    return True, f"NSFW keyword ({category}): {keyword}"
        
        # Check regex patterns
        for pattern in self.nsfw_patterns:
            if re.search(pattern, filename_lower, re.IGNORECASE):
                return True, f"NSFW pattern: {pattern}"
        
        return False, "No NSFW indicators found"
    
    def analyze_file_path(self, file_path: Path) -> Dict[str, any]:
        """
        Analyze a file's path and name for content classification.
        Returns classification details.
        """
        filename = file_path.name
        parent_dirs = [p.name.lower() for p in file_path.parents if p.name]
        
        # Check filename
        is_nsfw, reason = self.is_nsfw_filename(filename)
        
        # Check parent directory names for additional context
        dir_nsfw = False
        dir_reason = ""
        for dir_name in parent_dirs[:3]:  # Check up to 3 parent directories
            dir_is_nsfw, dir_check_reason = self.is_nsfw_filename(dir_name)
            if dir_is_nsfw:
                dir_nsfw = True
                dir_reason = f"Directory '{dir_name}': {dir_check_reason}"
                break
        
        # Final classification
        final_nsfw = is_nsfw or dir_nsfw
        final_reason = reason if is_nsfw else dir_reason
        
        return {
            'is_nsfw': final_nsfw,
            'reason': final_reason,
            'filename_check': (is_nsfw, reason),
            'directory_check': (dir_nsfw, dir_reason),
            'confidence': 'high' if final_nsfw else 'medium'
        }
    
    def classify_media_file(self, file_path: Path) -> str:
        """
        Classify a media file as 'nsfw' or 'sfw'.
        Returns the classification category.
        """
        analysis = self.analyze_file_path(file_path)
        
        if analysis['is_nsfw']:
            logger.info(f"Classified as NSFW: {file_path.name} - {analysis['reason']}")
            return 'nsfw'
        else:
            logger.debug(f"Classified as SFW: {file_path.name}")
            return 'sfw'
    
    def get_media_extensions(self) -> List[str]:
        """Get list of media file extensions that should be classified."""
        return [
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff',
            # Videos
            '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v',
            # Other media
            '.pdf'  # PDFs can contain adult content
        ]
    
    def should_classify_file(self, file_path: Path) -> bool:
        """Check if a file should be content-classified."""
        return file_path.suffix.lower() in self.get_media_extensions()
