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
