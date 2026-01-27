"""
Payroll Processing Screen
Create payroll periods and process employee payroll with calculations
"""

import sys
import os
from datetime import date, datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QAbstractItemView, QComboBox, QDialog, QDialogButtonBox,
    QDateEdit, QSpinBox, QDoubleSpinBox, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.repositories.employee_repository import EmployeeRepository
from database.repositories.payroll_repository import PayrollRepository
from business.payroll_calculator import PayrollCalculator, PayrollInput
from business.tax_calculator import TaxCalculator
from ui.dialogs.payroll_edit_dialog import PayrollEditDialog
from database.auth import AuthManager


class CreatePeriodDialog(QDialog):
    """Dialog to create a new payroll period"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Créer une Nouvelle Période de Paie")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)

        form = QFormLayout()

        # Start date
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Date de Début:", self.start_date)

        # End date
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Date de Fin:", self.end_date)

        # Payment date
        self.payment_date = QDateEdit()
        self.payment_date.setCalendarPopup(True)
        self.payment_date.setDate(QDate.currentDate())
        self.payment_date.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Date de Paiement:", self.payment_date)

        layout.addLayout(form)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        """Get period data from dialog"""
        return {
            'start_date': self.start_date.date().toPyDate(),
            'end_date': self.end_date.date().toPyDate(),
            'payment_date': self.payment_date.date().toPyDate()
        }


class PayrollScreen(QWidget):
    """Payroll processing screen"""

    def __init__(self):
        super().__init__()
        self.current_period = None
        self.payroll_records = []
        self.calculator = PayrollCalculator()
        self.init_ui()
        self.load_periods()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header with title and actions
        header_layout = QHBoxLayout()

        title = QLabel("Traitement de la Paie")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Create period button
        create_period_btn = QPushButton("+ Nouvelle Période")
        create_period_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        create_period_btn.clicked.connect(self.create_period)
        header_layout.addWidget(create_period_btn)

        layout.addLayout(header_layout)

        # Period selection bar
        period_layout = QHBoxLayout()

        period_label = QLabel("Période:")
        period_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        period_layout.addWidget(period_label)

        self.period_combo = QComboBox()
        self.period_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #3498db;
                border-radius: 4px;
                font-size: 13px;
                min-width: 300px;
            }
        """)
        self.period_combo.currentIndexChanged.connect(self.on_period_changed)
        period_layout.addWidget(self.period_combo)

        period_layout.addStretch()

        # Calculate All button
        self.calculate_all_btn = QPushButton("⚡ Calculer Tout")
        self.calculate_all_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.calculate_all_btn.clicked.connect(self.calculate_all)
        self.calculate_all_btn.setEnabled(False)
        period_layout.addWidget(self.calculate_all_btn)

        # Finalize button
        self.finalize_btn = QPushButton("✓ Finaliser")
        self.finalize_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.finalize_btn.clicked.connect(self.finalize_period)
        self.finalize_btn.setEnabled(False)
        period_layout.addWidget(self.finalize_btn)

        layout.addLayout(period_layout)

        # Payroll table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Employé", "Poste", "Salaire de Base", "Jours",
            "Indemnités", "Salaire Brut", "INPS+AMO", "Impôt",
            "Net à Payer", "Actions"
        ])

        # Table styling
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(45)  # Taller rows for buttons

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)

        self.table.setColumnWidth(3, 60)
        self.table.setColumnWidth(9, 200)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)

        layout.addWidget(self.table)

        # Summary bar
        self.summary_label = QLabel("Sélectionnez une période pour commencer")
        self.summary_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 12px;
                border-radius: 5px;
                font-size: 13px;
                color: #2c3e50;
            }
        """)
        layout.addWidget(self.summary_label)

    def load_periods(self):
        """Load all payroll periods"""
        try:
            periods = PayrollRepository.get_all_periods()

            self.period_combo.blockSignals(True)
            self.period_combo.clear()

            if not periods:
                self.period_combo.addItem("Aucune période - Créez-en une", None)
            else:
                for period in periods:
                    start = period['period_start_date']
                    end = period['period_end_date']
                    finalized = " [Finalisée]" if period['is_finalized'] else ""
                    label = f"{start} au {end}{finalized}"
                    self.period_combo.addItem(label, period['period_id'])

            self.period_combo.blockSignals(False)

            # Load first period if available
            if periods:
                self.period_combo.setCurrentIndex(0)
                self.on_period_changed(0)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des périodes:\n{e}")

    def on_period_changed(self, index):
        """Handle period selection change"""
        period_id = self.period_combo.currentData()

        if period_id is None:
            self.current_period = None
            self.table.setRowCount(0)
            self.calculate_all_btn.setEnabled(False)
            self.finalize_btn.setEnabled(False)
            self.summary_label.setText("Aucune période sélectionnée")
            return

        # Load period details
        self.current_period = PayrollRepository.get_period_by_id(period_id)

        # Check if finalized
        is_finalized = self.current_period['is_finalized']
        self.calculate_all_btn.setEnabled(not is_finalized)
        self.finalize_btn.setEnabled(not is_finalized)

        # Load payroll records
        self.load_payroll_records()

    def load_payroll_records(self):
        """Load payroll records for current period"""
        if not self.current_period:
            return

        try:
            period_id = self.current_period['period_id']
            self.payroll_records = PayrollRepository.get_records_by_period(period_id)

            # If no records, initialize with active employees
            if not self.payroll_records:
                count = PayrollRepository.initialize_period_with_employees(period_id)
                self.payroll_records = PayrollRepository.get_records_by_period(period_id)
                if count > 0:
                    QMessageBox.information(
                        self,
                        "Période Initialisée",
                        f"{count} employé(s) ajouté(s) à la période.\nCliquez sur 'Calculer Tout' pour effectuer les calculs."
                    )

            self.display_payroll_records()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des enregistrements:\n{e}")

    def display_payroll_records(self):
        """Display payroll records in table"""
        self.table.setRowCount(0)

        total_gross = 0
        total_net = 0

        for record in self.payroll_records:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Employee name
            self.table.setItem(row, 0, QTableWidgetItem(record['full_name']))

            # Position
            self.table.setItem(row, 1, QTableWidgetItem(record['position'] or "-"))

            # Base salary
            base_item = QTableWidgetItem(f"{int(record['base_salary']):,}")
            base_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 2, base_item)

            # Days worked
            days_item = QTableWidgetItem(str(record['days_worked']))
            days_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, days_item)

            # Total allowances - use correct database column names
            total_allowances = (
                record.get('ind_transport', 0) + record.get('family_allowance', 0) +
                record.get('responsibility_allowance', 0) + record.get('risk_premium', 0) +
                record.get('vehicle_allowance', 0) + record.get('overtime_pay', 0)
            )
            allowances_item = QTableWidgetItem(f"{int(total_allowances):,}")
            allowances_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 4, allowances_item)

            # Gross salary
            gross_item = QTableWidgetItem(f"{int(record['gross_salary']):,}")
            gross_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            gross_item.setFont(QFont("", -1, QFont.Weight.Bold))
            self.table.setItem(row, 5, gross_item)
            total_gross += record['gross_salary']

            # INPS + AMO
            social_deductions = record['inps_employee'] + record['amo_employee']
            social_item = QTableWidgetItem(f"{int(social_deductions):,}")
            social_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            social_item.setForeground(QColor("#e74c3c"))
            self.table.setItem(row, 6, social_item)

            # Tax
            tax_item = QTableWidgetItem(f"{int(record['income_tax_net']):,}")
            tax_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tax_item.setForeground(QColor("#e67e22"))
            self.table.setItem(row, 7, tax_item)

            # Net to pay
            net_item = QTableWidgetItem(f"{int(record['net_to_pay']):,}")
            net_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            net_item.setFont(QFont("", -1, QFont.Weight.Bold))
            net_item.setForeground(QColor("#27ae60"))
            self.table.setItem(row, 8, net_item)
            total_net += record['net_to_pay']

            # Actions
            actions_widget = self.create_action_buttons(record)
            self.table.setCellWidget(row, 9, actions_widget)

        # Update summary
        employee_count = len(self.payroll_records)
        self.summary_label.setText(
            f"Total: {employee_count} employé(s) | "
            f"Salaire Brut: {int(total_gross):,} CFA | "
            f"Net à Payer: {int(total_net):,} CFA"
        )

    def create_action_buttons(self, record):
        """Create action buttons for a payroll record"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # Edit button
        edit_btn = QPushButton("✏️ Éditer")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        edit_btn.setMinimumWidth(80)
        edit_btn.clicked.connect(lambda: self.edit_payroll_record(record))
        layout.addWidget(edit_btn)

        # Calculate button
        calc_btn = QPushButton("⚡ Calc")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        calc_btn.setMinimumWidth(75)
        calc_btn.clicked.connect(lambda: self.calculate_single_record(record))
        layout.addWidget(calc_btn)

        return widget

    def create_period(self):
        """Create a new payroll period"""
        if not AuthManager.has_permission('can_process_payroll'):
            QMessageBox.warning(self, "Permission refusée", "Vous n'avez pas la permission de créer des périodes de paie.")
            return

        dialog = CreatePeriodDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                period_id = PayrollRepository.create_period(
                    data['start_date'],
                    data['end_date'],
                    data['payment_date']
                )
                QMessageBox.information(
                    self,
                    "Succès",
                    "Période créée avec succès.\nLes employés actifs seront ajoutés automatiquement."
                )
                self.load_periods()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la création de la période:\n{e}")

    def calculate_single_record(self, record):
        """Calculate payroll for a single employee"""
        try:
            # Get employee data
            employee_id = record['employee_id']
            employees = EmployeeRepository.get_all(include_inactive=True)
            employee = next((e for e in employees if e.employee_id == employee_id), None)

            if not employee:
                QMessageBox.warning(self, "Erreur", "Employé introuvable")
                return

            # Create payroll input
            input_data = PayrollInput(
                employee_id=employee_id,
                base_salary=record['base_salary'],
                status_code=employee.status_code or "",
                days_worked=record['days_worked'],
                days_absent=record['days_absent'],
                transport_allowance=record.get('ind_transport', 0),
                family_allowance=record.get('family_allowance', 0),
                responsibility_allowance=record.get('responsibility_allowance', 0),
                risk_allowance=record.get('risk_premium', 0),
                housing_allowance=record.get('vehicle_allowance', 0),
                overtime_amount=record.get('overtime_pay', 0),
                bonus_amount=0,  # Not in current schema
                loan_deduction=record.get('advances_loans_deduction', 0),
                advance_deduction=0,
                other_deductions=0
            )

            # Auto-calculate family allowance if not set
            if input_data.family_allowance == 0:
                input_data.family_allowance = self.calculator.calculate_family_allowance(
                    employee.status_code or "", input_data.base_salary
                )

            # Calculate payroll
            result = self.calculator.calculate(input_data)

            # Update database
            payroll_data = {
                'base_salary': result.base_salary,
                'days_worked': result.days_worked,
                'days_absent': result.days_absent,
                'transport_allowance': result.transport_allowance,
                'family_allowance': result.family_allowance,
                'responsibility_allowance': result.responsibility_allowance,
                'risk_allowance': result.risk_allowance,
                'housing_allowance': result.housing_allowance,
                'overtime_amount': result.overtime_amount,
                'bonus_amount': result.bonus_amount,
                'ind_spec_1973': result.ind_spec_1973,
                'cher_vie_1974': result.cher_vie_1974,
                'gross_salary': result.gross_salary,
                'inps_employee': result.inps_employee,
                'amo_employee': result.amo_employee,
                'income_tax_net': result.income_tax_net,
                'loan_deduction': result.loan_deduction,
                'advance_deduction': result.advance_deduction,
                'other_deductions': result.other_deductions,
                'net_salary': result.net_salary,
                'net_to_pay': result.net_to_pay,
                'inps_employer': result.inps_employer,
                'amo_employer': result.amo_employer,
                'taxe_logement': result.taxe_logement,
                'taxe_formation': result.taxe_formation,
                'taxe_emploi': result.taxe_emploi,
                'contribution_cfe': result.contribution_cfe,
                'total_employer_cost': result.total_employer_cost,
                'total_cost': result.total_cost
            }

            PayrollRepository.create_payroll_record(
                self.current_period['period_id'],
                employee_id,
                payroll_data
            )

            # Reload data
            self.load_payroll_records()

            QMessageBox.information(self, "Succès", f"Calcul effectué pour {employee.full_name}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur lors du calcul:\n{e}")

    def calculate_all(self):
        """Calculate payroll for all employees in the period"""
        if not AuthManager.has_permission('can_process_payroll'):
            QMessageBox.warning(self, "Permission refusée", "Vous n'avez pas la permission de traiter la paie.")
            return

        if not self.current_period:
            return

        try:
            count = 0
            errors = []

            for record in self.payroll_records:
                try:
                    self.calculate_single_record(record)
                    count += 1
                except Exception as e:
                    errors.append(f"{record['full_name']}: {str(e)}")

            if errors:
                QMessageBox.warning(
                    self,
                    "Calculs Terminés avec Erreurs",
                    f"{count} calculs réussis.\n\nErreurs:\n" + "\n".join(errors[:5])
                )
            else:
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Calculs effectués pour {count} employé(s)."
                )

            self.load_payroll_records()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du calcul:\n{e}")

    def edit_payroll_record(self, record):
        """Edit a payroll record"""
        if not AuthManager.has_permission('can_process_payroll'):
            QMessageBox.warning(self, "Permission refusée", "Vous n'avez pas la permission de modifier la paie.")
            return

        # Open edit dialog
        dialog = PayrollEditDialog(
            employee_name=record['full_name'],
            record=record,
            parent=self
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get modified data
            modified_data = dialog.get_data()

            # Update the record with modified values
            record_copy = dict(record)
            record_copy.update(modified_data)

            # Recalculate with new values
            self.calculate_single_record(record_copy)

    def finalize_period(self):
        """Finalize the current period"""
        if not AuthManager.has_permission('can_finalize_payroll'):
            QMessageBox.warning(self, "Permission refusée", "Vous n'avez pas la permission de finaliser la paie.")
            return

        if not self.current_period:
            return

        reply = QMessageBox.question(
            self,
            "Confirmer la Finalisation",
            "Êtes-vous sûr de vouloir finaliser cette période?\n\n"
            "Une fois finalisée, la période ne pourra plus être modifiée.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if PayrollRepository.finalize_period(self.current_period['period_id']):
                QMessageBox.information(self, "Succès", "Période finalisée avec succès.")
                self.load_periods()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la finalisation.")
