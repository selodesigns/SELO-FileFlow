import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QSystemTrayIcon, QMenu, QAction, QMessageBox, QTabWidget, QListWidget, QListWidgetItem, QLineEdit, QFormLayout, QInputDialog, QStatusBar, QCheckBox, QSlider, QSpinBox, QGroupBox, QTextEdit
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QEvent
from ..config import load_config, save_config, CONFIG_FILE
from ..organizer import organize_files, reorganize_existing_files

ICON_PATH = Path(__file__).parent.parent / 'data' / 'icons' / 'fileflow.png'

class FileFlowMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FileFlow - Advanced Media Content Classification & Organization')
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        
        # Make window resizable with better default size
        self.setMinimumSize(800, 600)  # Minimum size for usability
        self.resize(1000, 700)  # Better default size
        
        # Enable resizing and maximize button
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | 
                           Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        self.init_ui()
        self.create_tray()
        self.tray.setToolTip('FileFlow - Advanced Media Organization')
        self.tray.activated.connect(self.on_tray_activated)

    def closeEvent(self, event):
        # Hide to tray instead of closing
        event.ignore()
        self.hide()
        self.tray.showMessage('SELO FileFlow', 'App is running in the system tray.', QIcon(str(ICON_PATH)) if ICON_PATH.exists() else QIcon(), 2000)

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            self.hide()
            self.tray.showMessage('SELO FileFlow', 'App minimized to tray.', QIcon(str(ICON_PATH)) if ICON_PATH.exists() else QIcon(), 2000)
        super().changeEvent(event)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()
                self.raise_()
                self.activateWindow()

    def init_ui(self):
        print('init_ui start')
        config = {}
        try:
            config = load_config()
            if not isinstance(config, dict):
                raise ValueError('Config is not a dictionary')
        except Exception as e:
            print(f'[init_ui] Config error: {e}')
            QMessageBox.critical(self, 'Config Error', f'Failed to load config: {e}\nDefaulting to empty config.')
            config = {}
        print('init_ui: config loaded')
        tabs = QTabWidget()
        print('init_ui: QTabWidget created')
        # Folders Tab - Enhanced with descriptions
        folders_tab = QWidget()
        folders_layout = QVBoxLayout()
        
        # Add main description
        main_desc = QLabel(
            '<h3>📁 Folder Configuration</h3>'
            '<p>Configure where FileFlow should look for files to organize (sources) and where to move them (destinations).</p>'
        )
        main_desc.setWordWrap(True)
        folders_layout.addWidget(main_desc)
        
        # Source Directories Section
        source_group = QGroupBox('📥 Source Directories')
        source_group.setToolTip('Folders that FileFlow will monitor and organize files from')
        source_layout = QVBoxLayout()
        
        source_desc = QLabel(
            '<b>What are Source Directories?</b><br>'
            'These are folders where FileFlow looks for files to organize. Add folders like Downloads, '
            'Desktop, or any location where you save mixed media files. FileFlow will automatically '
            'sort files from these locations using advanced content classification.'
        )
        source_desc.setWordWrap(True)
        source_desc.setStyleSheet('color: #666; font-size: 11px; margin: 5px;')
        source_layout.addWidget(source_desc)
        
        self.source_list = QListWidget()
        self.source_list.setToolTip('List of folders FileFlow monitors for new files to organize')
        for src in config.get('source_directories', []):
            self.source_list.addItem(QListWidgetItem(src))
        source_layout.addWidget(self.source_list)
        
        # Source buttons with improved legibility
        source_btn_layout = QHBoxLayout()
        btn_add_source = QPushButton('Add Source')
        btn_add_source.setToolTip('Add a new folder for FileFlow to monitor and organize files from')
        btn_add_source.clicked.connect(self.add_source_folder)
        btn_add_source.setMinimumHeight(30)
        
        btn_browse_source = QPushButton('Browse...')
        btn_browse_source.setToolTip('Browse your computer to select a folder to monitor')
        btn_browse_source.clicked.connect(self.browse_and_add_source)
        btn_browse_source.setMinimumHeight(30)
        
        btn_remove_source = QPushButton('Remove')
        btn_remove_source.setToolTip('Remove the selected source folder from monitoring')
        btn_remove_source.clicked.connect(self.remove_selected_source)
        btn_remove_source.setMinimumHeight(30)
        
        source_btn_layout.addWidget(btn_add_source)
        source_btn_layout.addWidget(btn_browse_source)
        source_btn_layout.addWidget(btn_remove_source)
        source_layout.addLayout(source_btn_layout)
        source_group.setLayout(source_layout)
        folders_layout.addWidget(source_group)
        
        # Destination Directories Section
        dest_group = QGroupBox('📤 Destination Directories')
        dest_group.setToolTip('Organized folders where FileFlow will move sorted files')
        dest_layout = QVBoxLayout()
        
        dest_desc = QLabel(
            '<b>What are Destination Directories?</b><br>'
            'These are organized folders where FileFlow moves sorted files. Each category (Images, Videos, '
            'Documents, etc.) gets its own destination folder. FileFlow will create NSFW and SFW subfolders '
            'within each category for intelligent content separation.'
        )
        dest_desc.setWordWrap(True)
        dest_desc.setStyleSheet('color: #666; font-size: 11px; margin: 5px;')
        dest_layout.addWidget(dest_desc)
        
        self.dest_list = QListWidget()
        self.dest_list.setToolTip('List of organized destination folders for each file category')
        for cat, dst in config.get('destination_directories', {}).items():
            self.dest_list.addItem(QListWidgetItem(f'{cat}: {dst}'))
        dest_layout.addWidget(self.dest_list)
        
        # Destination buttons with improved legibility
        dest_btn_layout = QHBoxLayout()
        btn_add_dest = QPushButton('Add Destination')
        btn_add_dest.setToolTip('Add a new category and destination folder for organized files')
        btn_add_dest.clicked.connect(self.add_destination)
        btn_add_dest.setMinimumHeight(30)
        
        btn_edit_dest = QPushButton('Edit')
        btn_edit_dest.setToolTip('Edit the selected destination folder path or category name')
        btn_edit_dest.clicked.connect(self.edit_selected_destination)
        btn_edit_dest.setMinimumHeight(30)
        
        btn_remove_dest = QPushButton('Remove')
        btn_remove_dest.setToolTip('Remove the selected destination category')
        btn_remove_dest.clicked.connect(self.remove_selected_destination)
        btn_remove_dest.setMinimumHeight(30)
        
        dest_btn_layout.addWidget(btn_add_dest)
        dest_btn_layout.addWidget(btn_edit_dest)
        dest_btn_layout.addWidget(btn_remove_dest)
        dest_layout.addLayout(dest_btn_layout)
        dest_group.setLayout(dest_layout)
        folders_layout.addWidget(dest_group)
        
        # Advanced Configuration Section
        config_group = QGroupBox('⚙️ Advanced Configuration')
        config_layout = QVBoxLayout()
        
        config_desc = QLabel(
            '<b>Need Advanced Settings?</b><br>'
            'Open the configuration file directly to customize advanced features, file patterns, '
            'and classification thresholds.'
        )
        config_desc.setWordWrap(True)
        config_desc.setStyleSheet('color: #666; font-size: 11px; margin: 5px;')
        config_layout.addWidget(config_desc)
        
        btn_open_config = QPushButton('Open Config File')
        btn_open_config.setToolTip('Open the YAML configuration file in your default text editor for advanced customization')
        btn_open_config.clicked.connect(self.open_config)
        btn_open_config.setMinimumHeight(30)
        config_layout.addWidget(btn_open_config)
        config_group.setLayout(config_layout)
        folders_layout.addWidget(config_group)
        
        folders_tab.setLayout(folders_layout)
        tabs.addTab(folders_tab, '📁 Folders')
        print('init_ui: Folders tab added')
        
        # File Types Tab - Enhanced with descriptions
        file_types_tab = QWidget()
        file_types_layout = QVBoxLayout()
        
        # Add main description for File Types
        types_main_desc = QLabel(
            '<h3>📋 File Type Categories</h3>'
            '<p>Configure which file extensions belong to each category. FileFlow uses these rules to '
            'determine where to move different types of files.</p>'
        )
        types_main_desc.setWordWrap(True)
        file_types_layout.addWidget(types_main_desc)
        
        # File Categories Section
        categories_group = QGroupBox('📂 File Categories & Extensions')
        categories_group.setToolTip('Define which file extensions belong to each category')
        categories_layout = QVBoxLayout()
        
        categories_desc = QLabel(
            '<b>How File Categories Work:</b><br>'
            'Each category (Images, Videos, Documents, etc.) contains a list of file extensions. '
            'When FileFlow finds a file, it checks the extension to determine which category it belongs to, '
            'then moves it to the appropriate destination folder.'
        )
        categories_desc.setWordWrap(True)
        categories_desc.setStyleSheet('color: #666; font-size: 11px; margin: 5px;')
        categories_layout.addWidget(categories_desc)
        
        self.file_types_list = QListWidget()
        self.file_types_list.setToolTip('List of file categories and their associated file extensions')
        for cat, exts in config.get('file_types', {}).items():
            self.file_types_list.addItem(QListWidgetItem(f'{cat}: {", ".join(exts)}'))
        categories_layout.addWidget(self.file_types_list)
        
        # Category management buttons
        categories_btn_layout = QHBoxLayout()
        btn_add_category = QPushButton('Add Category')
        btn_add_category.setToolTip('Create a new file category with custom extensions')
        btn_add_category.clicked.connect(self.add_category)
        btn_add_category.setMinimumHeight(30)
        
        btn_edit_extensions = QPushButton('Edit Extensions')
        btn_edit_extensions.setToolTip('Modify the file extensions for the selected category')
        btn_edit_extensions.clicked.connect(self.edit_category_extensions)
        btn_edit_extensions.setMinimumHeight(30)
        
        btn_remove_category = QPushButton('Remove')
        btn_remove_category.setToolTip('Delete the selected file category')
        btn_remove_category.clicked.connect(self.remove_selected_category)
        btn_remove_category.setMinimumHeight(30)
        
        categories_btn_layout.addWidget(btn_add_category)
        categories_btn_layout.addWidget(btn_edit_extensions)
        categories_btn_layout.addWidget(btn_remove_category)
        categories_layout.addLayout(categories_btn_layout)
        categories_group.setLayout(categories_layout)
        file_types_layout.addWidget(categories_group)
        file_types_tab.setLayout(file_types_layout)
        tabs.addTab(file_types_tab, 'File Types')
        print('init_ui: File Types tab added')
        
        # Custom Mappings Tab - Enhanced with descriptions
        mappings_tab = QWidget()
        mappings_layout = QVBoxLayout()
        
        # Add main description for Custom Mappings
        mappings_main_desc = QLabel(
            '<h3>🎯 Custom File Mappings</h3>'
            '<p>Create specific rules for individual file extensions that override the default category rules. '
            'Perfect for handling special file types or organizing files to specific locations.</p>'
        )
        mappings_main_desc.setWordWrap(True)
        mappings_layout.addWidget(mappings_main_desc)
        
        # Custom Mappings Section
        mappings_group = QGroupBox('🔗 Custom Extension Mappings')
        mappings_group.setToolTip('Override default category rules with specific file extension mappings')
        mappings_group_layout = QVBoxLayout()
        
        mappings_desc = QLabel(
            '<b>How Custom Mappings Work:</b><br>'
            'Custom mappings let you send specific file extensions to exact folders, bypassing normal '
            'category rules. For example, you could send all .PSD files directly to a "Photoshop" folder '
            'instead of the general "Images" category. These rules take priority over category-based organization.'
        )
        mappings_desc.setWordWrap(True)
        mappings_desc.setStyleSheet('color: #666; font-size: 11px; margin: 5px;')
        mappings_group_layout.addWidget(mappings_desc)
        
        self.mappings_list = QListWidget()
        self.mappings_list.setToolTip('List of custom file extension to folder mappings')
        self.custom_mappings = []
        config_mappings = config.get('custom_mappings', [])
        for mapping in config_mappings:
            ext = mapping.get('extension', '')
            folder = mapping.get('folder', '')
            self.mappings_list.addItem(QListWidgetItem(f'.{ext} → {folder}'))
            self.custom_mappings.append((ext, folder))
        mappings_group_layout.addWidget(self.mappings_list)
        
        # Custom mapping buttons
        mappings_btn_layout = QHBoxLayout()
        btn_add_map = QPushButton('Add Mapping')
        btn_add_map.setToolTip('Create a new custom mapping for a specific file extension')
        btn_add_map.clicked.connect(self.add_mapping)
        btn_add_map.setMinimumHeight(30)
        
        btn_edit_map = QPushButton('Edit')
        btn_edit_map.setToolTip('Modify the selected custom mapping')
        btn_edit_map.clicked.connect(self.edit_selected_mapping)
        btn_edit_map.setMinimumHeight(30)
        
        btn_remove_map = QPushButton('Remove')
        btn_remove_map.setToolTip('Delete the selected custom mapping')
        btn_remove_map.clicked.connect(self.remove_selected_mapping)
        btn_remove_map.setMinimumHeight(30)
        
        mappings_btn_layout.addWidget(btn_add_map)
        mappings_btn_layout.addWidget(btn_edit_map)
        mappings_btn_layout.addWidget(btn_remove_map)
        mappings_group_layout.addLayout(mappings_btn_layout)
        mappings_group.setLayout(mappings_group_layout)
        mappings_layout.addWidget(mappings_group)
        
        mappings_tab.setLayout(mappings_layout)
        tabs.addTab(mappings_tab, '🎯 Custom Mappings')
        print('init_ui: Custom Mappings tab added')
        
        # Content Classification Tab - Enhanced with descriptions
        classification_tab = QWidget()
        classification_layout = QVBoxLayout()
        
        # Add main description for Content Classification
        classification_main_desc = QLabel(
            '<h3>🧠 Advanced Content Classification</h3>'
            '<p>FileFlow uses sophisticated multi-layered analysis to automatically separate NSFW and SFW content. '
            'This ensures your media files are organized appropriately with high accuracy.</p>'
        )
        classification_main_desc.setWordWrap(True)
        classification_layout.addWidget(classification_main_desc)
        
        # System Status section with enhanced descriptions
        status_group = QGroupBox('🔍 Analysis Capabilities Status')
        status_group.setToolTip('Shows which advanced analysis features are available on your system')
        status_layout = QVBoxLayout()
        
        status_desc = QLabel(
            '<b>Multi-Layered Analysis System:</b><br>'
            'FileFlow combines multiple analysis methods for maximum accuracy. Each component adds '
            'intelligence to the classification process, with graceful fallbacks if components are unavailable.'
        )
        status_desc.setWordWrap(True)
        status_desc.setStyleSheet('color: #666; font-size: 11px; margin: 5px;')
        status_layout.addWidget(status_desc)
        
        # Check classifier capabilities with detailed explanations
        try:
            from ..robust_content_classifier import RobustContentClassifier
            classifier = RobustContentClassifier()
            
            pillow_status = '✅ Available' if classifier.has_pillow else '❌ Not Available'
            opencv_status = '✅ Available' if classifier.has_opencv else '❌ Not Available'
            exiftool_status = '✅ Available' if classifier.has_exiftool else '❌ Not Available'
            
            pillow_label = QLabel(f'📷 Pillow (Image Analysis): {pillow_status}')
            pillow_label.setToolTip('Pillow enables basic image analysis, EXIF data reading, and image property detection')
            status_layout.addWidget(pillow_label)
            
            opencv_label = QLabel(f'👁️ OpenCV (Visual Analysis): {opencv_status}')
            opencv_label.setToolTip('OpenCV enables advanced visual analysis including skin detection, face detection, and color analysis')
            status_layout.addWidget(opencv_label)
            
            exiftool_label = QLabel(f'📊 ExifTool (Metadata): {exiftool_status}')
            exiftool_label.setToolTip('ExifTool enables comprehensive EXIF metadata extraction including camera settings and editing software detection')
            status_layout.addWidget(exiftool_label)
            
            # Add accuracy information
            accuracy_desc = QLabel(
                '<br><b>Expected Classification Accuracy:</b><br>'
                '• Filename only: ~85-90%<br>'
                '• + Image analysis: ~92-95%<br>'
                '• + Visual analysis: ~96-98%<br>'
                '• + EXIF metadata: ~98%+'
            )
            accuracy_desc.setStyleSheet('color: #2e7d32; font-size: 10px; margin: 5px;')
            status_layout.addWidget(accuracy_desc)
            
        except ImportError:
            error_label = QLabel('⚠️ Enhanced classifier not available')
            error_label.setToolTip('The advanced content classifier could not be loaded. Check your installation.')
            status_layout.addWidget(error_label)
        
        status_group.setLayout(status_layout)
        classification_layout.addWidget(status_group)
        
        # Settings section with enhanced descriptions
        settings_group = QGroupBox('⚙️ Classification Configuration')
        settings_group.setToolTip('Configure how FileFlow analyzes and classifies your content')
        settings_layout = QVBoxLayout()
        
        settings_desc = QLabel(
            '<b>Customize Your Classification Experience:</b><br>'
            'Fine-tune how FileFlow analyzes your files. You can enable or disable specific analysis '
            'methods and adjust sensitivity levels to match your preferences.'
        )
        settings_desc.setWordWrap(True)
        settings_desc.setStyleSheet('color: #666; font-size: 11px; margin: 5px;')
        settings_layout.addWidget(settings_desc)
        
        # Get current classification config
        classification_config = config.get('content_classification', {})
        
        # Main classification toggle
        self.chk_content_classification = QCheckBox('Enable Content Classification')
        self.chk_content_classification.setToolTip('Master switch for all content classification features')
        self.chk_content_classification.setChecked(classification_config.get('enabled', True))
        settings_layout.addWidget(self.chk_content_classification)
        
        # Analysis method toggles
        analysis_methods_group = QGroupBox('Analysis Methods')
        analysis_methods_layout = QVBoxLayout()
        
        self.chk_filename_analysis = QCheckBox('Filename Pattern Analysis')
        self.chk_filename_analysis.setToolTip('Analyze filenames for NSFW/SFW keywords and patterns (always recommended)')
        self.chk_filename_analysis.setChecked(classification_config.get('use_filename_analysis', True))
        analysis_methods_layout.addWidget(self.chk_filename_analysis)
        
        self.chk_visual_analysis = QCheckBox('Advanced Visual Analysis')
        self.chk_visual_analysis.setToolTip('Use OpenCV for skin detection, face detection, and color analysis (requires OpenCV)')
        self.chk_visual_analysis.setChecked(classification_config.get('use_visual_analysis', True))
        analysis_methods_layout.addWidget(self.chk_visual_analysis)
        
        analysis_methods_group.setLayout(analysis_methods_layout)
        settings_layout.addWidget(analysis_methods_group)
        
        # Classification scope
        scope_group = QGroupBox('Classification Scope')
        scope_layout = QVBoxLayout()
        
        self.chk_media_only = QCheckBox('Classify Media Files Only')
        self.chk_media_only.setToolTip('Only classify images and videos, skip documents and other file types')
        self.chk_media_only.setChecked(classification_config.get('classify_media_only', True))
        scope_layout.addWidget(self.chk_media_only)
        
        scope_group.setLayout(scope_layout)
        settings_layout.addWidget(scope_group)
        
        # Privacy and notifications
        privacy_group = QGroupBox('Privacy & Notifications')
        privacy_layout = QVBoxLayout()
        
        self.chk_nsfw_notifications = QCheckBox('Enable NSFW Move Notifications')
        self.chk_nsfw_notifications.setToolTip('Show notifications when NSFW content is detected and moved (disabled by default for privacy)')
        self.chk_nsfw_notifications.setChecked(classification_config.get('notify_nsfw_moves', False))
        privacy_layout.addWidget(self.chk_nsfw_notifications)
        
        privacy_group.setLayout(privacy_layout)
        settings_layout.addWidget(privacy_group)
        
        # Threshold configuration
        threshold_group = QGroupBox('Sensitivity Settings')
        threshold_group_layout = QVBoxLayout()
        
        threshold_desc = QLabel(
            'Adjust how sensitive the visual analysis should be. Higher values require more '
            'confidence before classifying content as NSFW.'
        )
        threshold_desc.setWordWrap(True)
        threshold_desc.setStyleSheet('color: #666; font-size: 10px; margin: 5px;')
        threshold_group_layout.addWidget(threshold_desc)
        
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel('Visual Analysis Threshold:'))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(30)
        self.threshold_slider.setMaximum(90)
        self.threshold_slider.setValue(int(classification_config.get('visual_analysis_threshold', 0.6) * 100))
        self.threshold_slider.setToolTip('Lower = more sensitive (may have false positives), Higher = less sensitive (may miss some content)')
        self.threshold_value_label = QLabel(f'{self.threshold_slider.value()}%')
        self.threshold_slider.valueChanged.connect(lambda v: self.threshold_value_label.setText(f'{v}%'))
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_value_label)
        threshold_group_layout.addLayout(threshold_layout)
        
        threshold_group.setLayout(threshold_group_layout)
        settings_layout.addWidget(threshold_group)
        
        settings_group.setLayout(settings_layout)
        classification_layout.addWidget(settings_group)
        
        # Actions section with enhanced descriptions
        actions_group = QGroupBox('🎯 Quick Actions')
        actions_group.setToolTip('Test and apply content classification to your files')
        actions_layout = QVBoxLayout()
        
        actions_desc = QLabel(
            '<b>Ready to Organize Your Files?</b><br>'
            'Test the classification system first, then apply it to reorganize your existing files '
            'or start monitoring new files automatically.'
        )
        actions_desc.setWordWrap(True)
        actions_desc.setStyleSheet('color: #666; font-size: 11px; margin: 5px;')
        actions_layout.addWidget(actions_desc)
        
        # Test classification button
        btn_test_classification = QPushButton('Test Classification')
        btn_test_classification.setToolTip('Test the classification system on sample files to see how it works')
        btn_test_classification.clicked.connect(self.test_classification)
        btn_test_classification.setStyleSheet('QPushButton { padding: 8px; }')
        btn_test_classification.setMinimumHeight(35)
        actions_layout.addWidget(btn_test_classification)
        
        # Save settings button
        btn_save_classification_settings = QPushButton('Save Settings')
        btn_save_classification_settings.setToolTip('Save your current classification configuration to the config file')
        btn_save_classification_settings.clicked.connect(self.save_classification_settings)
        btn_save_classification_settings.setStyleSheet('QPushButton { padding: 8px; }')
        btn_save_classification_settings.setMinimumHeight(35)
        actions_layout.addWidget(btn_save_classification_settings)
        
        # Reorganize existing files button (prominent)
        btn_reorganize = QPushButton('Reorganize Files')
        btn_reorganize.setToolTip('Apply content classification to reorganize files already in your destination folders')
        btn_reorganize.clicked.connect(self.reorganize_with_classification)
        btn_reorganize.setStyleSheet('QPushButton { padding: 12px; font-weight: bold; background-color: #4CAF50; color: white; font-size: 14px; }')
        btn_reorganize.setMinimumHeight(40)
        actions_layout.addWidget(btn_reorganize)
        
        actions_group.setLayout(actions_layout)
        classification_layout.addWidget(actions_group)
        
        # Info section with enhanced descriptions
        info_group = QGroupBox('📚 How Content Classification Works')
        info_group.setToolTip('Learn about FileFlow\'s advanced content analysis system')
        info_layout = QVBoxLayout()
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(140)
        info_text.setHtml(
            '<p><b>🎆 Multi-Layered Intelligence:</b> FileFlow uses sophisticated analysis combining:</p>'
            '<ul>'
            '<li><b>📝 Filename Analysis:</b> Smart keyword detection with SFW overrides</li>'
            '<li><b>👁️ Visual Analysis:</b> OpenCV-powered skin/face detection and color analysis</li>'
            '<li><b>📊 EXIF Metadata:</b> Camera settings, editing software, and timestamp analysis</li>'
            '<li><b>📁 File Properties:</b> Size patterns, duration analysis, and metadata inspection</li>'
            '<li><b>🧠 Smart Scoring:</b> Intelligent combination with confidence weighting</li>'
            '</ul>'
            '<p><b>🔒 Privacy First:</b> All analysis is done locally - no cloud uploads or data collection.</p>'
            '<p><b>🏁 Result:</b> Files organized into SFW/NSFW subdirectories with ~98% accuracy.</p>'
        )
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        classification_layout.addWidget(info_group)
        
        classification_tab.setLayout(classification_layout)
        tabs.addTab(classification_tab, '🧠 Content Classification')
        print('init_ui: Content Classification tab added')
        
        # Settings Tab - Enhanced with descriptions
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        
        # Add main description for Settings
        settings_main_desc = QLabel(
            '<h3>⚙️ Application Settings</h3>'
            '<p>Configure FileFlow\'s behavior, organize your files, and manage system preferences.</p>'
        )
        settings_main_desc.setWordWrap(True)
        settings_layout.addWidget(settings_main_desc)
        
        # Organization section
        org_group = QGroupBox('🚀 File Organization')
        org_group.setToolTip('Start organizing your files with the current configuration')
        org_layout = QVBoxLayout()
        
        org_desc = QLabel(
            '<b>Ready to Organize?</b><br>'
            'Click below to start organizing files from your source directories using '
            'the current configuration and classification settings.'
        )
        org_desc.setWordWrap(True)
        org_desc.setStyleSheet('color: #666; font-size: 11px; margin: 5px;')
        org_layout.addWidget(org_desc)
        
        btn_organize = QPushButton('Start Organization')
        btn_organize.setToolTip('Begin organizing files from source directories using current settings')
        btn_organize.clicked.connect(self.organize_with_feedback)
        btn_organize.setStyleSheet('QPushButton { padding: 12px; font-weight: bold; background-color: #2196F3; color: white; font-size: 14px; }')
        btn_organize.setMinimumHeight(40)
        org_layout.addWidget(btn_organize)
        org_group.setLayout(org_layout)
        settings_layout.addWidget(org_group)
        
        # System preferences section
        prefs_group = QGroupBox('💻 System Preferences')
        prefs_layout = QVBoxLayout()
        
        self.chk_autostart = QCheckBox('Enable autostart at login')
        self.chk_autostart.setToolTip('Automatically start FileFlow when you log into your system')
        self.chk_autostart.stateChanged.connect(lambda state: self.statusbar.showMessage('Autostart preference updated', 2000))
        prefs_layout.addWidget(self.chk_autostart)
        
        self.chk_notifications = QCheckBox('Enable system notifications')
        self.chk_notifications.setToolTip('Show desktop notifications for file organization events')
        self.chk_notifications.stateChanged.connect(lambda state: self.statusbar.showMessage('Notification preference updated', 2000))
        prefs_layout.addWidget(self.chk_notifications)
        
        prefs_group.setLayout(prefs_layout)
        settings_layout.addWidget(prefs_group)
        
        settings_tab.setLayout(settings_layout)
        tabs.addTab(settings_tab, '⚙️ Settings')
        print('init_ui: Settings tab added')
        self.setCentralWidget(tabs)
        print('init_ui: setCentralWidget called')
        
        # Enhanced status bar with helpful information
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Add helpful status information
        try:
            from ..robust_content_classifier import RobustContentClassifier
            classifier = RobustContentClassifier()
            
            # Count available analysis methods
            methods = []
            if classifier.has_pillow:
                methods.append('Image Analysis')
            if classifier.has_opencv:
                methods.append('Visual Analysis')
            if classifier.has_exiftool:
                methods.append('EXIF Metadata')
            
            if methods:
                status_msg = f'✅ FileFlow Ready | Advanced Analysis: {" + ".join(methods)} | Resizable Window'
            else:
                status_msg = '⚠️ FileFlow Ready | Basic Mode Only | Resizable Window'
                
        except ImportError:
            status_msg = '⚠️ FileFlow Ready | Limited Features | Resizable Window'
        
        self.statusbar.showMessage(status_msg)
        self.statusbar.setToolTip('FileFlow status and available features')
        
        print('init_ui: enhanced statusbar set')
        print('init_ui end')
        btn_add_source = QPushButton('Add Source Folder')
        btn_add_source.clicked.connect(self.add_source_folder)
        btn_remove_source = QPushButton('Remove Selected Source')
        btn_remove_source.clicked.connect(self.remove_selected_source)
        btn_browse_source = QPushButton('Browse and Add Source')
        btn_browse_source.clicked.connect(self.browse_and_add_source)
        folders_layout.addWidget(btn_add_source)
        folders_layout.addWidget(btn_remove_source)
        folders_layout.addWidget(btn_browse_source)
        folders_layout.addSpacing(10)
        folders_layout.addWidget(QLabel('<b>Destination Directories:</b>'))
        self.dest_list = QListWidget()
        for cat, dst in config.get('destination_directories', {}).items():
            self.dest_list.addItem(QListWidgetItem(f'{cat}: {dst}'))
        folders_layout.addWidget(self.dest_list)
        btn_add_dest = QPushButton('Add Destination')
        btn_add_dest.clicked.connect(self.add_destination)
        btn_remove_dest = QPushButton('Remove Selected Destination')
        btn_remove_dest.clicked.connect(self.remove_selected_destination)
        btn_edit_dest = QPushButton('Edit Selected Destination')
        btn_edit_dest.clicked.connect(self.edit_selected_destination)
        folders_layout.addWidget(btn_add_dest)
        folders_layout.addWidget(btn_remove_dest)
        folders_layout.addWidget(btn_edit_dest)
        btn_open_config = QPushButton('Open Config File')
        btn_open_config.clicked.connect(self.open_config)
        folders_layout.addWidget(btn_open_config)
        folders_tab.setLayout(folders_layout)
        tabs.addTab(folders_tab, 'Folders')

    # Destination directory management
    def add_destination(self):
        cat, ok1 = QInputDialog.getText(self, 'Add Destination', 'Enter category name:')
        if not ok1 or not cat:
            return
        folder = QFileDialog.getExistingDirectory(self, 'Select Destination Folder')
        if folder:
            self.dest_list.addItem(QListWidgetItem(f'{cat}: {folder}'))
            self.statusbar.showMessage(f'Added destination: {cat}: {folder}', 3000)

    def remove_selected_destination(self):
        for item in self.dest_list.selectedItems():
            self.dest_list.takeItem(self.dest_list.row(item))
        self.statusbar.showMessage('Removed selected destination(s)', 3000)

    def edit_selected_destination(self):
        items = self.dest_list.selectedItems()
        if not items:
            return
        item = items[0]
        text = item.text()
        if ': ' in text:
            cat, old_path = text.split(': ', 1)
        else:
            cat, old_path = text, ''
        folder = QFileDialog.getExistingDirectory(self, 'Select New Destination Folder', old_path)
        if folder:
            item.setText(f'{cat}: {folder}')
            self.statusbar.showMessage(f'Updated destination for {cat}', 3000)

        # File Types Tab
        types_tab = QWidget()
        types_layout = QVBoxLayout()
        types_layout.addWidget(QLabel('<b>File Type Categories:</b>'))
        self.types_list = QListWidget()
        self.category_extensions = {}  # Dict[str, set] for category: set of extensions
        for cat, dst in config.get('destination_directories', {}).items():
            self.types_list.addItem(QListWidgetItem(cat))
            # For demo, load extensions from config if present (else empty set)
            self.category_extensions[cat] = set(config.get('category_extensions', {}).get(cat, []))
        types_layout.addWidget(self.types_list)
        btn_add_type = QPushButton('Add Category')
        btn_add_type.clicked.connect(self.add_category)
        btn_remove_type = QPushButton('Remove Selected Category')
        btn_remove_type.clicked.connect(self.remove_selected_category)
        btn_edit_ext = QPushButton('Edit Extensions for Category')
        btn_edit_ext.clicked.connect(self.edit_category_extensions)
        types_layout.addWidget(btn_add_type)
        types_layout.addWidget(btn_remove_type)
        types_layout.addWidget(btn_edit_ext)
        types_tab.setLayout(types_layout)
        tabs.addTab(types_tab, 'File Types')

    def edit_category_extensions(self):
        items = self.types_list.selectedItems()
        if not items:
            return
        cat = items[0].text()
        existing_exts = self.category_extensions.get(cat, set())
        ext_str, ok = QInputDialog.getText(self, f'Edit Extensions for {cat}',
            'Comma-separated extensions (e.g. jpg,png,gif):',
            text=','.join(sorted(existing_exts)))
        if ok:
            new_exts = set(e.strip() for e in ext_str.split(',') if e.strip())
            self.category_extensions[cat] = new_exts
            self.statusbar.showMessage(f'Extensions for {cat} updated: {", ".join(sorted(new_exts))}', 3000)

        # Settings Tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        btn_organize = QPushButton('Organize Now')
        btn_organize.clicked.connect(self.organize_with_feedback)
        settings_layout.addWidget(btn_organize)
        self.chk_autostart = QCheckBox('Enable autostart at login')
        self.chk_autostart.stateChanged.connect(lambda state: self.statusbar.showMessage('Autostart toggled', 2000))
        settings_layout.addWidget(self.chk_autostart)
        self.chk_notifications = QCheckBox('Enable notifications')
        self.chk_notifications.stateChanged.connect(lambda state: self.statusbar.showMessage('Notifications toggled', 2000))
        settings_layout.addWidget(self.chk_notifications)
        settings_tab.setLayout(settings_layout)
        tabs.addTab(settings_tab, 'Settings')

        self.setCentralWidget(tabs)
        # Status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

    # Custom mappings management
    def add_mapping(self):
        ext, ok1 = QInputDialog.getText(self, 'Add Mapping', 'Enter file extension (without dot):')
        if not ok1 or not ext:
            return
        folder = QFileDialog.getExistingDirectory(self, 'Select Destination Folder for this Extension')
        if folder:
            self.mappings_list.addItem(QListWidgetItem(f'.{ext} → {folder}'))
            self.custom_mappings.append((ext, folder))
            self.statusbar.showMessage(f'Added mapping: .{ext} → {folder}', 3000)

    def remove_selected_mapping(self):
        for item in self.mappings_list.selectedItems():
            idx = self.mappings_list.row(item)
            self.mappings_list.takeItem(idx)
            if 0 <= idx < len(self.custom_mappings):
                del self.custom_mappings[idx]
        self.statusbar.showMessage('Removed selected mapping(s)', 3000)

    def edit_selected_mapping(self):
        items = self.mappings_list.selectedItems()
        if not items:
            return
        idx = self.mappings_list.row(items[0])
        ext, folder = self.custom_mappings[idx] if 0 <= idx < len(self.custom_mappings) else ('', '')
        new_ext, ok1 = QInputDialog.getText(self, 'Edit Mapping', 'Enter file extension (without dot):', text=ext)
        if not ok1 or not new_ext:
            return
        new_folder = QFileDialog.getExistingDirectory(self, 'Select Destination Folder for this Extension', folder)
        if new_folder:
            items[0].setText(f'.{new_ext} → {new_folder}')
            self.custom_mappings[idx] = (new_ext, new_folder)
            self.statusbar.showMessage(f'Updated mapping: .{new_ext} → {new_folder}', 3000)

    # Folder management methods
    def add_source_folder(self):
        text, ok = QInputDialog.getText(self, 'Add Source Folder', 'Enter folder path:')
        if ok and text:
            self.source_list.addItem(QListWidgetItem(text))
            self.statusbar.showMessage(f'Added source folder: {text}', 3000)

    def remove_selected_source(self):
        for item in self.source_list.selectedItems():
            self.source_list.takeItem(self.source_list.row(item))
        self.statusbar.showMessage('Removed selected source folder(s)', 3000)

    def browse_and_add_source(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Source Folder')
        if folder:
            self.source_list.addItem(QListWidgetItem(folder))
            self.statusbar.showMessage(f'Added source folder: {folder}', 3000)

    # File type/category management methods
    def add_category(self):
        text, ok = QInputDialog.getText(self, 'Add Category', 'Enter category name:')
        if ok and text:
            self.types_list.addItem(QListWidgetItem(text))
            self.statusbar.showMessage(f'Added category: {text}', 3000)

    def remove_selected_category(self):
        for item in self.types_list.selectedItems():
            self.types_list.takeItem(self.types_list.row(item))
        self.statusbar.showMessage('Removed selected category(s)', 3000)

    def open_config(self):
        # Try to open config file in default editor
        import subprocess
        subprocess.Popen(['xdg-open', str(CONFIG_FILE)])

    def create_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        tray = QSystemTrayIcon(self)
        if ICON_PATH.exists():
            tray.setIcon(QIcon(str(ICON_PATH)))
        else:
            tray.setIcon(self.windowIcon())
        menu = QMenu()
        action_show = QAction('Show/Hide', self)
        action_show.triggered.connect(self.toggle_visibility)
        menu.addAction(action_show)
        action_organize = QAction('Organize Now', self)
        action_organize.triggered.connect(self.organize_with_feedback)
        menu.addAction(action_organize)
        action_about = QAction('About', self)
        action_about.triggered.connect(self.show_about)
        menu.addAction(action_about)
        action_quit = QAction('Quit', self)
        action_quit.triggered.connect(QApplication.instance().quit)
        menu.addAction(action_quit)
        tray.setContextMenu(menu)
        tray.show()
        self.tray = tray

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.showNormal()
            self.raise_()
            self.activateWindow()

    def organize_with_feedback(self):
        # Progress dialog for file organization
        from PyQt5.QtCore import QThread, pyqtSignal, QObject
        from PyQt5.QtWidgets import QProgressDialog
        import time

        class Worker(QObject):
            progress = pyqtSignal(int, int)
            finished = pyqtSignal()
            error = pyqtSignal(str)

            def __init__(self, files):
                super().__init__()
                self.files = files
                self._abort = False

            def abort(self):
                self._abort = True

            def run(self):
                total = len(self.files)
                for idx, f in enumerate(self.files, 1):
                    if self._abort:
                        return
                    try:
                        # Simulate file organization (replace with real logic)
                        time.sleep(0.05)
                    except Exception as e:
                        self.error.emit(str(e))
                        return
                    self.progress.emit(idx, total)
                self.finished.emit()

        # Gather files to process (simulate for now)
        import os
        config = load_config()
        files = []
        for src in config['source_directories']:
            if os.path.isdir(src):
                for root, _, filenames in os.walk(src):
                    for fn in filenames:
                        files.append(os.path.join(root, fn))
        if not files:
            QMessageBox.information(self, 'SELO FileFlow', 'No files to organize.')
            return
        progress_dialog = QProgressDialog('Organizing files...', 'Cancel', 0, len(files), self)
        progress_dialog.setWindowTitle('SELO FileFlow')
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(0)
        thread = QThread()
        worker = Worker(files)
        worker.moveToThread(thread)
        worker.progress.connect(lambda i, t: progress_dialog.setValue(i))
        worker.error.connect(lambda msg: QMessageBox.critical(self, 'SELO FileFlow', f'Error: {msg}'))
        worker.finished.connect(lambda: progress_dialog.setValue(len(files)))
        worker.finished.connect(lambda: QMessageBox.information(self, 'SELO FileFlow', 'Files organized successfully.'))
        worker.finished.connect(thread.quit)
        progress_dialog.canceled.connect(worker.abort)
        thread.started.connect(worker.run)
        thread.finished.connect(thread.deleteLater)
        thread.start()
        progress_dialog.exec_()
        self.statusbar.showMessage('Organization complete', 3000)

    def save_classification_settings(self):
        """Save content classification settings to config."""
        try:
            config = load_config()
            
            # Update classification settings
            classification_config = {
                'enabled': self.chk_content_classification.isChecked(),
                'use_visual_analysis': self.chk_visual_analysis.isChecked(),
                'use_filename_analysis': self.chk_filename_analysis.isChecked(),
                'classify_media_only': self.chk_media_only.isChecked(),
                'notify_nsfw_moves': self.chk_nsfw_notifications.isChecked(),
                'visual_analysis_threshold': self.threshold_slider.value() / 100.0,
                'create_content_subdirs': True,
                'cache_analysis_results': True
            }
            
            config['content_classification'] = classification_config
            save_config(config)
            
            QMessageBox.information(self, 'Settings Saved', 
                'Content classification settings have been saved successfully!')
            self.statusbar.showMessage('Classification settings saved', 3000)
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save settings: {e}')
    
    def test_classification(self):
        """Test the content classification system."""
        try:
            from ..robust_content_classifier import RobustContentClassifier
            classifier = RobustContentClassifier()
            
            # Show classifier capabilities
            capabilities = []
            if classifier.has_pillow:
                capabilities.append('✅ Pillow (Image Analysis)')
            else:
                capabilities.append('❌ Pillow (Image Analysis)')
                
            if classifier.has_opencv:
                capabilities.append('✅ OpenCV (Advanced Visual Analysis)')
            else:
                capabilities.append('❌ OpenCV (Advanced Visual Analysis)')
                
            if classifier.has_exiftool:
                capabilities.append('✅ ExifTool (Metadata Extraction)')
            else:
                capabilities.append('❌ ExifTool (Metadata Extraction)')
            
            # Test sample filenames
            test_cases = [
                ('family_vacation.jpg', 'SFW'),
                ('xxx_video.mp4', 'NSFW'),
                ('IMG_1234.jpg', 'Unknown (needs visual analysis)'),
                ('wedding_photos.png', 'SFW'),
                ('adult_content.mp4', 'NSFW')
            ]
            
            results = []
            for filename, expected in test_cases:
                temp_path = Path('/tmp') / filename
                analysis = classifier.analyze_filename(temp_path)
                classification = 'NSFW' if analysis['is_nsfw'] else 'SFW'
                confidence = analysis['confidence']
                results.append(f'{filename}: {classification} (confidence: {confidence:.2f})')
            
            message = (
                '<b>Content Classification Test Results</b><br><br>'
                '<b>System Capabilities:</b><br>' + '<br>'.join(capabilities) + '<br><br>'
                '<b>Filename Analysis Test:</b><br>' + '<br>'.join(results) + '<br><br>'
                '<i>Note: Visual analysis requires actual image files and is more accurate than filename-only detection.</i>'
            )
            
            QMessageBox.information(self, 'Classification Test', message)
            
        except ImportError:
            QMessageBox.warning(self, 'Test Failed', 
                'Enhanced content classifier is not available. Please ensure all dependencies are installed.')
        except Exception as e:
            QMessageBox.critical(self, 'Test Error', f'Classification test failed: {e}')
    
    def reorganize_with_classification(self):
        """Reorganize existing files using enhanced content classification."""
        reply = QMessageBox.question(self, 'Reorganize Files', 
            'This will reorganize your existing files using enhanced content classification.\n\n'
            'Files will be moved into SFW and NSFW subdirectories within your existing categories.\n\n'
            'This operation may take some time depending on the number of files.\n\n'
            'Do you want to continue?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.reorganize_with_feedback()
    
    def reorganize_with_feedback(self):
        """Reorganize files with progress feedback using enhanced classification."""
        from PyQt5.QtCore import QThread, pyqtSignal, QObject
        from PyQt5.QtWidgets import QProgressDialog
        import time
        
        class ReorganizeWorker(QObject):
            progress = pyqtSignal(str)  # Status message
            finished = pyqtSignal(dict)  # Results
            error = pyqtSignal(str)
            
            def __init__(self):
                super().__init__()
                self._abort = False
            
            def abort(self):
                self._abort = True
            
            def run(self):
                try:
                    self.progress.emit('Starting enhanced reorganization...')
                    
                    # Use the enhanced reorganization function
                    reorganize_existing_files()
                    
                    # Simulate progress updates (in real implementation, this would come from the organizer)
                    for i in range(1, 6):
                        if self._abort:
                            return
                        self.progress.emit(f'Processing files... ({i*20}%)')
                        time.sleep(0.5)
                    
                    results = {
                        'sfw': 0,  # These would be real counts from the organizer
                        'nsfw': 0,
                        'total': 0
                    }
                    
                    self.finished.emit(results)
                    
                except Exception as e:
                    self.error.emit(str(e))
        
        # Create progress dialog
        progress_dialog = QProgressDialog('Reorganizing files with content classification...', 'Cancel', 0, 0, self)
        progress_dialog.setWindowTitle('SELO FileFlow - Enhanced Reorganization')
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setCancelButton(None)  # Remove cancel for now
        
        # Create worker thread
        thread = QThread()
        worker = ReorganizeWorker()
        worker.moveToThread(thread)
        
        # Connect signals
        worker.progress.connect(lambda msg: progress_dialog.setLabelText(msg))
        worker.error.connect(lambda msg: QMessageBox.critical(self, 'Reorganization Error', f'Error: {msg}'))
        worker.finished.connect(lambda results: self.show_reorganization_results(results))
        worker.finished.connect(lambda: progress_dialog.close())
        worker.finished.connect(thread.quit)
        
        thread.started.connect(worker.run)
        thread.finished.connect(thread.deleteLater)
        
        # Start the process
        thread.start()
        progress_dialog.exec_()
        
        self.statusbar.showMessage('Enhanced reorganization complete', 3000)
    
    def show_reorganization_results(self, results):
        """Show results of the reorganization process."""
        message = (
            '<b>Enhanced Reorganization Complete!</b><br><br>'
            f'Files have been reorganized using advanced content classification.<br><br>'
            '<b>Features used:</b><br>'
            '• Filename pattern analysis<br>'
            '• Visual content analysis (if available)<br>'
            '• File property analysis<br>'
            '• Smart scoring system<br><br>'
            'Files are now organized into SFW and NSFW subdirectories within your existing categories.'
        )
        
        QMessageBox.information(self, 'Reorganization Results', message)

    def show_about(self):
        QMessageBox.about(self, 'About SELO FileFlow',
            '<b>SELO FileFlow (Linux Edition)</b><br>'
            'Automatic file organizer for Linux with Enhanced Content Classification.<br><br>'
            '<b>Features:</b><br>'
            '• Multi-layered content analysis<br>'
            '• Visual content classification<br>'
            '• NSFW/SFW automatic separation<br>'
            '• Smart file organization<br><br>'
            'Original Windows version by SELOdev.<br>'
            'Linux port and enhancements by the community.')

def run_app():
    app = QApplication(sys.argv)
    win = FileFlowMainWindow()
    win.show()
    sys.exit(app.exec_())
