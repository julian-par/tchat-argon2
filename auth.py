# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User
from argon2 import PasswordHasher, exceptions

# Création d'un Blueprint pour regrouper les routes d'authentification
auth_bp = Blueprint('auth', __name__)
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

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and verify_user(user, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = False  # Session non persistante
            flash("Connexion réussie", "success")
            return redirect(url_for('chat'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect", "danger")
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Page de création de compte."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
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

@auth_bp.route('/logout')
def logout():
    """Déconnecte l'utilisateur et efface la session."""
    session.clear()
    flash("Déconnexion réussie", "info")
    return redirect(url_for('auth.login'))

