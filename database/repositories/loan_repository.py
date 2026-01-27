"""
Loan Repository
Database operations for loans and advances
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import sqlite3

from database.connection import DatabaseConnection


class LoanRepository:
    """Repository for loan and advance operations"""

    @staticmethod
    def _ensure_notes_column():
        """Ensure the notes column exists in loans_advances table"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.execute("PRAGMA table_info(loans_advances)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'notes' not in columns:
            try:
                conn.execute("ALTER TABLE loans_advances ADD COLUMN notes TEXT")
                conn.commit()
                print("Added 'notes' column to loans_advances table")
            except Exception as e:
                print(f"Could not add notes column: {e}")

    @staticmethod
    def create_loan(employee_id: str, loan_type: str, total_amount: float,
                   grant_date: date, duration_months: int, notes: str = "") -> int:
        """
        Create a new loan or advance

        Args:
            employee_id: Employee ID
            loan_type: Type (LOAN or ADVANCE)
            total_amount: Total loan amount
            grant_date: Date loan was granted
            duration_months: Number of months for repayment
            notes: Optional notes

        Returns:
            loan_id of created loan
        """
        conn = DatabaseConnection.get_connection()

        # Ensure notes column exists (for older databases)
        LoanRepository._ensure_notes_column()

        # Calculate monthly payment
        monthly_payment = total_amount / duration_months if duration_months > 0 else total_amount

        cursor = conn.execute("""
            INSERT INTO loans_advances (
                employee_id, loan_type, total_amount, remaining_balance,
                grant_date, duration_months, monthly_payment, is_active, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (employee_id, loan_type, total_amount, total_amount,
              grant_date, duration_months, monthly_payment, notes))

        loan_id = cursor.lastrowid

        # Create payment schedule
        LoanRepository._create_payment_schedule(loan_id, grant_date, duration_months, monthly_payment)

        conn.commit()
        return loan_id

    @staticmethod
    def _create_payment_schedule(loan_id: int, grant_date: date,
                                 duration_months: int, monthly_payment: float):
        """Create payment schedule for a loan"""
        conn = DatabaseConnection.get_connection()

        # Start payments from the next month
        payment_date = grant_date + relativedelta(months=1)

        for month in range(duration_months):
            conn.execute("""
                INSERT INTO loan_payments (
                    loan_id, payment_date, scheduled_amount, is_paid
                ) VALUES (?, ?, ?, 0)
            """, (loan_id, payment_date, monthly_payment))

            payment_date += relativedelta(months=1)

    @staticmethod
    def get_all_loans(include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        Get all loans with employee information

        Args:
            include_inactive: Whether to include fully paid/inactive loans

        Returns:
            List of loan dictionaries
        """
        conn = DatabaseConnection.get_connection()

        query = """
            SELECT
                l.*,
                e.full_name,
                e.position,
                e.department_code
            FROM loans_advances l
            JOIN employees e ON l.employee_id = e.employee_id
        """

        if not include_inactive:
            query += " WHERE l.is_active = 1"

        query += " ORDER BY l.grant_date DESC"

        cursor = conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_loan_by_id(loan_id: int) -> Optional[Dict[str, Any]]:
        """Get a single loan by ID"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.execute("""
            SELECT
                l.*,
                e.full_name,
                e.position
            FROM loans_advances l
            JOIN employees e ON l.employee_id = e.employee_id
            WHERE l.loan_id = ?
        """, (loan_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_employee_loans(employee_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all loans for an employee"""
        conn = DatabaseConnection.get_connection()

        query = "SELECT * FROM loans_advances WHERE employee_id = ?"
        params = [employee_id]

        if active_only:
            query += " AND is_active = 1"

        query += " ORDER BY grant_date DESC"

        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_payment_schedule(loan_id: int) -> List[Dict[str, Any]]:
        """Get payment schedule for a loan"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.execute("""
            SELECT * FROM loan_payments
            WHERE loan_id = ?
            ORDER BY payment_date
        """, (loan_id,))
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def record_payment(payment_id: int, actual_amount: float, payment_date: date = None) -> bool:
        """
        Record a loan payment

        Args:
            payment_id: Payment ID
            actual_amount: Amount actually paid
            payment_date: Date of payment (defaults to today)

        Returns:
            True if successful
        """
        try:
            conn = DatabaseConnection.get_connection()

            if payment_date is None:
                payment_date = date.today()

            # Get payment info
            cursor = conn.execute(
                "SELECT loan_id, scheduled_amount FROM loan_payments WHERE payment_id = ?",
                (payment_id,)
            )
            payment = cursor.fetchone()

            if not payment:
                return False

            # Mark payment as paid
            conn.execute("""
                UPDATE loan_payments
                SET is_paid = 1, actual_amount = ?, paid_date = ?
                WHERE payment_id = ?
            """, (actual_amount, payment_date, payment_id))

            # Update loan remaining balance
            loan_id = payment['loan_id']
            conn.execute("""
                UPDATE loans_advances
                SET remaining_balance = remaining_balance - ?
                WHERE loan_id = ?
            """, (actual_amount, loan_id))

            # Check if loan is fully paid
            cursor = conn.execute("""
                SELECT remaining_balance FROM loans_advances WHERE loan_id = ?
            """, (loan_id,))
            loan = cursor.fetchone()

            if loan and loan['remaining_balance'] <= 0:
                conn.execute("""
                    UPDATE loans_advances
                    SET is_active = 0, remaining_balance = 0
                    WHERE loan_id = ?
                """, (loan_id,))

            conn.commit()
            return True

        except Exception:
            conn.rollback()
            return False

    @staticmethod
    def get_monthly_deduction(employee_id: str, period_date: date) -> float:
        """
        Get total monthly loan deduction for an employee

        Args:
            employee_id: Employee ID
            period_date: Date of the payroll period

        Returns:
            Total deduction amount
        """
        conn = DatabaseConnection.get_connection()

        # Get all unpaid payments due for this period
        cursor = conn.execute("""
            SELECT SUM(lp.scheduled_amount) as total_deduction
            FROM loan_payments lp
            JOIN loans_advances l ON lp.loan_id = l.loan_id
            WHERE l.employee_id = ?
            AND l.is_active = 1
            AND lp.is_paid = 0
            AND lp.payment_date <= ?
        """, (employee_id, period_date))

        result = cursor.fetchone()
        return result['total_deduction'] or 0.0

    @staticmethod
    def update_loan(loan_id: int, notes: str = None, is_active: bool = None) -> bool:
        """Update loan details"""
        try:
            conn = DatabaseConnection.get_connection()

            updates = []
            params = []

            if notes is not None:
                updates.append("notes = ?")
                params.append(notes)

            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)

            if not updates:
                return True

            params.append(loan_id)
            query = f"UPDATE loans_advances SET {', '.join(updates)} WHERE loan_id = ?"

            conn.execute(query, params)
            conn.commit()
            return True

        except Exception:
            conn.rollback()
            return False

    @staticmethod
    def delete_loan(loan_id: int) -> bool:
        """Delete a loan and its payment schedule"""
        try:
            conn = DatabaseConnection.get_connection()

            # Delete payments first
            conn.execute("DELETE FROM loan_payments WHERE loan_id = ?", (loan_id,))

            # Delete loan
            conn.execute("DELETE FROM loans_advances WHERE loan_id = ?", (loan_id,))

            conn.commit()
            return True

        except Exception:
            conn.rollback()
            return False

    @staticmethod
    def get_loan_summary() -> Dict[str, Any]:
        """Get summary statistics for loans"""
        conn = DatabaseConnection.get_connection()

        cursor = conn.execute("""
            SELECT
                COUNT(*) as total_loans,
                SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_loans,
                SUM(CASE WHEN is_active = 1 THEN total_amount ELSE 0 END) as total_active_amount,
                SUM(CASE WHEN is_active = 1 THEN remaining_balance ELSE 0 END) as total_remaining
            FROM loans_advances
        """)

        return dict(cursor.fetchone())
