// Progressive enhancement only. Every page reads fine without this file.
(function () {
  var doc = document.documentElement;
  doc.classList.add('js');
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ----- mobile nav ----- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.site-nav');
  var setNav = function (open) {
    nav.classList.toggle('open', open);
    doc.classList.toggle('nav-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  };
  if (toggle && nav) {
    toggle.addEventListener('click', function () { setNav(!nav.classList.contains('open')); });
  }

  /* ----- "Learn" disclosure menu ----- */
  var menu = document.querySelector('.nav-menu');
  var menuBtn = menu && menu.querySelector('.nav-menu-btn');
  var setMenu = function (open) {
    menu.classList.toggle('open', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  };
  if (menuBtn) {
    menuBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      setMenu(!menu.classList.contains('open'));
    });
    document.addEventListener('click', function (e) {
      if (!menu.contains(e.target)) setMenu(false);
    });
    menu.addEventListener('focusout', function (e) {
      if (window.innerWidth >= 1024 && !menu.contains(e.relatedTarget)) setMenu(false);
    });
  }
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (menu && menu.classList.contains('open')) { setMenu(false); menuBtn.focus(); }
    if (nav && nav.classList.contains('open')) { setNav(false); toggle.focus(); }
  });

  /* ----- header: hairline once the page scrolls ----- */
  var header = document.querySelector('.site-header');
  if (header) {
    var onScroll = function () { header.classList.toggle('scrolled', window.scrollY > 4); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ----- scroll reveals (skipped under reduced motion) ----- */
  if (!reduced && 'IntersectionObserver' in window) {
    var targets = document.querySelectorAll(
      '.section-head, .stats, .card, .case, .plan, .steps > li, .post, .deliverables, .surface, ' +
      '.nots > li, .split > *, .faq-list, .cta-panel, .price-callout, .chips'
    );
    var counts = [];
    var parents = [];
    // Read every position first, then write classes, so the browser lays out once.
    var fold = window.innerHeight * 0.9;
    var below = Array.prototype.filter.call(targets, function (el) {
      return el.getBoundingClientRect().top >= fold; // skip what is already on screen
    });
    below.forEach(function (el) {
      el.classList.add('reveal');
      var i = parents.indexOf(el.parentElement);
      if (i < 0) { parents.push(el.parentElement); counts.push(0); i = parents.length - 1; }
      if (counts[i]) el.style.setProperty('--d', Math.min(counts[i] * 0.07, 0.35) + 's');
      counts[i]++;
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add('in'); io.unobserve(entry.target); }
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.05 });
    document.querySelectorAll('.reveal').forEach(function (el) { io.observe(el); });
    setTimeout(function () {
      document.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('in'); });
    }, 5000);
  }

  /* ----- hero audit card: results land one by one ----- */
  var mock = document.querySelector('.mock');
  if (mock && !reduced) {
    mock.querySelectorAll('.mk, .mock-sources li').forEach(function (el, i) {
      el.style.setProperty('--d', (0.25 + i * 0.09) + 's');
    });
    mock.classList.add('pending');
    requestAnimationFrame(function () {
      setTimeout(function () { mock.classList.remove('pending'); }, 150);
    });
  }

  /* ----- article pages: reading progress + on-this-page nav ----- */
  var article = document.querySelector('main.article');
  if (article) {
    var bar = document.createElement('div');
    bar.className = 'progress-bar';
    bar.setAttribute('aria-hidden', 'true');
    document.body.appendChild(bar);
    var ticking = false;
    var onProgress = function () {
      var max = doc.scrollHeight - window.innerHeight;
      bar.style.transform = 'scaleX(' + (max > 0 ? Math.min(window.scrollY / max, 1) : 0) + ')';
      ticking = false;
    };
    onProgress();
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(onProgress); }
    }, { passive: true });

    var heads = Array.prototype.filter.call(
      article.querySelectorAll('.shell > h2'),
      function (h) { return !h.closest('.sources') && !h.closest('.cta-panel'); }
    );
    if (heads.length > 2) {
      var toc = document.createElement('nav');
      toc.className = 'toc';
      toc.setAttribute('aria-label', 'On this page');
      var title = document.createElement('h2');
      title.textContent = 'On this page';
      var list = document.createElement('ul');
      heads.forEach(function (h, i) {
        if (!h.id) h.id = 'sec-' + (i + 1);
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.href = '#' + h.id;
        a.textContent = h.textContent;
        li.appendChild(a);
        list.appendChild(li);
      });
      toc.appendChild(title);
      toc.appendChild(list);
      document.body.appendChild(toc);
      if ('IntersectionObserver' in window) {
        var spy = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            toc.querySelectorAll('a').forEach(function (a) {
              a.classList.toggle('active', a.getAttribute('href') === '#' + entry.target.id);
            });
          });
        }, { rootMargin: '-15% 0px -70% 0px' });
        heads.forEach(function (h) { spy.observe(h); });
      }
    }
  }

  /* ----- citation links: open the sources panel before jumping ----- */
  document.querySelectorAll('sup.cite a').forEach(function (a) {
    a.addEventListener('click', function () {
      var d = document.querySelector('details.sources');
      if (d) d.setAttribute('open', '');
    });
  });

  /* ----- website field: accept a bare domain, return a full https URL or '' ----- */
  function normaliseSite(raw) {
    var v = String(raw || '').trim();
    if (!v || /\s/.test(v)) return '';
    if (!/^[a-z][a-z0-9+.-]*:\/\//i.test(v)) v = 'https://' + v.replace(/^\/+/, '');
    var m = v.match(/^(https?):\/\/([^\/?#]+)([^]*)$/i);
    if (!m) return '';
    var host = m[2].toLowerCase().replace(/:\d+$/, '');
    if (!/^([a-z0-9]([a-z0-9-]*[a-z0-9])?\.)+[a-z0-9-]{2,}$/.test(host)) return '';
    return m[1].toLowerCase() + '://' + host + m[3];
  }

  /* ----- audit form: JSON POST to the same endpoint as before ----- */
  var form = document.querySelector('.audit-form[data-endpoint]');
  if (form) {
    var status = form.querySelector('.form-status');
    var btn = form.querySelector('button[type="submit"]');
    var label = btn.textContent;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      btn.disabled = true;
      btn.textContent = 'Sending…';
      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = v; });
      var web = form.querySelector('[name="website"]');
      if (web) {
        var norm = normaliseSite(web.value);
        if (!norm) {
          status.className = 'form-status err';
          status.textContent = 'Enter your website like yourcompany.com';
          web.focus();
          return;
        }
        web.value = norm;
        data.website = norm;
      }
      fetch(form.getAttribute('data-endpoint'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
        .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(function () {
          form.querySelectorAll('input').forEach(function (el) { el.value = ''; });
          status.className = 'form-status ok';
          status.textContent = 'Received. Your audit will be in your inbox within 48 hours.';
          btn.textContent = 'Request sent';
        })
        .catch(function () {
          status.className = 'form-status err';
          status.innerHTML = 'The form is not responding right now. Email the same details to ' +
            '<a href="mailto:contact@redaccel.com?subject=Free%20AI%20visibility%20audit">contact@redaccel.com</a> ' +
            'and we will run the audit from there.';
          btn.disabled = false;
          btn.textContent = label;
        });
    });
  }
})();
