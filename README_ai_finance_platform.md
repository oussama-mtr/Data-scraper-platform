# AI Finance Platform — Extraction et collecte de données financières

Outils de collecte de documents financiers, d’extraction de tableaux et d’export Excel. Ce README couvre uniquement le téléversement de fichiers et la recherche de documents en ligne.

Deux parcours distincts sont présents dans le code :


| Parcours                          | Interface et moteur                                         | Fonction                                                                                                        |
| --------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Extraction de fichiers téléversés | Streamlit + Python                                          | Lire un PDF, CSV ou classeur Excel, afficher les tableaux et télécharger un fichier XLSX                        |
| Recherche et collecte en ligne    | API FastAPI + frontend React/TypeScript configuré avec Vite | Rechercher des documents sur des sites configurés, les télécharger, extraire leur contenu et produire un export |


> **État vérifié le 27 septembre 2026 :** cette documentation correspond aux fichiers présents après restauration. Le point d’entrée `frontend/src/main.tsx` reste absent alors que `frontend/index.html` le référence. Le frontend React ne peut donc pas être considéré comme opérationnel en l’état. La vérification porte sur le code ; aucun test complet de lancement ou de collecte en ligne n’est revendiqué.



## Extraction de fichiers téléversés

Le module est accessible dans l’application Streamlit, sous **Financial Data Assistant → Upload & extract tables**. Il appelle directement `table_extractor.py`, sans requête vers FastAPI.

### Fonctionnement

1. L’utilisateur téléverse un fichier depuis le navigateur.
2. L’extraction démarre automatiquement.
3. Les tableaux obtenus sont affichés dans des panneaux dépliables.
4. Un classeur Excel contenant tous les tableaux extraits est généré en mémoire.
5. L’utilisateur télécharge le résultat avec **Download Excel workbook**.



### Formats pris en charge


| Format        | Lecture                                                         | Organisation de l’export                            |
| ------------- | --------------------------------------------------------------- | --------------------------------------------------- |
| PDF numérique | `pdfplumber`, avec `page.extract_tables()` sur toutes les pages | Une feuille par tableau reconnu et non vide         |
| CSV           | `pandas.read_csv()`                                             | Une feuille pour les données lues                   |
| XLS / XLSX    | `pandas.read_excel(..., sheet_name=None)`                       | Une feuille de sortie par feuille d’entrée non vide |


Le module supprime les lignes et colonnes entièrement vides. Pour les tableaux PDF, il utilise la première ligne comme en-tête, complète les intitulés manquants et distingue les en-têtes dupliqués. Cette interprétation doit être vérifiée sur le document source.

L’export utilise **pandas avec le moteur openpyxl**. Les noms de feuilles sont nettoyés, raccourcis et rendus uniques. Le classeur est proposé sous un nom de la forme `nom_du_fichier_tables.xlsx`.

### Portée actuelle

- Aucun recours à Camelot Lattice ou Stream n’est implémenté.
- Aucun OCR ni regroupement automatique de tableaux multipages n’est implémenté.
- Il n’existe pas de filtrage des tableaux par mot-clé ni de sélection manuelle avant export.
- Aucun formatage personnalisé d’en-tête coloré ou de largeur automatique des colonnes n’est programmé.
- Le classeur est généré pendant le traitement, avant le clic de téléchargement ; il n’existe pas d’étape séparée de validation déclenchant l’export.



## Recherche et scraping de documents

Le backend FastAPI reçoit une requête textuelle et orchestre la collecte :

```text
Requête utilisateur
    → Sélection de sources par mots-clés
    → Exploration de liens HTML
    → Téléchargement des documents retenus
    → Extraction partielle du contenu
    → Aperçu et export Excel
```



### Sources configurées

Les sources sont centralisées dans `backend/config/sources.py` :

- Bourse de Casablanca ;
- Bank Al-Maghrib ;
- Haut-Commissariat au Plan ;
- Autorité Marocaine du Marché des Capitaux.

