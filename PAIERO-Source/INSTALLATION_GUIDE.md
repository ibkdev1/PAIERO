# PAIERO Installation Guide

## How to Install PAIERO on Another Computer

This guide helps you install and run PAIERO on any computer.

---

## 📦 What You Need

**File to share:**
- `PAIERO-Source.zip` (99 KB)

**On the new computer:**
- Python 3.9 or higher
- Internet connection (for installing dependencies)

---

## 🚀 Installation Steps

### Step 1: Install Python

#### macOS:
```bash
# Check if Python is installed
python3 --version

# If not installed, download from python.org or use Homebrew:
brew install python@3.11
```

#### Windows:
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer and **check "Add Python to PATH"**
3. Open Command Prompt and verify:
```cmd
python --version
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip
```

---

### Step 2: Extract PAIERO

1. Copy `PAIERO-Source.zip` to the new computer (USB, email, cloud storage, etc.)
2. Extract the zip file to a folder (e.g., Desktop)

#### macOS/Linux:
```bash
cd ~/Desktop
unzip PAIERO-Source.zip -d PAIERO
cd PAIERO
```

#### Windows:
- Right-click `PAIERO-Source.zip`
- Select "Extract All..."
- Choose destination folder
- Open Command Prompt in that folder

---

### Step 3: Install Dependencies

```bash
# Make sure you're in the PAIERO folder
cd /path/to/PAIERO

# Install required Python packages
pip3 install -r requirements.txt
```

**On Windows, use:**
```cmd
pip install -r requirements.txt
```

This will install:
- PyQt6 (Desktop interface)
- pandas (Data processing)
- openpyxl (Excel export)
- reportlab (PDF generation)

---

### Step 4: Run PAIERO

#### macOS/Linux:
```bash
python3 main.py
```

#### Windows:
```cmd
python main.py
```

---

## 🔐 First Login

**Default credentials:**
- Username: `admin`
- Password: `admin`

**Important:** Change the admin password after first login!

---

## 📁 Where is My Data?

PAIERO automatically creates a database in your system's application data folder:

- **macOS:** `~/Library/Application Support/PAIERO/paiero.db`
- **Windows:** `~\AppData\Local\PAIERO\paiero.db`
- **Linux:** `~/.local/share/PAIERO/paiero.db`

Each computer has its **own separate database**. Data is NOT shared between installations.

---

## 🔄 Sharing Data Between Computers

If you want the same employee data on both computers:

### Option 1: Export/Import (Recommended)
1. On Computer A: Use Reports → Export to Excel
2. Copy Excel file to Computer B
3. On Computer B: Use Tools → Import from CSV/Excel

### Option 2: Copy Database File
1. On Computer A, locate database:
   ```bash
   # macOS
   open ~/Library/Application\ Support/PAIERO/

   # Windows
   explorer %LocalAppData%\PAIERO
   ```
2. Copy `paiero.db` file to USB/cloud storage
3. On Computer B, replace database file in same location
4. Restart PAIERO

---

## 🛠️ Troubleshooting

### "python3: command not found"
- Python is not installed or not in PATH
- Reinstall Python and check "Add to PATH" option

### "No module named 'PyQt6'"
- Dependencies not installed
- Run: `pip3 install -r requirements.txt`

### "Permission denied" (macOS)
- Give terminal permission to access files
- System Preferences → Security & Privacy → Privacy → Full Disk Access

### App window doesn't appear
- Check for window behind other windows
- Try clicking PAIERO in Dock/Taskbar
- Check terminal for error messages

### Database errors on first run
- Normal! Database will be created automatically
- Make sure you have write permissions

---

## 📊 System Requirements

**Minimum:**
- CPU: Any modern processor (Intel/AMD/Apple Silicon)
- RAM: 2 GB
- Storage: 100 MB free space
- Display: 1024x768 or higher

**Recommended:**
- RAM: 4 GB
- Storage: 500 MB (for reports and data)
- Display: 1920x1080

---

## 📚 Documentation

After installation, read:
- `README.md` - Quick start guide
- `QUICK_START_GUIDE.md` - Complete user manual
- `PERMISSIONS_GUIDE.md` - User permissions system

---

## 🆘 Need Help?

1. Check terminal/command prompt for error messages
2. Verify Python version: `python3 --version` (must be 3.9+)
3. Verify dependencies installed: `pip3 list | grep PyQt6`
4. Contact your system administrator

---

## ⚙️ Advanced: Create Desktop Shortcut

### macOS:
Create a file `start-paiero.command`:
```bash
#!/bin/bash
cd /path/to/PAIERO
python3 main.py
```
Make executable: `chmod +x start-paiero.command`

### Windows:
Create `start-paiero.bat`:
```cmd
@echo off
cd C:\path\to\PAIERO
python main.py
pause
```

### Linux:
Create `paiero.desktop`:
```ini
[Desktop Entry]
Type=Application
Name=PAIERO
Exec=python3 /path/to/PAIERO/main.py
Icon=/path/to/PAIERO/resources/icons/icon.png
Terminal=false
```

---

## 📝 Notes

- Each installation is **independent** - separate data per computer
- No internet connection required after installation
- Updates: Replace files and keep database intact
- Backup: Copy the database file regularly

---

**Installation complete!** Launch with `python3 main.py` 🎉
