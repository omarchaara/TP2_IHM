from PyQt5.QtWidgets import QApplication, QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox 
import sqlite3
import re

# Connexion à la base de données SQLite
def get_db_connection():
    """Retourner une connexion à la base de données."""
    return sqlite3.connect("DB_Pharmacy.db")

# Fonction pour valider le format de l'email
def is_valid_email(email):
    """Vérifie si l'email est dans un format valide."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zAZ0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Fonction pour valider le format du téléphone marocain
def is_valid_phone(telephone):
    """Vérifie si le téléphone est dans un format valide marocain (commence par 06, 05, ou +212)."""
    phone_regex = r'^(0[5-7]|(\+212))[0-9]{8}$'
    return re.match(phone_regex, telephone) is not None

class FormulaireFournisseur(QWidget):
    def __init__(self, parent=None, bg_color=None, button_color=None):
        super().__init__(parent)
        
        self.bg_color = bg_color
        self.button_color = button_color

        self.setWindowTitle("Gestion des Fournisseurs")
        self.setGeometry(100, 100, 800, 600)

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Titre
        title_label = QLabel("Gestion des Fournisseurs")
        title_label.setStyleSheet(f"font: 16px bold; color: #000000; background-color: {bg_color};")
        main_layout.addWidget(title_label)

        # Cadre pour les champs de saisie
        input_layout = QVBoxLayout()
        self.entry_nom = self.create_input_field(input_layout, "Nom :")
        self.entry_email = self.create_input_field(input_layout, "Email :")
        self.entry_telephone = self.create_input_field(input_layout, "Téléphone :")
        self.entry_adresse = self.create_input_field(input_layout, "Adresse :")

        # Labels d'erreur
        self.error_nom = self.create_error_label(input_layout)
        self.error_email = self.create_error_label(input_layout)
        self.error_telephone = self.create_error_label(input_layout)
        self.error_adresse = self.create_error_label(input_layout)

        main_layout.addLayout(input_layout)

        # Boutons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.create_button("Ajouter", self.ajouter))
        button_layout.addWidget(self.create_button("Supprimer", self.supprimer))
        button_layout.addWidget(self.create_button("Modifier", self.modifier))
        button_layout.addWidget(self.create_button("Rechercher", self.rechercher))

        main_layout.addLayout(button_layout)

        # Tableau (QTableWidget)
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Numéro", "Nom", "Email", "Téléphone", "Adresse"])
        main_layout.addWidget(self.table)

        # Ajuster la largeur des colonnes
        self.table.setColumnWidth(0, 100)  # Largeur de la colonne "Numéro"
        self.table.setColumnWidth(1, 200)  # Largeur de la colonne "Nom"
        self.table.setColumnWidth(2, 250)  # Largeur de la colonne "Email"
        self.table.setColumnWidth(3, 150)  # Largeur de la colonne "Téléphone"
        self.table.setColumnWidth(4, 300)  # Largeur de la colonne "Adresse"

        # Mettre à jour l'affichage des fournisseurs à l'initialisation
        self.afficher_fournisseurs()

        # Ajouter un événement de sélection sur le tableau
        self.table.cellClicked.connect(self.on_item_select)

    def create_input_field(self, layout, label_text):
        label = QLabel(label_text)
        input_field = QLineEdit(self)
        layout.addWidget(label)
        layout.addWidget(input_field)
        return input_field

    def create_error_label(self, layout):
        error_label = QLabel("")
        error_label.setStyleSheet("color: red; font-size: 8px;")
        layout.addWidget(error_label)
        return error_label

    def create_button(self, text, command):
        button = QPushButton(text)
        button.setStyleSheet(f"background-color: {self.button_color}; color: white; font: bold 10px;")
        button.clicked.connect(command)
        return button

    def vider_champs(self):
        """Vider les champs de saisie."""
        self.entry_nom.clear()
        self.entry_email.clear()
        self.entry_telephone.clear()
        self.entry_adresse.clear()

    def ajouter(self):
        nom = self.entry_nom.text()
        email = self.entry_email.text()
        telephone = self.entry_telephone.text()
        adresse = self.entry_adresse.text()

        # Réinitialiser les erreurs
        self.error_nom.setText("")
        self.error_email.setText("")
        self.error_telephone.setText("")
        self.error_adresse.setText("")

        erreurs = False

        if not nom:
            self.error_nom.setText("Le nom est requis.")
            erreurs = True

        if not email:
            self.error_email.setText("L'email est requis.")
            erreurs = True
        elif not is_valid_email(email):
            self.error_email.setText("L'email n'est pas valide.")
            erreurs = True

        if not telephone:
            self.error_telephone.setText("Le téléphone est requis.")
            erreurs = True
        elif not is_valid_phone(telephone):
            self.error_telephone.setText("Le téléphone n'est pas valide. Format marocain requis.")
            erreurs = True

        if not adresse:
            self.error_adresse.setText("L'adresse est requise.")
            erreurs = True

        if erreurs:
            return

        try:
            connexion = get_db_connection()
            curseur = connexion.cursor()

            # Correction : ordre des colonnes
            curseur.execute(''' 
                INSERT INTO Fournisseur (Nom_F, Email_F, Telephone_F, Address_F) 
                VALUES (?, ?, ?, ?) 
            ''', (nom, email, telephone, adresse))  # Assurez-vous que l'ordre correspond à votre base de données

            connexion.commit()
            self.afficher_fournisseurs()
            QMessageBox.information(self, "Succès", f"Fournisseur {nom} ajouté avec succès.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout du fournisseur: {e}")
        finally:
            connexion.close()

        self.vider_champs()

    def supprimer(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.critical(self, "Erreur", "Veuillez sélectionner un fournisseur à supprimer.")
            return

        fournisseur_numero = self.table.item(selected_row, 0).text()

        confirmation = QMessageBox.question(self, "Confirmer la suppression", 
                                            f"Voulez-vous vraiment supprimer le fournisseur avec numéro {fournisseur_numero}?",
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            try:
                connexion = get_db_connection()
                curseur = connexion.cursor()
                curseur.execute("DELETE FROM Fournisseur WHERE id_F=?", (fournisseur_numero,))
                connexion.commit()
                self.afficher_fournisseurs()
                QMessageBox.information(self, "Succès", f"Fournisseur avec numéro {fournisseur_numero} supprimé avec succès.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression du fournisseur: {e}")
            finally:
                connexion.close()

        self.vider_champs()

    def modifier(self):
        nom = self.entry_nom.text()
        email = self.entry_email.text()
        telephone = self.entry_telephone.text()
        adresse = self.entry_adresse.text()

        # Réinitialiser les erreurs
        self.error_nom.setText("")
        self.error_email.setText("")
        self.error_telephone.setText("")
        self.error_adresse.setText("")

        erreurs = False

        if not nom:
            self.error_nom.setText("Le nom est requis.")
            erreurs = True

        if not email:
            self.error_email.setText("L'email est requis.")
            erreurs = True
        elif not is_valid_email(email):
            self.error_email.setText("L'email n'est pas valide.")
            erreurs = True

        if not telephone:
            self.error_telephone.setText("Le téléphone est requis.")
            erreurs = True
        elif not is_valid_phone(telephone):
            self.error_telephone.setText("Le téléphone n'est pas valide. Format marocain requis.")
            erreurs = True

        if not adresse:
            self.error_adresse.setText("L'adresse est requise.")
            erreurs = True

        if erreurs:
            return

        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.critical(self, "Erreur", "Veuillez sélectionner un fournisseur à modifier.")
            return

        fournisseur_numero = self.table.item(selected_row, 0).text()

        try:
            connexion = get_db_connection()
            curseur = connexion.cursor()
            curseur.execute(''' 
                UPDATE Fournisseur 
                SET Nom_F = ?, Email_F = ?, Telephone_F = ?, Address_F = ? 
                WHERE id_F = ? 
            ''', (nom, email, telephone, adresse, fournisseur_numero))  # L'ordre des colonnes est important

            connexion.commit()
            self.afficher_fournisseurs()
            QMessageBox.information(self, "Succès", f"Fournisseur avec numéro {fournisseur_numero} modifié avec succès.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la modification du fournisseur: {e}")
        finally:
            connexion.close()

        self.vider_champs()

    def rechercher(self):
        """Afficher tous les fournisseurs dans le tableau"""
        connexion = get_db_connection()
        curseur = connexion.cursor()

        # Exécuter la requête pour récupérer tous les fournisseurs
        curseur.execute("SELECT * FROM Fournisseur")
        fournisseurs = curseur.fetchall()
        connexion.close()

        self.table.setRowCount(0)  # Réinitialiser le tableau

        for fournisseur in fournisseurs:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for column, item in enumerate(fournisseur):
                self.table.setItem(row_position, column, QTableWidgetItem(str(item)))

    def afficher_fournisseurs(self):
        """Afficher tous les fournisseurs dans le tableau"""
        self.rechercher()

    def on_item_select(self):
        """Lorsqu'un item est sélectionné, charger ses informations dans les champs"""
        selected_row = self.table.currentRow()
        if selected_row != -1:
            self.entry_nom.setText(self.table.item(selected_row, 1).text())
            self.entry_email.setText(self.table.item(selected_row, 2).text())
            self.entry_telephone.setText(self.table.item(selected_row, 3).text())
            self.entry_adresse.setText(self.table.item(selected_row, 4).text())
