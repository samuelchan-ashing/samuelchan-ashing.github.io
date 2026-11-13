# Site de Samuel Chan-ashing

Site statique (HTML, CSS et JavaScript, sans compilation), publié avec GitHub Pages.

## Pages

| Fichier | Contenu |
|---|---|
| `index.html` | Page d'accueil qui défile : Home, About, Research, Vita, Teaching, puis le pied de page (contact) |
| `paper.html?id=<arXiv id>` | Lecteur d'article : récupère la dernière version HTML sur arXiv et la met en page |
| `stays/*.html` | Mémoires de stage, au même format que les articles (pages fixes, générées une fois depuis les .tex) |
| `portrait.html` | Résumé en anglais du portrait paru dans *Réunionnais du Monde* (avril 2026), avec lien vers l'article en français |
| `agregation.html` | Page Agrégation (contenu en français dans les deux langues) |

## Apparence

- Mode clair par défaut : fond blanc cassé `#f0ebe3`, texte noir, bordeaux `#a72144` (onglet actif, liens, théorèmes), or `#eeb760`, chocolat `#4b3317` (bouton PDF).
- Mode sombre : bouton lune / soleil en haut de chaque page. Le choix est mémorisé dans le navigateur du visiteur. Les couleurs sont dans `assets/css/site.css`, bloc `:root[data-theme="dark"]`.
- Les pages d'article et de mémoire prennent une nuance de la couleur de leur pochette (`tint` dans `assets/js/data.js` pour les articles, dans la balise `<style>` de chaque page `stays/*.html` pour les mémoires).
- Sur l'accueil, un tap sur « Papers › » ou « Research stays › » fait passer des pochettes à une liste.
- Image d'accueil : `assets/img/hero.webp` (clair) et `assets/img/hero-dark.webp` (sombre), le cutoff du processus d'Ornstein–Uhlenbeck (voir « Images »).
- Polices incluses dans `assets/fonts` : Inter (texte), STIX Two Text (le nom), STIX Two Math (formules).

## Langues (anglais, français, kréol reyoné)

- Le site est écrit en anglais dans les fichiers HTML. Le bouton « EN » / « FR » / « KR » en haut de chaque page, à côté de la lune, ouvre un petit menu : English, Français, Kréol Reyoné. Le choix est mémorisé dans le navigateur du visiteur.
- Une première visite est toujours en anglais et en mode clair.
- La traduction est faite dans le navigateur par `assets/js/i18n.js`, à partir de deux dictionnaires « texte anglais → traduction » : `tools/i18n/fr.py` (français) et `tools/i18n/kr.py` (créole, code de langue `rcf`). Ce qui reste volontairement dans sa langue d'origine : titres et texte des articles (arXiv), mémoires (anglais ou français), titre de la thèse, contenu de la page Agrégation (français), noms d'établissements.
- Créole : graphie phonétique avec z et s (zour, sarz), tout créolisé y compris les termes mathématiques, noms de lieux réunionnais en créole (La Rényon, Lé Zaviron, Sin-Pyèr). Les mois sont dans `MONTHS_RCF` de `tools/i18n/build_i18n.py`.
- Pour corriger ou ajouter une traduction : modifier `fr.py` ou `kr.py` (la clé est le texte anglais exactement comme sur la page), puis depuis la racine du site `python3 tools/i18n/build_i18n.py`, qui réécrit `assets/js/i18n.js`. Les paragraphes longs (À propos, portrait) ont une clé `"#bio"` / `"#portrait-intro"` qui correspond à `data-i18n="…"` dans le HTML.
- Un texte anglais modifié dans le HTML sans mise à jour des dictionnaires reste simplement en anglais dans les autres langues.
- Un élément marqué `class="only-en"` n'est affiché qu'en anglais (par exemple « Original title » sur les mémoires en français).

## Images : vraies simulations

