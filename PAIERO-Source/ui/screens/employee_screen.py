"""
Employee Management Screen
List, search, add, edit, and delete employees
"""

import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox,
    QHeaderView, QAbstractItemView, QComboBox, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.repositories.employee_repository import EmployeeRepository
from models.employee import Employee
from ui.dialogs.employee_dialog import EmployeeDialog
from database.auth import AuthManager


class EmployeeScreen(QWidget):
    """Employee management screen"""

    def __init__(self):
        super().__init__()
        self.employees = []
        self.filtered_employees = []
        self.init_ui()
        self.load_employees()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title and actions header
        header_layout = QHBoxLayout()

        title = QLabel("Gestion des Employés")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Add employee button (only if user has permission)
        if AuthManager.has_permission('can_edit_employees'):
            add_btn = QPushButton("+ Ajouter Employé")
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
                QPushButton:pressed {
                    background-color: #229954;
                }
            """)
            add_btn.clicked.connect(self.add_employee)
            header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        # Search and filter bar
        search_layout = QHBoxLayout()

        search_label = QLabel("Recherche:")
        search_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par ID, nom ou poste...")
        self.search_input.textChanged.connect(self.on_search)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
            }
        """)
        search_layout.addWidget(self.search_input, 1)

        # Department filter
        dept_label = QLabel("Département:")
        search_layout.addWidget(dept_label)

        self.dept_filter = QComboBox()
        self.dept_filter.addItem("Tous", None)
        self.dept_filter.currentIndexChanged.connect(self.on_filter_change)
        self.dept_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        search_layout.addWidget(self.dept_filter)

        # Status filter
        status_label = QLabel("Statut:")
        search_layout.addWidget(status_label)

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
        search_layout.addWidget(self.status_filter)

        # Refresh button
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.clicked.connect(self.load_employees)
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
        search_layout.addWidget(refresh_btn)

        layout.addLayout(search_layout)

        # Employee table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom Complet", "Poste", "Catégorie",
            "Statut", "Date d'Embauche", "Ancienneté", "Actions"
        ])

        # Table styling
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)

        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(7, 200)

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

        # Status bar at bottom
        self.status_label = QLabel("Chargement...")
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self.status_label)

    def load_employees(self):
        """Load employees from database"""
        try:
            include_inactive = self.status_filter.currentData()
            self.employees = EmployeeRepository.get_all(include_inactive=include_inactive)
            self.filtered_employees = self.employees

            # Load departments for filter
            departments = EmployeeRepository.get_departments()
            current_dept = self.dept_filter.currentData()

            # Block signals to prevent infinite loop
            self.dept_filter.blockSignals(True)
            self.dept_filter.clear()
            self.dept_filter.addItem("Tous", None)
            for dept in departments:
                self.dept_filter.addItem(dept, dept)

            # Restore selected department
            if current_dept:
                index = self.dept_filter.findData(current_dept)
                if index >= 0:
                    self.dept_filter.setCurrentIndex(index)

            # Unblock signals
            self.dept_filter.blockSignals(False)

            self.apply_filters()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des employés:\n{e}")

    def apply_filters(self):
        """Apply search and filters"""
        # Start with all employees
        filtered = list(self.employees)

        # Apply search filter
        search_text = self.search_input.text().strip()
        if search_text:
            filtered = [
                emp for emp in filtered
                if search_text.lower() in emp.employee_id.lower()
                or search_text.lower() in emp.full_name.lower()
                or (emp.position and search_text.lower() in emp.position.lower())
            ]

        # Apply department filter
        dept_code = self.dept_filter.currentData()
        if dept_code:
            filtered = [emp for emp in filtered if emp.department_code == dept_code]

        self.filtered_employees = filtered
        self.display_employees()

    def display_employees(self):
        """Display employees in table"""
        self.table.setRowCount(0)

        for employee in self.filtered_employees:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ID
            id_item = QTableWidgetItem(employee.employee_id)
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, id_item)

            # Full Name
            self.table.setItem(row, 1, QTableWidgetItem(employee.full_name))

            # Position
            self.table.setItem(row, 2, QTableWidgetItem(employee.position or "-"))

            # Category
            category_item = QTableWidgetItem(employee.category or "-")
            category_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, category_item)

            # Status
            status_item = QTableWidgetItem("Actif" if employee.is_active else "Inactif")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if employee.is_active:
                status_item.setForeground(QColor("#2ecc71"))
            else:
                status_item.setForeground(QColor("#e74c3c"))
            self.table.setItem(row, 4, status_item)

            # Hire Date
            hire_date = employee.hire_date.strftime("%d/%m/%Y") if employee.hire_date else "-"
            date_item = QTableWidgetItem(hire_date)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 5, date_item)

            # Seniority
            seniority = f"{employee.seniority:.1f} ans" if employee.seniority else "-"
            sen_item = QTableWidgetItem(seniority)
            sen_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 6, sen_item)

            # Actions buttons
            actions_widget = self.create_action_buttons(employee)
            self.table.setCellWidget(row, 7, actions_widget)

        # Update status label with timestamp
        from datetime import datetime
        total = len(self.employees)
        shown = len(self.filtered_employees)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_label.setText(
            f"Affichage de {shown} employé(s) sur {total} | 🔄 Actualisé: {timestamp}"
        )

    def create_action_buttons(self, employee: Employee):
        """Create action buttons for a row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)

        # Edit button (only if user has permission)
        if AuthManager.has_permission('can_edit_employees'):
            edit_btn = QPushButton("Modifier")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            edit_btn.clicked.connect(lambda: self.edit_employee(employee))
            layout.addWidget(edit_btn)

        # Delete/Restore button (only if user has permission)
        if employee.is_active and AuthManager.has_permission('can_delete_employees'):
            delete_btn = QPushButton("Supprimer")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda: self.delete_employee(employee))
            layout.addWidget(delete_btn)
        elif not employee.is_active and AuthManager.has_permission('can_edit_employees'):
            restore_btn = QPushButton("Restaurer")
            restore_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """)
            restore_btn.clicked.connect(lambda: self.restore_employee(employee))
            layout.addWidget(restore_btn)

        # If no buttons shown, add a label
        if layout.count() == 0:
            no_action_label = QLabel("Lecture seule")
            no_action_label.setStyleSheet("color: #95a5a6; font-style: italic; font-size: 11px;")
            layout.addWidget(no_action_label)

        return widget

    def on_search(self, text):
        """Handle search text change"""
        self.apply_filters()

    def on_filter_change(self, index):
        """Handle filter change"""
        self.load_employees()

    def add_employee(self):
        """Open dialog to add new employee"""
        if not AuthManager.has_permission('can_edit_employees'):
            QMessageBox.warning(self, "Permission refusée", "Vous n'avez pas la permission d'ajouter des employés.")
            return

        dialog = EmployeeDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_employees()

    def edit_employee(self, employee: Employee):
        """Open dialog to edit employee"""
        if not AuthManager.has_permission('can_edit_employees'):
            QMessageBox.warning(self, "Permission refusée", "Vous n'avez pas la permission de modifier des employés.")
            return

        dialog = EmployeeDialog(parent=self, employee=employee)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_employees()

    def delete_employee(self, employee: Employee):
        """Delete employee (soft delete)"""
        if not AuthManager.has_permission('can_delete_employees'):
            QMessageBox.warning(self, "Permission refusée", "Vous n'avez pas la permission de supprimer des employés.")
            return

        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer l'employé:\n\n{employee.full_name} ({employee.employee_id})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if EmployeeRepository.delete(employee.employee_id):
                QMessageBox.information(self, "Succès", "Employé supprimé avec succès.")
                self.load_employees()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la suppression de l'employé.")

    def restore_employee(self, employee: Employee):
        """Restore deleted employee"""
        if EmployeeRepository.restore(employee.employee_id):
            QMessageBox.information(self, "Succès", "Employé restauré avec succès.")
            self.load_employees()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de la restauration de l'employé.")
