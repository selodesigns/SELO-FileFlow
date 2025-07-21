# SELO FileFlow

A **cross-platform** file management solution that automatically organizes files downloaded from web browsers into appropriate directories based on file types. Now fully compatible with **Linux**, **Windows**, and **macOS**!

## ✨ Features

- **Cross-Platform**: Works on Linux, Windows, and macOS
- **Real-time Monitoring**: Watches your downloads folder for new files
- **Smart Organization**: Automatically categorizes files into:
  - 📄 Documents (PDF, DOC, TXT, etc.)
  - 🖼️ Images (JPG, PNG, GIF, etc.)
  - 🎥 Videos (MP4, AVI, MKV, etc.)
  - 🎵 Audio (MP3, WAV, FLAC, etc.)
  - 📦 Archives (ZIP, RAR, 7Z, etc.)
  - 💾 Software and other files
- **Modern GUI**: PyQt5-based interface with system tray support
- **Privacy-Focused**: Handles sensitive content appropriately
- **Configurable**: Customizable paths, file type mappings, and rules
- **Background Operation**: Runs as a service/daemon
- **Autostart Support**: Optional startup integration

## 🚀 Quick Start (Fresh GitHub Install)

### Linux
```bash
git clone https://github.com/your-username/SELO-FileFlow.git
cd SELO-FileFlow

# Option 1: Simple launcher (recommended)
python3 fileflow.py

# Option 2: Automatic setup
chmod +x install_linux.sh
./install_linux.sh
```

### Windows
```cmd
git clone https://github.com/your-username/SELO-FileFlow.git
cd SELO-FileFlow
pip install -r requirements.txt
python fileflow.py
```

## 📋 Requirements

### Minimum Requirements
- **Python 3.8+** (tested on 3.8-3.12)
- **PyQt5** (for GUI)
- **watchdog** (for file monitoring)
- **PyYAML** (for configuration)

### Platform Support
- ✅ **Linux** (Ubuntu, Fedora, Arch, openSUSE, etc.)
- ✅ **Windows** (10/11)
- ✅ **macOS** (10.14+)

## 💻 Installation

### Quick Install (Any Platform)
```bash
# Clone the repository
git clone https://github.com/your-username/SELO-FileFlow.git
cd SELO-FileFlow

# Install dependencies
pip3 install --user -r requirements.txt

# Run immediately
python3 fileflow.py
```

### Linux (Recommended)
```bash
# Automatic installation with system integration
chmod +x install_linux.sh
./install_linux.sh

# Or install system packages first
sudo apt-get install python3-pyqt5 python3-yaml python3-watchdog  # Ubuntu/Debian
sudo dnf install python3-PyQt5 python3-pyyaml python3-watchdog     # Fedora
sudo pacman -S python-pyqt5 python-yaml python-watchdog            # Arch
```

### Windows
```cmd
# Install Python dependencies
pip install -r requirements.txt

# Run the application
python fileflow.py
```

### Standalone Executable (Windows)
1. Download the latest installer from releases
2. Run `SELO-FileFlow-Setup-x.x.x.exe`
3. Launch from Start menu or desktop shortcut

## 🎯 Usage

### GUI Mode (Default)
```bash
# Simple launcher
python3 fileflow.py

# Or direct launch
python3 src/ui_app.py

# Start minimized to tray
python3 fileflow.py --minimized
```

### CLI Mode (Background)
```bash
# CLI mode
python3 fileflow.py --cli

# Or direct launch
python3 src/main.py

# Process files once and exit
python3 src/main.py --process-once

# Run as daemon
python3 src/main.py --daemon
```

## ⚙️ Configuration

FileFlow automatically creates configuration files in platform-appropriate locations:

- **Linux**: `~/.config/fileflow/settings.yaml`
- **Windows**: `%APPDATA%\SELOdev\FileFlow\config\settings.yaml`
- **Development**: `./config/settings.yaml`

### Customization Options
- Source directory (downloads folder)
- Destination directories for each file type
- Custom file type mappings
- NSFW content handling
- Notification preferences
- Autostart settings
- Logging configuration

## 📚 Documentation

- **[Linux Installation Guide](README_LINUX.md)** - Detailed Linux setup instructions
- **Configuration Examples** - See `config/settings.yaml`
- **Troubleshooting** - Check the Linux guide for common issues

## 🔒 Privacy & Security

- **Local Processing**: All file organization happens on your machine
- **No External Connections**: No data sent to external servers
- **NSFW Support**: Appropriate handling of sensitive content
- **User Control**: Full control over file destinations and rules

## License

MIT
