# app.py
from flask import Flask, render_template, redirect, url_for, session, request, flash
from config import Config
from models import db, Message
from auth import auth_bp  # Import du Blueprint d'authentification

app = Flask(__name__)
app.config.from_object(Config)

# Initialisation de la base de données et création des tables
db.init_app(app)
with app.app_context():
    db.create_all()

# Enregistrement du Blueprint pour les routes d'authentification
app.register_blueprint(auth_bp)

@app.route('/')
def home():
    """
    Redirige vers la page de chat si l'utilisateur est connecté,
    sinon vers la page de connexion.
    """
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('auth.login'))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """Page du chat : affichage et envoi de messages."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
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

@app.route('/argon2_secret')
def argon2_secret():
    """Page secrète détaillant le fonctionnement d'Argon2."""
    return render_template('argon2_secret.html')


if __name__ == '__main__':
    app.run(debug=True)
