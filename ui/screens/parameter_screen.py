"""
Parameters Screen
System configuration and settings
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QDialog, QScrollArea, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.dialogs.tax_bracket_dialog import TaxBracketDialog
from database.connection import DatabaseConnection
from database.auth import AuthManager


class ParameterScreen(QWidget):
    """Parameters and configuration screen"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Title
        title = QLabel("Configuration du Système")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50;")
        main_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Paramètres de paie et configuration de l'application")
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-bottom: 10px;")
        main_layout.addWidget(subtitle)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(25)

        # === TAX BRACKETS (WORKING) ===
        tax_group = self.create_working_section(
            "📊 Barèmes d'Impôts Progressifs",
            "✅ FONCTIONNEL",
            "#27ae60"
        )
        tax_layout = tax_group.layout()

        # Current values
        values_label = QLabel(
            "• 7 tranches: 0% (0-330K) à 37% (>3.5M CFA/an)\n"
            "• Réductions familiales: 0% à 25% selon statut\n"
            "• Application automatique lors du calcul de paie"
        )
        values_label.setStyleSheet("font-size: 13px; color: #2c3e50; padding: 10px;")
        tax_layout.addWidget(values_label)

        edit_tax_btn = QPushButton("✏️ Modifier les Tranches")
        edit_tax_btn.setStyleSheet("""
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
        edit_tax_btn.clicked.connect(self.manage_tax_brackets)
        tax_layout.addWidget(edit_tax_btn)

        layout.addWidget(tax_group)

        # === SYSTEM RATES (INFO ONLY) ===
        rates_group = self.create_info_section(
            "⚙️ Taux du Système",
            "📋 CONSULTATION"
        )
        rates_layout = rates_group.layout()

        rates_info = QLabel(
            "<b>Cotisations Salariales:</b><br>"
            "• INPS: 3.6%<br>"
            "• AMO: 3.06%<br><br>"
            "<b>Cotisations Patronales:</b><br>"
            "• INPS: 16.4%<br>"
            "• AMO: 3.5%<br><br>"
            "<b>Taxes sur Salaires:</b><br>"
            "• TL: 1% | TFP: 2% | ATEJ: 2% | CFE: 3.5%"
        )
        rates_info.setStyleSheet("font-size: 13px; color: #2c3e50; padding: 10px;")
        rates_info.setWordWrap(True)
        rates_layout.addWidget(rates_info)

        note_label = QLabel("ℹ️ Ces taux sont définis par la législation malienne")
        note_label.setStyleSheet("""
            background-color: #d5f4e6;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            color: #27ae60;
        """)
        rates_layout.addWidget(note_label)

        layout.addWidget(rates_group)

        # === SALARY SCALE (COMING SOON) ===
        salary_group = self.create_future_section(
            "💰 Grille Salariale CCFC",
            "🔜 À VENIR"
        )
        salary_layout = salary_group.layout()

        salary_desc = QLabel(
            "• Actuellement: 18 catégories (cat 1 Ech A à cat 13 Ech E)\n"
            "• Mise à jour future: Modifier les salaires de base\n"
            "• Import/Export Excel pour mise à jour en masse"
        )
        salary_desc.setStyleSheet("font-size: 13px; color: #7f8c8d; padding: 10px;")
        salary_layout.addWidget(salary_desc)

        layout.addWidget(salary_group)

        # === STATUS CODES (COMING SOON) ===
        status_group = self.create_future_section(
            "👥 Codes Statut Familial",
            "🔜 À VENIR"
        )
        status_layout = status_group.layout()

        status_desc = QLabel(
            "• Actuellement: C0-C15 (célibataire) et M0-M20 (marié)\n"
            "• Allocations familiales: 15,000 à 55,000 CFA\n"
            "• Mise à jour future: Modifier les montants"
        )
        status_desc.setStyleSheet("font-size: 13px; color: #7f8c8d; padding: 10px;")
        status_layout.addWidget(status_desc)

        layout.addWidget(status_group)

        layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def create_working_section(self, title, badge, color):
        """Create a working feature section"""
        group = QGroupBox()
        group.setStyleSheet(f"""
            QGroupBox {{
                border: 3px solid {color};
                border-radius: 8px;
                margin-top: 10px;
                padding: 20px;
                background-color: #f0fdf4;
            }}
        """)

        # Main layout for the group
        group_layout = QVBoxLayout(group)

        # Header with badge
        header_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        header_layout.addWidget(title_label)

        badge_label = QLabel(badge)
        badge_label.setStyleSheet(f"""
            background-color: {color};
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        """)
        header_layout.addWidget(badge_label)
        header_layout.addStretch()

        group_layout.addLayout(header_layout)

        return group

    def create_info_section(self, title, badge):
        """Create an info-only section"""
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding: 20px;
                background-color: #ebf5fb;
            }
        """)

        # Main layout for the group
        group_layout = QVBoxLayout(group)

        # Header with badge
        header_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #3498db;")
        header_layout.addWidget(title_label)

        badge_label = QLabel(badge)
        badge_label.setStyleSheet("""
            background-color: #3498db;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        """)
        header_layout.addWidget(badge_label)
        header_layout.addStretch()

        group_layout.addLayout(header_layout)

        return group

    def create_future_section(self, title, badge):
        """Create a future feature section"""
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #95a5a6;
                border-radius: 8px;
                margin-top: 10px;
                padding: 20px;
                background-color: #f8f9fa;
            }
        """)

        # Main layout for the group
        group_layout = QVBoxLayout(group)

        # Header with badge
        header_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #7f8c8d;")
        header_layout.addWidget(title_label)

        badge_label = QLabel(badge)
        badge_label.setStyleSheet("""
            background-color: #95a5a6;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        """)
        header_layout.addWidget(badge_label)
        header_layout.addStretch()

        group_layout.addLayout(header_layout)

        return group

    def manage_tax_brackets(self):
        """Manage tax brackets"""
        if not AuthManager.has_permission('can_modify_parameters'):
            QMessageBox.warning(self, "Permission refusée", "Vous n'avez pas la permission de modifier les paramètres système.")
            return

        dialog = TaxBracketDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(
                self,
                "Succès",
                "Les tranches d'imposition ont été mises à jour.\n\n"
                "Les nouveaux taux seront appliqués lors des prochains calculs de paie."
            )
