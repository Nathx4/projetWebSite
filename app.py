from flask import Flask, render_template,request, g, url_for, redirect, abort, session
from database import Database
import datetime
import sqlite3
import re
import hashlib
import uuid
import secrets

app = Flask(__name__,static_url_path="",static_folder="static")


db_connection = sqlite3.connect('db/cms.db')


regex = r"[A-Za-z0-9#$%&'*+/=?@]{8,}" 
mdp_existant = re.compile(regex).match


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database


def deconnection():
    db = getattr(g, "_database", None)
    if db is not None:
        db.deconnection()


def match_utilisateur_mdp(utilisateur, mdp):
    user_data = get_db().get_user_by_username(utilisateur)
    if user_data is None:
        
        return False
    
    if isinstance(user_data, dict):
        
        hashed_password_db = user_data.get('mot_de_passe_hash')
        salt = user_data.get('mot_de_passe_salt')
    elif isinstance(user_data, (tuple, list)):
        
        hashed_password_db = user_data[1]  
        salt = user_data[2]  
    else:
        raise ValueError("Structure de données inattendue retournée par get_user_by_username")
    
    hashed_password_input = hashlib.sha512((mdp + salt).encode("utf-8")).hexdigest()

    return hashed_password_input == hashed_password_db



def utilisateur_existe(utilisateur):
    return get_db().utilisateur_existe(utilisateur)


@app.route('/')
def index():
    db = get_db()
    articles = db.get_articles()[:5]  
    return render_template('index.html', articles=articles)

@app.route('/article/<int:id>')
def afficher_article(id):
    
    db = get_db()
    article = db.get_article(id)

    if article is None:
        
        abort(404)

    return render_template('article.html', article=article)

@app.route('/liste_articles')
def liste_articles():
    articles = get_db()
    listeArticles = articles.get_articles()
    return render_template('liste_articles.html', articles=listeArticles) 


@app.route('/articles_trier/<expression>')
def articles_trier(expression):
    articles = get_db()
    listeArticles = articles.get_articles()
    liste_articles = []
    print(listeArticles)
    for article in listeArticles:
      if expression.lower() in article["contenu"].lower() or expression.lower() in article["titre"].lower():
        liste_articles.append(article)
    return render_template('liste_articles.html', articles=liste_articles) 

# Route pour la page d'administration
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Récupération des données du formulaire
        utilisateur = request.form['utilisateur']
        mdp = request.form['mdp']


        # Vérification si tous les champs sont remplis
        if utilisateur == "" or mdp == "":
            message_erreur = "Erreur, tous les champs doivent être remplis"
            return render_template('admin.html', message_erreur=message_erreur), 400

        # Vérification de l'existence de la paire utilisateur-mot de passe dans la base de données
        if not match_utilisateur_mdp(utilisateur, mdp):
            match_erreur = "Nom d'utilisateur ou mot de passe incorrect"
            return render_template('admin.html', match_erreur=match_erreur), 401

        # Redirection vers la page articles.html si l'authentification est réussie
        return redirect(url_for('articles'))
    else:
        # Si la méthode est GET, afficher simplement le formulaire d'authentification
        return render_template('admin.html')

     

@app.route('/articles')
def articles():
    articles = get_db()
    listeArticles = articles.get_articles()
    return render_template('articles.html', articles=listeArticles)

def valider_donnees(donnees, champs_requis):
    erreurs = {}
    for champ in champs_requis:
        if champ not in donnees or not donnees[champ]:
            erreurs[champ] = "Le champ {} est requis.".format(champ)
    return erreurs


def utilisateur_authentifie():
    return 'utilisateur' in session

@app.route('/admin-nouveau', methods=['GET', 'POST'])
def admin_nouveau():
    # Vérifier si l'utilisateur est authentifié
    if not utilisateur_authentifie():
        # Rediriger vers la page de connexion si l'utilisateur n'est pas authentifié
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Récupérer les données du formulaire
        titre = request.form['titre']
        auteur = request.form['auteur']
        date_publication = request.form['date_publication']
        contenu = request.form['contenu']
        
        # Valider les données
        erreurs = valider_donnees(titre, auteur, date_publication, contenu)
        if erreurs:
            # Si des erreurs de validation sont présentes, rendre le template du formulaire avec les erreurs
            return render_template('admin_nouveau.html', erreurs=erreurs, titre=titre, auteur=auteur,
                                   date_publication=date_publication, contenu=contenu)
        
        # Ajouter l'article à la base de données
        db = get_db()
        db.ajouter_article(titre, auteur, date_publication, contenu)
        
        # Rediriger vers la page des articles après avoir ajouté l'article avec succès
        return redirect(url_for('articles'))

    # Si la méthode est GET, simplement afficher le formulaire
    return render_template('admin_nouveau.html')


