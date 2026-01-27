"""
About Dialog
Application information and purpose
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QFrame,
    QHBoxLayout, QTextBrowser
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class AboutDialog(QDialog):
    """About application dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("À Propos de PAIERO")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Header with logo area
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db,
                    stop:1 #2980b9
                );
                border-radius: 10px;
                padding: 30px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)

        # App name
        app_name = QLabel("PAIERO")
        app_name_font = QFont()
        app_name_font.setPointSize(32)
        app_name_font.setBold(True)
        app_name.setFont(app_name_font)
        app_name.setStyleSheet("color: white;")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(app_name)

        # Subtitle
        subtitle = QLabel("Système de Gestion de Paie pour le Mali")
        subtitle.setStyleSheet("color: white; font-size: 16px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)

        # Version
        version = QLabel("Version 1.0.0 • 2019")
        version.setStyleSheet("color: #ecf0f1; font-size: 12px; margin-top: 5px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(version)

        layout.addWidget(header_frame)

        # Content area with information
        content = QTextBrowser()
        content.setOpenExternalLinks(True)
        content.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                background-color: white;
                font-size: 13px;
                line-height: 1.6;
            }
        """)

        content.setHtml("""
        <h2 style="color: #2c3e50;">🎯 Objectif</h2>
        <p style="color: #34495e;">
        PAIERO est une application de gestion de paie professionnelle conçue spécifiquement pour
        les entreprises maliennes. Elle automatise entièrement le processus de calcul de la paie
        en respectant la législation malienne et la Convention Collective du Mali (CCFC).
        </p>

        <h2 style="color: #2c3e50;">✨ Fonctionnalités Principales</h2>

        <h3 style="color: #3498db;">💼 Gestion des Employés</h3>
        <ul style="color: #34495e;">
            <li>Base de données complète des employés avec toutes les informations requises</li>
            <li>Catégories CCFC (18 catégories: Cat 1 Ech A à Cat 13 Ech E)</li>
            <li>Statuts familiaux (C0-C15 célibataire, M0-M20 marié)</li>
            <li>Suivi de l'ancienneté et des contrats</li>
            <li>Coordonnées bancaires pour virements automatiques</li>
        </ul>

        <h3 style="color: #27ae60;">📊 Calcul de Paie Automatique</h3>
        <ul style="color: #34495e;">
            <li><b>Salaire de base:</b> Selon la grille CCFC avec échelons</li>
            <li><b>Indemnités:</b> Transport (10%), Allocation familiale, Responsabilité, Risque, Monture</li>
            <li><b>Heures supplémentaires:</b> Calcul et majoration automatique</li>
            <li><b>Cotisations salariales:</b> INPS 3.6%, AMO 3.06%</li>
            <li><b>Impôt progressif:</b> 7 tranches de 0% à 37% avec réductions familiales (0% à 25%)</li>
            <li><b>Charges patronales:</b> INPS 16.4%, AMO 3.5%</li>
            <li><b>Taxes sur salaires:</b> TL 1%, TFP 2%, ATEJ 2%, CFE 3.5%</li>
        </ul>

        <h3 style="color: #f39c12;">🏦 Gestion des Prêts et Avances</h3>
        <ul style="color: #34495e;">
            <li>Suivi complet des prêts et avances aux employés</li>
            <li>Génération automatique des échéanciers de remboursement</li>
            <li>Déduction mensuelle automatique lors du calcul de paie</li>
            <li>Historique des paiements et soldes en temps réel</li>
        </ul>

        <h3 style="color: #9b59b6;">📄 Rapports Professionnels</h3>
        <ul style="color: #34495e;">
            <li><b>Bulletins de paie individuels:</b> PDF conformes au modèle légal</li>
            <li><b>Récapitulatif général:</b> Statistiques complètes de la période</li>
            <li><b>Liste de virements bancaires:</b> Export Excel prêt pour la banque</li>
            <li><b>Charges patronales:</b> Détail INPS, AMO et toutes les taxes</li>
            <li><b>Déclaration fiscale:</b> Récapitulatif des impôts à reverser</li>
            <li><b>Export Excel complet:</b> Toutes les données pour analyse</li>
        </ul>

        <h3 style="color: #e74c3c;">⚙️ Configuration et Paramètres</h3>
        <ul style="color: #34495e;">
            <li>Modification des tranches d'impôts progressifs (7 tranches éditables)</li>
            <li>Taux de cotisations conformes à la législation malienne</li>
            <li>Grille salariale CCFC actualisable</li>
            <li>Codes statut familial et allocations personnalisables</li>
        </ul>

        <h2 style="color: #2c3e50;">🇲🇱 Conformité Légale Mali 2019</h2>
        <p style="color: #34495e;">
        L'application respecte intégralement la législation malienne en vigueur:
        </p>
        <ul style="color: #34495e;">
            <li><b>Code du Travail malien</b></li>
            <li><b>Convention Collective du Mali (CCFC)</b></li>
            <li><b>Barème d'imposition progressif:</b> 7 tranches de 0% à 37%</li>
            <li><b>Institut National de Prévoyance Sociale (INPS):</b> 3.6% salarié, 16.4% patronal</li>
            <li><b>Assurance Maladie Obligatoire (AMO):</b> 3.06% salarié, 3.5% patronal</li>
            <li><b>Taxes sur salaires:</b> TL, TFP, ATEJ, CFE</li>
            <li><b>Réductions familiales:</b> Selon le statut et le nombre de personnes à charge</li>
        </ul>

        <h2 style="color: #2c3e50;">💻 Technologies</h2>
        <ul style="color: #34495e;">
            <li><b>Python 3.9+</b> - Langage de programmation robuste</li>
            <li><b>PyQt6</b> - Interface graphique moderne et professionnelle</li>
            <li><b>SQLite</b> - Base de données sécurisée avec intégrité ACID</li>
            <li><b>ReportLab</b> - Génération de PDF professionnels</li>
            <li><b>OpenPyXL</b> - Export Excel avec formatage avancé</li>
        </ul>

        <h2 style="color: #2c3e50;">📞 Support</h2>
        <p style="color: #34495e;">
        Pour toute question ou assistance technique, veuillez contacter le service informatique.
        </p>

        <hr style="border: 1px solid #ecf0f1; margin: 20px 0;">

        <p style="text-align: center; color: #7f8c8d; font-size: 11px;">
        © 2019 PAIERO - Tous droits réservés<br>
        Développé pour la gestion moderne de la paie au Mali
        </p>
        """)

        layout.addWidget(content)

        # Close button
        close_btn = QPushButton("Fermer")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_btn.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)
