# donor-acquisition-system
This app helps you collect fund using prospects generation 
# AI Donor Acquisition System

Un système avancé d'acquisition de donateurs utilisant l'intelligence artificielle pour identifier, évaluer et engager des prospects potentiels pour Second Life NGO.

![AI Donor Acquisition System](/home/ubuntu/donor-acquisition-system/src/static/screenshot.png)

## Fonctionnalités principales

- **Web Crawler Intelligent** : Identifie automatiquement les organisations et individus publiant sur la durabilité environnementale.
- **Moteur de Scoring IA** : Évalue les prospects selon leur historique de dons, leur engagement et leur alignement avec la mission.
- **Communication Personnalisée** : Génère des emails, messages LinkedIn et scripts d'appel adaptés à chaque prospect.
- **Automatisation des Campagnes** : Planifie et exécute des séquences de communication multi-canal.
- **Intégration n8n** : Automatise les workflows et connecte avec d'autres systèmes via webhooks.
- **Interface Utilisateur Intuitive** : Tableau de bord complet pour gérer l'ensemble du processus d'acquisition.

## Architecture du système

Le système est construit avec une architecture modulaire comprenant :

1. **Module de Crawling** : Découvre de nouveaux prospects potentiels sur le web.
2. **Module de Scoring** : Utilise l'IA pour évaluer et prioriser les prospects.
3. **Module de Communication** : Génère du contenu personnalisé pour l'engagement.
4. **API RESTful** : Permet l'intégration avec d'autres systèmes.
5. **Interface Utilisateur** : Tableau de bord pour gérer l'ensemble du processus.

## Technologies utilisées

- **Backend** : Flask (Python)
- **IA et ML** : OpenAI API, scikit-learn
- **Web Crawling** : BeautifulSoup, Requests
- **Base de données** : SQLite (extensible à PostgreSQL)
- **Frontend** : HTML5, CSS3, JavaScript
- **Automatisation** : n8n (via webhooks)

## Installation

### Prérequis

- Python 3.8+
- pip
- Clé API OpenAI

### Installation sur Linux/macOS

```bash
# Cloner le dépôt
git clone https://github.com/votre-organisation/donor-acquisition-system.git
cd donor-acquisition-system

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer le fichier .env avec votre clé API OpenAI

# Lancer l'application
python src/main.py
```

### Installation sur Windows

Voir le fichier [README_WINDOWS.md](README_WINDOWS.md) pour des instructions détaillées d'installation sur Windows avec VS Code.

## Utilisation

1. Accédez à l'interface web à l'adresse `http://localhost:5000`
2. Utilisez le formulaire de découverte pour lancer une recherche de prospects
3. Examinez et scorez les prospects découverts
4. Générez du contenu de communication personnalisé
5. Créez et lancez des campagnes d'engagement

## Intégration avec n8n

Le système expose des webhooks pour l'intégration avec n8n :

- `/api/donor/n8n/webhook` - Point d'entrée principal pour les automatisations

Actions disponibles :
- `start_crawl` - Lance une nouvelle campagne de crawling
- `score_prospects` - Score tous les prospects en attente
- `execute_outreach` - Exécute une tâche de communication

## Développement

### Structure du projet

```
donor-acquisition-system/
├── src/
│   ├── main.py                    # Point d'entrée de l'application
│   ├── intelligent_donor_crawler.py  # Module de crawling
│   ├── ai_scoring_engine.py       # Moteur de scoring IA
│   ├── personalized_outreach.py   # Génération de communication
│   ├── routes/                    # Routes API
│   ├── models/                    # Modèles de données
│   ├── static/                    # Fichiers frontend
│   └── database/                  # Base de données SQLite
├── venv/                          # Environnement virtuel
├── requirements.txt               # Dépendances Python
├── .env.example                   # Exemple de configuration
└── README.md                      # Documentation
```

### Contribution

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add some amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Contact

Second Life NGO - [contact@secondlife-ngo.org](mailto:contact@secondlife-ngo.org)

---

Développé avec ❤️ pour Second Life NGO

