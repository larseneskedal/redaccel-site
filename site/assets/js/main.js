// Progressive enhancement only. All content is readable without this file.
(function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

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