@app.route('/admin-modif/<int:id>', methods=['GET', 'POST'])
def modifier(id):
    db = get_db()
    article = db.get_article(id)

    if request.method == 'POST':
        nouveau_titre = request.form['nouveau_titre']
        nouveau_contenu = request.form['nouveau_contenu']
        
        # Mettre à jour l'article dans la base de données
        db.mettre_a_jour_article(id, nouveau_titre, nouveau_contenu)
        
        # Rediriger vers la page d'affichage de l'article modifié
        return redirect(url_for('afficher_article', id=id))
    
    return render_template('modifier_article.html', article=article)

    
@app.route('/utilisateurs', methods=['GET', 'POST'])
def gestion_utilisateurs():
    utilisateurs = get_db()
    listeUtilisateurs = utilisateurs.get_all_users()
   
    return render_template('utilisateurs.html', utilisateurs=listeUtilisateurs)


@app.route('/utilisateurs/ajouter', methods=['GET', 'POST'])
def ajouter_utilisateur():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom_utilisateur = request.form['nom_utilisateur']
        mot_de_passe = request.form['mot_de_passe']
        nom = request.form['nom']
        prenom = request.form['prenom']
        courriel = request.form['courriel']
        photo_profil = request.form['photo_profil']

        if (nom == "" or prenom == "" or courriel == "" or
                nom_utilisateur == "" or mot_de_passe == ""):
            message_erreur = "Erreur, un champ obligatoire n'a pas été rempli"
            return render_template('ajouter_utilisateur.html',
                                   nom=nom, prenom=prenom, courriel=courriel,
                                   message_erreur=message_erreur),400
        
        salt = uuid.uuid4().hex
        mot_de_passe_hash = hashlib.sha512(str(mot_de_passe + salt).encode("utf-8")).hexdigest()
        
        db = get_db()  
        db.inserer_utilisateur(nom_utilisateur, mot_de_passe_hash, salt, nom, prenom, courriel, photo_profil)
        
        # Rediriger vers une page de confirmation d'ajout d'utilisateur
        return redirect(url_for('confirmation_ajout_utilisateur', nom_utilisateur=nom_utilisateur)), 302
    
    return render_template('ajouter_utilisateur.html')


@app.route('/confirmation_ajout_utilisateur')
def confirmation_ajout_utilisateur():
    nom_utilisateur = request.args.get('nom_utilisateur')
    return render_template('confirmation_ajout_utilisateur.html',nom_utilisateur=nom_utilisateur), 200



@app.route('/modifier_desactiver/<nom_utilisateur>', methods=['GET', 'POST'])
def modifier_desactiver(nom_utilisateur):
    db = get_db()  # Récupérer la connexion à la base de données
    utilisateur = db.get_user_by_username(nom_utilisateur)
    # Traiter la modification de l'utilisateur avec le nom d'utilisateur spécifié
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nouveau_nom = request.form['nouveau_nom']
        nouveau_prenom = request.form['nouveau_prenom']
        nouveau_courriel = request.form['nouveau_courriel']
        nouvelle_photo_profil = request.form['nouvelle_photo_profil']
        
        # Mettre à jour l'utilisateur dans la base de données 
        db.mettre_a_jour_utilisateur(nom_utilisateur, nouveau_nom, nouveau_prenom, nouveau_courriel, nouvelle_photo_profil)
        
        # Rediriger vers la page de gestion des utilisateurs après la modification
        return redirect(url_for('utilisateurs'))
    else:
        # Afficher le formulaire de modification de l'utilisateur avec les données pré-remplies
        return render_template('modifier_desactiver.html', utilisateur=utilisateur)



@app.route('/desactiver/<nom_utilisateur>', methods=['POST'])
def desactiver_utilisateur(nom_utilisateur):
    # Appeler la méthode pour désactiver l'utilisateur dans la base de données
    db = get_db()
    db.desactiver_utilisateur(nom_utilisateur)
    
    return redirect(url_for('confirmation_desactivation'))


@app.route('/confirmation_desactivation')
def confirmation_desactivation():
    return render_template('confirmation_desactivation.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Clé secrète pour la session
secret_key = secrets.token_hex(16)
app.secret_key = secret_key

if __name__ == "__main__":
    app.run(debug=True)


