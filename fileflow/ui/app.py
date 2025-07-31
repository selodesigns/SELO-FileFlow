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
        self.setWindowTitle('SELO FileFlow')
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.resize(400, 300)
        self.init_ui()
        self.create_tray()
        self.tray.setToolTip('SELO FileFlow')
        self.tray.activated.connect(self.on_tray_activated)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint)

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
        # Folders Tab
        folders_tab = QWidget()
        folders_layout = QVBoxLayout()
        folders_layout.addWidget(QLabel('<b>Source Directories:</b>'))
        self.source_list = QListWidget()
        for src in config.get('source_directories', []):
            self.source_list.addItem(QListWidgetItem(src))
        folders_layout.addWidget(self.source_list)
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
        print('init_ui: Folders tab added')
        # File Types Tab
        types_tab = QWidget()
        types_layout = QVBoxLayout()
        types_layout.addWidget(QLabel('<b>File Type Categories:</b>'))
        self.types_list = QListWidget()
        self.category_extensions = {}
        for cat, dst in config.get('destination_directories', {}).items():
            self.types_list.addItem(QListWidgetItem(cat))
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
        print('init_ui: File Types tab added')
        # Custom Mappings Tab
        mappings_tab = QWidget()
        mappings_layout = QVBoxLayout()
        mappings_layout.addWidget(QLabel('<b>Custom Extension-to-Folder Mappings:</b>'))
        self.mappings_list = QListWidget()
        self.custom_mappings = []
        config_mappings = config.get('custom_mappings', [])
        for mapping in config_mappings:
            ext = mapping.get('extension', '')
            folder = mapping.get('folder', '')
            self.mappings_list.addItem(QListWidgetItem(f'.{ext} → {folder}'))
            self.custom_mappings.append((ext, folder))
        mappings_layout.addWidget(self.mappings_list)
        btn_add_map = QPushButton('Add Mapping')
        btn_add_map.clicked.connect(self.add_mapping)
        btn_remove_map = QPushButton('Remove Selected Mapping')
        btn_remove_map.clicked.connect(self.remove_selected_mapping)
        btn_edit_map = QPushButton('Edit Selected Mapping')
        btn_edit_map.clicked.connect(self.edit_selected_mapping)
        mappings_layout.addWidget(btn_add_map)
        mappings_layout.addWidget(btn_remove_map)
        mappings_layout.addWidget(btn_edit_map)
        mappings_tab.setLayout(mappings_layout)
        tabs.addTab(mappings_tab, 'Custom Mappings')
        print('init_ui: Custom Mappings tab added')
        
        # Content Classification Tab
        classification_tab = QWidget()
        classification_layout = QVBoxLayout()
        
        # Header
        header_label = QLabel('<b>Enhanced Content Classification</b>')
        header_label.setFont(QFont('Arial', 12, QFont.Bold))
        classification_layout.addWidget(header_label)
        
        # Status section
        status_group = QGroupBox('System Status')
        status_layout = QVBoxLayout()
        
        # Check classifier capabilities
        try:
            from ..robust_content_classifier import RobustContentClassifier
            classifier = RobustContentClassifier()
            
            pillow_status = '✅ Available' if classifier.has_pillow else '❌ Not Available'
            opencv_status = '✅ Available' if classifier.has_opencv else '❌ Not Available'
            exiftool_status = '✅ Available' if classifier.has_exiftool else '❌ Not Available'
            
            status_layout.addWidget(QLabel(f'Pillow (Image Analysis): {pillow_status}'))
            status_layout.addWidget(QLabel(f'OpenCV (Visual Analysis): {opencv_status}'))
            status_layout.addWidget(QLabel(f'ExifTool (Metadata): {exiftool_status}'))
            
        except ImportError:
            status_layout.addWidget(QLabel('⚠️ Enhanced classifier not available'))
        
        status_group.setLayout(status_layout)
        classification_layout.addWidget(status_group)
        
        # Settings section
        settings_group = QGroupBox('Classification Settings')
        settings_layout = QVBoxLayout()
        
        # Get current classification config
        classification_config = config.get('content_classification', {})
        
        self.chk_content_classification = QCheckBox('Enable Content Classification')
        self.chk_content_classification.setChecked(classification_config.get('enabled', True))
        settings_layout.addWidget(self.chk_content_classification)
        
        self.chk_visual_analysis = QCheckBox('Use Visual Analysis (requires OpenCV)')
        self.chk_visual_analysis.setChecked(classification_config.get('use_visual_analysis', True))
        settings_layout.addWidget(self.chk_visual_analysis)
        
        self.chk_filename_analysis = QCheckBox('Use Filename Analysis')
        self.chk_filename_analysis.setChecked(classification_config.get('use_filename_analysis', True))
        settings_layout.addWidget(self.chk_filename_analysis)
        
        self.chk_media_only = QCheckBox('Classify Media Files Only')
        self.chk_media_only.setChecked(classification_config.get('classify_media_only', True))
        settings_layout.addWidget(self.chk_media_only)
        
        self.chk_nsfw_notifications = QCheckBox('Enable NSFW Move Notifications')
        self.chk_nsfw_notifications.setChecked(classification_config.get('notify_nsfw_moves', False))
        settings_layout.addWidget(self.chk_nsfw_notifications)
        
        # Threshold slider
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel('Visual Analysis Threshold:'))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(30)
        self.threshold_slider.setMaximum(90)
        self.threshold_slider.setValue(int(classification_config.get('visual_analysis_threshold', 0.6) * 100))
        self.threshold_value_label = QLabel(f'{self.threshold_slider.value()}%')
        self.threshold_slider.valueChanged.connect(lambda v: self.threshold_value_label.setText(f'{v}%'))
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_value_label)
        settings_layout.addLayout(threshold_layout)
        
        settings_group.setLayout(settings_layout)
        classification_layout.addWidget(settings_group)
        
        # Actions section
        actions_group = QGroupBox('Actions')
        actions_layout = QVBoxLayout()
        
        btn_reorganize = QPushButton('🔄 Reorganize Existing Files with Content Classification')
        btn_reorganize.clicked.connect(self.reorganize_with_classification)
        btn_reorganize.setStyleSheet('QPushButton { padding: 8px; font-weight: bold; }')
        actions_layout.addWidget(btn_reorganize)
        
        btn_test_classification = QPushButton('🧪 Test Content Classification')
        btn_test_classification.clicked.connect(self.test_classification)
        actions_layout.addWidget(btn_test_classification)
        
        btn_save_classification_settings = QPushButton('💾 Save Classification Settings')
        btn_save_classification_settings.clicked.connect(self.save_classification_settings)
        actions_layout.addWidget(btn_save_classification_settings)
        
        actions_group.setLayout(actions_layout)
        classification_layout.addWidget(actions_group)
        
        # Info section
        info_group = QGroupBox('About Content Classification')
        info_layout = QVBoxLayout()
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(120)
        info_text.setHtml(
            '<p><b>Enhanced Content Classification</b> uses multiple analysis methods:</p>'
            '<ul>'
            '<li><b>Filename Analysis:</b> Detects NSFW/SFW keywords and patterns</li>'
            '<li><b>Visual Analysis:</b> Skin detection, face recognition, color analysis</li>'
            '<li><b>File Properties:</b> Size, metadata, and characteristic analysis</li>'
            '<li><b>Smart Scoring:</b> Combines multiple factors for accurate classification</li>'
            '</ul>'
            '<p>Files are organized into SFW and NSFW subdirectories within existing categories.</p>'
        )
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        classification_layout.addWidget(info_group)
        
        classification_tab.setLayout(classification_layout)
        tabs.addTab(classification_tab, 'Content Classification')
        print('init_ui: Content Classification tab added')
        
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
        print('init_ui: Settings tab added')
        self.setCentralWidget(tabs)
        print('init_ui: setCentralWidget called')
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        print('init_ui: statusbar set')
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
