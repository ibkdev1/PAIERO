#!/bin/bash
#
# PAIERO Installer for macOS
# Installs PAIERO payroll application
#

set -e

APP_NAME="PAIERO"
APP_FILE="PAIERO.app"
INSTALL_DIR="/Applications"

echo "========================================"
echo "  PAIERO Installer for macOS"
echo "========================================"
echo ""

# Check if running from correct directory
if [ ! -d "$APP_FILE" ]; then
    echo "Error: $APP_FILE not found in current directory."
    echo "Please run this installer from the folder containing PAIERO.app"
    exit 1
fi

# Check if already installed
if [ -d "$INSTALL_DIR/$APP_FILE" ]; then
    echo "PAIERO is already installed."
    read -p "Do you want to replace it? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    echo "Removing old version..."
    rm -rf "$INSTALL_DIR/$APP_FILE"
fi

# Copy to Applications
echo "Installing PAIERO to $INSTALL_DIR..."
cp -R "$APP_FILE" "$INSTALL_DIR/"

# Remove quarantine attribute (allows unsigned app to run)
echo "Configuring permissions..."
xattr -rd com.apple.quarantine "$INSTALL_DIR/$APP_FILE" 2>/dev/null || true

# Set executable permissions
chmod -R 755 "$INSTALL_DIR/$APP_FILE"

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "PAIERO has been installed to: $INSTALL_DIR/$APP_FILE"
echo ""
echo "To launch PAIERO:"
echo "  1. Open Finder"
echo "  2. Go to Applications"
echo "  3. Double-click PAIERO"
echo ""
echo "If you see a security warning:"
echo "  1. Open System Preferences > Security & Privacy"
echo "  2. Click 'Open Anyway' next to the PAIERO message"
echo ""
echo "Default login: admin / admin"
echo "(Change password after first login)"
echo ""
echo "========================================"
