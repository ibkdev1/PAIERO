"""
Permissions Management Dialog
Configure user permissions for granular access control
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QMessageBox, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.auth import AuthManager


class PermissionsDialog(QDialog):
    """Dialog for managing user permissions"""

    def __init__(self, user_id: int, username: str, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.username = username
        self.permission_checkboxes = {}

        self.setWindowTitle(f"Permissions - {username}")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)

        self.init_ui()
        self.load_permissions()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel(f"Configurer les Permissions")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # User info
        user_info = QLabel(f"Utilisateur: {self.username}")
        user_info.setStyleSheet("color: #7f8c8d; font-size: 13px; margin-bottom: 10px;")
        layout.addWidget(user_info)

        # Scroll area for permissions
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Container for permission groups
        permissions_widget = QWidget()
        permissions_layout = QVBoxLayout(permissions_widget)
        permissions_layout.setSpacing(15)

        # Employee permissions group
        employee_group = self.create_permission_group(
            "👥 Gestion des Employés",
            [
                ("can_view_employees", "Consulter les employés"),
                ("can_edit_employees", "Modifier les employés"),
                ("can_delete_employees", "Supprimer les employés")
            ]
        )
        permissions_layout.addWidget(employee_group)

        # Payroll permissions group
        payroll_group = self.create_permission_group(
            "💰 Gestion de la Paie",
            [
                ("can_view_payroll", "Consulter la paie"),
                ("can_process_payroll", "Traiter la paie"),
                ("can_finalize_payroll", "Finaliser les périodes de paie")
            ]
        )
        permissions_layout.addWidget(payroll_group)

        # Loan permissions group
        loan_group = self.create_permission_group(
            "💳 Gestion des Prêts & Avances",
            [
                ("can_view_loans", "Consulter les prêts"),
                ("can_manage_loans", "Gérer les prêts et avances")
            ]
        )
        permissions_layout.addWidget(loan_group)

        # Report permissions group
        report_group = self.create_permission_group(
            "📊 Rapports & Exports",
            [
                ("can_generate_reports", "Générer des rapports"),
                ("can_export_data", "Exporter les données")
            ]
        )
        permissions_layout.addWidget(report_group)

        # Parameter permissions group
        param_group = self.create_permission_group(
            "⚙️ Paramètres Système",
            [
                ("can_view_parameters", "Consulter les paramètres"),
                ("can_modify_parameters", "Modifier les paramètres")
            ]
        )
        permissions_layout.addWidget(param_group)

        # User management permissions group
        user_group = self.create_permission_group(
            "🔐 Gestion des Utilisateurs",
            [
                ("can_manage_users", "Gérer les comptes utilisateurs (Admin uniquement)")
            ]
        )
        permissions_layout.addWidget(user_group)

        permissions_layout.addStretch()

        scroll.setWidget(permissions_widget)
        layout.addWidget(scroll)

        # Info note
        info_label = QLabel("💡 Les administrateurs ont toujours un accès complet, quelle que soit la configuration des permissions.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            color: #7f8c8d;
            font-size: 11px;
            font-style: italic;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
        """)
        layout.addWidget(info_label)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Annuler")
        cancel_btn.setMinimumWidth(120)
        cancel_btn.setMinimumHeight(35)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setMinimumWidth(120)
        save_btn.setMinimumHeight(35)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.save_permissions)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

    def create_permission_group(self, title: str, permissions: list) -> QGroupBox:
        """Create a group of permission checkboxes"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px 10px 10px 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #3498db;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        for permission_key, permission_label in permissions:
            checkbox = QCheckBox(permission_label)
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-weight: normal;
                    font-size: 13px;
                    padding: 5px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                }
            """)
            self.permission_checkboxes[permission_key] = checkbox
            layout.addWidget(checkbox)

        group.setLayout(layout)
        return group

    def load_permissions(self):
        """Load current permissions from database"""
        permissions = AuthManager.get_user_permissions(self.user_id)

        if permissions:
            for key, checkbox in self.permission_checkboxes.items():
                value = permissions.get(key, 0)
                checkbox.setChecked(value == 1)

    def save_permissions(self):
        """Save permissions to database"""
        # Collect permission values
        permissions = {}
        for key, checkbox in self.permission_checkboxes.items():
            permissions[key] = 1 if checkbox.isChecked() else 0

        # Save to database
        success, error = AuthManager.set_user_permissions(self.user_id, permissions)

        if success:
            QMessageBox.information(
                self,
                "Succès",
                "Les permissions ont été enregistrées avec succès."
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'enregistrement des permissions:\n{error}"
            )
