# Windows Login Issue - Debugging Guide

## Problem
New users can be created but cannot login with their username and password on Windows.

## Root Causes (Possible)

### 1. **Character Encoding Issues**
Windows might use different character encoding (UTF-16/Windows-1252) vs Mac/Linux (UTF-8)
- Special characters in passwords might be encoded differently
- Accented characters (é, à, etc.) in usernames might cause issues

### 2. **Whitespace Issues**
- Invisible whitespace characters being added
- Copy-paste adding extra characters
- Keyboard input differences between Windows and Mac

### 3. **Database State Issues**
- Database created on Mac vs Windows might have different settings
- Migration might not have run on Windows database
- User permissions table might be corrupted

### 4. **Case Sensitivity**
- Windows filesystem vs SQLite case handling
- Username normalization differences

---

## Debug Steps for Windows

### Step 1: Enable Debug Output

The latest code now includes debug output. When running PAIERO from command line:

```cmd
cd C:\path\to\PAIERO
python main.py
```

Watch the console for these messages:

**When creating a user:**
```
DEBUG: Creating user with password length: X
DEBUG: Password (repr): 'your_password'
DEBUG: Generated hash length: 128
```

**When login fails:**
```
Login failed: Invalid password for user 'username'
DEBUG: Password length: X, Hash length: 128
DEBUG: Password (repr): 'your_password'
```

### Step 2: Compare Password Lengths

If the password length differs between creation and login:
- **Creation:** `DEBUG: Creating user with password length: 8`
- **Login:** `DEBUG: Password length: 10`

This indicates extra characters are being added (whitespace, etc.)

### Step 3: Check Password Representation

The `repr()` output shows the exact characters:
- **Normal:** `'test1234'`
- **With space:** `'test1234 '` (notice the space before closing quote)
- **With newline:** `'test1234\n'`
- **With carriage return:** `'test1234\r'`

### Step 4: Test with Simple Password

Try creating a user with a very simple password:
1. Username: `test`
2. Password: `1234` (just numbers, no letters)
3. Try logging in

If this works but complex passwords don't:
- Issue is with special characters or encoding

---

## Manual Testing Script

Run this on Windows to test user creation and login:

```cmd
cd C:\path\to\PAIERO
python -c "
import sys
sys.path.insert(0, '.')
from database.connection import DatabaseConnection
from database.auth import AuthManager

DatabaseConnection.initialize()

# Login as admin
AuthManager.login('admin', 'admin')

# Create test user
username = 'wintest'
password = '1234'
AuthManager.create_user(username, password, 'Windows Test', 'user')
print('User created')

# Logout
AuthManager.logout()

# Try login
success, error = AuthManager.login(username, password)
if success:
    print('✓ LOGIN WORKS!')
else:
    print(f'✗ LOGIN FAILED: {error}')

# Cleanup
import sqlite3
conn = DatabaseConnection.get_connection()
conn.execute('DELETE FROM users WHERE username = ?', (username,))
conn.commit()

DatabaseConnection.close()
"
```

---

## Solutions

### Solution 1: Strip Password (Not Recommended)

If whitespace is the issue, we COULD strip passwords, but this would prevent passwords with intentional spaces.

### Solution 2: Normalize Input (Recommended)

Ensure consistent encoding:

**In login_dialog.py:**
```python
def login(self):
    username = self.username_input.text().strip()
    password = self.password_input.text()  # Don't strip!

    # Ensure UTF-8 encoding
    username = username.encode('utf-8').decode('utf-8')
    password = password.encode('utf-8').decode('utf-8')

    success, error = AuthManager.login(username, password)
```

### Solution 3: Database Check

Verify user was created correctly:

```cmd
cd C:\path\to\PAIERO
sqlite3 "%LOCALAPPDATA%\PAIERO\paiero.db" "SELECT user_id, username, LENGTH(password_hash) as hash_len, is_active FROM users;"
```

