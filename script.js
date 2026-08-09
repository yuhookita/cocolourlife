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
