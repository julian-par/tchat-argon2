# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from models import db, User, Message
from argon2 import PasswordHasher, exceptions

app = Flask(__name__)
app.config.from_object(Config)

# Initialisation de la base de données et création des tables
db.init_app(app)
with app.app_context():
    db.create_all()

# Instance de PasswordHasher pour gérer le hachage des mots de passe avec Argon2
ph = PasswordHasher()

def create_user(username, password):
    """Crée un nouvel utilisateur avec un pseudo unique et un mot de passe haché."""
    if User.query.filter_by(username=username).first():
        return None  # Le pseudo est déjà utilisé
    hashed_password = ph.hash(password)
    new_user = User(username=username, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def verify_user(user, password):
    """
    Vérifie que le mot de passe fourni correspond au hash stocké.
    Effectue un re-hash si les paramètres de sécurité ont évolué.
    """
    try:
        ph.verify(user.password_hash, password)
        if ph.check_needs_rehash(user.password_hash):
            user.password_hash = ph.hash(password)
            db.session.commit()
        return True
    except exceptions.VerifyMismatchError:
        return False

@app.route('/')
def home():
    """
    Redirige vers la page de chat si l'utilisateur est connecté,
    sinon vers la page de connexion.
    """
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and verify_user(user, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = False  # Session non persistante (ferme à la fermeture du navigateur)
            flash("Connexion réussie", "success")
            return redirect(url_for('chat'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect", "danger")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Page de création de compte."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Vérifier si le pseudo est déjà utilisé
        if User.query.filter_by(username=username).first():
            flash("Ce pseudo est déjà utilisé. Veuillez en choisir un autre.", "warning")
            return render_template('signup.html')
        user = create_user(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = False
            flash("Compte créé avec succès !", "success")
            return redirect(url_for('chat'))
        else:
            flash("Erreur lors de la création du compte.", "danger")
    return render_template('signup.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """Page du chat : affichage et envoi de messages."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        message_content = request.form.get('message')
        if message_content:
            new_message = Message(content=message_content, user_id=session['user_id'])
            db.session.add(new_message)
            db.session.commit()
    messages = Message.query.order_by(Message.timestamp.asc()).all()
    return render_template('chat.html', messages=messages)

@app.route('/lore')
def lore():
    """Page qui raconte l'histoire immersive de Nebula Nexus."""
    return render_template('lore.html')

@app.route('/security')
def security():
    """Page qui détaille les mesures de sécurité mises en place sur Nebula Nexus."""
    return render_template('security.html')

@app.route('/logout')
def logout():
    """Déconnecte l'utilisateur et efface la session."""
    session.clear()
    flash("Déconnexion réussie", "info")
    return redirect(url_for('login'))

@app.route('/argon2_secret')
def argon2_secret():
    """Page secrète détaillant en profondeur le fonctionnement d'Argon2."""
    return render_template('argon2_secret.html')

if __name__ == '__main__':
    app.run(debug=True)
