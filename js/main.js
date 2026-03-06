/* ============================================
   CoColour Life — Main JavaScript
   ============================================ */

(function () {
  'use strict';

  // ========== Landing Screen ==========
  const landingScreen = document.getElementById('landing-screen');
  const landingLogo = document.getElementById('landing-logo');
  const enterBtn = document.getElementById('enter-site');
  const colourBurst = document.getElementById('colour-burst');
  const mainSite = document.getElementById('main-site');

  document.body.classList.add('landing-active');

  function enterSite(e) {
    // Calculate burst origin from click/touch
    let x = 50, y = 50;
    if (e) {
      x = (e.clientX / window.innerWidth) * 100;
      y = (e.clientY / window.innerHeight) * 100;
    }

    colourBurst.style.setProperty('--burst-x', x + '%');
    colourBurst.style.setProperty('--burst-y', y + '%');
    colourBurst.classList.add('active');

    // Start fading out landing
    setTimeout(() => {
      landingScreen.classList.add('hidden');
      mainSite.classList.add('visible');
      document.body.classList.remove('landing-active');
    }, 300);

    // Remove landing from DOM after animation
    setTimeout(() => {
      landingScreen.style.display = 'none';
    }, 1200);
  }

  landingLogo.addEventListener('click', enterSite);
  enterBtn.addEventListener('click', enterSite);

  // Also allow clicking anywhere on the landing screen
  landingScreen.addEventListener('click', function (e) {
    if (e.target === landingScreen || e.target.closest('.landing-content')) {
      enterSite(e);
    }
  });

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
      '.about-main',
      '.about-values',
      '.mission-story',
      '.mission-cards',
      '.pillar-card',
      '.research-card',
      '.global-map',
      '.global-details',
      '.workshop-feature',
      '.workshop-list',
      '.founder-portrait',
      '.founder-bio',
      '.contact-form',
      '.contact-info',
      '.research-cta'
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

  // ========== Form handling ==========
  const form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      const originalText = btn.textContent;
      btn.textContent = 'Message sent!';
      btn.style.background = 'var(--teal)';
      btn.style.color = 'var(--white)';

      setTimeout(function () {
        btn.textContent = originalText;
        btn.style.background = '';
        btn.style.color = '';
        form.reset();
      }, 2500);
    });
  }

})();
