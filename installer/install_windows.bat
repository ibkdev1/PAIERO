@echo off
REM ========================================
REM PAIERO Installer for Windows
REM Installs PAIERO payroll application
REM ========================================

setlocal enabledelayedexpansion

set APP_NAME=PAIERO
set APP_FOLDER=PAIERO
set APP_FILE=PAIERO.exe
set INSTALL_DIR=%LOCALAPPDATA%\PAIERO
set DESKTOP=%USERPROFILE%\Desktop
set START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs

echo ========================================
echo   PAIERO Installer for Windows
echo ========================================
echo.

REM Check if running from correct directory (folder-based structure)
if exist "%APP_FOLDER%\%APP_FILE%" (
    set SOURCE_DIR=%APP_FOLDER%
    goto :install
)

REM Fallback: single exe mode
if exist "%APP_FILE%" (
    set SOURCE_DIR=.
    goto :install
)

echo Error: PAIERO not found in current directory.
echo Please run this installer from the extracted folder.
pause
exit /b 1

:install
REM Check if already installed
if exist "%INSTALL_DIR%\%APP_FILE%" (
    echo PAIERO is already installed.
    set /p REPLY="Do you want to replace it? (Y/N): "
    if /i not "!REPLY!"=="Y" (
        echo Installation cancelled.
        pause
        exit /b 0
    )
    echo Removing old version...
    rmdir /s /q "%INSTALL_DIR%" 2>nul
)

REM Create installation directory
echo Creating installation directory...
mkdir "%INSTALL_DIR%" 2>nul

REM Copy application files
echo Installing PAIERO...
if "%SOURCE_DIR%"=="PAIERO" (
    xcopy "%SOURCE_DIR%" "%INSTALL_DIR%\" /E /I /Q >nul
) else (
    copy "%APP_FILE%" "%INSTALL_DIR%\" >nul
    if exist "*.dll" copy "*.dll" "%INSTALL_DIR%\" >nul
    if exist "_internal" xcopy "_internal" "%INSTALL_DIR%\_internal\" /E /I /Q >nul
)

REM Create desktop shortcut
echo Creating desktop shortcut...
(
echo Set oWS = WScript.CreateObject("WScript.Shell"^)
echo sLinkFile = "%DESKTOP%\PAIERO.lnk"
echo Set oLink = oWS.CreateShortcut(sLinkFile^)
echo oLink.TargetPath = "%INSTALL_DIR%\%APP_FILE%"
echo oLink.WorkingDirectory = "%INSTALL_DIR%"
echo oLink.Description = "PAIERO Payroll Management"
echo oLink.Save
) > "%TEMP%\CreateShortcut.vbs"
cscript //nologo "%TEMP%\CreateShortcut.vbs"
del "%TEMP%\CreateShortcut.vbs"

REM Create Start Menu shortcut
echo Creating Start Menu shortcut...
mkdir "%START_MENU%\PAIERO" 2>nul
(
echo Set oWS = WScript.CreateObject("WScript.Shell"^)
echo sLinkFile = "%START_MENU%\PAIERO\PAIERO.lnk"
echo Set oLink = oWS.CreateShortcut(sLinkFile^)
echo oLink.TargetPath = "%INSTALL_DIR%\%APP_FILE%"
echo oLink.WorkingDirectory = "%INSTALL_DIR%"
echo oLink.Description = "PAIERO Payroll Management"
echo oLink.Save
) > "%TEMP%\CreateShortcut.vbs"
cscript //nologo "%TEMP%\CreateShortcut.vbs"
del "%TEMP%\CreateShortcut.vbs"

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo PAIERO has been installed to: %INSTALL_DIR%
echo.
echo Shortcuts created:
echo   - Desktop: PAIERO
echo   - Start Menu: PAIERO
echo.
echo To launch PAIERO:
echo   Double-click the PAIERO icon on your desktop
echo.
echo If Windows SmartScreen appears:
echo   1. Click "More info"
echo   2. Click "Run anyway"
echo.
echo Default login: admin / admin
echo (Change password after first login)
echo.
echo ========================================
pause
