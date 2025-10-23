#!/bin/bash
# FileFlow Release Helper
# Assists with creating new releases

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   FileFlow Release Helper              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Function to get current version
get_current_version() {
    if [ -f "$PROJECT_ROOT/web/package.json" ]; then
        grep '"version"' "$PROJECT_ROOT/web/package.json" | head -1 | sed 's/.*"version": "\(.*\)".*/\1/'
    else
        echo "unknown"
    fi
}

# Function to update version in files
update_version() {
    local new_version=$1
    
    echo -e "${YELLOW}→${NC} Updating version to $new_version..."
    
    # Update web/package.json
    if [ -f "$PROJECT_ROOT/web/package.json" ]; then
        sed -i.bak "s/\"version\": \".*\"/\"version\": \"$new_version\"/" "$PROJECT_ROOT/web/package.json"
        rm "$PROJECT_ROOT/web/package.json.bak"
        echo -e "${GREEN}✓${NC} Updated web/package.json"
    fi
}

# Function to validate version format
validate_version() {
    local version=$1
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo -e "${RED}Error: Version must be in format X.Y.Z (e.g., 1.0.0)${NC}"
        exit 1
    fi
}

# Function to check if tag exists
tag_exists() {
    local tag=$1
    git tag | grep -q "^$tag$"
}

# Function to check for uncommitted changes
check_uncommitted_changes() {
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${YELLOW}Warning: You have uncommitted changes!${NC}"
        echo ""
        git status --short
        echo ""
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Release cancelled."
            exit 1
        fi
    fi
}

# Function to show release checklist
show_checklist() {
    echo -e "${BLUE}Pre-Release Checklist:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "□ All features tested on target platforms"
    echo "□ CHANGELOG.md updated with release notes"
    echo "□ README.md and guides up to date"
    echo "□ No critical bugs or issues"
    echo "□ All tests passing"
    echo "□ Dependencies up to date"
    echo ""
}

# Main interactive release process
interactive_release() {
    cd "$PROJECT_ROOT"
    
    # Show current version
    CURRENT_VERSION=$(get_current_version)
    echo -e "${GREEN}Current version:${NC} $CURRENT_VERSION"
    echo ""
    
    # Show checklist
    show_checklist
    
    # Ask for new version
    read -p "Enter new version (X.Y.Z format): " NEW_VERSION
    validate_version "$NEW_VERSION"
    
    TAG_NAME="v$NEW_VERSION"
    
    # Check if tag exists
    if tag_exists "$TAG_NAME"; then
        echo -e "${RED}Error: Tag $TAG_NAME already exists!${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${YELLOW}Release Plan:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "• Current version: $CURRENT_VERSION"
    echo "• New version: $NEW_VERSION"
    echo "• Git tag: $TAG_NAME"
    echo ""
    
    # Confirm
    read -p "Proceed with release? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Release cancelled."
        exit 1
    fi
    
    # Check for uncommitted changes
    check_uncommitted_changes
    
    # Update version files
    update_version "$NEW_VERSION"
    
    # Prompt to update CHANGELOG
    echo ""
    echo -e "${YELLOW}→${NC} Please update CHANGELOG.md now"
    read -p "Press Enter when CHANGELOG.md is updated..."
    
    # Show git status
    echo ""
    echo -e "${YELLOW}Changes to commit:${NC}"
    git status --short
    echo ""
    
    # Commit changes
    read -p "Commit version bump? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add -A
        git commit -m "Release $TAG_NAME"
        echo -e "${GREEN}✓${NC} Changes committed"
    fi
    
    # Create tag
    echo ""
    read -p "Create git tag $TAG_NAME? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -a "$TAG_NAME" -m "Release $TAG_NAME"
        echo -e "${GREEN}✓${NC} Tag created"
    fi
    
    # Push to remote
    echo ""
    read -p "Push to remote (this will trigger GitHub Actions)? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin main
        git push origin "$TAG_NAME"
        echo -e "${GREEN}✓${NC} Pushed to remote"
        echo ""
        echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║   Release Initiated!                   ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
        echo ""
        echo "GitHub Actions is now building release archives..."
        echo ""
        echo "Monitor progress at:"
        echo "https://github.com/selodesigns/SELO-FileFlow/actions"
        echo ""
        echo "Release will be available at:"
        echo "https://github.com/selodesigns/SELO-FileFlow/releases/tag/$TAG_NAME"
        echo ""
    else
        echo ""
        echo -e "${YELLOW}Release prepared but not pushed.${NC}"
        echo "To push manually:"
        echo "  git push origin main"
        echo "  git push origin $TAG_NAME"
    fi
}

# Quick mode (non-interactive)
quick_release() {
    local version=$1
    validate_version "$version"
    
    cd "$PROJECT_ROOT"
    
    TAG_NAME="v$version"
    
    # Check if tag exists
    if tag_exists "$TAG_NAME"; then
        echo -e "${RED}Error: Tag $TAG_NAME already exists!${NC}"
        exit 1
    fi
    
    # Update version
    update_version "$version"
    
    # Commit and tag
    git add -A
    git commit -m "Release $TAG_NAME"
    git tag -a "$TAG_NAME" -m "Release $TAG_NAME"
    
    echo -e "${GREEN}✓${NC} Release $TAG_NAME prepared"
    echo ""
    echo "To push and trigger build:"
    echo "  git push origin main && git push origin $TAG_NAME"
}

# Main
if [ $# -eq 0 ]; then
    interactive_release
elif [ "$1" = "--quick" ] && [ -n "$2" ]; then
    quick_release "$2"
else
    echo "Usage:"
    echo "  $0                    # Interactive mode"
    echo "  $0 --quick X.Y.Z      # Quick mode (auto-commit, no push)"
    exit 1
fi
