"""
PDF Report Generators
Generate comprehensive PDF reports
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime


class PDFReportGenerator:
    """Generate various PDF reports"""

    @staticmethod
    def generate_payroll_summary(records, period_data, output_path):
        """Generate comprehensive payroll summary PDF"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        story.append(Paragraph("RÉCAPITULATIF DE LA PAIE", title_style))
        story.append(Paragraph(
            f"Période: {period_data.get('period_start', '')} au {period_data.get('period_end', '')}",
            ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER, spaceAfter=20)
        ))

        # Summary statistics
        employee_count = len(records)
        total_gross = sum(r.get('gross_salary', 0) for r in records)
        total_net = sum(r.get('net_to_pay', 0) for r in records)
        total_inps_employee = sum(r.get('inps_employee', 0) for r in records)
        total_amo_employee = sum(r.get('amo_employee', 0) for r in records)
        total_tax = sum(r.get('income_tax', 0) for r in records)
        total_inps_employer = sum(r.get('inps_employer', 0) for r in records)
        total_amo_employer = sum(r.get('amo_employer', 0) for r in records)
        total_labor_taxes = sum(
            r.get('tl_tax', 0) + r.get('tfp_tax', 0) +
            r.get('atej_tax', 0) + r.get('cfe_tax', 0) for r in records
        )
        total_cost = sum(r.get('total_payroll_cost', 0) for r in records)

        # Summary table
        summary_data = [
            ['STATISTIQUES GÉNÉRALES', ''],
            ['Nombre d\'employés', str(employee_count)],
            ['Salaire brut total', f"{int(total_gross):,} CFA"],
            ['Cotisations salariales', f"{int(total_inps_employee + total_amo_employee):,} CFA"],
            ['Impôts sur salaires', f"{int(total_tax):,} CFA"],
            ['NET À PAYER', f"{int(total_net):,} CFA"],
            ['', ''],
            ['CHARGES PATRONALES', ''],
            ['INPS Patronal (16.4%)', f"{int(total_inps_employer):,} CFA"],
            ['AMO Patronal (3.5%)', f"{int(total_amo_employer):,} CFA"],
            ['Taxes sur salaires', f"{int(total_labor_taxes):,} CFA"],
            ['', ''],
            ['COÛT TOTAL EMPLOYEUR', f"{int(total_cost):,} CFA"],
        ]

        summary_table = Table(summary_data, colWidths=[12*cm, 6*cm])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 5), (-1, 5), colors.whitesmoke),
            ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 5), (-1, 5), 12),
            ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 7), (-1, 7), colors.whitesmoke),
            ('BACKGROUND', (0, 12), (-1, 12), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 12), (-1, 12), colors.whitesmoke),
            ('FONTNAME', (0, 12), (-1, 12), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 12), (-1, 12), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 1*cm))

        # Employee details
        story.append(Paragraph("DÉTAIL PAR EMPLOYÉ", ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10
        )))

        detail_data = [['Employé', 'Brut', 'Retenues', 'Net', 'Coût Total']]
        for record in records:
            retenues = (record.get('inps_employee', 0) +
                       record.get('amo_employee', 0) +
                       record.get('income_tax', 0) +
                       record.get('advances_loans_deduction', 0))
            detail_data.append([
                record.get('full_name', '')[:30],
                f"{int(record.get('gross_salary', 0)):,}",
                f"{int(retenues):,}",
                f"{int(record.get('net_to_pay', 0)):,}",
                f"{int(record.get('total_payroll_cost', 0)):,}"
            ])

        detail_table = Table(detail_data, colWidths=[7*cm, 3*cm, 3*cm, 3*cm, 3*cm])
        detail_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        story.append(detail_table)

        # Footer
        story.append(Spacer(1, 1*cm))
        footer = Paragraph(
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        )
        story.append(footer)

        doc.build(story)
        return output_path

    @staticmethod
    def generate_employer_costs(records, period_data, output_path):
        """Generate employer costs breakdown PDF"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#e74c3c'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        story.append(Paragraph("CHARGES PATRONALES", title_style))
        story.append(Paragraph(
            f"Période: {period_data.get('period_start', '')} au {period_data.get('period_end', '')}",
            ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER, spaceAfter=20)
        ))

        # Calculate totals
        total_inps = sum(r.get('inps_employer', 0) for r in records)
        total_amo = sum(r.get('amo_employer', 0) for r in records)
        total_tl = sum(r.get('tl_tax', 0) for r in records)
        total_tfp = sum(r.get('tfp_tax', 0) for r in records)
        total_atej = sum(r.get('atej_tax', 0) for r in records)
        total_cfe = sum(r.get('cfe_tax', 0) for r in records)
        grand_total = total_inps + total_amo + total_tl + total_tfp + total_atej + total_cfe

        # Summary table
        summary_data = [
            ['DÉSIGNATION', 'TAUX', 'MONTANT (CFA)'],
            ['INPS Patronal', '16.4%', f"{int(total_inps):,}"],
            ['AMO Patronal', '3.5%', f"{int(total_amo):,}"],
            ['Taxe Logement (TL)', '1.0%', f"{int(total_tl):,}"],
            ['Taxe Formation Prof. (TFP)', '2.0%', f"{int(total_tfp):,}"],
            ['ATEJ', '2.0%', f"{int(total_atej):,}"],
            ['CFE', '3.5%', f"{int(total_cfe):,}"],
            ['', '', ''],
            ['TOTAL CHARGES PATRONALES', '', f"{int(grand_total):,}"],
        ]

        summary_table = Table(summary_data, colWidths=[10*cm, 3*cm, 5*cm])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 8), (-1, 8), colors.HexColor('#c0392b')),
            ('TEXTCOLOR', (0, 8), (-1, 8), colors.whitesmoke),
            ('FONTNAME', (0, 8), (-1, 8), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 8), (-1, 8), 13),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 1*cm))

        # Employee breakdown
        story.append(Paragraph("DÉTAIL PAR EMPLOYÉ", ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10
        )))

        detail_data = [['Employé', 'INPS', 'AMO', 'Taxes', 'Total']]
        for record in records:
            taxes = (record.get('tl_tax', 0) + record.get('tfp_tax', 0) +
                    record.get('atej_tax', 0) + record.get('cfe_tax', 0))
            emp_total = record.get('inps_employer', 0) + record.get('amo_employer', 0) + taxes

            detail_data.append([
                record.get('full_name', '')[:35],
                f"{int(record.get('inps_employer', 0)):,}",
                f"{int(record.get('amo_employer', 0)):,}",
                f"{int(taxes):,}",
                f"{int(emp_total):,}"
            ])

        detail_table = Table(detail_data, colWidths=[8*cm, 3*cm, 3*cm, 3*cm, 3*cm])
        detail_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        story.append(detail_table)

        # Footer
        story.append(Spacer(1, 1*cm))
        footer = Paragraph(
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        )
        story.append(footer)

        doc.build(story)
        return output_path

    @staticmethod
    def generate_tax_summary(records, period_data, output_path):
        """Generate tax summary PDF"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#f39c12'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        story.append(Paragraph("RÉCAPITULATIF DES IMPÔTS", title_style))
        story.append(Paragraph(
            f"Période: {period_data.get('period_start', '')} au {period_data.get('period_end', '')}",
            ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER, spaceAfter=20)
        ))

        # Calculate total
        total_tax = sum(r.get('income_tax', 0) for r in records)

        # Summary
        summary_data = [
            ['TOTAL IMPÔTS SUR LES SALAIRES', f"{int(total_tax):,} CFA"],
            ['Nombre d\'employés imposés', str(len([r for r in records if r.get('income_tax', 0) > 0]))],
        ]

        summary_table = Table(summary_data, colWidths=[12*cm, 6*cm])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 13),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8c471')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 1*cm))

        # Detail by employee
        story.append(Paragraph("DÉTAIL PAR EMPLOYÉ", ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10
        )))

        detail_data = [['N° Mle', 'Nom Complet', 'Salaire Brut', 'Base Imposable', 'Impôt']]
        for record in records:
            taxable = record.get('gross_salary', 0) - record.get('family_allowance', 0)
            detail_data.append([
                record.get('employee_id', ''),
                record.get('full_name', '')[:30],
                f"{int(record.get('gross_salary', 0)):,}",
                f"{int(taxable):,}",
                f"{int(record.get('income_tax', 0)):,}"
            ])

        detail_table = Table(detail_data, colWidths=[2.5*cm, 7*cm, 3*cm, 3*cm, 3*cm])
        detail_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        story.append(detail_table)

        # Footer
        story.append(Spacer(1, 1*cm))
        footer = Paragraph(
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        )
        story.append(footer)

        doc.build(story)
        return output_path
