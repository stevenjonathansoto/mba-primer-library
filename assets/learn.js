(() => {
  const nav = document.querySelector('.format-nav');
  const tabs = [...nav.querySelectorAll('a')];
  const panels = tabs.map(tab => document.querySelector(tab.getAttribute('href')));
  nav.setAttribute('role', 'tablist');
  tabs.forEach((tab, i) => {
    tab.setAttribute('role', 'tab');
    tab.setAttribute('aria-controls', panels[i].id);
    panels[i].setAttribute('role', 'tabpanel');
    panels[i].tabIndex = 0;
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (i + 1) % tabs.length;
      if (event.key === 'ArrowLeft') next = (i + tabs.length - 1) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next !== undefined) { event.preventDefault(); tabs[next].focus(); tabs[next].click(); }
    });
  });
  function select() {
    const hash = location.hash.slice(1);
    const current = panels.find(p => !p.hidden)?.id || 'brief';
    const active = hash.startsWith('full-') ? 'full' : panels.some(p => p.id === hash) ? hash : current;
    tabs.forEach((tab, i) => {
      const selected = panels[i].id === active;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
      panels[i].hidden = !selected;
    });
    if (hash.startsWith('source-')) {
      const evidence = document.getElementById(hash);
      if (evidence) { evidence.open = true; evidence.scrollIntoView(); }
    }
    if (hash.startsWith('full-')) document.getElementById(hash)?.scrollIntoView();
  }
  window.addEventListener('hashchange', select);
  select();
})();
