"""
Tax Bracket Editor Dialog
Edit progressive income tax brackets
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDialogButtonBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import DatabaseConnection


class TaxBracketDialog(QDialog):
    """Dialog to edit tax brackets"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifier les Tranches d'Imposition")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.resize(800, 600)

        self.brackets = []
        self.init_ui()
        self.load_brackets()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Header
        header = QLabel("Tranches d'Imposition Progressives")
        header_font = QFont()
        header_font.setPointSize(20)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("color: #2c3e50; padding: 15px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Info banner
        info_label = QLabel(
            "ℹ️  Modifiez les taux d'imposition pour chaque tranche. "
            "Les tranches sont appliquées progressivement au salaire annuel."
        )
        info_label.setStyleSheet("""
            QLabel {
                background-color: #d5f4e6;
                padding: 12px 15px;
                border-radius: 6px;
                font-size: 13px;
                color: #27ae60;
                border: 1px solid #27ae60;
            }
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #bdc3c7;")
        layout.addWidget(separator)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Tranche", "Revenu Min (CFA)", "Revenu Max (CFA)", "Taux (%)"
        ])

        # Table styling
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(50)

        # Enable editing (double-click or click on selected cell)
        from PyQt6.QtWidgets import QAbstractItemView
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.SelectedClicked
        )

        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)

        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(3, 120)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 5px;
                gridline-color: #e0e0e0;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
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
                font-size: 13px;
            }
        """)

        layout.addWidget(self.table)

        # Current system note
        note_label = QLabel(
            "📋 Système actuel: 7 tranches de 0% (0-330K) à 37% (>3.49M CFA/an)"
        )
        note_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 10px 15px;
                border-radius: 5px;
                font-size: 12px;
                color: #7f8c8d;
            }
        """)
        layout.addWidget(note_label)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Save).setText("💾 Enregistrer")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Annuler")

        button_box.accepted.connect(self.save_brackets)
        button_box.rejected.connect(self.reject)

        button_box.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
        """)

        layout.addWidget(button_box)

    def load_brackets(self):
        """Load tax brackets from database"""
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.execute("""
                SELECT bracket_id, min_income, max_income, tax_rate, cumulative_tax
                FROM tax_brackets
                ORDER BY min_income
            """)
            self.brackets = [dict(row) for row in cursor.fetchall()]

            self.display_brackets()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement:\n{e}")

    def display_brackets(self):
        """Display brackets in table"""
        self.table.setRowCount(len(self.brackets))

        for row, bracket in enumerate(self.brackets):
            # Tranche number
            tranche_item = QTableWidgetItem(f"Tranche {row + 1}")
            tranche_item.setFlags(tranche_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            tranche_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tranche_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))

            # Color code by rate
            rate = bracket['tax_rate'] * 100
            if rate == 0:
                tranche_item.setBackground(QColor("#d5f4e6"))
            elif rate <= 12:
                tranche_item.setBackground(QColor("#fef5e7"))
            elif rate <= 26:
                tranche_item.setBackground(QColor("#fadbd8"))
            else:
                tranche_item.setBackground(QColor("#f5b7b1"))

            self.table.setItem(row, 0, tranche_item)

            # Min income
            min_item = QTableWidgetItem(f"{int(bracket['min_income']):,}")
            min_item.setFlags(min_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            min_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 1, min_item)

            # Max income
            max_income = bracket['max_income']
            if max_income and max_income < 99999999:
                max_text = f"{int(max_income):,}"
            else:
                max_text = "∞"
            max_item = QTableWidgetItem(max_text)
            max_item.setFlags(max_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            max_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 2, max_item)

            # Tax rate (editable)
            rate_item = QTableWidgetItem(f"{bracket['tax_rate'] * 100:.1f}")
            rate_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            rate_item.setBackground(QColor("#e8f8f5"))
            rate_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            self.table.setItem(row, 3, rate_item)

    def save_brackets(self):
        """Save modified tax rates"""
        try:
            # Validate and collect new rates
            new_rates = []
            for row in range(self.table.rowCount()):
                rate_item = self.table.item(row, 3)
                try:
                    rate = float(rate_item.text())
                    if rate < 0 or rate > 100:
                        raise ValueError("Taux invalide")
                    new_rates.append(rate / 100)  # Convert to decimal
                except ValueError:
                    QMessageBox.warning(
                        self,
                        "Erreur de Validation",
                        f"Taux invalide à la ligne {row + 1}. Veuillez entrer un nombre entre 0 et 100."
                    )
                    return

            # Confirm changes
            reply = QMessageBox.question(
                self,
                "Confirmer les Modifications",
                "Voulez-vous enregistrer les nouvelles tranches d'imposition?\n\n"
                "Cette modification affectera tous les futurs calculs de paie.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Update database
            conn = DatabaseConnection.get_connection()

            for idx, bracket in enumerate(self.brackets):
                new_rate = new_rates[idx]

                # Recalculate cumulative tax
                if idx == 0:
                    cumulative_tax = 0
                else:
                    prev_bracket = self.brackets[idx - 1]
                    bracket_width = prev_bracket['max_income'] - prev_bracket['min_income']
                    cumulative_tax = self.brackets[idx - 1]['cumulative_tax'] + (
                        bracket_width * prev_bracket['tax_rate']
                    )

                conn.execute("""
                    UPDATE tax_brackets
                    SET tax_rate = ?, cumulative_tax = ?
                    WHERE bracket_id = ?
                """, (new_rate, cumulative_tax, bracket['bracket_id']))

            conn.commit()

            QMessageBox.information(
                self,
                "Succès",
                "✅ Les tranches d'imposition ont été mises à jour avec succès!"
            )

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement:\n{e}")
