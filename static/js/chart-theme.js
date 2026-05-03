(function () {
  if (!window.Chart) {
    return;
  }

  const css = getComputedStyle(document.documentElement);
  const primary = css.getPropertyValue('--brand-primary').trim() || '#0f8ec7';
  const accent = css.getPropertyValue('--brand-accent').trim() || '#20c997';
  const success = css.getPropertyValue('--brand-success').trim() || '#22a06b';
  const danger = css.getPropertyValue('--brand-danger').trim() || '#dc3545';
  const ink = css.getPropertyValue('--brand-ink').trim() || '#12313f';
  const muted = css.getPropertyValue('--brand-muted').trim() || '#6c7a86';
  const border = css.getPropertyValue('--brand-border').trim() || '#d8e7ee';

  const currencyFormatter = new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  });

  const defaults = Chart.defaults || {};
  if (defaults.font) {
    defaults.font.family = "'Source Sans Pro', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
  }
  defaults.color = muted;
  defaults.borderColor = border;

  if (defaults.elements) {
    if (defaults.elements.line) {
      defaults.elements.line.borderWidth = 3;
      defaults.elements.line.tension = 0.38;
    }

    if (defaults.elements.point) {
      defaults.elements.point.radius = 3;
      defaults.elements.point.hoverRadius = 6;
      defaults.elements.point.borderWidth = 2;
    }

    if (defaults.elements.arc) {
      defaults.elements.arc.borderColor = '#fff';
      defaults.elements.arc.borderWidth = 3;
    }
  }

  if (defaults.plugins && defaults.plugins.legend && defaults.plugins.legend.labels) {
    defaults.plugins.legend.labels.usePointStyle = true;
    defaults.plugins.legend.labels.boxWidth = 8;
    defaults.plugins.legend.labels.boxHeight = 8;
    defaults.plugins.legend.labels.padding = 16;
  }

  if (defaults.plugins && defaults.plugins.tooltip) {
    defaults.plugins.tooltip.backgroundColor = 'rgba(18, 49, 63, 0.94)';
    defaults.plugins.tooltip.titleColor = '#fff';
    defaults.plugins.tooltip.bodyColor = '#fff';
    defaults.plugins.tooltip.padding = 12;
    defaults.plugins.tooltip.cornerRadius = 8;
    defaults.plugins.tooltip.displayColors = true;
    defaults.plugins.tooltip.boxPadding = 5;
  }

  function hexToRgb(hex) {
    const cleanHex = hex.replace('#', '');
    const value = parseInt(cleanHex.length === 3
      ? cleanHex.split('').map((char) => char + char).join('')
      : cleanHex, 16);

    return {
      r: (value >> 16) & 255,
      g: (value >> 8) & 255,
      b: value & 255,
    };
  }

  function alpha(hex, opacity) {
    const rgb = hexToRgb(hex);
    return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${opacity})`;
  }

  function lineGradient(ctx, color) {
    const area = ctx.chart.chartArea;
    if (!area) {
      return alpha(color, 0.18);
    }

    const gradient = ctx.chart.ctx.createLinearGradient(0, area.top, 0, area.bottom);
    gradient.addColorStop(0, alpha(color, 0.28));
    gradient.addColorStop(0.72, alpha(color, 0.08));
    gradient.addColorStop(1, alpha(color, 0));
    return gradient;
  }

  function money(value) {
    return currencyFormatter.format(Number(value || 0));
  }

  window.financeChartTheme = {
    colors: {
      primary,
      accent,
      success,
      danger,
      ink,
      muted,
      border,
      income: success,
      expense: danger,
    },
    alpha,
    lineGradient,
    money,
    moneyTick(value) {
      return money(value);
    },
    moneyTooltip(context) {
      const label = context.dataset.label || context.label || '';
      return `${label}: ${money(context.raw)}`;
    },
    doughnutOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '64%',
        radius: '92%',
        layout: {
          padding: 8,
        },
        plugins: {
          legend: {
            position: 'bottom',
          },
          tooltip: {
            callbacks: {
              label: this.moneyTooltip,
            },
          },
        },
      };
    },
    lineOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              padding: 8,
            },
          },
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(216, 231, 238, 0.72)',
              drawBorder: false,
            },
            ticks: {
              callback: this.moneyTick,
              padding: 10,
            },
          },
        },
        plugins: {
          legend: {
            position: 'bottom',
          },
          tooltip: {
            callbacks: {
              label: this.moneyTooltip,
            },
          },
        },
      };
    },
    barOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              padding: 8,
            },
          },
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(216, 231, 238, 0.72)',
              drawBorder: false,
            },
            ticks: {
              callback: this.moneyTick,
              padding: 10,
            },
          },
        },
        plugins: {
          legend: {
            position: 'bottom',
          },
          tooltip: {
            callbacks: {
              label: this.moneyTooltip,
            },
          },
        },
      };
    },
  };
})();
