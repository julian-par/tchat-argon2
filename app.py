# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from models import db, Message, PrivateChat, PrivateChatMembership, PrivateMessage
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
@app.route('/private_chats')
def private_chats():
    """Liste tous les chats privés où l'utilisateur est membre et accepté."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    # Récupère les groupes dont le status est 'accepted'
    memberships = PrivateChatMembership.query.filter_by(user_id=user_id, status='accepted').all()
    chats = [membership.chat for membership in memberships]
    return render_template('private_chats.html', chats=chats)

@app.route('/private_chat/<int:chat_id>', methods=['GET', 'POST'])
def private_chat(chat_id):
    """Affiche le chat privé et permet l'envoi de messages."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Vérifier que l'utilisateur fait partie du chat et a été accepté
    membership = PrivateChatMembership.query.filter_by(chat_id=chat_id, user_id=session['user_id'], status='accepted').first()
    if not membership:
        flash("Vous n'êtes pas autorisé à accéder à ce chat.", "danger")
        return redirect(url_for('private_chats'))
    if request.method == 'POST':
        content = request.form.get('message')
        if content:
            new_message = PrivateMessage(content=content, chat_id=chat_id, user_id=session['user_id'])
            db.session.add(new_message)
            db.session.commit()
    messages = PrivateMessage.query.filter_by(chat_id=chat_id).order_by(PrivateMessage.timestamp.asc()).all()
    return render_template('private_chat.html', messages=messages, chat_id=chat_id)

@app.route('/create_private_chat', methods=['GET', 'POST'])
def create_private_chat():
    """Permet de créer un nouveau groupe de chat privé."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        chat_name = request.form.get('chat_name')
        # Optionnel : définir si le groupe est ouvert aux demandes
        is_open = True if request.form.get('is_open') == 'on' else False
        new_chat = PrivateChat(name=chat_name, creator_id=session['user_id'], is_open=is_open)
        db.session.add(new_chat)
        db.session.commit()
        # Le créateur est ajouté automatiquement avec un statut "accepted"
        membership = PrivateChatMembership(user_id=session['user_id'], chat_id=new_chat.id, status='accepted')
        db.session.add(membership)
        db.session.commit()
        flash("Groupe privé créé avec succès.", "success")
        return redirect(url_for('private_chats'))
    return render_template('create_private_chat.html')

@app.route('/join_private_chat/<int:chat_id>', methods=['GET', 'POST'])
def join_private_chat(chat_id):
    """
    Permet à un utilisateur de demander à rejoindre un groupe privé ouvert.
    Si le groupe n'est pas ouvert, la demande est envoyée au créateur pour validation.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    existing = PrivateChatMembership.query.filter_by(chat_id=chat_id, user_id=session['user_id']).first()
    if existing:
        flash("Vous avez déjà envoyé une demande ou êtes déjà membre de ce groupe.", "warning")
        return redirect(url_for('private_chats'))
    new_membership = PrivateChatMembership(user_id=session['user_id'], chat_id=chat_id, status='pending')
    db.session.add(new_membership)
    db.session.commit()
    flash("Votre demande a été envoyée.", "info")
    return redirect(url_for('private_chats'))

@app.route('/manage_private_chat/<int:chat_id>')
def manage_private_chat(chat_id):
    """
    Permet au créateur d'un groupe privé de gérer les demandes d'adhésion.
    Seul le créateur peut accéder à cette page.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    chat = PrivateChat.query.get(chat_id)
    if chat.creator_id != session['user_id']:
        flash("Vous n'êtes pas autorisé à gérer ce groupe.", "danger")
        return redirect(url_for('private_chats'))
    # Récupérer toutes les demandes en attente
    pending_requests = PrivateChatMembership.query.filter_by(chat_id=chat_id, status='pending').all()
    return render_template('manage_private_chat.html', chat=chat, pending_requests=pending_requests)

@app.route('/respond_request/<int:membership_id>/<string:action>')
def respond_request(membership_id, action):
    """
    Permet au créateur d'accepter ou de rejeter une demande d'adhésion.
    'action' doit être 'accept' ou 'reject'.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    membership = PrivateChatMembership.query.get(membership_id)
    chat = PrivateChat.query.get(membership.chat_id)
    if chat.creator_id != session['user_id']:
        flash("Action non autorisée.", "danger")
        return redirect(url_for('private_chats'))
    if action == 'accept':
        membership.status = 'accepted'
        flash("Demande acceptée.", "success")
    elif action == 'reject':
        membership.status = 'rejected'
        flash("Demande rejetée.", "warning")
    db.session.commit()
    return redirect(url_for('manage_private_chat', chat_id=membership.chat_id))

if __name__ == '__main__':
    app.run(debug=True)
