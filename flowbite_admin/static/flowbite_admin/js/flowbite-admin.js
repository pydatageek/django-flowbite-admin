document.addEventListener('DOMContentLoaded', () => {
  initSidebarDrawer();
  initSidebarAccordion();
  initUserMenu();
  initFullscreenToggle();
});

function initSidebarDrawer() {
  const sidebar = document.getElementById('logo-sidebar');
  if (!sidebar) {
    return;
  }

  const toggleButtons = document.querySelectorAll('[data-drawer-target="logo-sidebar"]');
  const overlay = document.getElementById('sidebar-backdrop');
  const smMediaQuery = window.matchMedia('(min-width: 640px)');

  const setAriaExpanded = (isExpanded) => {
    toggleButtons.forEach((button) => {
      button.setAttribute('aria-expanded', String(isExpanded));
    });
  };

  const openSidebar = () => {
    sidebar.classList.remove('sidebar-hidden');
    sidebar.classList.remove('-translate-x-full');
    if (!smMediaQuery.matches) {
      overlay?.classList.remove('hidden');
      document.body.classList.add('overflow-hidden');
    } else {
      overlay?.classList.add('hidden');
      document.body.classList.remove('overflow-hidden');
    }
    setAriaExpanded(true);
  };

  const closeSidebar = () => {
    sidebar.classList.add('sidebar-hidden');
    sidebar.classList.add('-translate-x-full');
    overlay?.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
    setAriaExpanded(false);
  };

  const toggleSidebar = () => {
    const isOpen = !sidebar.classList.contains('-translate-x-full');
    if (isOpen) {
      closeSidebar();
    } else {
      openSidebar();
    }
  };

  toggleButtons.forEach((button) => {
    button.addEventListener('click', toggleSidebar);
  });

  overlay?.addEventListener('click', closeSidebar);

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeSidebar();
    }
  });

  const handleBreakpointChange = (event) => {
    if (event.matches) {
      openSidebar();
    } else {
      closeSidebar();
    }
  };

  smMediaQuery.addEventListener('change', handleBreakpointChange);
  handleBreakpointChange(smMediaQuery);
}

function initSidebarAccordion() {
  const sidebar = document.getElementById('logo-sidebar');
  if (!sidebar) {
    return;
  }

  const smMediaQuery = window.matchMedia('(min-width: 640px)');

  sidebar.querySelectorAll('[data-sidebar-accordion-toggle]').forEach((toggle) => {
    const targetId = toggle.getAttribute('aria-controls');
    if (!targetId) {
      return;
    }
    const panel = document.getElementById(targetId);
    if (!panel) {
      return;
    }
    const arrow = toggle.querySelector('[data-sidebar-accordion-arrow]');

    const setState = (expanded) => {
      toggle.setAttribute('aria-expanded', String(expanded));
      panel.classList.toggle('hidden', !expanded);
      if (arrow) {
        arrow.classList.toggle('rotate-180', expanded);
      }
    };

    const initialExpanded = smMediaQuery.matches;
    setState(initialExpanded);

    toggle.addEventListener('click', () => {
      const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
      setState(!isExpanded);
    });

    smMediaQuery.addEventListener('change', (event) => {
      if (event.matches) {
        setState(true);
      }
    });
  });
}

function initUserMenu() {
  const button = document.getElementById('user-menu-button');
  const menu = document.getElementById('user-menu');
  if (!button || !menu) {
    return;
  }

  const arrow = button.querySelector('[data-dropdown-arrow]');

  const openMenu = () => {
    menu.classList.remove('hidden');
    button.setAttribute('aria-expanded', 'true');
    arrow?.classList.add('rotate-180');
  };

  const closeMenu = () => {
    menu.classList.add('hidden');
    button.setAttribute('aria-expanded', 'false');
    arrow?.classList.remove('rotate-180');
  };

  const toggleMenu = () => {
    if (menu.classList.contains('hidden')) {
      openMenu();
    } else {
      closeMenu();
    }
  };

  button.addEventListener('click', (event) => {
    event.preventDefault();
    toggleMenu();
  });

  document.addEventListener('click', (event) => {
    if (!menu.contains(event.target) && !button.contains(event.target)) {
      closeMenu();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeMenu();
    }
  });
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

  const updateButtonState = () => {
    const isFullscreen = Boolean(document.fullscreenElement);
    button.setAttribute('aria-pressed', String(isFullscreen));
    button.setAttribute('aria-label', isFullscreen ? labels.exit : labels.enter);
    button.classList.toggle('is-fullscreen', isFullscreen);
  };

  const toggleFullscreen = () => {
    if (document.fullscreenElement) {
      document.exitFullscreen().catch(() => {
        updateButtonState();
      });
    } else {
      document.documentElement.requestFullscreen().catch(() => {
        updateButtonState();
      });
    }
  };

  button.addEventListener('click', (event) => {
    event.preventDefault();
    toggleFullscreen();
  });

  document.addEventListener('fullscreenchange', updateButtonState);
  updateButtonState();
}
