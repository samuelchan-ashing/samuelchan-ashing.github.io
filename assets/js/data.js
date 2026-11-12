/* Papers shown in the mini player and in the paper reader (paper.html?id=...).
   status: "Published" | "Submitted" | "Preprint"; for published papers add journal, ref, year (and doi).
   To add a paper: add an entry here (newest first) and a card in index.html.
   The reader always fetches the latest HTML version from arxiv.org/html/<id>. */
window.SITE = {
  author: "Samuel Chan-ashing",
  arxivAuthorUrl: "https://arxiv.org/search/?searchtype=author&query=Chan-ashing%2C+Samuel",
  papers: [
    {
      id: "2610.13655",
      title: "Metastable confinement of particle systems near linearly stable McKean–Vlasov equilibria",
      short: "Metastable confinement near McKean–Vlasov equilibria",
      date: "2026-10-09",
      status: "Preprint",
      coauthors: "with Quentin Cormier",
      cover: "assets/img/covers/metastable.webp",
      tint: "#8a2440",
      code: "metastable",       // tools/covers/metastable.py, shown on the paper page
    },
    {
      id: "2601.20390",
      title: "On the cutoff phenomenon for Dyson–Jacobi processes",
      short: "Dyson–Jacobi processes",
      date: "2026-01-28",
      status: "Submitted",
      cover: "assets/img/covers/dyson-jacobi.webp",
      tint: "#1d6a5b",
      code: "dyson-jacobi",     // tools/covers/dyson_jacobi.py, shown on the paper page
    },
    {
      id: "2509.19798",
      title: "On the cutoff phenomenon for Dyson–Laguerre processes",
      short: "Dyson–Laguerre processes",
      date: "2025-09-24",
      status: "Published",
      year: 2026,
      journal: "Stochastic Processes and their Applications",
      journalShort: "Stoch. Process. Appl.",
      ref: "201:105054",
      doi: "",            // e.g. "10.1016/j.spa.…" — adds a "Journal" link when filled
      cover: "assets/img/covers/dyson-laguerre.webp",
      tint: "#c4587a",
      code: "dyson-laguerre",   // tools/covers/dyson_laguerre.py, shown on the paper page
    }
  ]
};
