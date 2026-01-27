"""
Payroll Calculator
Complete payroll calculation engine with all salary components and deductions
"""

from typing import Dict, Optional
from dataclasses import dataclass
from decimal import Decimal

from business.tax_calculator import TaxCalculator
from config import (
    INPS_EMPLOYEE_RATE, INPS_EMPLOYER_RATE,
    AMO_EMPLOYEE_RATE, AMO_EMPLOYER_RATE
)


@dataclass
class PayrollInput:
    """Input data for payroll calculation"""
    employee_id: str
    base_salary: float
    status_code: str = ""

    # Days worked
    days_worked: int = 26
    days_absent: int = 0

    # Allowances
    transport_allowance: float = 0.0
    family_allowance: float = 0.0
    responsibility_allowance: float = 0.0
    risk_allowance: float = 0.0
    housing_allowance: float = 0.0
    overtime_amount: float = 0.0
    bonus_amount: float = 0.0

    # Fixed historical allowances (from CCFC)
    ind_spec_1973: float = 0.0
    cher_vie_1974: float = 0.0

    # Deductions (other than INPS/AMO/Tax)
    loan_deduction: float = 0.0
    advance_deduction: float = 0.0
    other_deductions: float = 0.0


@dataclass
class PayrollResult:
    """Result of payroll calculation"""
    employee_id: str

    # Salary components
    base_salary: float
    days_worked: int
    days_absent: int
    adjusted_base_salary: float  # After absence deduction

    # Allowances
    transport_allowance: float
    family_allowance: float
    responsibility_allowance: float
    risk_allowance: float
    housing_allowance: float
    overtime_amount: float
    bonus_amount: float
    ind_spec_1973: float
    cher_vie_1974: float
    total_allowances: float

    # Gross salary
    gross_salary: float

    # Employee deductions
    inps_employee: float
    amo_employee: float
    income_tax_net: float
    loan_deduction: float
    advance_deduction: float
    other_deductions: float
    total_deductions: float

    # Net amounts
    net_salary: float  # After INPS, AMO, Tax
    net_to_pay: float  # After all deductions including loans

    # Employer costs
    inps_employer: float
    amo_employer: float
    total_employer_cost: float

    # Labor taxes (employer only)
    taxe_logement: float  # TL: 1%
    taxe_formation: float  # TFP: 2%
    taxe_emploi: float  # ATEJ: 2%
    contribution_cfe: float  # CFE: 3.5%
    total_labor_taxes: float

    # Grand total
    total_cost: float  # Gross + Employer costs + Labor taxes


