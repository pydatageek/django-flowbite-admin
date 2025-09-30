(function () {
  document.addEventListener('DOMContentLoaded', function () {
    if (typeof window.initFlowbite === 'function') {
      window.initFlowbite();
    }

    initThemeToggle();
    initFullscreenToggle();
    initSidebarAccordionBreakpointSync();
    initDrawerAriaSync();
  });

  function initThemeToggle() {
    const toggle = document.querySelector('[data-theme-toggle]');
    if (!toggle) {
      return;
    }

    const icons = {
      dark: toggle.querySelector('[data-theme-toggle-icon="dark"]'),
      light: toggle.querySelector('[data-theme-toggle-icon="light"]'),
    };

    const prefersDarkMedia = window.matchMedia('(prefers-color-scheme: dark)');

    function setIcons(isDark) {
      if (icons.dark) {
        icons.dark.classList.toggle('hidden', isDark);
      }
      if (icons.light) {
        icons.light.classList.toggle('hidden', !isDark);
      }
    }

    function applyTheme(isDark, persist = true) {
      document.documentElement.classList.toggle('dark', isDark);
      toggle.setAttribute('aria-pressed', String(isDark));
      if (persist) {
        localStorage.setItem('color-theme', isDark ? 'dark' : 'light');
      }
      setIcons(isDark);
    }

    function resolvePreferredTheme() {
      const storedTheme = localStorage.getItem('color-theme');
      if (storedTheme === 'dark') {
        return true;
      }
      if (storedTheme === 'light') {
        return false;
      }
      return prefersDarkMedia.matches;
    }

    applyTheme(resolvePreferredTheme(), false);

    toggle.addEventListener('click', function (event) {
      event.preventDefault();
      const isDark = document.documentElement.classList.contains('dark');
      applyTheme(!isDark);
    });

    if (typeof prefersDarkMedia.addEventListener === 'function') {
      prefersDarkMedia.addEventListener('change', function (event) {
        if (localStorage.getItem('color-theme')) {
          return;
        }
        applyTheme(event.matches, false);
      });
    } else if (typeof prefersDarkMedia.addListener === 'function') {
      prefersDarkMedia.addListener(function (event) {
        if (localStorage.getItem('color-theme')) {
          return;
        }
        applyTheme(event.matches, false);
      });
    }
  }

  function initFullscreenToggle() {
    const button = document.querySelector('[data-action="toggle-fullscreen"]');
    if (!button) {
      return;
    }

    const labels = {
      enter: button.getAttribute('data-fullscreen-label-enter') || 'Enter fullscreen',
      exit: button.getAttribute('data-fullscreen-label-exit') || 'Exit fullscreen',
    };

    if (!document.documentElement.requestFullscreen || !document.exitFullscreen || !document.fullscreenEnabled) {
      button.setAttribute('aria-pressed', 'false');
      button.setAttribute('aria-label', labels.enter);
      button.setAttribute('disabled', 'disabled');
      button.classList.add('cursor-not-allowed', 'opacity-60');
      return;
    }

    function updateButtonState() {
      const isFullscreen = Boolean(document.fullscreenElement);
      button.setAttribute('aria-pressed', String(isFullscreen));
      button.setAttribute('aria-label', isFullscreen ? labels.exit : labels.enter);
      button.classList.toggle('is-fullscreen', isFullscreen);
    }

    function toggleFullscreen() {
      if (document.fullscreenElement) {
        document.exitFullscreen().catch(function () {
          updateButtonState();
        });
      } else {
        document.documentElement.requestFullscreen().catch(function () {
          updateButtonState();
        });
      }
    }

    button.addEventListener('click', function (event) {
      event.preventDefault();
      toggleFullscreen();
    });

    document.addEventListener('fullscreenchange', updateButtonState);
    updateButtonState();
  }

  function initSidebarAccordionBreakpointSync() {
    const accordionContainer = document.getElementById('sidebar-accordion');
    if (!accordionContainer) {
      return;
    }

    const triggers = accordionContainer.querySelectorAll('[data-accordion-target]');
    if (!triggers.length) {
      return;
    }

    const smMediaQuery = window.matchMedia('(min-width: 640px)');

    function setExpanded(trigger, expanded) {
      trigger.setAttribute('aria-expanded', String(expanded));
      const targetSelector = trigger.getAttribute('data-accordion-target');
      if (!targetSelector) {
        return;
      }
      const target = accordionContainer.querySelector(targetSelector);
      if (!target) {
        return;
      }
      target.classList.toggle('hidden', !expanded);
    }

    function expandAll() {
      triggers.forEach(function (trigger) {
        setExpanded(trigger, true);
      });
    }

    function handleBreakpointChange(event) {
      if (event.matches) {
        expandAll();
      }
    }

    if (smMediaQuery.matches) {
      expandAll();
    }

    if (typeof smMediaQuery.addEventListener === 'function') {
      smMediaQuery.addEventListener('change', handleBreakpointChange);
    } else if (typeof smMediaQuery.addListener === 'function') {
      smMediaQuery.addListener(handleBreakpointChange);
    }
  }

  function initDrawerAriaSync() {
    const drawer = document.getElementById('logo-sidebar');
    if (!drawer) {
      return;
    }

    const triggers = document.querySelectorAll('[data-drawer-toggle="logo-sidebar"], [data-drawer-target="logo-sidebar"]');
    if (!triggers.length) {
      return;
    }

    const overlay = document.getElementById('sidebar-backdrop');
    const smMediaQuery = window.matchMedia('(min-width: 640px)');

    function updateExpandedState(isExpanded) {
      triggers.forEach(function (trigger) {
        trigger.setAttribute('aria-expanded', String(isExpanded));
      });
      const shouldLockScroll = isExpanded && !smMediaQuery.matches;
      if (overlay) {
        overlay.classList.toggle('hidden', !shouldLockScroll);
      }
      document.body.classList.toggle('overflow-hidden', shouldLockScroll);
    }

    const observer = new MutationObserver(function () {
      const isExpanded = !drawer.classList.contains('-translate-x-full');
      updateExpandedState(isExpanded);
    });

    observer.observe(drawer, { attributes: true, attributeFilter: ['class'] });
    function syncForBreakpoint(event) {
      if (event.matches) {
        drawer.classList.remove('-translate-x-full');
      } else {
        drawer.classList.add('-translate-x-full');
      }
      updateExpandedState(!drawer.classList.contains('-translate-x-full'));
    }

    syncForBreakpoint(smMediaQuery);
    if (typeof smMediaQuery.addEventListener === 'function') {
      smMediaQuery.addEventListener('change', syncForBreakpoint);
    } else if (typeof smMediaQuery.addListener === 'function') {
      smMediaQuery.addListener(syncForBreakpoint);
    }

    if (overlay) {
      overlay.addEventListener('click', function (event) {
        event.preventDefault();
        drawer.classList.add('-translate-x-full');
      });
    }
  }
})();
