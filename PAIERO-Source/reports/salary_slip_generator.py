"""
Salary Slip PDF Generator
Generate professional salary slips in PDF format
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas


class SalarySlipGenerator:
    """Generate PDF salary slips"""

    def __init__(self, output_dir="bulletins_paie"):
        """
        Initialize the generator

        Args:
            output_dir: Directory to save PDF files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_slip(self, employee_data, payroll_data, period_data, company_info=None):
        """
        Generate a single salary slip

        Args:
            employee_data: Employee information dict
            payroll_data: Payroll calculation dict
            period_data: Period information dict
            company_info: Optional company information dict

        Returns:
            str: Path to generated PDF file
        """
        # Default company info
        if company_info is None:
            company_info = {
                'name': 'COMPAGNIE COTONNIÈRE DU MALI',
                'address': 'Bamako, Mali',
                'phone': '+223 XX XX XX XX',
                'email': 'contact@ccfc.ml'
            }

        # Generate filename
        period_month = period_data.get('period_start', datetime.now().strftime('%Y-%m'))
        employee_id = employee_data.get('employee_id', 'XXX')
        filename = f"bulletin_{employee_id}_{period_month.replace('-', '_')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        # Create PDF
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # Build content
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=12
        )

        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=6
        )

        # Company header
        story.append(Paragraph(company_info['name'], title_style))
        story.append(Paragraph(company_info['address'], header_style))
        story.append(Spacer(1, 0.5*cm))

        # Document title
        doc_title = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#27ae60'),
            alignment=TA_CENTER,
            spaceAfter=12
        )
        story.append(Paragraph("BULLETIN DE PAIE", doc_title))
        story.append(Paragraph(f"Période: {period_data.get('period_start', '')} - {period_data.get('period_end', '')}", header_style))
        story.append(Spacer(1, 0.5*cm))

        # Employee information
        emp_data = [
            ['Employé', employee_data.get('full_name', ''), 'N° Matricule', employee_data.get('employee_id', '')],
            ['Position', employee_data.get('position', ''), 'Catégorie', employee_data.get('category', '')],
            ['Département', employee_data.get('department_code', ''), 'Statut Familial', employee_data.get('status_code', '')]
        ]

        emp_table = Table(emp_data, colWidths=[3*cm, 5.5*cm, 3*cm, 5.5*cm])
        emp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(emp_table)
        story.append(Spacer(1, 0.5*cm))

        # Salary components
        components_data = [
            ['DÉSIGNATION', 'MONTANT (CFA)'],
        ]

        # Earnings section
        components_data.append(['GAINS', ''])
        components_data.append(['Salaire de Base', self._format_amount(payroll_data.get('base_salary', 0))])
        components_data.append(['Indemnité de Transport', self._format_amount(payroll_data.get('ind_transport', 0))])
        components_data.append(['Allocation Charge Famille', self._format_amount(payroll_data.get('family_allowance', 0))])

        # Additional allowances
        if payroll_data.get('responsibility_allowance', 0) > 0:
            components_data.append(['Indemnité de Responsabilité', self._format_amount(payroll_data.get('responsibility_allowance', 0))])
        if payroll_data.get('risk_premium', 0) > 0:
            components_data.append(['Prime de Risque', self._format_amount(payroll_data.get('risk_premium', 0))])
        if payroll_data.get('vehicle_allowance', 0) > 0:
            components_data.append(['Indemnité de Monture', self._format_amount(payroll_data.get('vehicle_allowance', 0))])
        if payroll_data.get('overtime_pay', 0) > 0:
            components_data.append(['Heures Supplémentaires', self._format_amount(payroll_data.get('overtime_pay', 0))])

        components_data.append(['SALAIRE BRUT', self._format_amount(payroll_data.get('gross_salary', 0))])

        # Deductions section
        components_data.append(['', ''])
        components_data.append(['RETENUES', ''])
        components_data.append(['INPS Salarié (3.6%)', self._format_amount(payroll_data.get('inps_employee', 0))])
        components_data.append(['AMO Salarié (3.06%)', self._format_amount(payroll_data.get('amo_employee', 0))])
        components_data.append(['Impôt sur le Revenu', self._format_amount(payroll_data.get('income_tax', 0))])

        if payroll_data.get('advances_loans_deduction', 0) > 0:
            components_data.append(['Avances/Prêts', self._format_amount(payroll_data.get('advances_loans_deduction', 0))])

        components_data.append(['TOTAL RETENUES', self._format_amount(
            payroll_data.get('inps_employee', 0) +
            payroll_data.get('amo_employee', 0) +
            payroll_data.get('income_tax', 0) +
            payroll_data.get('advances_loans_deduction', 0)
        )])

        components_data.append(['', ''])
        components_data.append(['NET À PAYER', self._format_amount(payroll_data.get('net_to_pay', 0))])

        # Create table
        comp_table = Table(components_data, colWidths=[12*cm, 5*cm])

        # Style with alternating colors and emphasis on totals
        style_commands = [
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),

            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),

            # Section headers (GAINS, RETENUES)
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.whitesmoke),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ]

        # Find and style GAINS total
        gains_total_row = None
        retenues_header_row = None
        retenues_total_row = None
        net_row = None

        for idx, row in enumerate(components_data):
            if row[0] == 'SALAIRE BRUT':
                gains_total_row = idx
            elif row[0] == 'RETENUES':
                retenues_header_row = idx
            elif row[0] == 'TOTAL RETENUES':
                retenues_total_row = idx
            elif row[0] == 'NET À PAYER':
                net_row = idx

        if gains_total_row:
            style_commands.extend([
                ('BACKGROUND', (0, gains_total_row), (-1, gains_total_row), colors.HexColor('#d5f4e6')),
                ('FONTNAME', (0, gains_total_row), (-1, gains_total_row), 'Helvetica-Bold'),
                ('FONTSIZE', (0, gains_total_row), (-1, gains_total_row), 10),
            ])

        if retenues_header_row:
            style_commands.extend([
                ('BACKGROUND', (0, retenues_header_row), (-1, retenues_header_row), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, retenues_header_row), (-1, retenues_header_row), colors.whitesmoke),
                ('FONTNAME', (0, retenues_header_row), (-1, retenues_header_row), 'Helvetica-Bold'),
            ])

        if retenues_total_row:
            style_commands.extend([
                ('BACKGROUND', (0, retenues_total_row), (-1, retenues_total_row), colors.HexColor('#fadbd8')),
                ('FONTNAME', (0, retenues_total_row), (-1, retenues_total_row), 'Helvetica-Bold'),
            ])

        if net_row:
            style_commands.extend([
                ('BACKGROUND', (0, net_row), (-1, net_row), colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0, net_row), (-1, net_row), colors.whitesmoke),
                ('FONTNAME', (0, net_row), (-1, net_row), 'Helvetica-Bold'),
                ('FONTSIZE', (0, net_row), (-1, net_row), 12),
            ])

        comp_table.setStyle(TableStyle(style_commands))
        story.append(comp_table)
        story.append(Spacer(1, 1*cm))

        # Employer contributions footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_LEFT
        )

        employer_info = f"""
        <b>Charges Patronales:</b><br/>
        INPS Patronal (16.4%): {self._format_amount(payroll_data.get('inps_employer', 0))} CFA |
        AMO Patronal (3.5%): {self._format_amount(payroll_data.get('amo_employer', 0))} CFA<br/>
        TL (1%): {self._format_amount(payroll_data.get('tl_tax', 0))} CFA |
        TFP (2%): {self._format_amount(payroll_data.get('tfp_tax', 0))} CFA |
        ATEJ (2%): {self._format_amount(payroll_data.get('atej_tax', 0))} CFA |
        CFE (3.5%): {self._format_amount(payroll_data.get('cfe_tax', 0))} CFA
        """
        story.append(Paragraph(employer_info, footer_style))
        story.append(Spacer(1, 0.5*cm))

        # Signature section
        sign_data = [
            ['Date d\'édition: ' + datetime.now().strftime('%d/%m/%Y'), 'Signature Employeur'],
        ]
        sign_table = Table(sign_data, colWidths=[8.5*cm, 8.5*cm])
        sign_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
        ]))
        story.append(sign_table)

        # Build PDF
        doc.build(story)

        return filepath

    def generate_batch(self, employees_payroll_data, period_data, company_info=None):
        """
        Generate salary slips for multiple employees

        Args:
            employees_payroll_data: List of (employee_data, payroll_data) tuples
            period_data: Period information dict
            company_info: Optional company information dict

        Returns:
            list: Paths to generated PDF files
        """
        generated_files = []

        for employee_data, payroll_data in employees_payroll_data:
            try:
                filepath = self.generate_slip(employee_data, payroll_data, period_data, company_info)
                generated_files.append(filepath)
            except Exception as e:
                print(f"Error generating slip for {employee_data.get('employee_id')}: {e}")

        return generated_files

    @staticmethod
    def _format_amount(amount):
        """Format amount with thousand separators"""
        if amount is None:
            return "0"
        return f"{int(amount):,}".replace(',', ' ')