La sélection repose sur des règles de correspondance textuelle, sans appel à un modèle de langage. Jusqu’à deux sources sont retenues. L’exploration visite au maximum 25 pages par source, et l’agent tente de télécharger jusqu’à cinq documents par source retenue.

Le scraper utilise **httpx** et **BeautifulSoup**. Il parcourt des liens HTML pertinents sur les domaines configurés, sans navigateur exécutant le JavaScript des sites. La recherche n’est pas exhaustive et ne garantit pas que les documents trouvés correspondent exactement à la période ou à l’indicateur demandé.

### Formats et limites du backend


| Élément                                           | Comportement actuel                                                                                        |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Liens retenus pour téléchargement                 | `.xls`, `.xlsx`, `.csv` uniquement                                                                         |
| PDF en ligne                                      | Exclus de la liste des formats téléchargeables                                                             |
| Extraction CSV                                    | Conservation des 50 premières lignes de données                                                            |
| Extraction Excel                                  | Première feuille uniquement, avec 50 lignes de données maximum                                             |
| Fonction d’extraction PDF, si appelée directement | 5 premières pages ; 2 tableaux par page ; 20 lignes par tableau ; texte limité à 1 200 caractères par page |
| Aperçu                                            | 12 éléments maximum au total                                                                               |
| Export Excel                                      | Une feuille `Doc_N` par document contenant des éléments extraits                                           |


Les limites de lecture du backend s’appliquent aux données exportées, pas seulement à l’aperçu. Elles ne s’appliquent pas au module de téléversement Streamlit, qui parcourt toutes les pages des PDF et toutes les feuilles des classeurs.

### Routes disponibles


| Méthode | Route                            | Rôle                                             |
| ------- | -------------------------------- | ------------------------------------------------ |
| GET     | `/api/health`                    | Vérifier que l’API répond                        |
| GET     | `/api/sources`                   | Lister les sources configurées                   |
| POST    | `/api/search/stream`             | Lancer une recherche avec un champ JSON `query`  |
| GET     | `/api/history`                   | Consulter l’historique du processus courant      |
| GET     | `/api/downloads`                 | Lister les métadonnées des documents téléchargés |
| GET     | `/api/results/{search_id}`       | Consulter un résultat                            |
| GET     | `/api/results/{search_id}/excel` | Télécharger son export Excel                     |


Aucune route de téléversement de fichier n’est définie dans l’API. Le téléversement se fait dans Streamlit.

La recherche utilise une réponse **SSE**. Toutefois, les événements de progression sont actuellement accumulés pendant l’exécution de l’agent puis émis après son retour. Ils ne constituent pas une progression transmise en direct pendant la collecte.

## Structure des composants concernés

Cette arborescence présente uniquement les composants utiles à l’extraction et au scraping. Les autres fichiers du projet ne sont pas détaillés ici.

```text
ai_finance_platform/
├── app.py                          # Interface Streamlit hébergeant l’onglet d’extraction
├── table_extractor.py              # Lecture des fichiers téléversés et export en mémoire
├── requirements.txt                # Dépendances Python partagées
├── .gitignore
├── backend/
│   ├── api/
│   │   ├── main.py                 # Application FastAPI et CORS
│   │   └── routes/search.py        # Routes de recherche, résultats et téléchargements
│   ├── agents/search_agent.py      # Orchestration de la collecte
│   ├── config/sources.py           # Sources, mots-clés et formats téléchargeables
│   ├── models/schemas.py           # Structures de requêtes et de résultats
│   └── services/
│       ├── source_selector.py      # Classement des sources par mots-clés
│       ├── site_crawler.py         # Exploration des liens HTML
│       ├── document_downloader.py  # Téléchargement sur disque
│       ├── extraction_engine.py    # Extraction partielle, aperçu et export
│       └── history_store.py        # Historique en mémoire
└── frontend/
    ├── index.html                  # Référence src/main.tsx, absent actuellement
    ├── package.json                # React, TypeScript et Vite
    ├── vite.config.ts              # Port 5173 et proxy vers FastAPI
    └── src/
        ├── hooks/                 # Gestion d’état et suivi des recherches
        ├── services/api.ts        # Client HTTP
        ├── types/                 # Types TypeScript
        └── index.css
```



