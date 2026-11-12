/* Shared behaviour: icons, top bar, menu, share, dock (mini player + tab bar). */
(function () {
  "use strict";

  const icon = window.SiteIcon;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const page = document.body.dataset.page || "home";

  /* ---------- Toast + share + menu */
  const toast = document.createElement("div");
  toast.className = "toast glass";
  toast.setAttribute("role", "status");
  document.body.appendChild(toast);
  let toastTimer;
  function showToast(msg) {
    toast.textContent = msg;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 1800);
  }
  async function copy(text, msg) {
    let ok = false;
    try { await navigator.clipboard.writeText(text); ok = true; } catch (e) { /* fall back below */ }
    if (!ok) {
      const ta = document.createElement("textarea");
      ta.value = text; ta.setAttribute("readonly", "");
      ta.style.cssText = "position:fixed;top:0;left:0;opacity:0;";
      document.body.appendChild(ta); ta.select();
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      ta.remove();
    }
    showToast(ok ? (msg || "Copied") : text);
  }
  async function share() {
    const url = location.href.split("#")[0];
    // the system share sheet (iPhone, Mac, Android) when available on the real site
    if (navigator.share && /^https?:$/.test(location.protocol)) {
      try { await navigator.share({ title: document.title, url }); return; }
      catch (e) { if (e && e.name === "AbortError") return; }
    }
    copy(url, "Link copied");
  }
  $$("[data-action=share]").forEach((b) => b.addEventListener("click", share));

  const menu = $(".menu");
  const menuBtn = $("[data-action=menu]");
  if (menu && menuBtn) {
    const close = () => { menu.classList.remove("open"); menuBtn.setAttribute("aria-expanded", "false"); };
    menuBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = !menu.classList.contains("open");
      menu.classList.toggle("open", open);
      menuBtn.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("click", (e) => { if (!menu.contains(e.target)) close(); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
    menu.addEventListener("click", (e) => {
      const c = e.target.closest("[data-copy]");
      if (c) { copy(c.dataset.copy === "url" ? location.href : c.dataset.copy, c.dataset.msg || "Copied"); }
      if (e.target.closest("a, button")) setTimeout(close, 120);
    });
  }

  /* ---------- Scroll state: scrolled / past hero */
  const hero = $(".hero") || $(".album-head") || $(".page-head");
  function onScrollState() {
    const y = window.scrollY;
    document.body.classList.toggle("scrolled", y > 8);
    const limit = hero ? hero.offsetTop + hero.offsetHeight - 90 : 160;
    document.body.classList.toggle("past-hero", y > limit);
  }

  /* ---------- Dock */
  const dock = $(".dock");
  const Dock = { el: dock };
  if (dock) {
    const narrow = window.matchMedia("(max-width: 699px)");
    let lastY = window.scrollY, acc = 0, quietUntil = 0;
    function setCollapsed(c) { dock.classList.toggle("collapsed", c); }
    function onScrollDock() {
      const y = window.scrollY, dy = y - lastY;
      lastY = y;
      if (!narrow.matches) { setCollapsed(false); return; }
      // scrolling triggered by a tap on a tab or an in-page link must not hide the bar
      if (Date.now() < quietUntil) { acc = 0; return; }
      if (y < 80) { setCollapsed(false); acc = 0; return; }
      acc = (Math.sign(dy) === Math.sign(acc)) ? acc + dy : dy;
      if (acc > 18) setCollapsed(true);
      else if (acc < -14) setCollapsed(false);
    }
    window.addEventListener("scroll", onScrollDock, { passive: true });
    const orbR = $(".orb-right", dock);
    if (orbR) orbR.addEventListener("click", () => setCollapsed(false));
    document.addEventListener("click", (e) => {
      const a = e.target.closest('a[href*="#"]');
      if (a && a.pathname === location.pathname) { quietUntil = Date.now() + 1600; setCollapsed(false); }
    });

    // active tab
    Dock.setActive = function (name) {
      $$(".tab", dock).forEach((t) => {
        const on = t.dataset.tab === name;
        t.classList.toggle("active", on);
        if (on) t.setAttribute("aria-current", "page"); else t.removeAttribute("aria-current");
      });
      const t = $(`.tab[data-tab="${name}"]`, dock);
      if (orbR && t) orbR.innerHTML = icon(t.dataset.icon);
    };
    Dock.setMini = function ({ art, route, title, href }) {
      const m = $(".mini", dock);
      if (!m) return;
      if (art) $(".mini-art", m).src = art;
      if (route != null) $(".mini-route", m).textContent = route;
      if (title != null) $(".mini-title", m).textContent = title;
      if (href) $(".mini-link", m).href = href;
    };
    Dock.setProgress = function (p) {
      const m = $(".mini", dock);
      if (!m) return;
      m.classList.add("has-progress");
      $(".mini-progress i", m).style.width = (Math.max(0, Math.min(1, p)) * 100).toFixed(1) + "%";
    };
    Dock.setActive(dock.dataset.active || page);
  }
  window.Dock = Dock;

  /* ---------- Home page: scroll-spy + mini player cycling through papers */
  if (page === "home" && dock) {
    const sections = $$("[data-tab-section]");
    const spy = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) Dock.setActive(e.target.dataset.tabSection); });
    }, { rootMargin: "-45% 0px -50% 0px" });
    sections.forEach((s) => spy.observe(s));

    const papers = (window.SITE && window.SITE.papers) || [];
    let k = 0;
    function showPaper(i) {
      const p = papers[i];
      if (!p) return;
      Dock.setMini({ art: p.cover, route: k === 0 ? "arXiv → Latest paper" : `arXiv → ${p.id}`, title: p.title, href: `paper.html?id=${p.id}` });
    }
    const next = $(".mini-btn.next", dock);
    if (next) next.addEventListener("click", () => { k = (k + 1) % papers.length; showPaper(k); });
    const play = $(".mini-btn.play", dock);
    if (play) play.addEventListener("click", () => { const p = papers[k]; if (p) location.href = `paper.html?id=${p.id}`; });
  }

  /* ---------- "More" buttons for clamped text */
  $$("[data-more]").forEach((btn) => {
    const target = document.getElementById(btn.dataset.more);
    if (!target) return;
    const check = () => { if (!target.classList.contains("open")) btn.hidden = target.scrollHeight <= target.clientHeight + 2; };
    btn.addEventListener("click", () => {
      const open = target.classList.toggle("open");
      btn.textContent = open ? "Less" : "More";
    });
    window.addEventListener("load", check);
    window.addEventListener("resize", check);
    check();
  });

  window.addEventListener("scroll", onScrollState, { passive: true });
  onScrollState();
})();
