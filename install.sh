#!/bin/bash

# FileFlow Comprehensive Installer Script
# Automatically installs all dependencies and sets up FileFlow for optimal performance

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="FileFlow"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_EXEC="python3"
PIP_EXEC="python3 -m pip"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  FileFlow Installation Script  ${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_os() {
    print_step "Detecting operating system..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get >/dev/null 2>&1; then
            OS="ubuntu"
            PACKAGE_MANAGER="apt"
            print_success "Detected Ubuntu/Debian-based system"
        elif command -v yum >/dev/null 2>&1; then
            OS="centos"
            PACKAGE_MANAGER="yum"
            print_success "Detected CentOS/RHEL-based system"
        elif command -v pacman >/dev/null 2>&1; then
            OS="arch"
            PACKAGE_MANAGER="pacman"
            print_success "Detected Arch-based system"
        else
            print_warning "Unknown Linux distribution. Manual installation may be required."
            OS="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
        print_success "Detected macOS"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

check_python() {
    print_step "Checking Python installation..."
    
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 8 ]]; then
        print_error "Python $PYTHON_VERSION detected. FileFlow requires Python 3.8 or higher."
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION detected (compatible)"
}

install_system_dependencies() {
    print_step "Installing system dependencies..."
    
    case $OS in
        "ubuntu")
            print_step "Updating package list..."
            sudo apt update
            
            print_step "Installing ExifTool for EXIF metadata analysis..."
            sudo apt install -y libimage-exiftool-perl
            
            print_step "Installing FFmpeg for video analysis..."
            sudo apt install -y ffmpeg
            
            print_step "Installing additional dependencies..."
            sudo apt install -y python3-pip python3-dev python3-venv
            ;;
            
        "centos")
            print_step "Installing EPEL repository..."
            sudo yum install -y epel-release
            
            print_step "Installing ExifTool..."
            sudo yum install -y perl-Image-ExifTool
            
            print_step "Installing FFmpeg..."
            sudo yum install -y ffmpeg ffmpeg-devel
            
            print_step "Installing Python development tools..."
            sudo yum install -y python3-pip python3-devel
            ;;
            
        "arch")
            print_step "Installing ExifTool..."
            sudo pacman -S --noconfirm perl-image-exiftool
            
            print_step "Installing FFmpeg..."
            sudo pacman -S --noconfirm ffmpeg
            
            print_step "Installing Python tools..."
            sudo pacman -S --noconfirm python-pip
            ;;
            
        "macos")
            if ! command -v brew >/dev/null 2>&1; then
                print_error "Homebrew is not installed. Please install Homebrew first:"
                print_error "https://brew.sh/"
                exit 1
            fi
            
            print_step "Installing ExifTool..."
            brew install exiftool
            
            print_step "Installing FFmpeg..."
            brew install ffmpeg
            ;;
            
        *)
            print_warning "Unknown OS. Please install the following manually:"
            print_warning "- ExifTool (libimage-exiftool-perl)"
            print_warning "- FFmpeg"
            print_warning "- Python 3.8+ with pip"
            ;;
    esac
    
    print_success "System dependencies installed"
}

install_python_dependencies() {
    print_step "Installing Python dependencies..."
    
    # Upgrade pip first
    print_step "Upgrading pip..."
    $PIP_EXEC install --user --upgrade pip
    
    # Install requirements
    if [[ -f "$SCRIPT_DIR/requirements.txt" ]]; then
        print_step "Installing from requirements.txt..."
        $PIP_EXEC install --user -r "$SCRIPT_DIR/requirements.txt"
    else
        print_error "requirements.txt not found in $SCRIPT_DIR"
        exit 1
    fi
    
    print_success "Python dependencies installed"
}

verify_installation() {
    print_step "Verifying installation..."
    
    cd "$SCRIPT_DIR"
    
    if [[ -f "verify_installation.py" ]]; then
        print_step "Running installation verification script..."
        if python3 verify_installation.py; then
            print_success "Installation verification passed!"
        else
            print_warning "Some verification checks failed. FileFlow will still work with reduced functionality."
        fi
    else
        print_step "Manual verification..."
        
        # Check Python imports
        python3 -c "
import sys
try:
    import yaml
    import watchdog
    import PyQt5
    import cv2
    import PIL
    import numpy
    print('✅ All core Python dependencies available')
except ImportError as e:
    print(f'❌ Missing Python dependency: {e}')
    sys.exit(1)
"
        
        # Check system tools
        if command -v exiftool >/dev/null 2>&1; then
            echo "✅ ExifTool available: $(exiftool -ver)"
        else
            echo "⚠️  ExifTool not found (EXIF analysis will be limited)"
        fi
        
        if command -v ffmpeg >/dev/null 2>&1; then
            echo "✅ FFmpeg available: $(ffmpeg -version 2>&1 | head -1)"
        else
            echo "⚠️  FFmpeg not found (video analysis will be limited)"
        fi
    fi
}

