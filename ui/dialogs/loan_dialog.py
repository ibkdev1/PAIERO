"""
Loan Dialog
Add/Edit loan or advance
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton,
    QDialogButtonBox, QGroupBox, QFormLayout, QDateEdit,
    QComboBox, QTextEdit, QFrame, QWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import date


class LoanDialog(QDialog):
    """Dialog to add or edit a loan/advance"""

    def __init__(self, employees, loan=None, parent=None):
        super().__init__(parent)
        self.employees = employees
        self.loan = loan
        self.is_edit = loan is not None

        title = "Modifier Prêt/Avance" if self.is_edit else "Nouveau Prêt/Avance"
        self.setWindowTitle(title)
        self.setMinimumWidth(700)
        self.setMinimumHeight(650)
        self.resize(700, 650)

        self.init_ui()

        if self.is_edit:
            self.load_loan_data()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Header
        header = QLabel("Nouveau Prêt ou Avance")
        header_font = QFont()
        header_font.setPointSize(20)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("color: #2c3e50; padding: 15px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #bdc3c7;")
        layout.addWidget(separator)

        # Employee selection
        employee_group = QGroupBox("Sélection de l'Employé")
        employee_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 15px;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 15px;
                padding: 20px 15px 15px 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #3498db;
            }
        """)
        employee_layout = QFormLayout()
        employee_layout.setSpacing(15)
        employee_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        employee_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        emp_label = QLabel("Employé:")
        emp_label.setStyleSheet("font-size: 14px; font-weight: bold; padding-right: 10px;")

        self.employee_combo = QComboBox()
        self.employee_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                min-height: 25px;
            }
        """)
        for emp in self.employees:
            self.employee_combo.addItem(
                f"{emp.employee_id} - {emp.full_name}",
                emp.employee_id
            )
        employee_layout.addRow(emp_label, self.employee_combo)

        employee_group.setLayout(employee_layout)
        layout.addWidget(employee_group)

        # Loan details
        loan_group = QGroupBox("Détails du Prêt/Avance")
        loan_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 15px;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 15px;
                padding: 20px 15px 15px 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #27ae60;
            }
        """)
        loan_layout = QFormLayout()
        loan_layout.setSpacing(18)
        loan_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        loan_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # Type
        type_label = QLabel("Type:")
        type_label.setStyleSheet("font-size: 14px; font-weight: bold; padding-right: 10px;")

        self.type_combo = QComboBox()
        self.type_combo.addItem("Prêt", "Prêt")
        self.type_combo.addItem("Avance", "Avance")
        self.type_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                min-height: 25px;
            }
        """)
        loan_layout.addRow(type_label, self.type_combo)

        # Amount
        amount_label = QLabel("Montant Total:")
        amount_label.setStyleSheet("font-size: 14px; font-weight: bold; padding-right: 10px;")

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(1000, 10000000)
        self.amount_input.setDecimals(0)
        self.amount_input.setSingleStep(10000)
        self.amount_input.setSuffix(" CFA")
        self.amount_input.setStyleSheet("""
            QDoubleSpinBox {
                padding: 10px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                min-height: 25px;
            }
        """)
        self.amount_input.valueChanged.connect(self.calculate_monthly_payment)
        loan_layout.addRow(amount_label, self.amount_input)

        # Grant date
        date_label = QLabel("Date d'Octroi:")
        date_label.setStyleSheet("font-size: 14px; font-weight: bold; padding-right: 10px;")

        self.grant_date_input = QDateEdit()
        self.grant_date_input.setCalendarPopup(True)
        self.grant_date_input.setDate(QDate.currentDate())
        self.grant_date_input.setDisplayFormat("dd/MM/yyyy")
        self.grant_date_input.setStyleSheet("""
            QDateEdit {
                padding: 10px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                min-height: 25px;
            }
        """)
        loan_layout.addRow(date_label, self.grant_date_input)

        # Duration with preset buttons
        duration_label = QLabel("Durée:")
        duration_label.setStyleSheet("font-size: 14px; font-weight: bold; padding-right: 10px;")

        duration_container = QWidget()
        duration_container_layout = QVBoxLayout(duration_container)
        duration_container_layout.setContentsMargins(0, 0, 0, 0)
        duration_container_layout.setSpacing(10)

        # Duration input
        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 60)
        self.duration_input.setValue(12)
        self.duration_input.setSuffix(" mois")
        self.duration_input.setStyleSheet("""
            QSpinBox {
                padding: 10px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                min-height: 25px;
            }
        """)
        self.duration_input.valueChanged.connect(self.calculate_monthly_payment)
        duration_container_layout.addWidget(self.duration_input)

        # Quick preset buttons
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(8)

        preset_label = QLabel("Durées courantes:")
        preset_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        preset_layout.addWidget(preset_label)

        for months in [3, 6, 12, 18, 24, 36]:
            preset_btn = QPushButton(f"{months} mois")
            preset_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    padding: 5px 12px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3498db;
                    color: white;
                    border-color: #3498db;
                }
            """)
            preset_btn.clicked.connect(lambda checked, m=months: self.duration_input.setValue(m))
            preset_layout.addWidget(preset_btn)

        preset_layout.addStretch()
        duration_container_layout.addLayout(preset_layout)

        # Instruction note
        instruction_label = QLabel("💡 Vous pouvez ajuster la durée manuellement (1-60 mois) ou utiliser les boutons ci-dessus")
        instruction_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #7f8c8d;
                font-style: italic;
                padding: 3px;
            }
        """)
        instruction_label.setWordWrap(True)
        duration_container_layout.addWidget(instruction_label)

        loan_layout.addRow(duration_label, duration_container)

        # Monthly payment (calculated)
        monthly_label = QLabel("Mensualité:")
        monthly_label.setStyleSheet("font-size: 14px; font-weight: bold; padding-right: 10px;")

        self.monthly_payment_label = QLabel("0 CFA")
        self.monthly_payment_label.setStyleSheet("""
            QLabel {
                background-color: #d5f4e6;
                padding: 12px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                color: #27ae60;
                border: 2px solid #27ae60;
            }
        """)
        self.monthly_payment_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loan_layout.addRow(monthly_label, self.monthly_payment_label)

        loan_group.setLayout(loan_layout)
        layout.addWidget(loan_group)

        # Notes
        notes_group = QGroupBox("Notes (Optionnel)")
        notes_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 15px;
                border: 2px solid #95a5a6;
                border-radius: 8px;
                margin-top: 15px;
                padding: 20px 15px 15px 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #7f8c8d;
            }
        """)
        notes_layout = QVBoxLayout()

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Ajouter des notes sur ce prêt/avance...")
        self.notes_input.setMaximumHeight(90)
        self.notes_input.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                font-size: 13px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
        """)
        notes_layout.addWidget(self.notes_input)

        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)

        # Info banner
        info_label = QLabel(
            "ℹ️  La mensualité sera automatiquement déduite chaque mois lors du traitement de la paie."
        )
        info_label.setStyleSheet("""
            QLabel {
                background-color: #d5f4e6;
                padding: 12px 15px;
                border-radius: 6px;
                font-size: 13px;
                color: #27ae60;
                border: 1px solid #27ae60;
            }
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addStretch()

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Initial calculation
        self.calculate_monthly_payment()

    def calculate_monthly_payment(self):
        """Calculate and display monthly payment"""
        amount = self.amount_input.value()
        duration = self.duration_input.value()

        if duration > 0:
            monthly = amount / duration
            self.monthly_payment_label.setText(f"{int(monthly):,} CFA")
        else:
            self.monthly_payment_label.setText("0 CFA")

    def load_loan_data(self):
        """Load loan data for editing"""
        if not self.loan:
            return

        # Find and select employee
        employee_index = self.employee_combo.findData(self.loan['employee_id'])
        if employee_index >= 0:
            self.employee_combo.setCurrentIndex(employee_index)
        self.employee_combo.setEnabled(False)  # Can't change employee

        # Set type
        type_index = self.type_combo.findData(self.loan['loan_type'])
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)

        # Set amount
        self.amount_input.setValue(self.loan['total_amount'])

        # Set grant date
        if self.loan['grant_date']:
            grant_date = QDate.fromString(self.loan['grant_date'], "yyyy-MM-dd")
            self.grant_date_input.setDate(grant_date)

        # Set duration
        self.duration_input.setValue(self.loan['duration_months'])

        # Set notes
        if self.loan.get('notes'):
            self.notes_input.setPlainText(self.loan['notes'])

    def validate_and_accept(self):
        """Validate form before accepting"""
        if self.amount_input.value() <= 0:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Erreur",
                "Le montant doit être supérieur à 0."
            )
            return

        if self.duration_input.value() <= 0:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Erreur",
                "La durée doit être supérieure à 0."
            )
            return

        self.accept()

    def get_data(self):
        """Get loan data from form"""
        return {
            'employee_id': self.employee_combo.currentData(),
            'loan_type': self.type_combo.currentData(),
            'total_amount': self.amount_input.value(),
            'grant_date': self.grant_date_input.date().toPyDate(),
            'duration_months': self.duration_input.value(),
            'notes': self.notes_input.toPlainText().strip()
        }
