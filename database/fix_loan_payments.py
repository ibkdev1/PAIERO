#!/usr/bin/env python3
"""
Manual migration script to fix loan_payments.period_id constraint
Run this if you're getting "NOT NULL constraint failed loan_payment.period_id" error

Usage:
    python database/fix_loan_payments.py
"""

import sqlite3
import sys
import os
from pathlib import Path


def fix_loan_payments_table(db_path: str):
    """Fix the loan_payments table to allow NULL period_id"""

    print(f"Connecting to database: {db_path}")

    if not os.path.exists(db_path):
        print(f"ERROR: Database file not found: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if period_id has NOT NULL constraint
        cursor.execute("PRAGMA table_info(loan_payments)")
        columns = cursor.fetchall()

        period_id_not_null = False
        for col in columns:
            # col = (cid, name, type, notnull, dflt_value, pk)
            if col[1] == 'period_id' and col[3] == 1:  # col[3] is notnull flag
                period_id_not_null = True
                break

        if not period_id_not_null:
            print("✓ Database is already correct - period_id allows NULL")
            conn.close()
            return True

        print("Found issue: period_id has NOT NULL constraint")
        print("Applying migration...")

        # Create backup first
        backup_path = db_path + '.backup'
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✓ Backup created: {backup_path}")

        # Create new table with correct schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loan_payments_new (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                loan_id INTEGER NOT NULL,
                period_id INTEGER,
                payment_date DATE NOT NULL,
                scheduled_amount REAL NOT NULL,
                actual_amount REAL DEFAULT 0,
                is_paid BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (loan_id) REFERENCES loans_advances(loan_id),
                FOREIGN KEY (period_id) REFERENCES payroll_periods(period_id)
            )
        """)
        print("✓ Created new table with correct schema")

        # Copy existing data
        cursor.execute("""
            INSERT INTO loan_payments_new
            SELECT * FROM loan_payments
        """)
        print("✓ Copied existing data")

        # Drop old table
        cursor.execute("DROP TABLE loan_payments")
        print("✓ Dropped old table")

        # Rename new table
        cursor.execute("ALTER TABLE loan_payments_new RENAME TO loan_payments")
        print("✓ Renamed new table")

        # Recreate indexes
        cursor.execute("CREATE INDEX idx_payments_loan ON loan_payments(loan_id)")
        cursor.execute("CREATE INDEX idx_payments_period ON loan_payments(period_id)")
        cursor.execute("CREATE INDEX idx_payments_status ON loan_payments(is_paid)")
        print("✓ Recreated indexes")

        # Recreate trigger
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_payments_timestamp
            AFTER UPDATE ON loan_payments
            FOR EACH ROW
            BEGIN
                UPDATE loan_payments SET updated_at = CURRENT_TIMESTAMP
                WHERE payment_id = NEW.payment_id;
            END
        """)
        print("✓ Recreated trigger")

        # Commit transaction
        conn.commit()
        print("✓ Migration committed successfully")

        # Verify the fix
        cursor.execute("PRAGMA table_info(loan_payments)")
        columns = cursor.fetchall()
        for col in columns:
            if col[1] == 'period_id':
                if col[3] == 0:  # notnull = 0 means NULL is allowed
                    print("✓ Verification passed - period_id now allows NULL")
                else:
                    print("⚠ Warning: period_id still has NOT NULL constraint")
                break

        conn.close()
        print("\n✅ Migration completed successfully!")
        print(f"Backup saved at: {backup_path}")
        return True

    except Exception as e:
        print(f"\n❌ ERROR during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        print("Database was not modified. Please contact support.")
        return False


def main():
    """Main function"""
    print("=" * 70)
    print("PAIERO - Loan Payments Table Migration")
    print("=" * 70)
    print()

    # Try to find database automatically
    if sys.platform == 'darwin':  # macOS
        default_path = os.path.expanduser('~/Library/Application Support/PAIERO/paiero.db')
    elif sys.platform == 'win32':  # Windows
        default_path = os.path.expanduser('~/AppData/Local/PAIERO/paiero.db')
    else:  # Linux
        default_path = os.path.expanduser('~/.local/share/PAIERO/paiero.db')

    # Check if database exists at default location
    if os.path.exists(default_path):
        db_path = default_path
        print(f"Found database at: {db_path}")
    else:
        print(f"Database not found at default location: {default_path}")
        db_path = input("Enter the full path to your paiero.db file: ").strip()

    print()

    if not db_path:
        print("ERROR: No database path provided")
        return 1

    success = fix_loan_payments_table(db_path)

    print()
    print("=" * 70)

    if success:
        print("You can now create loans in PAIERO without errors.")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
