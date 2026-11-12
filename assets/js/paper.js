/* Paper reader: fetches the latest HTML version of a paper from arXiv
   (https://arxiv.org/html/<id>, which allows cross-origin reads), falls back to
   a local copy in papers/<id>.html (made by tools/update_papers.py), and
   re-renders it in the site's design: album-style header, sections as a
   track list, then the full text with MathML. */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const icon = window.SiteIcon;
  const SITE = window.SITE || { papers: [] };

  const params = new URLSearchParams(location.search);
  const id = (params.get("id") || "").trim();
  if (!/^\d{4}\.\d{4,5}(v\d+)?$/.test(id) && !/^[a-z\-]+(\.[A-Z]{2})?\/\d{7}(v\d+)?$/.test(id)) {
    location.replace("index.html#research");
    return;
  }
  const baseId = id.replace(/v\d+$/, "");
  const meta = SITE.papers.find((p) => p.id === baseId) || { id: baseId, title: "", cover: "assets/img/covers/dyson-laguerre.webp" };

  const ABS = `https://arxiv.org/abs/${id}`;
  const PDF = `https://arxiv.org/pdf/${id}`;
  const HTML = `https://arxiv.org/html/${id}`;
  const SOURCES = [
    { url: HTML, label: "live from arXiv" },
    { url: `papers/${baseId}.html`, label: "saved copy" }
  ];

  /* ---------- Immediate header from local data */
  const fmtDate = (d) => new Date(d + "T12:00:00").toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
  if (meta.tint) document.documentElement.style.setProperty("--tint", meta.tint);
  $("#cover").src = meta.cover;
  $("#cover").alt = "Artwork: simulation for " + (meta.title || id);
  setTitle(meta.title || `arXiv:${id}`);
  const status = meta.status || "Preprint";
  const pubYear = meta.year ? String(meta.year) : (meta.date ? meta.date.slice(0, 4) : "");
  $("#meta").textContent = [status, pubYear, "arXiv"].filter(Boolean).join(" · ");
  if (meta.journal) {
    const doiUrl = meta.doi ? `https://doi.org/${meta.doi}` : "";
    const jtxt = `<em>${esc(meta.journal)}</em>${meta.ref ? ", " + esc(meta.ref) : ""}`;
    $("#journal").innerHTML = doiUrl ? `<a href="${doiUrl}" target="_blank" rel="noopener">${jtxt}</a>` : jtxt;
    $("#journal").hidden = false;
    if (doiUrl) { $("#m-doi").href = doiUrl; $("#m-doi").hidden = false; }
  }
  $("#pdf-btn").href = PDF;
  $("#m-abs").href = ABS; $("#m-pdf").href = PDF; $("#m-html").href = HTML;
  if (window.Dock) Dock.setMini({ art: meta.cover, route: "arXiv → Reading", title: meta.title || id, href: "#paper-body" });

  function setTitle(t) {
    $("#title").textContent = t;
    $("#bar-title").textContent = t;
    document.title = `${t} — Samuel Chan-ashing`;
  }

  /* ---------- More by (other papers) */
  const others = SITE.papers.filter((p) => p.id !== baseId);
  if (others.length) {
    $("#more-list").innerHTML = others.map((p) => `
      <li class="card"><a href="paper.html?id=${p.id}" title="${esc(p.title)}">
        <div class="art"><img src="${p.cover}" alt="" width="800" height="800" loading="lazy"><span class="badge">arXiv</span></div>
        <div class="card-title">${esc(p.short || p.title)}</div>
        <div class="card-sub">${p.year || (p.date ? p.date.slice(0, 4) : "")} · ${esc(p.journalShort || p.status || "Preprint")}</div></a></li>`).join("");
    $("#more-by").hidden = false;
  }

  function esc(s) { return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }

  /* ---------- Fetch */
  async function fetchFirst() {
    let lastErr;
    for (const src of SOURCES) {
      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), 20000);
      try {
        const r = await fetch(src.url, { signal: ctrl.signal });
        clearTimeout(timer);
        if (!r.ok) { lastErr = new Error(`${src.url}: HTTP ${r.status}`); continue; }
        const text = await r.text();
        if (!text.includes("ltx_document")) { lastErr = new Error(`${src.url}: no LaTeXML document`); continue; }
        return { text, src };
      } catch (e) { clearTimeout(timer); lastErr = e; }
    }
    throw lastErr || new Error("No source available");
  }

  /* ---------- Clean & adapt arXiv's LaTeXML HTML */
  function sanitize(root, base) {
    $$("script, style, link, iframe, object, embed, form, input, textarea, select, button, dialog, meta", root).forEach((n) => n.remove());
    for (const el of $$("*", root)) {
      for (const a of [...el.attributes]) {
        const n = a.name.toLowerCase();
        if (n.startsWith("on") || n === "srcdoc") el.removeAttribute(a.name);
        else if ((n === "href" || n === "src" || n === "xlink:href") && /^\s*javascript:/i.test(a.value)) el.removeAttribute(a.name);
      }
    }
    $$("img[src]", root).forEach((img) => {
      const s = img.getAttribute("src");
      if (!/^(https?:|data:)/.test(s)) img.src = new URL(s, base).href;
      img.loading = "lazy"; img.decoding = "async";
      img.removeAttribute("width"); img.removeAttribute("height");
    });
    $$("a[href]", root).forEach((a) => {
      const h = a.getAttribute("href");
      if (h.startsWith("#")) return;
      if (!/^(https?:|mailto:)/.test(h)) a.href = new URL(h, base).href;
      a.target = "_blank"; a.rel = "noopener";
    });
    // wide content scrolls sideways instead of breaking the page
    $$("table.ltx_equation, table.ltx_equationgroup, table.ltx_eqn_table, .ltx_tabular, math[display=block]", root).forEach((t) => {
      if (t.closest(".x-scroll")) return;
      if (t.tagName.toLowerCase() === "math" && t.closest("table")) return;
      const w = document.createElement("div");
      w.className = "x-scroll";
      t.parentNode.insertBefore(w, t);
      w.appendChild(t);
    });
  }

  // plain text (math rendered as its visible characters, e.g. "β=1")
  function textOf(el, drop = ".ltx_tag, .ltx_note") {
    if (!el) return "";
    const c = el.cloneNode(true);
    $$(drop, c).forEach((n) => n.remove());
    $$("math", c).forEach((m) => {
      const shown = m.querySelector("semantics > :first-child");
      m.replaceWith(document.createTextNode(shown ? shown.textContent : (m.getAttribute("alttext") || "")));
    });
    return c.textContent.replace(/\s+/g, " ").trim();
  }
  // inline HTML (keeps MathML) for titles shown on the page
  function htmlOf(el, drop = ".ltx_tag, .ltx_note") {
    if (!el) return "";
    const c = el.cloneNode(true);
    $$(drop, c).forEach((n) => n.remove());
    $$("[id]", c).forEach((n) => n.removeAttribute("id"));
    $$("a", c).forEach((a) => a.replaceWith(...a.childNodes));
    return c.innerHTML.trim();
  }
  // words outside math, plus a little for each formula
  function readingMinutes(root) {
    let words = 0, formulas = 0;
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT, {
      acceptNode: (n) => n.nodeType === 1 && n.localName === "math" ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT
    });
    for (let n = w.nextNode(); n; n = w.nextNode()) if (n.nodeType === 3) words += (n.nodeValue.match(/\S+/g) || []).length;
    $$("math", root).forEach((m) => { formulas += m.getAttribute("display") === "block" ? 6 : 1; });
    return Math.max(1, Math.round((words + formulas * 2) / 200));
  }

  function render(doc, src) {
    const art = doc.querySelector("article.ltx_document");
    if (!art) throw new Error("Unexpected document structure");

    // version info: "arXiv:2601.20390v1 [math.PR] 28 Jan 2026"
    const wm = doc.querySelector("#watermark-tr");
    const m = wm && wm.textContent.match(/arXiv:(\S+?)(v\d+)\s*\[([^\]]+)\]\s*(.+)/);
    const version = m ? m[2] : (id.match(/v\d+$/) || [""])[0];
    const category = m ? m[3] : "";
    const vdate = m ? m[4].trim() : "";
    // arXiv's relative links (e.g. "2610.13655v1/figure.png") resolve against the page URL itself
    const base = HTML;

    sanitize(art, base);

    // ---- header
    const titleEl = art.querySelector(".ltx_title_document");
    const t = textOf(titleEl);
    if (t) { setTitle(t); if (titleEl.querySelector("math")) $("#title").innerHTML = htmlOf(titleEl); }
    const authors = $$(".ltx_personname", art).map((p) => textOf(p)).filter(Boolean);
    if (authors.length) $("#authors").textContent = authors.join(", ");
    const year = pubYear || (vdate.match(/\d{4}/) || [""])[0];
    $("#meta").textContent = [status, year, category].filter(Boolean).join(" · ");

    const abs = art.querySelector(".ltx_abstract");
    if (abs) {
      const box = $("#abstract");
      box.innerHTML = "";
      $$(".ltx_p, p", abs).forEach((p) => box.appendChild(document.importNode(p, true)));
      if (!box.children.length) box.textContent = textOf(abs);
    } else {
      $("#abstract").remove();
    }

    const kw = art.querySelector(".ltx_keywords");
    if (kw) {
      const words = textOf(kw, ".ltx_title, .ltx_note").split(/[;,]\s*/).map((w) => w.replace(/[.;,]$/, "").trim()).filter(Boolean);
      $("#keywords").innerHTML = words.map((w) => `<li class="chip">${esc(w)}</li>`).join("");
    }

    // ---- body: everything except the front matter rendered above
    const skip = ".ltx_title_document, .ltx_authors, .ltx_dates, .ltx_abstract, .ltx_keywords, .ltx_classification, nav.ltx_TOC";
    const body = $("#paper-body");
    body.innerHTML = "";
    for (const child of [...art.children]) {
      if (child.matches(skip)) continue;
      body.appendChild(document.importNode(child, true));
    }
    const msc = art.querySelector(".ltx_classification");
    if (msc) {
      const p = document.createElement("p");
      p.className = "paper-msc";
      p.textContent = textOf(msc, ".ltx_note");
      body.appendChild(p);
    }

    // "1. " -> "1" in section labels (the label is styled as a kicker above the title)
    $$(".ltx_title_section > .ltx_tag, .ltx_title_appendix > .ltx_tag", body).forEach((t) => { t.textContent = t.textContent.replace(/[.\s]+$/, ""); });

    // ---- track list from the top-level sections
    const secs = $$(":scope > section", body);
    const tracks = secs.map((s) => {
      const h = s.querySelector(":scope > .ltx_title");
      const tag = h && h.querySelector(".ltx_tag");
      let num = tag ? tag.textContent.replace(/^(Appendix|Annexe)\s*/i, "").replace(/[.\s]+$/, "").trim() : "";
      const isBib = s.classList.contains("ltx_bibliography");
      const title = isBib ? (textOf(h) || "References") : (textOf(h) || "Untitled");
      const titleHTML = h ? htmlOf(h) : esc(title);
      const subs = $$(":scope > section > .ltx_title", s).map((x) => textOf(x)).filter(Boolean);
      return { id: s.id, num, title, titleHTML, subs, isBib, el: s };
    });
    const mins = readingMinutes(body);

    $("#tracks").innerHTML = tracks.map((tr) => `
      <li class="row"><a href="#${esc(tr.id)}">
        <span class="row-lead num">${tr.isBib ? icon("list") : esc(tr.num)}</span>
        <span class="row-body"><span class="row-title">${tr.titleHTML || esc(tr.title)}</span>${tr.subs.length ? `<span class="row-sub one">${esc(tr.subs.join(" · "))}</span>` : ""}</span>
        <span class="row-trail dots">${icon("dots")}</span></a></li>`).join("");

    const nSec = tracks.filter((x) => !x.isBib).length;
    $("#foot").innerHTML = [
      meta.journal ? `Published in ${esc(meta.journal)}${meta.ref ? " " + esc(meta.ref) : ""} (${esc(year)})` : "",
      `${nSec} section${nSec > 1 ? "s" : ""}, about ${mins} min of reading`,
      `Text: arXiv:${esc(baseId)}${esc(version)}${vdate ? " · " + esc(vdate) : (meta.date ? " · " + esc(fmtDate(meta.date)) : "")} · <span class="src">${esc(src.label)}</span>`
    ].filter(Boolean).map((l) => `<span>${l}</span>`).join("");

    // citation to copy
    $("#m-cite").dataset.copy = meta.journal
      ? `${authors.join(", ") || "S. Chan-ashing"}. ${t || meta.title}. ${meta.journal}${meta.ref ? ", " + meta.ref : ""} (${year}). arXiv:${baseId}.`
      : `${authors.join(", ") || "S. Chan-ashing"}. ${t || meta.title}. Preprint, arXiv:${baseId} (${year}).`;

    setupReading(tracks);
  }

  /* ---------- Reading mode (shared with the memoir pages) */
  function setupReading(tracks) {
    if (window.Reader) Reader.follow($("#paper-body"), tracks);
  }

  function showError(err) {
    console.warn("Paper load failed:", err);
    $("#tracks").innerHTML = "";
    $("#abstract").remove();
    const box = $("#error");
    box.hidden = false;
    box.innerHTML = `
      <p><strong>The HTML version could not be loaded.</strong><br>arXiv may not have an HTML rendering of this paper yet, or you are offline.</p>
      <div class="album-actions">
        <a class="cta" href="${ABS}" target="_blank" rel="noopener">${icon("arrow-ur")} arXiv page</a>
        <a class="cta" href="${PDF}" target="_blank" rel="noopener">${icon("doc")} PDF</a>
      </div>`;
  }

  fetchFirst()
    .then(({ text, src }) => {
      const doc = new DOMParser().parseFromString(text, "text/html");
      render(doc, src);
      if (location.hash) { const t = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (t) t.scrollIntoView(); }
    })
    .catch(showError);
})();
