"""
UI Manager for the SELO FileFlow application.
Provides a PyQt5-based graphical interface for configuring and controlling the application.
"""

import os
import sys
import logging
from pathlib import Path
from functools import partial

# Set up Linux environment variables for cleaner startup (applies to all launch methods)
if sys.platform.startswith('linux'):
    # Set XDG_RUNTIME_DIR if not set
    if 'XDG_RUNTIME_DIR' not in os.environ:
        runtime_dir = f'/tmp/runtime-{os.getenv("USER", "user")}'
        os.environ['XDG_RUNTIME_DIR'] = runtime_dir
        # Create the directory if it doesn't exist
        Path(runtime_dir).mkdir(mode=0o700, exist_ok=True)
    
    # Suppress Qt warnings and PNG color profile warnings for cleaner output
    os.environ['QT_LOGGING_RULES'] = 'qt.qpa.xcb.glx.debug=false'
    # Suppress libpng warnings about color profiles
    os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning:PIL'
    
    # Set appropriate Qt platform theme for better desktop integration
    if 'QT_QPA_PLATFORMTHEME' not in os.environ:
        desktop_env = os.getenv('XDG_CURRENT_DESKTOP', '').lower()
        if 'gnome' in desktop_env:
            os.environ['QT_QPA_PLATFORMTHEME'] = 'gtk3'
        elif 'kde' in desktop_env or 'plasma' in desktop_env:
            os.environ['QT_QPA_PLATFORMTHEME'] = 'kde'
        else:
            os.environ['QT_QPA_PLATFORMTHEME'] = 'gtk3'  # Default fallback

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QTabWidget, QFormLayout,
    QLineEdit, QCheckBox, QMessageBox, QProgressDialog, QSystemTrayIcon,
    QMenu, QAction, QSpinBox, QStyle, QDialog, QGridLayout, QComboBox,
    QGroupBox, QListWidgetItem, QAbstractItemView, QSizePolicy
)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont, QWindow
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QThread, QSettings

# Import direct fixes module
from src.modules.direct_fixes import WindowsAppFixes

from src.modules.config_manager import ConfigManager
from src.modules.file_handler import FileHandler

logger = logging.getLogger(__name__)


class FileProcessWorker(QThread):
    """Worker thread for processing files in the background."""
    
    # Define signals for communication with main thread
    progress_signal = pyqtSignal(int, int)  # current, total
    status_signal = pyqtSignal(str)  # status message
    finished_signal = pyqtSignal(int)  # total processed
    error_signal = pyqtSignal(str)  # error message
    
    def __init__(self, config):
        """Initialize the worker thread."""
        super().__init__()
        self.config = config
        self.file_handler = FileHandler(config)
        self.abort_flag = False
    
    def run(self):
        """Process files in background thread."""
        try:
            processed_count = 0
            source_dirs = self.config.get('source_directory', '')
            
            # Convert to list if it's a single string
            if isinstance(source_dirs, str):
                source_dirs = [source_dirs]
            
            # Count total files to process
            total_files = 0
            for dir_path in source_dirs:
                expanded_path = Path(dir_path).expanduser()
                if expanded_path.exists() and expanded_path.is_dir():
                    # Count files in directory and all subdirectories
                    total_files += sum(1 for _ in expanded_path.rglob('*') if _.is_file())
            
            self.status_signal.emit(f"Processing {total_files} files...")
            
            # Custom file handler that emits progress
            class ProgressFileHandler(FileHandler):
                def __init__(self, config, progress_callback, abort_check):
                    super().__init__(config)
                    self.progress_callback = progress_callback
                    self.abort_check = abort_check
                    self.processed_count = 0
                
                def process_file(self, file_path):
                    # Check if abort was requested
                    if self.abort_check():
                        return False
                    
                    result = super().process_file(file_path)
                    if result:
                        self.processed_count += 1
                        self.progress_callback(self.processed_count, total_files)
                    return result
            
            # Create progress-aware file handler
            progress_handler = ProgressFileHandler(
                self.config, 
                self.progress_signal.emit,
                lambda: self.abort_flag
            )
            
            # Process each source directory
            for dir_path in source_dirs:
                if self.abort_flag:
                    break
                    
                expanded_path = Path(dir_path).expanduser()
                if expanded_path.exists() and expanded_path.is_dir():
                    self.status_signal.emit(f"Processing directory: {expanded_path}")
                    progress_handler.process_directory(expanded_path, recursive=True)
                else:
                    logger.warning(f"Source directory does not exist: {expanded_path}")
            
            if self.abort_flag:
                self.status_signal.emit("Operation canceled")
            else:
                self.finished_signal.emit(progress_handler.processed_count)
            
        except Exception as e:
            logger.error(f"Error in worker thread: {e}")
            self.error_signal.emit(str(e))
    
    def abort(self):
        """Set flag to abort processing."""
        self.abort_flag = True
        self.status_signal.emit("Canceling operation...")


