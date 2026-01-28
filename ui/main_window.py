"""
Main Application Window
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QMessageBox,
    QStatusBar, QMenuBar, QMenu, QFileDialog, QDialog,
    QFormLayout, QDateEdit, QComboBox, QDialogButtonBox, QLineEdit
)
from PyQt6.QtCore import Qt, QSize, QDate
from PyQt6.QtGui import QAction, QFont
import os
from datetime import datetime, date

from config import APP_TITLE, APP_VERSION, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, \
    WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT, BACKUP_DIR, REPORTS_DIR
from ui.screens.dashboard_screen import DashboardScreen
from ui.screens.employee_screen import EmployeeScreen
from ui.screens.payroll_screen import PayrollScreen
from ui.screens.loan_screen import LoanScreen
from ui.screens.parameter_screen import ParameterScreen
from ui.screens.report_screen import ReportScreen
from ui.screens.user_management_screen import UserManagementScreen
from ui.dialogs.about_dialog import AboutDialog
from database.auth import AuthManager


class MainWindow(QMainWindow):
    """Main application window with navigation sidebar"""

    def __init__(self):
        super().__init__()
        self.current_screen = None
        self.user_management_screen = None  # Initialize to None for non-admin users
        try:
            self.init_ui()
        except Exception as e:
            print(f"ERROR in MainWindow.init_ui: {e}")
            import traceback
            traceback.print_exc()
            raise

    def init_ui(self):
        """Initialize the user interface"""
        # Set window properties
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)

        # Create menu bar
        self.create_menu_bar()

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create navigation sidebar
        navigation = self.create_navigation()
        main_layout.addWidget(navigation)

        # Create content area with stacked widget
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #f5f5f5;
            }
        """)

        main_layout.addWidget(self.content_stack)

        # Initialize screens
        self.init_screens()

        # Create status bar
        self.create_status_bar()

        # Show dashboard by default
        self.show_dashboard()

    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("Fichier")

        new_period_action = QAction("Nouvelle Période", self)
        new_period_action.triggered.connect(self.new_period)
        file_menu.addAction(new_period_action)

        import_action = QAction("Importer CSV...", self)
        import_action.triggered.connect(self.import_csv)
        file_menu.addAction(import_action)

        export_action = QAction("Exporter...", self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        backup_action = QAction("Sauvegarder", self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)

        file_menu.addSeparator()

        logout_action = QAction("Déconnexion", self)
        logout_action.setShortcut("Ctrl+L")
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        exit_action = QAction("Quitter", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Édition")

        edit_employee_action = QAction("Employés...", self)
        edit_employee_action.setShortcut("Ctrl+E")
        edit_employee_action.triggered.connect(self.show_employees)
        edit_menu.addAction(edit_employee_action)

        edit_payroll_action = QAction("Paie...", self)
        edit_payroll_action.setShortcut("Ctrl+P")
        edit_payroll_action.triggered.connect(self.show_payroll)
        edit_menu.addAction(edit_payroll_action)

        edit_loans_action = QAction("Prêts/Avances...", self)
        edit_loans_action.setShortcut("Ctrl+A")
        edit_loans_action.triggered.connect(self.show_loans)
        edit_menu.addAction(edit_loans_action)

        edit_menu.addSeparator()

        edit_parameters_action = QAction("Paramètres...", self)
        edit_parameters_action.triggered.connect(self.show_parameters)
        edit_menu.addAction(edit_parameters_action)

        # Reports menu
        reports_menu = menubar.addMenu("Rapports")

        salary_slip_action = QAction("Bulletin de Salaire...", self)
        salary_slip_action.triggered.connect(self.generate_salary_slip)
        reports_menu.addAction(salary_slip_action)

        payroll_summary_action = QAction("Résumé de Paie...", self)
        payroll_summary_action.triggered.connect(self.generate_payroll_summary)
        reports_menu.addAction(payroll_summary_action)

        reports_menu.addSeparator()

        all_reports_action = QAction("Tous les Rapports...", self)
        all_reports_action.triggered.connect(self.show_reports)
        reports_menu.addAction(all_reports_action)

        # Tools menu
        tools_menu = menubar.addMenu("Outils")

        settings_action = QAction("Paramètres", self)
        settings_action.triggered.connect(self.show_parameters)
        tools_menu.addAction(settings_action)

        # User management (admin only)
        if AuthManager.is_admin():
            tools_menu.addSeparator()
            user_mgmt_action = QAction("Gestion des Utilisateurs", self)
            user_mgmt_action.triggered.connect(self.show_user_management)
            tools_menu.addAction(user_mgmt_action)

        # Help menu
        help_menu = menubar.addMenu("Aide")

        about_action = QAction("À propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_navigation(self):
        """Create navigation sidebar"""
        nav_frame = QFrame()
        nav_frame.setFixedWidth(240)
        nav_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-right: 1px solid #1a252f;
            }
        """)

        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)

        # Application title section
        title_container = QWidget()
        title_container.setStyleSheet("background-color: #1a252f;")
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(15, 25, 15, 25)
        title_layout.setSpacing(5)

        # Main title
        main_title = QLabel("PAIERO")
        main_title.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 26px;
                font-weight: bold;
                letter-spacing: 2px;
            }
        """)
        main_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(main_title)

        # Subtitle
        subtitle = QLabel("Gestion de Paie")
        subtitle.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 13px;
                font-weight: normal;
            }
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle)

        nav_layout.addWidget(title_container)

        # Navigation buttons
        self.nav_buttons = {}

        buttons_config = [
            ("dashboard", "Tableau de Bord", self.show_dashboard),
            ("employees", "Employés", self.show_employees),
            ("payroll", "Paie", self.show_payroll),
            ("loans", "Avances & Prêts", self.show_loans),
            ("reports", "Rapports", self.show_reports),
            ("parameters", "Paramètres", self.show_parameters),
        ]

        for btn_id, text, callback in buttons_config:
            btn = self.create_nav_button(text, callback)
            self.nav_buttons[btn_id] = btn
            nav_layout.addWidget(btn)

        # Add stretch to push buttons to top
        nav_layout.addStretch()

        # User session display
        user_frame = QWidget()
        user_frame.setStyleSheet("""
            QWidget {
                background-color: #1a252f;
                border-top: 1px solid #34495e;
                padding: 15px;
            }
        """)
        user_layout = QVBoxLayout(user_frame)
        user_layout.setSpacing(8)

        # Current user info
        current_user = AuthManager.get_current_user()
        if current_user:
            user_icon = QLabel("👤")
            user_icon.setStyleSheet("font-size: 20px;")
            user_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            user_layout.addWidget(user_icon)

            user_name = QLabel(current_user['full_name'])
            user_name.setStyleSheet("""
                QLabel {
                    color: #ecf0f1;
                    font-size: 13px;
                    font-weight: bold;
                }
            """)
            user_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            user_name.setWordWrap(True)
            user_layout.addWidget(user_name)

            role_text = "Administrateur" if current_user['role'] == 'admin' else "Utilisateur"
            user_role = QLabel(role_text)
            user_role.setStyleSheet("""
                QLabel {
                    color: #3498db;
                    font-size: 11px;
                }
            """)
            user_role.setAlignment(Qt.AlignmentFlag.AlignCenter)
            user_layout.addWidget(user_role)

            # Logout button
            logout_btn = QPushButton("🚪 Déconnexion")
            logout_btn.setFixedHeight(35)
            logout_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 12px;
                    font-weight: bold;
                    margin-top: 8px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            logout_btn.clicked.connect(self.logout)
            user_layout.addWidget(logout_btn)

        nav_layout.addWidget(user_frame)

        # Version label at bottom
        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 10px;
                padding: 10px;
            }
        """)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(version_label)

        return nav_frame

    def create_nav_button(self, text, callback):
        """Create a navigation button"""
        btn = QPushButton(text)
        btn.setFixedHeight(55)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ecf0f1;
                border: none;
                text-align: left;
                padding-left: 25px;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #1a252f;
            }
            QPushButton[active="true"] {
                background-color: #3498db;
                border-left: 5px solid #2980b9;
                font-weight: bold;
            }
        """)
        btn.clicked.connect(callback)
        btn.setProperty("active", "false")
        return btn

    def set_active_nav_button(self, button_id):
        """Set the active navigation button"""
        for btn_id, btn in self.nav_buttons.items():
            if btn_id == button_id:
                btn.setProperty("active", "true")
            else:
                btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add status message
        self.status_label = QLabel("Prêt")
        self.status_bar.addWidget(self.status_label)

        # Add employee count
        self.employee_count_label = QLabel("Employés: 0")
        self.status_bar.addPermanentWidget(self.employee_count_label)

        # Add period info
        self.period_label = QLabel("Période: --")
        self.status_bar.addPermanentWidget(self.period_label)

    def init_screens(self):
        """Initialize all application screens"""
        # Dashboard
        self.dashboard_screen = DashboardScreen()

        # Connect dashboard navigation signals
        self.dashboard_screen.navigate_to_employees.connect(self.show_employees)
        self.dashboard_screen.navigate_to_payroll.connect(self.show_payroll)
        self.dashboard_screen.navigate_to_loans.connect(self.show_loans)
        self.dashboard_screen.navigate_to_reports.connect(self.show_reports)

        self.content_stack.addWidget(self.dashboard_screen)

        # Employee Management Screen
        self.employees_screen = EmployeeScreen()
        self.content_stack.addWidget(self.employees_screen)

        # Payroll Processing Screen
        self.payroll_screen = PayrollScreen()
        self.content_stack.addWidget(self.payroll_screen)

        # Loans & Advances Screen
        self.loans_screen = LoanScreen()
        self.content_stack.addWidget(self.loans_screen)

        # Reports Screen
        self.reports_screen = ReportScreen()
        self.content_stack.addWidget(self.reports_screen)

        # Parameters Screen
        self.parameters_screen = ParameterScreen()
        self.content_stack.addWidget(self.parameters_screen)

        # User Management Screen (admin only)
        if AuthManager.is_admin():
            self.user_management_screen = UserManagementScreen()
            self.content_stack.addWidget(self.user_management_screen)

    def create_placeholder_screen(self, title):
        """Create a placeholder screen for features to be implemented"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(f"{title}\n\nEn cours de développement...")
        label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #7f8c8d;
            }
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        return widget

    # Navigation methods
    def show_dashboard(self):
        """Show dashboard screen"""
        self.content_stack.setCurrentWidget(self.dashboard_screen)
        self.set_active_nav_button("dashboard")
        self.status_label.setText("Tableau de Bord")
        # Refresh dashboard data when shown
        self.dashboard_screen.refresh_data()

    def show_employees(self):
        """Show employees screen"""
        self.content_stack.setCurrentWidget(self.employees_screen)
        self.set_active_nav_button("employees")
        self.status_label.setText("Gestion des Employés")

    def show_payroll(self):
        """Show payroll screen"""
        self.content_stack.setCurrentWidget(self.payroll_screen)
        self.set_active_nav_button("payroll")
        self.status_label.setText("Traitement de la Paie")

    def show_loans(self):
        """Show loans screen"""
        self.content_stack.setCurrentWidget(self.loans_screen)
        self.set_active_nav_button("loans")
        self.status_label.setText("Avances et Prêts")

    def show_reports(self):
        """Show reports screen"""
        self.content_stack.setCurrentWidget(self.reports_screen)
        self.set_active_nav_button("reports")
        self.status_label.setText("Rapports")
        # Refresh report screen data when shown
        self.reports_screen.refresh_data()

    def show_parameters(self):
        """Show parameters screen"""
        self.content_stack.setCurrentWidget(self.parameters_screen)
        self.set_active_nav_button("parameters")
        self.status_label.setText("Paramètres")

    def show_user_management(self):
        """Show user management screen (admin only)"""
        if not AuthManager.is_admin():
            QMessageBox.warning(
                self,
                "Accès Refusé",
                "Seuls les administrateurs peuvent accéder à cette fonctionnalité."
            )
            return

        self.content_stack.setCurrentWidget(self.user_management_screen)
        self.set_active_nav_button(None)  # No nav button for this screen
        self.status_label.setText("Gestion des Utilisateurs")

    def logout(self):
        """Logout current user"""
        reply = QMessageBox.question(
            self,
            "Déconnexion",
            "Voulez-vous vraiment vous déconnecter?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            AuthManager.logout()
            QMessageBox.information(
                self,
                "Déconnexion",
                "Vous avez été déconnecté avec succès."
            )
            self.close()
            # Reopen login dialog
            from ui.dialogs.login_dialog import LoginDialog
            login_dialog = LoginDialog()
            if login_dialog.exec() == QDialog.DialogCode.Accepted:
                # Create new main window
                new_window = MainWindow()
                new_window.show()

    # Menu actions
    def new_period(self):
        """Create a new payroll period"""
        from database.repositories.payroll_repository import PayrollRepository

        dialog = QDialog(self)
        dialog.setWindowTitle("Nouvelle Période de Paie")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        # Month/Year selection
        month_combo = QComboBox()
        months = [
            ("Janvier", 1), ("Février", 2), ("Mars", 3), ("Avril", 4),
            ("Mai", 5), ("Juin", 6), ("Juillet", 7), ("Août", 8),
            ("Septembre", 9), ("Octobre", 10), ("Novembre", 11), ("Décembre", 12)
        ]
        for name, num in months:
            month_combo.addItem(name, num)
        month_combo.setCurrentIndex(datetime.now().month - 1)
        form_layout.addRow("Mois:", month_combo)

        year_combo = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year - 1, current_year + 2):
            year_combo.addItem(str(year), year)
        year_combo.setCurrentText(str(current_year))
        form_layout.addRow("Année:", year_combo)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            month = month_combo.currentData()
            year = year_combo.currentData()

            # Calculate start and end dates
            import calendar
            start_date = date(year, month, 1)
            last_day = calendar.monthrange(year, month)[1]
            end_date = date(year, month, last_day)
            period_name = f"{month_combo.currentText()} {year}"

            try:
                period_id = PayrollRepository.create_period(start_date, end_date, period_name)
                if period_id:
                    QMessageBox.information(
                        self, "Succès",
                        f"Période '{period_name}' créée avec succès!"
                    )
                    # Refresh payroll screen if visible
                    self.payroll_screen.load_periods()
                else:
                    QMessageBox.warning(self, "Erreur", "Cette période existe déjà.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {str(e)}")

    def import_csv(self):
        """Import data from CSV"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importer un fichier CSV",
            "",
            "Fichiers CSV (*.csv);;Tous les fichiers (*)"
        )

        if file_path:
            try:
                import pandas as pd
                from database.repositories.employee_repository import EmployeeRepository

                df = pd.read_csv(file_path)

                # Show preview and confirmation
                preview = f"Fichier: {os.path.basename(file_path)}\n"
                preview += f"Lignes: {len(df)}\n"
                preview += f"Colonnes: {', '.join(df.columns[:5])}..."

                reply = QMessageBox.question(
                    self, "Confirmer l'import",
                    f"{preview}\n\nVoulez-vous importer ces données?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    # Basic import logic - adjust based on CSV structure
                    imported = 0
                    for _, row in df.iterrows():
                        try:
                            # Attempt to import as employee
                            EmployeeRepository.create_employee(row.to_dict())
                            imported += 1
                        except Exception:
                            continue

                    QMessageBox.information(
                        self, "Import terminé",
                        f"{imported} enregistrements importés avec succès."
                    )
                    self.employees_screen.load_employees()

            except Exception as e:
                QMessageBox.critical(self, "Erreur d'import", f"Erreur: {str(e)}")

    def export_data(self):
        """Export data to Excel"""
        from reports.excel_exporter import ExcelExporter
        from database.repositories.employee_repository import EmployeeRepository
        from database.repositories.payroll_repository import PayrollRepository

        # Ask what to export
        dialog = QDialog(self)
        dialog.setWindowTitle("Exporter les données")
        dialog.setMinimumWidth(350)

        layout = QVBoxLayout(dialog)

        export_combo = QComboBox()
        export_combo.addItem("Liste des employés", "employees")
        export_combo.addItem("Données de paie (période actuelle)", "payroll")
        export_combo.addItem("Toutes les données de paie", "all_payroll")
        layout.addWidget(QLabel("Que voulez-vous exporter?"))
        layout.addWidget(export_combo)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            export_type = export_combo.currentData()

            # Get save location
            default_name = f"PAIERO_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer l'export",
                os.path.join(REPORTS_DIR, default_name),
                "Fichiers Excel (*.xlsx)"
            )

            if file_path:
                try:
                    if export_type == "employees":
                        employees = EmployeeRepository.get_all()
                        # Convert Employee objects to dictionaries
                        employees_data = [
                            {
                                'employee_id': emp.employee_id,
                                'last_name': emp.last_name,
                                'first_name': emp.first_name,
                                'position': emp.position,
                                'category': emp.category,
                                'status_code': emp.status_code,
                                'hire_date': emp.hire_date,
                                'agency_code': emp.agency_code,
                                'department_code': emp.department_code,
                                'inps_number': emp.inps_number,
                                'bank_name': emp.bank_name,
                                'account_number': emp.account_number
                            }
                            for emp in employees
                        ]
                        ExcelExporter.export_employee_list(employees_data, file_path)
                    elif export_type in ["payroll", "all_payroll"]:
                        periods = PayrollRepository.get_all_periods()
                        if periods:
                            records = PayrollRepository.get_records_by_period(periods[0]['period_id'])
                            ExcelExporter.export_payroll_period(records, periods[0], file_path)

                    QMessageBox.information(
                        self, "Export réussi",
                        f"Données exportées vers:\n{file_path}"
                    )

                    # Open the file location
                    if os.path.exists(file_path):
                        os.startfile(os.path.dirname(file_path)) if os.name == 'nt' else os.system(f'open "{os.path.dirname(file_path)}"')

                except Exception as e:
                    QMessageBox.critical(self, "Erreur d'export", f"Erreur: {str(e)}")

    def backup_database(self):
        """Backup database"""
        from database.connection import DatabaseConnection

        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"paiero_backup_{timestamp}.db"

        # Ask for save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder la base de données",
            os.path.join(BACKUP_DIR, default_name),
            "Fichiers de base de données (*.db)"
        )

        if file_path:
            try:
                DatabaseConnection.backup_database(file_path)
                QMessageBox.information(
                    self, "Sauvegarde réussie",
                    f"Base de données sauvegardée vers:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Erreur de sauvegarde",
                    f"Erreur lors de la sauvegarde: {str(e)}"
                )

    def generate_salary_slip(self):
        """Generate salary slip for an employee"""
        # Switch to reports screen and let user generate from there
        self.show_reports()
        QMessageBox.information(
            self,
            "Bulletin de Salaire",
            "Utilisez l'écran Rapports pour générer des bulletins de salaire.\n\n"
            "Vous pouvez sélectionner une période et un employé spécifique."
        )

    def generate_payroll_summary(self):
        """Generate payroll summary report"""
        # Switch to reports screen and let user generate from there
        self.show_reports()
        QMessageBox.information(
            self,
            "Résumé de Paie",
            "Utilisez l'écran Rapports pour générer des résumés de paie.\n\n"
            "Vous pouvez sélectionner une période et le type de rapport souhaité."
        )

    def show_about(self):
        """Show about dialog"""
        dialog = AboutDialog(self)
        dialog.exec()