class PayrollCalculator:
    """
    Complete payroll calculation engine

    Calculation flow:
    1. Adjust base salary for absences
    2. Calculate all allowances
    3. Calculate gross salary
    4. Calculate employee deductions (INPS, AMO, Tax)
    5. Calculate net salary
    6. Apply loans/advances
    7. Calculate employer costs and labor taxes
    """

    def __init__(self):
        """Initialize payroll calculator"""
        self.tax_calculator = TaxCalculator()

    def calculate(self, input_data: PayrollInput) -> PayrollResult:
        """
        Calculate complete payroll for an employee

        Args:
            input_data: PayrollInput with all salary components

        Returns:
            PayrollResult with all calculations
        """
        # 1. Adjust base salary for absences
        adjusted_base = self._calculate_adjusted_base(
            input_data.base_salary,
            input_data.days_worked,
            input_data.days_absent
        )

        # 2. Calculate allowances
        transport = input_data.transport_allowance or (adjusted_base * 0.10)
        family = input_data.family_allowance
        responsibility = input_data.responsibility_allowance
        risk = input_data.risk_allowance
        housing = input_data.housing_allowance
        overtime = input_data.overtime_amount
        bonus = input_data.bonus_amount
        ind_spec = input_data.ind_spec_1973
        cher_vie = input_data.cher_vie_1974

        total_allowances = (
            transport + family + responsibility + risk + housing +
            overtime + bonus + ind_spec + cher_vie
        )

        # 3. Calculate gross salary
        gross_salary = adjusted_base + total_allowances

        # 4. Calculate INPS/AMO base (some allowances excluded from social contributions)
        # Typically: base + transport + family + fixed allowances
        # Exclude: risk, responsibility, overtime, bonus
        inps_amo_base = adjusted_base + transport + family + ind_spec + cher_vie

        # 5. Calculate employee deductions
        inps_employee = inps_amo_base * INPS_EMPLOYEE_RATE
        amo_employee = inps_amo_base * AMO_EMPLOYEE_RATE

        # Calculate income tax on gross salary
        income_tax = self.tax_calculator.calculate_monthly_tax(
            gross_salary,
            self.tax_calculator.get_family_charge_reduction(input_data.status_code)
        )

        total_deductions = (
            inps_employee + amo_employee + income_tax +
            input_data.loan_deduction + input_data.advance_deduction +
            input_data.other_deductions
        )

        # 6. Calculate net amounts
        net_salary = gross_salary - inps_employee - amo_employee - income_tax
        net_to_pay = net_salary - input_data.loan_deduction - input_data.advance_deduction - input_data.other_deductions

        # 7. Calculate employer costs
        inps_employer = inps_amo_base * INPS_EMPLOYER_RATE
        amo_employer = inps_amo_base * AMO_EMPLOYER_RATE

        # Labor taxes (calculated on gross salary)
        taxe_logement = gross_salary * 0.01  # TL: 1%
        taxe_formation = gross_salary * 0.02  # TFP: 2%
        taxe_emploi = gross_salary * 0.02  # ATEJ: 2%
        contribution_cfe = gross_salary * 0.035  # CFE: 3.5%

        total_labor_taxes = taxe_logement + taxe_formation + taxe_emploi + contribution_cfe
        total_employer_cost = inps_employer + amo_employer + total_labor_taxes

        # 8. Grand total cost
        total_cost = gross_salary + total_employer_cost

        # Return complete result
        return PayrollResult(
            employee_id=input_data.employee_id,
            base_salary=round(input_data.base_salary, 2),
            days_worked=input_data.days_worked,
            days_absent=input_data.days_absent,
            adjusted_base_salary=round(adjusted_base, 2),
            transport_allowance=round(transport, 2),
            family_allowance=round(family, 2),
            responsibility_allowance=round(responsibility, 2),
            risk_allowance=round(risk, 2),
            housing_allowance=round(housing, 2),
            overtime_amount=round(overtime, 2),
            bonus_amount=round(bonus, 2),
            ind_spec_1973=round(ind_spec, 2),
            cher_vie_1974=round(cher_vie, 2),
            total_allowances=round(total_allowances, 2),
            gross_salary=round(gross_salary, 2),
            inps_employee=round(inps_employee, 2),
            amo_employee=round(amo_employee, 2),
            income_tax_net=round(income_tax, 2),
            loan_deduction=round(input_data.loan_deduction, 2),
            advance_deduction=round(input_data.advance_deduction, 2),
            other_deductions=round(input_data.other_deductions, 2),
            total_deductions=round(total_deductions, 2),
            net_salary=round(net_salary, 2),
            net_to_pay=round(net_to_pay, 2),
            inps_employer=round(inps_employer, 2),
            amo_employer=round(amo_employer, 2),
            total_employer_cost=round(total_employer_cost, 2),
            taxe_logement=round(taxe_logement, 2),
            taxe_formation=round(taxe_formation, 2),
            taxe_emploi=round(taxe_emploi, 2),
            contribution_cfe=round(contribution_cfe, 2),
            total_labor_taxes=round(total_labor_taxes, 2),
            total_cost=round(total_cost, 2)
        )

    def _calculate_adjusted_base(self, base_salary: float,
                                 days_worked: int,
                                 days_absent: int) -> float:
        """
        Calculate adjusted base salary based on days worked

        Args:
            base_salary: Monthly base salary
            days_worked: Number of days worked
            days_absent: Number of days absent (unpaid)

        Returns:
            Adjusted base salary
        """
        # Standard working days per month
        standard_days = 26

        # If no absences, return full salary
        if days_absent == 0:
            return base_salary

        # Calculate daily rate
        daily_rate = base_salary / standard_days

        # Deduct absent days
        absence_deduction = daily_rate * days_absent
        adjusted_base = base_salary - absence_deduction

        return max(0, adjusted_base)  # Ensure not negative

    def calculate_family_allowance(self, status_code: str, base_salary: float) -> float:
        """
        Calculate family allowance based on status code

        Family allowances (from Paramètres.csv):
        - C0-C4: 15,000 to 30,000 CFA (single, 0-4 children)
        - C5+: 35,000 to 45,000 CFA (single, 5+ children)
        - M0-M4: 25,000 to 40,000 CFA (married, 0-4 children)
        - M5+: 35,000 to 60,000 CFA (married, 5+ children)

        Args:
            status_code: Employee status code (e.g., "C0", "M08")
            base_salary: Base salary (may influence allowance in some systems)

        Returns:
            Family allowance amount in CFA
        """
        if not status_code:
            return 0.0

        status_code = status_code.upper().strip()

        # Extract marital status and number
        marital_status = status_code[0]
        try:
            number = int(status_code[1:])
        except (ValueError, IndexError):
            return 0.0

        # Single (Célibataire)
        if marital_status == 'C':
            if 0 <= number <= 1:
                return 15000.0
            elif 2 <= number <= 4:
                return 25000.0
            elif number >= 5:
                return 35000.0

        # Married (Marié)
        elif marital_status == 'M':
            if 0 <= number <= 2:
                return 25000.0
            elif 3 <= number <= 4:
                return 35000.0
            elif 5 <= number <= 7:
                return 45000.0
            elif number >= 8:
                return 55000.0

        return 0.0


# Convenience function for quick calculation
def calculate_payroll(employee_id: str, base_salary: float,
                     status_code: str = "", **kwargs) -> PayrollResult:
    """
    Quick function to calculate payroll

    Args:
        employee_id: Employee ID
        base_salary: Monthly base salary
        status_code: Employee status code
        **kwargs: Additional payroll input parameters

    Returns:
        PayrollResult with all calculations
    """
    calculator = PayrollCalculator()

    # Auto-calculate family allowance if not provided
    if 'family_allowance' not in kwargs:
        kwargs['family_allowance'] = calculator.calculate_family_allowance(
            status_code, base_salary
        )

    input_data = PayrollInput(
        employee_id=employee_id,
        base_salary=base_salary,
        status_code=status_code,
        **kwargs
    )

    return calculator.calculate(input_data)
