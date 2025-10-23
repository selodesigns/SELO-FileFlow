#!/bin/bash
# FileFlow Release Builder
# Creates distribution archives for direct download

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VERSION=${1:-"dev"}
PLATFORM=${2:-"all"}
BUILD_DIR="build"
DIST_DIR="dist"
PROJECT_NAME="fileflow"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   FileFlow Release Builder             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Version:${NC} $VERSION"
echo -e "${GREEN}Platform:${NC} $PLATFORM"
echo ""

# Validate version format
if [[ ! $VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] && [[ $VERSION != "dev" ]]; then
    echo -e "${RED}Error: Version must be in format vX.Y.Z (e.g., v1.0.0)${NC}"
    exit 1
fi

# Clean previous builds
clean_build() {
    echo -e "${YELLOW}→${NC} Cleaning previous builds..."
    cd "$PROJECT_ROOT"
    rm -rf "$BUILD_DIR" "$DIST_DIR"
    mkdir -p "$BUILD_DIR" "$DIST_DIR"
}

# Build web UI
build_web() {
    echo -e "${YELLOW}→${NC} Building web UI (production)..."
    cd "$PROJECT_ROOT/web"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}  Installing Node.js dependencies...${NC}"
        npm install
    fi
    
    # Build production bundle
    echo -e "${YELLOW}  Building production bundle...${NC}"
    npm run build
    
    echo -e "${GREEN}✓${NC} Web UI built successfully"
}

# Create platform-specific archive
create_archive() {
    local platform=$1
    local archive_name="${PROJECT_NAME}-${VERSION}-${platform}"
    local build_path="$PROJECT_ROOT/$BUILD_DIR/$archive_name"
    
    echo -e "${YELLOW}→${NC} Creating $platform archive..."
    
    # Create build directory structure
    mkdir -p "$build_path"
    
    # Copy core files
    echo -e "${YELLOW}  Copying core files...${NC}"
    cp -r "$PROJECT_ROOT/fileflow" "$build_path/"
    cp -r "$PROJECT_ROOT/web/dist" "$build_path/web/"
    cp -r "$PROJECT_ROOT/scripts" "$build_path/"
    cp "$PROJECT_ROOT/requirements.txt" "$build_path/"
    cp "$PROJECT_ROOT/README.md" "$build_path/"
    cp "$PROJECT_ROOT/QUICKSTART.md" "$build_path/"
    cp "$PROJECT_ROOT/USER_GUIDE.md" "$build_path/"
    cp "$PROJECT_ROOT/WEB_UI_GUIDE.md" "$build_path/"
    
    # Copy LICENSE if exists
    if [ -f "$PROJECT_ROOT/LICENSE" ]; then
        cp "$PROJECT_ROOT/LICENSE" "$build_path/"
    fi
    
    # Copy platform-specific files
    case $platform in
        linux)
            cp "$PROJECT_ROOT/install.sh" "$build_path/"
            cp "$PROJECT_ROOT/INSTALLATION.md" "$build_path/"
            
            # Create launcher scripts
            cat > "$build_path/launch-web.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
./scripts/launch-web.sh
EOF
            
            cat > "$build_path/launch-desktop.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
python -m fileflow.gui.main
EOF
            
            cat > "$build_path/fileflow" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
python -m fileflow.cli "$@"
EOF
            
            chmod +x "$build_path/install.sh"
            chmod +x "$build_path/launch-web.sh"
            chmod +x "$build_path/launch-desktop.sh"
            chmod +x "$build_path/fileflow"
            ;;
            
        macos)
            cp "$PROJECT_ROOT/install.sh" "$build_path/"
            cp "$PROJECT_ROOT/INSTALLATION.md" "$build_path/"
            
            # Same launcher scripts as Linux (macOS uses bash)
            cat > "$build_path/launch-web.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
./scripts/launch-web.sh
EOF
            
            cat > "$build_path/launch-desktop.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
python -m fileflow.gui.main
EOF
            
            cat > "$build_path/fileflow" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
python -m fileflow.cli "$@"
EOF
            
            chmod +x "$build_path/install.sh"
            chmod +x "$build_path/launch-web.sh"
            chmod +x "$build_path/launch-desktop.sh"
            chmod +x "$build_path/fileflow"
            ;;
            
        windows)
            cp "$PROJECT_ROOT/install.bat" "$build_path/"
            cp "$PROJECT_ROOT/install.ps1" "$build_path/"
            cp "$PROJECT_ROOT/WINDOWS.md" "$build_path/"
            
            # Create Windows launcher scripts
            cat > "$build_path/launch-web.bat" << 'EOF'
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat 2>nul
call scripts\launch-web.bat
EOF
            
            cat > "$build_path/launch-desktop.bat" << 'EOF'
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat 2>nul
python -m fileflow.gui.main
EOF
            
            cat > "$build_path/fileflow.bat" << 'EOF'
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat 2>nul
python -m fileflow.cli %*
EOF
            ;;
    esac
    
    # Create INSTALL.txt with quick instructions
    cat > "$build_path/INSTALL.txt" << EOF
