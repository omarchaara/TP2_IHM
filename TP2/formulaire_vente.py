from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt
import sqlite3
import sys


class FormulaireVentes(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ventes par Client")
        self.resize(800, 600)
        
        # Couleurs
        self.bg_color = "#f0f0f0"
        self.button_color = "#516079"

        # Layout principal
        self.layout = QVBoxLayout(self)
        self.setStyleSheet(f"background-color: {self.bg_color};")

        # Titre
        self.title_label = QLabel("Ventes par Client", self)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Champ de recherche par ID Client
        self.search_layout = QVBoxLayout(self)
        self.layout.addLayout(self.search_layout)

        self.search_label = QLabel("ID Client:", self)
        self.search_input = QLineEdit(self)
        self.search_button = QPushButton("Rechercher Ventes", self)
        self.search_button.setStyleSheet(f"background-color: {self.button_color}; color: white;")
        self.search_button.clicked.connect(self.search_ventes)

        self.search_layout.addWidget(self.search_label)
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_button)

        # Bouton pour afficher toutes les ventes
        self.show_all_button = QPushButton("Afficher Toutes les Ventes", self)
        self.show_all_button.setStyleSheet(f"background-color: {self.button_color}; color: white;")
        self.show_all_button.clicked.connect(self.show_all_ventes)
        self.layout.addWidget(self.show_all_button)

        # Tableau des ventes
        self.table = QTableWidget(self)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID Vente", "ID Article", "ID Client", "Nom Complet",
            "Date Vente", "Quantité Vendue", "Prix Total"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

    def search_ventes(self):
        """Rechercher les ventes par ID Client et afficher dans le tableau."""
        id_client = self.search_input.text()
        if not id_client:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un ID client.")
            return

        try:
            connexion = sqlite3.connect("DB_Pharmacy.db")
            curseur = connexion.cursor()

            rows = curseur.execute(
                '''
                SELECT 
                    v.id_Vente,
                    v.Code_Article,
                    v.id_C AS id_client,
                    c.Prenom_C || ' ' || c.Nom_C AS nom_complet,
                    v.Date_Vente,
                    v.Quantite_Vendue,
                    v.Quantite_Vendue * m.Prix_Unitaire AS prix_total
                FROM Vente v
                JOIN Client c ON v.id_C = c.id_C
                JOIN Medicament m ON v.Code_Article = m.Code_Article
                WHERE v.id_C = ?
                ''', (id_client,)
            ).fetchall()

            connexion.close()

            self.update_table(rows)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche des ventes : {e}")

    def show_all_ventes(self):
        """Afficher toutes les ventes de tous les clients."""
        try:
            connexion = sqlite3.connect("DB_Pharmacy.db")
            curseur = connexion.cursor()

            rows = curseur.execute(
                '''
                SELECT 
                    v.id_Vente,
                    v.Code_Article,
                    v.id_C AS id_client,
                    c.Prenom_C || ' ' || c.Nom_C AS nom_complet,
                    v.Date_Vente,
                    v.Quantite_Vendue,
                    v.Quantite_Vendue * m.Prix_Unitaire AS prix_total
                FROM Vente v
                JOIN Client c ON v.id_C = c.id_C
                JOIN Medicament m ON v.Code_Article = m.Code_Article
                '''
            ).fetchall()

            connexion.close()

            self.update_table(rows)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la récupération des ventes : {e}")

    def update_table(self, rows):
        """Mettre à jour le tableau avec les données."""
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, item in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

    def on_mode_change(self):
        """Listener pour le changement de mode de stockage."""
        mode_selectionne = self.mode_stockage.currentText()
        QMessageBox.information(self, "Changement de mode", f"Mode de stockage changé en : {mode_selectionne}")
        if mode_selectionne == "SQLite":
            self.show_all_ventes()
