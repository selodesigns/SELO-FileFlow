"""
File handler for the FileFlow application.
Responsible for processing files and organizing them based on their types.
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union, Literal

logger = logging.getLogger(__name__)

# Define common type aliases
PathLike = Union[str, Path]
FileCategory = Literal['images', 'documents', 'videos', 'software', 'other', 'archives', 'music', 'custom']

class FileHandler:
    """Handles file operations for organizing downloads."""
    
    def __init__(self, config: Dict) -> None:
        """
        Initialize the file handler.
        
        Args:
            config: The application configuration dictionary containing source and destination directories.
        """
        self.config = config
        
        # Handle source directory/directories using pattern matching (Python 3.10+)
        source_dir_config = config['source_directory']
        match source_dir_config:
            case list():
                # Multiple source directories
                self.source_dirs: List[Path] = [
                    Path(directory).expanduser().resolve()
                    for directory in source_dir_config
                ]
            case str():
                # Single source directory (string)
                self.source_dirs = [Path(source_dir_config).expanduser().resolve()]
            case _:
                # Fallback for unexpected types
                logger.warning(f"Unexpected source_directory type: {type(source_dir_config)}, using default")
                self.source_dirs = [Path.home() / 'Downloads']
        
        # For backwards compatibility, keep a reference to the first source directory
        self.source_dir: Path = self.source_dirs[0] if self.source_dirs else Path.home() / 'Downloads'
        
        self.destination_dirs: Dict[str, Path] = {
            category: Path(directory).expanduser().resolve()
            for category, directory in config['destination_directories'].items()
        }
        self.file_types: Dict[str, List[str]] = config['file_types']
        self.move_files: bool = config.get('move_files', True)
    
    def get_file_category(self, file_path: PathLike) -> Union[FileCategory, str]:
        """
        Determine the category of a file based on its extension.
        
        Args:
            file_path: Path to the file to categorize.
            
        Returns:
            The category of the file or custom mapping name if found in custom mappings.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        file_extension = file_path.suffix.lower()
        
        # Check custom mappings first if enabled
        if self.config.get('use_custom_mappings_first', True):
            custom_mappings = self.config.get('custom_mappings', [])
            for mapping in custom_mappings:
                if file_extension in mapping.get('extensions', []):
                    return mapping.get('name', 'custom')  # Return the custom mapping name
        
        # Then check standard categories
        for category, extensions in self.file_types.items():
            if file_extension in extensions:
                return category  # type: ignore # We ensure these match the FileCategory type
        
        # If use_custom_mappings_first is False, check custom mappings after standard categories
        if not self.config.get('use_custom_mappings_first', True):
            custom_mappings = self.config.get('custom_mappings', [])
            for mapping in custom_mappings:
                if file_extension in mapping.get('extensions', []):
                    return mapping.get('name', 'custom')  # Return the custom mapping name
        
        return 'other'  # Default category
    
    def get_destination_path(self, file_path: PathLike, category: Union[FileCategory, str]) -> Path:
        """
        Get the destination path for a file.
        
        Args:
            file_path: Path to the file.
            category: The category of the file or custom mapping name.
            
        Returns:
            The destination path for the file, with uniqueness handling.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        # First check if this is a custom mapping category
        custom_mappings = self.config.get('custom_mappings', [])
        for mapping in custom_mappings:
            if mapping.get('name') == category:
                dest_dir = Path(mapping.get('destination')).expanduser().resolve()
                dest_dir.mkdir(parents=True, exist_ok=True)
                break
        else:  # No matching custom mapping found
            # Use pattern matching to handle destination directory selection
            match self.destination_dirs.get(category):
                case dest_dir if dest_dir is not None:
                    # Category exists in destination directories
                    pass
                case _:
                    # Fallback to 'other' category
                    dest_dir = self.destination_dirs.get('other', self.source_dir.parent / 'Organized')
                    # Create the fallback directory if needed
                    dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if file with same name already exists
        dest_path = dest_dir / file_path.name
        if dest_path.exists():
            # Add timestamp to filename to make it unique
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            dest_path = dest_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        
        return dest_path
    
    def process_file(self, file_path: PathLike) -> bool:
        """
        Process a file and move/copy it to the appropriate directory.
        
        Args:
            file_path: Path to the file to process.
            
        Returns:
            True if the file was processed successfully, False otherwise.
        """
        try:
            file_path = Path(file_path).resolve()
            
            # Skip directories and non-existent files
            if not file_path.is_file():
                return False
            
            # Skip files that are not in any of the source directories
            # Using any() for more concise Python code
            file_in_source_dir = any(
                source_dir in file_path.parents or source_dir == file_path.parent
                for source_dir in self.source_dirs
            )
            
            if not file_in_source_dir:
                logger.debug(f"Skipping file outside source directories: {file_path}")
                return False
            
            # Get file category
            category = self.get_file_category(file_path)
            
            # Get destination path
            dest_path = self.get_destination_path(file_path, category)
            
            # Create destination directory if it doesn't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use pattern matching to handle file operations (Python 3.10+)
            match self.move_files:
                case True:
                    # Move the file
                    shutil.move(str(file_path), str(dest_path))
                    action = "Moved"
                case False:
                    # Copy the file
                    shutil.copy2(str(file_path), str(dest_path))
                    action = "Copied"
            
            logger.info(f"{action} '{file_path.name}' to {category} folder: {dest_path}")
            return True
            
        # Use except* for grouping related exceptions (Python 3.11+)
        except (PermissionError, FileNotFoundError) as e:
            # File might be in use or locked
            logger.warning(f"Could not process file '{file_path}': {e}")
            return False
        except OSError as e:
            # Handle specific OS errors
            logger.warning(f"OS error processing file '{file_path}': {e}")
            return False
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Error processing file '{file_path}': {e}")
            return False
    
    def process_directory(self, directory_path: PathLike, recursive: bool = False) -> int:
        """
        Process all files in a directory.
        
        Args:
            directory_path: Path to the directory to process.
            recursive: Whether to process subdirectories recursively.
            
        Returns:
            Number of files processed successfully.
        """
        try:
            directory_path = Path(directory_path).resolve()
            
            if not directory_path.is_dir():
                logger.error(f"Not a directory: {directory_path}")
                return 0
            
            processed_count = 0
            
            # Process files in directory using more efficient pattern matching
            for item_path in directory_path.iterdir():
                match item_path, recursive:
                    case path, _ if path.is_file():
                        # Process file
                        if self.process_file(path):
                            processed_count += 1
                    case path, True if path.is_dir():
                        # Process subdirectory recursively
                        processed_count += self.process_directory(path, recursive=True)
                    case _:
                        # Skip other items (symlinks, etc.) or non-recursive directories
                        pass
            
            return processed_count
        
        except PermissionError as e:
            logger.error(f"Permission denied accessing directory '{directory_path}': {e}")
            return 0
        except OSError as e:
            logger.error(f"OS error processing directory '{directory_path}': {e}")
            return 0
        except Exception as e:
            logger.error(f"Error processing directory '{directory_path}': {e}")
            return 0
