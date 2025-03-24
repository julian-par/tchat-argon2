# Tchat-Argon2  
Un système de messagerie sécurisé avec authentification renforcée  

## Présentation  
Tchat-Argon2 est une plateforme de discussion en ligne développée avec **Flask** et **SQLite**, mettant l'accent sur la sécurité et la confidentialité des échanges. Le projet repose sur les meilleures pratiques en matière d'authentification, avec une gestion avancée des mots de passe et un chiffrement des conversations.  

## Objectifs du projet  
- Fournir un système d'authentification sécurisé avec **Argon2** pour le hachage des mots de passe.  
- Mettre en place un **re-hash automatique** des mots de passe lors de la connexion pour garantir leur sécurité continue.  
- Implémenter un **système de sessions basé sur des cookies configurables** avec expiration automatique lors de la fermeture des onglets.  
- Assurer la confidentialité des échanges avec un **chiffrement des messages**.  
- Proposer une expérience utilisateur moderne avec une interface soignée et ergonomique.  
- Développer un univers unique autour du site, avec une **page de présentation immersive** et une section détaillée sur la sécurité.  

## Fonctionnalités principales  

### Authentification et sécurité  
- Enregistrement et connexion sécurisés avec **Argon2**.  
- Vérification de la disponibilité des pseudos lors de l'inscription.  
- Système de **re-hash automatique** des mots de passe obsolètes.  
- Gestion des sessions avec expiration configurable.  
- Déconnexion automatique lors de la fermeture des onglets.  

### Messagerie  
- Interface de chat en temps réel avec WebSockets.  
- Chiffrement des messages pour garantir la confidentialité des échanges.  
- Interface claire et moderne facilitant la discussion.  

### Expérience utilisateur  
- Design moderne et responsive avec une organisation CSS optimisée.  
- Page détaillant l'histoire du site et son univers.  
- Section dédiée à la **sécurité** expliquant les mesures mises en place pour protéger les utilisateurs.  
- Une page "secrète" accessible via un élément interactif (Argon2) détaillant de manière approfondie les aspects techniques du hachage et du chiffrement.  

## Architecture du projet  

Le projet est structuré en plusieurs fichiers pour assurer une organisation claire et une bonne maintenabilité :  

```plaintext
/tchat-argon2
│── /static
│   ├── /css
│   │   ├── main.css
│   │   ├── auth.css
│   │   ├── chat.css
│   │   ├── security.css
│── /templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── chat.html
│   ├── security.html
│   ├── secret.html
│── /routes
│   ├── auth.py
│   ├── chat.py
│   ├── security.py
│── app.py
│── config.py
│── models.py
│── requirements.txt
│── README.md
```

## Installation et exécution  

### Prérequis  
- Python 3.9+  
- Pip et virtualenv  

### Installation  

1. **Cloner le projet**  
   ```sh
   git clone https://github.com/julian-par/tchat-argon2.git
   cd tchat-argon2
   ```

2. **Créer un environnement virtuel et installer les dépendances**  
   ```sh
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Lancer l'application**  
   ```sh
   python app.py
   ```

4. **Accéder à l'interface**  
   Ouvrir un navigateur et aller sur `http://127.0.0.1:5000`  

## Sécurité et cryptographie  
Le projet met en œuvre plusieurs bonnes pratiques de sécurité :  
- **Stockage des mots de passe avec Argon2**, l’un des algorithmes de hachage les plus sécurisés actuellement.  
- **Re-hash automatique** si un mot de passe a été haché avec une version obsolète du paramétrage d’Argon2.  
- **Chiffrement des conversations** pour garantir la confidentialité des échanges.  
- **Protection contre les attaques XSS et CSRF** via l’utilisation des mécanismes intégrés à Flask.  
- **Gestion des sessions avec expiration configurable** et invalidation après fermeture des onglets du navigateur.  

## À venir  
- Ajout du **support multi-utilisateurs** pour les discussions de groupe.  
- Intégration d’un **système d’authentification à deux facteurs (2FA)**.  
- Mise en place d’un **mode anonyme** pour la discussion.  
- Amélioration de la gestion des logs et des notifications.  

## Licence  
Ce projet est sous licence **GPL-3.0**. Vous êtes libre de l'utiliser, de le modifier et de le redistribuer, mais tout projet dérivé doit également être sous la même licence.  

## Remerciements  
Ce projet a été développé avec l’aide de **ChatGPT** pour l’optimisation du code, l’organisation des fichiers et la documentation.
