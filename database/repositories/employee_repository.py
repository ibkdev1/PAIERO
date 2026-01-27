"""
Employee Repository
Handles all database operations for employees
"""

import sys
import os
from typing import List, Optional
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import DatabaseConnection
from models.employee import Employee


class EmployeeRepository:
    """Repository for employee CRUD operations"""

    @staticmethod
    def get_all(include_inactive: bool = False) -> List[Employee]:
        """
        Get all employees

        Args:
            include_inactive: Include inactive employees

        Returns:
            List of Employee objects
        """
        query = "SELECT * FROM employees"

        if not include_inactive:
            query += " WHERE is_active = 1"

        query += " ORDER BY employee_id"

        rows = DatabaseConnection.fetch_all(query)
        return [Employee.from_db_row(row) for row in rows]

    @staticmethod
    def get_by_id(employee_id: str) -> Optional[Employee]:
        """
        Get employee by ID

        Args:
            employee_id: Employee ID

        Returns:
            Employee object or None
        """
        query = "SELECT * FROM employees WHERE employee_id = ?"
        row = DatabaseConnection.fetch_one(query, (employee_id,))

        if row:
            return Employee.from_db_row(row)
        return None

    @staticmethod
    def search(search_term: str, include_inactive: bool = False) -> List[Employee]:
        """
        Search employees by name, ID, or position

        Args:
            search_term: Search term
            include_inactive: Include inactive employees

        Returns:
            List of matching Employee objects
        """
        search_pattern = f"%{search_term}%"

        query = """
            SELECT * FROM employees
            WHERE (
                employee_id LIKE ? OR
                first_name LIKE ? OR
                last_name LIKE ? OR
                full_name LIKE ? OR
                position LIKE ?
            )
        """

        params = [search_pattern] * 5

        if not include_inactive:
            query += " AND is_active = 1"

        query += " ORDER BY employee_id"

        rows = DatabaseConnection.fetch_all(query, tuple(params))
        return [Employee.from_db_row(row) for row in rows]

    @staticmethod
    def filter_by_department(department_code: str, include_inactive: bool = False) -> List[Employee]:
        """
        Filter employees by department

        Args:
            department_code: Department code
            include_inactive: Include inactive employees

        Returns:
            List of Employee objects
        """
        query = "SELECT * FROM employees WHERE department_code = ?"
        params = [department_code]

        if not include_inactive:
            query += " AND is_active = 1"

        query += " ORDER BY employee_id"

        rows = DatabaseConnection.fetch_all(query, tuple(params))
        return [Employee.from_db_row(row) for row in rows]

    @staticmethod
    def filter_by_category(category: str, include_inactive: bool = False) -> List[Employee]:
        """
        Filter employees by category

        Args:
            category: Category code
            include_inactive: Include inactive employees

        Returns:
            List of Employee objects
        """
        query = "SELECT * FROM employees WHERE category = ?"
        params = [category]

        if not include_inactive:
            query += " AND is_active = 1"

        query += " ORDER BY employee_id"

        rows = DatabaseConnection.fetch_all(query, tuple(params))
        return [Employee.from_db_row(row) for row in rows]

    @staticmethod
    def create(employee: Employee) -> bool:
        """
        Create a new employee

        Args:
            employee: Employee object

        Returns:
            True if successful, False otherwise
        """
        try:
            # Update seniority before saving
            employee.update_seniority()

            data = employee.to_dict()

            query = """
                INSERT INTO employees (
                    employee_id, first_name, last_name, full_name, position,
                    hire_date, contract_end_date, seniority, status_code,
                    agency_code, department_code, category, address,
                    inps_number, inps_allocation_number, bank_name,
                    bank_account, is_active
                ) VALUES (
                    :employee_id, :first_name, :last_name, :full_name, :position,
                    :hire_date, :contract_end_date, :seniority, :status_code,
                    :agency_code, :department_code, :category, :address,
                    :inps_number, :inps_allocation_number, :bank_name,
                    :bank_account, :is_active
                )
            """

            conn = DatabaseConnection.get_connection()
            conn.execute(query, data)
            conn.commit()

            return True

        except Exception as e:
            print(f"Error creating employee: {e}")
            DatabaseConnection.rollback()
            return False

    @staticmethod
    def update(employee: Employee) -> bool:
        """
        Update an existing employee

        Args:
            employee: Employee object with updated data

        Returns:
            True if successful, False otherwise
        """
        try:
            # Update seniority before saving
            employee.update_seniority()

            data = employee.to_dict()
            data['updated_employee_id'] = employee.employee_id

            query = """
                UPDATE employees SET
                    first_name = :first_name,
                    last_name = :last_name,
                    full_name = :full_name,
                    position = :position,
                    hire_date = :hire_date,
                    contract_end_date = :contract_end_date,
                    seniority = :seniority,
                    status_code = :status_code,
                    agency_code = :agency_code,
                    department_code = :department_code,
                    category = :category,
                    address = :address,
                    inps_number = :inps_number,
                    inps_allocation_number = :inps_allocation_number,
                    bank_name = :bank_name,
                    bank_account = :bank_account,
                    is_active = :is_active
                WHERE employee_id = :updated_employee_id
            """

            conn = DatabaseConnection.get_connection()
            conn.execute(query, data)
            conn.commit()

            return True

        except Exception as e:
            print(f"Error updating employee: {e}")
            DatabaseConnection.rollback()
            return False

    @staticmethod
    def delete(employee_id: str) -> bool:
        """
        Delete an employee (soft delete - sets is_active to 0)

        Args:
            employee_id: Employee ID

        Returns:
            True if successful, False otherwise
        """
        try:
            query = "UPDATE employees SET is_active = 0 WHERE employee_id = ?"
            conn = DatabaseConnection.get_connection()
            conn.execute(query, (employee_id,))
            conn.commit()
            return True

        except Exception as e:
            print(f"Error deleting employee: {e}")
            DatabaseConnection.rollback()
            return False

    @staticmethod
    def restore(employee_id: str) -> bool:
        """
        Restore a deleted employee (sets is_active to 1)

        Args:
            employee_id: Employee ID

        Returns:
            True if successful, False otherwise
        """
        try:
            query = "UPDATE employees SET is_active = 1 WHERE employee_id = ?"
            conn = DatabaseConnection.get_connection()
            conn.execute(query, (employee_id,))
            conn.commit()
            return True

        except Exception as e:
            print(f"Error restoring employee: {e}")
            DatabaseConnection.rollback()
            return False

    @staticmethod
    def exists(employee_id: str) -> bool:
        """
        Check if employee exists

        Args:
            employee_id: Employee ID

        Returns:
            True if exists, False otherwise
        """
        query = "SELECT COUNT(*) as count FROM employees WHERE employee_id = ?"
        row = DatabaseConnection.fetch_one(query, (employee_id,))
        return row['count'] > 0 if row else False

    @staticmethod
    def get_count(include_inactive: bool = False) -> int:
        """
        Get total employee count

        Args:
            include_inactive: Include inactive employees

        Returns:
            Employee count
        """
        query = "SELECT COUNT(*) as count FROM employees"

        if not include_inactive:
            query += " WHERE is_active = 1"

        row = DatabaseConnection.fetch_one(query)
        return row['count'] if row else 0

    @staticmethod
    def get_next_employee_id() -> str:
        """
        Get the next available employee ID

        Returns:
            Next employee ID (e.g., "001", "002", etc.)
        """
        query = "SELECT employee_id FROM employees ORDER BY employee_id DESC LIMIT 1"
        row = DatabaseConnection.fetch_one(query)

        if row:
            try:
                last_id = int(row['employee_id'])
                next_id = last_id + 1
                return f"{next_id:03d}"
            except ValueError:
                return "001"
        else:
            return "001"

    @staticmethod
    def get_departments() -> List[str]:
        """
        Get list of unique departments

        Returns:
            List of department codes
        """
        query = """
            SELECT DISTINCT department_code
            FROM employees
            WHERE department_code IS NOT NULL
            ORDER BY department_code
        """
        rows = DatabaseConnection.fetch_all(query)
        return [row['department_code'] for row in rows]

    @staticmethod
    def get_categories() -> List[str]:
        """
        Get list of unique categories

        Returns:
            List of category codes
        """
        query = """
            SELECT DISTINCT category
            FROM employees
            WHERE category IS NOT NULL
            ORDER BY category
        """
        rows = DatabaseConnection.fetch_all(query)
        return [row['category'] for row in rows]
