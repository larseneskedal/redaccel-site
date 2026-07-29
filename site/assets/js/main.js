// Progressive enhancement only. Every piece of content is readable without this file.
(function () {
  var doc = document.documentElement;
  doc.classList.add('js');
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ----- mobile nav ----- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* ----- header: gain surface once the page scrolls ----- */
  var header = document.querySelector('.site-header');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('scrolled', window.scrollY > 8);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ----- scroll reveals (auto-tagged; skipped under reduced motion) ----- */
  if (!reduced && 'IntersectionObserver' in window) {
    var targets = document.querySelectorAll(
      'main h2, .extract, .table-wrap, .stat-strip, .card, .faq, .sources, ' +
      '.hero-grid > div, .cta-band, .audit-form, main .kicker'
    );
    var siblings = {};
    targets.forEach(function (el, i) {
      el.classList.add('reveal');
      // stagger cards within the same grid
      var parent = el.parentElement;
      if (parent && parent.classList.contains('card-grid')) {
        var key = 'g' + Array.prototype.indexOf.call(document.querySelectorAll('.card-grid'), parent);
        siblings[key] = (siblings[key] || 0) + 1;
        el.style.setProperty('--d', ((siblings[key] - 1) * 0.09) + 's');
      }
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
    targets.forEach(function (el) { io.observe(el); });
    // Safety net: nothing stays hidden even if the observer misbehaves.
    setTimeout(function () {
      targets.forEach(function (el) { el.classList.add('in'); });
    }, 6000);
  }

  /* ----- stat counters: count up when visible ----- */
  if (!reduced && 'IntersectionObserver' in window) {
    var stats = document.querySelectorAll('.stat b');
    var counterIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        counterIO.unobserve(entry.target);
        var el = entry.target;
        var m = /^([^0-9]*)(\d+)(.*)$/.exec(el.textContent.trim());
        if (!m) return;
        var prefix = m[1], target = parseInt(m[2], 10), suffix = m[3];
        var t0 = null, dur = 900;
        var step = function (ts) {
          if (!t0) t0 = ts;
          var p = Math.min((ts - t0) / dur, 1);
          var eased = 1 - Math.pow(1 - p, 3);
          el.textContent = prefix + Math.round(target * eased) + suffix;
          if (p < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      });
    }, { threshold: 0.5 });
    stats.forEach(function (el) { counterIO.observe(el); });
  }

  /* ----- cards: cursor-tracked spotlight ----- */
  document.querySelectorAll('.card').forEach(function (card) {
    card.addEventListener('pointermove', function (e) {
      var r = card.getBoundingClientRect();
      card.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100) + '%');
      card.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100) + '%');
    });
  });

  /* ----- hero: type the query, then land the answer ----- */
  var query = document.querySelector('.answer-panel .query');
  if (query && !reduced) {
    var full = query.textContent.trim();
    var body = document.querySelector('.answer-panel .answer-body');
    query.textContent = '';
    var caret = document.createElement('span');
    caret.className = 'caret';
    caret.setAttribute('aria-hidden', 'true');
    var textNode = document.createTextNode('');
    query.appendChild(textNode);
    query.appendChild(caret);
    query.setAttribute('aria-label', full);
    if (body) {
      body.style.opacity = '0';
      body.style.transition = 'opacity .6s ease';
    }
    var i = 0;
    var type = function () {
      if (i <= full.length) {
        textNode.textContent = full.slice(0, i);
        i++;
        setTimeout(type, 26 + Math.random() * 34);
      } else if (body) {
        setTimeout(function () { body.style.opacity = '1'; }, 250);
      }
    };
    setTimeout(type, 500);
  }

  /* ----- audit form ----- */
  var form = document.querySelector('.audit-form[data-endpoint]');
  if (form) {
    var status = form.querySelector('.form-status');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var btn = form.querySelector('button[type="submit"]');
      btn.disabled = true;
      btn.textContent = 'Sending…';
      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = v; });
      fetch(form.getAttribute('data-endpoint'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
        .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(function () {
          form.querySelectorAll('input, textarea').forEach(function (el) { el.value = ''; });
          status.className = 'form-status ok';
          status.textContent = 'Received. Your audit will be in your inbox within 48 hours.';
          btn.textContent = 'Request sent';
        })
        .catch(function () {
          status.className = 'form-status err';
          status.innerHTML = 'The form endpoint is not responding. Email the same details to ' +
            '<a href="mailto:contact@redaccel.com?subject=Free%20AI%20visibility%20audit">contact@redaccel.com</a> ' +
            'and we will run the audit from there.';
          btn.disabled = false;
          btn.textContent = 'Request the audit';
        });
    });
  }
})();
