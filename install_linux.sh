#!/bin/bash

# FileFlow Linux Installation Script
# This script helps set up FileFlow on Linux systems

echo "=== FileFlow Linux Installation ==="
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✓ pip3 found"

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo "Warning: Cannot detect Linux distribution. Proceeding with generic installation."
    DISTRO="unknown"
fi

echo "✓ Detected distribution: $DISTRO"
echo

# Install system dependencies based on distribution
echo "Installing system dependencies..."

case $DISTRO in
    ubuntu|debian)
        echo "Installing packages for Ubuntu/Debian..."
        sudo apt-get update
        sudo apt-get install -y python3-pyqt5 python3-yaml python3-watchdog python3-pip
        ;;
    fedora)
        echo "Installing packages for Fedora..."
        sudo dnf install -y python3-PyQt5 python3-pyyaml python3-watchdog python3-pip
        ;;
    arch|manjaro)
        echo "Installing packages for Arch/Manjaro..."
        sudo pacman -S --noconfirm python-pyqt5 python-yaml python-watchdog python-pip
        ;;
    opensuse*)
        echo "Installing packages for openSUSE..."
        sudo zypper install -y python3-qt5 python3-PyYAML python3-watchdog python3-pip
        ;;
    *)
        echo "Unknown distribution. Installing via pip only..."
        ;;
esac

echo

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user -r requirements.txt

echo

# Create directories
echo "Creating user directories..."
mkdir -p ~/.config/fileflow
mkdir -p ~/.local/share/fileflow
mkdir -p ~/.cache/fileflow

echo

# Install desktop entry
echo "Installing desktop entry..."
DESKTOP_FILE="$HOME/.local/share/applications/fileflow.desktop"
CURRENT_DIR="$(pwd)"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=FileFlow
GenericName=File Organizer
Comment=Automatically organize downloaded files by type and category
Exec=python3 "$CURRENT_DIR/src/ui_app.py"
Icon=$CURRENT_DIR/resources/icon.png
StartupNotify=true
Terminal=false
Categories=Utility;FileManager;
Keywords=file;organizer;download;automation;
MimeType=inode/directory;
Actions=StartMinimized;

[Desktop Action StartMinimized]
Name=Start Minimized
Exec=python3 "$CURRENT_DIR/src/ui_app.py" --minimized
EOF

chmod +x "$DESKTOP_FILE"

echo "✓ Desktop entry installed to: $DESKTOP_FILE"

# Create launcher script
echo "Creating launcher script..."
LAUNCHER_SCRIPT="$HOME/.local/bin/fileflow"
mkdir -p "$HOME/.local/bin"

cat > "$LAUNCHER_SCRIPT" << EOF
#!/bin/bash
# FileFlow launcher script
cd "$CURRENT_DIR"
python3 src/ui_app.py "\$@"
EOF

chmod +x "$LAUNCHER_SCRIPT"

echo "✓ Launcher script created: $LAUNCHER_SCRIPT"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Adding ~/.local/bin to PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo "Note: You may need to restart your terminal or run 'source ~/.bashrc' for the PATH change to take effect."
fi

echo

# Create default configuration
echo "Creating default configuration..."
CONFIG_FILE="$HOME/.config/fileflow/settings.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << EOF
# FileFlow Configuration
source_directory: "~/Downloads"
organize_existing_files: true
notify_on_move: true

# File type mappings
file_types:
  documents:
    - pdf
    - doc
    - docx
    - txt
    - rtf
  images:
    - jpg
    - jpeg
    - png
    - gif
    - bmp
    - svg
  videos:
    - mp4
    - avi
    - mkv
    - mov
    - wmv
    - flv
  audio:
    - mp3
    - wav
    - flac
    - aac
    - ogg
  archives:
    - zip
    - rar
    - 7z
    - tar
    - gz

# Destination folders
destination_folders:
  documents: "~/Documents/Organized"
  images: "~/Pictures/Organized"
  videos: "~/Videos/Organized"
  audio: "~/Music/Organized"
  archives: "~/Downloads/Archives"
  other: "~/Downloads/Other"
EOF

    echo "✓ Default configuration created: $CONFIG_FILE"
else
    echo "✓ Configuration file already exists: $CONFIG_FILE"
fi

echo

echo "=== Installation Complete! ==="
echo
echo "FileFlow has been successfully installed on your Linux system."
echo
echo "You can now:"
echo "1. Run 'fileflow' from the terminal (after restarting terminal or sourcing ~/.bashrc)"
echo "2. Find FileFlow in your application menu"
echo "3. Run directly with: python3 $CURRENT_DIR/src/ui_app.py"
echo
echo "Configuration file: $CONFIG_FILE"
echo "Edit this file to customize your file organization preferences."
echo
echo "Enjoy organizing your files with FileFlow!"
