#!/bin/bash
#
# PAIERO Installer for macOS (double-clickable)
# This file can be double-clicked in Finder to run
#

# Get the directory where this script is located
cd "$(dirname "$0")"

APP_NAME="PAIERO"
APP_FILE="PAIERO.app"
INSTALL_DIR="/Applications"

clear
echo "========================================"
echo "  PAIERO Installer for macOS"
echo "========================================"
echo ""

# Check if running from correct directory
if [ ! -d "$APP_FILE" ]; then
    echo "Error: $APP_FILE not found."
    echo ""
    echo "Please make sure PAIERO.app is in the same folder"
    echo "as this installer."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if already installed
if [ -d "$INSTALL_DIR/$APP_FILE" ]; then
    echo "PAIERO is already installed in Applications."
    echo ""
    read -p "Replace existing installation? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        read -p "Press Enter to exit..."
        exit 0
    fi
    echo ""
    echo "Removing old version..."
    rm -rf "$INSTALL_DIR/$APP_FILE"
fi

# Copy to Applications
echo "Installing PAIERO to Applications..."
cp -R "$APP_FILE" "$INSTALL_DIR/"

# Remove quarantine attribute
echo "Configuring security settings..."
xattr -rd com.apple.quarantine "$INSTALL_DIR/$APP_FILE" 2>/dev/null || true

# Set permissions
chmod -R 755 "$INSTALL_DIR/$APP_FILE"

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "PAIERO has been installed to Applications."
echo ""
echo "To launch:"
echo "  - Open Finder > Applications > PAIERO"
echo "  - Or press Cmd+Space, type 'PAIERO', press Enter"
echo ""
echo "Default login: admin / admin"
echo ""
echo "========================================"
echo ""

# Ask to launch
read -p "Launch PAIERO now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    open "$INSTALL_DIR/$APP_FILE"
fi

echo ""
echo "You can close this window."
