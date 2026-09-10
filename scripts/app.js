const state = {
  selectedColor: COLORS[0].hex,
  activePicture: null,
  activeWorld: null,
  activeComponent: null,
  fills: {}
};

function renderHome() {
  clearApp();
  state.activePicture = null;
  state.activeWorld = null;
  state.activeComponent = null;
  state.fills = {};

  const page = el('section', 'page page--home');
  const hero = el('header', 'hero');
  hero.appendChild(el('h1', '', 'Aria Paints'));
  hero.appendChild(el('p', '', 'Pick a picture to paint!'));

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

function renderPaintScreen(options) {
  const meta = pictureMeta(options.pictureId);
  const title = options.title || meta.name;

  const download = downloadButton(function() {
    downloadSvg('aria-paints-' + slug(title) + '.png', document.querySelector('.paint-svg'), 'Aria Paints - ' + title);
  });
  download.disabled = !hasAnyFill(options.fills);

  const layout = openPaintLayout(title, {
    left: [pill(options.backLabel, options.onBack)],
    right: [download]
  }, 'canvas-card coloring-page');
  layout.card.appendChild(clonePictureSvg(options.pictureId, options.fills, function(sectionId) {
    toggleFill(options.pictureId, sectionId, options.fills);
    renderPaintScreen(options);
    if (isComplete(options.pictureId, options.fills)) celebrate();
  }));
  layout.page.appendChild(renderPalette());
}

preventGestures();
preloadPictures().then(renderHome).catch(function(error) {
  app.innerHTML = '<p class="load-error">Could not load coloring pages. ' + error.message + '</p>';
});
