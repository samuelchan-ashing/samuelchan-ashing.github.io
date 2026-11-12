/* Reading mode shared by paper.html (arXiv papers) and stays/*.html (memoirs):
   the mini player follows the current section, ⏮ / ⏭ jump between sections,
   a thin bar shows progress, and footnote marks open their note on tap. */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  function plain(el) {
    if (!el) return "";
    const c = el.cloneNode(true);
    $$(".ltx_tag, .ltx_note", c).forEach((n) => n.remove());
    $$("math", c).forEach((m) => {
      const shown = m.querySelector("semantics > :first-child");
      m.replaceWith(document.createTextNode(shown ? shown.textContent : (m.getAttribute("alttext") || "")));
    });
    return c.textContent.replace(/\s+/g, " ").trim();
  }

  // tracks from the DOM: top-level <section>s of the article
  function tracksFrom(body) {
    return $$(":scope > section", body).map((s, i) => {
      const h = s.querySelector(":scope > .ltx_title");
      const tag = h && h.querySelector(".ltx_tag");
      const num = tag ? tag.textContent.replace(/^(Appendix|Annexe)\s*/i, "").replace(/[.\s]+$/, "").trim() : "";
      const isBib = s.classList.contains("ltx_bibliography");
      return { id: s.id, num, title: plain(h) || (isBib ? "References" : `Section ${i + 1}`), isBib, el: s };
    });
  }

  // formulas that would stick out of the column (too wide, or starting late on a line)
  // get their own small horizontal scroller; as inline-blocks they also wrap to the next line
  function fitWideMath(body) {
    for (let pass = 0; pass < 3; pass++) {
      const right = body.getBoundingClientRect().right - parseFloat(getComputedStyle(body).paddingRight);
      const todo = $$("math", body).filter((m) => !m.closest(".x-scroll, .x-inline") && m.getBoundingClientRect().right > right + 1);
      if (!todo.length) break;
      todo.forEach((m) => {
        const s = document.createElement("span");
        s.className = "x-inline";
        m.parentNode.insertBefore(s, m);
        s.appendChild(m);
      });
    }
  }

  function follow(body, tracks) {
    tracks = tracks || tracksFrom(body);
    fitWideMath(body);
    body.addEventListener("click", (e) => {
      const mark = e.target.closest(".ltx_note_mark");
      if (mark) { e.preventDefault(); mark.closest(".ltx_note").classList.toggle("open"); }
    });
    if (!window.Dock || !tracks.length) return;
    let cur = 0;
    const show = (i) => {
      const tr = tracks[i];
      Dock.setMini({ route: tr.isBib ? "Reading · References" : `Reading · Section ${tr.num || i + 1}`, title: tr.title, href: `#${tr.id}` });
    };
    const spy = new IntersectionObserver((es) => {
      es.forEach((e) => {
        if (!e.isIntersecting) return;
        const i = tracks.findIndex((x) => x.el === e.target);
        if (i >= 0) { cur = i; show(i); }
      });
    }, { rootMargin: "-30% 0px -65% 0px" });
    tracks.forEach((tr) => spy.observe(tr.el));
    const go = (d) => tracks[Math.max(0, Math.min(tracks.length - 1, cur + d))].el.scrollIntoView({ behavior: "smooth", block: "start" });
    const nb = $(".dock .mini-btn.next"), pb = $(".dock .mini-btn.prev");
    if (nb) nb.addEventListener("click", () => go(1));
    if (pb) pb.addEventListener("click", () => go(-1));
    const onScroll = () => {
      const r = body.getBoundingClientRect();
      const total = r.height - innerHeight * 0.6;
      Dock.setProgress(total > 0 ? -r.top / total : 0);
    };
    addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  window.Reader = { plain, tracksFrom, follow };

  // static pages (memoirs): start right away
  const staticBody = document.querySelector(".paper[data-static]");
  if (staticBody) follow(staticBody);
})();
