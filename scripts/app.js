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

const SVG_NS = 'http://www.w3.org/2000/svg';
const svgTemplateCache = {};

const WORLDS = [
  {
    id: 'land',
    name: 'Land World',
    thumb: 'assets/world-thumbs/land.svg',
    renderScenery: appendLandScenery,
    components: [
      worldPart('house', 'House', 'house', 25, 88, 0.4, 'bob'),
      worldPart('giraffe', 'Giraffe', 'giraffe', 455, 108, 0.48, 'walk'),
      worldPart('butterfly', 'Butterfly', 'butterfly', 175, 42, 0.26, 'flutter')
    ]
  },
  {
    id: 'sea',
    name: 'Sea World',
    thumb: 'assets/world-thumbs/sea.svg',
    renderScenery: appendSeaScenery,
    components: [
      worldPart('fish', 'Fish', 'fish', 35, 72, 0.34, 'swim'),
      worldPart('dolphin', 'Dolphin', 'dolphin', 255, 78, 0.44, 'bob'),
      worldPart('crab', 'Crab', 'crab', 115, 228, 0.34, 'walk'),
      worldPart('whale', 'Whale', 'whale', 455, 118, 0.5, 'bob')
    ]
  }
];

const state = {
  selectedColor: COLORS[0].hex,
  activePicture: null,
  activeWorld: null,
  activeComponent: null,
  fills: {}
};

function worldPart(id, name, pictureId, x, y, scale, animation) {
  return { id, name, pictureId, x, y, scale, animation };
}

function pictureMeta(pictureId) {
  return PICTURE_CATALOG[pictureId];
}

async function loadPictureTemplate(pictureId) {
  if (svgTemplateCache[pictureId]) return svgTemplateCache[pictureId];
  const response = await fetch('assets/pictures/' + pictureId + '.svg');
  if (!response.ok) throw new Error('Missing picture asset: ' + pictureId);
  const text = await response.text();
  const doc = new DOMParser().parseFromString(text, 'image/svg+xml');
  svgTemplateCache[pictureId] = doc.documentElement;
  return doc.documentElement;
}

async function preloadPictures() {
  await Promise.all(ALL_PICTURE_IDS.map(loadPictureTemplate));
}

function clonePictureSvg(pictureId, fills, onSectionClick, className) {
  const meta = pictureMeta(pictureId);
  const template = svgTemplateCache[pictureId];
  const svg = template.cloneNode(true);
  const classes = ['paint-svg'];
  if (pictureId === 'butterfly' && className !== 'preview-svg') {
    classes.push('paint-svg--butterfly');
  }
  if (pictureId === 'giraffe' && className !== 'preview-svg') {
    classes.push('paint-svg--giraffe');
  }
  if (className) classes.push(className);
  svg.setAttribute('class', classes.join(' '));
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', meta.name);
  if (!svg.getAttribute('viewBox')) svg.setAttribute('viewBox', meta.viewBox);

  svg.querySelectorAll('.paint-section').forEach(function(node) {
    const sectionId = node.id;
    if (!sectionId) return;
    node.setAttribute('fill', fills[sectionId] || '#fff');
    if (onSectionClick) {
      node.addEventListener('click', function(event) {
        event.stopPropagation();
        onSectionClick(sectionId);
      });
    }
  });

  return svg;
}

function buildPicturePreview(pictureId) {
  const meta = pictureMeta(pictureId);
  const inner = clonePictureSvg(pictureId, {}, null, 'preview-svg');
  const wrap = svgEl('svg', {
    class: 'home-card__svg',
    viewBox: meta.viewBox,
    role: 'img',
    'aria-hidden': 'true'
  });
  while (inner.firstChild) wrap.appendChild(inner.firstChild);
  return wrap;
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  return node;
}

function svgEl(tag, attrs) {
  const node = document.createElementNS(SVG_NS, tag);
  Object.keys(attrs || {}).forEach(function(key) {
    node.setAttribute(key, attrs[key]);
  });
  return node;
}

function setHomeDecorVisible(visible) {
  document.body.classList.toggle('is-home', visible);
}

