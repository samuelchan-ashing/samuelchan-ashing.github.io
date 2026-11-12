# Site de Samuel Chan-ashing

Site statique (HTML/CSS/JS, sans compilation) : il suffit de déposer le dossier sur le serveur.

## Pages

| Fichier | Contenu |
|---|---|
| `index.html` | Page d'accueil unique qui défile : Home, About, Research, Vita, Teaching (en anglais) |
| `paper.html?id=<arXiv id>` | Lecteur d'article : récupère la dernière version HTML sur arXiv et la met en page |
| `agregation.html` | Page Agrégation (en français) |
| `portrait.html` | Résumé en anglais du portrait paru dans *Réunionnais du Monde* (avril 2026), avec lien vers l’article original en français |
| `stays/*.html` | Pages des mémoires de stage, au même format que les articles (fixes, générées une fois depuis les .tex) |

## Ajouter un article

1. Dans `assets/js/data.js`, ajouter une entrée en haut de `papers` (id arXiv, titre, date, pochette, couleur `tint`).
2. Dans `index.html`, copier une carte `<li class="card">` de la section **Papers** (en premier si c'est le plus récent) et changer l'id, le titre et l'image.
3. Pochette : `python3 tools/generate_art.py <dossier> laguerre` (voir les fonctions du script) ou n'importe quelle image carrée de 800×800 dans `assets/img/covers/`.

## Comment le HTML arXiv est récupéré

`paper.html` lit `https://arxiv.org/html/<id>` directement dans le navigateur du visiteur (arXiv autorise ces lectures croisées), donc une nouvelle version postée sur arXiv apparaît sur le site sans rien faire.
Si arXiv est injoignable, la page essaie `papers/<id>.html`. Pour créer ou rafraîchir ces copies de secours :

```
python3 tools/update_papers.py
```

Si un papier n'a pas de version HTML sur arXiv, la page affiche des boutons vers la page arXiv et le PDF.

## Polices

Le texte est en Inter (incluse dans `assets/fonts`, identique sur tous les appareils). Le nom en haut est en STIX Two Text, et les formules en STIX Two Math.

## Mise en ligne sur GitHub Pages

1. Sur GitHub, créer un dépôt **public** nommé exactement `<identifiant>.github.io` (sans README).
2. Y déposer le **contenu** de ce dossier (pas le dossier lui-même) : `index.html` doit être à la racine du dépôt.
3. Ajouter à la racine le dossier `agreg/` (avec son sous-dossier `développement/` et les 30 PDF), récupéré sur l'ancien serveur : la page Agrégation pointe vers `agreg/développement/<titre>.pdf`.
4. *Settings → Pages → Build and deployment* : Source « Deploy from a branch », branche `main`, dossier `/ (root)`, *Save*.
5. Le site est en ligne après une ou deux minutes à `https://<identifiant>.github.io/`. Chaque modification poussée sur `main` est publiée de la même façon.

Remarques :
- Les liens sont tous relatifs : le site marche aussi dans un dépôt de projet (`https://<identifiant>.github.io/<dépôt>/`).
- GitHub distingue majuscules, minuscules et accents dans les noms de fichiers. Les PDF du site sont dans `pdf/` avec des noms sans accent ; pour `agreg/`, vérifier après la mise en ligne qu'un PDF s'ouvre bien depuis la page Agrégation.
- `.nojekyll` (fichier caché) indique à GitHub de publier les fichiers tels quels.
- `pdf/approximation-fonctions-regulieres.pdf` venait de l'ancien site mais n'est lié depuis aucune page.
- Ancien site (serveur ENS Rennes) : on peut y remplacer `index.html` par une redirection vers la nouvelle adresse.

## Mémoires de stage

Les pages `stays/` ont été générées une fois à partir des sources LaTeX (pandoc + MathML, figures TikZ compilées en SVG dans `stays/figures/`). Elles ne dépendent de rien et ne changent pas.
Pour les régénérer : mettre les `.tex` dans `tools/memoirs/src/` (noms dans `stays.json`) puis `python3 tools/memoirs/build_stays.py .` (il faut pandoc via `pip install pypandoc_binary`, `beautifulsoup4`, et une distribution LaTeX pour les figures).
Sources utilisées : Cutoff 2024 (`Corps.tex`), Cambridge 2022 (`Article final - S. Chan-ashing.tex`, version finale du PDF), N corps 2021, Logvinenko–Sereda 2021.
