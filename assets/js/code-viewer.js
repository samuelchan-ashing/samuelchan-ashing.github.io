/* Paper page: hovering the cover offers to see the Python code of the simulation that drew it; a click opens it.
   The code itself comes from assets/js/sim-code.js (generated from tools/covers/*.py by tools/covers/build_code_js.py),
   so it also works when the site is opened from a folder (file://). */
(function () {
  "use strict";
  const T = (s, v) => (window.I18N ? I18N.t(s, v) : s);
  const tr = (el) => { if (window.I18N) I18N.translate(el); };
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  /* a small Python highlighter: strings, comments, numbers, keywords, called names */
  const RE = /("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')|(#[^\n]*)|\b(\d+\.?\d*(?:e[+-]?\d+)?)\b|\b(def|return|for|in|if|else|elif|while|import|from|as|with|lambda|not|and|or|is|None|True|False|class|try|except|pass|break|continue|yield)\b|\b([A-Za-z_]\w*)(?=\()/g;
  function highlight(src) {
    let out = "", last = 0, m;
    RE.lastIndex = 0;
    while ((m = RE.exec(src))) {
      const cls = m[1] ? (/^("""|''')/.test(m[1]) ? "d" : "s") : m[2] ? "c" : m[3] ? "n" : m[4] ? "k" : "f";   // d = docstring
      out += esc(src.slice(last, m.index)) + `<span class="tok-${cls}">${esc(m[0])}</span>`;
      last = RE.lastIndex;
    }
    return out + esc(src.slice(last));
  }

  function toast(msg) {
    const t = document.querySelector(".toast"); if (!t) return;
    t.textContent = msg; t.classList.add("show");
    clearTimeout(toast.timer); toast.timer = setTimeout(() => t.classList.remove("show"), 1800);
  }
  async function copyText(text) {
    try { await navigator.clipboard.writeText(text); return true; } catch (e) { /* fall back below */ }
    const ta = document.createElement("textarea");
    ta.value = text; ta.setAttribute("readonly", ""); ta.style.cssText = "position:fixed;top:0;left:0;opacity:0;";
    document.body.appendChild(ta); ta.select();
    let ok = false; try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    ta.remove(); return ok;
  }
  function download(name, text) {
    const url = URL.createObjectURL(new Blob([text], { type: "text/x-python" }));
    const a = document.createElement("a"); a.href = url; a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }

  let dialog = null, current = null;
  function sheet() {
    if (dialog) return dialog;
    dialog = document.createElement("dialog");
    dialog.className = "code-sheet";
    dialog.setAttribute("aria-labelledby", "code-title");
    dialog.innerHTML =
      '<div class="code-head">' +
        '<div class="code-name"><div class="code-title" id="code-title">Simulation code</div><div class="code-file" data-no-i18n></div></div>' +
        '<div class="code-actions">' +
          '<button type="button" data-act="copy" aria-label="Copy code"><svg class="icon"><use href="#i-copy"/></svg></button>' +
          '<button type="button" data-act="download" aria-label="Download .py"><svg class="icon"><use href="#i-download"/></svg></button>' +
          '<button type="button" data-act="close" aria-label="Close"><svg class="icon"><use href="#i-close"/></svg></button>' +
        "</div>" +
      "</div>" +
      '<pre class="code" data-no-i18n tabindex="0"><code></code></pre>';
    document.body.appendChild(dialog);
    tr(dialog);
    dialog.addEventListener("click", async (e) => {
      if (e.target === dialog) { dialog.close(); return; }                  // click on the backdrop
      const b = e.target.closest("[data-act]"); if (!b || !current) return;
      if (b.dataset.act === "close") dialog.close();
      if (b.dataset.act === "copy") toast(T((await copyText(current.code)) ? "Code copied" : "Copied"));
      if (b.dataset.act === "download") download(current.file, current.code);
    });
    dialog.addEventListener("close", () => document.documentElement.classList.remove("sheet-open"));
    return dialog;
  }
  function open(key) {
    const item = window.SIM_CODE && SIM_CODE[key]; if (!item) return;
    current = item;
    const d = sheet();
    d.querySelector(".code-file").textContent = `${item.file} · Python`;
    d.querySelector("code").innerHTML = highlight(item.code);
    d.querySelector("pre").scrollTop = 0;
    document.documentElement.classList.add("sheet-open");
    if (d.showModal) d.showModal(); else d.setAttribute("open", "");
  }

  function attach(cover, key) {
    if (!cover || !window.SIM_CODE || !SIM_CODE[key]) return;
    const b = document.createElement("button");
    b.type = "button"; b.className = "cover-code";
    const label = () => b.setAttribute("aria-label", T("View the simulation code"));   // the element's own attribute
    label(); document.addEventListener("langchange", label);
    b.innerHTML = '<svg class="icon" aria-hidden="true"><use href="#i-code"/></svg>' +
                  '<span class="cc-long">View the simulation code</span><span class="cc-short">Code</span>';
    b.addEventListener("click", () => open(key));
    cover.appendChild(b);
    tr(b);
  }

  window.CodeViewer = { attach, open, highlight };
})();
