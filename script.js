/* ============================================================
   CoColour Life — bilingual toggle (EN / 日本語)
   - Default DOM text is English, so English shows when JS is off.
   - Initial language: saved choice, else browser language.
   - Choice persisted in localStorage. <html lang> kept in sync.
   ============================================================ */
(function () {
  'use strict';

  var STORAGE_KEY = 'ccl_lang';
  var SUPPORTED = ['en', 'ja'];

  var nodes = document.querySelectorAll('[data-en][data-ja]');
  var buttons = document.querySelectorAll('.lang-btn');

  function normalise(lang) {
    return SUPPORTED.indexOf(lang) !== -1 ? lang : 'en';
  }

  function detectInitial() {
    var saved;
    try { saved = localStorage.getItem(STORAGE_KEY); } catch (e) { saved = null; }
    if (saved && SUPPORTED.indexOf(saved) !== -1) return saved;
    var nav = (navigator.language || navigator.userLanguage || 'en').toLowerCase();
    return nav.indexOf('ja') === 0 ? 'ja' : 'en';
  }

  function apply(lang) {
    lang = normalise(lang);

    for (var i = 0; i < nodes.length; i++) {
      var text = nodes[i].getAttribute('data-' + lang);
      if (text !== null) nodes[i].textContent = text;
    }

    document.documentElement.lang = lang;

    var META = {
      en: {
        title: 'CoColour Life \u2014 Connecting research and practice for more accessible and sustainable health and rehabilitation',
        desc: 'CoColour Life Pty Ltd is an Australian company connecting research and practice for more accessible and sustainable health and rehabilitation.'
      },
      ja: {
        title: 'CoColour Life \u2014 \u7814\u7a76\u3068\u5b9f\u8df5\u3092\u3064\u306a\u304e\u3001\u3088\u308a\u30a2\u30af\u30bb\u30b9\u3057\u3084\u3059\u304f\u6301\u7d9a\u53ef\u80fd\u306a\u4fdd\u5065\u533b\u7642\u30fb\u30ea\u30cf\u30d3\u30ea\u30c6\u30fc\u30b7\u30e7\u30f3\u3078',
        desc: 'CoColour Life Pty Ltd\u306f\u3001\u7814\u7a76\u3068\u5b9f\u8df5\u3092\u3064\u306a\u304e\u3001\u3088\u308a\u30a2\u30af\u30bb\u30b9\u3057\u3084\u3059\u304f\u6301\u7d9a\u53ef\u80fd\u306a\u4fdd\u5065\u533b\u7642\u30fb\u30ea\u30cf\u30d3\u30ea\u30c6\u30fc\u30b7\u30e7\u30f3\u306b\u8ca2\u732e\u3059\u308b\u30aa\u30fc\u30b9\u30c8\u30e9\u30ea\u30a2\u306e\u4f01\u696d\u3067\u3059\u3002'
      }
    };
    document.title = META[lang].title;
    var md = document.querySelector('meta[name="description"]');
    if (md) md.setAttribute('content', META[lang].desc);

    for (var j = 0; j < buttons.length; j++) {
      var active = buttons[j].getAttribute('data-lang') === lang;
      buttons[j].classList.toggle('is-active', active);
      buttons[j].setAttribute('aria-pressed', active ? 'true' : 'false');
    }

    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) {}
  }

  for (var k = 0; k < buttons.length; k++) {
    buttons[k].addEventListener('click', function () {
      apply(this.getAttribute('data-lang'));
    });
  }

  apply(detectInitial());
})();

/* ============================================================
   Scrollspy — the section being read lights its nav item.
   Degrades silently without IntersectionObserver or the nav.
   ============================================================ */
(function () {
  'use strict';

  var links = document.querySelectorAll('.site-nav a[href^="#"]');
  if (!links.length || !('IntersectionObserver' in window)) return;

  var sections = [];
  for (var i = 0; i < links.length; i++) {
    var id = links[i].getAttribute('href').slice(1);
    var el = document.getElementById(id);
    if (el) sections.push(el);
  }

  function setCurrent(id) {
    for (var j = 0; j < links.length; j++) {
      links[j].classList.toggle('is-current', links[j].getAttribute('href') === '#' + id);
    }
  }

  var observer = new IntersectionObserver(function (entries) {
    for (var k = 0; k < entries.length; k++) {
      if (entries[k].isIntersecting) setCurrent(entries[k].target.id);
    }
  }, { rootMargin: '-35% 0px -55% 0px' });

  for (var s = 0; s < sections.length; s++) observer.observe(sections[s]);
})();
