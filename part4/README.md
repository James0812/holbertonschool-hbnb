# 🏠 HBnB — Holberton School Project

> Application web de location de logements inspirée d'Airbnb, développée dans le cadre du cursus Holberton School — Part 4.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-REST%20API-black?style=flat-square&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?style=flat-square&logo=sqlite)
![HTML5](https://img.shields.io/badge/HTML5-Frontend-orange?style=flat-square&logo=html5)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?style=flat-square&logo=javascript)

---

## 👥 Auteurs

| Nom | GitHub |
| :--- | :--- |
| **James** | [James0812](https://github.com/James0812) |
| **Tommy Jouhans** | [Tommy-JOUHANS](https://github.com/Tommy-JOUHANS) |

---

## 📋 Description du projet

HBnB est une application web full-stack qui permet à des utilisateurs de :
- 🏡 **Consulter** une liste de logements disponibles
- 🔍 **Filtrer** les logements par prix
- 📄 **Voir le détail** d'un logement (description, prix, équipements, avis)
- 🔐 **Se connecter** et gérer leur session
- ⭐ **Laisser un avis** sur un logement

Le projet est divisé en **4 parties** :
- `part1` — Modélisation UML et architecture
- `part2` — API REST avec Flask
- `part3` — Base de données avec SQLAlchemy
- `part4` — Frontend HTML/CSS/JS connecté à l'API

---

## 🏗️ Architecture du code
```
part4/
├── hbnb/
│   ├── __init__.py          # Initialisation de l'application Flask
│   ├── models/              # Modèles de données (User, Place, Review, Amenity)
│   │   ├── user.py
│   │   ├── place.py
│   │   ├── review.py
│   │   └── amenity.py
│   ├── api/
│   │   └── v1/              # Routes de l'API REST
│   │       ├── auth.py      # Login / JWT
│   │       ├── users.py     # CRUD utilisateurs
│   │       ├── places.py    # CRUD logements
│   │       ├── reviews.py   # CRUD avis
│   │       └── amenities.py # CRUD équipements
│   ├── web/                 # Frontend statique
│   │   ├── index.html       # Page d'accueil
│   │   ├── login.html       # Page de connexion
│   │   ├── place.html       # Page détail logement
│   │   ├── add_review.html  # Page ajout d'avis
│   │   ├── scripts.js       # Logique JavaScript
│   │   └── styles.css       # Styles CSS
│   └── extensions.py        # SQLAlchemy, JWT
├── instance/
│   └── hbnb.db              # Base de données SQLite
├── run.py                   # Point d'entrée de l'application
└── README.md
```

### Comment ça fonctionne ?
```
Navigateur (HTML/CSS/JS)
        ↕  requêtes AJAX (Fetch API)
API REST Flask (/api/v1/...)
        ↕  ORM SQLAlchemy
Base de données SQLite (hbnb.db)
```

Le frontend ne communique **jamais directement** avec la base de données. Il passe toujours par l'API Flask qui gère la logique métier et la sécurité.

---

## ⚙️ Installation et lancement

### Prérequis

- Python 3.x installé
- pip installé
- Git installé

### Étape 1 — Cloner le projet
```bash
git clone https://github.com/James0812/holbertonschool-hbnb.git
cd holbertonschool-hbnb/part4
```

### Étape 2 — Créer et activer l'environnement virtuel
```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer sur Linux/Mac
source venv/bin/activate

# Activer sur Windows
venv\Scripts\activate
```

### Étape 3 — Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 4 — Lancer le serveur
```bash
python run.py
```

### Étape 5 — Ouvrir le frontend

Ouvrez votre navigateur sur :
```
http://127.0.0.1:5000
```

---

## 🌐 Pages du Frontend

### 📄 index.html — Page d'accueil

Page principale de l'application. Elle affiche tous les logements disponibles sous forme de cartes.

**Fonctionnalités :**
- Affichage dynamique des logements via l'API
- Filtre par prix max (10€ / 50€ / 100€ / Tous)
- Si l'utilisateur est connecté → bouton "Déconnexion" affiché
- Si l'utilisateur n'est pas connecté → lien "Connexion" affiché
- Chaque carte logement contient : titre, description, prix et bouton "Voir"

---

### 🔐 login.html — Page de connexion

Formulaire de connexion avec email et mot de passe.

**Fonctionnalités :**
- Envoi des identifiants à l'API via une requête POST
- Si succès → token JWT stocké dans un cookie et redirection vers l'accueil
- Si échec → message d'erreur affiché

---

### 🏡 place.html — Page détail d'un logement

Page qui affiche toutes les informations d'un logement spécifique.

**Fonctionnalités :**
- Récupération de l'ID du logement depuis l'URL (`?id=...`)
- Affichage : titre, adresse, prix, description, équipements, avis
- Liste de tous les avis avec note en étoiles et commentaire
- Si connecté → bouton "Ajouter un avis" visible
- Si non connecté → bouton caché

---

### ⭐ add_review.html — Page ajout d'avis

Formulaire pour laisser un avis sur un logement.

**Fonctionnalités :**
- Accessible uniquement aux utilisateurs connectés
- Si non connecté → redirection automatique vers l'accueil
- Champs : note (1 à 5) et commentaire
- Envoi à l'API via requête POST avec le token JWT
- Si succès → message de confirmation et retour sur la page du logement

---

## 🗄️ Base de données SQLite

### Structure des tables

La base de données contient **5 tables** :

| Table | Description |
| :--- | :--- |
| `users` | Utilisateurs de l'application |
| `places` | Logements disponibles |
| `reviews` | Avis laissés sur les logements |
| `amenities` | Équipements disponibles |
| `place_amenity` | Table de liaison places ↔ amenities |

### Schéma des relations
```
users ──────────── places
  │                  │
  │                  │
reviews ────────── place_amenity ── amenities
```

- Un **user** peut avoir plusieurs **places**
- Un **user** peut laisser plusieurs **reviews**
- Une **place** peut avoir plusieurs **reviews**
- Une **place** peut avoir plusieurs **amenities** (relation many-to-many)

### Ouvrir la base de données
```bash
sqlite3 instance/hbnb.db
```

### Commandes SQLite essentielles

| Commande | Description |
| :--- | :--- |
| `.tables` | Lister toutes les tables |
| `.quit` | Quitter SQLite |
| `PRAGMA table_info(places);` | Voir la structure d'une table |

### Lire les données

| Commande | Description |
| :--- | :--- |
| `SELECT * FROM places;` | Voir tous les logements |
| `SELECT * FROM users;` | Voir tous les utilisateurs |
| `SELECT * FROM reviews;` | Voir tous les avis |
| `SELECT * FROM amenities;` | Voir tous les équipements |
| `SELECT COUNT(*) FROM places;` | Compter les logements |
| `SELECT title, price FROM places;` | Voir titres et prix |

### Requête avancée — Reviews liées aux places
```sql
SELECT r.text, r.rating, p.title
FROM reviews r
JOIN places p ON r.place_id = p.id;
```

### Modifier les données

| Commande | Description |
| :--- | :--- |
| `DELETE FROM reviews;` | Supprimer toutes les reviews |
| `INSERT INTO places VALUES (...);` | Insérer un logement |
| `INSERT INTO reviews VALUES (...);` | Insérer un avis |

---

## 🔐 Comment fonctionne le JWT

JWT signifie **JSON Web Token**. C'est un système d'authentification sans session serveur.

### Fonctionnement étape par étape
```
1. L'utilisateur entre son email + mot de passe
        ↓
2. Le frontend envoie une requête POST à /api/v1/auth/login
        ↓
3. Flask vérifie les identifiants en base de données
        ↓
4. Si correct → Flask génère un token JWT et le renvoie
        ↓
5. Le frontend stocke le token dans un cookie
        ↓
6. Pour chaque requête suivante, le token est envoyé
   dans le header Authorization: Bearer <token>
        ↓
7. Flask vérifie le token à chaque requête protégée
        ↓
8. Si le token est valide → accès autorisé
   Si invalide ou absent → accès refusé
```

### Structure d'un token JWT

Un token JWT est composé de 3 parties séparées par des points :
```
header.payload.signature
```

- **Header** : algorithme de chiffrement utilisé
- **Payload** : données de l'utilisateur (id, email, etc.)
- **Signature** : garantit que le token n'a pas été modifié

### Stocker et supprimer le token
```javascript
// Stocker le token après login
document.cookie = `token=${data.access_token}; path=/`;

// Supprimer le token à la déconnexion
document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
```

---

## 🔧 API REST — Endpoints

### Authentification

| Méthode | Endpoint | Description | Auth requise |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Connexion utilisateur | ❌ |

### Places

| Méthode | Endpoint | Description | Auth requise |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/places/` | Liste de tous les logements | ❌ |
| `GET` | `/api/v1/places/<id>` | Détail d'un logement | ❌ |
| `POST` | `/api/v1/places/` | Créer un logement | ✅ |
| `PUT` | `/api/v1/places/<id>` | Modifier un logement | ✅ |
| `DELETE` | `/api/v1/places/<id>` | Supprimer un logement | ✅ |

### Reviews

| Méthode | Endpoint | Description | Auth requise |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/reviews/` | Liste de tous les avis | ❌ |
| `POST` | `/api/v1/reviews/` | Ajouter un avis | ✅ |
| `PUT` | `/api/v1/reviews/<id>` | Modifier un avis | ✅ |
| `DELETE` | `/api/v1/reviews/<id>` | Supprimer un avis | ✅ |

### Users

| Méthode | Endpoint | Description | Auth requise |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/users/` | Liste des utilisateurs | ✅ |
| `POST` | `/api/v1/users/` | Créer un utilisateur | ❌ |
| `PUT` | `/api/v1/users/<id>` | Modifier un utilisateur | ✅ |

---

## 🐛 Erreurs rencontrées et solutions

### ❌ Problème — Double "Emplacement non précisé"

**Cause :** Le fichier `place.html` avait une balise statique avec ce texte ET le JavaScript en ajoutait une deuxième dynamiquement.

**Solution :**
```bash
sed -i '/<p id="place-address">📍 Emplacement non précisé<\/p>/d' place.html
```

---

### ❌ Problème — Reviews n'apparaissaient pas (JOIN vide)

**Cause :** Les `place_id` dans la table `reviews` contenaient l'ID de l'utilisateur au lieu de l'ID des places — les colonnes avaient été inversées lors de l'INSERT.

**Solution :**
```sql
DELETE FROM reviews;
-- Réinsérer avec les bons place_id dans le bon ordre
INSERT INTO reviews VALUES ('id', 'texte', note, 'user_id', 'place_id', ...);
```

---

### ❌ Problème — Mots en anglais (Home, Logout, User)

**Cause :** Les fichiers `login.html` et `add_review.html` n'avaient pas été traduits.

**Solution :**
```bash
sed -i 's/>Logout</>Déconnexion</g' login.html add_review.html
sed -i 's/>Home</>Accueil</g' login.html add_review.html
sed -i "s/|| 'User'/|| 'Utilisateur'/g" scripts.js
```

---

### ❌ Problème — SHOW TABLES ne fonctionne pas dans SQLite

**Cause :** `SHOW TABLES` est une commande MySQL, pas SQLite.

**Solution :**
```sql
.tables  -- Commande SQLite correcte
```

---

## 🔐 Compte administrateur par défaut

| Champ | Valeur |
| :--- | :--- |
| Email | `admin@hbnb.io` |
| Mot de passe | `admin1234` |
| Rôle | Administrateur |

---

## 📦 Technologies utilisées

| Technologie | Version | Usage |
| :--- | :--- | :--- |
| Python | 3.x | Langage principal backend |
| Flask | 2.x | Framework web et API REST |
| SQLAlchemy | 2.x | ORM pour la base de données |
| SQLite | 3.x | Base de données locale |
| Flask-JWT-Extended | - | Authentification par token |
| HTML5 | - | Structure des pages |
| CSS3 | - | Style et mise en page |
| JavaScript ES6 | - | Logique frontend et appels API |
| Fetch API | - | Requêtes AJAX vers l'API |

---

## 🧹 Commandes Linux utiles

### Navigation et lecture

| Commande | Description |
| :--- | :--- |
| `ls` | Lister les fichiers |
| `cd dossier/` | Se déplacer |
| `cat fichier` | Lire un fichier |
| `grep -n "mot" fichier` | Chercher dans un fichier |
| `find . -name "*.html"` | Trouver des fichiers |
| `sed -n '10,20p' fichier` | Lire des lignes précises |

### Modifier des fichiers

| Commande | Description |
| :--- | :--- |
| `sed -i 's/ancien/nouveau/g' fichier` | Remplacer du texte |
| `sed -i '/ligne/d' fichier` | Supprimer une ligne |
| `cat >> fichier << 'EOF'` | Ajouter à la fin d'un fichier |

### Navigateur

| Raccourci | Description |
| :--- | :--- |
| `Ctrl + Shift + R` | Vider le cache et recharger |

---

> 📚 Projet réalisé dans le cadre de la formation **Holberton School** — 2026
