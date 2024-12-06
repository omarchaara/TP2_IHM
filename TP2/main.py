import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QStackedWidget
from formulaire_medicament import FormulaireMedicament
from formulaire_fournisseur import FormulaireFournisseur
from formulaire_Client import FormulaireClient
from formulaire_vente import FormulaireVentes  # Import du formulaire des ventes
from formulaire_facture import FormulaireFacture  # Import du formulaire des factures

class Application(QWidget):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre principale
        self.setWindowTitle("Gestion des Médicaments, Commandes, Fournisseurs, Clients, Ventes et Factures")
        self.setGeometry(100, 100, 1500, 600)

        # Couleurs
        self.sidebar_bg_color = "#2E3244"
        self.main_bg_color = "#FFFFFF"
        self.button_bg_color = "#516079"
        self.entry_bg_color = "#C5C6C6"

        # Layout principal pour la fenêtre
        main_layout = QHBoxLayout(self)

        # Barre latérale
        self.sidebar = QFrame(self)
        self.sidebar.setStyleSheet(f"background-color: {self.sidebar_bg_color};")
        self.sidebar.setFixedWidth(200)

        # Layout de la barre latérale
        sidebar_layout = QVBoxLayout(self.sidebar)

        # Boutons de la barre latérale
        self.button_medecaments = QPushButton("Gestion des Médicaments", self)
        self.button_medecaments.setStyleSheet(f"background-color: {self.button_bg_color}; color: #FDFEFE;")
        self.button_medecaments.clicked.connect(self.show_medecaments)
        sidebar_layout.addWidget(self.button_medecaments)

        self.button_fournisseurs = QPushButton("Gestion des Fournisseurs", self)
        self.button_fournisseurs.setStyleSheet(f"background-color: {self.button_bg_color}; color: #FDFEFE;")
        self.button_fournisseurs.clicked.connect(self.show_fournisseurs)
        sidebar_layout.addWidget(self.button_fournisseurs)

        self.button_clients = QPushButton("Gestion des Clients", self)
        self.button_clients.setStyleSheet(f"background-color: {self.button_bg_color}; color: #FDFEFE;")
        self.button_clients.clicked.connect(self.show_clients)
        sidebar_layout.addWidget(self.button_clients)

        self.button_ventes = QPushButton("Gestion des Ventes", self)
        self.button_ventes.setStyleSheet(f"background-color: {self.button_bg_color}; color: #FDFEFE;")
        self.button_ventes.clicked.connect(self.show_ventes)
        sidebar_layout.addWidget(self.button_ventes)

        # Bouton pour la gestion des factures
        self.button_factures = QPushButton("Gestion des Factures", self)
        self.button_factures.setStyleSheet(f"background-color: {self.button_bg_color}; color: #FDFEFE;")
        self.button_factures.clicked.connect(self.show_factures)
        sidebar_layout.addWidget(self.button_factures)

        # Ajout de la barre latérale au layout principal
        main_layout.addWidget(self.sidebar)

        # Stack pour les pages
        self.main_stack = QStackedWidget(self)

        # Création des pages
        self.page_medecaments = FormulaireMedicament(self.main_stack, self.main_bg_color, self.button_bg_color, self.entry_bg_color)
        self.page_fournisseurs = FormulaireFournisseur(self.main_stack, self.main_bg_color, self.button_bg_color)
        self.page_clients = FormulaireClient()
        self.page_ventes = FormulaireVentes()  # Page pour la gestion des ventes
        self.page_factures = FormulaireFacture()  # Page pour la gestion des factures

        # Ajout des pages au stack
        self.main_stack.addWidget(self.page_medecaments)
        self.main_stack.addWidget(self.page_fournisseurs)
        self.main_stack.addWidget(self.page_clients)
        self.main_stack.addWidget(self.page_ventes)
        self.main_stack.addWidget(self.page_factures)

        # Ajout de la zone principale contenant les pages au layout principal
        main_layout.addWidget(self.main_stack)

        # Définir la disposition de la fenêtre
        self.setLayout(main_layout)

        # Page par défaut
        self.show_medecaments()

    def show_medecaments(self):
        self.main_stack.setCurrentWidget(self.page_medecaments)

    def show_fournisseurs(self):
        self.main_stack.setCurrentWidget(self.page_fournisseurs)

    def show_clients(self):
        self.main_stack.setCurrentWidget(self.page_clients)

    def show_ventes(self):
        self.main_stack.setCurrentWidget(self.page_ventes)

    def show_factures(self):
        self.main_stack.setCurrentWidget(self.page_factures)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec_())
