"""
User Management Screen
Admin interface for managing system users
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QAbstractItemView, QDialog, QLineEdit, QComboBox, QFormLayout,
    QDialogButtonBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from database.auth import AuthManager
from ui.dialogs.permissions_dialog import PermissionsDialog


class ChangePasswordDialog(QDialog):
    """Dialog to change user password"""

    def __init__(self, user_id, username, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.username = username
        self.setWindowTitle(f"Changer le Mot de Passe - {username}")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Header
        header = QLabel(f"Nouveau mot de passe pour: {self.username}")
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(header)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Entrez le nouveau mot de passe")
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 13px;
            }
        """)
        form_layout.addRow("Mot de passe:", self.password_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirmez le mot de passe")
        self.confirm_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 13px;
            }
        """)
        form_layout.addRow("Confirmation:", self.confirm_input)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_password)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def save_password(self):
        """Save new password"""
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not password:
            QMessageBox.warning(self, "Erreur", "Le mot de passe ne peut pas être vide")
            return

        if len(password) < 4:
            QMessageBox.warning(self, "Erreur", "Le mot de passe doit contenir au moins 4 caractères")
            return

        if password != confirm:
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas")
            return

        # Change password
        success, error = AuthManager.change_password(self.user_id, password)

        if success:
            QMessageBox.information(self, "Succès", "Mot de passe modifié avec succès")
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", error)


class AddUserDialog(QDialog):
    """Dialog to add a new user"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un Utilisateur")
        self.setMinimumWidth(450)
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Header
        header = QLabel("Créer un nouveau compte utilisateur")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(header)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur unique")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 13px;
            }
        """)
        form_layout.addRow("Nom d'utilisateur:", self.username_input)

        # Full name
        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Nom complet de l'utilisateur")
        self.fullname_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 13px;
            }
        """)
        form_layout.addRow("Nom complet:", self.fullname_input)

        # Role
        self.role_combo = QComboBox()
        self.role_combo.addItem("Utilisateur", "user")
        self.role_combo.addItem("Administrateur", "admin")
        self.role_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 13px;
            }
        """)
        form_layout.addRow("Rôle:", self.role_combo)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Mot de passe initial")
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 13px;
            }
        """)
        form_layout.addRow("Mot de passe:", self.password_input)

        # Confirm password
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirmez le mot de passe")
        self.confirm_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 13px;
            }
        """)
        form_layout.addRow("Confirmation:", self.confirm_input)

        layout.addLayout(form_layout)

        # Info note
        info_label = QLabel("ℹ️ L'utilisateur pourra changer son mot de passe après la première connexion")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 11px; font-style: italic; padding: 8px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.create_user)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def create_user(self):
        """Create new user"""
        username = self.username_input.text().strip()
        fullname = self.fullname_input.text().strip()
        role = self.role_combo.currentData()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        # Validation
        if not username:
            QMessageBox.warning(self, "Erreur", "Le nom d'utilisateur est requis")
            return

        if len(username) < 3:
            QMessageBox.warning(self, "Erreur", "Le nom d'utilisateur doit contenir au moins 3 caractères")
            return

        if not fullname:
            QMessageBox.warning(self, "Erreur", "Le nom complet est requis")
            return

        if not password:
            QMessageBox.warning(self, "Erreur", "Le mot de passe est requis")
            return

        if len(password) < 4:
            QMessageBox.warning(self, "Erreur", "Le mot de passe doit contenir au moins 4 caractères")
            return

        if password != confirm:
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas")
            return

        # Create user
        success, error = AuthManager.create_user(username, password, fullname, role)

        if success:
            QMessageBox.information(self, "Succès", f"Utilisateur '{username}' créé avec succès")
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", error)


class UserManagementScreen(QWidget):
    """User management screen for administrators"""

    def __init__(self):
        super().__init__()
        self.users = []
        self.init_ui()
        self.load_users()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Gestion des Utilisateurs")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Add user button
        add_btn = QPushButton("+ Nouvel Utilisateur")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_user)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        # Subtitle
        subtitle = QLabel("Gérer les comptes utilisateurs et leurs permissions")
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(subtitle)

        # Users table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Nom d'utilisateur", "Nom Complet", "Rôle",
            "Statut", "Dernière Connexion", "Créé le", "Actions"
        ])

        # Table styling
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(50)

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)

        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(6, 280)

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
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)

        layout.addWidget(self.table)

        # Summary
        self.summary_label = QLabel()
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

    def load_users(self):
        """Load users from database"""
        self.users = AuthManager.get_all_users()
        self.display_users()

    def display_users(self):
        """Display users in table"""
        self.table.setRowCount(0)

        active_count = 0
        admin_count = 0

        for user in self.users:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Username
            username_item = QTableWidgetItem(user['username'])
            username_item.setFont(QFont("", -1, QFont.Weight.Bold))
            self.table.setItem(row, 0, username_item)

            # Full name
            self.table.setItem(row, 1, QTableWidgetItem(user['full_name']))

            # Role
            role_text = "Admin" if user['role'] == 'admin' else "Utilisateur"
            role_item = QTableWidgetItem(role_text)
            role_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if user['role'] == 'admin':
                role_item.setForeground(QColor("#e74c3c"))
                admin_count += 1
            else:
                role_item.setForeground(QColor("#3498db"))
            self.table.setItem(row, 2, role_item)

            # Status
            status_text = "Actif" if user['is_active'] else "Inactif"
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if user['is_active']:
                status_item.setForeground(QColor("#27ae60"))
                active_count += 1
            else:
                status_item.setForeground(QColor("#95a5a6"))
            self.table.setItem(row, 3, status_item)

            # Last login
            last_login = user['last_login'] if user['last_login'] else "Jamais"
            if user['last_login']:
                # Format datetime to readable format
                last_login = last_login[:16].replace('T', ' ')
            last_login_item = QTableWidgetItem(last_login)
            last_login_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, last_login_item)

            # Created date
            created = user['created_at'][:10]  # Just the date part
            created_item = QTableWidgetItem(created)
            created_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 5, created_item)

            # Actions
            actions_widget = self.create_action_buttons(user)
            self.table.setCellWidget(row, 6, actions_widget)

        # Update summary
        total_count = len(self.users)
        self.summary_label.setText(
            f"Total: {total_count} utilisateur(s) | "
            f"Actifs: {active_count} | "
            f"Administrateurs: {admin_count}"
        )

    def create_action_buttons(self, user):
        """Create action buttons for a user"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Change password button
        password_btn = QPushButton("🔑 Mot de passe")
        password_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 6px 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        password_btn.clicked.connect(lambda: self.change_password(user))
        layout.addWidget(password_btn)

        # Permissions button
        permissions_btn = QPushButton("🔒 Permissions")
        permissions_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 6px 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        permissions_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        permissions_btn.clicked.connect(lambda: self.manage_permissions(user))
        layout.addWidget(permissions_btn)

        # Toggle active button
        toggle_text = "❌ Désactiver" if user['is_active'] else "✓ Activer"
        toggle_color = "#e74c3c" if user['is_active'] else "#27ae60"

        toggle_btn = QPushButton(toggle_text)
        toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {toggle_color};
                color: white;
                border: none;
                border-radius: 3px;
                padding: 6px 10px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        toggle_btn.clicked.connect(lambda: self.toggle_user(user))
        layout.addWidget(toggle_btn)

        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 6px 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(lambda: self.delete_user(user))
        layout.addWidget(delete_btn)

        return widget

    def add_user(self):
        """Add a new user"""
        dialog = AddUserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()

    def change_password(self, user):
        """Change user password"""
        dialog = ChangePasswordDialog(user['user_id'], user['username'], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()

    def manage_permissions(self, user):
        """Manage user permissions"""
        dialog = PermissionsDialog(user['user_id'], user['username'], self)
        dialog.exec()

    def toggle_user(self, user):
        """Toggle user active status"""
        action = "désactiver" if user['is_active'] else "activer"

        reply = QMessageBox.question(
            self,
            "Confirmer",
            f"Voulez-vous vraiment {action} l'utilisateur '{user['username']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, error = AuthManager.toggle_user_active(user['user_id'])

            if success:
                QMessageBox.information(self, "Succès", f"Utilisateur {action}é avec succès")
                self.load_users()
            else:
                QMessageBox.critical(self, "Erreur", error)

    def delete_user(self, user):
        """Delete a user"""
        reply = QMessageBox.question(
            self,
            "Confirmer la Suppression",
            f"Êtes-vous sûr de vouloir supprimer l'utilisateur '{user['username']}'?\n\n"
            "Cette action est irréversible!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, error = AuthManager.delete_user(user['user_id'])

            if success:
                QMessageBox.information(self, "Succès", "Utilisateur supprimé avec succès")
                self.load_users()
            else:
                QMessageBox.critical(self, "Erreur", error)
