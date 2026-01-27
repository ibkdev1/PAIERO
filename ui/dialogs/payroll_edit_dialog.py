"""
Payroll Edit Dialog
Edit payroll record details before calculation
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton,
    QDialogButtonBox, QGroupBox, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class PayrollEditDialog(QDialog):
    """Dialog to edit payroll record details"""

    def __init__(self, employee_name, record, parent=None):
        super().__init__(parent)
        self.record = record
        self.employee_name = employee_name

        self.setWindowTitle(f"Éditer Paie - {employee_name}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)

        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Header
        header = QLabel(f"Édition du Dossier de Paie")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(header)

        employee_label = QLabel(f"Employé: {self.employee_name}")
        employee_label.setStyleSheet("font-size: 14px; color: #34495e; padding: 5px;")
        layout.addWidget(employee_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #bdc3c7;")
        layout.addWidget(separator)

        # Work tracking section
        work_group = QGroupBox("Suivi du Travail")
        work_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        work_layout = QFormLayout()
        work_layout.setSpacing(15)

        self.base_salary_input = QDoubleSpinBox()
        self.base_salary_input.setRange(0, 10000000)
        self.base_salary_input.setDecimals(0)
        self.base_salary_input.setSingleStep(1000)
        self.base_salary_input.setStyleSheet("padding: 5px; font-size: 13px;")
        self.base_salary_input.setEnabled(False)  # Read-only, comes from salary scale
        work_layout.addRow("Salaire de Base (CFA):", self.base_salary_input)

        self.days_worked_input = QSpinBox()
        self.days_worked_input.setRange(0, 31)
        self.days_worked_input.setValue(26)
        self.days_worked_input.setStyleSheet("padding: 5px; font-size: 13px;")
        work_layout.addRow("Jours Travaillés:", self.days_worked_input)

        self.days_absent_input = QSpinBox()
        self.days_absent_input.setRange(0, 31)
        self.days_absent_input.setValue(0)
        self.days_absent_input.setStyleSheet("padding: 5px; font-size: 13px;")
        work_layout.addRow("Jours Absents:", self.days_absent_input)

        work_group.setLayout(work_layout)
        layout.addWidget(work_group)

        # Allowances section
        allowances_group = QGroupBox("Indemnités et Primes")
        allowances_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #27ae60;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        allowances_layout = QFormLayout()
        allowances_layout.setSpacing(15)

        # Transport (auto-calculated at 10%)
        self.transport_input = QDoubleSpinBox()
        self.transport_input.setRange(0, 1000000)
        self.transport_input.setDecimals(0)
        self.transport_input.setSingleStep(1000)
        self.transport_input.setStyleSheet("padding: 5px; font-size: 13px;")
        self.transport_input.setEnabled(False)  # Auto-calculated
        allowances_layout.addRow("Ind. Transport (10%):", self.transport_input)

        # Family allowance
        self.family_input = QDoubleSpinBox()
        self.family_input.setRange(0, 100000)
        self.family_input.setDecimals(0)
        self.family_input.setSingleStep(5000)
        self.family_input.setStyleSheet("padding: 5px; font-size: 13px;")
        self.family_input.setEnabled(False)  # Auto-calculated from status
        allowances_layout.addRow("All. Charge Famille:", self.family_input)

        # Responsibility allowance
        self.responsibility_input = QDoubleSpinBox()
        self.responsibility_input.setRange(0, 500000)
        self.responsibility_input.setDecimals(0)
        self.responsibility_input.setSingleStep(5000)
        self.responsibility_input.setStyleSheet("padding: 5px; font-size: 13px;")
        allowances_layout.addRow("Ind. Responsabilité:", self.responsibility_input)

        # Risk premium
        self.risk_input = QDoubleSpinBox()
        self.risk_input.setRange(0, 500000)
        self.risk_input.setDecimals(0)
        self.risk_input.setSingleStep(5000)
        self.risk_input.setStyleSheet("padding: 5px; font-size: 13px;")
        allowances_layout.addRow("Prime de Risque:", self.risk_input)

        # Vehicle allowance
        self.vehicle_input = QDoubleSpinBox()
        self.vehicle_input.setRange(0, 500000)
        self.vehicle_input.setDecimals(0)
        self.vehicle_input.setSingleStep(5000)
        self.vehicle_input.setStyleSheet("padding: 5px; font-size: 13px;")
        allowances_layout.addRow("Ind. Monture:", self.vehicle_input)

        # Overtime
        self.overtime_input = QDoubleSpinBox()
        self.overtime_input.setRange(0, 1000000)
        self.overtime_input.setDecimals(0)
        self.overtime_input.setSingleStep(10000)
        self.overtime_input.setStyleSheet("padding: 5px; font-size: 13px;")
        allowances_layout.addRow("Heures Supplémentaires:", self.overtime_input)

        allowances_group.setLayout(allowances_layout)
        layout.addWidget(allowances_group)

        # Deductions section
        deductions_group = QGroupBox("Retenues et Avances")
        deductions_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e74c3c;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        deductions_layout = QFormLayout()
        deductions_layout.setSpacing(15)

        self.loan_input = QDoubleSpinBox()
        self.loan_input.setRange(0, 1000000)
        self.loan_input.setDecimals(0)
        self.loan_input.setSingleStep(5000)
        self.loan_input.setStyleSheet("padding: 5px; font-size: 13px;")
        deductions_layout.addRow("Prêt/Avance:", self.loan_input)

        deductions_group.setLayout(deductions_layout)
        layout.addWidget(deductions_group)

        # Info label
        info_label = QLabel(
            "ℹ️ Les valeurs en gris (Salaire de Base, Transport, Allocation Familiale) "
            "sont calculées automatiquement."
        )
        info_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
                color: #34495e;
            }
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        # Recalculate button
        recalc_btn = QPushButton("⚡ Recalculer")
        recalc_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        recalc_btn.clicked.connect(self.accept)
        button_layout.addWidget(recalc_btn)

        button_layout.addStretch()

        # Standard buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.rejected.connect(self.reject)
        button_layout.addWidget(button_box)

        layout.addLayout(button_layout)

    def load_data(self):
        """Load data from record into form"""
        self.base_salary_input.setValue(self.record.get('base_salary', 0))
        self.days_worked_input.setValue(self.record.get('days_worked', 26))
        self.days_absent_input.setValue(self.record.get('days_absent', 0))

        # Allowances - use correct column names
        self.transport_input.setValue(self.record.get('ind_transport', 0))
        self.family_input.setValue(self.record.get('family_allowance', 0))
        self.responsibility_input.setValue(self.record.get('responsibility_allowance', 0))
        self.risk_input.setValue(self.record.get('risk_premium', 0))
        self.vehicle_input.setValue(self.record.get('vehicle_allowance', 0))
        self.overtime_input.setValue(self.record.get('overtime_pay', 0))

        # Deductions
        self.loan_input.setValue(self.record.get('advances_loans_deduction', 0))

    def get_data(self):
        """Get modified data from form"""
        return {
            'base_salary': self.base_salary_input.value(),
            'days_worked': self.days_worked_input.value(),
            'days_absent': self.days_absent_input.value(),
            'responsibility_allowance': self.responsibility_input.value(),
            'risk_allowance': self.risk_input.value(),
            'housing_allowance': self.vehicle_input.value(),
            'overtime_amount': self.overtime_input.value(),
            'loan_deduction': self.loan_input.value()
        }