## Prérequis

- Python compatible avec les dépendances de `requirements.txt` ; le code utilise une syntaxe Python 3.10 ou ultérieure. Aucune matrice de compatibilité testée n’est fournie.
- **Streamlit**, à installer séparément pour l’interface de téléversement : il manque dans le fichier de dépendances actuel.
- **xlrd**, à installer pour la lecture des fichiers `.xls` : il manque également dans ce fichier.
- Node.js et npm compatibles avec Vite 5, uniquement pour le frontend React. Le dépôt ne fixe pas de version Node via un champ `engines`.

L’extraction de tableaux et le backend de scraping ne nécessitent pas de modèle de langage. Cependant, `app.py` importe actuellement un client Anthropic lors de son démarrage : cette dépendance partagée doit être configurée pour lancer l’interface Streamlit existante.

## Installation

Les commandes Python suivantes doivent être lancées depuis la racine du projet. Les imports du backend et ses chemins de stockage reposent sur ce répertoire de travail.

### Environnement Python

Sous Windows PowerShell :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install streamlit xlrd
```

Sous macOS ou Linux :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install streamlit xlrd
```



### Configuration de l’application Streamlit existante

Créer ou compléter le fichier `.env` à la racine, sans écraser les valeurs existantes :

```dotenv
ANTHROPIC_API_KEY=valeur_a_renseigner
```

Cette configuration est liée aux imports de l’application partagée. Le module `table_extractor.py` n’appelle pas Anthropic et ne lui envoie pas les documents téléversés. Le backend FastAPI de scraping n’utilise pas cette clé.

Le fichier `.env.example` n’est pas présent dans l’état vérifié. Un éventuel modèle `.env.example` peut être versionné avec des valeurs fictives ; le fichier `.env` contenant les secrets doit rester exclu du dépôt.

### Frontend React

```bash
cd frontend
npm install
```

Avant de lancer l’interface, restaurer `src/main.tsx` et les composants nécessaires à son affichage. L’installation des dépendances ne remplace pas les fichiers sources manquants.

## Lancement



### Extraction de fichiers avec Streamlit

Depuis la racine, avec l’environnement Python activé :

```bash
python -m streamlit run app.py
```

Ouvrir l’adresse indiquée par Streamlit dans le terminal. Ce parcours ne nécessite pas de lancer FastAPI ou Vite séparément.

### Scraping avec FastAPI

Depuis la racine, avec l’environnement Python activé :

```bash
python -m uvicorn backend.api.main:app --reload
```

