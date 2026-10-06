/* Oblong Traders — interactions
   Restrained, progressive enhancement: the page is fully readable without JS. */
(() => {
  const doc = document.documentElement;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  const desktop = window.matchMedia('(min-width: 961px)');
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  doc.classList.add('js');

  // ---------- Load transition ----------
  const onLoaded = () => requestAnimationFrame(() => document.body.classList.add('is-loaded'));
  if (document.readyState === 'complete') onLoaded();
  else window.addEventListener('load', onLoaded);
  setTimeout(onLoaded, 1600); // never hold the page behind the curtain

  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // ---------- Normalise SVG paths for draw-on animations ----------
  document.querySelectorAll('.routes path, .pulses path, .chart .ln').forEach(p => p.setAttribute('pathLength', '1'));

  // ---------- Stagger masked headline lines ----------
  document.querySelectorAll('h1, h2, .cta__big').forEach(h => {
    h.querySelectorAll('.mask > span').forEach((s, i) => s.style.setProperty('--i', i));
  });

  // ---------- Reveal on scroll ----------
  const revealTargets = document.querySelectorAll(
    '.reveal, .img-reveal, h1:has(.mask), h2:has(.mask), .cta__big, .map, .layer, .crow'
  );
  if ('IntersectionObserver' in window && !reduce.matches) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        e.target.classList.add('in');
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.12 });

    // stagger siblings in lists
    document.querySelectorAll('.pillars, .why__list, .who__list, .layers, .about__list').forEach(list => {
      [...list.children].forEach((c, i) => c.style.setProperty('--d', i * 90));
    });
    revealTargets.forEach(el => io.observe(el));
  } else {
    revealTargets.forEach(el => el.classList.add('in'));
  }

  // ---------- Navigation ----------
  const nav = document.getElementById('nav');
  const toggle = nav.querySelector('.nav__toggle');
  const menu = document.getElementById('menu');

  const setMenu = open => {
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.classList.toggle('menu-open', open);
    document.body.style.overflow = open ? 'hidden' : '';
    if (open) {
      menu.hidden = false;
      requestAnimationFrame(() => menu.classList.add('is-open'));
    } else {
      menu.classList.remove('is-open');
      setTimeout(() => { if (!menu.classList.contains('is-open')) menu.hidden = true; }, 700);
    }
  };
  toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMenu(false)));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && menu.classList.contains('is-open')) { setMenu(false); toggle.focus(); } });
  desktop.addEventListener('change', e => { if (e.matches) setMenu(false); });

  // Active nav link by section in view
  const navLinks = [...document.querySelectorAll('.nav__links a')];
  const sections = navLinks.map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
  if ('IntersectionObserver' in window) {
    const so = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        navLinks.forEach(a => a.classList.toggle('is-active', a.getAttribute('href') === '#' + e.target.id));
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach(s => so.observe(s));
  }

  // ---------- Scroll-driven effects (single rAF loop) ----------
  const life = document.querySelector('.life');
  const stagesList = life && life.querySelector('.life__stages');
  const stages = stagesList ? [...stagesList.children] : [];
  const parallax = [...document.querySelectorAll('[data-speed]')];
  const darkSections = [...document.querySelectorAll('main .dark, .footer')];
  let ticking = false;

  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));

  const update = () => {
    ticking = false;
    const y = window.scrollY;
    const vh = window.innerHeight;
    nav.classList.toggle('is-scrolled', y > 24);
    const probe = nav.offsetHeight / 2;
    nav.classList.toggle('is-dark', darkSections.some(sec => {
      const r = sec.getBoundingClientRect();
      return r.top <= probe && r.bottom >= probe;
    }));

    // Lifecycle: progress through the tall sticky section
    if (stagesList) {
      let p;
      if (reduce.matches) p = 1;
      else {
        const r = life.getBoundingClientRect();
        const total = r.height - vh;
        p = clamp((-r.top + vh * 0.15) / (total * 0.85));
      }
      stagesList.style.setProperty('--p', p.toFixed(4));
      const lit = Math.round(p * (stages.length - 1));
      stages.forEach((s, i) => s.classList.toggle('is-on', p > 0.01 ? i <= lit : i === 0));
    }

    // Subtle parallax on imagery
    if (!reduce.matches && desktop.matches) {
      parallax.forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) return;
        const offset = (r.top + r.height / 2 - vh / 2) * parseFloat(el.dataset.speed);
        el.style.translate = `0 ${offset.toFixed(1)}px`;
      });
    }
  };
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } };
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  update();

  // ---------- Capabilities ----------
  const caps = [...document.querySelectorAll('.cap')];
  const frameImgs = [...document.querySelectorAll('.caps__frame img')];
  const frame = document.querySelector('.caps__frame');
  const countEl = document.querySelector('.caps__count b');
  const nameEl = document.querySelector('.caps__name');
  let current = 0;

  const activateCap = (idx, { toggleOff = false } = {}) => {
    if (idx === current && !toggleOff) return;
    if (idx === current && toggleOff) {
      // mobile accordion: allow closing the open row
      const open = caps[idx].classList.toggle('is-active');
      caps[idx].querySelector('.cap__row').setAttribute('aria-expanded', String(open));
      return;
    }
    caps.forEach((c, i) => {
      const on = i === idx;
      c.classList.toggle('is-active', on);
      c.querySelector('.cap__row').setAttribute('aria-expanded', String(on));
    });
    frameImgs.forEach((img, i) => {
      img.classList.toggle('was-active', i === current);
      img.classList.toggle('is-active', i === idx);
    });
    if (frame) {
      frame.classList.remove('pulse');
      void frame.offsetWidth;
      frame.classList.add('pulse');
    }
    if (countEl) countEl.textContent = String(idx + 1).padStart(2, '0');
    if (nameEl) nameEl.textContent = caps[idx].querySelector('.cap__t').textContent;
    current = idx;
  };

  caps.forEach((c, i) => {
    const row = c.querySelector('.cap__row');
    row.addEventListener('click', () => activateCap(i, { toggleOff: !desktop.matches }));
    row.addEventListener('focus', () => { if (desktop.matches) activateCap(i); });
    c.addEventListener('mouseenter', () => { if (desktop.matches && finePointer.matches) activateCap(i); });
  });
  if (frame) frame.classList.add('pulse');

  // ---------- Process steps ----------
  const steps = [...document.querySelectorAll('.step')];
  const numEl = document.querySelector('.process__num');
  const bar = document.querySelector('.process__bar i');
  if (steps.length && 'IntersectionObserver' in window) {
    const po = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        const i = steps.indexOf(e.target);
        steps.forEach((s, j) => s.classList.toggle('is-active', j === i));
        if (numEl) numEl.textContent = String(i + 1).padStart(2, '0');
        if (bar) bar.style.setProperty('--p', ((i + 1) / steps.length).toFixed(3));
      });
    }, { rootMargin: '-45% 0px -45% 0px' });
    steps.forEach(s => po.observe(s));
    steps[0].classList.add('is-active');
  }

  // ---------- Who we work with: image swap on hover ----------
  const whoImg = document.querySelector('.who__img img');
  const whoItems = [...document.querySelectorAll('.who__list li')];
  let swapTimer;
  whoItems.forEach(li => {
    li.addEventListener('mouseenter', () => {
      if (!whoImg || !finePointer.matches) return;
      whoItems.forEach(x => x.classList.toggle('is-active', x === li));
      const src = li.dataset.img;
      if (!src || whoImg.getAttribute('src') === src) return;
      clearTimeout(swapTimer);
      whoImg.classList.add('swap');
      swapTimer = setTimeout(() => {
        whoImg.src = src;
        whoImg.alt = '';
        whoImg.onload = () => whoImg.classList.remove('swap');
        if (whoImg.complete) whoImg.classList.remove('swap');
      }, 220);
    });
  });
})();
