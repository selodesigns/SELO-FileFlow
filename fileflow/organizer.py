# Legacy organizer - now imports from enhanced_content_organizer for visual analysis
from .enhanced_content_organizer import organize_files, reorganize_existing_files
from .utils.logging import get_logger

logger = get_logger()

# Re-export the main functions for backward compatibility
__all__ = ['organize_files', 'reorganize_existing_files']
