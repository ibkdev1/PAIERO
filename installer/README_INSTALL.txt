================================================================
            PAIERO - Installation Instructions
        Professional Payroll Management System
================================================================

Thank you for downloading PAIERO!

================================================================
                    QUICK START
================================================================

macOS Users:
------------
1. Extract PAIERO-Mac.zip
2. Double-click install_mac.command (or drag PAIERO.app to Applications)
3. If security warning appears: Right-click PAIERO > Open > Open
4. Login: admin / admin

Windows Users:
--------------
1. Extract PAIERO-Windows.zip
2. Double-click install_windows.bat
3. If SmartScreen warning: Click "More info" > "Run anyway"
4. Login: admin / admin


================================================================
                 DETAILED INSTRUCTIONS
================================================================

----- macOS Installation -----

OPTION A: Using Installer (Recommended)

  1. Extract the downloaded PAIERO-Mac.zip file
  2. Open Terminal (Applications > Utilities > Terminal)
  3. Navigate to the extracted folder:
     cd ~/Downloads/PAIERO-Mac
  4. Run the installer:
     chmod +x install_mac.sh
     ./install_mac.sh
  5. Launch PAIERO from your Applications folder

OPTION B: Manual Installation

  1. Extract PAIERO-Mac.zip
  2. Drag PAIERO.app to your Applications folder
  3. Double-click to launch

SECURITY WARNING (macOS):
  Since PAIERO is not from the App Store, macOS will show a
  security warning on first launch.

  To bypass:
  - Right-click (or Control-click) on PAIERO.app
  - Select "Open" from the menu
  - Click "Open" in the dialog

  Or:
  - Open System Preferences > Security & Privacy
  - Click "Open Anyway" next to the PAIERO message


----- Windows Installation -----

OPTION A: Using Installer (Recommended)

  1. Extract the downloaded PAIERO-Windows.zip file
  2. Double-click install_windows.bat
  3. Follow the on-screen prompts
  4. Launch PAIERO from the desktop shortcut

OPTION B: Manual Installation

  1. Extract PAIERO-Windows.zip to desired location
  2. Double-click PAIERO.exe to run

SMARTSCREEN WARNING (Windows):
  Since PAIERO is not signed, Windows may show a warning.

  To bypass:
  - Click "More info"
  - Click "Run anyway"

  This only appears on the first launch.


================================================================
                    FIRST LOGIN
================================================================

Username: admin
Password: admin

IMPORTANT: Change your password after first login!
Go to: Settings > User Management > Change Password


================================================================
                   DATA LOCATION
================================================================

Your data is stored separately from the application:

macOS:   ~/Library/Application Support/PAIERO/
Windows: %LOCALAPPDATA%\PAIERO\

The database file is: paiero.db

BACKUP RECOMMENDATION:
Regularly copy the paiero.db file to a safe location.


================================================================
                  UNINSTALLATION
================================================================

macOS:
  1. Drag PAIERO from Applications to Trash
  2. Optional: Delete ~/Library/Application Support/PAIERO/

Windows:
  1. Run uninstall_windows.bat from installation folder
  OR
  1. Delete desktop shortcut
  2. Delete %LOCALAPPDATA%\PAIERO\ folder


================================================================
                  TROUBLESHOOTING
================================================================

Problem: "PAIERO is damaged and can't be opened" (macOS)
Solution: Open Terminal and run:
  xattr -rd com.apple.quarantine /Applications/PAIERO.app

Problem: Missing DLL error (Windows)
Solution: Install Visual C++ Redistributable from:
  https://aka.ms/vs/17/release/vc_redist.x64.exe

Problem: App crashes on startup
Solution: Delete the database and restart:
  macOS: rm ~/Library/Application\ Support/PAIERO/paiero.db
  Windows: del %LOCALAPPDATA%\PAIERO\paiero.db
  WARNING: This deletes all your data!

Problem: Forgot password
Solution: Contact administrator or delete database (loses data)


================================================================
                    SYSTEM REQUIREMENTS
================================================================

macOS:    macOS 10.14 (Mojave) or later
Windows:  Windows 10 or later
RAM:      4 GB minimum
Storage:  500 MB free space


================================================================
                      SUPPORT
================================================================

For support: support@abdc.com

================================================================
          PAIERO by ABDC - Version 1.0.0
================================================================