Les trois pochettes d'articles et l'image d'accueil sont calculées à partir des processus étudiés, avec les couleurs Sanzo Wada du site. Chaque script de `tools/covers/` est entièrement autonome (numpy, scipy, matplotlib) : copié-collé dans un fichier ou une cellule de notebook, il simule tout et produit l'image en PNG (affichée aussi dans un notebook). Le PNG est écrit à côté du script (dans un notebook : dans le dossier courant), et chaque exécution tire un nouvel aléa. Pour régénérer les images du site, avec les graines fixes du site (6 pour la métastabilité, pour que le saut tombe au milieu) : `python3 tools/covers/make_site_images.py` (ou avec le nom d'un script en argument).

| Script | Image | Contenu |
|---|---|---|
| `dyson_laguerre.py` | `assets/img/covers/dyson-laguerre.webp` | β = 2, α = 2n, départ en 0. Trajectoires simulées exactement (valeurs propres de M M*, M matrice n × 2n d'Ornstein–Uhlenbeck complexe), n = 40. Profils de cutoff simulés pour n = 2 à 256 : distance de Kolmogorov entre la loi de la somme des particules (la trace de M M*, calculée sur des matrices simulées) et sa loi d'équilibre ; environ 1 min 30 |
| `dyson_jacobi.py` | `assets/img/covers/dyson-jacobi.webp` | β = 2, a = b = 2n, départ dans [0,75 ; 1). Euler–Maruyama où chaque copie a son propre pas, θ × (plus petit écart entre particules)², θ = 0,05. Profils mesurés par Monte-Carlo pour n = 2 à 32 ; environ 15 minutes. Vérifications dans `dyson_jacobi_checks.py` (figure `dyson-jacobi-checks.png`) : moments exacts E[Σxᵢ²] et Var(Σxᵢ) (système d'EDO fermé), erreur faible en fonction du pas, comparaison avec le modèle matriciel β = 2 (mouvement brownien unitaire) ; aucun biais détectable à la précision Monte-Carlo |
| `metastable.py` | `assets/img/covers/metastable.webp` | Modèle cosinus du notebook `metacos_rapport.ipynb` : N = 80, σ = √2, J = √(50e), graine 6, horizon 800 ; densité des particules et moyenne empirique, qui saute de 6,64 à 1,38 |
| `ornstein_uhlenbeck.py` | `assets/img/hero.webp`, `hero-dark.webp` | Ornstein–Uhlenbeck dans Rⁿ depuis (1, …, 1) : distance en variation totale à l'équilibre estimée par Monte-Carlo (vecteurs gaussiens de dimension n simulés, rapport de vraisemblance), pour n = 2 à 2¹⁸, contre t / (½ log n) ; environ 1 min 30 |

Les profils sont tracés contre t / cₙ ; plus n est grand, plus ils se rapprochent d'un angle droit (cutoff).

Sur la page d'un article, un petit bouton « </> Code » en bas de la pochette (qui devient « View the simulation code » au survol) ouvre le script, avec Copier et Télécharger. C'est exactement le code du script, lu dans `assets/js/sim-code.js`, généré par `python3 tools/covers/build_code_js.py` : à relancer après toute modification d'un script. Le lien entre article et script est le champ `code` de `assets/js/data.js`.

Sous chaque pochette d'article, une légende d'une phrase, comme un titre de figure (quel processus, quelle distance, les paramètres). Le texte est dans `tools/i18n/captions.py`, en anglais, français et créole : après une modification, depuis la racine du site, `python3 tools/i18n/captions.py` (qui l'écrit dans le champ `caption` de `assets/js/data.js` et dans `fr.py` / `kr.py`), puis `python3 tools/i18n/build_i18n.py`.

Les pochettes des mémoires de stage restent des illustrations.

## Ajouter un article

1. Dans `assets/js/data.js`, ajouter une entrée en haut de `papers` : id arXiv, titre, date, statut, pochette, `tint`.
2. Dans `index.html`, section **Papers** :
   - copier une carte `<li class="card">` du carrousel (en premier si c'est le plus récent) et changer l'id, le titre et l'image ;
   - copier aussi une ligne `<li class="row">` de la liste `#papers-list` juste en dessous.
3. Pochette : une image carrée de 800×800 dans `assets/img/covers/`. Si elle vient d'un script de `tools/covers/`, l'ajouter dans `build_code_js.py` et mettre son nom dans le champ `code` de l'article : la pochette proposera alors son code.

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

## CV

`pdf/CV_Samuel_Chan-ashing.pdf`, lié depuis l'accueil (bouton rond « CV » sous le nom), le bouton « PDF » à côté du titre Vita et le pied de page. Pour le mettre à jour : remplacer ce fichier par le nouveau PDF en gardant exactement le même nom (rien d'autre à changer).

## Mise en ligne (GitHub Pages)

Dépôt `samuelchan-ashing.github.io`, branche `main`, dossier racine. Pour mettre à jour : **Add file → Upload files**, glisser les fichiers modifiés (ou tout le contenu de ce dossier), puis **Commit changes**. Les fichiers de même nom sont remplacés ; la mise en ligne prend une ou deux minutes.

Avant d'envoyer des fichiers modifiés, lancer `python3 tools/bump_version.py` : il met un numéro de version (`?v=…`) sur les liens vers les CSS et JS de chaque page, pour que les navigateurs ne mélangent pas les nouveaux fichiers avec d'anciennes copies gardées en cache. Après l'envoi, si une page paraît bizarre, la recharger avec Cmd+Maj+R.

- Le dossier `agreg/` (PDF des développements, liés depuis `agregation.html` sous `agreg/développement/…`) n'est pas dans ce dossier : il faut l'ajouter à la racine du dépôt depuis l'ancien serveur.
- `.nojekyll` (fichier caché) indique à GitHub de publier les fichiers tels quels.
