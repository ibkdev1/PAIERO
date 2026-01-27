"""
Dashboard Screen - Simple and Clean Version
Main application dashboard with summary statistics
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from database.connection import DatabaseConnection


class DashboardScreen(QWidget):
    """Dashboard screen with summary cards and quick actions"""

    # Signals to communicate with main window
    navigate_to_employees = pyqtSignal()
    navigate_to_payroll = pyqtSignal()
    navigate_to_loans = pyqtSignal()
    navigate_to_reports = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Dashboard header
        header_label = QLabel("Tableau de Bord")
        header_font = QFont()
        header_font.setPointSize(28)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(header_label)

        # Summary statistics - compact horizontal layout
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(30)

        self.employee_card = self.create_compact_stat("👥", "Employés", "0")
        stats_layout.addWidget(self.employee_card)

        stats_layout.addWidget(self.create_separator())

        self.period_card = self.create_compact_stat("📅", "Période", "---")
        stats_layout.addWidget(self.period_card)

        stats_layout.addWidget(self.create_separator())

        self.net_card = self.create_compact_stat("💰", "Net à Payer", "0 CFA")
        stats_layout.addWidget(self.net_card)

        stats_layout.addStretch()

        layout.addWidget(stats_frame)

        # Quick Actions - Simple buttons
        actions_label = QLabel("Actions Rapides")
        actions_font = QFont()
        actions_font.setPointSize(18)
        actions_font.setBold(True)
        actions_label.setFont(actions_font)
        actions_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(actions_label)

        actions_layout = QGridLayout()
        actions_layout.setSpacing(15)

        # Create working action buttons
        emp_btn = self.create_action_button("👥 Gérer les Employés", "#3498db")
        emp_btn.clicked.connect(self.navigate_to_employees.emit)
        actions_layout.addWidget(emp_btn, 0, 0)

        payroll_btn = self.create_action_button("💼 Traiter la Paie", "#27ae60")
        payroll_btn.clicked.connect(self.navigate_to_payroll.emit)
        actions_layout.addWidget(payroll_btn, 0, 1)

        loans_btn = self.create_action_button("🏦 Gérer les Prêts", "#f39c12")
        loans_btn.clicked.connect(self.navigate_to_loans.emit)
        actions_layout.addWidget(loans_btn, 1, 0)

        reports_btn = self.create_action_button("📊 Voir les Rapports", "#9b59b6")
        reports_btn.clicked.connect(self.navigate_to_reports.emit)
        actions_layout.addWidget(reports_btn, 1, 1)

        layout.addLayout(actions_layout)

        # Add stretch to push everything to top
        layout.addStretch()

    def create_compact_stat(self, icon, label, value):
        """Create a compact statistic display"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon_label)

        # Text container
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #7f8c8d; font-size: 11px; font-weight: bold;")
        text_layout.addWidget(label_widget)

        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #2c3e50; font-size: 18px; font-weight: bold;")
        text_layout.addWidget(value_label)

        layout.addWidget(text_container)

        # Store value label for updates
        container.value_label = value_label

        return container

    def create_separator(self):
        """Create a vertical separator"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("background-color: #e0e0e0;")
        separator.setFixedWidth(1)
        return separator

    def create_action_button(self, text, color):
        """Create a simple action button"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 20px;
                font-size: 16px;
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color, 0.15)};
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.3)};
            }}
        """)
        btn.setMinimumHeight(80)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def darken_color(self, hex_color, factor=0.2):
        """Darken a hex color by a factor"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return f'#{r:02x}{g:02x}{b:02x}'

    def load_data(self):
        """Load dashboard data from database"""
        try:
            conn = DatabaseConnection.get_connection()

            # Get employee count
            cursor = conn.execute("SELECT COUNT(*) FROM employees WHERE is_active = 1")
            employee_count = cursor.fetchone()[0]
            self.employee_card.value_label.setText(str(employee_count))

            # Get latest period with payroll data
            cursor = conn.execute("""
                SELECT DISTINCT pp.period_start_date, pp.period_end_date
                FROM payroll_periods pp
                JOIN payroll_records pr ON pp.period_id = pr.period_id
                ORDER BY pp.period_start_date DESC
                LIMIT 1
            """)
            period = cursor.fetchone()
            if period:
                start = period['period_start_date']
                end = period['period_end_date']
                # Format as "2026-02"
                self.period_card.value_label.setText(start[:7])
            else:
                self.period_card.value_label.setText("Aucune")

            # Get payroll statistics - net to pay from most recent period with data
            cursor = conn.execute("""
                SELECT SUM(pr.net_to_pay) as total_net
                FROM payroll_records pr
                WHERE pr.period_id = (
                    SELECT pr2.period_id
                    FROM payroll_records pr2
                    JOIN payroll_periods pp ON pr2.period_id = pp.period_id
                    ORDER BY pp.period_start_date DESC
                    LIMIT 1
                )
            """)
            stats = cursor.fetchone()

            if stats and stats['total_net'] and stats['total_net'] > 0:
                # Format with thousands separators and CFA
                self.net_card.value_label.setText(f"{int(stats['total_net']):,} CFA")
            else:
                self.net_card.value_label.setText("0 CFA")

            # Success - data loaded
            print(f"Dashboard data loaded successfully: {employee_count} employees")

        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            import traceback
            traceback.print_exc()
            # Show error to user
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Erreur de Chargement",
                f"Impossible de charger les données du tableau de bord:\n{str(e)}\n\n"
                "Vérifiez que la base de données est correctement initialisée."
            )

    def refresh_data(self):
        """Refresh dashboard data"""
        self.load_data()
