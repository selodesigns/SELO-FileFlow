import shutil
from pathlib import Path
from typing import Dict, List
from .config import load_config, save_config
from .content_classifier import ContentClassifier
from .ui.notifications import send_notification
from .utils.logging import get_logger

logger = get_logger()

class ContentOrganizer:
    """Enhanced organizer that separates content by type (NSFW/SFW) and category."""
    
    def __init__(self):
        self.classifier = ContentClassifier()
        self.config = load_config()
    
    def get_enhanced_config(self) -> Dict:
        """Get or create enhanced configuration with content separation."""
        config = self.config.copy()
        
        # Add content-based destination directories if not present
        if 'content_destinations' not in config:
            home = Path.home()
            config['content_destinations'] = {
                'sfw': {
                    'images': str(home / 'Pictures' / 'SFW'),
                    'videos': str(home / 'Videos' / 'SFW'),
                    'documents': str(home / 'Documents' / 'SFW'),
                    'other': str(home / 'Downloads' / 'Other' / 'SFW')
                },
                'nsfw': {
                    'images': str(home / 'Pictures' / 'NSFW'),
                    'videos': str(home / 'Videos' / 'NSFW'),
                    'documents': str(home / 'Documents' / 'NSFW'),
                    'other': str(home / 'Downloads' / 'Other' / 'NSFW')
                }
            }
            
            # Add content classification settings
            config['content_classification'] = {
                'enabled': True,
                'classify_media_only': True,
                'create_content_subdirs': True,
                'notify_nsfw_moves': False  # Privacy consideration
            }
            
            # Save the enhanced config
            save_config(config)
            self.config = config
        
        return config
    
    def get_category_for_file(self, filename: str, file_types: Dict) -> str:
        """Get file category based on extension."""
        ext = Path(filename).suffix.lower()
        for category, extensions in file_types.items():
            if ext in extensions:
                return category
        return 'other'
    
    def get_destination_path(self, file_path: Path, config: Dict) -> Path:
        """Get the destination path for a file based on content and category."""
        filename = file_path.name
        
        # Get basic file category
        category = self.get_category_for_file(filename, config['file_types'])
        
        # Check if content classification is enabled
        if not config.get('content_classification', {}).get('enabled', True):
            # Use original logic
            dest_dir = config['destination_directories'].get(category, config['destination_directories']['other'])
            return Path(dest_dir).expanduser()
        
        # Determine if file should be content-classified
        should_classify = (
            config.get('content_classification', {}).get('classify_media_only', True) and
            self.classifier.should_classify_file(file_path)
        ) or not config.get('content_classification', {}).get('classify_media_only', True)
        
        if should_classify:
            # Classify content
            content_type = self.classifier.classify_media_file(file_path)
            
            # Get content-specific destination
            content_destinations = config.get('content_destinations', {})
            if content_type in content_destinations and category in content_destinations[content_type]:
                dest_dir = content_destinations[content_type][category]
            else:
                # Fallback to regular destinations with content subdirectory
                base_dest = config['destination_directories'].get(category, config['destination_directories']['other'])
                dest_dir = str(Path(base_dest) / content_type.upper())
        else:
            # Use original destination for non-media files
            dest_dir = config['destination_directories'].get(category, config['destination_directories']['other'])
        
        return Path(dest_dir).expanduser()
    
    def organize_files(self):
        """Organize files with content-based separation."""
        config = self.get_enhanced_config()
        src_dirs = config['source_directories']
        notify = config.get('notify_on_move', True)
        notify_nsfw = config.get('content_classification', {}).get('notify_nsfw_moves', False)
        
        moved_files = {'sfw': 0, 'nsfw': 0, 'other': 0}
        
        for src_dir in src_dirs:
            src_path = Path(src_dir).expanduser()
            if not src_path.exists():
                logger.error(f"Source directory does not exist: {src_path}")
                continue
            
            logger.info(f"Organizing files in: {src_path}")
            
            for item in src_path.iterdir():
                if item.is_file():
                    try:
                        # Get destination path
                        dest_dir = self.get_destination_path(item, config)
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        dest_file = dest_dir / item.name
                        
                        # Handle file name conflicts
                        counter = 1
                        original_dest = dest_file
                        while dest_file.exists():
                            stem = original_dest.stem
                            suffix = original_dest.suffix
                            dest_file = dest_dir / f"{stem}_{counter}{suffix}"
                            counter += 1
                        
                        # Move the file
                        shutil.move(str(item), str(dest_file))
                        logger.info(f"Moved {item.name} -> {dest_file}")
                        
                        # Determine content type for statistics
                        if self.classifier.should_classify_file(item):
                            content_type = self.classifier.classify_media_file(item)
                            moved_files[content_type] += 1
                            
                            # Send notification (respecting privacy settings)
                            if notify and (content_type != 'nsfw' or notify_nsfw):
                                content_label = content_type.upper()
                                send_notification(
                                    f"FileFlow: {content_label} File Moved",
                                    f"{item.name} → {dest_dir.name}"
                                )
                        else:
                            moved_files['other'] += 1
                            if notify:
                                send_notification("FileFlow: File Moved", f"{item.name} → {dest_dir.name}")
                        
                    except Exception as e:
                        logger.error(f"Failed to move {item}: {e}")
        
        # Log summary
        total_moved = sum(moved_files.values())
        if total_moved > 0:
            logger.info(f"Organization complete! Moved {total_moved} files:")
            logger.info(f"  - SFW: {moved_files['sfw']}")
            logger.info(f"  - NSFW: {moved_files['nsfw']}")
            logger.info(f"  - Other: {moved_files['other']}")
            
            # Send summary notification
            if notify:
                send_notification(
                    "FileFlow: Organization Complete",
                    f"Organized {total_moved} files (SFW: {moved_files['sfw']}, NSFW: {moved_files['nsfw']}, Other: {moved_files['other']})"
                )
    
    def reorganize_existing_files(self, target_dirs: List[str] = None):
        """Reorganize existing files that were previously organized without content classification."""
        config = self.get_enhanced_config()
        
        if target_dirs is None:
            # Use destination directories as sources for reorganization
            target_dirs = list(config['destination_directories'].values())
        
        logger.info("Starting reorganization of existing files with content classification...")
        
        reorganized_files = {'sfw': 0, 'nsfw': 0}
        
        for target_dir in target_dirs:
            target_path = Path(target_dir).expanduser()
            if not target_path.exists():
                continue
            
            logger.info(f"Reorganizing files in: {target_path}")
            
            # Get all media files in the directory
            media_files = []
            for item in target_path.rglob('*'):
                if item.is_file() and self.classifier.should_classify_file(item):
                    media_files.append(item)
            
            for item in media_files:
                try:
                    # Skip if already in content-specific directory
                    if any(content_dir in str(item.parent).upper() for content_dir in ['SFW', 'NSFW']):
                        continue
                    
                    # Get new destination based on content
                    dest_dir = self.get_destination_path(item, config)
                    
                    # Skip if file is already in the correct location
                    if item.parent == dest_dir:
                        continue
                    
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    dest_file = dest_dir / item.name
                    
                    # Handle file name conflicts
                    counter = 1
                    original_dest = dest_file
                    while dest_file.exists():
                        stem = original_dest.stem
                        suffix = original_dest.suffix
                        dest_file = dest_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    # Move the file
                    shutil.move(str(item), str(dest_file))
                    
                    # Determine content type for statistics
                    content_type = self.classifier.classify_media_file(item)
                    reorganized_files[content_type] += 1
                    
                    logger.info(f"Reorganized {item.name} -> {dest_file} ({content_type.upper()})")
                    
                except Exception as e:
                    logger.error(f"Failed to reorganize {item}: {e}")
        
        # Log summary
        total_reorganized = sum(reorganized_files.values())
        if total_reorganized > 0:
            logger.info(f"Reorganization complete! Moved {total_reorganized} files:")
            logger.info(f"  - SFW: {reorganized_files['sfw']}")
            logger.info(f"  - NSFW: {reorganized_files['nsfw']}")
            
            # Send summary notification
            send_notification(
                "FileFlow: Reorganization Complete",
                f"Reorganized {total_reorganized} files (SFW: {reorganized_files['sfw']}, NSFW: {reorganized_files['nsfw']})"
            )
        else:
            logger.info("No files needed reorganization.")


def organize_files():
    """Main organize function that uses content-based organization."""
    organizer = ContentOrganizer()
    organizer.organize_files()


def reorganize_existing_files(target_dirs: List[str] = None):
    """Reorganize existing files with content classification."""
    organizer = ContentOrganizer()
    organizer.reorganize_existing_files(target_dirs)
