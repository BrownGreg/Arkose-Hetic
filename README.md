(The file `/home/browngreg/Hetic/arkose/README.md` exists, but is empty)
# Arkose — Dashboard & Automations

Ce dépôt contient un tableau de bord Streamlit (`main.py`) et trois exports de workflows n8n. (automatisations marketing pour Arkose).

**Prérequis**
- Python 3.8+ installé
- Créez et activez un environnement virtuel recommandé

**Installation**

1. Créez et activez un venv :

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

**Lancer l'application**

Depuis la racine du projet lancez :

```bash
streamlit run main.py
```

L'application Streamlit s'ouvrira dans votre navigateur (par défaut sur `http://localhost:8501`).

Si vous voulez spécifier un CSV différent, modifiez la valeur du chemin dans `main.py` ou remplacez `ARKOSE donnees_2025_graph.csv` par votre fichier.

---

**À quoi sert `main.py`**

- `main.py` est une application Streamlit qui :
	- charge et nettoie les données depuis `ARKOSE donnees_2025_graph.csv`;
	- propose des filtres (mois, jour) et affiche des KPIs financiers (CA estimé, part restauration, dépense moyenne par visiteur) ;
	- propose un simulateur de prix/mix clients pour estimer le CA selon différents profils (abonnés, carnets, unitaires) ;
	- affiche des graphiques (flux grimpeurs, ventes resto, taux de conversion) et un onglet de données brutes téléchargeable (`arkose_donnees_propres.csv`) ;
	- dans l'onglet "Automations n8n" : affiche et permet de télécharger les exports JSON des workflows n8n fournis.

Fonctions utiles dans le fichier : `load_data(path)` pour charger/normaliser le CSV, et `load_workflow(path)` pour lire un JSON d'export n8n.

---

**Les 3 automations n8n (fichiers JSON fournis)**

Les fichiers à la racine :

- `n8n_arkose_acquisition.json` — Acquisition Heures Creuses
	- Déclenchement : hebdomadaire (`Schedule Trigger`).
	- Récupère la ligne de la semaine passée depuis un Google Sheet (configurer `sheetId`).
	- Si la capacité/passage est faible (ex. seuil 160), envoie un email promotionnel aux abonnés.
	- Usage : importer dans n8n, ajouter l'ID du Google Sheet et configurer OAuth2 / paramètres email.

- `n8n_arkose_conversion.json` — Conversion Restauration
	- Déclenchement : quotidien.
	- Récupère les données de la journée précédente, calcule le ratio `Plat / Passage`.
	- Si le ratio < 15%, envoie une alerte Slack pour lancer une promo restauration.
	- Usage : importer, configurer l'accès Google Sheets et le canal Slack.

- `n8n_arkose_fidelisation.json` — Fidélisation J+21
	- Déclenchement : quotidien.
	- Récupère le fichier clients depuis Google Sheets, filtre les clients dont la dernière visite remonte à 21 jours.
	- Envoie un email de relance personnalisé (`Email Relance`) aux clients ciblés.
	- Usage : importer et renseigner l'ID du sheet clients et les paramètres d'envoi d'email.

Remarques pour n8n :
- Avant d'activer les workflows, mettez à jour les `sheetId` et configurez les credentials OAuth2 (Google Sheets), Slack et email.
- Pour importer un workflow : ouvrez n8n → Workflows → Import → choisissez le fichier JSON.

---

Fichiers clés dans ce dépôt :
- `main.py` — application Streamlit (dashboard)
- `requirements.txt` — dépendances Python
- `ARKOSE donnees_2025_graph.csv` — jeu de données source
- `n8n_arkose_*.json` — exports de workflows n8n à importer

Si vous voulez, je peux :
- exécuter l'application localement et vérifier qu'elle démarre, ou
- générer un petit script d'exemple pour importer automatiquement ces workflows dans n8n (via API).