setup_desktop_integration() {
    print_step "Setting up desktop integration..."
    
    # Create desktop entry
    DESKTOP_DIR="$HOME/.local/share/applications"
    DESKTOP_FILE="$DESKTOP_DIR/fileflow.desktop"
    
    mkdir -p "$DESKTOP_DIR"
    
    cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=FileFlow
Comment=Advanced Media Content Classification & Organization
Exec=$PYTHON_EXEC -m fileflow.main --ui
Icon=folder-organize
Terminal=false
Categories=Utility;FileManager;
Keywords=file;organize;sort;media;classification;
StartupNotify=true
Path=$SCRIPT_DIR
EOF
    
    chmod +x "$DESKTOP_FILE"
    print_success "Desktop entry created at $DESKTOP_FILE"
    
    # Ask about autostart
    echo ""
    read -p "Would you like FileFlow to start automatically at login? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        AUTOSTART_DIR="$HOME/.config/autostart"
        AUTOSTART_FILE="$AUTOSTART_DIR/fileflow.desktop"
        
        mkdir -p "$AUTOSTART_DIR"
        cp "$DESKTOP_FILE" "$AUTOSTART_FILE"
        
        # Add autostart specific settings
        echo "X-GNOME-Autostart-enabled=true" >> "$AUTOSTART_FILE"
        echo "Hidden=false" >> "$AUTOSTART_FILE"
        
        print_success "Autostart enabled"
    fi
}

create_config_directory() {
    print_step "Creating configuration directory..."
    
    CONFIG_DIR="$HOME/.config/fileflow"
    mkdir -p "$CONFIG_DIR"
    
    if [[ ! -f "$CONFIG_DIR/config.yaml" ]]; then
        print_step "Creating default configuration..."
        cat > "$CONFIG_DIR/config.yaml" <<EOF
# FileFlow Configuration
# Edit this file to customize your file organization

source_directories:
  - "$HOME/Downloads"

destination_directories:
  Images: "$HOME/Pictures/Organized"
  Videos: "$HOME/Videos/Organized"
  Documents: "$HOME/Documents/Organized"

# Enhanced content classification settings
content_classification:
  enabled: true
  visual_analysis: true
  filename_analysis: true
  media_only: true
  visual_threshold: 0.5
  nsfw_notifications: false

# File type mappings
file_types:
  Images: [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"]
  Videos: [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".m4v"]
  Documents: [".pdf", ".doc", ".docx", ".txt", ".rtf"]

# Performance settings
performance:
  batch_size: 100
  cache_enabled: true
  parallel_workers: 2
EOF
        print_success "Default configuration created at $CONFIG_DIR/config.yaml"
    else
        print_success "Configuration directory already exists"
    fi
}

show_completion_message() {
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}   Installation Complete! 🎉   ${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo -e "${BLUE}FileFlow has been successfully installed with:${NC}"
    echo "✅ Advanced content classification capabilities"
    echo "✅ Multi-layered NSFW/SFW detection"
    echo "✅ EXIF metadata analysis"
    echo "✅ Visual content analysis"
    echo "✅ Desktop integration"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Launch FileFlow: ${YELLOW}python3 -m fileflow.main --ui${NC}"
    echo "2. Configure your source and destination folders"
    echo "3. Test classification on sample files"
    echo "4. Run organization on your media collection"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo "• User Guide: $SCRIPT_DIR/USER_GUIDE.md"
    echo "• Installation Guide: $SCRIPT_DIR/INSTALLATION.md"
    echo "• Configuration: $HOME/.config/fileflow/config.yaml"
    echo ""
    echo -e "${BLUE}Support:${NC}"
    echo "• Run verification: ${YELLOW}python3 verify_installation.py${NC}"
    echo "• Check logs: $HOME/.cache/fileflow/logs/"
    echo "• Report issues: GitHub Issues"
    echo ""
}

# Main installation process
main() {
    print_header
    
    echo "This script will install FileFlow and all its dependencies."
    echo "You may be prompted for your password to install system packages."
    echo ""
    read -p "Continue with installation? (Y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    
    check_os
    check_python
    install_system_dependencies
    install_python_dependencies
    verify_installation
    create_config_directory
    setup_desktop_integration
    show_completion_message
    
    echo -e "${GREEN}Ready to launch FileFlow!${NC}"
    echo ""
    read -p "Would you like to launch FileFlow now? (Y/n): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        cd "$SCRIPT_DIR"
        python3 -m fileflow.main --ui
    fi
}

# Run main function
main "$@"
