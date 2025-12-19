# Arbres de Montréal

Visualisation interactive des arbres plantés à Montréal avec chronologie temporelle.

## 🚀 Déploiement sur GitHub Pages

### 1. Créer un nouveau dépôt GitHub

1. Créez un nouveau dépôt sur GitHub
2. Téléversez ces fichiers :
   - `index.html`
   - Les 7 fichiers CSV : `arbres-part-aa.csv` à `arbres-part-ag.csv`
   - `README.md` (ce fichier)

### 2. Activer GitHub Pages

1. Allez dans **Settings** → **Pages**
2. Sous "Source", sélectionnez **Deploy from a branch**
3. Sélectionnez la branche **main** et le dossier **/ (root)**
4. Cliquez sur **Save**

Votre site sera disponible à : `https://votrenom.github.io/nom-du-depot/`

## 🌳 Fonctionnalités

- **Curseur temporel** : Naviguez à travers les années pour voir l'évolution des plantations
- **Lecture automatique** : Visualisation animée des plantations (2,5 secondes par année)
- **Filtre par type** : Sélectionnez une espèce d'arbre spécifique
- **Information détaillée** : Cliquez sur un arbre pour voir ses détails
- **Statistiques en temps réel** : Nombre d'arbres visibles et total

## 🧪 Test en local

Pour tester localement avant le déploiement :

```bash
# Avec Python 3
python3 -m http.server 8000

# Ouvrez ensuite : http://localhost:8000
```

## 📊 Structure des fichiers

```
votre-depot/
│
├── index.html              # Page principale
├── arbres-part-aa.csv      # Données arbres (partie 1)
├── arbres-part-ab.csv      # Données arbres (partie 2)
├── arbres-part-ac.csv      # Données arbres (partie 3)
├── arbres-part-ad.csv      # Données arbres (partie 4)
├── arbres-part-ae.csv      # Données arbres (partie 5)
├── arbres-part-af.csv      # Données arbres (partie 6)
├── arbres-part-ag.csv      # Données arbres (partie 7)
└── README.md               # Ce fichier
```

## ⚙️ Configuration

Le jeton Mapbox est déjà configuré dans le fichier `index.html`. Les années invalides (< 1850 ou > 2025) sont automatiquement filtrées.

## 🎨 Design

- Interface minimaliste et élégante
- Palette de couleurs verte sobre
- Carte de base claire (Mapbox Light)
- Interface entièrement en français

---

Données : Ville de Montréal (données ouvertes)
