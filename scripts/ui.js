const app = document.getElementById('app');
const celebrationLayer = document.getElementById('celebration-layer');

const COLORS = [
  { key: 'red', name: 'Red', hex: '#e53935' },
  { key: 'orange', name: 'Orange', hex: '#fb8c00' },
  { key: 'yellow', name: 'Yellow', hex: '#fdd835' },
  { key: 'green', name: 'Green', hex: '#43a047' },
  { key: 'blue', name: 'Blue', hex: '#1e88e5' },
  { key: 'lightBlue', name: 'Light blue', hex: '#4fc3f7' },
  { key: 'purple', name: 'Purple', hex: '#8e24aa' },
  { key: 'pink', name: 'Pink', hex: '#f06292' },
  { key: 'brown', name: 'Brown', hex: '#8d6e63' },
  { key: 'black', name: 'Black', hex: '#212121' },
  { key: 'gray', name: 'Gray', hex: '#757575' },
  { key: 'teal', name: 'Teal', hex: '#00897b' }
];

function setHomeDecorVisible(visible) {
  document.body.classList.toggle('is-home', visible);
}

function clearApp() {
  app.innerHTML = '';
  setHomeDecorVisible(false);
}

function toolbar(title, buttons) {
  const bar = el('div', 'toolbar');
  const left = el('div', 'toolbar__group');
  const right = el('div', 'toolbar__group');

  buttons.left.forEach(function(btn) { left.appendChild(btn); });
  buttons.right.forEach(function(btn) { right.appendChild(btn); });

  bar.appendChild(left);
  bar.appendChild(el('h1', 'toolbar__title', title));
  bar.appendChild(right);
  return bar;
}

function pill(label, onClick) {
  const button = el('button', 'pill-btn', label);
  button.type = 'button';
  button.addEventListener('click', onClick);
  return button;
}

function openPaintLayout(title, buttons, cardClassName) {
  clearApp();
  const page = el('section', 'page paint-layout');
  page.appendChild(toolbar(title, buttons));
  const card = el('div', cardClassName || 'canvas-card');
  page.appendChild(card);
  app.appendChild(page);
  return { page, card };
}

function homePictureCard(name, pictureId, onClick) {
  const button = el('button', 'home-card home-card--picture');
  button.type = 'button';
  button.setAttribute('aria-label', 'Color ' + name);

  const preview = el('div', 'home-card__preview home-card__preview--art');
  preview.appendChild(buildPicturePreview(pictureId));

  button.appendChild(preview);
  button.appendChild(el('span', 'home-card__name', name));
  button.addEventListener('click', onClick);
  return button;
}

function homeComingSoonCard(name) {
  const card = el('div', 'home-card home-card--coming-soon');
  card.setAttribute('role', 'group');
  card.setAttribute('aria-label', name + ', coming soon');

  const preview = el('div', 'home-card__preview home-card__preview--coming-soon');
  preview.appendChild(el('span', 'home-card__coming-soon', 'Coming soon'));

  card.appendChild(preview);
  card.appendChild(el('span', 'home-card__name', name));
  return card;
}

function homeWorldCard(world, onClick) {
  const button = el('button', 'home-card home-card--world');
  button.type = 'button';
  button.setAttribute('aria-label', 'Open ' + world.name);

  const preview = el('div', 'home-card__preview home-card__preview--scene');
  const img = document.createElement('img');
  img.src = world.thumb;
  img.alt = '';
  img.decoding = 'async';
  img.className = 'home-card__thumb';
  preview.appendChild(img);

  button.appendChild(preview);
  button.appendChild(el('span', 'home-card__name', world.name));
  button.appendChild(el('span', 'home-card__hint', 'Paint the whole scene'));
  button.addEventListener('click', onClick);
  return button;
}

