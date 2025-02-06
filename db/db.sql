DROP TABLE IF EXISTS Utilisateurs;
DROP TABLE IF EXISTS Articles;

-- Création de la table des utilisateurs
CREATE TABLE Utilisateurs (
    nom_utilisateur VARCHAR(50) PRIMARY KEY NOT NULL,
    mot_de_passe_hash TEXT NON NULL,
    mot_de_passe_salt TEXT NON NULL,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    courriel VARCHAR(100) NOT NULL,
    photo_profil TEXT,
    est_active BOOLEAN NOT NULL DEFAULT 1
);


-- Création de la table des articles
CREATE TABLE Articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titre VARCHAR(100) NOT NULL,
    auteur VARCHAR(100) NOT NULL,
    date_publication DATE NOT NULL,
    contenu TEXT NOT NULL,
    FOREIGN KEY (auteur) REFERENCES Utilisateurs(nom_utilisateur)
);

