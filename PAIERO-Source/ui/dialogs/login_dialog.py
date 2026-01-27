"""
Login Dialog
User authentication dialog
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.auth import AuthManager


class LoginDialog(QDialog):
    """Login dialog for user authentication"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PAIERO - Connexion")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setMinimumHeight(350)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("PAIERO")
        title_font = QFont()
        title_font.setPointSize(32)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; padding: 20px;")
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Système de Gestion de Paie")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        # Login form group
        form_group = QGroupBox("Connexion")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding: 20px 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #3498db;
            }
        """)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # Username field
        username_label = QLabel("Nom d'utilisateur:")
        username_label.setStyleSheet("font-weight: normal;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("admin")
        self.username_input.setMinimumHeight(35)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.username_input.returnPressed.connect(self.login)
        form_layout.addRow(username_label, self.username_input)

        # Password field
        password_label = QLabel("Mot de passe:")
        password_label.setStyleSheet("font-weight: normal;")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("admin")
        self.password_input.setMinimumHeight(35)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.password_input.returnPressed.connect(self.login)
        form_layout.addRow(password_label, self.password_input)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Info message
        info_label = QLabel("💡 Compte par défaut: admin / admin")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("""
            color: #7f8c8d;
            font-size: 11px;
            font-style: italic;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
        """)
        layout.addWidget(info_label)

        # Login button
        login_btn = QPushButton("Se Connecter")
        login_btn.setMinimumHeight(40)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        layout.addStretch()

        # Set focus to username field
        self.username_input.setFocus()

    def login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        # Validate inputs
        if not username:
            QMessageBox.warning(
                self,
                "Champ Requis",
                "Veuillez entrer votre nom d'utilisateur."
            )
            self.username_input.setFocus()
            return

        if not password:
            QMessageBox.warning(
                self,
                "Champ Requis",
                "Veuillez entrer votre mot de passe."
            )
            self.password_input.setFocus()
            return

        # Attempt login
        success, error_message = AuthManager.login(username, password)

        if success:
            # Login successful
            self.accept()
        else:
            # Login failed
            QMessageBox.critical(
                self,
                "Erreur de Connexion",
                error_message
            )
            self.password_input.clear()
            self.password_input.setFocus()

    def keyPressEvent(self, event):
        """Handle key press events"""
        # Prevent closing with Escape key
        if event.key() != Qt.Key.Key_Escape:
            super().keyPressEvent(event)
