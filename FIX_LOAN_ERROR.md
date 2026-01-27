# Fix for Loan Creation Error

## Problem
When clicking on "Avances/Prêts" and trying to create a loan, you get this error:
```
Erreur de la creation No Null constraint failed loan_payment.period_id
```

## Root Cause
The database was created with an older version of the schema where the `loan_payments.period_id` column had a NOT NULL constraint. The current schema allows NULL values (loans are created without being linked to a payroll period initially), but existing databases need to be migrated.

## Solution

There are **two ways** to fix this:

### Option 1: Automatic Fix (Recommended)
The fix is now included in the application. Simply:

1. **Update your PAIERO installation** with the latest code
2. **Launch PAIERO** - the migration will run automatically on startup
3. Watch the console for this message:
   ```
   Migration: Fixing loan_payments.period_id constraint...
   Migration: Successfully fixed loan_payments.period_id constraint
   ```
4. **Try creating a loan again** - it should work now!

### Option 2: Manual Fix (If automatic doesn't work)

If the automatic migration doesn't work, you can run the manual migration script:

**On Windows:**
```cmd
cd C:\path\to\PAIERO
python database\fix_loan_payments.py
```

**On macOS/Linux:**
```bash
cd /path/to/PAIERO
python3 database/fix_loan_payments.py
```

The script will:
- Find your database automatically
- Create a backup (`.backup` file)
- Fix the table structure
- Verify the fix

## For Windows Users

### Where is your database?
```
C:\Users\YourUsername\AppData\Local\PAIERO\paiero.db
```

### How to update your Windows installation:

1. **Option A - Replace the Python files:**
   - Locate your PAIERO installation folder
   - Replace `database/connection.py` with the updated version
   - Restart PAIERO

2. **Option B - Rebuild the application:**
   ```cmd
   cd C:\path\to\PAIERO
   python build_app.py
   ```
   Then install the new PAIERO.exe

3. **Option C - Run the manual migration script:**
   ```cmd
   python database\fix_loan_payments.py
   ```

## Verification

After applying the fix, test by:
1. Opening PAIERO
2. Going to "Avances/Prêts"
3. Click "Nouveau Prêt/Avance"
4. Fill in the form and save
5. The loan should be created without errors

## What Changed

The migration modifies the `loan_payments` table structure:

**Before (old schema):**
```sql
period_id INTEGER NOT NULL
```

**After (fixed schema):**
```sql
period_id INTEGER  -- Allows NULL
```

This allows loans to be created without immediately linking them to a payroll period. The `period_id` will be set when the loan payment is processed during payroll.

## Files Modified

- [database/connection.py](database/connection.py) - Added automatic migration in `_run_migrations()` method
- [database/fix_loan_payments.py](database/fix_loan_payments.py) - Manual migration script

## Backup

The migration always creates a backup of your database before making changes:
- **Automatic migration:** Backup is done by the system
- **Manual script:** Creates `paiero.db.backup` in the same folder

## Need Help?

If you still encounter issues after applying this fix:
1. Check that the migration ran (look for console output)
2. Verify your database location
3. Try the manual migration script
4. Check that you have the latest version of all files

## Technical Details

**Changed Files:**
- `/database/connection.py` (lines 96-190)
- `/PAIERO-Source/database/connection.py` (same changes)
- `/database/fix_loan_payments.py` (new file)

**Database Schema:**
- Table: `loan_payments`
- Column: `period_id`
- Change: NOT NULL → NULL (allows NULL values)
- Reason: Loans are created before being linked to payroll periods
