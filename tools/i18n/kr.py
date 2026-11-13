# English text (exactly as on the page, spaces collapsed) -> Reunion Creole (kréol reyoné).
# Spelling: phonetic, with z and s for the French "j" and "ch" sounds (zour, sarz), è / é, k, w, i for the French "u".
# Choices made with Samuel: everything creolized, maths included; Réunion place names in Creole (La Rényon, Lé Zaviron,
# Sin-Pyèr); "Kisa mi lé" for Home and About, "arsèrs" for research, "Zansényeman" for teaching, "moin".
# Kept as they are: names of institutions (Université Paris-Dauphine, ENS…), places outside Réunion, and the real
# titles of the two memoirs written in French.
NB = " "   # non-breaking space before ; : ? ! (French typography)
KR = {
 # ---------- shared chrome
 "Home": "Kisa mi lé", "Research": "Arsèrs", "Vita": "Parkour", "Teaching": "Zansényeman",
 "Share": "Partaz", "Back": "Rotour", "More": "Plis", "Sections": "Bann seksyon", "Show sections": "Montr bann seksyon",
 "Contents": "Sak néna dedan", "Summary": "Rézimé", "Copy link": "Kopié lo lyin", "Link copied": "Lyin kopié", "Copied": "Kopié",
 "Dark mode": "Mod nwar", "Light mode": "Mod klèr", "PDF": "PDF", "References": "Référans", "Untitled": "San tit",
 "Language": "Lang", "Agrégation": "Agrégasyon", "Contact": "Kontak",
 # ---------- home: hero and about
 "Samuel Chan-ashing — Probability": "Samuel Chan-ashing — Probabilité",
 "PhD student in probability · Paris": "Doktoran an probabilité · Paris",
 "Email": "Imel", "About": "Kisa mi lé", "Simulation artwork": "Imaz" + NB + ": simulasyon",
 "#bio": ('Mi fé in tez an probabilité, ancadré par <a href="https://djalil.chafai.net/wiki/" target="_blank" rel="noopener">Djalil Chafaï</a> '
          'semb <a href="https://quentincormier.org" target="_blank" rel="noopener">Quentin Cormier</a>. Mon arsèrs i port si la konverzans ann tan lon '
          'bann difisyon, si bann fénomèn konverzans abript (cutoff) ek si la métastabilité' + NB + '; mon tez i apel '
          '<em>Cutoff and metastability phenomena for ergodic diffusion processes</em>. Mi travay l’Université Paris-Dauphine (CEREMADE), '
          'l’École normale supérieure (DMA), Inria Saclay (ASCII) ek l’École polytechnique (CMAP).'),
 "In the press · April 2026": "Dann zournal · avril 2026",
 "Portrait in Réunionnais du Monde": "Portré dann Réunionnais du Monde",
 "Interview in French · English summary on this site": "Lartik lé an fransé · rézimé isi",
 # ---------- research
 "Research interests": "Bann tèm arsèrs", "Cutoff phenomenon": "Fénomèn cutoff", "Diffusions": "Difisyon",
 "Interacting particle systems": "Sistèm partikil an intéraksyon", "Metastability phenomenon": "Fénomèn métastabilité",
 "Random matrices": "Matris aléatoir", "Papers": "Artik",
 "2026 · with Q. Cormier": "2026 · ek Q. Cormier", "2026 · Submitted": "2026 · Soumi",
 "with Quentin Cormier · Preprint · arXiv:2610.13655": "ek Quentin Cormier · Prépiblikasyon · arXiv:2610.13655",
 "Submitted · arXiv:2601.20390": "Soumi · arXiv:2601.20390",
 "All my papers on arXiv": "Tout mon bann artik si arXiv",
 "Simulated particle systems jumping away from a metastable equilibrium": "Sistèm partikil similé k’i sort dann in ékilib métastab",
 "Cutoff profiles over simulated Dyson–Jacobi paths": "Profil cutoff si bann trazektwar Dyson–Jacobi similé",
 "Cutoff profiles over simulated Dyson–Laguerre paths": "Profil cutoff si bann trazektwar Dyson–Laguerre similé",
 "Research stays": "Staz arsèrs", "Memoir": "Mémwar",
 # the two memoirs written in French keep their real (French) titles
 "N-body problems, large N": "Problèmes à N corps, N grand",
 "Uncertainty principles": "Principes d’incertitude",
 "N-body problems when N is large": "Étude des problèmes à N corps, lorsque N est grand",
 "Uncertainty principles and the Logvinenko–Sereda theorem": "Principe d’incertitude et théorème de Logvinenko-Sereda",
 "Master 2 research stay · DMA, ENS Paris · supervised by Djalil Chafaï": "Staz arsèrs M2 · DMA, ENS Paris · ancadré par Djalil Chafaï · an anglé",
 "Master research stay · DPMMS, University of Cambridge · supervised by Clément Mouhot": "Staz arsèrs mastèr · DPMMS, liniversité Cambridge · ancadré par Clément Mouhot · an anglé",
 "Bachelor research stay · CMLS, École Polytechnique · supervised by Samir Salem · in French": "Staz arsèrs lisans · CMLS, École polytechnique · ancadré par Samir Salem · an fransé",
 "Research seminar · ENS Rennes · with Bastien Lecluse, supervised by Jérémy Martin · in French": "Séminèr arsèrs · ENS Rennes · ek Bastien Lecluse, ancadré par Jérémy Martin · an fransé",
 "Supervisors & collaborators": "Lancadran ek kolaboratèr",
 "PhD advisor": "Direktèr tez", "PhD advisor · co-author": "Direktèr tez · co-otèr",
 "Research stay, Cambridge 2022": "Staz arsèrs, Cambridge 2022", "Research stay, Polytechnique 2021": "Staz arsèrs, Polytechnique 2021",
 "Co-author, ENS Rennes 2021": "Co-otèr, ENS Rennes 2021",
 # ---------- vita
 "Education": "Formasyon", "PhD in Mathematics": "Doktora an matématik", "Thesis:": "Tez" + NB + ":",
 "Master 2, Probability and Stochastic Models": "Mastèr 2 Probabilité ek model aléatoir",
 "Agrégation of mathematics": "Agrégasyon matématik",
 "Master 1, Fundamental Mathematics": "Mastèr 1 Matématik fondamantal",
 "Bachelor, Fundamental Mathematics": "Lisans 3 Matématik fondamantal",
 "École Normale Supérieure de Rennes": "École normale supérieure de Rennes",
 "Preparatory classes": "Klas prépa", "Lycée LaSalle Saint-Charles, La Réunion": "Lycée La Salle Saint-Charles, La Rényon",
 "Distinction & talks": "Distinksyon ek ekspozé",
 "Young Talent, Higher education & research · ceremony on 23 January 2026, Université Paris Cité": "Zène talan, Zansényeman sipéryèr ek arsèrs · séremoni lo 23 zanvié 2026, Université Paris Cité",
 "Research talk, Saint-Pierre-d’Oléron, Sept.–Oct. 2025": "Ekspozé arsèrs, Saint-Pierre-d’Oléron, sep.–okt. 2025",
 "ANR Conviviality workshop": "Atelié ANR Conviviality",
 "Talk on the cutoff for Dyson–Laguerre processes, Université Lyon 1, June 2025": "Ekspozé si lo cutoff bann prosésis Dyson–Laguerre, Université Lyon 1, zin 2025",
 "Experience": "Ekspéryans", "President of the Student Council": "Prézidan BDE",
 "Since 2025": "Dopi 2025", "Expert Committee Member, La Réunion Innovation": "Manm komité lekspèr, La Réunion Innovation",
 "Advising on innovation strategy for Réunion Island, from digital transformation and inclusive societies to ecological transition and adaptations to global changes":
     "Mi done konsey si la stratézi linovasyon La Rényon, dopi la transformasyon nimérik ek bann sosyété inkluziv ziska la tranzisyon ékolozik ek ladaptasyon fas bann sanzman global",
 "Skills": "Sak mi koné fé", "Computing": "Linformatik", "Languages": "Lang",
 "French (native), Reunionese Creole (native), English (fluent), German (basic)": "Fransé (lang maternel), kréol reyoné (lang maternel), anglé (mi koz byin), alman (in pé)",
 # ---------- teaching
 "Courses": "Kour", "Analysis 3": "Analiz 3",
 "Tutorials · Undergraduate, Université Paris-Dauphine": "TD · Lisans, Université Paris-Dauphine",
 "Introduction to probability": "Introdiksyon probabilité", "Oral examiner in mathematics": "Kolèr an matématik",
 "French preparatory classes (ECG), IPESUP, Paris": "Klas prépa (ECG), IPESUP, Paris",
 "French preparatory classes (PCSI), Lycée Assomption, Rennes": "Klas prépa (PCSI), Lycée Assomption, Rennes",
 "French agrégation 2023 · option A (probability & statistics)": "Agrégasyon ekstern 2023 · opsyon A (probabilité ek statistik)",
 "Lesson developments in analysis, probability and algebra": "Dévlopman an analiz, probabilité ek alzeb",
 "30 documents · in French": "30 dokiman · an fransé", "Personal notes": "Mon bann not", "Coming soon": "I ariv byinto",
 # ---------- footer
 "Office B225": "Biro B225", "Office B006 (V3)": "Biro B006 (V3)", "Office 00 2018 9-3/4, aile 0": "Biro 00 2018 9-3/4, aile 0",
 "Online": "Si internet", "(with ‘-’)": "(ek in tiré)",
 "Artwork: simulations of the processes studied in each paper.": "Bann imaz" + NB + ": simulasyon bann prosésis étidié dann sak artik.",
 # ---------- paper reader
 "Paper — Samuel Chan-ashing": "Artik — Samuel Chan-ashing",
 "Open on arXiv": "Ouvèr si arXiv", "HTML on arXiv": "HTML si arXiv", "Journal version": "Versyon piblié",
 "Copy citation": "Kopié la référans", "Citation copied": "Référans kopié",
 "Preprint": "Prépiblikasyon", "Submitted": "Soumi", "Published": "Piblié",
 "More by Samuel Chan-ashing": "Lézot artik",
 "This page needs JavaScript to load the paper from arXiv.": "Pou sarz lartik dopi arXiv, i fo JavaScript.",
 "Open arXiv": "Ouvèr arXiv",
 "{n} section, about {m} min of reading": "{n} seksyon, anviron {m} min lektir",
 "{n} sections, about {m} min of reading": "{n} seksyon, anviron {m} min lektir",
 "Published in {j} ({y})": "Piblié dann {j} ({y})",
 "Text:": "Teks" + NB + ":", "live from arXiv": "an direk dopi arXiv", "saved copy": "kopi gardé",
 "Mathematics Subject Classification": "Klasifikasyon matématik (MSC)",
 "Artwork: simulation for {t}": "Imaz" + NB + ": simulasyon pou {t}",
 "The HTML version could not be loaded.": "Lo versyon HTML la pa pi sarz.",
 "arXiv may not have an HTML rendering of this paper yet, or you are offline.": "Pétet arXiv néna pa ankor in versyon HTML pou lartik-la, oubien ou lé pa konekté.",
 "arXiv page": "Paz arXiv",
 # ---------- press portrait
 "Portrait in Réunionnais du Monde — Samuel Chan-ashing": "Portré dann Réunionnais du Monde — Samuel Chan-ashing",
 "Original article (French)": "Lartik orizinal (an fransé)",
 "Samuel Chan-ashing, PhD student in mathematics in Paris": "Samuel Chan-ashing, doktoran an matématik Paris",
 "Press · April 22, 2026 · in French": "Zournal · 22 avril 2026 · an fransé",
 "Read (French)": "Lir lartik",
 "#portrait-intro": ("<p><em>Réunionnais du Monde</em>, lo magazine bann Reyoné dann lo monn, la poz kestyon Samuel an avril 2026. "
                     "Vwala in pti rézimé" + NB + "; ou pé lir tout lartik si lo sit magazine-la.</p>"),
 "Roots": "Rasine",
 "Grew up in Les Avirons, on Réunion Island, with family ties in Saint-Pierre.": "Li la grandi Lé Zaviron, La Rényon, é in parti son fanmiy lé Sin-Pyèr.",
 "Studies": "Zétid",
 "Preparatory classes on the island, then ENS Rennes, where he also led the student union and widened his interests beyond mathematics.":
     "Klas prépa dann lil, apré ENS Rennes" + NB + ": la li la osi prézid lo BDE, é li la ouvèr ali pou lézot soz ke lo matématik.",
 "Towards research": "Vèr larsèrs",
 "A two-month research stay at the University of Cambridge, obtained after many unanswered applications, then a master’s year at Sorbonne Université, the agrégation and a PhD in probability in Paris.":
     "In staz arsèrs dé mwa liniversité Cambridge, li la trouv ali apré in bonpé kandidatir san répons" + NB + "; apré, in lané mastèr Sorbonne Université, lagrégasyon ek in tez an probabilité Paris.",
 "Obstacles": "Bann difikilté",
 "Being far from information and networks when coming from Réunion, impostor syndrome among overseas students, and getting used to life in Paris.":
     "Kan ou sort La Rényon, ou lé lwin bann linformasyon ek bann rézo" + NB + "; lo sindrom lenpostèr dann bann zétidyan outremèr" + NB + "; ek abitié avek la vi Paris.",
 "Recognition": "Rékonésans",
 "Laureate of the Talents de l’Outre-mer prize; he also sits on the expert committee of La Réunion Innovation.":
     "Li la gagn lo pri Talents de l’Outre-mer" + NB + "; li lé osi dann komité lekspèr La Réunion Innovation.",
 "After the thesis": "Apré la tez",
 "An interest in artificial intelligence and its geopolitical and security stakes, in industry or in public service.":
     "Lintélizans artifisyel i intérès ali, ek sak i zoué dann zéopolitik ek la sékirité, dann in lantropriz oubien dann lo servis piblik.",
 "Réunion, seen from afar": "La Rényon, vi dopi lwin",
 "Support for helping young graduates return to the island, and how living away has changed the way he sees its landscapes and Creole identity.":
     "Li vé ed bann zène diplomé rotourn dann lil, é rès lwin la sanz son manyèr gard bann péizaz ek lidantité kréol.",
 "Summary written for this site. The interview and its wording belong to Réunionnais du Monde.":
     "Rézimé ékri pou sit-la. Lartik ek son bann mo lé pou Réunionnais du Monde.",
 "reunionnaisdumonde.com · in French": "reunionnaisdumonde.com · an fransé",
 "Read the full interview": "Lir tout lartik",
 "Portrait of Samuel Chan-ashing": "Portré Samuel Chan-ashing",
 # ---------- agrégation page (its content stays in French)
 "Accueil (English)": "Kisa mi lé",
 # ---------- memoir pages
 "All research": "Tout larsèrs", "More research stays": "Lézot staz arsèrs",
 "Research stay · 2024 · ENS (DMA)": "Staz arsèrs · 2024 · ENS (DMA)",
 "Research stay · 2022 · Cambridge": "Staz arsèrs · 2022 · Cambridge",
 "Research stay · 2021 · Polytechnique": "Staz arsèrs · 2021 · Polytechnique",
 "Research seminar · 2021 · ENS Rennes": "Séminèr arsèrs · 2021 · ENS Rennes",
 "Master 2 research stay, DMA, École normale supérieure, Paris": "Staz arsèrs M2, DMA, École normale supérieure, Paris",
 "Master research stay, DPMMS, University of Cambridge": "Staz arsèrs mastèr, DPMMS, liniversité Cambridge",
 "Bachelor research stay, CMLS, École polytechnique": "Staz arsèrs lisans, CMLS, École polytechnique",
 "Directed research seminar, ENS Rennes": "Séminèr arsèrs ancadré, ENS Rennes",
 "Supervised by Djalil Chafaï · 12 weeks": "Ancadré par Djalil Chafaï · 12 smèn",
 "Supervised by Clément Mouhot · 8 weeks": "Ancadré par Clément Mouhot · 8 smèn",
 "Supervised by Samir Salem · 4 weeks": "Ancadré par Samir Salem · 4 smèn",
 "Supervised by Jérémy Martin": "Ancadré par Jérémy Martin",
 "3 sections, about 38 min of reading": "3 seksyon, anviron 38 min lektir · an anglé",
 "7 sections, about 87 min of reading": "7 seksyon, anviron 87 min lektir · an anglé",
 "5 sections, about 57 min of reading · in French": "5 seksyon, anviron 57 min lektir · an fransé",
 "4 sections, about 40 min of reading · in French": "4 seksyon, anviron 40 min lektir · an fransé",
 "Cutoff": "Cutoff", "Diffusion processes": "Prosésis difisyon", "Mixing time": "Tan mélanz",
 "Random dynamical systems": "Sistèm dinamik aléatoir", "Turbulence": "Tirbilans", "Batchelor’s law": "Lwa Batchelor", "Mixing": "Mélanz",
 "N-body problem": "Problèm N kor", "Transport equation": "Ékwasyon transpor", "Method of characteristics": "Métod bann karaktéristik",
 "Empirical measure": "Mézir anpirik", "Mean-field limit": "Limit san mwayin",
 "Fourier transform": "Transformé Fourier", "Heisenberg uncertainty principle": "Prinsip linsertitid Heisenberg",
 "Annihilating pairs": "Pèr anilant", "Thick sets": "Ansanm épé",
 "Artwork: simulation related to Cutoff for ergodic diffusions": "Imaz" + NB + ": simulasyon pou lo cutoff bann difisyon ergodik",
 "Artwork: simulation related to Turbulence & random dynamics": "Imaz" + NB + ": simulasyon pou la tirbilans",
 "Artwork: simulation related to N-body problems, large N": "Imaz" + NB + ": simulasyon pou bann problèm N kor",
 "Artwork: simulation related to Uncertainty principles": "Imaz" + NB + ": simulasyon pou bann prinsip linsertitid",
 "N-body problems when N is large — Samuel Chan-ashing": "Étude des problèmes à N corps, lorsque N est grand — Samuel Chan-ashing",
 "Uncertainty principles and the Logvinenko–Sereda theorem — Samuel Chan-ashing": "Principe d’incertitude et théorème de Logvinenko-Sereda — Samuel Chan-ashing",
 # ---------- simulation code (paper pages)
 "View the simulation code": "Get lo kod simulasyon", "Code": "Kod", "Simulation code": "Kod simulasyon",
 "Copy code": "Kopié lo kod", "Code copied": "Kod kopié", "Download .py": "Télésarz lo .py", "Close": "Ferm",
 # ---------- language menu (names stay in their own language)
 "Français": "Français", "English": "English",

 # ---------- captions under the paper covers (generated by captions.py)
 "#cap-dyson-jacobi": "Bann profil cutoff simulé pou <i>n</i> = 2 ziska 32 (β = 2, <i>a</i> = <i>b</i> = 2<i>n</i>) : distans Kolmogorov ziska léquilib <i>x</i><sub>1</sub> + ⋯ + <i>x<sub>n</sub></i>, dapré <i>t</i>/<i>c<sub>n</sub></i>.",
 "#cap-dyson-laguerre": "Bann profil cutoff simulé pou <i>n</i> = 2 ziska 256 (β = 2, α = 2<i>n</i>) : distans Kolmogorov ziska léquilib <i>x</i><sub>1</sub> + ⋯ + <i>x<sub>n</sub></i>, dapré <i>t</i>/<i>c<sub>n</sub></i>.",
 "#cap-metastable": "In simulasyon ek <i>N</i> = 80 partikil (σ = √2, <i>J</i> = √(50e)) : la moyèn ampirik i kit léquilib stab <i>m</i> ≈ 6,64 pou <i>m</i> ≈ 1,38.",
}
