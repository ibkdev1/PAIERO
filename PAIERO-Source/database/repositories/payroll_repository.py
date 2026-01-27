"""
Payroll Repository
Database operations for payroll periods and records
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
import sqlite3

from database.connection import DatabaseConnection


class PayrollRepository:
    """Repository for payroll period and record operations"""

    @staticmethod
    def create_period(start_date: date, end_date: date,
                     payment_date: Optional[date] = None) -> int:
        """
        Create a new payroll period

        Args:
            start_date: Period start date
            end_date: Period end date
            payment_date: Scheduled payment date

        Returns:
            period_id of created period
        """
        conn = DatabaseConnection.get_connection()
        cursor = conn.execute("""
            INSERT INTO payroll_periods (
                period_start_date, period_end_date, payment_date, is_finalized
            ) VALUES (?, ?, ?, 0)
        """, (start_date, end_date, payment_date))
        conn.commit()
        return cursor.lastrowid

    @staticmethod
    def get_all_periods(include_finalized: bool = True) -> List[Dict[str, Any]]:
        """
        Get all payroll periods

        Args:
            include_finalized: Whether to include finalized periods

        Returns:
            List of period dictionaries
        """
        conn = DatabaseConnection.get_connection()

        query = "SELECT * FROM payroll_periods"
        if not include_finalized:
            query += " WHERE is_finalized = 0"
        query += " ORDER BY period_start_date DESC"

        cursor = conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_period_by_id(period_id: int) -> Optional[Dict[str, Any]]:
        """Get period by ID"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.execute(
            "SELECT * FROM payroll_periods WHERE period_id = ?",
            (period_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_latest_period() -> Optional[Dict[str, Any]]:
        """Get the most recent payroll period"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.execute("""
            SELECT * FROM payroll_periods
            ORDER BY period_start_date DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def finalize_period(period_id: int) -> bool:
        """
        Finalize a payroll period (lock it from editing)

        Args:
            period_id: Period to finalize

        Returns:
            True if successful
        """
        try:
            conn = DatabaseConnection.get_connection()
            conn.execute("""
                UPDATE payroll_periods
                SET is_finalized = 1
                WHERE period_id = ?
            """, (period_id,))
            conn.commit()
            return True
        except Exception:
            return False

    @staticmethod
    def delete_period(period_id: int) -> bool:
        """
        Delete a payroll period and all its records

        Args:
            period_id: Period to delete

        Returns:
            True if successful
        """
        try:
            conn = DatabaseConnection.get_connection()

            # Delete all records in this period first
            conn.execute(
                "DELETE FROM payroll_records WHERE period_id = ?",
                (period_id,)
            )

            # Delete the period
            conn.execute(
                "DELETE FROM payroll_periods WHERE period_id = ?",
                (period_id,)
            )

            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False

    @staticmethod
    def create_payroll_record(period_id: int, employee_id: str,
                             payroll_data: Dict[str, Any]) -> int:
        """
        Create or update a payroll record for an employee in a period

        Args:
            period_id: Payroll period ID
            employee_id: Employee ID
            payroll_data: Dictionary with all payroll fields

        Returns:
            record_id of created/updated record
        """
        conn = DatabaseConnection.get_connection()

        # Check if record already exists
        cursor = conn.execute("""
            SELECT record_id FROM payroll_records
            WHERE period_id = ? AND employee_id = ?
        """, (period_id, employee_id))
        existing = cursor.fetchone()

        if existing:
            # Update existing record
            record_id = existing['record_id']
            PayrollRepository.update_payroll_record(record_id, payroll_data)
            return record_id
        else:
            # Insert new record
            # Calculate total advances/loans deduction
            advances_total = (
                payroll_data.get('loan_deduction', 0) +
                payroll_data.get('advance_deduction', 0) +
                payroll_data.get('other_deductions', 0)
            )

            # Calculate total employer cost (taxes)
            total_employer = (
                payroll_data.get('inps_employer', 0) +
                payroll_data.get('amo_employer', 0) +
                payroll_data.get('taxe_logement', 0) +
                payroll_data.get('taxe_formation', 0) +
                payroll_data.get('taxe_emploi', 0) +
                payroll_data.get('contribution_cfe', 0)
            )

            cursor = conn.execute("""
                INSERT INTO payroll_records (
                    period_id, employee_id,
                    base_salary, days_worked, days_absent,
                    ind_transport, family_allowance, responsibility_allowance,
                    risk_premium, vehicle_allowance, overtime_pay,
                    ind_spe_1973, ind_cher_vie_1974,
                    gross_salary,
                    inps_employee, amo_employee, income_tax_net,
                    advances_loans_deduction,
                    net_salary, net_to_pay,
                    inps_employer, amo_employer,
                    tl_tax, tfp_tax, atej_tax, cfe_tax,
                    total_payroll_cost
                ) VALUES (
                    ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?,
                    ?, ?, ?,
                    ?,
                    ?, ?,
                    ?, ?,
                    ?, ?, ?, ?,
                    ?
                )
            """, (
                period_id, employee_id,
                payroll_data.get('base_salary', 0),
                payroll_data.get('days_worked', 26),
                payroll_data.get('days_absent', 0),
                payroll_data.get('transport_allowance', 0),
                payroll_data.get('family_allowance', 0),
                payroll_data.get('responsibility_allowance', 0),
                payroll_data.get('risk_allowance', 0),
                payroll_data.get('housing_allowance', 0),
                payroll_data.get('overtime_amount', 0),
                payroll_data.get('ind_spec_1973', 0),
                payroll_data.get('cher_vie_1974', 0),
                payroll_data.get('gross_salary', 0),
                payroll_data.get('inps_employee', 0),
                payroll_data.get('amo_employee', 0),
                payroll_data.get('income_tax_net', 0),
                advances_total,
                payroll_data.get('net_salary', 0),
                payroll_data.get('net_to_pay', 0),
                payroll_data.get('inps_employer', 0),
                payroll_data.get('amo_employer', 0),
                payroll_data.get('taxe_logement', 0),
                payroll_data.get('taxe_formation', 0),
                payroll_data.get('taxe_emploi', 0),
                payroll_data.get('contribution_cfe', 0),
                payroll_data.get('total_cost', 0)
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def update_payroll_record(record_id: int, payroll_data: Dict[str, Any]) -> bool:
        """
        Update an existing payroll record

        Args:
            record_id: Record ID to update
            payroll_data: Dictionary with payroll fields to update

        Returns:
            True if successful
        """
        try:
            # Calculate total advances/loans deduction
            advances_total = (
                payroll_data.get('loan_deduction', 0) +
                payroll_data.get('advance_deduction', 0) +
                payroll_data.get('other_deductions', 0)
            )

            conn = DatabaseConnection.get_connection()
            conn.execute("""
                UPDATE payroll_records SET
                    base_salary = ?,
                    days_worked = ?,
                    days_absent = ?,
                    ind_transport = ?,
                    family_allowance = ?,
                    responsibility_allowance = ?,
                    risk_premium = ?,
                    vehicle_allowance = ?,
                    overtime_pay = ?,
                    ind_spe_1973 = ?,
                    ind_cher_vie_1974 = ?,
                    gross_salary = ?,
                    inps_employee = ?,
                    amo_employee = ?,
                    income_tax_net = ?,
                    advances_loans_deduction = ?,
                    net_salary = ?,
                    net_to_pay = ?,
                    inps_employer = ?,
                    amo_employer = ?,
                    tl_tax = ?,
                    tfp_tax = ?,
                    atej_tax = ?,
                    cfe_tax = ?,
                    total_payroll_cost = ?
                WHERE record_id = ?
            """, (
                payroll_data.get('base_salary', 0),
                payroll_data.get('days_worked', 26),
                payroll_data.get('days_absent', 0),
                payroll_data.get('transport_allowance', 0),
                payroll_data.get('family_allowance', 0),
                payroll_data.get('responsibility_allowance', 0),
                payroll_data.get('risk_allowance', 0),
                payroll_data.get('housing_allowance', 0),
                payroll_data.get('overtime_amount', 0),
                payroll_data.get('ind_spec_1973', 0),
                payroll_data.get('cher_vie_1974', 0),
                payroll_data.get('gross_salary', 0),
                payroll_data.get('inps_employee', 0),
                payroll_data.get('amo_employee', 0),
                payroll_data.get('income_tax_net', 0),
                advances_total,
                payroll_data.get('net_salary', 0),
                payroll_data.get('net_to_pay', 0),
                payroll_data.get('inps_employer', 0),
                payroll_data.get('amo_employer', 0),
                payroll_data.get('taxe_logement', 0),
                payroll_data.get('taxe_formation', 0),
                payroll_data.get('taxe_emploi', 0),
                payroll_data.get('contribution_cfe', 0),
                payroll_data.get('total_cost', 0),
                record_id
            ))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False

    @staticmethod
    def get_records_by_period(period_id: int) -> List[Dict[str, Any]]:
        """
        Get all payroll records for a period

        Args:
            period_id: Period ID

        Returns:
            List of payroll record dictionaries with employee info
        """
        conn = DatabaseConnection.get_connection()
        cursor = conn.execute("""
            SELECT
                pr.*,
                e.full_name,
                e.position,
                e.status_code,
                e.category
            FROM payroll_records pr
            JOIN employees e ON pr.employee_id = e.employee_id
            WHERE pr.period_id = ?
            ORDER BY e.full_name
        """, (period_id,))
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_record_by_id(record_id: int) -> Optional[Dict[str, Any]]:
        """Get a single payroll record by ID"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.execute(
            "SELECT * FROM payroll_records WHERE record_id = ?",
            (record_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def delete_record(record_id: int) -> bool:
        """Delete a payroll record"""
        try:
            conn = DatabaseConnection.get_connection()
            conn.execute(
                "DELETE FROM payroll_records WHERE record_id = ?",
                (record_id,)
            )
            conn.commit()
            return True
        except Exception:
            return False

    @staticmethod
    def get_period_summary(period_id: int) -> Dict[str, Any]:
        """
        Get summary statistics for a payroll period

        Args:
            period_id: Period ID

        Returns:
            Dictionary with summary totals
        """
        conn = DatabaseConnection.get_connection()
        cursor = conn.execute("""
            SELECT
                COUNT(*) as employee_count,
                SUM(gross_salary) as total_gross,
                SUM(inps_employee) as total_inps_employee,
                SUM(amo_employee) as total_amo_employee,
                SUM(income_tax_net) as total_income_tax,
                SUM(loan_deduction) as total_loan_deductions,
                SUM(net_to_pay) as total_net_to_pay,
                SUM(inps_employer) as total_inps_employer,
                SUM(amo_employer) as total_amo_employer,
                SUM(taxe_logement + taxe_formation + taxe_emploi + contribution_cfe) as total_labor_taxes,
                SUM(total_cost) as total_cost
            FROM payroll_records
            WHERE period_id = ?
        """, (period_id,))

        row = cursor.fetchone()
        return dict(row) if row else {}

    @staticmethod
    def initialize_period_with_employees(period_id: int) -> int:
        """
        Initialize a period by creating payroll records for all active employees
        with their base salaries from the salary scale

        Args:
            period_id: Period ID to initialize

        Returns:
            Number of records created
        """
        conn = DatabaseConnection.get_connection()

        # Get all active employees with their base salary from salary scale
        cursor = conn.execute("""
            SELECT
                e.employee_id,
                e.status_code,
                e.category,
                COALESCE(s.adjusted_base_salary, 500000) as base_salary
            FROM employees e
            LEFT JOIN salary_scale_ccfc s ON e.category = s.category
            WHERE e.is_active = 1
        """)
        employees = cursor.fetchall()

        count = 0
        for emp in employees:
            # Check if record already exists
            existing = conn.execute("""
                SELECT record_id FROM payroll_records
                WHERE period_id = ? AND employee_id = ?
            """, (period_id, emp['employee_id'])).fetchone()

            if not existing:
                # Create basic payroll record with base salary from scale
                conn.execute("""
                    INSERT INTO payroll_records (
                        period_id, employee_id, base_salary, days_worked, days_absent
                    ) VALUES (?, ?, ?, 26, 0)
                """, (period_id, emp['employee_id'], emp['base_salary']))
                count += 1

        conn.commit()
        return count
