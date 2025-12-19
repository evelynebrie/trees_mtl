# Arbres de Montréal

Visualisation interactive des arbres plantés à Montréal avec chronologie temporelle.

## 🚀 Déploiement sur GitHub Pages

### Étape 1 : Générer le fichier de données

**Important** : Pour un chargement ultra-rapide, vous devez d'abord combiner les 7 fichiers CSV en un seul fichier JSON.

1. Placez tous les fichiers CSV dans un dossier avec `combine_tree_data.py`
2. Exécutez le script :
   ```bash
   python3 combine_tree_data.py
   ```
3. Cela créera `trees_combined.json` (chargement instantané ⚡)

### Étape 2 : Téléverser sur GitHub

1. Créez un nouveau dépôt sur GitHub
2. Téléversez ces fichiers :
   - `index.html`
   - `trees_combined.json` ⚡ (fichier généré)
   - `README.md` (ce fichier)
   
**Note** : Vous n'avez PAS besoin de téléverser les 7 fichiers CSV individuels sur GitHub, seulement le `trees_combined.json`.

### Étape 3 : Activer GitHub Pages

1. Allez dans **Settings** → **Pages**
2. Sous "Source", sélectionnez **Deploy from a branch**
3. Sélectionnez la branche **main** et le dossier **/ (root)**
4. Cliquez sur **Save**

Votre site sera disponible à : `https://votrenom.github.io/nom-du-depot/`

## 🌳 Fonctionnalités

- **Curseur temporel** : Naviguez à travers les années
- **Lecture automatique** : Animation fluide (2,5 secondes par année)
- **Filtre par type** : Sélectionnez une espèce spécifique
- **Information détaillée** : Cliquez sur un arbre pour voir ses détails
- **Statistiques en temps réel** : Nombre d'arbres visibles
- **Chargement instantané** ⚡ : Grâce au fichier JSON pré-traité

## 🧪 Test en local

```bash
# Avec Python 3
python3 -m http.server 8000

# Ouvrez : http://localhost:8000
```

## 📊 Structure des fichiers

### Sur votre ordinateur (pour la génération) :
```
dossier-local/
│
├── combine_tree_data.py    # Script Python
├── arbres-part-aa.csv      # Données source
├── arbres-part-ab.csv
├── ... (jusqu'à ag.csv)
└── trees_combined.json     # ← Généré par le script
```

### Sur GitHub (déploiement) :
```
votre-depot/
│
├── index.html              # Page principale
├── trees_combined.json     # Données (fichier unique)
└── README.md               # Documentation
```

## ⚡ Pourquoi c'est plus rapide ?

- **Avant** : 7 fichiers CSV → 7 requêtes réseau → parsing CSV → ~10-30 secondes
- **Après** : 1 fichier JSON → 1 requête → parsing natif → **< 2 secondes** ⚡

## ⚙️ Filtrage des données

Le script filtre automatiquement :
- Années invalides (< 1850 ou > 2025)
- Coordonnées manquantes ou invalides
- Valeurs aberrantes comme "205" sont ignorées

---

Données : Ville de Montréal (données ouvertes)
