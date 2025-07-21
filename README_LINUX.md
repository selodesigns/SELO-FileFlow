# FileFlow - Linux Installation Guide

FileFlow is a cross-platform file organization tool that automatically sorts your downloaded files by type and category. This guide covers installation and setup on Linux systems.

## Quick Start (Fresh GitHub Install)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/SELO-FileFlow.git
cd SELO-FileFlow
```

### 2. Install Dependencies

#### Option A: Automatic Installation (Recommended)
```bash
chmod +x install_linux.sh
./install_linux.sh
```

#### Option B: Manual Installation

**Install system packages:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-pyqt5 python3-yaml python3-watchdog python3-pip

# Fedora
sudo dnf install python3-PyQt5 python3-pyyaml python3-watchdog python3-pip

# Arch/Manjaro
sudo pacman -S python-pyqt5 python-yaml python-watchdog python-pip

# openSUSE
sudo zypper install python3-qt5 python3-PyYAML python3-watchdog python3-pip
```

**Install Python dependencies:**
```bash
pip3 install --user -r requirements.txt
```

### 3. Run the Application

#### GUI Version (Recommended)
```bash
python3 src/ui_app.py
```

#### CLI Version (Background monitoring)
```bash
python3 src/main.py
```

## Features

- **Cross-Platform**: Works on Linux, Windows, and macOS
- **GUI Interface**: Easy-to-use PyQt5-based interface
- **File Monitoring**: Real-time monitoring of download directories
- **Customizable Rules**: Define custom file organization rules
- **System Tray**: Minimizes to system tray for background operation
- **Autostart**: Optional startup integration
- **Privacy-Focused**: Handles sensitive content appropriately

## Configuration

The application creates a default configuration file at:
- **Linux**: `~/.config/fileflow/settings.yaml` (XDG compliant)
- **Development**: `./config/settings.yaml`

### Default File Organization

| File Type | Extensions | Default Destination |
|-----------|------------|-------------------|
| Documents | pdf, doc, docx, txt, rtf | ~/Documents/Organized |
| Images | jpg, jpeg, png, gif, bmp, svg | ~/Pictures/Organized |
| Videos | mp4, avi, mkv, mov, wmv, flv | ~/Videos/Organized |
| Audio | mp3, wav, flac, aac, ogg | ~/Music/Organized |
| Archives | zip, rar, 7z, tar, gz | ~/Downloads/Archives |
| Other | All other files | ~/Downloads/Other |

## Usage

### GUI Mode
1. Launch with `python3 src/ui_app.py`
2. Configure source and destination folders
3. Set up file type mappings
4. Enable autostart if desired
5. Click "Start Monitoring" or minimize to tray

### CLI Mode
```bash
# Monitor continuously
python3 src/main.py

# Process existing files once and exit
python3 src/main.py --process-once

# Run as daemon
python3 src/main.py --daemon

# Custom config file
python3 src/main.py --config /path/to/config.yaml
```

### Command Line Options

#### GUI (`ui_app.py`)
- `--config CONFIG`: Path to configuration file
- `--minimized`: Start minimized to system tray

#### CLI (`main.py`)
- `--config CONFIG`: Path to configuration file
- `--daemon`: Run as daemon
- `--process-once`: Process files once and exit

## Linux-Specific Features

### XDG Base Directory Support
FileFlow follows Linux standards:
- Config: `~/.config/fileflow/`
- Data: `~/.local/share/fileflow/`
- Cache: `~/.cache/fileflow/`
- Logs: `~/.local/share/fileflow/logs/`

### Desktop Integration
- Creates `.desktop` file for application menu
- System tray integration with most desktop environments
- Autostart support via `~/.config/autostart/`

### Supported Desktop Environments
- GNOME
- KDE Plasma
- XFCE
- MATE
- Cinnamon
- Most other freedesktop.org compliant environments

## Troubleshooting

### Common Issues

**ImportError: No module named 'PyQt5'**
```bash
# Install PyQt5 via system package manager (recommended)
sudo apt-get install python3-pyqt5  # Ubuntu/Debian
# OR via pip
pip3 install --user PyQt5
```

**Permission denied errors**
- Ensure you have write permissions to destination folders
- Check that source directory exists and is readable

**System tray not working**
- Install system tray support for your desktop environment
- For GNOME: Install TopIcons Plus extension
- For others: Usually works out of the box

**Application doesn't start**
- Check Python version: `python3 --version` (requires 3.8+)
- Verify all dependencies are installed
- Check logs in `~/.local/share/fileflow/logs/`

### Getting Help

1. Check the logs: `~/.local/share/fileflow/logs/fileflow.log`
2. Run with verbose output: `python3 src/ui_app.py` (check terminal output)
3. Verify configuration: `~/.config/fileflow/settings.yaml`

## Development

### Running from Source
```bash
# Clone and enter directory
git clone https://github.com/your-username/SELO-FileFlow.git
cd SELO-FileFlow

# Install dependencies
pip3 install --user -r requirements.txt

# Run directly
python3 src/ui_app.py
```

### Project Structure
```
SELO-FileFlow/
├── src/
│   ├── main.py              # CLI entry point
│   ├── ui_app.py            # GUI entry point
│   └── modules/
│       ├── config_manager.py    # Configuration handling
│       ├── file_handler.py      # File processing logic
│       ├── ui_manager.py        # GUI implementation
│       ├── direct_fixes.py      # Cross-platform fixes
│       └── user_dirs.py         # Directory management
├── resources/
│   ├── icon.png             # Linux icon
│   ├── icon.ico             # Windows icon
│   └── fileflow.desktop     # Desktop entry template
├── config/
│   └── settings.yaml        # Default configuration
├── requirements.txt         # Python dependencies
├── install_linux.sh         # Linux installation script
└── README_LINUX.md         # This file
```

## Privacy and Security

FileFlow is designed with privacy in mind:
- All processing happens locally on your machine
- No data is sent to external servers
- Configuration and logs are stored in standard user directories
- Supports organizing sensitive content with appropriate privacy measures

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
