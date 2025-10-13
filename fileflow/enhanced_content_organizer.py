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
        """Get or create enhanced configuration with content separation, but never seed any destination directories by default."""
        config = self.config.copy()
        # Remove any logic that seeds home/XDG-based destinations
        if 'content_destinations' in config:
            # If present, leave as-is (user must have set it explicitly)
            return config
        # No content_destinations: abort unless user provided explicit destinations
        if not (config.get('user_destination') or config.get('dest')):
            raise RuntimeError("No destination directory specified. Please provide --dest on the CLI or set it in the config. FileFlow will not use any default or home/XDG-based destination.")
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
        """Get the destination path for a file based only on the user-supplied destination. Abort if unavailable or unwritable."""
        import os
        filename = file_path.name
        category = self.get_category_for_file(filename, config['file_types'])
        
        # Always use the user-supplied destination root
        user_dest = config.get('user_destination') or config.get('dest') or None
        if not user_dest:
            raise RuntimeError("No destination directory specified. Please provide --dest on the CLI or set it in the config.")
        dest_root = Path(user_dest).expanduser()
        if not dest_root.exists():
            raise RuntimeError(f"Destination directory does not exist: {dest_root}")
        if not os.access(dest_root, os.W_OK):
            raise RuntimeError(f"Destination directory is not writable: {dest_root}")

        # Determine subfolder by content type
        should_classify = (
            config.get('content_classification', {}).get('classify_media_only', True) and
            (self.filename_classifier.should_classify_file(file_path) or 
             self.visual_classifier.should_classify_file(file_path))
        ) or not config.get('content_classification', {}).get('classify_media_only', True)

        if should_classify:
            classification_result = self.classify_file_content(file_path, config)
            content_type = 'NSFW' if classification_result['is_nsfw'] else 'SFW'
            dest_dir = dest_root / content_type
        else:
            classification_result = {'is_nsfw': False, 'method': 'not_classified'}
            dest_dir = dest_root / 'Other'

        return dest_dir, classification_result


    def _process_item(self, item: Path, config: Dict, notify: bool, notify_nsfw: bool, analysis_stats: Dict = None, cli_feedback: bool = False):
        import os
        import sys
        dest_dir, classification = self.get_destination_path(item, config)
        if item.parent == dest_dir:
            return None
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / item.name
        counter = 1
        original_dest = dest_file
        while dest_file.exists():
            stem = original_dest.stem
            suffix = original_dest.suffix
            dest_file = dest_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        shutil.move(str(item), str(dest_file))
        content_key = 'nsfw' if classification.get('is_nsfw') else 'sfw'
        if classification.get('is_nsfw'):
            logger.info(f"NSFW: {item.name} -> {dest_file} ({classification.get('method')}: {classification.get('final_decision_reason', 'N/A')})")
        else:
            logger.info(f"SFW: {item.name} -> {dest_file}")
        if analysis_stats is not None:
            method = classification.get('method', 'other')
            if method in analysis_stats:
                analysis_stats[method] += 1
            else:
                analysis_stats['other'] = analysis_stats.get('other', 0) + 1
        if cli_feedback:
            method = classification.get('method', 'unknown')
            confidence = classification.get('confidence', 0)
            cat = 'NSFW' if classification.get('is_nsfw') else 'SFW'
            print(f"[FileFlow] Moved {item} to {dest_file} [{cat}, {method}, confidence: {confidence:.2f}]")
        if notify and not (os.environ.get('SSH_CONNECTION') or not sys.stdout.isatty()):
            if not classification.get('is_nsfw') or notify_nsfw:
                content_label = 'NSFW' if classification.get('is_nsfw') else 'SFW'
                confidence = classification.get('confidence', 0)
                try:
                    send_notification(
                        f"FileFlow: {content_label} File Moved",
                        f"{item.name} → {dest_dir.name} (confidence: {confidence:.1f})"
                    )
                except Exception:
                    pass
        return {'content_key': content_key, 'classification': classification, 'destination': dest_file}


    def organize_path(self, file_path: Path, config: Dict = None):
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Source file does not exist: {path}")
        active_config = config or self.get_enhanced_config()
        notify = active_config.get('notify_on_move', True)
        notify_nsfw = active_config.get('content_classification', {}).get('notify_nsfw_moves', False)
        result = self._process_item(path, active_config, notify, notify_nsfw)
        if result is None:
            return {'content_key': 'other', 'classification': {}, 'destination': path}
        return result


    def organize_files(self):
        """Organize files with enhanced content-based separation."""
        import sys
        config = self.get_enhanced_config()
        src_dirs = config['source_directories']
        notify = config.get('notify_on_move', True)
        notify_nsfw = config.get('content_classification', {}).get('notify_nsfw_moves', False)
        
        moved_files = {'sfw': 0, 'nsfw': 0, 'other': 0}
        analysis_stats = {'filename_only': 0, 'visual_only': 0, 'filename+visual': 0, 'visual_override': 0, 'other': 0}
        
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
                    # System/protected file exclusion
                    if (
                        item.name.startswith('.') or
                        item.is_symlink() or
                        not item.resolve().is_file() or
                        item.is_socket() if hasattr(item, 'is_socket') else False or
                        item.is_fifo() if hasattr(item, 'is_fifo') else False or
                        not str(item.resolve()).startswith(str(src_path.resolve()))
                    ):
                        if is_cli:
                            print(f"[FileFlow] Skipped protected/system file: {item}")
                        continue
                    try:
                        processed = self._process_item(item, config, notify, notify_nsfw, analysis_stats, is_cli)
                        if processed:
                            moved_files[processed['content_key']] += 1
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
            logger.info(f"  - Other: {moved_files['other']}")
            if is_cli:
                print(f"[FileFlow] Organization complete! Moved {total_moved} files:")
                print(f"[FileFlow]   - SFW: {moved_files['sfw']}")
                print(f"[FileFlow]   - NSFW: {moved_files['nsfw']}")
                print(f"[FileFlow]   - Other: {moved_files['other']}")
                print("[FileFlow] Classification method summary:")
                print("[FileFlow]   - filename_only:    {}".format(analysis_stats['filename_only']))
                print("[FileFlow]   - visual_only:      {}".format(analysis_stats['visual_only']))
                print("[FileFlow]   - filename+visual:  {}".format(analysis_stats['filename+visual']))
                print("[FileFlow]   - visual_override:  {}".format(analysis_stats['visual_override']))
                print("[FileFlow]   - other:            {}".format(analysis_stats.get('other', 0)))
            # Completely disable notifications in CLI mode
            # Only send notifications if running in GUI/desktop (not CLI/SSH)
            # (No-op in CLI)
            pass
        else:
            if is_cli:
                print("[FileFlow] No files needed organization.")
    
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
        config = organizer.get_enhanced_config() if organizer.config else {}
        if sources is not None:
            config['source_directories'] = sources
        if dest is not None:
            # Set both destination_directories and dest for compatibility with all checks
            config['destination_directories'] = {k: dest for k in config.get('destination_directories', {}).keys()}
            config['dest'] = dest
        organizer.config = config
    organizer.organize_files()



def reorganize_existing_files(target_dirs: List[str] = None, dest: str = None):
    """Reorganize existing files with enhanced content classification. CLI can override destination."""
    organizer = EnhancedContentOrganizer()
    if dest is not None:
        config = organizer.get_enhanced_config() if organizer.config else {}
        config['dest'] = dest
        organizer.config = config
    organizer.reorganize_existing_files(target_dirs)

