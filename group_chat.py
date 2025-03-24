# group_chat.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, ChatGroup, ChatGroupMember, ChatGroupMessage, User
from cryptography.fernet import Fernet

group_bp = Blueprint('group', __name__)

def generate_group_key():
    """Génère une clé symétrique Fernet pour le groupe."""
    return Fernet.generate_key()

def encrypt_message(message, key):
    f = Fernet(key)
    return f.encrypt(message.encode()).decode()

def decrypt_message(token, key):
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()

@group_bp.route('/group/create', methods=['GET', 'POST'])
def create_group():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        group_name = request.form.get('group_name')
        if not group_name:
            flash("Le nom du groupe est obligatoire.", "warning")
            return render_template('group_create.html')
        group_key = generate_group_key()
        # Ici, on stocke la clé en clair pour simplifier (à améliorer en production)
        new_group = ChatGroup(name=group_name, owner_id=session['user_id'], encrypted_group_key=group_key.decode())
        db.session.add(new_group)
        db.session.commit()
        owner_membership = ChatGroupMember(group_id=new_group.id, user_id=session['user_id'], accepted=True)
        db.session.add(owner_membership)
        db.session.commit()
        flash("Groupe créé avec succès.", "success")
        return redirect(url_for('group.manage_group', group_id=new_group.id))
    return render_template('group_create.html')

@group_bp.route('/group/<int:group_id>/invite', methods=['GET', 'POST'])
def invite_to_group(group_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    group = ChatGroup.query.get_or_404(group_id)
    membership = ChatGroupMember.query.filter_by(group_id=group_id, user_id=session['user_id'], accepted=True).first()
    if not membership:
        flash("Vous n'êtes pas autorisé à inviter dans ce groupe.", "danger")
        return redirect(url_for('group.group_chat', group_id=group_id))
    if request.method == 'POST':
        invite_username = request.form.get('username')
        user_to_invite = User.query.filter_by(username=invite_username).first()
        if not user_to_invite:
            flash("Utilisateur introuvable.", "warning")
            return render_template('group_invite.html', group=group)
        if ChatGroupMember.query.filter_by(group_id=group_id, user_id=user_to_invite.id).first():
            flash("Cet utilisateur est déjà invité.", "info")
            return redirect(url_for('group.manage_group', group_id=group_id))
        invitation = ChatGroupMember(group_id=group_id, user_id=user_to_invite.id, accepted=False)
        db.session.add(invitation)
        db.session.commit()
        flash("Invitation envoyée.", "success")
        return redirect(url_for('group.manage_group', group_id=group_id))
    return render_template('group_invite.html', group=group)

@group_bp.route('/group/<int:group_id>')
def group_chat(group_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    group = ChatGroup.query.get_or_404(group_id)
    membership = ChatGroupMember.query.filter_by(group_id=group_id, user_id=session['user_id']).first()
    if not membership or not membership.accepted:
        flash("Vous n'êtes pas membre de ce groupe.", "danger")
        return redirect(url_for('home'))
    group_key = group.encrypted_group_key.encode()
    messages = ChatGroupMessage.query.filter_by(group_id=group_id).order_by(ChatGroupMessage.timestamp.asc()).all()
    decrypted_messages = []
    for msg in messages:
        try:
            decrypted = decrypt_message(msg.encrypted_content, group_key)
        except Exception:
            decrypted = "[Erreur de déchiffrement]"
        decrypted_messages.append({
            'sender_id': msg.sender_id,
            'content': decrypted,
            'timestamp': msg.timestamp
        })
    return render_template('group_chat.html', group=group, messages=decrypted_messages)

@group_bp.route('/group/<int:group_id>/send', methods=['POST'])
def send_group_message(group_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    group = ChatGroup.query.get_or_404(group_id)
    membership = ChatGroupMember.query.filter_by(group_id=group_id, user_id=session['user_id'], accepted=True).first()
    if not membership:
        flash("Vous n'êtes pas autorisé à envoyer des messages dans ce groupe.", "danger")
        return redirect(url_for('group.group_chat', group_id=group_id))
    message_content = request.form.get('message')
    if message_content:
        group_key = group.encrypted_group_key.encode()
        encrypted_content = encrypt_message(message_content, group_key)
        new_message = ChatGroupMessage(group_id=group_id, sender_id=session['user_id'], encrypted_content=encrypted_content)
        db.session.add(new_message)
        db.session.commit()
    return redirect(url_for('group.group_chat', group_id=group_id))

@group_bp.route('/group/<int:group_id>/manage', methods=['GET', 'POST'])
def manage_group(group_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    group = ChatGroup.query.get_or_404(group_id)
    # Seul le propriétaire peut gérer le groupe
    if group.owner_id != session['user_id']:
        flash("Vous n'êtes pas autorisé à gérer ce groupe.", "danger")
        return redirect(url_for('group.group_chat', group_id=group_id))
    # Gestion POST : suppression de membres ou retrait d'invitations
    if request.method == 'POST':
        action = request.form.get('action')
        member_id = request.form.get('member_id')
        member = ChatGroupMember.query.filter_by(group_id=group_id, user_id=member_id).first()
        if action == "remove" and member:
            db.session.delete(member)
            db.session.commit()
            flash("Membre supprimé.", "success")
        return redirect(url_for('group.manage_group', group_id=group_id))
    # Récupération des membres acceptés et des invitations en attente
    members = ChatGroupMember.query.filter_by(group_id=group_id, accepted=True).all()
    pending_invitations = ChatGroupMember.query.filter_by(group_id=group_id, accepted=False).all()
    return render_template("group_management.html", group=group, members=members, pending_invitations=pending_invitations)
