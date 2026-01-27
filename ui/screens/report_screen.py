"""
Reports Screen
Generate and export payroll reports
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout,
    QFrame, QMessageBox, QComboBox, QHBoxLayout, QFileDialog
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont, QDesktopServices
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.repositories.payroll_repository import PayrollRepository
from database.repositories.employee_repository import EmployeeRepository
from reports.salary_slip_generator import SalarySlipGenerator
from reports.pdf_reports import PDFReportGenerator
from reports.excel_exporter import ExcelExporter
from database.auth import AuthManager


class ReportScreen(QWidget):
    """Reports generation screen"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Title
        title = QLabel("Rapports et Exports")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)

        # Period selection
        period_layout = QHBoxLayout()

        period_label = QLabel("Période:")
        period_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        period_layout.addWidget(period_label)

        self.period_combo = QComboBox()
        self.period_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 15px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                min-width: 300px;
                background-color: white;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
        """)
        self.load_periods()
        period_layout.addWidget(self.period_combo)
        period_layout.addStretch()

        layout.addLayout(period_layout)

        # Reports grid - 3x2 layout
        reports_grid = QGridLayout()
        reports_grid.setSpacing(20)

        # Row 1 - PDF Reports
        slip_card = self.create_report_card(
            "📄 Bulletins de Paie",
            "PDF - Bulletins individuels par employé",
            "#3498db",
            self.generate_salary_slips
        )
        reports_grid.addWidget(slip_card, 0, 0)

        summary_card = self.create_report_card(
            "📊 Récapitulatif Général",
            "PDF - Rapport complet de la période",
            "#27ae60",
            self.generate_payroll_summary
        )
        reports_grid.addWidget(summary_card, 0, 1)

        cost_card = self.create_report_card(
            "💼 Charges Patronales",
            "PDF - INPS, AMO, Taxes (TL, TFP, ATEJ, CFE)",
            "#e74c3c",
            self.generate_employer_costs
        )
        reports_grid.addWidget(cost_card, 0, 2)

        # Row 2 - Mixed Reports
        tax_card = self.create_report_card(
            "📈 Déclaration Fiscale",
            "PDF - Récapitulatif des impôts",
            "#f39c12",
            self.generate_tax_summary
        )
        reports_grid.addWidget(tax_card, 1, 0)

        bank_card = self.create_report_card(
            "🏦 Virements Bancaires",
            "Excel - Liste pour la banque",
            "#9b59b6",
            self.generate_bank_transfers
        )
        reports_grid.addWidget(bank_card, 1, 1)

        excel_card = self.create_report_card(
            "📑 Export Complet",
            "Excel - Toutes les données",
            "#16a085",
            self.export_to_excel
        )
        reports_grid.addWidget(excel_card, 1, 2)

        layout.addLayout(reports_grid)
        layout.addStretch()

    def load_periods(self):
        """Load payroll periods"""
        try:
            periods = PayrollRepository.get_all_periods()
            self.period_combo.clear()

            if not periods:
                self.period_combo.addItem("Aucune période", None)
            else:
                for period in periods:
                    start = period['period_start_date']
                    end = period['period_end_date']
                    label = f"{start} au {end}"
                    self.period_combo.addItem(label, period['period_id'])
        except:
            pass

    def create_report_card(self, title, description, color, callback):
        """Create a simple report card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 5px solid {color};
                border-radius: 8px;
                padding: 20px;
            }}
            QFrame:hover {{
                background-color: #f8f9fa;
            }}
        """)
        card.setMinimumHeight(140)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 16px;
                font-weight: bold;
            }}
        """)
        card_layout.addWidget(title_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 13px;
            }
        """)
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)

        card_layout.addStretch()

        # Generate button
        btn = QPushButton("Générer")
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(callback)
        card_layout.addWidget(btn)

        return card

    def darken_color(self, hex_color, factor=0.15):
        """Darken a hex color by a factor"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return f'#{r:02x}{g:02x}{b:02x}'

    def generate_salary_slips(self):
        """Generate salary slips"""
        if not AuthManager.has_permission('can_generate_reports'):
            QMessageBox.warning(self, "Permission refusée", "Vous n'avez pas la permission de générer des rapports.")
            return

        period_id = self.period_combo.currentData()
        if not period_id:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une période.")
            return

        try:
            # Get period info
            periods = PayrollRepository.get_all_periods()
            period_data = next((p for p in periods if p['period_id'] == period_id), None)
            if not period_data:
                QMessageBox.warning(self, "Erreur", "Période introuvable.")
                return

            # Get all payroll records for this period
            records = PayrollRepository.get_records_by_period(period_id)
            if not records:
                QMessageBox.warning(self, "Erreur", "Aucun enregistrement trouvé pour cette période.")
                return

            # Ask user to choose output directory
            output_dir = QFileDialog.getExistingDirectory(
                self,
                "Choisir le dossier de destination",
                os.path.expanduser("~/Desktop"),
                QFileDialog.Option.ShowDirsOnly
            )

            if not output_dir:
                return  # User cancelled

            # Create subdirectory for this period
            period_folder = os.path.join(
                output_dir,
                f"bulletins_{period_data['period_start_date'].replace('-', '_')}"
            )
            os.makedirs(period_folder, exist_ok=True)

            # Initialize PDF generator
            generator = SalarySlipGenerator(output_dir=period_folder)

            # Prepare employee data
            employees_data = []
            for record in records:
                employee_data = {
                    'employee_id': record.get('employee_id'),
                    'full_name': record.get('full_name', 'N/A'),
                    'position': record.get('position', 'N/A'),
                    'category': record.get('category', 'N/A'),
                    'department_code': record.get('department_code', 'N/A'),
                    'status_code': record.get('status_code', 'N/A')
                }

                payroll_data = {
                    'base_salary': record.get('base_salary', 0),
                    'ind_transport': record.get('ind_transport', 0),
                    'family_allowance': record.get('family_allowance', 0),
                    'responsibility_allowance': record.get('responsibility_allowance', 0),
                    'risk_premium': record.get('risk_premium', 0),
                    'vehicle_allowance': record.get('vehicle_allowance', 0),
                    'overtime_pay': record.get('overtime_pay', 0),
                    'gross_salary': record.get('gross_salary', 0),
                    'inps_employee': record.get('inps_employee', 0),
                    'amo_employee': record.get('amo_employee', 0),
                    'income_tax': record.get('income_tax', 0),
                    'advances_loans_deduction': record.get('advances_loans_deduction', 0),
                    'net_to_pay': record.get('net_to_pay', 0),
                    'inps_employer': record.get('inps_employer', 0),
                    'amo_employer': record.get('amo_employer', 0),
                    'tl_tax': record.get('tl_tax', 0),
                    'tfp_tax': record.get('tfp_tax', 0),
                    'atej_tax': record.get('atej_tax', 0),
                    'cfe_tax': record.get('cfe_tax', 0),
                }

                employees_data.append((employee_data, payroll_data))

            # Generate PDFs
            period_info = {
                'period_start': period_data['period_start_date'],
                'period_end': period_data['period_end_date']
            }

            generated_files = generator.generate_batch(employees_data, period_info)

            # Show success message
            QMessageBox.information(
                self,
                "Succès",
                f"✅ {len(generated_files)} bulletin(s) de paie généré(s)!\n\n"
                f"Dossier: {period_folder}\n\n"
                "Voulez-vous ouvrir le dossier?"
            )

            # Open folder
            QDesktopServices.openUrl(QUrl.fromLocalFile(period_folder))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération:\n{e}")

    def generate_payroll_summary(self):
        """Generate payroll summary PDF"""
        period_id = self.period_combo.currentData()
        if not period_id:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une période.")
            return

        try:
            # Get period info
            periods = PayrollRepository.get_all_periods()
            period_data = next((p for p in periods if p['period_id'] == period_id), None)
            if not period_data:
                QMessageBox.warning(self, "Erreur", "Période introuvable.")
                return

            # Get records
            records = PayrollRepository.get_records_by_period(period_id)
            if not records:
                QMessageBox.warning(self, "Erreur", "Aucun enregistrement trouvé.")
                return

            # Choose output location
            output_dir = QFileDialog.getExistingDirectory(
                self,
                "Choisir le dossier de destination",
                os.path.expanduser("~/Desktop"),
                QFileDialog.Option.ShowDirsOnly
            )

            if not output_dir:
                return

            # Generate PDF
            filename = f"recapitulatif_paie_{period_data['period_start_date'].replace('-', '_')}.pdf"
            output_path = os.path.join(output_dir, filename)

            PDFReportGenerator.generate_payroll_summary(records, period_data, output_path)

            QMessageBox.information(
                self,
                "Succès",
                f"✅ Récapitulatif généré avec succès!\n\nFichier: {filename}"
            )

            # Open file
            QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{e}")

    def generate_bank_transfers(self):
        """Generate bank transfer list Excel"""
        period_id = self.period_combo.currentData()
        if not period_id:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une période.")
            return

        try:
            # Get period info
            periods = PayrollRepository.get_all_periods()
            period_data = next((p for p in periods if p['period_id'] == period_id), None)
            if not period_data:
                QMessageBox.warning(self, "Erreur", "Période introuvable.")
                return

            # Get records
            records = PayrollRepository.get_records_by_period(period_id)
            if not records:
                QMessageBox.warning(self, "Erreur", "Aucun enregistrement trouvé.")
                return

            # Choose output location
            output_dir = QFileDialog.getExistingDirectory(
                self,
                "Choisir le dossier de destination",
                os.path.expanduser("~/Desktop"),
                QFileDialog.Option.ShowDirsOnly
            )

            if not output_dir:
                return

            # Generate Excel
            filename = f"virements_bancaires_{period_data['period_start_date'].replace('-', '_')}.xlsx"
            output_path = os.path.join(output_dir, filename)

            ExcelExporter.export_bank_transfers(records, period_data, output_path)

            total_amount = sum(r.get('net_to_pay', 0) for r in records)

            QMessageBox.information(
                self,
                "Succès",
                f"✅ Liste des virements générée!\n\n"
                f"Employés: {len(records)}\n"
                f"Montant total: {int(total_amount):,} CFA\n\n"
                f"Fichier: {filename}"
            )

            # Open file
            QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{e}")

    def generate_employer_costs(self):
        """Generate employer costs report PDF"""
        period_id = self.period_combo.currentData()
        if not period_id:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une période.")
            return

        try:
            # Get period info
            periods = PayrollRepository.get_all_periods()
            period_data = next((p for p in periods if p['period_id'] == period_id), None)
            if not period_data:
                QMessageBox.warning(self, "Erreur", "Période introuvable.")
                return

            # Get records
            records = PayrollRepository.get_records_by_period(period_id)
            if not records:
                QMessageBox.warning(self, "Erreur", "Aucun enregistrement trouvé.")
                return

            # Choose output location
            output_dir = QFileDialog.getExistingDirectory(
                self,
                "Choisir le dossier de destination",
                os.path.expanduser("~/Desktop"),
                QFileDialog.Option.ShowDirsOnly
            )

            if not output_dir:
                return

            # Generate PDF
            filename = f"charges_patronales_{period_data['period_start_date'].replace('-', '_')}.pdf"
            output_path = os.path.join(output_dir, filename)

            PDFReportGenerator.generate_employer_costs(records, period_data, output_path)

            # Calculate total
            total_charges = sum(
                r.get('inps_employer', 0) + r.get('amo_employer', 0) +
                r.get('tl_tax', 0) + r.get('tfp_tax', 0) +
                r.get('atej_tax', 0) + r.get('cfe_tax', 0)
                for r in records
            )

            QMessageBox.information(
                self,
                "Succès",
                f"✅ Rapport des charges patronales généré!\n\n"
                f"Montant total: {int(total_charges):,} CFA\n\n"
                f"Fichier: {filename}"
            )

            # Open file
            QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{e}")

    def generate_tax_summary(self):
        """Generate tax summary PDF"""
        period_id = self.period_combo.currentData()
        if not period_id:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une période.")
            return

        try:
            # Get period info
            periods = PayrollRepository.get_all_periods()
            period_data = next((p for p in periods if p['period_id'] == period_id), None)
            if not period_data:
                QMessageBox.warning(self, "Erreur", "Période introuvable.")
                return

            # Get records
            records = PayrollRepository.get_records_by_period(period_id)
            if not records:
                QMessageBox.warning(self, "Erreur", "Aucun enregistrement trouvé.")
                return

            # Choose output location
            output_dir = QFileDialog.getExistingDirectory(
                self,
                "Choisir le dossier de destination",
                os.path.expanduser("~/Desktop"),
                QFileDialog.Option.ShowDirsOnly
            )

            if not output_dir:
                return

            # Generate PDF
            filename = f"recapitulatif_impots_{period_data['period_start_date'].replace('-', '_')}.pdf"
            output_path = os.path.join(output_dir, filename)

            PDFReportGenerator.generate_tax_summary(records, period_data, output_path)

            # Calculate total
            total_tax = sum(r.get('income_tax', 0) for r in records)

            QMessageBox.information(
                self,
                "Succès",
                f"✅ Récapitulatif des impôts généré!\n\n"
                f"Montant total: {int(total_tax):,} CFA\n\n"
                f"Fichier: {filename}"
            )

            # Open file
            QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{e}")

    def export_to_excel(self):
        """Export complete payroll to Excel"""
        if not AuthManager.has_permission('can_export_data'):
            QMessageBox.warning(self, "Permission refusée", "Vous n'avez pas la permission d'exporter des données.")
            return

        period_id = self.period_combo.currentData()
        if not period_id:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une période.")
            return

        try:
            # Get period info
            periods = PayrollRepository.get_all_periods()
            period_data = next((p for p in periods if p['period_id'] == period_id), None)
            if not period_data:
                QMessageBox.warning(self, "Erreur", "Période introuvable.")
                return

            # Get records
            records = PayrollRepository.get_records_by_period(period_id)
            if not records:
                QMessageBox.warning(self, "Erreur", "Aucun enregistrement trouvé.")
                return

            # Choose output location
            output_dir = QFileDialog.getExistingDirectory(
                self,
                "Choisir le dossier de destination",
                os.path.expanduser("~/Desktop"),
                QFileDialog.Option.ShowDirsOnly
            )

            if not output_dir:
                return

            # Generate Excel
            filename = f"paie_complete_{period_data['period_start_date'].replace('-', '_')}.xlsx"
            output_path = os.path.join(output_dir, filename)

            ExcelExporter.export_payroll_period(records, period_data, output_path)

            QMessageBox.information(
                self,
                "Succès",
                f"✅ Export Excel complet généré!\n\n"
                f"Employés: {len(records)}\n"
                f"Fichier: {filename}\n\n"
                f"Toutes les données de la période ont été exportées."
            )

            # Open file
            QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{e}")
