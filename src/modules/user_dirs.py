"""
User directory management for FileFlow application.
Handles the creation and management of user-specific data directories.
"""
import os
import sys
from pathlib import Path
from typing import Union, Literal

# Type definitions for directory types
DirType = Literal['config', 'logs', 'data', 'cache']

class UserDirectories:
    """Manages user-specific directories for the application."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize user directories."""
        if getattr(self, "_initialized", False):
            return
            
        # Determine if running as packaged application
        self.is_frozen = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
        self.platform = sys.platform
        
        # Set up base directories based on platform and packaging
        if self.is_frozen:
            # For packaged application, use appropriate user directories
            if self.platform == 'win32':
                # Windows: Use AppData
                self.base_user_dir = Path(os.environ.get('APPDATA', '')) / "SELOdev" / "FileFlow"
            elif self.platform.startswith('linux'):
                # Linux: Use XDG Base Directory specification
                xdg_config_home = os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')
                self.base_user_dir = Path(xdg_config_home) / "fileflow"
            elif self.platform == 'darwin':
                # macOS: Use ~/Library/Application Support
                self.base_user_dir = Path.home() / "Library" / "Application Support" / "FileFlow"
            else:
                # Fallback for other Unix-like systems
                self.base_user_dir = Path.home() / ".fileflow"
                
            # Get the application directory (where the executable is)
            if self.is_frozen:
                self.app_dir = Path(sys._MEIPASS)
            else:
                self.app_dir = Path(__file__).parent.parent.parent
        else:
            # For development, use project directory
            self.app_dir = Path(__file__).parent.parent.parent
            
            # In development mode, still respect platform conventions for user data
            if self.platform == 'win32':
                # Windows development: use project directory
                self.base_user_dir = self.app_dir
            elif self.platform.startswith('linux'):
                # Linux development: use XDG directories or project dir if not writable
                try:
                    xdg_config_home = os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')
                    test_dir = Path(xdg_config_home) / "fileflow-dev"
                    test_dir.mkdir(parents=True, exist_ok=True)
                    # Test if we can write to it
                    test_file = test_dir / ".test"
                    test_file.touch()
                    test_file.unlink()
                    self.base_user_dir = test_dir
                except (PermissionError, OSError):
                    # Fall back to project directory if XDG dirs aren't writable
                    self.base_user_dir = self.app_dir
            else:
                # Other platforms: use project directory for development
                self.base_user_dir = self.app_dir
        
        # Create specific directories with platform-appropriate structure
        if self.platform.startswith('linux') and self.is_frozen:
            # Linux follows XDG Base Directory specification more strictly
            xdg_data_home = os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share')
            xdg_cache_home = os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')
            
            self.dirs = {
                'config': self.base_user_dir,  # Already set to XDG_CONFIG_HOME/fileflow
                'logs': Path(xdg_data_home) / "fileflow" / "logs",
                'data': Path(xdg_data_home) / "fileflow",
                'cache': Path(xdg_cache_home) / "fileflow"
            }
        else:
            # Windows, macOS, or development mode: use simple subdirectory structure
            self.dirs = {
                'config': self.base_user_dir / "config",
                'logs': self.base_user_dir / "logs",
                'data': self.base_user_dir / "data",
                'cache': self.base_user_dir / "cache"
            }
        
        self._initialized = True
    
    def get_dir(self, dir_type: DirType, create: bool = True) -> Path:
        """
        Get a specific user directory path.
        
        Args:
            dir_type: Type of directory ('config', 'logs', 'data', 'cache')
            create: Whether to create the directory if it doesn't exist
            
        Returns:
            Path to the requested directory
        """
        dir_path = self.dirs.get(dir_type)
        if dir_path is None:
            raise ValueError(f"Invalid directory type: {dir_type}")
            
        if create and not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            
        return dir_path
    
    def get_file_path(self, dir_type: DirType, filename: str, create_dir: bool = True) -> Path:
        """
        Get the path to a file within a user directory.
        
        Args:
            dir_type: Type of directory ('config', 'logs', 'data', 'cache')
            filename: Name of the file
            create_dir: Whether to create the directory if it doesn't exist
            
        Returns:
            Path to the file
        """
        return self.get_dir(dir_type, create_dir) / filename
    
    def is_protected_directory(self, path: Union[str, Path]) -> bool:
        """
        Check if a path is in a protected directory that requires admin privileges.
        
        Args:
            path: The path to check
            
        Returns:
            True if the path is in a protected directory, False otherwise
        """
        path_str = str(path).lower()
        
        if self.platform == 'win32':
            protected_dirs = [
                "program files", 
                "program files (x86)", 
                "windows", 
                "system32"
            ]
        elif self.platform.startswith('linux'):
            protected_dirs = [
                "/bin", "/sbin", "/usr/bin", "/usr/sbin",
                "/etc", "/boot", "/sys", "/proc",
                "/root", "/var/log", "/var/lib",
                "/usr/lib", "/usr/share", "/opt"
            ]
        elif self.platform == 'darwin':
            protected_dirs = [
                "/system", "/usr", "/bin", "/sbin",
                "/private", "/etc", "/var", "/tmp"
            ]
        else:
            # Generic Unix-like system
            protected_dirs = [
                "/bin", "/sbin", "/usr", "/etc",
                "/boot", "/sys", "/proc", "/root"
            ]
        
        return any(protected_dir in path_str for protected_dir in protected_dirs)

# Singleton instance
user_dirs = UserDirectories()
