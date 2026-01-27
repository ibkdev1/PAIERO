"""
Loan Management Screen
Manage employee loans and advances
"""

import sys
import os
from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QAbstractItemView, QComboBox, QDialog, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.repositories.employee_repository import EmployeeRepository
from database.repositories.loan_repository import LoanRepository
from ui.dialogs.loan_dialog import LoanDialog
from database.auth import AuthManager


class LoanScreen(QWidget):
    """Loan management screen"""

    def __init__(self):
        super().__init__()
        self.loans = []
        self.filtered_loans = []
        self.init_ui()
        self.load_loans()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Avances & Prêts")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Add loan button
        add_btn = QPushButton("+ Nouveau Prêt/Avance")
        add_btn.setStyleSheet("""
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
        add_btn.clicked.connect(self.add_loan)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        # Search and filter bar
        filter_layout = QHBoxLayout()

        search_label = QLabel("Recherche:")
        filter_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par employé...")
        self.search_input.textChanged.connect(self.on_search)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
            }
        """)
        filter_layout.addWidget(self.search_input, 1)

        # Status filter
        status_label = QLabel("Statut:")
        filter_layout.addWidget(status_label)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Actifs", False)
        self.status_filter.addItem("Tous", True)
        self.status_filter.currentIndexChanged.connect(self.on_filter_change)
        self.status_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        filter_layout.addWidget(self.status_filter)

        # Refresh button
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.clicked.connect(self.load_loans)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        filter_layout.addWidget(refresh_btn)

        layout.addLayout(filter_layout)

        # Loans table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Employé", "Type", "Montant Total", "Restant",
            "Mensualité", "Date Octroi", "Durée", "Statut", "Actions"
        ])

        # Table styling
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40)

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)

        self.table.setColumnWidth(1, 80)
        self.table.setColumnWidth(6, 80)
        self.table.setColumnWidth(7, 80)
        self.table.setColumnWidth(8, 180)

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
        self.summary_label = QLabel("Chargement...")
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

    def load_loans(self):
        """Load loans from database"""
        try:
            include_inactive = self.status_filter.currentData()
            self.loans = LoanRepository.get_all_loans(include_inactive=include_inactive)
            self.filtered_loans = self.loans
            self.apply_filters()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des prêts:\n{e}")

    def apply_filters(self):
        """Apply search filters"""
        filtered = list(self.loans)

        # Apply search filter
        search_text = self.search_input.text().strip().lower()
        if search_text:
            filtered = [
                loan for loan in filtered
                if search_text in loan['full_name'].lower()
            ]

        self.filtered_loans = filtered
        self.display_loans()

    def display_loans(self):
        """Display loans in table"""
        self.table.setRowCount(0)

        total_amount = 0
        total_remaining = 0

        for loan in self.filtered_loans:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Employee name
            self.table.setItem(row, 0, QTableWidgetItem(loan['full_name']))

            # Type
            type_item = QTableWidgetItem(loan['loan_type'])
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, type_item)

            # Total amount
            total_item = QTableWidgetItem(f"{int(loan['total_amount']):,}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 2, total_item)
            total_amount += loan['total_amount']

            # Remaining balance
            remaining_item = QTableWidgetItem(f"{int(loan['remaining_balance']):,}")
            remaining_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            remaining_item.setForeground(QColor("#e74c3c") if loan['remaining_balance'] > 0 else QColor("#27ae60"))
            self.table.setItem(row, 3, remaining_item)
            total_remaining += loan['remaining_balance']

            # Monthly payment
            monthly_item = QTableWidgetItem(f"{int(loan['monthly_payment']):,}")
            monthly_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 4, monthly_item)

            # Grant date
            grant_date = loan['grant_date'] if loan['grant_date'] else "-"
            date_item = QTableWidgetItem(grant_date)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 5, date_item)

            # Duration
            duration_item = QTableWidgetItem(f"{loan['duration_months']} mois")
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 6, duration_item)

            # Status
            status = "Actif" if loan['is_active'] else "Soldé"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if loan['is_active']:
                status_item.setForeground(QColor("#27ae60"))
            else:
                status_item.setForeground(QColor("#95a5a6"))
            self.table.setItem(row, 7, status_item)

            # Actions
            actions_widget = self.create_action_buttons(loan)
            self.table.setCellWidget(row, 8, actions_widget)

        # Update summary with timestamp
        from datetime import datetime
        count = len(self.filtered_loans)
        active_count = sum(1 for l in self.filtered_loans if l['is_active'])
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.summary_label.setText(
            f"Total: {count} prêt(s) | Actifs: {active_count} | "
            f"Montant Total: {int(total_amount):,} CFA | "
            f"Restant: {int(total_remaining):,} CFA | "
            f"🔄 Actualisé: {timestamp}"
        )

    def create_action_buttons(self, loan):
        """Create action buttons for a loan"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # View button
        view_btn = QPushButton("👁️ Voir")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        view_btn.clicked.connect(lambda: self.view_loan_details(loan))
        layout.addWidget(view_btn)

        # Delete button (only for unpaid loans)
        if loan['is_active']:
            delete_btn = QPushButton("🗑️")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px 10px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda: self.delete_loan(loan))
            layout.addWidget(delete_btn)

        return widget

    def on_search(self, text):
        """Handle search text change"""
        self.apply_filters()

    def on_filter_change(self, index):
        """Handle filter change"""
        self.load_loans()

    def add_loan(self):
        """Add a new loan"""
        if not AuthManager.has_permission('can_manage_loans'):
            QMessageBox.warning(self, "Permission refusée", "Vous n'avez pas la permission de gérer les prêts.")
            return

        try:
            employees = EmployeeRepository.get_all()
            dialog = LoanDialog(employees, parent=self)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                loan_id = LoanRepository.create_loan(
                    employee_id=data['employee_id'],
                    loan_type=data['loan_type'],
                    total_amount=data['total_amount'],
                    grant_date=data['grant_date'],
                    duration_months=data['duration_months'],
                    notes=data['notes']
                )
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Prêt/Avance créé avec succès.\nMensualité: {int(data['total_amount'] / data['duration_months']):,} CFA"
                )
                self.load_loans()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création:\n{e}")

    def view_loan_details(self, loan):
        """View loan payment schedule"""
        try:
            schedule = LoanRepository.get_payment_schedule(loan['loan_id'])

            # Build message
            msg = f"Prêt pour: {loan['full_name']}\n\n"
            msg += f"Montant Total: {int(loan['total_amount']):,} CFA\n"
            msg += f"Restant: {int(loan['remaining_balance']):,} CFA\n"
            msg += f"Mensualité: {int(loan['monthly_payment']):,} CFA\n"
            msg += f"Durée: {loan['duration_months']} mois\n\n"
            msg += "Échéancier:\n"

            for i, payment in enumerate(schedule, 1):
                status = "✓ Payé" if payment['is_paid'] else "⏳ En attente"
                msg += f"{i}. {payment['payment_date']} - {int(payment['scheduled_amount']):,} CFA - {status}\n"

            QMessageBox.information(self, "Détails du Prêt", msg)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{e}")

    def delete_loan(self, loan):
        """Delete a loan"""
        if not AuthManager.has_permission('can_manage_loans'):
            QMessageBox.warning(self, "Permission refusée", "Vous n'avez pas la permission de supprimer des prêts.")
            return

        reply = QMessageBox.question(
            self,
            "Confirmer la Suppression",
            f"Êtes-vous sûr de vouloir supprimer ce prêt?\n\n"
            f"Employé: {loan['full_name']}\n"
            f"Montant: {int(loan['total_amount']):,} CFA\n"
            f"Restant: {int(loan['remaining_balance']):,} CFA",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if LoanRepository.delete_loan(loan['loan_id']):
                QMessageBox.information(self, "Succès", "Prêt supprimé avec succès.")
                self.load_loans()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la suppression.")
