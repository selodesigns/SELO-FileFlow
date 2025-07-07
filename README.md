# SELO FileFlow (Linux Edition)

![SELO FileFlow Logo](fileflow/data/icons/fileflow.png)

**SELO FileFlow** is an open-source, Linux-native file organizer and automation tool. It automatically monitors and sorts your downloaded files into categorized folders, keeping your directories tidy and organized with minimal effort. Inspired by the original SELO FileFlow for Windows, this version is rebuilt from the ground up for seamless Linux desktop integration.

---

## Features

- **Automatic file organization**: Monitors your Downloads (or any folder) and sorts files by type (images, documents, music, videos, archives, software, etc.)
- **Customizable rules**: Easily edit the config to add or change categories and destinations
- **Linux-native notifications**: Get notified when files are moved
- **System tray integration**: Quick access to organize, show/hide/minimize, About, and quit
- **Enhanced PyQt5 GUI**: Clean interface, in-app feedback (success/error dialogs), About dialog, and improved user experience
- **Settings tab**: Toggle autostart and notifications from within the app
- **Progress dialog**: See progress and cancel file organization from the UI
- **Minimize to tray**: App hides to tray on close/minimize, and restores on tray icon click or menu
- **Robust to config errors**: App always loads, even if config is missing or broken
- **Autostart support**: Optionally launch at login via `.desktop` entry
- **Logging**: All actions and errors are logged for troubleshooting
- **Open source**: MIT-licensed and ready for community contributions

---

## Screenshots

> _Add your screenshots here!_
> _Tip: Use the Settings tab and progress dialog to show off the new features!_

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/SELOFileFlowLinux.git
cd SELOFileFlowLinux/selo-fileflow
```

### 2. Install Dependencies

> **Important:** To avoid issues with mismatched Python and pip environments, always use:
> ```bash
> python3 -m pip install -r requirements.txt
> ```
> instead of just `pip install ...`. This ensures dependencies are installed for the correct Python version (`python3`).

### 3. (Optional) Enable Autostart
```bash
bash scripts/install.sh
```
This will add SELO FileFlow to your desktop environment's autostart.

---

## Enhanced Linux UI

- **Tabbed interface:** Organize your folders, file types, and custom mappings from dedicated tabs.
- **Settings tab:** Easily enable/disable autostart and notifications.
- **Progress dialog:** See real-time progress and cancel organization jobs.
- **In-app feedback:** Success and error dialogs are shown in the GUI when organizing files.
- **Tray icon minimize/restore:** Closing or minimizing the main window hides it to the system tray. Click the tray icon or use the tray menu to restore.
- **About dialog:** Access app info and credits from the tray menu.
- **Improved user experience:** All main actions are accessible from the tray or main window.

---

## Usage

### Launch the GUI
```bash
python3 -m fileflow.main --ui
```

### Organize Files Once (CLI)
```bash
python3 -m fileflow.main --organize-once
```

### Run as a Watcher Daemon (CLI)
```bash
python3 -m fileflow.main --watch
```

---

## Configuration

- The configuration file is stored at:  
  `~/.config/selo-fileflow/config.yaml`
- Edit this file to change source/destination directories, file type rules, and notification/autostart settings.
- You can also open the config file from the GUI.

---

## Logging

- Log files are stored at:  
  `~/.local/share/selo-fileflow/logs/fileflow.log`
- Check these logs for details on actions taken and any errors.

---

## Contributing

Pull requests, bug reports, and feature suggestions are welcome!
- Fork the repo and open a PR
- File issues for bugs or feature requests
- See `tests/` for unit tests; run with `pytest`

---

## License

MIT License

---

## Credits

- Original Windows version by SELOdev
- Linux port and enhancements by [Your Name]
- Built with Python, PyQt5, watchdog, and PyYAML

---

**Enjoy a cleaner, more organized Linux desktop with SELO FileFlow!**