L’API est accessible à [localhost:8000](http://localhost:8000), et sa documentation interactive à [localhost:8000/docs](http://localhost:8000/docs).

Dans cette documentation, utiliser `POST /api/search/stream` avec, par exemple :

```json
{
  "query": "exchange rate dirham"
}
```

Cet exemple illustre le format d’entrée ; il ne garantit pas qu’un document pertinent sera trouvé.

### Interface React, après restauration

Dans un autre terminal :

```bash
cd frontend
npm run dev
```

Le port configuré est **5173**. Utiliser l’adresse effectivement affichée par Vite. Le proxy de développement transmet les requêtes `/api` à `http://127.0.0.1:8000`.

La compilation est prévue avec `npm run build`. Le backend possède une logique de service des fichiers compilés, mais son chemin actuel pointe vers `backend/frontend/dist` au lieu du dossier `frontend/dist` à la racine. Ce chemin doit être corrigé avant d’utiliser cette intégration.

Les commandes ci-dessus lancent des services de développement et ne configurent pas HTTPS.

## Guide utilisateur pour l’extraction

1. Ouvrir l’application Streamlit.
2. Sélectionner **Financial Data Assistant**.
3. Ouvrir **Upload & extract tables**.
4. Cliquer sur **Choose a file** et sélectionner un PDF, CSV, XLS ou XLSX.
5. Attendre l’extraction automatique.
6. Examiner les tableaux affichés : en-têtes, colonnes, unités, signes et valeurs.
7. Cliquer sur **Download Excel workbook**.
8. Ouvrir le classeur et le rapprocher du document source avant toute utilisation analytique.

L’onglet voisin **Request data** ne constitue pas le parcours de scraping FastAPI : il produit une demande adressée à un modèle de langage, sans outil de collecte connecté à cet appel. Pour extraire des documents, utiliser le parcours d’upload ou l’API de recherche décrits ici.

## Stockage et conservation


| Élément                         | Comportement                                                                                             |
| ------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Fichier téléversé               | Lu depuis les octets fournis par Streamlit ; le module d’extraction n’enregistre pas de copie sur disque |
| Export Streamlit                | Produit en mémoire avec `BytesIO`                                                                        |
| Documents collectés par FastAPI | Stockés dans `backend/data/downloads/<source_id>/`                                                       |
| Exports FastAPI                 | Stockés dans `backend/data/exports/`                                                                     |
| Historique et résultats FastAPI | Conservés dans un dictionnaire en mémoire du processus                                                   |


Aucun nettoyage automatique des documents téléchargés et des exports n’est implémenté. L’historique disparaît au redémarrage du processus, mais les fichiers sur disque peuvent rester présents. L’historique n’est pas isolé par utilisateur et n’est pas partagé entre plusieurs processus serveur.

## Limitations et dépannage


| Situation                           | Explication ou action                                                                                               |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Aucun tableau détecté dans un PDF   | Vérifier la présence de texte sélectionnable et la structure du document ; aucun OCR n’est intégré                  |
| Colonnes ou en-têtes incorrects     | Les mises en page complexes peuvent être mal reconnues ; contrôler et corriger les données avant utilisation        |
| Tableau réparti sur plusieurs pages | Les fragments restent séparés ; aucune fusion automatique n’est effectuée                                           |
| CSV mal interprété                  | La lecture utilise les paramètres par défaut de pandas, sans détection personnalisée du séparateur ou de l’encodage |
| Échec de lecture d’un fichier XLS   | Vérifier l’installation du moteur `xlrd` dans l’environnement actif                                                 |
| Recherche sans résultat             | Les sources, mots-clés, liens accessibles et formats retenus limitent la couverture                                 |
| Export FastAPI incomplet            | Les plafonds de lignes et de feuilles sont appliqués avant l’export                                                 |
| Interface React vide ou en erreur   | Vérifier notamment le point d’entrée manquant et les composants de l’interface                                      |


L’extraction ne valide pas automatiquement les unités, les signes, les périodes comptables ni les totaux financiers. Un export lisible n’est pas une garantie d’exactitude des données.

## Sécurité

- Aucune authentification ni autorisation par utilisateur n’est implémentée pour les parcours décrits.
- Ne pas exposer ces services pour traiter des documents confidentiels sans contrôle d’accès et configuration de déploiement appropriés.
- La configuration CORS du backend autorise toutes les origines et active les identifiants ; elle doit être revue pour l’environnement cible et ne remplace pas l’authentification.
- Conserver les secrets hors du dépôt. `.env` est déjà exclu par `.gitignore`.
- Prévoir les exclusions Git de `.venv/`, `frontend/dist/` et `backend/data/`, ainsi qu’une politique de conservation et de nettoyage des fichiers.
- Définir et vérifier des limites de taille, de durée de traitement et de consommation de ressources avant un usage partagé.

