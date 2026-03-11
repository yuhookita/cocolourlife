/* ============================================
   CoColour Life — Coming Soon Gate
   TODO: サイト公開時にこのファイルと参照を削除すること
   ============================================ */

(function () {
  'use strict';

  var PASSWORD = 'cocolour2026';
  var STORAGE_KEY = 'ccl_preview';

  // Check if already authenticated
  if (sessionStorage.getItem(STORAGE_KEY) === 'ok') {
    showSite();
    return;
  }

  // Gate elements
  var gate = document.getElementById('coming-soon-gate');
  var toggle = document.getElementById('gate-toggle');
  var form = document.getElementById('gate-form');
  var input = document.getElementById('gate-input');
  var error = document.getElementById('gate-error');

  if (!gate) return;

  // Toggle password form
  if (toggle) {
    toggle.addEventListener('click', function () {
      form.classList.toggle('show');
      if (form.classList.contains('show')) {
        input.focus();
      }
    });
  }

  // Handle form submit
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (input.value === PASSWORD) {
        sessionStorage.setItem(STORAGE_KEY, 'ok');
        showSite();
      } else {
        error.classList.add('show');
        input.value = '';
        input.focus();
      }
    });
  }

  function showSite() {
    document.body.classList.add('ccl-unlocked');
    var gateEl = document.getElementById('coming-soon-gate');
    if (gateEl) gateEl.classList.add('hidden');
  }
})();