function clearApp() {
  app.innerHTML = '';
  setHomeDecorVisible(false);
}

function renderHome() {
  clearApp();
  state.activePicture = null;
  state.activeWorld = null;
  state.activeComponent = null;
  state.fills = {};

  const page = el('section', 'page page--home');
  const hero = el('header', 'hero');
  hero.appendChild(el('h1', '', 'Aria Paints'));
  hero.appendChild(el('p', '', 'Tap the butterfly to color!'));

  const grid = el('div', 'home-grid');

  STANDALONE_PICTURE_IDS.forEach(function(pictureId) {
    const meta = pictureMeta(pictureId);
    grid.appendChild(homePictureCard(meta.name, pictureId, function() {
      openStandalonePicture(pictureId);
    }));
  });

  COMING_SOON_ITEMS.forEach(function(item) {
    grid.appendChild(homeComingSoonCard(item.label));
  });

  page.appendChild(hero);
  page.appendChild(grid);
  app.appendChild(page);
  setHomeDecorVisible(true);
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

function openStandalonePicture(pictureId) {
  state.activePicture = pictureId;
  state.activeWorld = null;
  state.activeComponent = null;
  state.fills = {};
  renderPaintScreen({
    pictureId,
    fills: state.fills,
    onBack: renderHome,
    backLabel: '← Home'
  });
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

function startWorld(worldId) {
  const world = WORLDS.find(function(item) { return item.id === worldId; });
  state.activePicture = null;
  state.activeWorld = { id: worldId, fills: {} };
  state.activeComponent = null;
  world.components.forEach(function(component) {
    state.activeWorld.fills[component.id] = {};
  });
  renderWorldScene();
}

function renderWorldScene() {
  const world = WORLDS.find(function(item) { return item.id === state.activeWorld.id; });
  clearApp();

  const download = downloadButton(function() {
    downloadSvg('aria-paints-' + world.id + '.png', document.querySelector('.world-svg'), 'Aria Paints - ' + world.name);
  });
  download.disabled = !hasAnyWorldFill();

  const page = el('section', 'page paint-layout');
  page.appendChild(toolbar(world.name, {
    left: [pill('← Home', renderHome)],
    right: [download]
  }));

  const card = el('div', 'canvas-card');
  card.appendChild(renderWorldSvg(world));
  page.appendChild(card);
  page.appendChild(el('p', 'world-help', 'Tap a friend to paint. Colored friends come alive!'));
  app.appendChild(page);
}

function appendLandScenery(svg) {
  svg.appendChild(svgEl('rect', { class: 'scene-sky', x: 0, y: 0, width: 800, height: 500, fill: '#87ceeb' }));
  svg.appendChild(svgEl('circle', { cx: 680, cy: 72, r: 52, fill: '#fff59d', stroke: '#f9a825', 'stroke-width': 3 }));
  svg.appendChild(svgEl('path', {
    class: 'scene-hill scene-hill--back',
    d: 'M0 310 C120 250 220 290 360 255 C480 228 620 268 800 235 V500 H0Z',
    fill: '#81c784'
  }));
  svg.appendChild(svgEl('path', {
    class: 'scene-hill scene-hill--front',
    d: 'M0 355 C100 330 200 365 320 340 C450 312 580 350 800 318 V500 H0Z',
    fill: '#66bb6a'
  }));
  svg.appendChild(svgEl('path', {
    class: 'scene-road',
    d: 'M-20 390 C80 365 140 395 220 368 C310 338 400 378 500 352 C590 328 680 360 820 340 L835 395 C700 415 590 385 480 405 C360 428 240 400 140 418 C60 430 10 420 -20 410Z',
    fill: '#9e9e9e',
    stroke: '#616161',
    'stroke-width': 4,
    'stroke-linejoin': 'round'
  }));
  svg.appendChild(svgEl('path', {
    class: 'scene-road-mark',
    fill: 'none',
    stroke: '#fff',
    'stroke-width': 5,
    'stroke-dasharray': '18 22',
    'stroke-linecap': 'round',
    d: 'M30 378 C120 358 200 382 290 360 C380 338 470 368 560 348 C650 330 720 352 790 342'
  }));
  svg.appendChild(svgEl('ellipse', { cx: 95, cy: 318, rx: 42, ry: 22, fill: '#4caf50', opacity: 0.85 }));
  svg.appendChild(svgEl('ellipse', { cx: 620, cy: 298, rx: 55, ry: 26, fill: '#388e3c', opacity: 0.8 }));
}

function appendSeaScenery(svg) {
  const defs = svgEl('defs');
  const grad = svgEl('linearGradient', { id: 'sea-water', x1: 0, y1: 0, x2: 0, y2: 1 });
  grad.appendChild(svgEl('stop', { offset: '0%', 'stop-color': '#4fc3f7' }));
  grad.appendChild(svgEl('stop', { offset: '100%', 'stop-color': '#0277bd' }));
  defs.appendChild(grad);
  svg.appendChild(defs);
  svg.appendChild(svgEl('rect', { x: 0, y: 0, width: 800, height: 500, fill: 'url(#sea-water)' }));

  svg.appendChild(svgEl('path', {
    class: 'scene-seaweed',
    d: 'M55 500 Q48 380 62 260 Q72 340 68 420 Q75 460 55 500Z',
    fill: '#26a69a'
  }));
  svg.appendChild(svgEl('path', {
    class: 'scene-seaweed',
    d: 'M120 500 Q115 400 128 320 Q135 390 130 450 Q138 485 120 500Z',
    fill: '#00897b'
  }));
  svg.appendChild(svgEl('path', {
    class: 'scene-seaweed',
    d: 'M720 500 Q710 390 735 280 Q745 360 738 430 Q728 470 720 500Z',
    fill: '#26a69a'
  }));
  svg.appendChild(svgEl('path', {
    class: 'scene-coral',
    d: 'M640 420 Q650 360 670 375 Q660 410 640 420Z',
    fill: '#ff7043'
  }));
  svg.appendChild(svgEl('ellipse', { cx: 175, cy: 395, rx: 28, ry: 16, fill: '#ffca28', stroke: '#f57f17', 'stroke-width': 2 }));
  svg.appendChild(svgEl('path', {
    class: 'scene-jelly',
    d: 'M520 120 Q535 85 550 120 Q535 145 520 120Z',
    fill: '#ce93d8',
    opacity: 0.9
  }));
  svg.appendChild(svgEl('path', {
    class: 'scene-jelly',
    d: 'M530 120 L525 155 M540 118 L545 150 M555 122 L558 148',
    stroke: '#ab47bc',
    'stroke-width': 2,
    fill: 'none',
    'stroke-linecap': 'round'
  }));
  svg.appendChild(svgEl('ellipse', { cx: 400, cy: 55, rx: 8, ry: 8, fill: '#fff59d', opacity: 0.75 }));
  svg.appendChild(svgEl('ellipse', { cx: 450, cy: 38, rx: 6, ry: 6, fill: '#fff59d', opacity: 0.65 }));
  svg.appendChild(svgEl('ellipse', { cx: 280, cy: 70, rx: 7, ry: 7, fill: '#fff59d', opacity: 0.7 }));
  svg.appendChild(svgEl('path', {
    class: 'scene-mini-fish',
    fill: '#ff8a65',
    d: 'M590 200 C610 195 625 205 615 215 C600 225 575 218 590 200Z'
  }));
  svg.appendChild(svgEl('circle', { cx: 612, cy: 206, r: 3, fill: '#111' }));
  svg.appendChild(svgEl('path', {
    class: 'scene-mini-fish',
    fill: '#9575cd',
    d: 'M155 250 C170 245 182 255 172 262 C160 270 145 260 155 250Z'
  }));
}

function renderWorldSvg(world) {
  const svg = svgEl('svg', { class: 'world-svg', viewBox: '0 0 800 500', role: 'img', 'aria-label': world.name });
  world.renderScenery(svg);

  world.components.forEach(function(component) {
    const fills = state.activeWorld.fills[component.id];
    const group = svgEl('g', {
      class: 'world-component ' + (hasAnyFill(fills) ? 'is-painted animation-' + component.animation : ''),
      transform: 'translate(' + component.x + ' ' + component.y + ') scale(' + component.scale + ')',
      role: 'button',
      'aria-label': 'Paint ' + component.name
    });
    group.addEventListener('click', function() {
      renderWorldComponent(component.id);
    });
    const picture = clonePictureSvg(component.pictureId, fills, null);
    picture.classList.remove('paint-svg');
    picture.classList.add('world-piece');
    group.appendChild(picture);
    svg.appendChild(group);
  });

  return svg;
}

function renderWorldComponent(componentId) {
  const world = WORLDS.find(function(item) { return item.id === state.activeWorld.id; });
  const component = world.components.find(function(item) { return item.id === componentId; });
  state.activeComponent = componentId;
  renderPaintScreen({
    pictureId: component.pictureId,
    title: component.name,
    fills: state.activeWorld.fills[componentId],
    onBack: renderWorldScene,
    backLabel: '🌎 World'
  });
}

function renderPaintScreen(options) {
  clearApp();
  const meta = pictureMeta(options.pictureId);
  const title = options.title || meta.name;

  const download = downloadButton(function() {
    downloadSvg('aria-paints-' + slug(title) + '.png', document.querySelector('.paint-svg'), 'Aria Paints - ' + title);
  });
  download.disabled = !hasAnyFill(options.fills);

  const page = el('section', 'page paint-layout');
  page.appendChild(toolbar(title, {
    left: [pill(options.backLabel, options.onBack)],
    right: [download]
  }));

  const card = el('div', 'canvas-card coloring-page');
  card.appendChild(clonePictureSvg(options.pictureId, options.fills, function(sectionId) {
    toggleFill(sectionId, options.fills);
    renderPaintScreen(options);
    if (isComplete(options.pictureId, options.fills)) celebrate();
  }));

  page.appendChild(card);
  page.appendChild(renderPalette());
  app.appendChild(page);
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

function toggleFill(sectionId, fills) {
  if (fills[sectionId] === state.selectedColor) delete fills[sectionId];
  else fills[sectionId] = state.selectedColor;
}

function hasAnyFill(fills) {
  return Object.keys(fills).length > 0;
}

function hasAnyWorldFill() {
  return Object.keys(state.activeWorld.fills).some(function(key) {
    return hasAnyFill(state.activeWorld.fills[key]);
  });
}

function isComplete(pictureId, fills) {
  return pictureMeta(pictureId).sections.every(function(sectionId) {
    return !!fills[sectionId];
  });
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
  const exportSvg = svgEl('svg', { xmlns: SVG_NS, viewBox: '0 0 ' + width + ' ' + height, width, height });
  exportSvg.appendChild(svgEl('rect', { x: 0, y: 0, width, height, fill: '#fff' }));

  Array.from(sourceSvg.children).forEach(function(child) {
    exportSvg.appendChild(child.cloneNode(true));
  });

  const date = new Date().toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  const label = svgEl('text', {
    x: width / 2,
    y: height - 16,
    'text-anchor': 'middle',
    'font-family': 'Arial, sans-serif',
    'font-size': 18,
    'font-weight': 700,
    fill: '#4a148c'
  });
  label.textContent = title + ' • ' + date;
  exportSvg.appendChild(label);

  const serialized = new XMLSerializer().serializeToString(exportSvg);
  const blob = new Blob([serialized], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const img = new Image();
  img.onload = function() {
    const canvas = document.createElement('canvas');
    canvas.width = width * 2;
    canvas.height = height * 2;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    URL.revokeObjectURL(url);
    const link = document.createElement('a');
    link.download = filename;
    link.href = canvas.toDataURL('image/png');
    link.click();
  };
  img.src = url;
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

preventGestures();
preloadPictures().then(renderHome).catch(function(error) {
  app.innerHTML = '<p class="load-error">Could not load coloring pages. ' + error.message + '</p>';
});
