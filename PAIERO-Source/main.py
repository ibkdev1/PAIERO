"""
PAIERO - Desktop Payroll Management Application
Main application entry point
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_TITLE, APP_VERSION, APP_SUBTITLE, initialize_directories
from database.connection import DatabaseConnection
from ui.main_window import MainWindow
from ui.dialogs.login_dialog import LoginDialog
from PyQt6.QtWidgets import QDialog


def main():
    """Main application entry point"""
    print("=" * 70)
    print(f"  {APP_TITLE}")
    print(f"  {APP_SUBTITLE}")
    print(f"  Version {APP_VERSION}")
    print("=" * 70)
    print()

    # Initialize application directories
    print("Initializing application directories...")
    initialize_directories()

    # Initialize database
    print("Initializing database...")
    try:
        DatabaseConnection.initialize()
        print(f"Database ready at: {DatabaseConnection.get_database_path()}")
    except Exception as e:
        print(f"ERROR: Failed to initialize database: {e}")
        return 1

    # Create Qt Application
    print("Starting application...")
    app = QApplication(sys.argv)

    # Set application-wide properties
    app.setApplicationName(APP_TITLE)
    app.setApplicationVersion(APP_VERSION)

    # Note: High DPI scaling is enabled by default in PyQt6

    # Show login dialog first
    print("\n" + "="*60)
    print("🚀 LOGIN WINDOW OPENING NOW!")
    print("="*60)
    print("👀 Look for the PAIERO login window on your screen")
    print("   (it might be behind other windows)")
    print("="*60 + "\n")

    login_dialog = LoginDialog()
    login_dialog.raise_()  # Bring to front
    login_dialog.activateWindow()  # Activate window

    if login_dialog.exec() != QDialog.DialogCode.Accepted:
        print("Login cancelled or failed")
        return 0

    print("Login successful!")

    # Create and show main window
    window = MainWindow()
    window.show()

    print(f"{APP_TITLE} started successfully!")
    print("=" * 60)
    print()

    # Run application
    exit_code = app.exec()

    # Cleanup
    print("\nShutting down...")
    DatabaseConnection.close()
    print("Application closed")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
