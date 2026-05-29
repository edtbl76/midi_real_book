(function () {
  const toggle = document.querySelector('[data-sidebar-toggle]');
  if (toggle) {
    const isMobile = function () { return window.matchMedia('(max-width: 860px)').matches; };
    const sync = function () {
      const expanded = isMobile() ? document.body.classList.contains('sidebar-open') : !document.body.classList.contains('sidebar-collapsed');
      toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    };
    toggle.addEventListener('click', function () {
      if (isMobile()) {
        document.body.classList.toggle('sidebar-open');
      } else {
        document.body.classList.toggle('sidebar-collapsed');
      }
      sync();
    });
    document.querySelectorAll('.sidebar a').forEach(function (link) {
      link.addEventListener('click', function () {
        if (isMobile()) document.body.classList.remove('sidebar-open');
        sync();
      });
    });
    window.addEventListener('resize', sync);
    sync();
  }

  const search = document.querySelector('[data-record-search]');
  if (search) {
    const cards = Array.from(document.querySelectorAll('[data-record-card]'));
    const count = document.querySelector('[data-record-count]');
    const update = function () {
      const q = search.value.trim().toLowerCase();
      let visible = 0;
      cards.forEach(function (card) {
        const show = !q || card.textContent.toLowerCase().includes(q);
        card.hidden = !show;
        if (show) visible += 1;
      });
      if (count) count.textContent = visible + ' ensembles';
    };
    search.addEventListener('input', update);
    update();
  }
})();
