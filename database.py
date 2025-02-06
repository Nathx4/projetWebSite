#from flask import Flask
import sqlite3
#import datetime


def _build_article(result_set_item):
    article = {}
    article["id"] = result_set_item[0]
    article["titre"] = result_set_item[1]
    article["auteur"] = result_set_item[2]
    article["date_publication"] = result_set_item[3]
    article["contenu"] = result_set_item[4]
    return article

def _build_utilisateur(result_set_item):
    utilisateur = {}
    utilisateur["nom_utilisateur"] = result_set_item[0]
    utilisateur["mot_de_passe_hash"] = result_set_item[1]
    utilisateur["mot_de_passe_salt"] = result_set_item[2]
    utilisateur["nom"] = result_set_item[3]
    utilisateur["prenom"] = result_set_item[4]
    utilisateur["courriel"] = result_set_item[5]
    utilisateur["photo_profil"] = result_set_item[6]
    utilisateur["est_active"] = result_set_item[7]
    return utilisateur


class Database():
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/cms.db')
        return self.connection

    def deconnection(self):
        if self.connection is not None:
            self.connection.close()

    
    db_connection = sqlite3.connect('db/cms.db')

    def inserer_utilisateur(self, nom_utilisateur, mot_de_passe, salt,  nom, prenom, courriel, photo_profil):
        connection = self.get_connection()
        query = ("INSERT INTO Utilisateurs (nom_utilisateur, mot_de_passe_hash, mot_de_passe_salt,  nom, prenom, courriel, photo_profil) "
                 "VALUES (?, ?, ?, ?, ?, ?, ?)")
        connection.execute(query, (nom_utilisateur, mot_de_passe, salt, nom, prenom, courriel, photo_profil))
        connection.commit()

    def get_user_by_username(self, nom_utilisateur):
        cursor = self.get_connection().cursor()
        query = "SELECT * FROM Utilisateurs WHERE nom_utilisateur = ?"
        cursor.execute(query, (nom_utilisateur,))
        result = cursor.fetchone()
        if result is not None:
            return _build_utilisateur(result)
        else:
            return None

    # Méthodes pour gérer les articles
    def add_article(self, titre, identifiant, auteur, date_publication, contenu):
        connection = self.get_connection()
        query = ("INSERT INTO Articles (titre, identifiant, auteur, date_publication, contenu) "
                 "VALUES (?, ?, ?, ?, ?)")
        connection.execute(query, (titre, identifiant, auteur, date_publication, contenu))
        connection.commit()
    
    def get_articles(self):
        cursor = self.get_connection().cursor()
        query = ("SELECT id, titre, auteur, date_publication, contenu "
                    "FROM Articles")
        cursor.execute(query)
        all_data = cursor.fetchall()
        return [_build_article(item) for item in all_data]
    
    def get_all_users(self):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT nom_utilisateur, mot_de_passe_hash, mot_de_passe_salt, nom, prenom, courriel, photo_profil, est_active FROM Utilisateurs")
        all_data = cursor.fetchall()
        return [_build_utilisateur(item) for item in all_data]

    
    def get_article(self, id):
        cursor = self.get_connection().cursor()
        query = ("SELECT id, titre, auteur, date_publication, contenu "
                "FROM Articles WHERE id = ?")
        cursor.execute(query, (id,))
        item = cursor.fetchone()
        if item is None:
            return item
        else:
            return _build_article(item)
    
    def get_latest_articles(self, limit=5):
        cursor = self.get_connection().cursor()
        query = "SELECT * FROM Articles ORDER BY date_publication DESC LIMIT ?"
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    
    def mettre_a_jour_article(self, id, nouveau_titre, nouveau_contenu):
        cursor = self.db_connection.cursor()
        query = ("UPDATE Articles "
                 "SET titre = ?, contenu = ? "
                 "WHERE id = ?")
        cursor.execute(query, (nouveau_titre, nouveau_contenu, id))
        self.db_connection.commit()

    def mettre_a_jour_utilisateur(self, nom_utilisateur, nouveau_nom, nouveau_prenom, nouveau_courriel, nouvelle_photo_profil):
        cursor = self.db_connection.cursor()
        query = ("UPDATE Utilisateurs "
                "SET nom = ?, prenom = ?, courriel = ?, photo_profil = ? "
                "WHERE nom_utilisateur = ?")
        cursor.execute(query, (nouveau_nom, nouveau_prenom, nouveau_courriel, nouvelle_photo_profil, nom_utilisateur))
        self.db_connection.commit()


    def desactiver_utilisateur(self, nom_utilisateur):
        cursor = self.db_connection.cursor()
        query = "UPDATE Utilisateurs SET est_active = 0 WHERE nom_utilisateur = ?"
        cursor.execute(query, (nom_utilisateur,))
        self.db_connection.commit()

    
    def disconnect(self):
            if self.connection is not None:
                self.connection.close()