FileFlow ${VERSION} - Installation Instructions

1. INSTALL DEPENDENCIES:
   
   Linux/macOS:
   $ ./install.sh
   
   Windows:
   > install.bat
   OR
   > powershell -ExecutionPolicy Bypass -File install.ps1

2. LAUNCH:
   
   Web UI (Recommended):
   $ ./launch-web.sh        # Linux/macOS
   > launch-web.bat         # Windows
   Then open: http://localhost:5173
   
   Desktop UI:
   $ ./launch-desktop.sh    # Linux/macOS
   > launch-desktop.bat     # Windows
   
   CLI:
   $ ./fileflow --help      # Linux/macOS
   > fileflow.bat --help    # Windows

For detailed instructions, see:
- QUICKSTART.md - Quick start guide
- README.md - Full documentation
- WINDOWS.md - Windows-specific guide (Windows only)

Support: https://github.com/selodesigns/SELO-FileFlow/issues
EOF
    
    # Remove development files
    find "$build_path" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$build_path" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find "$build_path" -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
    find "$build_path" -name "*.pyc" -delete 2>/dev/null || true
    find "$build_path" -name ".DS_Store" -delete 2>/dev/null || true
    
    # Create archive
    cd "$PROJECT_ROOT/$BUILD_DIR"
    if [ "$platform" = "windows" ]; then
        echo -e "${YELLOW}  Creating ZIP archive...${NC}"
        zip -r "../$DIST_DIR/${archive_name}.zip" "$archive_name" > /dev/null
        echo -e "${GREEN}✓${NC} Created: ${archive_name}.zip"
    else
        echo -e "${YELLOW}  Creating TAR.GZ archive...${NC}"
        tar -czf "../$DIST_DIR/${archive_name}.tar.gz" "$archive_name"
        echo -e "${GREEN}✓${NC} Created: ${archive_name}.tar.gz"
    fi
}

# Create source archive (all platforms)
create_source_archive() {
    echo -e "${YELLOW}→${NC} Creating source archive..."
    
    cd "$PROJECT_ROOT"
    local archive_name="${PROJECT_NAME}-${VERSION}-source"
    
    # Create temporary directory
    local temp_dir="$BUILD_DIR/$archive_name"
    mkdir -p "$temp_dir"
    
    # Copy source files (excluding build artifacts)
    rsync -a \
        --exclude 'build/' \
        --exclude 'dist/' \
        --exclude 'venv/' \
        --exclude '.git/' \
        --exclude '__pycache__/' \
        --exclude '*.pyc' \
        --exclude '.DS_Store' \
        --exclude 'node_modules/' \
        --exclude 'web/dist/' \
        --exclude '.pytest_cache/' \
        . "$temp_dir/"
    
    # Create archive
    cd "$BUILD_DIR"
    tar -czf "../$DIST_DIR/${archive_name}.tar.gz" "$archive_name"
    
    echo -e "${GREEN}✓${NC} Created: ${archive_name}.tar.gz"
}

# Generate checksums
generate_checksums() {
    echo -e "${YELLOW}→${NC} Generating checksums..."
    
    cd "$PROJECT_ROOT/$DIST_DIR"
    
    # Create checksums file
    {
        echo "# SHA256 checksums for FileFlow $VERSION"
        echo "# Generated on $(date)"
        echo ""
        
        for file in *; do
            if [ -f "$file" ] && [ "$file" != "checksums.txt" ]; then
                sha256sum "$file"
            fi
        done
    } > checksums.txt
    
    echo -e "${GREEN}✓${NC} Checksums generated"
}

# Main build process
main() {
    clean_build
    build_web
    
    # Build platform archives
    case $PLATFORM in
        linux)
            create_archive "linux"
            ;;
        windows)
            create_archive "windows"
            ;;
        macos)
            create_archive "macos"
            ;;
        all)
            create_archive "linux"
            create_archive "windows"
            create_archive "macos"
            create_source_archive
            ;;
        *)
            echo -e "${RED}Error: Unknown platform '$PLATFORM'${NC}"
            echo "Valid options: linux, windows, macos, all"
            exit 1
            ;;
    esac
    
    # Generate checksums
    generate_checksums
    
    # Summary
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   Build Complete!                      ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}Release archives:${NC}"
    cd "$PROJECT_ROOT"
    ls -lh "$DIST_DIR"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Test archives on target platforms"
    echo "2. Create GitHub release: https://github.com/selodesigns/SELO-FileFlow/releases/new"
    echo "3. Upload archives from: $DIST_DIR/"
    echo "4. Update website download links"
    echo ""
}

# Run main function
main