class FileFlowUI(QMainWindow):
    """Main window for the SELO FileFlow UI."""
    
    def __init__(self, config_manager=None, config_path=None):
        """
        Initialize the main window.
        
        Args:
            config_manager (ConfigManager, optional): A config manager instance.
            config_path (str, optional): Path to the configuration file.
        """
        super().__init__()
        
        # CRITICAL FIX: Apply aggressive Windows icon handling before initializing UI
        if sys.platform == 'win32':
            try:
                # Load icon directly from file
                icon_path = os.path.abspath(os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    'resources', 'icon.ico'
                ))
                
                if os.path.exists(icon_path):
                    # Import needed modules
                    import ctypes
                    
                    # Set application ID for proper taskbar grouping
                    app_id = 'SELOdev.FileFlow.App.1.0'
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
                    
                    # Store icon path for later use when the window is actually visible
                    self.icon_path = icon_path
                    print(f"Will apply icon from: {icon_path} when window is shown")
            except Exception as e:
                print(f"Failed to apply icon fix: {e}")
        
        # Set up config manager
        if config_manager:
            self.config_manager = config_manager
        elif config_path:
            self.config_manager = ConfigManager(Path(config_path))
        else:
            default_config_path = Path(__file__).parent.parent.parent / 'config' / 'settings.yaml'
            self.config_manager = ConfigManager(default_config_path)
        
        self.config = self.config_manager.get_config()
        
        # Set up file handler
        self.file_handler = FileHandler(self.config)
        
        # Set up UI components
        self._init_ui()
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Set up system tray
        self._setup_tray()
        
        # Set up timer for status updates
        self.status_timer = QTimer()
        self.status_timer.setInterval(10000)  # 10 seconds
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start()
        
        # Load initial data
        self._load_config_to_ui()
    
    def _set_application_icon(self):
        """Set the application icon with enhanced handling for PyInstaller environments."""
        try:
            # Determine if we're running in a PyInstaller bundle
            is_frozen = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
            
            if is_frozen:
                # PyInstaller-specific path handling
                base_dir = sys._MEIPASS
                icon_path = os.path.join(base_dir, 'icon.ico')
                if not os.path.exists(icon_path):
                    # Try to find icon in resource directory embedded by PyInstaller
                    icon_path = os.path.join(base_dir, 'resources', 'icon.ico')
            else:
                # Standard path for development environment
                icon_path = os.path.abspath(os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    'resources', 'icon.ico'
                ))
            
            # Debug the icon path
            print(f"Looking for icon at: {icon_path}")
            
            # Check if icon exists
            if os.path.exists(icon_path):
                # Create icon and apply at multiple levels
                icon = QIcon(icon_path)
                
                # Apply icon to the window (standard method)
                self.setWindowIcon(icon)
                
                # Apply icon to the application (needed for taskbar)
                QApplication.instance().setWindowIcon(icon)
                
                # For Windows, try additional methods
                if sys.platform == 'win32':
                    try:
                        import ctypes
                        # Set application ID for proper taskbar grouping
                        app_id = 'SELOdev.FileFlow.App.1.0'
                        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
                        
                        # Try Win32 specific methods if available
                        try:
                            import win32gui
                            import win32con
                            import win32api
                            
                            # Force icon refresh in taskbar
                            self.winId()  # Ensure window has a valid ID
                            hwnd = int(self.winId())
                            win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, 
                                            win32gui.LoadImage(None, icon_path, win32con.IMAGE_ICON, 
                                                            0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE))
                            win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, 
                                            win32gui.LoadImage(None, icon_path, win32con.IMAGE_ICON, 
                                                            16, 16, win32con.LR_LOADFROMFILE))
                        except ImportError:
                            print("Win32 extensions not available for enhanced icon handling")
                    except Exception as e:
                        print(f"Windows-specific icon handling failed: {e}")
                
                print(f"Successfully set icon from: {icon_path}")
                return True
            else:
                print(f"WARNING: Icon file not found at: {icon_path}")
                return False
                
        except Exception as e:
            print(f"Error setting application icon: {e}")
            return False
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Set window properties
        self.setWindowTitle("FileFlow")
        self.resize(800, 600)
        
        # Set window icon - important for title bar
        self._set_application_icon()
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Create tabs
        self.folders_tab = self._create_folders_tab()
        self.file_types_tab = self._create_file_types_tab()
        self.custom_mappings_tab = self._create_custom_mappings_tab()
        self.settings_tab = self._create_settings_tab()
        
        # Add tabs to tab widget
        tab_widget.addTab(self.folders_tab, "Folders")
        tab_widget.addTab(self.file_types_tab, "File Types")
        tab_widget.addTab(self.custom_mappings_tab, "Custom Mappings")
        tab_widget.addTab(self.settings_tab, "Settings")
        
        # Add tab widget to main layout
        main_layout.addWidget(tab_widget)
        
        # Create bottom bar with status and buttons
        bottom_bar = QHBoxLayout()
        
        # Status label
        self.status_label = QLabel("Ready")
        bottom_bar.addWidget(self.status_label)
        
        # Spacer
        bottom_bar.addStretch()
        
        # Buttons
        self.process_now_btn = QPushButton("Process Now")
        self.process_now_btn.clicked.connect(self._process_now)
        bottom_bar.addWidget(self.process_now_btn)
        
        self.save_btn = QPushButton("Save Configuration")
        self.save_btn.clicked.connect(self._save_config)
        bottom_bar.addWidget(self.save_btn)
        
        # Add bottom bar to main layout
        main_layout.addLayout(bottom_bar)
        
        # Set central widget
        self.setCentralWidget(central_widget)
    
    def _create_folders_tab(self):
        """Create the folders tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Source directories section
        source_group = QGroupBox("Source Directories")
        source_layout = QVBoxLayout(source_group)
        
        # List of source directories
        self.source_list = QListWidget()
        self.source_list.setSelectionMode(QListWidget.ExtendedSelection)
        source_layout.addWidget(self.source_list)
        
        # Buttons for source directories
        source_buttons = QHBoxLayout()
        
        add_source_btn = QPushButton("Add Folder")
        add_source_btn.clicked.connect(partial(self._add_folder, self.source_list, "source"))
        source_buttons.addWidget(add_source_btn)
        
        remove_source_btn = QPushButton("Remove Selected")
        remove_source_btn.clicked.connect(partial(self._remove_selected, self.source_list, "source"))
        source_buttons.addWidget(remove_source_btn)
        
        source_layout.addLayout(source_buttons)
        
        # Destination directories section
        dest_group = QGroupBox("Destination Directories")
        dest_layout = QFormLayout(dest_group)
        
        # Create inputs for each destination category
        self.dest_inputs = {}
        for category in ["images", "documents", "videos", "software", "other"]:
            row_layout = QHBoxLayout()
            
            # Path input
            path_input = QLineEdit()
            path_input.setReadOnly(True)
            row_layout.addWidget(path_input, 1)
            
            # Browse button
            browse_btn = QPushButton("Browse...")
            browse_btn.clicked.connect(partial(self._browse_folder, path_input, category))
            row_layout.addWidget(browse_btn)
            
            # Add to form
            dest_layout.addRow(f"{category.capitalize()}:", row_layout)
            
            # Save reference
            self.dest_inputs[category] = path_input
        
        # Add groups to tab layout
        layout.addWidget(source_group)
        layout.addWidget(dest_group)
        
        return tab
    
    def _create_file_types_tab(self):
        """Create the file types tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # File type mapping section
        self.file_type_widgets = {}
        
        for category in ["images", "documents", "videos", "software", "other"]:
            group = QGroupBox(f"{category.capitalize()} File Types")
            group_layout = QVBoxLayout(group)
            
            # List of file extensions
            list_widget = QListWidget()
            list_widget.setSelectionMode(QListWidget.ExtendedSelection)
            group_layout.addWidget(list_widget)
            
            # Buttons
            buttons_layout = QHBoxLayout()
            
            add_btn = QPushButton("Add Extension")
            add_btn.clicked.connect(partial(self._add_extension, list_widget, category))
            buttons_layout.addWidget(add_btn)
            
            remove_btn = QPushButton("Remove Selected")
            remove_btn.clicked.connect(partial(self._remove_extension, list_widget, category))
            buttons_layout.addWidget(remove_btn)
            
            group_layout.addLayout(buttons_layout)
            
            # Add to tab layout
            layout.addWidget(group)
            
            # Save reference
            self.file_type_widgets[category] = list_widget
        
        return tab
    
    def _create_custom_mappings_tab(self):
        """Create the custom mappings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Instructions label
        instructions = QLabel(
            "Create custom mappings to organize specific file types to custom destinations. "
            "These mappings will be checked before the default file type categories."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Use custom mappings checkbox
        self.use_custom_mappings_cb = QCheckBox("Prioritize custom mappings over default categories")
        layout.addWidget(self.use_custom_mappings_cb)
        
        # Custom mappings list
        self.custom_mappings_list = QListWidget()
        self.custom_mappings_list.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.custom_mappings_list)
        
        # Buttons for managing custom mappings
        buttons_layout = QHBoxLayout()
        
        self.add_mapping_btn = QPushButton("Add Mapping")
        self.add_mapping_btn.clicked.connect(self._add_custom_mapping)
        buttons_layout.addWidget(self.add_mapping_btn)
        
        self.edit_mapping_btn = QPushButton("Edit Selected")
        self.edit_mapping_btn.clicked.connect(self._edit_custom_mapping)
        buttons_layout.addWidget(self.edit_mapping_btn)
        
        self.remove_mapping_btn = QPushButton("Remove Selected")
        self.remove_mapping_btn.clicked.connect(self._remove_custom_mapping)
        buttons_layout.addWidget(self.remove_mapping_btn)
        
        layout.addLayout(buttons_layout)
        
        return tab
    
    def _create_settings_tab(self):
        """Create the settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Move files checkbox
        self.move_files_cb = QCheckBox("Move files (instead of copying)")
        layout.addRow(self.move_files_cb)
        
        # Organize existing files checkbox
        self.organize_existing_cb = QCheckBox("Organize existing files when starting")
        layout.addRow(self.organize_existing_cb)
        
        # Notify on move checkbox
        self.notify_cb = QCheckBox("Show notification when files are organized")
        layout.addRow(self.notify_cb)
        
        # Auto-start with Windows checkbox
        self.autostart_cb = QCheckBox("Start automatically with Windows")
        layout.addRow(self.autostart_cb)
        
        # Check interval
        interval_layout = QHBoxLayout()
        self.check_interval_spin = QSpinBox()
        self.check_interval_spin.setMinimum(1)
        self.check_interval_spin.setMaximum(60)
        self.check_interval_spin.setValue(1)
        interval_layout.addWidget(self.check_interval_spin)
        interval_layout.addWidget(QLabel("minutes"))
        layout.addRow("Check interval:", interval_layout)
        
        # Add Apply button
        self.apply_btn = QPushButton("Apply Settings")
        self.apply_btn.clicked.connect(self._apply_settings)
        layout.addRow(self.apply_btn)
        
        return tab
    
    def _setup_tray(self):
        """Set up system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Load the application icon
        icon_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'icon.ico'))
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.tray_icon.setIcon(icon)
            # Set tooltip explicitly to ensure it shows FileFlow
            self.tray_icon.setToolTip("FileFlow")
            print(f"Tray icon set from: {icon_path}")
        else:
            print(f"Warning: Tray icon not found at {icon_path}")
            # Create a fallback icon
            pixmap = QPixmap(QSize(64, 64))
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setPen(Qt.blue)
            painter.setFont(QFont("Arial", 20, QFont.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "FF")
            painter.end()
            self.tray_icon.setIcon(QIcon(pixmap))
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Add actions
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        process_action = QAction("Process Now", self)
        process_action.triggered.connect(self._process_now)
        tray_menu.addAction(process_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self._exit_app)
        tray_menu.addAction(exit_action)
        
        # Set the menu
        self.tray_icon.setContextMenu(tray_menu)
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Connect activation signal
        self.tray_icon.activated.connect(self._tray_activated)
    
    def _create_placeholder_icon(self):
        """Load the application icon from resources folder."""
        # Try to load the actual icon file
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'icon.ico')
        
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            # Fallback to a simple placeholder if icon not found
            print(f"Warning: Icon file not found at {icon_path}")
            pixmap = QPixmap(QSize(64, 64))
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setPen(Qt.blue)
            painter.setFont(QFont("Arial", 20, QFont.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "FF")
            painter.end()
            return QIcon(pixmap)
    
    def _tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()
    
    def _exit_app(self):
        """Exit the application."""
        self._save_config()
        QApplication.quit()
    
    def showEvent(self, event):
        """Handle the window show event - apply icon fixes when window is visible."""
        super().showEvent(event)
        
        # Fix title bar icon when window is actually shown and visible
        if hasattr(self, 'icon_path') and os.path.exists(self.icon_path):
            try:
                # Set icon multiple ways to ensure it's picked up
                app_icon = QIcon(self.icon_path)
                self.setWindowIcon(app_icon)
                QApplication.instance().setWindowIcon(app_icon)
                
                # Use native Windows API if available
                if sys.platform == 'win32':
                    try:
                        import ctypes
                        from ctypes import windll
                        # Try forcing icon refresh with Windows API
                        hwnd = int(self.winId())
                        windll.user32.SendMessageW(hwnd, 0x0080, 0, 0)  # WM_SETICON
                    except Exception as e:
                        print(f"Windows icon API error: {e}")
                        
                print("Applied icon to visible window")
            except Exception as e:
                print(f"Error setting window icon: {e}")
    
    def closeEvent(self, event):
        """Handle the window close event."""
        if self.tray_icon.isVisible():
            # Hide to tray instead of closing
            self.hide()
            # DIRECT FIX: Force the notification title to be FileFlow
            self.tray_icon.showMessage(
                "FileFlow", # Fixed title
                "FileFlow is still running in the background.", # Fixed message
                QSystemTrayIcon.Information,
                3000
            )
            event.ignore()
        else:
            # Actually close
            self._save_config()
            event.accept()
    
    def _show_tray_message(self, message, title=None, icon=QSystemTrayIcon.Information, duration=3000):
        """Show a message from the tray icon.
        
        Args:
            message: The message text to display
            title: The title of the notification (defaults to "FileFlow")
            icon: The icon type to display (Information, Warning, Critical)
            duration: How long to show the notification in milliseconds
        """
        # CRITICAL FIX: Force the title to always be FileFlow, no matter what
        title = "FileFlow"  # Hard-coded to ensure consistency
            
        # CRITICAL FIX: Make sure there is no trace of Download Organizer in the message
        if message and ("download" in message.lower() or "organizer" in message.lower()):
            message = message.replace("Download Organizer", "FileFlow")
            message = message.replace("download organizer", "FileFlow")
            message = message.replace("DownloadOrganizer", "FileFlow")
            
        print(f"Showing notification with fixed title: {title}")
        print(f"Notification message: {message}")
        
        # Show the message with hard-coded title
        self.tray_icon.showMessage(title, message, icon, duration)
    
    def _load_config_to_ui(self):
        """Load configuration data into the UI."""
        # Source directories
        source_dir = self.config.get('source_directory', '')
        if source_dir:
            # Convert to list if it's a single string
            if isinstance(source_dir, str):
                source_dirs = [source_dir]
            else:
                source_dirs = source_dir
            
            # Add to list
            for dir_path in source_dirs:
                expanded_path = str(Path(dir_path).expanduser())
                self.source_list.addItem(expanded_path)
        
        # Destination directories
        dest_dirs = self.config.get('destination_directories', {})
        for category, path in dest_dirs.items():
            if category in self.dest_inputs:
                expanded_path = str(Path(path).expanduser())
                self.dest_inputs[category].setText(expanded_path)
        
        # File type mappings
        file_types = self.config.get('file_types', {})
        for category, extensions in file_types.items():
            if category in self.file_type_widgets:
                list_widget = self.file_type_widgets[category]
                list_widget.clear()
                for ext in extensions:
                    list_widget.addItem(ext)
        
        # Custom mappings
        self._refresh_custom_mappings_list()
        
        # Use custom mappings first
        self.use_custom_mappings_cb.setChecked(self.config.get('use_custom_mappings_first', True))
        
        # Settings
        self.move_files_cb.setChecked(self.config.get('move_files', True))
        self.organize_existing_cb.setChecked(self.config.get('organize_existing_files', True))
        self.notify_cb.setChecked(self.config.get('notify_on_move', True))
        
        # Check if we're set to auto-start
        # This is a Windows-specific implementation
        import winreg
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            )
            winreg.QueryValueEx(key, "SELOFileFlow")
            self.autostart_cb.setChecked(True)
        except:
            self.autostart_cb.setChecked(False)
        
        # Check interval
        self.check_interval_spin.setValue(self.config.get('check_interval_minutes', 1))
    
    def _update_config_from_ui(self):
        """Update configuration from UI inputs."""
        # Source directories - support multiple folders
        source_dirs = []
        for i in range(self.source_list.count()):
            source_dirs.append(self.source_list.item(i).text())
        
        # If only one source directory, store as string for backward compatibility
        if len(source_dirs) == 1:
            self.config['source_directory'] = source_dirs[0]
        elif len(source_dirs) > 1:
            # Store as list for multiple directories
            self.config['source_directory'] = source_dirs
        
        # Destination directories
        for category, input_widget in self.dest_inputs.items():
            path = input_widget.text()
            if path:
                self.config['destination_directories'][category] = path
        
        # File type mappings
        for category, list_widget in self.file_type_widgets.items():
            extensions = []
            for i in range(list_widget.count()):
                extensions.append(list_widget.item(i).text())
            self.config['file_types'][category] = extensions
        
        # Use custom mappings first setting
        self.config['use_custom_mappings_first'] = self.use_custom_mappings_cb.isChecked()
        
        # Settings
        self.config['move_files'] = self.move_files_cb.isChecked()
        self.config['organize_existing_files'] = self.organize_existing_cb.isChecked()
        self.config['notify_on_move'] = self.notify_cb.isChecked()
        self.config['check_interval_minutes'] = self.check_interval_spin.value()
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            self._update_config_from_ui()
            self.config_manager.update_config(self.config)
            self._show_status("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            QMessageBox.warning(self, "Error", f"Could not save configuration: {e}")
    
    def _apply_settings(self):
        """Apply settings from the settings tab."""
        # Handle auto-start setting
        self._set_autostart(self.autostart_cb.isChecked())
        
        # Save other settings
        self._save_config()
        
        # Show confirmation
        QMessageBox.information(self, "Settings Applied", "Settings have been applied successfully.")
    
    def _set_autostart(self, enabled):
        """Set or remove auto-start entry across platforms."""
        try:
            from src.modules.direct_fixes import CrossPlatformAppFixes
            
            success = CrossPlatformAppFixes.setup_autostart(enabled)
            
            if success:
                if enabled:
                    logger.info("Added FileFlow to startup")
                    QMessageBox.information(self, "Success", "FileFlow has been added to startup programs.")
                else:
                    logger.info("Removed FileFlow from startup")
                    QMessageBox.information(self, "Success", "FileFlow has been removed from startup programs.")
            else:
                error_msg = f"Could not {'enable' if enabled else 'disable'} auto-start on this platform."
                logger.error(error_msg)
                QMessageBox.warning(self, "Error", error_msg)
                
        except Exception as e:
            logger.error(f"Error setting auto-start: {e}")
            QMessageBox.warning(self, "Error", f"Could not set auto-start: {e}")
    
    def _add_folder(self, list_widget, folder_type):
        """Add a folder to the list."""
        folder = QFileDialog.getExistingDirectory(
            self, f"Select {folder_type.capitalize()} Directory",
            str(Path.home())
        )
        
        if folder:
            list_widget.addItem(folder)
    
    def _remove_selected(self, list_widget, folder_type):
        """Remove selected folders from the list."""
        selected_items = list_widget.selectedItems()
        for item in selected_items:
            list_widget.takeItem(list_widget.row(item))
    
    def _browse_folder(self, line_edit, category):
        """Browse for a folder and set the path in the line edit."""
        folder = QFileDialog.getExistingDirectory(
            self, f"Select {category.capitalize()} Directory",
            line_edit.text() or str(Path.home())
        )
        
        if folder:
            line_edit.setText(folder)
    
    def _add_extension(self, list_widget, category):
        """Add a file extension to the list."""
        # Simple dialog to input extension
        from PyQt5.QtWidgets import QInputDialog
        
        extension, ok = QInputDialog.getText(
            self, f"Add {category.capitalize()} Extension",
            "Enter file extension (include the dot, e.g. '.pdf'):"
        )
        
        if ok and extension:
            # Validate extension
            if not extension.startswith('.'):
                extension = '.' + extension
            
            # Add to list
            list_widget.addItem(extension.lower())
    
    def _remove_extension(self, list_widget, category):
        """Remove selected extensions from the list."""
        selected_items = list_widget.selectedItems()
        for item in selected_items:
            list_widget.takeItem(list_widget.row(item))
    
    def _refresh_custom_mappings_list(self):
        """Refresh the custom mappings list with current configuration."""
        self.custom_mappings_list.clear()
        custom_mappings = self.config.get('custom_mappings', [])
        
        for mapping in custom_mappings:
            name = mapping.get('name', '')
            extensions = mapping.get('extensions', [])
            destination = mapping.get('destination', '')
            
            if name and extensions and destination:
                # Create a formatted display string
                extensions_str = ', '.join(extensions)
                display_text = f"{name}: {extensions_str} → {destination}"
                
                # Add to list with the full mapping data stored as user data
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, mapping)  # Store the mapping dictionary as item data
                self.custom_mappings_list.addItem(item)
    
    def _add_custom_mapping(self):
        """Add a new custom file type mapping."""
        # Create and show dialog to gather mapping information
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Custom Mapping")
        dialog.setMinimumWidth(400)
        
        layout = QFormLayout(dialog)
        
        # Name input
        name_input = QLineEdit()
        layout.addRow("Mapping Name:", name_input)
        
        # Extensions input
        extensions_input = QLineEdit()
        extensions_input.setPlaceholderText(".pdf, .doc, .txt")
        layout.addRow("File Extensions (comma separated):", extensions_input)
        
        # Destination folder input and browse button
        dest_layout = QHBoxLayout()
        dest_input = QLineEdit()
        dest_input.setReadOnly(True)
        dest_layout.addWidget(dest_input, 1)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self._browse_folder_for_dialog(dest_input))
        dest_layout.addWidget(browse_btn)
        
        layout.addRow("Destination Folder:", dest_layout)
        
        # Buttons
        buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow("", buttons)
        
        # Connect buttons
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        # Execute dialog
        if dialog.exec_() == QDialog.Accepted:
            # Get values and create mapping
            name = name_input.text().strip()
            extensions_text = extensions_input.text().strip()
            destination = dest_input.text().strip()
            
            if name and extensions_text and destination:
                # Process extensions
                extensions = [ext.strip().lower() for ext in extensions_text.split(',')]
                
                # Ensure each extension starts with a dot
                extensions = ['.' + ext if not ext.startswith('.') else ext for ext in extensions]
                
                # Create the mapping
                mapping = {
                    'name': name,
                    'extensions': extensions,
                    'destination': destination
                }
                
                # Add to config
                if 'custom_mappings' not in self.config:
                    self.config['custom_mappings'] = []
                    
                self.config['custom_mappings'].append(mapping)
                
                # Refresh the list
                self._refresh_custom_mappings_list()
                
                # Show success message
                self.status_label.setText(f"Added custom mapping: {name}")
            else:
                # Show error message
                QMessageBox.warning(self, "Missing Information",
                                  "Please provide a name, at least one extension, and a destination folder.")
    
    def _edit_custom_mapping(self):
        """Edit the selected custom mapping."""
        selected_items = self.custom_mappings_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a mapping to edit.")
            return
        
        # Get the selected mapping
        item = selected_items[0]
        mapping = item.data(Qt.UserRole)
        
        if not mapping:
            QMessageBox.warning(self, "Error", "Could not retrieve mapping data.")
            return
        
        # Create and show dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Custom Mapping")
        dialog.setMinimumWidth(400)
        
        layout = QFormLayout(dialog)
        
        # Name input
        name_input = QLineEdit(mapping.get('name', ''))
        layout.addRow("Mapping Name:", name_input)
        
        # Extensions input
        extensions_str = ', '.join(mapping.get('extensions', []))
        extensions_input = QLineEdit(extensions_str)
        extensions_input.setPlaceholderText(".pdf, .doc, .txt")
        layout.addRow("File Extensions (comma separated):", extensions_input)
        
        # Destination folder input and browse button
        dest_layout = QHBoxLayout()
        dest_input = QLineEdit(mapping.get('destination', ''))
        dest_input.setReadOnly(True)
        dest_layout.addWidget(dest_input, 1)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self._browse_folder_for_dialog(dest_input))
        dest_layout.addWidget(browse_btn)
        
        layout.addRow("Destination Folder:", dest_layout)
        
        # Buttons
        buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow("", buttons)
        
        # Connect buttons
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        # Execute dialog
        if dialog.exec_() == QDialog.Accepted:
            # Get values and update mapping
            name = name_input.text().strip()
            extensions_text = extensions_input.text().strip()
            destination = dest_input.text().strip()
            
            if name and extensions_text and destination:
                # Process extensions
                extensions = [ext.strip().lower() for ext in extensions_text.split(',')]
                
                # Ensure each extension starts with a dot
                extensions = ['.' + ext if not ext.startswith('.') else ext for ext in extensions]
                
                # Update the mapping
                mapping['name'] = name
                mapping['extensions'] = extensions
                mapping['destination'] = destination
                
                # Update in config
                custom_mappings = self.config.get('custom_mappings', [])
                for i, m in enumerate(custom_mappings):
                    if m.get('name') == mapping.get('name'):
                        custom_mappings[i] = mapping
                        break
                
                # Refresh the list
                self._refresh_custom_mappings_list()
                
                # Show success message
                self.status_label.setText(f"Updated custom mapping: {name}")
            else:
                # Show error message
                QMessageBox.warning(self, "Missing Information",
                                  "Please provide a name, at least one extension, and a destination folder.")
    
    def _remove_custom_mapping(self):
        """Remove the selected custom mapping."""
        selected_items = self.custom_mappings_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a mapping to remove.")
            return
        
        # Get the selected mapping
        item = selected_items[0]
        mapping = item.data(Qt.UserRole)
        
        # Confirm removal
        response = QMessageBox.question(self, "Confirm Removal",
                                     f"Are you sure you want to remove the mapping '{mapping.get('name')}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if response == QMessageBox.Yes:
            # Remove from config
            custom_mappings = self.config.get('custom_mappings', [])
            self.config['custom_mappings'] = [m for m in custom_mappings if m.get('name') != mapping.get('name')]
            
            # Refresh the list
            self._refresh_custom_mappings_list()
            
            # Show success message
            self.status_label.setText(f"Removed custom mapping: {mapping.get('name')}")
    
    def _browse_folder_for_dialog(self, line_edit):
        """Browse for a folder and set the path in the line edit (used in dialogs)."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Destination Directory",
            line_edit.text() or str(Path.home())
        )
        
        if folder:
            line_edit.setText(folder)
    
    def _process_now(self):
        """Process files in the source directories now using a background thread."""
        try:
            # Get latest config
            self._update_config_from_ui()
            
            # Create a progress dialog
            progress_dialog = QProgressDialog("Preparing to process files...", "Cancel", 0, 100, self)
            progress_dialog.setWindowTitle("FileFlow - Processing Files")
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.setAutoClose(True)
            progress_dialog.setMinimumDuration(0)  # Show immediately
            
            # Create worker thread
            self.worker = FileProcessWorker(self.config)
            
            # Connect signals
            self.worker.progress_signal.connect(self._update_progress)
            self.worker.status_signal.connect(progress_dialog.setLabelText)
            self.worker.finished_signal.connect(lambda count: self._processing_finished(count, progress_dialog))
            self.worker.error_signal.connect(lambda err: self._processing_error(err, progress_dialog))
            
            # Connect cancel button
            progress_dialog.canceled.connect(self.worker.abort)
            
            # Start processing
            self.worker.start()
            
            # Show toast notification that processing has started
            if self.config.get('notify_on_move', True):
                self._show_tray_message("FileFlow is organizing your files...")
            
            # Show the dialog
            progress_dialog.show()
            
        except Exception as e:
            logger.error(f"Error starting file processing: {e}")
            self._show_status(f"Error: {e}")
            QMessageBox.warning(self, "Error", f"Could not process files: {e}")
    
    def _update_progress(self, current, total):
        """Update progress dialog with current progress."""
        if total > 0:
            percent = int((current / total) * 100)
            # Find the progress dialog
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, QProgressDialog):
                    widget.setValue(percent)
                    widget.setLabelText(f"Processing files: {current}/{total} ({percent}%)")
                    break
    
    def _processing_finished(self, count, progress_dialog):
        """Handle completion of file processing."""
        message = f"Processed {count} files successfully."
        self._show_status(message)
        
        # Close the progress dialog if it's still open
        if progress_dialog and progress_dialog.isVisible():
            progress_dialog.close()
        
        # Show notification
        if self.config.get('notify_on_move', True):
            self._show_tray_message(message, "FileFlow - Complete")
    
    def _processing_error(self, error_message, progress_dialog):
        """Handle errors during file processing."""
        logger.error(f"Error processing files: {error_message}")
        self._show_status(f"Error: {error_message}")
        
        # Close the progress dialog if it's still open
        if progress_dialog and progress_dialog.isVisible():
            progress_dialog.close()
            
        # Show error message
        QMessageBox.warning(self, "Error", f"Error processing files: {error_message}")
        
        # Show notification
        if self.config.get('notify_on_move', True):
            self._show_tray_message(f"Error: {error_message}", "FileFlow - Error")
    
    def _update_status(self):
        """Update the status label with current info."""
        # Just update the time for now
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.status_label.setText(f"Last check: {now}")
    
    def _show_status(self, message):
        """Show a message in the status bar."""
        self.status_label.setText(message)


def run_ui(config_path=None):
    """
    Run the FileFlow UI.
    
    Args:
        config_path (str, optional): Path to the configuration file.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("FileFlow")
    
    # Set application icon for all windows
    icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'icon.ico')
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
        
        # More explicit way to set the icon for all windows
        from PyQt5.QtCore import Qt
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)  # For better scaling on high DPI displays
        
        # Print for debugging
        print(f"Setting application icon from: {icon_path}")
    
    # Set app style
    app.setStyle("Fusion")
    
    # Create and show the main window
    main_window = FileFlowUI(config_path=config_path)
    
    # Check for --minimized flag
    if "--minimized" in sys.argv:
        # Start minimized to tray
        pass
    else:
        main_window.show()
    
    # Run the app
    sys.exit(app.exec_())
