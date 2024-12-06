import sqlite3

# Connect to the SQLite database
connexion = sqlite3.connect("DB_Pharmacy.db")
curseur = connexion.cursor()

# Activer les clés étrangères
curseur.execute("PRAGMA foreign_keys = ON;")


# Create tables
# Medicament table
curseur.execute('''
CREATE TABLE IF NOT EXISTS Medicament (
    Code_Article TEXT PRIMARY KEY,
    Nom_Generique TEXT,
    Nom_Commercial TEXT,
    Forme_Pharmaceutique TEXT,
    Dosage TEXT,
    Prix_Unitaire REAL,
    Date_Fab DATE,
    Date_Exp DATE,
    Emplacement TEXT,
    Seuil_Approv INTEGER,
    Statut TEXT,
    Avec_Ordonnance BOOLEAN
)
''')

# Fournisseur table
curseur.execute('''
CREATE TABLE IF NOT EXISTS Fournisseur (
    id_F INTEGER PRIMARY KEY,
    Nom_F TEXT,
    Email_F TEXT,
    Telephone_F TEXT,
    Address_F TEXT
)
''')

# Commande table
curseur.execute('''
CREATE TABLE IF NOT EXISTS Commande (
    id_Commande INTEGER PRIMARY KEY AUTOINCREMENT,
    Code_Article INTEGER,
    id_F INTEGER,
    Quantite_Commandee INTEGER,
    Date_Commande DATE,
    FOREIGN KEY (Code_Article) REFERENCES Medicament(Code_Article),
    FOREIGN KEY (id_F) REFERENCES Fournisseur(id_F)
)
''')

# Vente table
curseur.execute('''
CREATE TABLE IF NOT EXISTS Vente (
    id_Vente INTEGER PRIMARY KEY AUTOINCREMENT,
    Code_Article INTEGER,
    Quantite_Vendue INTEGER,
    Date_Vente DATE,
    FOREIGN KEY (Code_Article) REFERENCES Medicament(Code_Article)
)
''')

# Client table
curseur.execute('''
CREATE TABLE IF NOT EXISTS Client (
    id_C INTEGER PRIMARY KEY AUTOINCREMENT,
    Prenom_C TEXT,
    Nom_C TEXT,
    Telephone_C TEXT,
    Date_Naissance DATE
)
''')

# Commit changes and close connection
connexion.commit()
print("Tables created successfully.")
connexion.close()
