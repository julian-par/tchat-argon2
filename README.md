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

