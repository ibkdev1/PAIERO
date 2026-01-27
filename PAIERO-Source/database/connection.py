"""
Database Connection Manager
Handles SQLite database connections and initialization
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional


class DatabaseConnection:
    """Singleton database connection manager"""

    _instance: Optional['DatabaseConnection'] = None
    _connection: Optional[sqlite3.Connection] = None
    _database_path: Optional[str] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls, database_path: str = None) -> 'DatabaseConnection':
        """
        Initialize the database connection

        Args:
            database_path: Path to the SQLite database file
                          If None, uses platform-specific application data directory

        Returns:
            DatabaseConnection instance
        """
        instance = cls()

        if database_path is None:
            # Import here to avoid circular imports
            from config import DATABASE_PATH
            database_path = DATABASE_PATH

        instance._database_path = database_path

        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(database_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        # Connect to database
        instance._connection = sqlite3.connect(
            database_path,
            check_same_thread=False  # Allow multi-threaded access
        )

        # Enable foreign key constraints
        instance._connection.execute("PRAGMA foreign_keys = ON")

        # Set row factory to return dict-like objects
        instance._connection.row_factory = sqlite3.Row

        # Initialize schema if database is empty
        instance._initialize_schema()

        return instance

    def _initialize_schema(self):
        """Initialize database schema if tables don't exist"""
        # Check if employees table exists
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='employees'"
        )

        if cursor.fetchone() is None:
            # Database is empty, create schema
            schema_path = os.path.join(
                os.path.dirname(__file__),
                'schema.sql'
            )

            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()

                # Execute schema (split by semicolon to handle multiple statements)
                self._connection.executescript(schema_sql)
                self._connection.commit()
                print(f"Database schema initialized at {self._database_path}")

                # Create default admin account if no users exist
                from database.auth import AuthManager
                AuthManager.create_default_admin()
            else:
                raise FileNotFoundError(f"Schema file not found: {schema_path}")
        else:
            # Database exists, run migrations for any missing columns
            self._run_migrations()

    def _run_migrations(self):
        """Run database migrations to add any missing columns"""
        cursor = self._connection.cursor()

        # Migration 1: Add 'notes' column to loans_advances if it doesn't exist
        cursor.execute("PRAGMA table_info(loans_advances)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'notes' not in columns:
            try:
                cursor.execute("ALTER TABLE loans_advances ADD COLUMN notes TEXT")
                self._connection.commit()
                print("Migration: Added 'notes' column to loans_advances")
            except Exception as e:
                print(f"Migration warning: {e}")

        # Migration 2: Fix loan_payments.period_id to allow NULL
        # Check if period_id has NOT NULL constraint
        cursor.execute("PRAGMA table_info(loan_payments)")
        columns = cursor.fetchall()

        period_id_not_null = False
        for col in columns:
            if col[1] == 'period_id' and col[3] == 1:  # col[3] is notnull flag
                period_id_not_null = True
                break

        if period_id_not_null:
            # Need to recreate table with nullable period_id
            try:
                print("Migration: Fixing loan_payments.period_id constraint...")
                cursor.execute("BEGIN TRANSACTION")

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

                # Copy existing data
                cursor.execute("""
                    INSERT INTO loan_payments_new
                    SELECT * FROM loan_payments
                """)

                # Drop old table
                cursor.execute("DROP TABLE loan_payments")

                # Rename new table
                cursor.execute("ALTER TABLE loan_payments_new RENAME TO loan_payments")

                # Recreate indexes
                cursor.execute("CREATE INDEX idx_payments_loan ON loan_payments(loan_id)")
                cursor.execute("CREATE INDEX idx_payments_period ON loan_payments(period_id)")
                cursor.execute("CREATE INDEX idx_payments_status ON loan_payments(is_paid)")

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

                self._connection.commit()
                print("Migration: Successfully fixed loan_payments.period_id constraint")
            except Exception as e:
                self._connection.rollback()
                print(f"Migration error (loan_payments): {e}")
                print("You may need to manually fix the loan_payments table")

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        """
        Get the current database connection

        Returns:
            sqlite3.Connection object

        Raises:
            RuntimeError: If database not initialized
        """
        if cls._instance is None or cls._instance._connection is None:
            raise RuntimeError(
                "Database not initialized. Call DatabaseConnection.initialize() first."
            )

        return cls._instance._connection

    @classmethod
    def close(cls):
        """Close the database connection"""
        if cls._instance and cls._instance._connection:
            cls._instance._connection.close()
            cls._instance._connection = None
            print("Database connection closed")

    @classmethod
    def commit(cls):
        """Commit current transaction"""
        if cls._instance and cls._instance._connection:
            cls._instance._connection.commit()

    @classmethod
    def rollback(cls):
        """Rollback current transaction"""
        if cls._instance and cls._instance._connection:
            cls._instance._connection.rollback()

    @classmethod
    def execute_query(cls, query: str, parameters: tuple = ()) -> sqlite3.Cursor:
        """
        Execute a SQL query

        Args:
            query: SQL query string
            parameters: Query parameters

        Returns:
            Cursor object with results
        """
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        return cursor

    @classmethod
    def execute_many(cls, query: str, parameters_list: list):
        """
        Execute a SQL query with multiple parameter sets

        Args:
            query: SQL query string
            parameters_list: List of parameter tuples
        """
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, parameters_list)
        conn.commit()

    @classmethod
    def fetch_one(cls, query: str, parameters: tuple = ()) -> Optional[sqlite3.Row]:
        """
        Execute query and fetch one result

        Args:
            query: SQL query string
            parameters: Query parameters

        Returns:
            Single row result or None
        """
        cursor = cls.execute_query(query, parameters)
        return cursor.fetchone()

    @classmethod
    def fetch_all(cls, query: str, parameters: tuple = ()) -> list:
        """
        Execute query and fetch all results

        Args:
            query: SQL query string
            parameters: Query parameters

        Returns:
            List of row results
        """
        cursor = cls.execute_query(query, parameters)
        return cursor.fetchall()

    @classmethod
    def get_database_path(cls) -> Optional[str]:
        """Get the current database file path"""
        if cls._instance:
            return cls._instance._database_path
        return None

    @classmethod
    def backup_database(cls, backup_path: str):
        """
        Create a backup of the database

        Args:
            backup_path: Path for the backup file
        """
        import shutil

        if cls._instance and cls._instance._database_path:
            # Commit any pending transactions
            cls.commit()

            # Create backup directory if needed
            backup_dir = os.path.dirname(backup_path)
            if backup_dir and not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            # Copy database file
            shutil.copy2(cls._instance._database_path, backup_path)
            print(f"Database backed up to {backup_path}")
        else:
            raise RuntimeError("Database not initialized")


def get_db() -> sqlite3.Connection:
    """
    Convenience function to get database connection

    Returns:
        sqlite3.Connection object
    """
    return DatabaseConnection.get_connection()


if __name__ == "__main__":
    # Test the database connection
    print("Testing database connection...")

    # Initialize database
    db = DatabaseConnection.initialize()
    print(f"Database initialized at: {DatabaseConnection.get_database_path()}")

    # Test query
    cursor = DatabaseConnection.execute_query(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )

    tables = cursor.fetchall()
    print(f"\nCreated tables ({len(tables)}):")
    for table in tables:
        print(f"  - {table['name']}")

    # Close connection
    DatabaseConnection.close()
    print("\nDatabase connection test completed successfully!")
