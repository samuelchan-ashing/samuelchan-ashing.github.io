# Site de Samuel Chan-ashing

Site statique (HTML, CSS et JavaScript, sans compilation), publié avec GitHub Pages.

## Pages

| Fichier | Contenu |
|---|---|
| `index.html` | Page d'accueil qui défile : Home, About, Research, Vita, Teaching, puis le pied de page (contact) |
| `paper.html?id=<arXiv id>` | Lecteur d'article : récupère la dernière version HTML sur arXiv et la met en page |
| `stays/*.html` | Mémoires de stage, au même format que les articles (pages fixes, générées une fois depuis les .tex) |
| `portrait.html` | Résumé en anglais du portrait paru dans *Réunionnais du Monde* (avril 2026), avec lien vers l'article en français |
| `agregation.html` | Page Agrégation (en français) |

## Apparence

- Mode clair par défaut : fond blanc cassé `#f0ebe3`, texte noir, bordeaux `#a72144` (onglet actif, liens, théorèmes), or `#eeb760`, chocolat `#4b3317` (bouton PDF).
- Mode sombre : bouton lune / soleil en haut de chaque page. Le choix est mémorisé dans le navigateur du visiteur. Les couleurs sont dans `assets/css/site.css`, bloc `:root[data-theme="dark"]`.
- Les pages d'article et de mémoire prennent une nuance de la couleur de leur pochette (`tint` dans `assets/js/data.js` pour les articles, dans la balise `<style>` de chaque page `stays/*.html` pour les mémoires).
- Sur l'accueil, un tap sur « Papers › » ou « Research stays › » fait passer des pochettes à une liste.
- Image d'accueil : `assets/img/hero.webp` (clair) et `assets/img/hero-dark.webp` (sombre), les courbes du phénomène de cutoff.
- Polices incluses dans `assets/fonts` : Inter (texte), STIX Two Text (le nom), STIX Two Math (formules).

## Ajouter un article

1. Dans `assets/js/data.js`, ajouter une entrée en haut de `papers` : id arXiv, titre, date, statut, pochette, `tint`.
2. Dans `index.html`, section **Papers** :
   - copier une carte `<li class="card">` du carrousel (en premier si c'est le plus récent) et changer l'id, le titre et l'image ;
   - copier aussi une ligne `<li class="row">` de la liste `#papers-list` juste en dessous.
3. Pochette : une image carrée de 800×800 dans `assets/img/covers/`.

## Comment le HTML arXiv est récupéré

`paper.html` lit `https://arxiv.org/html/<id>` directement dans le navigateur du visiteur (arXiv autorise ces lectures croisées), donc une nouvelle version postée sur arXiv apparaît sur le site sans rien faire. Les mots-clés et la classification MSC sont reconnus qu'ils soient écrits avec `\keywords` / `\subjclass` ou en simples paragraphes.
Si arXiv est injoignable, la page essaie `papers/<id>.html`. Pour créer ou rafraîchir ces copies de secours :

```
python3 tools/update_papers.py
```

## Mémoires de stage

Les pages `stays/` ont été générées une fois à partir des sources LaTeX (pandoc + MathML, figures TikZ compilées en SVG dans `stays/figures/`).
Pour les régénérer : mettre les `.tex` dans `tools/memoirs/src/` (noms dans `stays.json`) puis `python3 tools/memoirs/build_stays.py .` (il faut pandoc via `pip install pypandoc_binary`, `beautifulsoup4`, et une distribution LaTeX pour les figures).
Les PDF sont dans `pdf/`, avec des noms sans accents.

## Mise en ligne (GitHub Pages)

Dépôt `samuelchan-ashing.github.io`, branche `main`, dossier racine. Pour mettre à jour : **Add file → Upload files**, glisser les fichiers modifiés (ou tout le contenu de ce dossier), puis **Commit changes**. Les fichiers de même nom sont remplacés ; la mise en ligne prend une ou deux minutes.

- Le dossier `agreg/` (PDF des développements, liés depuis `agregation.html` sous `agreg/développement/…`) n'est pas dans ce dossier : il faut l'ajouter à la racine du dépôt depuis l'ancien serveur.
- `.nojekyll` (fichier caché) indique à GitHub de publier les fichiers tels quels.
