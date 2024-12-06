from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QMessageBox, QFormLayout
)
from PyQt5.QtCore import Qt
import sqlite3
from datetime import datetime

class FormulaireFacture(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Formulaire de Vente")
        self.setGeometry(100, 100, 800, 600)

        self.mode_stockage = "SQLite"

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Section : Détails de la vente
        details_group = QGroupBox("Détails de la Vente")
        details_layout = QFormLayout()

        self.num_inscription_entry = QLineEdit()
        self.search_client_button = QPushButton("Rechercher Client")
        self.search_client_button.clicked.connect(self.search_client)
        details_layout.addRow("Rechercher Client (Numéro d'Inscription) :", self.num_inscription_entry)
        details_layout.addRow("", self.search_client_button)

        self.nom_prenom_entry = QLineEdit()
        self.nom_prenom_entry.setReadOnly(True)
        details_layout.addRow("Nom et Prénom :", self.nom_prenom_entry)

        self.telephone_entry = QLineEdit()
        self.telephone_entry.setReadOnly(True)
        details_layout.addRow("Téléphone :", self.telephone_entry)

        self.med_entry = QLineEdit()
        self.search_med_button = QPushButton("Rechercher Médicament")
        self.search_med_button.clicked.connect(self.search_med)
        details_layout.addRow("Rechercher Médicament (Code Article) :", self.med_entry)
        details_layout.addRow("", self.search_med_button)

        self.med_desc = QLineEdit()
        self.med_desc.setReadOnly(True)
        details_layout.addRow("Description :", self.med_desc)

        self.med_price = QLineEdit()
        self.med_price.setReadOnly(True)
        details_layout.addRow("Prix Unitaire :", self.med_price)

        self.quantity_entry = QLineEdit()
        details_layout.addRow("Quantité :", self.quantity_entry)

        details_group.setLayout(details_layout)
        main_layout.addWidget(details_group)

        # Boutons d'ajout, modification, suppression
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Ajouter Ligne")
        self.add_button.clicked.connect(self.add_line)
        self.modify_button = QPushButton("Modifier Ligne")
        self.modify_button.clicked.connect(self.modify_line)
        self.delete_button = QPushButton("Supprimer Ligne")
        self.delete_button.clicked.connect(self.delete_line)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.modify_button)
        button_layout.addWidget(self.delete_button)
        main_layout.addLayout(button_layout)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Code Article", "Description", "Quantité", "Prix Unitaire", "Prix Total"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.on_item_select)
        main_layout.addWidget(self.table)

        # Total général
        total_layout = QHBoxLayout()
        total_label = QLabel("Total Général :")
        self.total_label = QLabel("0.00")
        self.save_button = QPushButton("Enregistrer")
        self.save_button.clicked.connect(self.save_sale)  # Modification ici
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_label)
        total_layout.addWidget(self.save_button)
        main_layout.addLayout(total_layout)

        self.setLayout(main_layout)

    def update_mode_stockage(self, value):
        self.mode_stockage = value

    def search_client(self):
        client_id = self.num_inscription_entry.text().strip()
        if self.mode_stockage == "SQLite":
            conn = sqlite3.connect("DB_Pharmacy.db")
            cursor = conn.cursor()
            cursor.execute("SELECT Nom_C, prenom_C, telephone_C FROM client WHERE id_C=?", (client_id,))
            client = cursor.fetchone()
            conn.close()
            if client:
                self.nom_prenom_entry.setText(f"{client[0]} {client[1]}")
                self.telephone_entry.setText(client[2])
            else:
                QMessageBox.critical(self, "Erreur", "Client introuvable.")
        

    def search_med(self):
        med_code = self.med_entry.text().strip()
        if self.mode_stockage == "SQLite":
            conn = sqlite3.connect("DB_Pharmacy.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Nom_Commercial || ' ' || Dosage || ' ' || Forme_Pharmaceutique, Prix_Unitaire "
                "FROM Medicament WHERE LOWER(Code_Article) = LOWER(?)", (med_code,)
            )
            med = cursor.fetchone()
            conn.close()
            if med:
                self.med_desc.setText(med[0])
                self.med_price.setText(str(med[1]))
            else:
                QMessageBox.critical(self, "Erreur", "Médicament introuvable.")
  
    
    def add_line(self):
        med_code = self.med_entry.text().strip()
        description = self.med_desc.text().strip()
        try:
            qty = int(self.quantity_entry.text())
            unit_price = float(self.med_price.text())
            total_price = qty * unit_price
        except ValueError:
            QMessageBox.critical(self, "Erreur", "Veuillez entrer une quantité valide.")
            return
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(med_code))
        self.table.setItem(row_position, 1, QTableWidgetItem(description))
        self.table.setItem(row_position, 2, QTableWidgetItem(str(qty)))
        self.table.setItem(row_position, 3, QTableWidgetItem(str(unit_price)))
        self.table.setItem(row_position, 4, QTableWidgetItem(str(total_price)))
        self.update_total()

    def modify_line(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner une ligne à modifier.")
            return
        med_code = self.med_entry.text().strip()
        description = self.med_desc.text().strip()
        try:
            qty = int(self.quantity_entry.text())
            unit_price = float(self.med_price.text())
            total_price = qty * unit_price
        except ValueError:
            QMessageBox.critical(self, "Erreur", "Veuillez entrer une quantité valide.")
            return
        self.table.setItem(selected_row, 0, QTableWidgetItem(med_code))
        self.table.setItem(selected_row, 1, QTableWidgetItem(description))
        self.table.setItem(selected_row, 2, QTableWidgetItem(str(qty)))
        self.table.setItem(selected_row, 3, QTableWidgetItem(str(unit_price)))
        self.table.setItem(selected_row, 4, QTableWidgetItem(str(total_price)))
        self.update_total()

    def delete_line(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner une ligne à supprimer.")
            return
        self.table.removeRow(selected_row)
        self.update_total()

    def update_total(self):
        total = 0
        for row in range(self.table.rowCount()):
            total += float(self.table.item(row, 4).text())
        self.total_label.setText(f"{total:.2f}")

    def on_item_select(self, row, column):
        self.med_entry.setText(self.table.item(row, 0).text())
        self.med_desc.setText(self.table.item(row, 1).text())
        self.quantity_entry.setText(self.table.item(row, 2).text())
        self.med_price.setText(self.table.item(row, 3).text())

    def save_sale(self):  # Modification ici
       client_id = self.num_inscription_entry.text().strip()
    
       # Vérifier si la table est vide
       if self.table.rowCount() == 0:
           QMessageBox.warning(self, "Avertissement", "Veuillez ajouter des lignes avant d'enregistrer.")
           return
    
       now = datetime.now()
       try:
           conn = sqlite3.connect("DB_Pharmacy.db")
           cursor = conn.cursor()
           # Parcourir chaque ligne de la table pour l'enregistrer
           for row in range(self.table.rowCount()):
               med_code = self.table.item(row, 0).text()
               qty = int(self.table.item(row, 2).text())
               sale_date = now.strftime("%Y-%m-%d")
               cursor.execute(
                   "INSERT INTO Vente (Code_Article, Quantite_Vendue, Date_Vente) VALUES (?, ?, ?)",
                   (med_code, qty, sale_date)
               )
           conn.commit()
           conn.close()
        
           # Après enregistrement, vider la table
           self.table.setRowCount(0)  # Supprime toutes les lignes du tableau
           self.update_total()  # Met à jour le total pour le remettre à zéro
           QMessageBox.information(self, "Succès", "Vente enregistrée avec succès.")
        
       except sqlite3.Error as e:
           QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement de la vente : {e}")
