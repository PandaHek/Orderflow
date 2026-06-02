/**
 * Enhances .search-row select.filter-select into hover-open custom dropdowns.
 * Native <select> is kept (hidden) so GET form submit behaviour is unchanged.
 */
(function () {
  function initFilterDropdowns() {
    document.querySelectorAll('.search-row select.filter-select').forEach((select) => {
      if (select.closest('.filter-dropdown')) return;

      const wrap = document.createElement('div');
      wrap.className = 'filter-dropdown';

      const trigger = document.createElement('button');
      trigger.type = 'button';
      trigger.className = 'filter-dropdown-trigger';
      trigger.setAttribute('aria-haspopup', 'listbox');
      trigger.setAttribute('aria-expanded', 'false');

      const label = document.createElement('span');
      label.className = 'filter-dropdown-label';

      const chevron = document.createElement('i');
      chevron.className = 'ti ti-chevron-down filter-dropdown-chevron';

      const panel = document.createElement('div');
      panel.className = 'filter-dropdown-panel';
      panel.setAttribute('role', 'listbox');

      function syncLabel() {
        const opt = select.options[select.selectedIndex];
        label.textContent = opt ? opt.textContent : '';
      }

      function setSelected(value) {
        select.value = value;
        panel.querySelectorAll('.filter-dropdown-option').forEach((btn) => {
          const on = btn.dataset.value === value;
          btn.classList.toggle('is-selected', on);
          btn.setAttribute('aria-selected', on ? 'true' : 'false');
        });
        syncLabel();
      }

      Array.from(select.options).forEach((opt) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'filter-dropdown-option';
        btn.dataset.value = opt.value;
        btn.textContent = opt.textContent;
        btn.setAttribute('role', 'option');
        if (opt.selected) {
          btn.classList.add('is-selected');
          btn.setAttribute('aria-selected', 'true');
        }
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          setSelected(opt.value);
          close();
        });
        panel.appendChild(btn);
      });

      syncLabel();
      trigger.append(label, chevron);
      wrap.append(trigger, panel);

      select.classList.add('filter-select-native');
      select.tabIndex = -1;
      select.setAttribute('aria-hidden', 'true');
      select.parentNode.insertBefore(wrap, select);
      wrap.appendChild(select);

      let closeTimer;
      let closeAnimTimer;
      const CLOSE_GRACE_MS = 120;
      const ANIM_MS = 520;

      function finishClose() {
        wrap.classList.remove('open', 'is-closing');
        trigger.setAttribute('aria-expanded', 'false');
      }

      function open() {
        clearTimeout(closeTimer);
        clearTimeout(closeAnimTimer);
        wrap.classList.remove('is-closing');
        wrap.classList.add('open');
        trigger.setAttribute('aria-expanded', 'true');
      }

      function close() {
        if (!wrap.classList.contains('open')) return;
        if (wrap.classList.contains('is-closing')) return;

        wrap.classList.add('is-closing');
        trigger.setAttribute('aria-expanded', 'false');
        void panel.offsetHeight;

        clearTimeout(closeAnimTimer);
        closeAnimTimer = setTimeout(finishClose, ANIM_MS);
      }

      wrap.addEventListener('mouseenter', open);
      wrap.addEventListener('mouseleave', () => {
        closeTimer = setTimeout(close, CLOSE_GRACE_MS);
      });

      panel.addEventListener('transitionend', (e) => {
        if (e.target !== panel || e.propertyName !== 'opacity') return;
        if (!wrap.classList.contains('is-closing')) return;
        clearTimeout(closeAnimTimer);
        finishClose();
      });

      trigger.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          wrap.classList.toggle('open');
          trigger.setAttribute('aria-expanded', wrap.classList.contains('open'));
        }
        if (e.key === 'Escape') close();
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFilterDropdowns);
  } else {
    initFilterDropdowns();
  }
})();
