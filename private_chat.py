"""
private_chat.py

Ce module gère l'ensemble des fonctionnalités liées aux chats privés :
- Liste des groupes privés auxquels l'utilisateur appartient (statut accepté)
- Affichage et envoi de messages dans un chat privé
- Création d'un groupe privé (avec option d'ouverture pour les demandes)
- Envoi d'une demande pour rejoindre un groupe privé ouvert
- Gestion des demandes d'adhésion par le créateur du groupe

Les fonctions auxiliaires (vérification de session, récupération de l'ID utilisateur, etc.)
sont définies ici pour améliorer la lisibilité et la réutilisabilité du code.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, PrivateChat, PrivateChatMembership, PrivateMessage

# Création du Blueprint pour les fonctionnalités de chat privé
private_bp = Blueprint('private', __name__)

# =======================
# Fonctions Utilitaires
# =======================

def is_logged_in():
    """Vérifie si l'utilisateur est connecté."""
    return 'user_id' in session

def get_user_id():
    """Retourne l'ID de l'utilisateur connecté."""
    return session.get('user_id')

def get_open_groups(user_id):
    """
    Retourne la liste des groupes ouverts (is_open=True) 
    auxquels l'utilisateur n'est pas déjà associé (pas de demande ni membre).
    """
    all_open_groups = PrivateChat.query.filter_by(is_open=True).all()
    # Filtrer pour exclure les groupes avec une demande existante ou déjà membre
    open_groups = [
        group for group in all_open_groups
        if not PrivateChatMembership.query.filter_by(chat_id=group.id, user_id=user_id).first()
    ]
    return open_groups

# =======================
# Routes pour le Chat Privé
# =======================

@private_bp.route('/private_chats')
def private_chats():
    """
    Affiche la liste des groupes privés où l'utilisateur est membre (statut 'accepted'),
    ainsi que la liste des groupes ouverts auxquels il peut envoyer une demande.
    """
    if not is_logged_in():
        return redirect(url_for('auth.login'))
    
    user_id = get_user_id()
    # Récupération des groupes privés où l'utilisateur est accepté
    memberships = PrivateChatMembership.query.filter_by(user_id=user_id, status='accepted').all()
    chats = [membership.chat for membership in memberships]
    
    # Récupération des groupes ouverts auxquels l'utilisateur peut envoyer une demande
    open_groups = get_open_groups(user_id)
    
    return render_template('private_chats.html', chats=chats, open_groups=open_groups)


@private_bp.route('/private_chat/<int:chat_id>', methods=['GET', 'POST'])
def private_chat(chat_id):
    """
    Affiche un chat privé et permet l'envoi de messages.
    Seul un utilisateur avec un statut 'accepted' dans le groupe peut y accéder.
    """
    if not is_logged_in():
        return redirect(url_for('auth.login'))
    
    user_id = get_user_id()
    # Vérifier l'appartenance au groupe avec statut 'accepted'
    membership = PrivateChatMembership.query.filter_by(chat_id=chat_id, user_id=user_id, status='accepted').first()
    if not membership:
        flash("Vous n'êtes pas autorisé à accéder à ce chat.", "danger")
        return redirect(url_for('private.private_chats'))
    
    if request.method == 'POST':
        content = request.form.get('message')
        if content:
            new_message = PrivateMessage(content=content, chat_id=chat_id, user_id=user_id)
            db.session.add(new_message)
            db.session.commit()
    
    # Récupération des messages classés par date croissante
    messages = PrivateMessage.query.filter_by(chat_id=chat_id).order_by(PrivateMessage.timestamp.asc()).all()
    return render_template('private_chat.html', messages=messages, chat_id=chat_id)


