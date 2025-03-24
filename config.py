# config.py
import os

class Config:
    # Clé secrète pour les sessions Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key'
    # Utilisation d'une base SQLite pour simplifier l'exemple
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Exemple de durée de session configurable (ici 30 minutes si on souhaite les sessions permanentes)
    PERMANENT_SESSION_LIFETIME = 1800  # 1800 secondes = 30 minutes
