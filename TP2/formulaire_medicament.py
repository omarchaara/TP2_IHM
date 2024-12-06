from PyQt5.QtWidgets import QApplication, QSizePolicy, QSpacerItem, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QDateEdit, QHBoxLayout, QFrame, QScrollArea, QMessageBox
from PyQt5.QtCore import QDate
import sqlite3

class FormulaireMedicament(QWidget):
    def __init__(self, parent=None, bg_color='white', button_color='blue', entry_color='lightgray'):
        super().__init__(parent)

        # Initialisation des couleurs
        self.bg_color = bg_color
        self.button_color = button_color
        self.entry_color = entry_color

        # Connexion à la base de données
        self.connexion = sqlite3.connect("DB_Pharmacy.db")
        self.curseur = self.connexion.cursor()

        # Création de la table si elle n'existe pas
        self.curseur.execute(''' 
            CREATE TABLE IF NOT EXISTS Medicament (
                Code_Article TEXT PRIMARY KEY,
                Nom_Generique TEXT,
                Nom_Commercial TEXT,
                Forme_Pharmaceutique TEXT,
                Dosage TEXT,
                Prix_Unitaire REAL,
                Date_Fab TEXT,
                Date_Exp TEXT,
                Emplacement TEXT,
                Seuil_Approv INTEGER,
                Statut TEXT,
                Avec_Ordonnance INTEGER
            )
        ''')
        self.connexion.commit()

        # Création des widgets
        self.create_widgets()

    def create_widgets(self):
        # Créer le layout principal et l'associer à la fenêtre principale
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Création du formulaire avec les champs
        self.form_frame = QWidget(self)
        self.form_frame.setStyleSheet(f"background-color: {self.bg_color};")
        self.form_layout = QFormLayout(self.form_frame)

        # Ajout des champs du formulaire
        self.fields = {}
        self.add_form_field("Code Article :", "code_article", 0, "entry")
        self.add_form_field("Nom Générique :", "nom_generique", 1, "entry")
        self.add_form_field("Nom Commercial :", "nom_commercial", 2, "entry")
        self.add_form_field("Forme Pharmaceutique :", "forme", 3, "combobox", ["Comprimé", "Solution", "Injection", "Pommade"])
        self.add_form_field("Dosage :", "dosage", 4, "entry")
        self.add_form_field("Prix Unitaire :", "prix_unitaire", 5, "entry")
        self.add_form_field("Date de Fabrication :", "date_fab", 6, "date")
        self.add_form_field("Date d'Expiration :", "date_exp", 7, "date")
        self.add_form_field("Emplacement :", "emplacement", 8, "entry")
        self.add_form_field("Seuil Approvisionnement :", "seuil", 9, "entry")
        self.add_form_field("Statut :", "statut", 10, "combobox", ["Disponible", "Indisponible"])
        self.add_form_field("Avec Ordonnance :", "ordonnance", 11, "combobox", ["Oui", "Non"])
        

        layout.addWidget(self.form_frame)

        # Création des boutons d'action
        self.buttons_frame = QHBoxLayout()
        buttons = [
            ("Ajouter", self.ajouter_medicament),
            ("Modifier", self.modifier_medicament),
            ("Supprimer", self.supprimer_medicament),
            ("Rechercher", self.rechercher_medicament),
            ("Réinitialiser", self.reinitialiser_formulaire),
        ]
        for text, command in buttons:
            button = QPushButton(text)
            button.setStyleSheet(f"background-color: {self.button_color}; color: white;")
            button.clicked.connect(command)
            self.buttons_frame.addWidget(button)

        layout.addLayout(self.buttons_frame)

        # Création du tableau pour afficher les médicaments
        self.table_frame = QScrollArea(self)
        self.table = QTableWidget(self)
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "Code_Article", "Nom_Generique", "Nom_Commercial", "Forme_Pharmaceutique", "Dosage",
            "Prix_Unitaire", "Date_Fab", "Date_Exp", "Emplacement", "Seuil_Approv", "Statut", "Avec_Ordonnance"
        ])
        
        
        self.table.cellClicked.connect(self.selectionner_ligne)
        layout.addWidget(self.table)

        self.load_table()

    def add_form_field(self, label, field, row, widget_type, options=None):
        label_widget = QLineEdit(label)
        label_widget.setStyleSheet(f"background-color: {self.bg_color}; color: black;")
        self.form_layout.setWidget(row, QFormLayout.LabelRole, label_widget)

        if widget_type == "entry":
            widget = QLineEdit()
            widget.setStyleSheet(f"background-color: {self.entry_color}; border: none;")

        elif widget_type == "combobox":
            widget = QComboBox()
            widget.addItems(options or [])
        elif widget_type == "date":
            widget = QDateEdit()
            widget.setDate(QDate.currentDate())
        else:
            return

        self.form_layout.setWidget(row, QFormLayout.FieldRole, widget)
        self.fields[field] = widget

    def load_table(self):
        """Charge les données de la base dans le tableau."""
        self.table.setRowCount(0)
        try:
            self.curseur.execute("SELECT * FROM Medicament")
            rows = self.curseur.fetchall()
            for row in rows:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                for column, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row_position, column, item)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des données : {e}")

    def selectionner_ligne(self, row):
        """Affiche les données de la ligne sélectionnée dans le formulaire."""
        for column, field in enumerate(self.fields.keys()):
            value = self.table.item(row, column).text()
            widget = self.fields[field]
            if isinstance(widget, QComboBox):
                index = widget.findText(value)
                widget.setCurrentIndex(index)
            elif isinstance(widget, QDateEdit):
                widget.setDate(QDate.fromString(value, "yyyy-MM-dd"))
            else:
                widget.setText(value)

    def ajouter_medicament(self):
        try:
            data = {key: field.currentText() if isinstance(field, QComboBox) else field.text() for key, field in self.fields.items()}
            data["ordonnance"] = 1 if data["ordonnance"] == "Oui" else 0

            if not data["code_article"]:
                QMessageBox.critical(self, "Erreur", "Le champ Code Article est obligatoire.")
                return

            self.curseur.execute(''' 
                INSERT INTO Medicament (Code_Article, Nom_Generique, Nom_Commercial, Forme_Pharmaceutique, Dosage,
                Prix_Unitaire, Date_Fab, Date_Exp, Emplacement, Seuil_Approv, Statut, Avec_Ordonnance)
                VALUES (:code_article, :nom_generique, :nom_commercial, :forme, :dosage, :prix_unitaire, :date_fab,
                :date_exp, :emplacement, :seuil, :statut, :ordonnance)
            ''', data)
            self.connexion.commit()
            self.load_table()
            QMessageBox.information(self, "Succès", "Médicament ajouté avec succès.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout : {e}")

    def modifier_medicament(self):
        selected = self.table.selectedIndexes()
        if not selected:
            QMessageBox.critical(self, "Erreur", "Veuillez sélectionner un médicament à modifier.")
            return

        try:
            code_article = self.table.item(selected[0].row(), 0).text()
            data = {key: field.currentText() if isinstance(field, QComboBox) else field.text() for key, field in self.fields.items()}
            data["ordonnance"] = 1 if data["ordonnance"] == "Oui" else 0

            self.curseur.execute(''' 
                UPDATE Medicament SET Nom_Generique = :nom_generique, Nom_Commercial = :nom_commercial, 
                Forme_Pharmaceutique = :forme, Dosage = :dosage, Prix_Unitaire = :prix_unitaire, 
                Date_Fab = :date_fab, Date_Exp = :date_exp, Emplacement = :emplacement, 
                Seuil_Approv = :seuil, Statut = :statut, Avec_Ordonnance = :ordonnance 
                WHERE Code_Article = :code_article
            ''', {**data, "code_article": code_article})
            self.connexion.commit()
            self.load_table()
            QMessageBox.information(self, "Succès", "Médicament modifié avec succès.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la modification : {e}")

    def supprimer_medicament(self):
        selected = self.table.selectedIndexes()
        if not selected:
            QMessageBox.critical(self, "Erreur", "Veuillez sélectionner un médicament à supprimer.")
            return

        try:
            code_article = self.table.item(selected[0].row(), 0).text()
            self.curseur.execute('DELETE FROM Medicament WHERE Code_Article = ?', (code_article,))
            self.connexion.commit()
            self.load_table()
            QMessageBox.information(self, "Succès", "Médicament supprimé avec succès.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression : {e}")

    def rechercher_medicament(self):
        code_article = self.fields["code_article"].text()
        if not code_article:
            QMessageBox.critical(self.main_frame, "Erreur", "Veuillez entrer un Code Article pour la recherche.")
            return

        try:
            self.curseur.execute('SELECT * FROM Medicament WHERE Code_Article = ?', (code_article,))
            row = self.curseur.fetchone()
            if row:
                for column, key in enumerate(self.fields.keys()):
                    widget = self.fields[key]
                    value = str(row[column])
                    if isinstance(widget, QComboBox):
                        index = widget.findText(value)
                        widget.setCurrentIndex(index)
                    elif isinstance(widget, QDateEdit):
                        widget.setDate(QDate.fromString(value, "yyyy-MM-dd"))
                    else:
                        widget.setText(value)
            else:
                QMessageBox.warning(self.main_frame, "Résultat", "Aucun médicament trouvé.")
        except sqlite3.Error as e:
            QMessageBox.critical(self.main_frame, "Erreur", f"Erreur lors de la recherche : {e}")

    def reinitialiser_formulaire(self):
        for field in self.fields.values():
            if isinstance(field, QComboBox):
                field.setCurrentIndex(0)
            elif isinstance(field, QDateEdit):
                field.setDate(QDate.currentDate())
            else:
                field.clear()



