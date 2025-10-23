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

check_nodejs() {
    print_step "Checking Node.js installation (for web UI)..."
    
    if ! command -v node >/dev/null 2>&1; then
        print_warning "Node.js is not installed. Web UI will not be available."
        print_warning "To install Node.js, visit: https://nodejs.org/"
        HAS_NODEJS=false
        return
    fi
    
    NODE_VERSION=$(node --version | sed 's/v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
    
    if [[ $NODE_MAJOR -lt 18 ]]; then
        print_warning "Node.js $NODE_VERSION detected. Web UI requires Node.js 18+."
        print_warning "Please upgrade Node.js for web UI support."
        HAS_NODEJS=false
    else
        print_success "Node.js $NODE_VERSION detected (compatible)"
        HAS_NODEJS=true
    fi
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

install_nodejs_dependencies() {
    if [[ "$HAS_NODEJS" != "true" ]]; then
        print_warning "Skipping Node.js dependencies (Node.js not available)"
        return
    fi
    
    print_step "Installing Node.js dependencies for web UI..."
    
    WEB_DIR="$SCRIPT_DIR/web"
    if [[ ! -d "$WEB_DIR" ]]; then
        print_warning "Web UI directory not found. Skipping web dependencies."
        return
    fi
    
    cd "$WEB_DIR"
    
    if [[ -f "package.json" ]]; then
        print_step "Installing npm packages..."
        npm install --silent
        print_success "Node.js dependencies installed"
    else
        print_warning "package.json not found in $WEB_DIR"
    fi
    
    cd "$SCRIPT_DIR"
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

create_launchers() {
    print_step "Creating launcher scripts..."
    
    # Create desktop UI launcher
    cat > "$SCRIPT_DIR/launch-desktop.sh" <<EOF
#!/bin/bash
cd "$SCRIPT_DIR"
python3 -m fileflow.main --ui
EOF
    chmod +x "$SCRIPT_DIR/launch-desktop.sh"
    print_success "Desktop launcher created: ./launch-desktop.sh"
    
    # Create web UI launcher if Node.js is available
    if [[ "$HAS_NODEJS" == "true" ]]; then
        cat > "$SCRIPT_DIR/launch-web.sh" <<EOF
#!/bin/bash
cd "$SCRIPT_DIR"

echo "🚀 Starting FileFlow Web UI..."
echo "================================"
echo ""
echo "Services:"
echo "  • API Server: http://localhost:9001"
echo "  • Web UI: http://localhost:5173"
echo "  • API Docs: http://localhost:9001/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start API server in background
python3 -m fileflow.main --web --host 127.0.0.1 --port 9001 &
API_PID=\$!

# Give API time to start
sleep 2

# Start frontend
cd web
npm run dev &
FRONTEND_PID=\$!

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill \$API_PID \$FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
EOF
        chmod +x "$SCRIPT_DIR/launch-web.sh"
        print_success "Web launcher created: ./launch-web.sh"
    fi
    
    # Create CLI helper
    cat > "$SCRIPT_DIR/fileflow" <<EOF
#!/bin/bash
cd "$SCRIPT_DIR"
python3 -m fileflow.main "\$@"
EOF
    chmod +x "$SCRIPT_DIR/fileflow"
    print_success "CLI helper created: ./fileflow"
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
    if [[ "$HAS_NODEJS" == "true" ]]; then
        echo "✅ Modern web interface"
    fi
    echo ""
    echo -e "${BLUE}Quick Start:${NC}"
    if [[ "$HAS_NODEJS" == "true" ]]; then
        echo "• Launch Web UI: ${YELLOW}./launch-web.sh${NC}"
        echo "  Access at: ${YELLOW}http://localhost:5173${NC}"
        echo ""
    fi
    echo "• Launch Desktop UI: ${YELLOW}./launch-desktop.sh${NC}"
    echo "• CLI Usage: ${YELLOW}./fileflow --help${NC}"
    echo ""
    echo -e "${BLUE}Command Examples:${NC}"
    echo "• Organize once: ${YELLOW}./fileflow --organize-once${NC}"
    echo "• Start watcher: ${YELLOW}./fileflow --watch${NC}"
    echo "• Reorganize with NSFW classification: ${YELLOW}./fileflow --reorganize${NC}"
    echo ""
    echo -e "${BLUE}Configuration:${NC}"
    echo "• Config file: ${YELLOW}$HOME/.config/fileflow/config.yaml${NC}"
    echo "• Or use the web/desktop UI to configure"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    if [[ "$HAS_NODEJS" == "true" ]]; then
        echo "• Web UI Guide: $SCRIPT_DIR/WEB_UI_GUIDE.md"
    fi
    echo "• User Guide: $SCRIPT_DIR/USER_GUIDE.md"
    echo "• Configuration: $SCRIPT_DIR/CONFIGURATION.md"
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
    check_nodejs
    install_system_dependencies
    install_python_dependencies
    install_nodejs_dependencies
    verify_installation
    create_config_directory
    create_launchers
    setup_desktop_integration
    show_completion_message
    
    echo -e "${GREEN}Ready to launch FileFlow!${NC}"
    echo ""
    
    if [[ "$HAS_NODEJS" == "true" ]]; then
        echo "Choose interface:"
        echo "1) Web UI (modern, browser-based)"
        echo "2) Desktop UI (PyQt, native)"
        echo "3) Skip for now"
        read -p "Enter choice (1-3): " -n 1 -r
        echo ""
        
        case $REPLY in
            1)
                cd "$SCRIPT_DIR"
                ./launch-web.sh
                ;;
            2)
                cd "$SCRIPT_DIR"
                python3 -m fileflow.main --ui
                ;;
            *)
                echo "You can launch FileFlow anytime with ./launch-web.sh or ./launch-desktop.sh"
                ;;
        esac
    else
        read -p "Would you like to launch the Desktop UI now? (Y/n): " -n 1 -r
        echo ""
        
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            cd "$SCRIPT_DIR"
            python3 -m fileflow.main --ui
        fi
    fi
}

# Run main function
main "$@"
