"""
Tax Calculator
Progressive income tax calculation based on Malian tax brackets
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TaxBracket:
    """Tax bracket with min/max income and tax rate"""
    min_income: float
    max_income: Optional[float]  # None for highest bracket
    tax_rate: float
    cumulative_tax: float = 0.0  # Tax from previous brackets


class TaxCalculator:
    """
    Calculate progressive income tax based on annual taxable income

    Mali Tax Brackets (2019):
    - 0 to 330,000 CFA: 0%
    - 330,001 to 578,400 CFA: 5%
    - 578,401 to 1,176,400 CFA: 12%
    - 1,176,401 to 1,789,733 CFA: 18%
    - 1,789,734 to 2,384,195 CFA: 26%
    - 2,384,196 to 3,494,130 CFA: 31%
    - 3,494,131 and above: 37%
    """

    # Default Mali tax brackets
    DEFAULT_BRACKETS = [
        TaxBracket(0, 330000, 0.0, 0),
        TaxBracket(330001, 578400, 0.05, 0),
        TaxBracket(578401, 1176400, 0.12, 12420),
        TaxBracket(1176401, 1789733, 0.18, 84180),
        TaxBracket(1789734, 2384195, 0.26, 194579),
        TaxBracket(2384196, 3494130, 0.31, 349134),
        TaxBracket(3494131, None, 0.37, 693217)
    ]

    def __init__(self, brackets: Optional[List[TaxBracket]] = None):
        """
        Initialize tax calculator with tax brackets

        Args:
            brackets: List of tax brackets (uses DEFAULT_BRACKETS if None)
        """
        self.brackets = brackets or self.DEFAULT_BRACKETS

    def calculate_annual_tax(self, annual_taxable_income: float) -> float:
        """
        Calculate annual income tax based on progressive brackets

        Args:
            annual_taxable_income: Annual taxable income in CFA

        Returns:
            Annual tax amount in CFA
        """
        if annual_taxable_income <= 0:
            return 0.0

        tax = 0.0

        for bracket in self.brackets:
            # Skip if income is below this bracket
            if annual_taxable_income < bracket.min_income:
                break

            # Calculate taxable amount in this bracket
            if bracket.max_income is None:
                # Highest bracket - tax all remaining income
                taxable_in_bracket = annual_taxable_income - bracket.min_income + 1
            elif annual_taxable_income > bracket.max_income:
                # Income exceeds this bracket - tax the full bracket
                taxable_in_bracket = bracket.max_income - bracket.min_income + 1
            else:
                # Income falls within this bracket
                taxable_in_bracket = annual_taxable_income - bracket.min_income + 1

            # Add tax from this bracket
            bracket_tax = taxable_in_bracket * bracket.tax_rate
            tax += bracket_tax

        return round(tax, 2)

    def calculate_monthly_tax(self, monthly_gross_salary: float,
                             family_charge_reduction: float = 0.0) -> float:
        """
        Calculate monthly income tax

        Args:
            monthly_gross_salary: Monthly gross salary in CFA
            family_charge_reduction: Family charge reduction percentage (0.0 to 0.25)

        Returns:
            Monthly tax amount in CFA
        """
        # Calculate annual taxable income
        annual_taxable = monthly_gross_salary * 12

        # Apply family charge reduction (0% to 25%)
        if family_charge_reduction > 0:
            annual_taxable = annual_taxable * (1 - family_charge_reduction)

        # Calculate annual tax
        annual_tax = self.calculate_annual_tax(annual_taxable)

        # Convert to monthly
        monthly_tax = annual_tax / 12

        return round(monthly_tax, 2)

    def get_family_charge_reduction(self, status_code: str) -> float:
        """
        Get family charge reduction based on employee status code

        Status codes (C = Célibataire/Single, M = Marié/Married):
        - C0-C4: 0% (single, 0-4 children)
        - C5-C9: 10% (single, 5-9 children)
        - C10-C15: 15% (single, 10-15 children)
        - M0-M4: 10% (married, 0-4 children)
        - M5-M9: 20% (married, 5-9 children)
        - M10-M20: 25% (married, 10-20 children)

        Args:
            status_code: Employee status code (e.g., "C0", "M08")

        Returns:
            Reduction percentage as decimal (0.0 to 0.25)
        """
        if not status_code:
            return 0.0

        status_code = status_code.upper().strip()

        # Extract marital status and number
        marital_status = status_code[0]  # C or M
        try:
            number = int(status_code[1:])
        except (ValueError, IndexError):
            return 0.0

        # Single (Célibataire)
        if marital_status == 'C':
            if 0 <= number <= 4:
                return 0.0
            elif 5 <= number <= 9:
                return 0.10
            elif 10 <= number <= 15:
                return 0.15

        # Married (Marié)
        elif marital_status == 'M':
            if 0 <= number <= 4:
                return 0.10
            elif 5 <= number <= 9:
                return 0.20
            elif 10 <= number <= 20:
                return 0.25

        return 0.0

    def calculate_tax_details(self, monthly_gross_salary: float,
                             status_code: str = "") -> dict:
        """
        Calculate detailed tax breakdown

        Args:
            monthly_gross_salary: Monthly gross salary in CFA
            status_code: Employee status code for family reduction

        Returns:
            Dictionary with tax calculation details
        """
        # Get family charge reduction
        reduction_rate = self.get_family_charge_reduction(status_code)

        # Calculate annual values
        annual_gross = monthly_gross_salary * 12
        annual_taxable = annual_gross * (1 - reduction_rate)
        annual_tax = self.calculate_annual_tax(annual_taxable)

        # Calculate monthly values
        monthly_tax = annual_tax / 12

        return {
            'monthly_gross': round(monthly_gross_salary, 2),
            'annual_gross': round(annual_gross, 2),
            'status_code': status_code,
            'family_reduction_rate': reduction_rate,
            'annual_taxable': round(annual_taxable, 2),
            'annual_tax': round(annual_tax, 2),
            'monthly_tax': round(monthly_tax, 2),
            'effective_tax_rate': round((monthly_tax / monthly_gross_salary * 100), 2) if monthly_gross_salary > 0 else 0.0
        }


# Convenience function for quick calculations
def calculate_income_tax(monthly_gross: float, status_code: str = "") -> float:
    """
    Quick function to calculate monthly income tax

    Args:
        monthly_gross: Monthly gross salary in CFA
        status_code: Employee status code (e.g., "C0", "M08")

    Returns:
        Monthly tax amount in CFA
    """
    calculator = TaxCalculator()
    return calculator.calculate_monthly_tax(
        monthly_gross,
        calculator.get_family_charge_reduction(status_code)
    )
