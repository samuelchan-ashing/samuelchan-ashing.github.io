/* Icon sprite (SF Symbols-like, 24x24). Loaded first thing in <body> so <use href="#i-…"> resolves immediately. */
(function () {
  "use strict";
  const ICONS = {
    home: '<path d="M12.7 2.9a1.1 1.1 0 0 0-1.4 0L2.9 9.8a1.1 1.1 0 0 0 1.4 1.7l.6-.5v8.5c0 1 .8 1.8 1.8 1.8h3.6v-5.6c0-.5.4-.9.9-.9h1.6c.5 0 .9.4.9.9v5.6h3.6c1 0 1.8-.8 1.8-1.8V11l.6.5a1.1 1.1 0 0 0 1.4-1.7z"/>',
    grid: '<rect x="3" y="3" width="8.2" height="8.2" rx="2.3"/><rect x="12.8" y="3" width="8.2" height="8.2" rx="2.3"/><rect x="3" y="12.8" width="8.2" height="8.2" rx="2.3"/><rect x="12.8" y="12.8" width="8.2" height="8.2" rx="2.3"/>',
    news: '<path d="M4.5 5.5h12a1.5 1.5 0 0 1 1.5 1.5v11.5a2 2 0 0 0 2 2H6.5a2 2 0 0 1-2-2z" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round"/><path d="M18 9.5h1.5a1 1 0 0 1 1 1v8a2 2 0 0 1-2 2M7.5 9h7M7.5 12.3h7M7.5 15.6h4.5" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>',
    sigma: '<path d="M17.9 4.9H6.5l6.3 7.1-6.3 7.1h11.4" fill="none" stroke="currentColor" stroke-width="3.1" stroke-linecap="round" stroke-linejoin="round"/>',
    cap: '<path d="M12.5 3.6a1.3 1.3 0 0 0-1 0L1.9 8a.8.8 0 0 0 0 1.4l9.6 4.6c.3.2.7.2 1 0l7.6-3.6V16a1 1 0 1 0 2 0V9.5a.9.9 0 0 0-.5-.8z"/><path d="M5.6 13v3.6c0 1.9 2.9 3.8 6.4 3.8s6.4-1.9 6.4-3.8V13l-5.3 2.6a2.6 2.6 0 0 1-2.2 0z"/>',
    vita: '<path fill-rule="evenodd" d="M5 4h14a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3zm0 2a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1z"/><circle cx="8.6" cy="10.2" r="2.2"/><path d="M5.2 16c.4-1.8 1.8-2.8 3.4-2.8S11.6 14.2 12 16z"/><rect x="13.6" y="9" width="5" height="1.8" rx=".9"/><rect x="13.6" y="12.6" width="3.8" height="1.8" rx=".9"/>',
    books: '<rect x="2.6" y="3.5" width="4.8" height="17" rx="1.3"/><rect x="8.7" y="5.5" width="4.8" height="15" rx="1.3"/><rect x="15.6" y="4.2" width="4.8" height="16" rx="1.3" transform="rotate(-13 18 12.2)"/>',
    "chev-l": '<path d="M15.2 4.2 7.4 12l7.8 7.8" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>',
    "chev-r": '<path d="m9 4.5 7.5 7.5L9 19.5" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>',
    share: '<path d="M12 14.6V3.4M8 7.2l4-4 4 4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M8.4 10.2H7.3a2 2 0 0 0-2 2v7.4a2 2 0 0 0 2 2h9.4a2 2 0 0 0 2-2v-7.4a2 2 0 0 0-2-2h-1.1" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    moon: '<path d="M20.4 14.4a8.4 8.4 0 0 1-10.8-10.8.7.7 0 0 0-.9-.9 9.6 9.6 0 1 0 12.6 12.6.7.7 0 0 0-.9-.9z"/>',
    sun: '<circle cx="12" cy="12" r="4.3"/><path d="M12 1.9v2.3M12 19.8v2.3M1.9 12h2.3M19.8 12h2.3M4.9 4.9l1.6 1.6M17.5 17.5l1.6 1.6M4.9 19.1l1.6-1.6M17.5 6.5l1.6-1.6" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round"/>',
    dots: '<circle cx="4.8" cy="12" r="2.1"/><circle cx="12" cy="12" r="2.1"/><circle cx="19.2" cy="12" r="2.1"/>',
    play: '<path d="M7 4.6v14.8c0 .9 1 1.4 1.7 1L21 12.9c.7-.4.7-1.4 0-1.8L8.7 3.6c-.7-.5-1.7 0-1.7 1z"/>',
    fwd: '<path d="M1.8 6.4v11.2c0 .7.8 1.2 1.4.8L11.4 13v4.6c0 .7.8 1.2 1.4.8l9.2-5.6c.6-.4.6-1.2 0-1.6l-9.2-5.6c-.6-.4-1.4.1-1.4.8V11L3.2 5.6c-.6-.4-1.4.1-1.4.8z"/>',
    back: '<path transform="matrix(-1 0 0 1 24 0)" d="M1.8 6.4v11.2c0 .7.8 1.2 1.4.8L11.4 13v4.6c0 .7.8 1.2 1.4.8l9.2-5.6c.6-.4.6-1.2 0-1.6l-9.2-5.6c-.6-.4-1.4.1-1.4.8V11L3.2 5.6c-.6-.4-1.4.1-1.4.8z"/>',
    info: '<circle cx="12.4" cy="4.9" r="2"/><path d="M9.2 9.2h4.6v8.6h1.9a1.1 1.1 0 1 1 0 2.2H9a1.1 1.1 0 1 1 0-2.2h2.2v-6.4h-2a1.1 1.1 0 1 1 0-2.2z"/>',
    mail: '<rect x="2.5" y="5" width="19" height="14" rx="2.6" fill="none" stroke="currentColor" stroke-width="2"/><path d="m3.6 6.6 8.4 6.6 8.4-6.6" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>',
    check: '<path d="m5 12.5 4.5 4.5L19 7.5" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>',
    "arrow-ur": '<path d="M7 17 17 7M8.5 7H17v8.5" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/>',
    doc: '<path d="M6.5 2.5h7.2l5.3 5.3v11.7a2 2 0 0 1-2 2H6.5a2 2 0 0 1-2-2v-15a2 2 0 0 1 2-2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M13.5 2.8v5.2h5.2M8 13h8M8 16.8h5.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    link: '<path d="M10.2 13.8a4 4 0 0 0 5.7 0l3.1-3.1a4 4 0 0 0-5.7-5.7l-1.2 1.2M13.8 10.2a4 4 0 0 0-5.7 0L5 13.3A4 4 0 0 0 10.7 19l1.2-1.2" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round"/>',
    linkedin: '<g transform="translate(-0.2 -0.4) scale(0.4233)"><path d="M49.265,4.667H7.145c-2.016,0-3.651,1.596-3.651,3.563v42.613c0,1.966,1.635,3.562,3.651,3.562h42.12c2.019,0,3.654-1.597,3.654-3.562V8.23C52.919,6.262,51.283,4.667,49.265,4.667z M18.475,46.304h-7.465V23.845h7.465V46.304z M14.743,20.777h-0.05c-2.504,0-4.124-1.725-4.124-3.88c0-2.203,1.67-3.88,4.223-3.88c2.554,0,4.125,1.677,4.175,3.88C18.967,19.052,17.345,20.777,14.743,20.777z M45.394,46.304h-7.465V34.286c0-3.018-1.08-5.078-3.781-5.078c-2.062,0-3.29,1.389-3.831,2.731c-0.197,0.479-0.245,1.149-0.245,1.821v12.543h-7.465c0,0,0.098-20.354,0-22.459h7.465v3.179c0.992-1.53,2.766-3.709,6.729-3.709c4.911,0,8.594,3.211,8.594,10.11V46.304z"/></g>',
    copy: '<rect x="8" y="8" width="12.5" height="12.5" rx="2.4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M15.8 5.2A2.4 2.4 0 0 0 13.6 3.5H6A2.5 2.5 0 0 0 3.5 6v7.6c0 1 .7 1.9 1.7 2.2" fill="none" stroke="currentColor" stroke-width="2"/>',
    chi: '<path d="M4.6 6.4c2.6-.9 4.4.4 6.3 4.1l2.2 4.3c1.6 3.1 3 4 5.9 3.1" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><path d="M17.6 5.8 6.4 18.6" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>',
    papers: '<path d="M8.5 2.5h7l4 4v11a2 2 0 0 1-2 2h-9a2 2 0 0 1-2-2v-13a2 2 0 0 1 2-2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M4.5 7v12.5a2 2 0 0 0 2 2H15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M10 10.5h6M10 14h4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    list: '<circle cx="4.5" cy="6" r="1.7"/><circle cx="4.5" cy="12" r="1.7"/><circle cx="4.5" cy="18" r="1.7"/><rect x="8.5" y="5" width="13" height="2" rx="1"/><rect x="8.5" y="11" width="13" height="2" rx="1"/><rect x="8.5" y="17" width="13" height="2" rx="1"/>'
  };
  const sprite = '<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">' +
    Object.entries(ICONS).map(([k, v]) => `<symbol id="i-${k}" viewBox="0 0 24 24">${v}</symbol>`).join("") + "</svg>";
  document.body.insertAdjacentHTML("afterbegin", sprite);
  const icon = (name) => `<svg class="icon" aria-hidden="true"><use href="#i-${name}"/></svg>`;

  window.SiteIcon = icon;
})();
