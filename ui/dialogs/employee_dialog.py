"""
Employee Add/Edit Dialog
Dialog for creating and editing employees
"""

import sys
import os
from datetime import date
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QDateEdit, QComboBox, QPushButton,
    QMessageBox, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.employee import Employee
from database.repositories.employee_repository import EmployeeRepository


class EmployeeDialog(QDialog):
    """Dialog for adding or editing an employee"""

    def __init__(self, parent=None, employee: Employee = None):
        super().__init__(parent)
        self.employee = employee
        self.is_edit_mode = employee is not None

        self.init_ui()
        if self.employee:
            self.load_employee_data()

    def init_ui(self):
        """Initialize the user interface"""
        # Set dialog properties
        title = "Modifier Employé" if self.is_edit_mode else "Ajouter Employé"
        self.setWindowTitle(title)
        self.setMinimumWidth(600)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Personal Information Group
        personal_group = QGroupBox("Informations Personnelles")
        personal_layout = QFormLayout()

        # Employee ID
        self.id_input = QLineEdit()
        if not self.is_edit_mode:
            # Auto-generate next ID for new employees
            next_id = EmployeeRepository.get_next_employee_id()
            self.id_input.setText(next_id)
        else:
            self.id_input.setReadOnly(True)
        personal_layout.addRow("N° Matricule *:", self.id_input)

        # First Name
        self.first_name_input = QLineEdit()
        personal_layout.addRow("Prénom *:", self.first_name_input)

        # Last Name
        self.last_name_input = QLineEdit()
        personal_layout.addRow("Nom *:", self.last_name_input)

        # Position
        self.position_input = QLineEdit()
        personal_layout.addRow("Fonction:", self.position_input)

        # Hire Date
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDate(QDate.currentDate())
        self.hire_date_input.setDisplayFormat("dd/MM/yyyy")
        personal_layout.addRow("Date d'Embauche *:", self.hire_date_input)

        # Contract End Date
        self.contract_end_input = QDateEdit()
        self.contract_end_input.setCalendarPopup(True)
        self.contract_end_input.setDisplayFormat("dd/MM/yyyy")
        self.contract_end_input.setSpecialValueText("Indéterminé")
        self.contract_end_input.setDate(QDate.currentDate().addYears(1))
        personal_layout.addRow("Fin de Contrat:", self.contract_end_input)

        # Address
        self.address_input = QLineEdit()
        personal_layout.addRow("Adresse:", self.address_input)

        personal_group.setLayout(personal_layout)
        layout.addWidget(personal_group)

        # Classification Group
        classification_group = QGroupBox("Classification")
        classification_layout = QFormLayout()

        # Status Code
        self.status_input = QComboBox()
        self.status_input.addItems([
            "C0", "C01", "C02", "C03", "C04", "C05", "C06",
            "M0", "M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08"
        ])
        classification_layout.addRow("Statut:", self.status_input)

        # Category
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems([
            "Cat 1 Ech A", "Cat 2 Ech A", "Cat 3 Ech A",
            "Cat 5 Ech A", "Cat 7", "Cat 8",
            "Cat 10 Ech A", "Cat 10 Ech B", "Cat 11"
        ])
        classification_layout.addRow("Catégorie:", self.category_input)

        # Department
        self.department_input = QComboBox()
        self.department_input.setEditable(True)
        departments = EmployeeRepository.get_departments()
        if departments:
            self.department_input.addItems(departments)
        classification_layout.addRow("Département:", self.department_input)

        # Agency
        self.agency_input = QLineEdit()
        classification_layout.addRow("Agence:", self.agency_input)

        classification_group.setLayout(classification_layout)
        layout.addWidget(classification_group)

        # Banking Information Group
        banking_group = QGroupBox("Informations Bancaires")
        banking_layout = QFormLayout()

        # INPS Number
        self.inps_input = QLineEdit()
        banking_layout.addRow("N° INPS:", self.inps_input)

        # INPS Allocation Number
        self.inps_alloc_input = QLineEdit()
        banking_layout.addRow("N° Allocation INPS:", self.inps_alloc_input)

        # Bank Name
        self.bank_name_input = QLineEdit()
        banking_layout.addRow("Nom de la Banque:", self.bank_name_input)

        # Bank Account
        self.bank_account_input = QLineEdit()
        banking_layout.addRow("N° Compte Bancaire:", self.bank_account_input)

        banking_group.setLayout(banking_layout)
        layout.addWidget(banking_group)

        # Active Status
        self.active_checkbox = QCheckBox("Employé Actif")
        self.active_checkbox.setChecked(True)
        layout.addWidget(self.active_checkbox)

        # Required fields note
        note_label = QLabel("* Champs obligatoires")
        note_label.setStyleSheet("color: #7f8c8d; font-size: 11px; font-style: italic;")
        layout.addWidget(note_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.save)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def load_employee_data(self):
        """Load employee data into form fields"""
        if not self.employee:
            return

        self.id_input.setText(self.employee.employee_id)
        self.first_name_input.setText(self.employee.first_name)
        self.last_name_input.setText(self.employee.last_name)
        self.position_input.setText(self.employee.position or "")

        if self.employee.hire_date:
            qdate = QDate(
                self.employee.hire_date.year,
                self.employee.hire_date.month,
                self.employee.hire_date.day
            )
            self.hire_date_input.setDate(qdate)

        if self.employee.contract_end_date:
            qdate = QDate(
                self.employee.contract_end_date.year,
                self.employee.contract_end_date.month,
                self.employee.contract_end_date.day
            )
            self.contract_end_input.setDate(qdate)

        self.address_input.setText(self.employee.address or "")

        if self.employee.status_code:
            index = self.status_input.findText(self.employee.status_code)
            if index >= 0:
                self.status_input.setCurrentIndex(index)

        if self.employee.category:
            self.category_input.setCurrentText(self.employee.category)

        if self.employee.department_code:
            self.department_input.setCurrentText(self.employee.department_code)

        self.agency_input.setText(self.employee.agency_code or "")
        self.inps_input.setText(self.employee.inps_number or "")
        self.inps_alloc_input.setText(self.employee.inps_allocation_number or "")
        self.bank_name_input.setText(self.employee.bank_name or "")
        self.bank_account_input.setText(self.employee.bank_account or "")
        self.active_checkbox.setChecked(self.employee.is_active)

    def validate(self) -> bool:
        """Validate form data"""
        # Check required fields
        if not self.id_input.text().strip():
            QMessageBox.warning(self, "Validation", "Le numéro matricule est obligatoire.")
            self.id_input.setFocus()
            return False

        if not self.first_name_input.text().strip():
            QMessageBox.warning(self, "Validation", "Le prénom est obligatoire.")
            self.first_name_input.setFocus()
            return False

        if not self.last_name_input.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire.")
            self.last_name_input.setFocus()
            return False

        # Check if employee ID already exists (for new employees)
        if not self.is_edit_mode:
            if EmployeeRepository.exists(self.id_input.text().strip()):
                QMessageBox.warning(
                    self,
                    "Validation",
                    f"Un employé avec le matricule {self.id_input.text()} existe déjà."
                )
                self.id_input.setFocus()
                return False

        return True

    def save(self):
        """Save employee data"""
        if not self.validate():
            return

        try:
            # Create or update employee object
            employee_id = self.id_input.text().strip()
            first_name = self.first_name_input.text().strip()
            last_name = self.last_name_input.text().strip()
            full_name = f"{first_name} {last_name}"

            qdate = self.hire_date_input.date()
            hire_date = date(qdate.year(), qdate.month(), qdate.day())

            contract_end_date = None
            if self.contract_end_input.text() != self.contract_end_input.specialValueText():
                qdate = self.contract_end_input.date()
                contract_end_date = date(qdate.year(), qdate.month(), qdate.day())

            employee = Employee(
                employee_id=employee_id,
                first_name=first_name,
                last_name=last_name,
                full_name=full_name,
                position=self.position_input.text().strip() or None,
                hire_date=hire_date,
                contract_end_date=contract_end_date,
                status_code=self.status_input.currentText(),
                agency_code=self.agency_input.text().strip() or None,
                department_code=self.department_input.currentText().strip() or None,
                category=self.category_input.currentText().strip() or None,
                address=self.address_input.text().strip() or None,
                inps_number=self.inps_input.text().strip() or None,
                inps_allocation_number=self.inps_alloc_input.text().strip() or None,
                bank_name=self.bank_name_input.text().strip() or None,
                bank_account=self.bank_account_input.text().strip() or None,
                is_active=self.active_checkbox.isChecked()
            )

            # Calculate seniority
            employee.update_seniority()

            # Save to database
            if self.is_edit_mode:
                success = EmployeeRepository.update(employee)
                message = "Employé modifié avec succès."
            else:
                success = EmployeeRepository.create(employee)
                message = "Employé ajouté avec succès."

            if success:
                QMessageBox.information(self, "Succès", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de l'enregistrement.")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement:\n{e}")
