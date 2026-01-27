"""
Employee Data Model
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Employee:
    """Employee data model"""

    employee_id: str
    first_name: str
    last_name: str
    full_name: str
    position: Optional[str] = None
    hire_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    seniority: Optional[float] = None
    status_code: Optional[str] = None
    agency_code: Optional[str] = None
    department_code: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    inps_number: Optional[str] = None
    inps_allocation_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_db_row(cls, row) -> 'Employee':
        """Create Employee instance from database row"""
        return cls(
            employee_id=row['employee_id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            full_name=row['full_name'],
            position=row['position'],
            hire_date=cls._parse_date(row['hire_date']),
            contract_end_date=cls._parse_date(row['contract_end_date']),
            seniority=row['seniority'],
            status_code=row['status_code'],
            agency_code=row['agency_code'],
            department_code=row['department_code'],
            category=row['category'],
            address=row['address'],
            inps_number=row['inps_number'],
            inps_allocation_number=row['inps_allocation_number'],
            bank_name=row['bank_name'],
            bank_account=row['bank_account'],
            is_active=bool(row['is_active']),
            created_at=cls._parse_datetime(row['created_at']),
            updated_at=cls._parse_datetime(row['updated_at'])
        )

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[date]:
        """Parse date string to date object"""
        if not date_str:
            return None
        try:
            if isinstance(date_str, date):
                return date_str
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not dt_str:
            return None
        try:
            if isinstance(dt_str, datetime):
                return dt_str
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            return None

    def to_dict(self) -> dict:
        """Convert employee to dictionary for database insert/update"""
        return {
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'position': self.position,
            'hire_date': self.hire_date.strftime('%Y-%m-%d') if self.hire_date else None,
            'contract_end_date': self.contract_end_date.strftime('%Y-%m-%d') if self.contract_end_date else None,
            'seniority': self.seniority,
            'status_code': self.status_code,
            'agency_code': self.agency_code,
            'department_code': self.department_code,
            'category': self.category,
            'address': self.address,
            'inps_number': self.inps_number,
            'inps_allocation_number': self.inps_allocation_number,
            'bank_name': self.bank_name,
            'bank_account': self.bank_account,
            'is_active': 1 if self.is_active else 0
        }

    def calculate_seniority(self, as_of_date: Optional[date] = None) -> float:
        """Calculate employee seniority in years"""
        if not self.hire_date:
            return 0.0

        end_date = as_of_date or date.today()
        delta = end_date - self.hire_date
        years = delta.days / 365.25
        return round(years, 2)

    def update_seniority(self):
        """Update the seniority field based on hire date"""
        self.seniority = self.calculate_seniority()

    def __str__(self) -> str:
        """String representation"""
        return f"{self.employee_id} - {self.full_name}"

    def __repr__(self) -> str:
        """Detailed representation"""
        return f"Employee(id={self.employee_id}, name={self.full_name}, position={self.position})"
