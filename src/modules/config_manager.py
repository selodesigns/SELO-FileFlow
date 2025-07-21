"""
Configuration manager for the FileFlow application.
Handles loading and validation of configuration settings.
"""

import os
import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, Any

from src.modules.user_dirs import user_dirs

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'source_directory': str(Path.home() / 'Downloads'),  # Can be a string or list of strings
    'destination_directories': {
        'images': str(Path.home() / 'Pictures' / 'Downloaded'),
        'documents': str(Path.home() / 'Documents' / 'Downloaded'),
        'videos': str(Path.home() / 'Videos' / 'Downloaded'),
        'software': str(Path.home() / 'Downloads' / 'Software'),
        'other': str(Path.home() / 'Downloads' / 'Other')
    },
    'file_types': {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico', '.heic'],
        'documents': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.odt', '.ods', '.odp', '.csv', '.epub', '.mobi'],
        'videos': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp'],
        'software': ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm', '.appimage', '.apk', '.zip', '.rar', '.7z', '.tar', '.gz', '.iso']
    },
    'custom_mappings': [
        # Example format:
        # {
        #     'extensions': ['.mp3', '.wav', '.flac'],
        #     'destination': str(Path.home() / 'Music' / 'Downloaded'),
        #     'name': 'Music Files'
        # }
    ],
    'logging': {
        'level': 'INFO',
        'file': 'logs/fileflow.log'
    },
    'move_files': True,  # If False, files will be copied instead of moved
    'organize_existing_files': True,  # Process files that already exist in the source directory
    'notify_on_move': True,  # Desktop notification when files are organized
    'use_custom_mappings_first': True  # Whether to prioritize custom mappings over default categories
}


class ConfigManager:
    """Manages configuration settings for the application."""
    
    def __init__(self, config_path):
        """
        Initialize the configuration manager.
        
        Args:
            config_path (Path): Path to the configuration file.
        """
        # Convert config_path to Path if it's not already
        config_path = Path(config_path) if not isinstance(config_path, Path) else config_path
        
        # If the path is in a protected directory, use the user_dirs module
        if user_dirs.is_protected_directory(config_path):
            # Use the same filename from the original config_path
            filename = config_path.name
            self.config_path = user_dirs.get_file_path('config', filename)
            logger.info(f"Using user-specific config path: {self.config_path}")
        else:
            self.config_path = config_path
        
        self.config = self._load_config()
        self._ensure_directories_exist()
    
    # Removed _is_in_protected_directory method as it's now in the user_dirs module
    
    def _load_config(self):
        """
        Load configuration from file or create a default one if it doesn't exist.
        
        Returns:
            dict: The configuration settings.
        """
        try:
            if not self.config_path.exists():
                logger.info(f"Configuration file not found at {self.config_path}. Creating default configuration.")
                self._create_default_config()
            
            with open(self.config_path, 'r') as config_file:
                config = yaml.safe_load(config_file)
                logger.info(f"Configuration loaded successfully from {self.config_path}")
                return self._validate_config(config)
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.info("Using default configuration")
            return DEFAULT_CONFIG
    
    def _create_default_config(self):
        """Create a default configuration file."""
        try:
            # Ensure the directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Try to write the config file
            try:
                with open(self.config_path, 'w') as config_file:
                    yaml.dump(DEFAULT_CONFIG, config_file, default_flow_style=False, sort_keys=False)
                logger.info(f"Default configuration created at {self.config_path}")
            except PermissionError:
                # If we can't write to the specified location, use the user_dirs module
                fallback_path = user_dirs.get_file_path('config', 'settings.yaml')
                
                with open(fallback_path, 'w') as config_file:
                    yaml.dump(DEFAULT_CONFIG, config_file, default_flow_style=False, sort_keys=False)
                
                # Update the config path to the new location
                self.config_path = fallback_path
                logger.info(f"Created configuration in fallback location: {self.config_path}")
        except Exception as e:
            logger.error(f"Error creating default configuration: {e}")
    
    def _validate_config(self, config):
        """
        Validate and fill in missing configuration with defaults.
        
        Args:
            config (dict): The configuration to validate.
            
        Returns:
            dict: The validated configuration.
        """
        validated_config = DEFAULT_CONFIG.copy()
        
        for key, value in config.items():
            if key in validated_config:
                if isinstance(value, dict) and isinstance(validated_config[key], dict):
                    for subkey, subvalue in value.items():
                        validated_config[key][subkey] = subvalue
                else:
                    validated_config[key] = value
        
        return validated_config
    
    def _ensure_directories_exist(self):
        """Ensure that all configured directories exist."""
        try:
            # Ensure source directory exists
            source_dir = Path(self.config['source_directory']).expanduser()
            source_dir.mkdir(parents=True, exist_ok=True)
            
            # Ensure destination directories exist
            for category, directory in self.config['destination_directories'].items():
                dest_dir = Path(directory).expanduser()
                dest_dir.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured destination directory exists: {dest_dir}")
        
        except Exception as e:
            logger.error(f"Error ensuring directories exist: {e}")
    
    def get_config(self):
        """
        Get the current configuration.
        
        Returns:
            dict: The current configuration.
        """
        return self.config
    
    def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the configuration and save it to file.
        
        Args:
            new_config: The new configuration settings.
            
        Returns:
            The updated configuration.
        """
        try:
            self.config = self._validate_config(new_config)
            
            try:
                # Try to write to the configured path
                with open(self.config_path, 'w') as config_file:
                    yaml.dump(self.config, config_file, default_flow_style=False, sort_keys=False)
                logger.info(f"Configuration updated and saved to {self.config_path}")
            except PermissionError:
                # If we can't write to the current location, use the user_dirs module
                fallback_path = user_dirs.get_file_path('config', 'settings.yaml')
                
                with open(fallback_path, 'w') as config_file:
                    yaml.dump(self.config, config_file, default_flow_style=False, sort_keys=False)
                
                # Update the config path for future saves
                self.config_path = fallback_path
                logger.warning(f"Couldn't write to {self.config_path}. Saved to {fallback_path} instead.")
            
            self._ensure_directories_exist()
            return self.config
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return self.config
