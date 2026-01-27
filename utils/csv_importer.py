"""
CSV Import Utility
Migrates data from existing CSV files to SQLite database
"""

import pandas as pd
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import DatabaseConnection


class CSVImporter:
    """Handles CSV data import into SQLite database"""

    def __init__(self, csv_directory: str = None):
        """
        Initialize CSV importer

        Args:
            csv_directory: Directory containing CSV files
                          If None, uses current directory
        """
        self.csv_directory = csv_directory or os.getcwd()
        self.db = None
        self.import_stats = {
            'parameters': 0,
            'tax_brackets': 0,
            'salary_scale': 0,
            'employees': 0,
            'payroll_periods': 0,
            'payroll_records': 0,
            'loans': 0,
            'loan_payments': 0
        }

    def initialize_database(self, db_path: str = None):
        """Initialize database connection"""
        self.db = DatabaseConnection.initialize(db_path)
        print(f"Database initialized at: {DatabaseConnection.get_database_path()}")

    def import_all(self):
        """Import all CSV files in correct order"""
        print("\n" + "=" * 60)
        print("PAIERO - CSV Data Import")
        print("=" * 60 + "\n")

        try:
            # Import in dependency order
            print("Step 1/5: Importing parameters and configuration...")
            self.import_parameters()

            print("\nStep 2/5: Importing CCFC salary scale...")
            self.import_salary_scale()

            print("\nStep 3/5: Importing employee and payroll data...")
            self.import_salary_data()

            print("\nStep 4/5: Importing loan and advance data...")
            self.import_loan_data()

            print("\nStep 5/5: Validating import...")
            self.validate_import()

            # Print summary
            self.print_summary()

            print("\n" + "=" * 60)
            print("Import completed successfully!")
            print("=" * 60 + "\n")

        except Exception as e:
            print(f"\nERROR during import: {e}")
            import traceback
            traceback.print_exc()
            DatabaseConnection.rollback()
            raise

    def import_parameters(self):
        """Import parameters from Paramètres.csv"""
        file_path = os.path.join(self.csv_directory, 'Paramètres.csv')

        if not os.path.exists(file_path):
            print(f"  WARNING: {file_path} not found, skipping...")
            return

        df = pd.read_csv(file_path, encoding='utf-8')

        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        # Import status codes (employee family status)
        # Look for columns with status information
        status_count = 0
        tax_count = 0

        for idx, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row).all():
                continue

            # Try to identify status codes (C0-C15, M0-M20)
            # Look for patterns in the first few columns
            first_col = str(row.iloc[0]) if len(row) > 0 else ""

            # Check if this is a status code row
            if first_col.startswith('C') or first_col.startswith('M'):
                status_code = first_col
                description = str(row.iloc[1]) if len(row) > 1 and not pd.isna(row.iloc[1]) else ""
                allowance = float(row.iloc[2]) if len(row) > 2 and not pd.isna(row.iloc[2]) else 0.0
                reduction_rate = float(row.iloc[3]) if len(row) > 3 and not pd.isna(row.iloc[3]) else 0.0

                cursor.execute("""
                    INSERT OR REPLACE INTO parameters
                    (param_type, param_code, param_value, numeric_value, description)
                    VALUES (?, ?, ?, ?, ?)
                """, ('STATUS', status_code, str(allowance), reduction_rate, description))

                status_count += 1

            # Check if this is a tax bracket row
            # Tax brackets have numeric income ranges
            elif isinstance(row.iloc[0], (int, float)) and not pd.isna(row.iloc[0]):
                try:
                    min_income = float(row.iloc[0])
                    max_income = float(row.iloc[1]) if len(row) > 1 and not pd.isna(row.iloc[1]) else None
                    tax_rate = float(row.iloc[2]) if len(row) > 2 and not pd.isna(row.iloc[2]) else 0.0
                    cumulative = float(row.iloc[3]) if len(row) > 3 and not pd.isna(row.iloc[3]) else 0.0

                    cursor.execute("""
                        INSERT INTO tax_brackets
                        (min_income, max_income, tax_rate, cumulative_tax, effective_date)
                        VALUES (?, ?, ?, ?, ?)
                    """, (min_income, max_income, tax_rate / 100, cumulative, datetime.now().date()))

                    tax_count += 1
                except (ValueError, TypeError):
                    pass  # Skip invalid rows

        conn.commit()

        self.import_stats['parameters'] = status_count
        self.import_stats['tax_brackets'] = tax_count

        print(f"  ✓ Imported {status_count} status codes")
        print(f"  ✓ Imported {tax_count} tax brackets")

    def import_salary_scale(self):
        """Import salary scale from Salaires_actualisés_CCFC.csv"""
        file_path = os.path.join(self.csv_directory, 'Salaires_actualisés_CCFC.csv')

        if not os.path.exists(file_path):
            print(f"  WARNING: {file_path} not found, skipping...")
            return

        df = pd.read_csv(file_path, encoding='utf-8')

        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        count = 0
        for idx, row in df.iterrows():
            # Skip header rows and empty rows
            if pd.isna(row).all() or idx < 3:
                continue

            # First column should be category
            category = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else None

            if category and ('Cat' in category or 'Ech' in category):
                # Extract all salary components
                try:
                    cursor.execute("""
                        INSERT INTO salary_scale_ccfc
                        (category, base_salary_1958, ind_spe_1973, ind_cher_vie_1974,
                         maj_1976, maj_1978, maj_1980, ind_spe_1982, maj_3000_or_10pct,
                         ind_sol_1991, maj_pre_1994, maj_1994, maj_1997, maj_1998,
                         maj_1999, maj_2008, maj_2009, total_gross, cumulative_maj,
                         adjusted_base_salary, effective_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        category,
                        float(row.iloc[1]) if len(row) > 1 and not pd.isna(row.iloc[1]) else 0.0,
                        float(row.iloc[2]) if len(row) > 2 and not pd.isna(row.iloc[2]) else 0.0,
                        float(row.iloc[3]) if len(row) > 3 and not pd.isna(row.iloc[3]) else 0.0,
                        float(row.iloc[4]) if len(row) > 4 and not pd.isna(row.iloc[4]) else 0.0,
                        float(row.iloc[5]) if len(row) > 5 and not pd.isna(row.iloc[5]) else 0.0,
                        float(row.iloc[6]) if len(row) > 6 and not pd.isna(row.iloc[6]) else 0.0,
                        float(row.iloc[7]) if len(row) > 7 and not pd.isna(row.iloc[7]) else 0.0,
                        float(row.iloc[8]) if len(row) > 8 and not pd.isna(row.iloc[8]) else 0.0,
                        float(row.iloc[9]) if len(row) > 9 and not pd.isna(row.iloc[9]) else 0.0,
                        float(row.iloc[10]) if len(row) > 10 and not pd.isna(row.iloc[10]) else 0.0,
                        float(row.iloc[11]) if len(row) > 11 and not pd.isna(row.iloc[11]) else 0.0,
                        float(row.iloc[12]) if len(row) > 12 and not pd.isna(row.iloc[12]) else 0.0,
                        float(row.iloc[13]) if len(row) > 13 and not pd.isna(row.iloc[13]) else 0.0,
                        float(row.iloc[14]) if len(row) > 14 and not pd.isna(row.iloc[14]) else 0.0,
                        float(row.iloc[15]) if len(row) > 15 and not pd.isna(row.iloc[15]) else 0.0,
                        float(row.iloc[16]) if len(row) > 16 and not pd.isna(row.iloc[16]) else 0.0,
                        float(row.iloc[17]) if len(row) > 17 and not pd.isna(row.iloc[17]) else 0.0,
                        float(row.iloc[18]) if len(row) > 18 and not pd.isna(row.iloc[18]) else 0.0,
                        float(row.iloc[19]) if len(row) > 19 and not pd.isna(row.iloc[19]) else 0.0,
                        datetime.now().date()
                    ))
                    count += 1
                except Exception as e:
                    print(f"  Warning: Could not import category {category}: {e}")
                    continue

        conn.commit()
        self.import_stats['salary_scale'] = count
        print(f"  ✓ Imported {count} salary scale entries")

    def import_salary_data(self):
        """Import employee and payroll data from Salaire.csv"""
        file_path = os.path.join(self.csv_directory, 'Salaire.csv')

        if not os.path.exists(file_path):
            print(f"  WARNING: {file_path} not found, skipping...")
            return

        df = pd.read_csv(file_path, encoding='utf-8')

        # Extract period information from header (first few rows)
        period_start = None
        period_end = None

        # Try to find period dates in first few rows
        for idx in range(min(5, len(df))):
            row_str = ' '.join([str(v) for v in df.iloc[idx].values if not pd.isna(v)])
            if '2019-03-01' in row_str:
                period_start = '2019-03-01'
            if '2019-03-31' in row_str:
                period_end = '2019-03-31'

        if not period_start:
            period_start = '2019-03-01'
        if not period_end:
            period_end = '2019-03-31'

        # Create payroll period
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO payroll_periods
            (period_start_date, period_end_date, payment_date, is_finalized)
            VALUES (?, ?, ?, ?)
        """, (period_start, period_end, period_end, 0))

        period_id = cursor.lastrowid
        if period_id == 0:
            # Period already exists, get its ID
            cursor.execute(
                "SELECT period_id FROM payroll_periods WHERE period_start_date = ? AND period_end_date = ?",
                (period_start, period_end)
            )
            result = cursor.fetchone()
            period_id = result[0] if result else 1

        # Find the data start row (skip header rows)
        data_start_row = 0
        for idx, row in df.iterrows():
            # Look for the row where employee data starts (has employee ID pattern)
            first_col = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else ""
            if first_col.isdigit() and len(first_col) == 3:
                data_start_row = idx
                break

        if data_start_row == 0:
            print("  WARNING: Could not find employee data rows")
            return

        # Import employees and payroll records
        employee_count = 0
        payroll_count = 0

        for idx in range(data_start_row, len(df)):
            row = df.iloc[idx]

            # Skip empty rows
            if pd.isna(row).all():
                continue

            # Extract employee ID
            employee_id = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else None
            if not employee_id or not employee_id.isdigit():
                continue

            # Ensure 3-digit format
            employee_id = employee_id.zfill(3)

            # Extract employee data
            first_name = str(row.iloc[1]) if len(row) > 1 and not pd.isna(row.iloc[1]) else ""
            last_name = str(row.iloc[2]) if len(row) > 2 and not pd.isna(row.iloc[2]) else ""
            full_name = f"{first_name} {last_name}".strip()
            position = str(row.iloc[3]) if len(row) > 3 and not pd.isna(row.iloc[3]) else ""

            # Insert employee (ignore if exists)
            cursor.execute("""
                INSERT OR IGNORE INTO employees
                (employee_id, first_name, last_name, full_name, position, hire_date, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (employee_id, first_name, last_name, full_name, position, datetime.now().date(), 1))

            if cursor.rowcount > 0:
                employee_count += 1

            # Import payroll record for this employee
            # This is a simplified import - adjust column indices based on actual CSV structure
            cursor.execute("""
                INSERT OR REPLACE INTO payroll_records
                (period_id, employee_id, days_worked, days_absent, base_salary, gross_salary,
                 net_salary, net_to_pay)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                period_id,
                employee_id,
                30,  # Default days worked
                0,   # Default days absent
                0.0,  # Will be calculated
                0.0,  # Will be calculated
                0.0,  # Will be calculated
                0.0   # Will be calculated
            ))

            payroll_count += 1

        conn.commit()

        self.import_stats['employees'] = employee_count
        self.import_stats['payroll_periods'] = 1
        self.import_stats['payroll_records'] = payroll_count

        print(f"  ✓ Imported {employee_count} employees")
        print(f"  ✓ Created 1 payroll period ({period_start} to {period_end})")
        print(f"  ✓ Imported {payroll_count} payroll records")

    def import_loan_data(self):
        """Import loan data from Avance_&_Prêt.csv"""
        file_path = os.path.join(self.csv_directory, 'Avance_&_Prêt.csv')

        if not os.path.exists(file_path):
            print(f"  WARNING: {file_path} not found, skipping...")
            return

        df = pd.read_csv(file_path, encoding='utf-8')

        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        loan_count = 0
        payment_count = 0

        # Find data start row
        data_start_row = 0
        for idx, row in df.iterrows():
            first_col = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else ""
            if first_col.isdigit() and len(first_col) == 3:
                data_start_row = idx
                break

        # Import loans
        for idx in range(data_start_row, len(df)):
            row = df.iloc[idx]

            if pd.isna(row).all():
                continue

            employee_id = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else None
            if not employee_id or not employee_id.isdigit():
                continue

            employee_id = employee_id.zfill(3)

            # Extract loan details (adjust indices based on actual CSV structure)
            loan_type = str(row.iloc[3]) if len(row) > 3 and not pd.isna(row.iloc[3]) else "Prêt"
            total_amount = float(row.iloc[4]) if len(row) > 4 and not pd.isna(row.iloc[4]) else 0.0
            remaining = float(row.iloc[5]) if len(row) > 5 and not pd.isna(row.iloc[5]) else total_amount

            if total_amount > 0:
                cursor.execute("""
                    INSERT INTO loans_advances
                    (employee_id, loan_type, total_amount, remaining_balance, grant_date,
                     duration_months, monthly_payment, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    employee_id,
                    loan_type,
                    total_amount,
                    remaining,
                    datetime.now().date(),
                    12,  # Default duration
                    total_amount / 12,  # Default monthly payment
                    1 if remaining > 0 else 0
                ))

                loan_count += 1

        conn.commit()

        self.import_stats['loans'] = loan_count
        print(f"  ✓ Imported {loan_count} loans/advances")

    def validate_import(self):
        """Validate that import was successful"""
        conn = DatabaseConnection.get_connection()

        # Check table counts
        tables = [
            'employees', 'payroll_periods', 'payroll_records',
            'loans_advances', 'salary_scale_ccfc', 'parameters', 'tax_brackets'
        ]

        print("\n  Validating import...")
        for table in tables:
            cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()[0]
            print(f"    - {table}: {count} records")

    def print_summary(self):
        """Print import summary"""
        print("\n" + "=" * 60)
        print("IMPORT SUMMARY")
        print("=" * 60)
        print(f"  Parameters (status codes):  {self.import_stats['parameters']}")
        print(f"  Tax brackets:               {self.import_stats['tax_brackets']}")
        print(f"  Salary scale entries:       {self.import_stats['salary_scale']}")
        print(f"  Employees:                  {self.import_stats['employees']}")
        print(f"  Payroll periods:            {self.import_stats['payroll_periods']}")
        print(f"  Payroll records:            {self.import_stats['payroll_records']}")
        print(f"  Loans/Advances:             {self.import_stats['loans']}")
        print("=" * 60)


def main():
    """Main import function"""
    import argparse

    parser = argparse.ArgumentParser(description='Import CSV data to PAIERO database')
    parser.add_argument('--csv-dir', default='.', help='Directory containing CSV files')
    parser.add_argument('--db-path', default='paiero.db', help='Database file path')

    args = parser.parse_args()

    # Create importer
    importer = CSVImporter(csv_directory=args.csv_dir)

    # Initialize database
    importer.initialize_database(db_path=args.db_path)

    # Import all data
    importer.import_all()

    # Close database
    DatabaseConnection.close()


if __name__ == "__main__":
    main()
