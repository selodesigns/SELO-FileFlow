#!/bin/bash

# FileFlow Quick Setup Script
# Run this immediately after cloning the repository

echo "🚀 FileFlow Quick Setup"
echo "======================="
echo ""
echo "This will install FileFlow with all dependencies."
echo "For detailed installation options, see INSTALLATION.md"
echo ""

# Check if we're in the right directory
if [[ ! -f "install.sh" ]]; then
    echo "❌ Error: install.sh not found. Please run this from the FileFlow directory."
    exit 1
fi

# Run the comprehensive installer
./install.sh