Expected output:
```
1|admin|128|1
2|newuser|128|1
```

Hash length should be exactly **128 characters**.

### Solution 4: Reset User Password

If user exists but can't login, reset password:

```cmd
cd C:\path\to\PAIERO
python -c "
from database.connection import DatabaseConnection
from database.auth import AuthManager

DatabaseConnection.initialize()
AuthManager.login('admin', 'admin')

# Change password for user ID 2 (adjust as needed)
AuthManager.change_password(2, 'newpassword')
print('Password changed')

DatabaseConnection.close()
"
```

---

## Files to Check on Windows

### 1. Database Location
```
C:\Users\YourUsername\AppData\Local\PAIERO\paiero.db
```

Verify file exists and is not corrupted:
```cmd
sqlite3 "%LOCALAPPDATA%\PAIERO\paiero.db" ".tables"
```

Should show all tables including `users` and `user_permissions`.

### 2. Migration Log
Check if migrations ran:
```cmd
sqlite3 "%LOCALAPPDATA%\PAIERO\paiero.db" "SELECT * FROM migration_log;"
```

### 3. User Table Structure
```cmd
sqlite3 "%LOCALAPPDATA%\PAIERO\paiero.db" "PRAGMA table_info(users);"
```

---

## Temporary Workaround

### Option A: Use Admin Account

Have all users share the admin account temporarily:
- Username: `admin`
- Password: `admin`

Then change admin password to something known to all users.

### Option B: Manual SQL User Creation

Create user directly in database:

```cmd
cd C:\path\to\PAIERO
python -c "
from database.connection import DatabaseConnection
from database.auth import AuthManager
import hashlib, os

DatabaseConnection.initialize()

# Create user with known hash
username = 'newuser'
password = 'password123'

# Hash password (same method as AuthManager)
salt = os.urandom(32)
pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
password_hash = salt.hex() + pwd_hash.hex()

# Insert directly
conn = DatabaseConnection.get_connection()
cursor = conn.execute('''
    INSERT INTO users (username, password_hash, full_name, role, is_active)
    VALUES (?, ?, ?, ?, 1)
''', (username, password_hash, 'New User', 'user'))
user_id = cursor.lastrowid

# Create permissions
conn.execute('''
    INSERT INTO user_permissions (
        user_id, can_view_employees, can_edit_employees, can_delete_employees,
        can_view_payroll, can_process_payroll, can_finalize_payroll,
        can_view_loans, can_manage_loans,
        can_generate_reports, can_export_data,
        can_view_parameters, can_modify_parameters,
        can_manage_users
    ) VALUES (?, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0)
''', (user_id,))

conn.commit()
print(f'User {username} created with ID {user_id}')

DatabaseConnection.close()
"
```

---

## Report Issue

If none of these solutions work, collect this information:

1. **Debug output** from console when creating user
2. **Debug output** from console when login fails
3. **Windows version:** (e.g., Windows 10 Pro, Windows 11)
4. **Python version:** `python --version`
5. **PyQt6 version:** `pip show PyQt6`
6. **Database check results:**
   ```cmd
   sqlite3 "%LOCALAPPDATA%\PAIERO\paiero.db" "SELECT user_id, username, LENGTH(password_hash), is_active FROM users;"
   ```
7. **Test script results** (from Manual Testing Script above)

---

## Prevention for Future Users

When creating new users on Windows:

1. **Use simple passwords first** (only letters and numbers)
2. **Avoid special characters** (!, @, #, etc.) until tested
3. **Avoid accented characters** (é, à, ù, etc.)
4. **Test login immediately** after creating user
5. **Write down exact password** before creating user
6. **Test with copy-paste** - copy password from notepad, paste into both password fields

---

## Quick Fix: Password Reset Feature

I'll add a "Reset Password" button in user management that allows admin to reset any user's password without knowing the old one. This will help if users are created but can't login.
