#!/usr/bin/env python3
"""
Migration script to add user_permissions table
"""

import sqlite3
from database.connection import DatabaseConnection
from database.auth import AuthManager


def migrate_permissions():
    """Add user_permissions table and create default permissions for existing users"""
    print("Starting permissions migration...")

    conn = DatabaseConnection.get_connection()

    try:
        # Create user_permissions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_permissions (
                permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                -- Employee permissions
                can_view_employees BOOLEAN DEFAULT 1,
                can_edit_employees BOOLEAN DEFAULT 0,
                can_delete_employees BOOLEAN DEFAULT 0,
                -- Payroll permissions
                can_view_payroll BOOLEAN DEFAULT 1,
                can_process_payroll BOOLEAN DEFAULT 0,
                can_finalize_payroll BOOLEAN DEFAULT 0,
                -- Loan permissions
                can_view_loans BOOLEAN DEFAULT 1,
                can_manage_loans BOOLEAN DEFAULT 0,
                -- Report permissions
                can_generate_reports BOOLEAN DEFAULT 1,
                can_export_data BOOLEAN DEFAULT 0,
                -- Parameter permissions
                can_view_parameters BOOLEAN DEFAULT 0,
                can_modify_parameters BOOLEAN DEFAULT 0,
                -- User management permissions (admin only)
                can_manage_users BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE(user_id)
            )
        """)

        # Create index
        conn.execute("CREATE INDEX IF NOT EXISTS idx_permissions_user ON user_permissions(user_id)")

        # Create trigger
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS update_permissions_timestamp
            AFTER UPDATE ON user_permissions
            FOR EACH ROW
            BEGIN
                UPDATE user_permissions SET updated_at = CURRENT_TIMESTAMP WHERE permission_id = NEW.permission_id;
            END
        """)

        print("✓ user_permissions table created")

        # Get all existing users
        cursor = conn.execute("SELECT user_id, role FROM users")
        users = cursor.fetchall()

        # Create default permissions for each user
        for user in users:
            user_id = user['user_id']
            role = user['role']

            # Check if permissions already exist
            cursor = conn.execute("SELECT user_id FROM user_permissions WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                print(f"  Permissions already exist for user {user_id}")
                continue

            # Admin gets full permissions, regular users get read-only
            if role == 'admin':
                conn.execute("""
                    INSERT INTO user_permissions (
                        user_id,
                        can_view_employees, can_edit_employees, can_delete_employees,
                        can_view_payroll, can_process_payroll, can_finalize_payroll,
                        can_view_loans, can_manage_loans,
                        can_generate_reports, can_export_data,
                        can_view_parameters, can_modify_parameters,
                        can_manage_users
                    ) VALUES (?, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
                """, (user_id,))
                print(f"✓ Created full admin permissions for user {user_id}")
            else:
                conn.execute("""
                    INSERT INTO user_permissions (
                        user_id,
                        can_view_employees, can_edit_employees, can_delete_employees,
                        can_view_payroll, can_process_payroll, can_finalize_payroll,
                        can_view_loans, can_manage_loans,
                        can_generate_reports, can_export_data,
                        can_view_parameters, can_modify_parameters,
                        can_manage_users
                    ) VALUES (?, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0)
                """, (user_id,))
                print(f"✓ Created read-only permissions for user {user_id}")

        conn.commit()
        print("\n✓ Permissions migration completed successfully!")
        return True

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        conn.rollback()
        return False


if __name__ == "__main__":
    DatabaseConnection.initialize()
    migrate_permissions()
    DatabaseConnection.close()