function renderPalette() {
  const palette = el('div', 'palette');
  COLORS.forEach(function(color) {
    const button = el('button', 'color-btn color-crayon' + (state.selectedColor === color.hex ? ' is-selected' : ''));
    button.type = 'button';
    button.style.setProperty('--crayon-color', color.hex);
    button.setAttribute('aria-label', color.name);

    const shape = el('span', 'color-crayon__shape');
    shape.setAttribute('aria-hidden', 'true');
    shape.appendChild(el('span', 'color-crayon__tip'));
    shape.appendChild(el('span', 'color-crayon__shaft'));
    shape.appendChild(el('span', 'color-crayon__wrap'));
    button.appendChild(shape);

    button.addEventListener('click', function() {
      state.selectedColor = color.hex;
      document.querySelectorAll('.color-btn').forEach(function(btn) { btn.classList.remove('is-selected'); });
      button.classList.add('is-selected');
    });
    palette.appendChild(button);
  });
  return palette;
}

function downloadButton(onClick) {
  const button = el('button', 'download-btn', 'Download PNG');
  button.type = 'button';
  button.addEventListener('click', function() {
    if (!button.disabled) onClick();
  });
  return button;
}

function downloadSvg(filename, sourceSvg, title) {
  const sourceViewBox = sourceSvg.getAttribute('viewBox').split(' ').map(Number);
  const width = sourceViewBox[2];
  const height = sourceViewBox[3] + 48;
  const exportSvg = svgEl('svg', {
    xmlns: SVG_NS,
    viewBox: '0 0 ' + width + ' ' + height,
    width: String(width),
    height: String(height)
  });
  exportSvg.appendChild(svgEl('rect', {
    x: 0,
    y: 0,
    width: String(width),
    height: String(height),
    fill: '#fff'
  }));

  Array.from(sourceSvg.children).forEach(function(child) {
    exportSvg.appendChild(child.cloneNode(true));
  });

  const date = new Date().toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  const label = svgEl('text', {
    x: String(width / 2),
    y: String(height - 16),
    'text-anchor': 'middle',
    'font-family': 'Arial, sans-serif',
    'font-size': '18',
    'font-weight': '700',
    fill: '#4a148c'
  });
  label.textContent = title + ' • ' + date;
  exportSvg.appendChild(label);

  const serialized = new XMLSerializer().serializeToString(exportSvg);
  // data: URLs are more reliable than blob: SVG → canvas on older Safari/iPad.
  const url = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(serialized);
  const img = new Image();
  img.onload = function() {
    const canvas = document.createElement('canvas');
    canvas.width = width * 2;
    canvas.height = height * 2;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    savePngFromCanvas(canvas, filename);
  };
  img.onerror = function() {
    window.alert('Could not create the PNG on this device. Try again or use another browser.');
  };
  img.src = url;
}

function savePngFromCanvas(canvas, filename) {
  let dataUrl;
  try {
    dataUrl = canvas.toDataURL('image/png');
  } catch (error) {
    window.alert('Could not save the picture on this device.');
    return;
  }

  // iPad/iPhone Safari often ignores <a download> for data URLs.
  const isIos = /iPad|iPhone|iPod/.test(navigator.userAgent)
    || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  if (isIos) {
    window.open(dataUrl, '_blank');
    return;
  }

  const link = document.createElement('a');
  link.download = filename;
  link.href = dataUrl;
  link.rel = 'noopener';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function celebrate() {
  ['🎉', '✨', '🌈', '💖', '⭐', '🦋'].forEach(function(symbol, index) {
    const item = el('div', 'celebration-emoji', symbol);
    item.style.left = (12 + index * 15) + '%';
    item.style.bottom = (10 + (index % 2) * 12) + '%';
    item.style.animationDelay = (index * 0.08) + 's';
    celebrationLayer.appendChild(item);
    window.setTimeout(function() { item.remove(); }, 1700);
  });
}

function slug(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function preventGestures() {
  document.addEventListener('gesturestart', function(event) { event.preventDefault(); });
  document.addEventListener('gesturechange', function(event) { event.preventDefault(); });
  document.addEventListener('gestureend', function(event) { event.preventDefault(); });
  document.addEventListener('touchmove', function(event) {
    if (event.touches.length > 1) event.preventDefault();
  }, { passive: false });
}
