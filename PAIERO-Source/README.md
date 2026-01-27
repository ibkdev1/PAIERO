# PAIERO - Desktop Payroll Management Application

Professional desktop application for managing employee payroll, built with Python and PyQt6.

---

## 🚀 Quick Start

### Run Application
```bash
cd /Users/ibrehimakeita/Desktop/PAIERO
python3 main.py
```

### Default Login
- **Username:** admin
- **Password:** admin

---

## ✨ Features

- 👥 **Employee Management** - Add, edit, track employees
- 💰 **Payroll Processing** - Calculate salaries with deductions
- 🏦 **Loan Management** - Track employee loans
- 📄 **PDF Reports** - Generate salary slips
- 📊 **Excel Exports** - Export data for analysis
- 🔐 **User Authentication** - Secure login system
- 👮 **Permissions** - Role-based access control

---

## 📋 Requirements

- Python 3.9+
- PyQt6
- SQLite (included)

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 📁 Project Structure

```
PAIERO/
├── main.py              # Application entry point
├── config.py            # Configuration
├── requirements.txt     # Dependencies
│
├── ui/                  # User interface (PyQt6)
│   ├── main_window.py
│   ├── screens/         # App screens
│   ├── dialogs/         # Dialog windows
│   └── widgets/         # Custom widgets
│
├── database/            # Database layer
│   ├── connection.py
│   ├── auth.py
│   ├── schema.sql
│   └── repositories/    # Data access
│
├── business/            # Business logic
│   ├── payroll_calculator.py
│   └── loan_manager.py
│
├── models/              # Data models
│   ├── employee.py
│   ├── payroll.py
│   └── loan.py
│
├── reports/             # Report generation
│   ├── pdf_generator.py
│   └── excel_exporter.py
│
└── utils/               # Utilities
    └── csv_importer.py
```

---

## 💾 Database

**Location:**
```
~/Library/Application Support/PAIERO/paiero.db  (macOS)
~/AppData/Local/PAIERO/paiero.db                (Windows)
~/.local/share/PAIERO/paiero.db                 (Linux)
```

**Backup:**
```bash
cp ~/Library/Application\ Support/PAIERO/paiero.db ~/Desktop/backup.db
```

---

## 📊 Current Data

- ✅ 8 active employees
- ✅ User accounts configured
- ✅ Permission system enabled

---

## 🔧 Development

### Run from Source
```bash
python3 main.py
```

### Project Size
- Source Code: ~476 KB
- Dependencies: Installed via pip

---

## 📚 Documentation

- **QUICK_START_GUIDE.md** - Complete user manual
- **PERMISSIONS_GUIDE.md** - User permissions guide
- **requirements.txt** - Python dependencies

---

## 🛡️ Security

- Session-based authentication
- Role-based permissions
- Password protection
- Audit logging

---

## ⚙️ Configuration

Edit `config.py` to customize:
- Database path
- Tax rates
- Payroll calculation parameters
- UI settings

---

## 📞 Support

For questions or issues:
1. Check QUICK_START_GUIDE.md
2. Review PERMISSIONS_GUIDE.md
3. Contact system administrator

---

## 📝 Version

**Version:** 1.0.0
**Last Updated:** 2026-01-25
**Platform:** macOS, Windows, Linux

---

## 📄 License

© 2026 ABDC. All rights reserved.

---

**Launch the application:**
```bash
python3 main.py
```

🎉 **Ready to use!**
