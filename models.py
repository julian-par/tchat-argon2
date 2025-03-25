# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Stockage du mot de passe haché (salt intégré dans le hash)
    password_hash = db.Column(db.String(200), nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='author', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# models.py (ajouts à la fin du fichier)

from datetime import datetime

class PrivateChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Détermine si le groupe est ouvert pour les demandes ou s'il nécessite une invitation directe
    is_open = db.Column(db.Boolean, default=False)
    # Relations
    memberships = db.relationship('PrivateChatMembership', backref='chat', lazy=True)
    messages = db.relationship('PrivateMessage', backref='chat', lazy=True)

class PrivateChatMembership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('private_chat.id'), nullable=False)
    # Status : "pending", "accepted" ou "rejected"
    status = db.Column(db.String(20), default='pending')
    request_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# models.py (modification de la classe PrivateMessage)

class PrivateMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    chat_id = db.Column(db.Integer, db.ForeignKey('private_chat.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Ajout de la relation pour accéder aux informations de l'utilisateur qui a envoyé le message
    author = db.relationship('User', backref='private_messages')
