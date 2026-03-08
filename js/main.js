/* ============================================
   CoColour Life — Main JavaScript
   ============================================ */

(function () {
  'use strict';

  // ========== Navigation ==========
  const nav = document.getElementById('main-nav');
  const navToggle = document.getElementById('nav-toggle');
  const mobileMenu = document.getElementById('mobile-menu');

  // Scroll handling for nav
  let lastScroll = 0;
  window.addEventListener('scroll', function () {
    const scrollY = window.scrollY;

    if (scrollY > 60) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }

    lastScroll = scrollY;
  }, { passive: true });

  // Mobile menu toggle
  navToggle.addEventListener('click', function () {
    navToggle.classList.toggle('active');
    mobileMenu.classList.toggle('open');

    if (mobileMenu.classList.contains('open')) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
  });

  // Close mobile menu on link click
  document.querySelectorAll('.mobile-link').forEach(function (link) {
    link.addEventListener('click', function () {
      navToggle.classList.remove('active');
      mobileMenu.classList.remove('open');
      document.body.style.overflow = '';
    });
  });

  // ========== Scroll Reveal ==========
  function setupReveal() {
    // Add reveal class to key elements
    const revealSelectors = [
      '.section-header',
      '.about-image',
      '.about-main',
      '.about-values',
      '.mission-story',
      '.mission-cards',
      '.pillar-card',
      '.research-card',
      '.global-card',
      '.insight-card',
      '.workshop-feature',
      '.workshop-list',
      '.founder-portrait',
      '.founder-bio',
      '.contact-form',
      '.contact-info',
      '.research-cta',
      '.pub-profiles',
      '.pub-list',
      '.pub-expand-wrapper',
      '.founder-background',
      '.founder-links',
      '.founder-cta'
    ];

    revealSelectors.forEach(function (selector) {
      document.querySelectorAll(selector).forEach(function (el) {
        el.classList.add('reveal');
      });
    });

    // Add stagger reveal to grids
    const staggerSelectors = [
      '.pillars-grid',
      '.research-grid',
      '.research-stat-grid'
    ];

    staggerSelectors.forEach(function (selector) {
      document.querySelectorAll(selector).forEach(function (el) {
        el.classList.add('reveal-stagger');
        el.classList.add('reveal');
      });
    });
  }

  function handleReveal() {
    const reveals = document.querySelectorAll('.reveal');
    const windowHeight = window.innerHeight;

    reveals.forEach(function (el) {
      const elementTop = el.getBoundingClientRect().top;
      const revealPoint = windowHeight * 0.88;

      if (elementTop < revealPoint) {
        el.classList.add('revealed');
      }
    });
  }

  setupReveal();

  window.addEventListener('scroll', handleReveal, { passive: true });
  // Initial check
  setTimeout(handleReveal, 100);

  // ========== Cursor Glow (Desktop) ==========
  if (window.matchMedia('(pointer: fine)').matches) {
    const glow = document.createElement('div');
    glow.className = 'cursor-glow';
    document.body.appendChild(glow);

    let rafId = null;
    document.addEventListener('mousemove', function (e) {
      if (rafId) cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(function () {
        glow.style.left = e.clientX + 'px';
        glow.style.top = e.clientY + 'px';
        glow.classList.add('active');
      });
    });

    document.addEventListener('mouseleave', function () {
      glow.classList.remove('active');
    });
  }

  // ========== Smooth scroll for anchor links ==========
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href === '#') return;

      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        const offset = 80;
        const top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top: top, behavior: 'smooth' });
      }
    });
  });

  // ========== Publications expand/collapse ==========
  var pubExpandBtn = document.getElementById('pub-expand-btn');
  var pubExtra = document.getElementById('pub-extra');
  if (pubExpandBtn && pubExtra) {
    pubExpandBtn.addEventListener('click', function () {
      var isExpanded = pubExpandBtn.getAttribute('aria-expanded') === 'true';

      if (isExpanded) {
        pubExtra.classList.add('pub-hidden');
        pubExtra.classList.remove('pub-visible');
        pubExpandBtn.textContent = 'View all publications →';
        pubExpandBtn.setAttribute('aria-expanded', 'false');
      } else {
        pubExtra.classList.remove('pub-hidden');
        pubExtra.classList.add('pub-visible');
        pubExpandBtn.textContent = 'Show fewer publications ←';
        pubExpandBtn.setAttribute('aria-expanded', 'true');
      }
    });
  }

  // ========== Form handling (Formspree AJAX) ==========
  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var btn = form.querySelector('button[type="submit"]');
      var originalText = btn.textContent;
      btn.textContent = 'Sending...';
      btn.disabled = true;

      var data = {
        name: form.querySelector('[name="name"]').value,
        email: form.querySelector('[name="email"]').value,
        interest: form.querySelector('[name="interest"]').value,
        message: form.querySelector('[name="message"]').value
      };

      fetch(form.action, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      }).then(function (response) {
        if (response.ok) {
          btn.textContent = 'Message sent!';
          btn.style.background = 'var(--teal)';
          btn.style.color = 'var(--white)';
          form.reset();
        } else {
          return response.json().then(function (json) {
            var msg = (json.errors && json.errors.length)
              ? json.errors.map(function (err) { return err.message; }).join(', ')
              : 'Something went wrong';
            btn.textContent = msg;
            btn.style.background = 'var(--red)';
            btn.style.color = 'var(--white)';
          });
        }
      }).catch(function () {
        btn.textContent = 'Connection error';
        btn.style.background = 'var(--red)';
        btn.style.color = 'var(--white)';
      }).finally(function () {
        setTimeout(function () {
          btn.textContent = originalText;
          btn.style.background = '';
          btn.style.color = '';
          btn.disabled = false;
        }, 3000);
      });
    });
  }

})();
