import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QDateEdit, QFormLayout, QDialog
from PyQt5.QtCore import QDate
import sqlite3
import re
from datetime import datetime


# Connexion à la base de données SQLite
def get_db_connection():
    """Retourner une connexion à la base de données."""
    return sqlite3.connect("DB_Pharmacy.db")

# Validation du téléphone marocain
def is_valid_phone(telephone):
    phone_regex = r'^(0[5-7]|(\+212))[0-9]{8}$'
    return re.match(phone_regex, telephone) is not None

class FormulaireClient(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestion des Clients")

        # Layout principal
        self.main_layout = QVBoxLayout()

        # Titre
        self.title_label = QLabel("Gestion des Clients")
        self.title_label.setStyleSheet("font: bold 16pt Arial")
        self.main_layout.addWidget(self.title_label)

        # Formulaire
        self.form_layout = QFormLayout()
        self.entry_nom = QLineEdit()
        self.entry_prenom = QLineEdit()
        self.entry_telephone = QLineEdit()
        self.entry_date_naissance = QDateEdit()
        self.entry_date_naissance.setDate(QDate.currentDate())

        self.form_layout.addRow("Nom :", self.entry_nom)
        self.form_layout.addRow("Prénom :", self.entry_prenom)
        self.form_layout.addRow("Téléphone :", self.entry_telephone)
        self.form_layout.addRow("Date de Naissance :", self.entry_date_naissance)

        self.main_layout.addLayout(self.form_layout)

        # Erreurs
        self.error_labels = []
        for _ in range(4):
            error_label = QLabel("")
            error_label.setStyleSheet("color: red; font: 8pt Arial")
            self.error_labels.append(error_label)
            self.main_layout.addWidget(error_label)

        # Boutons
        self.button_layout = QHBoxLayout()
        self.button_ajouter = QPushButton("Ajouter")
        self.button_ajouter.clicked.connect(self.ajouter)
        self.button_layout.addWidget(self.button_ajouter)

        self.button_supprimer = QPushButton("Supprimer")
        self.button_supprimer.clicked.connect(self.supprimer)
        self.button_layout.addWidget(self.button_supprimer)

        self.button_modifier = QPushButton("Modifier")
        self.button_modifier.clicked.connect(self.modifier)
        self.button_layout.addWidget(self.button_modifier)

        self.button_rechercher = QPushButton("Rechercher")
        self.button_rechercher.clicked.connect(self.rechercher)
        self.button_layout.addWidget(self.button_rechercher)

        self.main_layout.addLayout(self.button_layout)

        # Tableau (TableWidget)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Téléphone", "Date de Naissance"])
        self.main_layout.addWidget(self.table)

        # Ajuster la largeur des colonnes
        self.table.setColumnWidth(0, 100)  # Largeur de la colonne "ID"
        self.table.setColumnWidth(1, 200)  # Largeur de la colonne "Nom"
        self.table.setColumnWidth(2, 200)  # Largeur de la colonne "Prénom"
        self.table.setColumnWidth(3, 150)  # Largeur de la colonne "Téléphone"
        self.table.setColumnWidth(4, 200)  # Largeur de la colonne "Date de Naissance"

        # Charger les données
        self.afficher_clients()

        self.setLayout(self.main_layout)

        # Connecter l'événement de sélection d'un item
        self.table.itemSelectionChanged.connect(self.remplir_champs)


    def vider_champs(self):
        self.entry_nom.clear()
        self.entry_prenom.clear()
        self.entry_telephone.clear()
        self.entry_date_naissance.clear()

    def ajouter(self):
        nom = self.entry_nom.text()
        prenom = self.entry_prenom.text()
        telephone = self.entry_telephone.text()
        date_naissance = self.entry_date_naissance.text()

        # Validation des champs
        for label in self.error_labels:
            label.setText("")

        erreurs = False
        if not nom:
            self.error_labels[0].setText("Le nom est requis.")
            erreurs = True
        if not prenom:
            self.error_labels[1].setText("Le prénom est requis.")
            erreurs = True
        if not telephone:
            self.error_labels[2].setText("Le téléphone est requis.")
            erreurs = True
        elif not is_valid_phone(telephone):
            self.error_labels[2].setText("Format de téléphone invalide.")
            erreurs = True
        try:
            datetime.strptime(date_naissance, "%d/%m/%Y")
        except ValueError:
            self.error_labels[3].setText("Format de date invalide (DD/MM/YYYY).")
            erreurs = True

        if erreurs:
            return

        try:
            with get_db_connection() as connexion:
                curseur = connexion.cursor()
                curseur.execute(
                    """
                    INSERT INTO Client (Nom_C, Prenom_C, Telephone_C, Date_Naissance)
                    VALUES (?, ?, ?, ?)
                    """,
                    (nom, prenom, telephone, date_naissance),
                )
                connexion.commit()
                self.afficher_clients()
                self.show_message("Succès", f"Client {nom} {prenom} ajouté avec succès.")
        except sqlite3.Error as e:
            self.show_message("Erreur", f"Erreur lors de l'ajout : {e}")

        self.vider_champs()

    def supprimer(self):
        selected_item = self.table.selectedIndexes()
        if not selected_item:
            self.show_message("Erreur", "Veuillez sélectionner un client à supprimer.")
            return

        client_id = self.table.item(selected_item[0].row(), 0).text()
        confirmation = self.show_confirmation("Confirmer la suppression", f"Supprimer le client ID {client_id} ?")
        if confirmation:
            try:
                with get_db_connection() as connexion:
                    curseur = connexion.cursor()
                    curseur.execute("DELETE FROM Client WHERE id_C = ?", (client_id,))
                    connexion.commit()
                    self.afficher_clients()
                    self.show_message("Succès", "Client supprimé.")
            except sqlite3.Error as e:
                self.show_message("Erreur", f"Erreur : {e}")

        self.vider_champs()

    def remplir_champs(self):
        """Remplit les champs d'entrée avec les données de la ligne sélectionnée."""
        selected_item = self.table.selectedIndexes()
        if not selected_item:
            return

        row = selected_item[0].row()
        self.entry_nom.setText(self.table.item(row, 1).text())
        self.entry_prenom.setText(self.table.item(row, 2).text())
        self.entry_telephone.setText(self.table.item(row, 3).text())
        self.entry_date_naissance.setDate(
            QDate.fromString(self.table.item(row, 4).text(), "dd/MM/yyyy")
        )

    def modifier(self):
        """Met à jour le client dans la base de données."""
        selected_item = self.table.selectedIndexes()
        if not selected_item:
            self.show_message("Erreur", "Veuillez sélectionner un client à modifier.")
            return

        # ID du client
        client_id = self.table.item(selected_item[0].row(), 0).text()

        # Nouvelles données
        nom = self.entry_nom.text()
        prenom = self.entry_prenom.text()
        telephone = self.entry_telephone.text()
        date_naissance = self.entry_date_naissance.text()

        # Validation des champs
        for label in self.error_labels:
            label.setText("")

        erreurs = False
        if not nom:
            self.error_labels[0].setText("Le nom est requis.")
            erreurs = True
        if not prenom:
            self.error_labels[1].setText("Le prénom est requis.")
            erreurs = True
        if not telephone:
            self.error_labels[2].setText("Le téléphone est requis.")
            erreurs = True
        elif not is_valid_phone(telephone):
            self.error_labels[2].setText("Format de téléphone invalide.")
            erreurs = True
        try:
            datetime.strptime(date_naissance, "%d/%m/%Y")
        except ValueError:
            self.error_labels[3].setText("Format de date invalide (DD/MM/YYYY).")
            erreurs = True

        if erreurs:
            return

        # Mettre à jour la base de données
        try:
            with get_db_connection() as connexion:
                curseur = connexion.cursor()
                curseur.execute(
                    """
                    UPDATE Client
                    SET Nom_C = ?, Prenom_C = ?, Telephone_C = ?, Date_Naissance = ?
                    WHERE id_C = ?
                    """,
                    (nom, prenom, telephone, date_naissance, client_id),
                )
                connexion.commit()
                self.afficher_clients()
                self.show_message("Succès", "Client modifié avec succès.")
        except sqlite3.Error as e:
            self.show_message("Erreur", f"Erreur lors de la modification : {e}")

        self.vider_champs()
        
    def rechercher(self):
        nom = self.entry_nom.text().lower()
        prenom = self.entry_prenom.text().lower()

        try:
            with get_db_connection() as connexion:
                curseur = connexion.cursor()
                curseur.execute(
                    """
                    SELECT * FROM Client
                    WHERE Nom_C COLLATE NOCASE LIKE ? AND Prenom_C COLLATE NOCASE LIKE ?
                    """,
                    (f"%{nom}%", f"%{prenom}%"),
                )
                clients = curseur.fetchall()

            if clients:
                self.table.setRowCount(0)
                for client in clients:
                    row_position = self.table.rowCount()
                    self.table.insertRow(row_position)
                    for col, value in enumerate(client):
                        self.table.setItem(row_position, col, QTableWidgetItem(str(value)))
            else:
                self.show_message("Aucun résultat", "Aucun client trouvé avec ces critères.")
        except sqlite3.Error as e:
            self.show_message("Erreur", f"Erreur lors de la recherche : {e}")

    def afficher_clients(self):
        try:
            with get_db_connection() as connexion:
                curseur = connexion.cursor()
                curseur.execute("SELECT * FROM Client")
                clients = curseur.fetchall()

            self.table.setRowCount(0)
            for client in clients:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                for col, value in enumerate(client):
                    self.table.setItem(row_position, col, QTableWidgetItem(str(value)))
        except sqlite3.Error as e:
            self.show_message("Erreur", f"Erreur lors de l'affichage des clients : {e}")

    def show_message(self, title, message):
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def show_confirmation(self, title, message):
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return msg.exec_() == QMessageBox.Yes