@private_bp.route('/create_private_chat', methods=['GET', 'POST'])
def create_private_chat():
    """
    Permet à un utilisateur de créer un nouveau groupe de chat privé.
    Le créateur est ajouté automatiquement en tant que membre accepté.
    """
    if not is_logged_in():
        return redirect(url_for('auth.login'))
    
    user_id = get_user_id()
    if request.method == 'POST':
        chat_name = request.form.get('chat_name')
        # Vérifie si l'option "groupe ouvert" est cochée
        is_open = True if request.form.get('is_open') == 'on' else False
        new_chat = PrivateChat(name=chat_name, creator_id=user_id, is_open=is_open)
        db.session.add(new_chat)
        db.session.commit()
        
        # Ajout automatique du créateur avec le statut 'accepted'
        membership = PrivateChatMembership(user_id=user_id, chat_id=new_chat.id, status='accepted')
        db.session.add(membership)
        db.session.commit()
        flash("Groupe privé créé avec succès.", "success")
        return redirect(url_for('private.private_chats'))
    
    return render_template('create_private_chat.html')


@private_bp.route('/join_private_chat/<int:chat_id>', methods=['GET', 'POST'])
def join_private_chat(chat_id):
    """
    Permet à un utilisateur de demander à rejoindre un groupe privé ouvert.
    Une demande est créée avec le statut 'pending'.
    Si le groupe n'est pas ouvert, la demande n'est pas autorisée.
    """
    if not is_logged_in():
        return redirect(url_for('auth.login'))
    
    user_id = get_user_id()
    group = PrivateChat.query.get(chat_id)
    if not group.is_open:
        flash("Ce groupe n'est pas ouvert aux demandes d'adhésion.", "warning")
        return redirect(url_for('private.private_chats'))
    
    # Vérifier qu'il n'existe pas déjà une demande ou adhésion
    existing = PrivateChatMembership.query.filter_by(chat_id=chat_id, user_id=user_id).first()
    if existing:
        flash("Vous avez déjà envoyé une demande ou êtes déjà membre de ce groupe.", "warning")
        return redirect(url_for('private.private_chats'))
    
    new_membership = PrivateChatMembership(user_id=user_id, chat_id=chat_id, status='pending')
    db.session.add(new_membership)
    db.session.commit()
    flash("Votre demande a été envoyée. En attente de validation.", "info")
    return redirect(url_for('private.private_chats'))


@private_bp.route('/manage_private_chat/<int:chat_id>')
def manage_private_chat(chat_id):
    """
    Permet au créateur d'un groupe privé de gérer les demandes d'adhésion.
    Seul le créateur peut accéder à cette page.
    """
    if not is_logged_in():
        return redirect(url_for('auth.login'))
    
    user_id = get_user_id()
    chat = PrivateChat.query.get(chat_id)
    if chat.creator_id != user_id:
        flash("Vous n'êtes pas autorisé à gérer ce groupe.", "danger")
        return redirect(url_for('private.private_chats'))
    
    # Récupérer toutes les demandes en attente pour ce groupe
    pending_requests = PrivateChatMembership.query.filter_by(chat_id=chat_id, status='pending').all()
    return render_template('manage_private_chat.html', chat=chat, pending_requests=pending_requests)


@private_bp.route('/respond_request/<int:membership_id>/<string:action>')
def respond_request(membership_id, action):
    """
    Permet au créateur d'accepter ou de rejeter une demande d'adhésion.
    Le paramètre 'action' doit être 'accept' ou 'reject'.
    """
    if not is_logged_in():
        return redirect(url_for('auth.login'))
    
    user_id = get_user_id()
    membership = PrivateChatMembership.query.get(membership_id)
    chat = PrivateChat.query.get(membership.chat_id)
    if chat.creator_id != user_id:
        flash("Action non autorisée.", "danger")
        return redirect(url_for('private.private_chats'))
    
    if action == 'accept':
        membership.status = 'accepted'
        flash("Demande acceptée.", "success")
    elif action == 'reject':
        membership.status = 'rejected'
        flash("Demande rejetée.", "warning")
    db.session.commit()
    return redirect(url_for('private.manage_private_chat', chat_id=chat.id))
