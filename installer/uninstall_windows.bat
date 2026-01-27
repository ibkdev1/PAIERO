@echo off
REM ========================================
REM PAIERO Uninstaller for Windows
REM ========================================

setlocal

set APP_NAME=PAIERO
set INSTALL_DIR=%LOCALAPPDATA%\PAIERO
set DATA_DIR=%LOCALAPPDATA%\PAIERO
set DESKTOP=%USERPROFILE%\Desktop
set START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs

echo ========================================
echo   PAIERO Uninstaller
echo ========================================
echo.

if not exist "%INSTALL_DIR%" (
    echo PAIERO is not installed.
    pause
    exit /b 0
)

echo This will uninstall PAIERO from your computer.
echo.
set /p REPLY="Do you want to continue? (Y/N): "
if /i not "%REPLY%"=="Y" (
    echo Uninstallation cancelled.
    pause
    exit /b 0
)

echo.
set /p KEEP_DATA="Keep your data (employees, payroll records)? (Y/N): "

REM Remove shortcuts
echo Removing shortcuts...
del "%DESKTOP%\PAIERO.lnk" 2>nul
rmdir /s /q "%START_MENU%\PAIERO" 2>nul

REM Remove application
echo Removing application files...
rmdir /s /q "%INSTALL_DIR%" 2>nul

REM Optionally remove data
if /i not "%KEEP_DATA%"=="Y" (
    echo Removing application data...
    rmdir /s /q "%DATA_DIR%" 2>nul
)

echo.
echo ========================================
echo   Uninstallation Complete!
echo ========================================
echo.
if /i "%KEEP_DATA%"=="Y" (
    echo Your data has been preserved at:
    echo   %DATA_DIR%
)
echo.
echo PAIERO has been removed from your computer.
echo ========================================
pause
