(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn, { once: true });
    } else {
      fn();
    }
  }

  function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split('; ') : [];
    for (let i = 0; i < cookies.length; i += 1) {
      const cookie = cookies[i];
      if (!cookie.startsWith(name + '=')) {
        continue;
      }
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
    return null;
  }

  function initialiseCharts(container) {
    if (typeof window.Chart === 'undefined') {
      return;
    }

    const script = document.getElementById('dashboard-chart-data');
    const config = script ? JSON.parse(script.textContent || '{}') : {};

    container.querySelectorAll('canvas[data-chart-key]').forEach((canvas) => {
      const key = canvas.dataset.chartKey;
      const dataset = config[key];
      if (!dataset) {
        return;
      }

      const context = canvas.getContext('2d');
      if (!context) {
        return;
      }

      new window.Chart(context, {
        type: 'line',
        data: {
          labels: dataset.labels,
          datasets: dataset.datasets,
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: true,
              labels: {
                color: getComputedStyle(document.documentElement).getPropertyValue('--color-gray-700') || '#374151',
              },
            },
          },
          scales: {
            x: {
              ticks: {
                color: 'rgba(107, 114, 128, 1)',
              },
              grid: {
                color: 'rgba(226, 232, 240, 0.4)',
              },
            },
            y: {
              beginAtZero: true,
              ticks: {
                precision: 0,
                color: 'rgba(107, 114, 128, 1)',
              },
              grid: {
                color: 'rgba(226, 232, 240, 0.35)',
              },
            },
          },
        },
      });
    });

    if (script) {
      script.remove();
    }
  }

  function initialiseWidgetManagement(grid) {
    const canEdit = grid.dataset.dashboardCanEdit === 'true';
    if (!canEdit) {
      return;
    }

    const toggleButton = document.querySelector('[data-dashboard-action="toggle"]');
    const resetButton = document.querySelector('[data-dashboard-action="reset"]');
    const toggleLabel = toggleButton ? toggleButton.querySelector('[data-dashboard-toggle-label]') : null;
    const saveUrl = grid.dataset.dashboardSaveUrl;
    const csrftoken = getCookie('csrftoken');
    let editing = false;
    let dragSource = null;

    function setEditing(state) {
      editing = state;
      grid.dataset.dashboardEditing = state ? 'true' : 'false';
      grid.querySelectorAll('[data-widget-id]').forEach((widget) => {
        widget.setAttribute('draggable', state ? 'true' : 'false');
      });

      if (toggleButton && toggleLabel) {
        const defaultLabel = toggleButton.getAttribute('data-label-default') || 'Manage layout';
        const activeLabel = toggleButton.getAttribute('data-label-active') || 'Done arranging';
        toggleLabel.textContent = state ? activeLabel : defaultLabel;
        toggleButton.setAttribute('aria-pressed', state ? 'true' : 'false');
      }

      if (resetButton) {
        resetButton.classList.toggle('hidden', !state);
      }
    }

    function currentLayout() {
      return Array.from(grid.querySelectorAll('[data-widget-id]')).map((el) => el.dataset.widgetId);
    }

    function saveLayout(layout) {
      if (!saveUrl) {
        return;
      }

      window.fetch(saveUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken || '',
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify({ widget_order: layout }),
      }).catch(() => {
        // Silently ignore network errors – the layout just won't persist.
      });
    }

    function resetLayout() {
      if (!saveUrl) {
        return;
      }

      window.fetch(saveUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken || '',
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify({ action: 'reset' }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (!data || !Array.isArray(data.layout)) {
            return;
          }
          const fragment = document.createDocumentFragment();
          data.layout.forEach((widgetId) => {
            const widget = grid.querySelector('[data-widget-id="' + widgetId + '"]');
            if (widget) {
              fragment.appendChild(widget);
            }
          });
          grid.appendChild(fragment);
        })
        .catch(() => {});
    }

    function handleDragStart(event) {
      if (!editing) {
        event.preventDefault();
        return;
      }
      dragSource = event.currentTarget;
      dragSource.dataset.dragging = 'true';
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/plain', dragSource.dataset.widgetId);
    }

    function handleDragEnter(event) {
      event.preventDefault();
    }

    function handleDragOver(event) {
      if (!editing || !dragSource) {
        return;
      }
      event.preventDefault();
      const target = event.currentTarget;
      if (dragSource === target) {
        return;
      }

      const bounding = target.getBoundingClientRect();
      const offset = event.clientY - bounding.top;
      const shouldInsertBefore = offset < bounding.height / 2;

      if (shouldInsertBefore) {
        grid.insertBefore(dragSource, target);
      } else {
        grid.insertBefore(dragSource, target.nextSibling);
      }
    }

    function handleDrop(event) {
      if (!editing) {
        return;
      }
      event.preventDefault();
      dragSource = null;
      grid.querySelectorAll('[data-widget-id]').forEach((widget) => {
        widget.removeAttribute('data-dragging');
      });
      saveLayout(currentLayout());
    }

    function handleDragEnd(event) {
      event.currentTarget.removeAttribute('data-dragging');
      dragSource = null;
    }

    grid.querySelectorAll('[data-widget-id]').forEach((widget) => {
      widget.addEventListener('dragstart', handleDragStart);
      widget.addEventListener('dragenter', handleDragEnter);
      widget.addEventListener('dragover', handleDragOver);
      widget.addEventListener('drop', handleDrop);
      widget.addEventListener('dragend', handleDragEnd);
    });

    if (toggleButton) {
      toggleButton.addEventListener('click', () => {
        setEditing(!editing);
      });
    }

    if (resetButton) {
      resetButton.addEventListener('click', () => {
        resetLayout();
      });
    }

    document.addEventListener('keyup', (event) => {
      if (event.key === 'Escape' && editing) {
        setEditing(false);
      }
    });

    setEditing(false);
  }

  ready(() => {
    const grid = document.querySelector('[data-dashboard-grid]');
    if (!grid) {
      return;
    }

    initialiseCharts(grid);
    initialiseWidgetManagement(grid);
  });
})();
