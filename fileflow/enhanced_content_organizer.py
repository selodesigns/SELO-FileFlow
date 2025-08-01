import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .config import load_config, save_config
from .content_classifier import ContentClassifier
from .robust_content_classifier import RobustContentClassifier
from .ui.notifications import send_notification
from .utils.logging import get_logger

logger = get_logger()

class EnhancedContentOrganizer:
    """Enhanced organizer that uses both filename and visual content analysis for NSFW/SFW classification."""
    
    def __init__(self):
        self.filename_classifier = ContentClassifier()
        self.visual_classifier = RobustContentClassifier()
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
            
            # Add enhanced content classification settings
            config['content_classification'] = {
                'enabled': True,
                'use_visual_analysis': True,
                'use_filename_analysis': True,
                'visual_analysis_threshold': 0.6,
                'filename_overrides_visual': False,  # Visual analysis takes precedence
                'classify_media_only': True,
                'create_content_subdirs': True,
                'notify_nsfw_moves': False,  # Privacy consideration
                'cache_analysis_results': True
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
    
    def classify_file_content(self, file_path: Path, config: Dict) -> Dict:
        """Classify file content using both filename and visual analysis."""
        classification_config = config.get('content_classification', {})
        
        result = {
            'is_nsfw': False,
            'confidence': 0.0,
            'method': 'none',
            'filename_analysis': None,
            'visual_analysis': None,
            'final_decision_reason': ''
        }
        
        use_filename = classification_config.get('use_filename_analysis', True)
        use_visual = classification_config.get('use_visual_analysis', True)
        visual_threshold = classification_config.get('visual_analysis_threshold', 0.6)
        filename_overrides = classification_config.get('filename_overrides_visual', False)
        
        # Filename analysis
        if use_filename:
            filename_result = self.filename_classifier.analyze_file_path(file_path)
            result['filename_analysis'] = filename_result
            
            if filename_result['is_nsfw']:
                result['is_nsfw'] = True
                result['confidence'] = 0.8  # High confidence for explicit filenames
                result['method'] = 'filename'
                result['final_decision_reason'] = f"Filename indicates NSFW: {filename_result['reason']}"
                
                # If filename analysis is definitive and overrides visual, return early
                if filename_overrides or not use_visual:
                    return result
        
        # Visual content analysis (for supported media files)
        if use_visual and self.visual_classifier.should_classify_file(file_path):
            try:
                logger.info(f"Performing visual analysis on {file_path.name}...")
                visual_result = self.visual_classifier.classify_media_file(file_path)
                result['visual_analysis'] = visual_result
                
                if 'error' not in visual_result:
                    visual_nsfw = visual_result.get('is_nsfw', False)
                    visual_confidence = visual_result.get('confidence', 0.0)
                    visual_score = visual_result.get('nsfw_score', 0.0)
                    
                    # Combine filename and visual analysis
                    if result['is_nsfw'] and visual_nsfw:
                        # Both methods agree on NSFW
                        result['confidence'] = min(result['confidence'] + visual_confidence * 0.5, 1.0)
                        result['method'] = 'filename+visual'
                        result['final_decision_reason'] = f"Both filename and visual analysis indicate NSFW (visual score: {visual_score:.2f})"
                    
                    elif not result['is_nsfw'] and visual_nsfw and visual_score > visual_threshold:
                        # Visual analysis overrides filename analysis
                        result['is_nsfw'] = True
                        result['confidence'] = visual_confidence
                        result['method'] = 'visual'
                        result['final_decision_reason'] = f"Visual analysis indicates NSFW (score: {visual_score:.2f}, skin: {visual_result.get('skin_percentage', 0):.1f}%)"
                    
                    elif result['is_nsfw'] and not visual_nsfw:
                        # Filename says NSFW but visual says SFW - use visual with lower confidence
                        if visual_confidence > 0.7:  # High confidence visual analysis
                            result['is_nsfw'] = False
                            result['confidence'] = visual_confidence * 0.8
                            result['method'] = 'visual_override'
                            result['final_decision_reason'] = f"Visual analysis overrides filename (visual score: {visual_score:.2f})"
                        else:
                            # Keep filename result but lower confidence
                            result['confidence'] *= 0.7
                            result['method'] = 'filename_uncertain'
                            result['final_decision_reason'] += f" (visual analysis uncertain: {visual_score:.2f})"
                    
                    else:
                        # Both agree on SFW or visual analysis used alone
                        if not result['is_nsfw']:
                            result['confidence'] = max(result['confidence'], visual_confidence * 0.8)
                            result['method'] = 'visual' if result['method'] == 'none' else 'filename+visual'
                            if result['method'] == 'visual':
                                result['final_decision_reason'] = f"Visual analysis indicates SFW (score: {visual_score:.2f})"
                            else:
                                result['final_decision_reason'] += f" (confirmed by visual analysis: {visual_score:.2f})"
                
                else:
                    logger.warning(f"Visual analysis failed for {file_path.name}: {visual_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Visual analysis error for {file_path.name}: {e}")
        
        # Default to SFW if no analysis was performed
        if result['method'] == 'none':
            result['final_decision_reason'] = "No NSFW indicators found"
        
        return result
    
    def get_destination_path(self, file_path: Path, config: Dict) -> Tuple[Path, Dict]:
        """Get the destination path for a file based on content and category."""
        filename = file_path.name
        
        # Get basic file category
        category = self.get_category_for_file(filename, config['file_types'])
        
        # Check if content classification is enabled
        if not config.get('content_classification', {}).get('enabled', True):
            # Use original logic
            dest_dir = config['destination_directories'].get(category, config['destination_directories']['other'])
            return Path(dest_dir).expanduser(), {'is_nsfw': False, 'method': 'disabled'}
        
        # Determine if file should be content-classified
        should_classify = (
            config.get('content_classification', {}).get('classify_media_only', True) and
            (self.filename_classifier.should_classify_file(file_path) or 
             self.visual_classifier.should_classify_file(file_path))
        ) or not config.get('content_classification', {}).get('classify_media_only', True)
        
        if should_classify:
            # Classify content using enhanced analysis
            classification_result = self.classify_file_content(file_path, config)
            content_type = 'nsfw' if classification_result['is_nsfw'] else 'sfw'
            
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
            classification_result = {'is_nsfw': False, 'method': 'not_classified'}
        
        return Path(dest_dir).expanduser(), classification_result
    
    def organize_files(self):
        """Organize files with enhanced content-based separation."""
        import sys
        config = self.get_enhanced_config()
        src_dirs = config['source_directories']
        notify = config.get('notify_on_move', True)
        notify_nsfw = config.get('content_classification', {}).get('notify_nsfw_moves', False)
        
        moved_files = {'sfw': 0, 'nsfw': 0, 'other': 0}
        analysis_stats = {'filename_only': 0, 'visual_only': 0, 'filename+visual': 0, 'visual_override': 0}
        
        is_cli = hasattr(sys, 'ps1') is False and sys.stdout.isatty()
        if is_cli:
            print("[FileFlow] Starting organization job...")
        for src_dir in src_dirs:
            src_path = Path(src_dir).expanduser()
            if not src_path.exists():
                logger.error(f"Source directory does not exist: {src_path}")
                if is_cli:
                    print(f"[FileFlow] Source directory does not exist: {src_path}")
                continue
            logger.info(f"Organizing files in: {src_path}")
            if is_cli:
                print(f"[FileFlow] Organizing files in: {src_path}")
            for item in src_path.rglob('*'):
                if item.is_file():
                    try:
                        dest_dir, classification = self.get_destination_path(item, config)
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
                        shutil.move(str(item), str(dest_file))
                        if classification['is_nsfw']:
                            logger.info(f"NSFW: {item.name} -> {dest_file} ({classification['method']}: {classification.get('final_decision_reason', 'N/A')})")
                            moved_files['nsfw'] += 1
                        else:
                            logger.info(f"SFW: {item.name} -> {dest_file}")
                            moved_files['sfw'] += 1
                        # Update analysis statistics
                        method = classification.get('method', 'other')
                        if method in analysis_stats:
                            analysis_stats[method] += 1
                        # CLI feedback
                        if is_cli:
                            print(f"[FileFlow] Moved {item} to {dest_file}")
                        # Send notification (respecting privacy settings)
                        if notify and (not classification['is_nsfw'] or notify_nsfw):
                            content_label = 'NSFW' if classification['is_nsfw'] else 'SFW'
                            confidence = classification.get('confidence', 0)
                            send_notification(
                                f"FileFlow: {content_label} File Moved",
                                f"{item.name} → {dest_dir.name} (confidence: {confidence:.1f})"
                            )
                    except Exception as e:
                        logger.error(f"Failed to move {item}: {e}")
                        moved_files['other'] += 1
                        if is_cli:
                            print(f"[FileFlow] Failed to move {item}: {e}")
        
        # Log summary
        total_moved = sum(moved_files.values())
        if total_moved > 0:
            logger.info(f"Organization complete! Moved {total_moved} files:")
            logger.info(f"  - SFW: {moved_files['sfw']}")
            logger.info(f"  - NSFW: {moved_files['nsfw']}")
            logger.info(f"  - Other/Failed: {moved_files['other']}")
            logger.info(f"Analysis methods used:")
            for method, count in analysis_stats.items():
                if count > 0:
                    logger.info(f"  - {method}: {count}")
            
            # Send summary notification
            if notify:
                send_notification(
                    "FileFlow: Enhanced Organization Complete",
                    f"Organized {total_moved} files with visual content analysis (SFW: {moved_files['sfw']}, NSFW: {moved_files['nsfw']})"
                )
    
    def reorganize_existing_files(self, target_dirs: List[str] = None):
        """Reorganize existing files using enhanced content classification."""
        config = self.get_enhanced_config()
        
        if target_dirs is None:
            # Use destination directories as sources for reorganization
            target_dirs = list(config['destination_directories'].values())
        
        logger.info("Starting enhanced reorganization with visual content analysis...")
        
        reorganized_files = {'sfw': 0, 'nsfw': 0}
        analysis_stats = {'filename_only': 0, 'visual_only': 0, 'filename+visual': 0, 'visual_override': 0}
        
        for target_dir in target_dirs:
            target_path = Path(target_dir).expanduser()
            if not target_path.exists():
                continue
            
            logger.info(f"Reorganizing files in: {target_path}")
            
            # Get all media files in the directory
            media_files = []
            for item in target_path.rglob('*'):
                if item.is_file() and (
                    self.filename_classifier.should_classify_file(item) or 
                    self.visual_classifier.should_classify_file(item)
                ):
                    media_files.append(item)
            
            logger.info(f"Found {len(media_files)} media files to analyze")
            
            for i, item in enumerate(media_files, 1):
                try:
                    logger.info(f"Processing {i}/{len(media_files)}: {item.name}")
                    
                    # Skip if already in content-specific directory
                    if any(content_dir in str(item.parent).upper() for content_dir in ['SFW', 'NSFW']):
                        continue
                    
                    # Get new destination based on enhanced content analysis
                    dest_dir, classification = self.get_destination_path(item, config)
                    
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
                    
                    # Update statistics
                    content_type = 'nsfw' if classification['is_nsfw'] else 'sfw'
                    reorganized_files[content_type] += 1
                    
                    method = classification.get('method', 'other')
                    if method in analysis_stats:
                        analysis_stats[method] += 1
                    
                    # Log with classification details
                    confidence = classification.get('confidence', 0)
                    reason = classification.get('final_decision_reason', 'N/A')
                    logger.info(f"Reorganized {item.name} -> {dest_file} ({content_type.upper()}, {method}, confidence: {confidence:.2f}) - {reason}")
                    
                except Exception as e:
                    logger.error(f"Failed to reorganize {item}: {e}")
        
        # Log summary
        total_reorganized = sum(reorganized_files.values())
        if total_reorganized > 0:
            logger.info(f"Enhanced reorganization complete! Moved {total_reorganized} files:")
            logger.info(f"  - SFW: {reorganized_files['sfw']}")
            logger.info(f"  - NSFW: {reorganized_files['nsfw']}")
            logger.info(f"Analysis methods used:")
            for method, count in analysis_stats.items():
                if count > 0:
                    logger.info(f"  - {method}: {count}")
            
            # Send summary notification
            send_notification(
                "FileFlow: Enhanced Reorganization Complete",
                f"Reorganized {total_reorganized} files with visual analysis (SFW: {reorganized_files['sfw']}, NSFW: {reorganized_files['nsfw']})"
            )
        else:
            logger.info("No files needed reorganization.")


def organize_files(sources=None, dest=None):
    """Main organize function that uses enhanced content-based organization. CLI args can override config."""
    organizer = EnhancedContentOrganizer()
    if sources is not None or dest is not None:
        # Patch config for this run
        config = organizer.get_enhanced_config()
        if sources is not None:
            config['source_directories'] = sources
        if dest is not None:
            # Send all categories to this dest for this ad-hoc run
            config['destination_directories'] = {k: dest for k in config.get('destination_directories', {}).keys()}
        organizer.config = config
    organizer.organize_files()


def reorganize_existing_files(target_dirs: List[str] = None):
    """Reorganize existing files with enhanced content classification."""
    organizer = EnhancedContentOrganizer()
    organizer.reorganize_existing_files(target_dirs)
