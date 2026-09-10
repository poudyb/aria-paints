function worldPart(id, name, pictureId, x, y, scale, animation) {
  return { id, name, pictureId, x, y, scale, animation };
}

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

function hasAnyWorldFill() {
  return Object.keys(state.activeWorld.fills).some(function(key) {
    return hasAnyFill(state.activeWorld.fills[key]);
  });
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

  const download = downloadButton(function() {
    downloadSvg('aria-paints-' + world.id + '.png', document.querySelector('.world-svg'), 'Aria Paints - ' + world.name);
  });
  download.disabled = !hasAnyWorldFill();

  const layout = openPaintLayout(world.name, {
    left: [pill('← Home', renderHome)],
    right: [download]
  });
  layout.card.appendChild(renderWorldSvg(world));
  layout.page.appendChild(el('p', 'world-help', 'Tap a friend to paint. Colored friends come alive!'));
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
    bindTap(group, function() {
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
