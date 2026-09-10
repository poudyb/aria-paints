const svgTemplateCache = {};

async function loadPictureTemplate(pictureId) {
  if (svgTemplateCache[pictureId]) return svgTemplateCache[pictureId];
  const assetUrl = 'assets/pictures/' + pictureId + '.svg';
  const response = await fetch(assetUrl);
  if (!response.ok) throw new Error('Missing picture asset: ' + pictureId);
  const text = await response.text();
  const doc = new DOMParser().parseFromString(text, 'image/svg+xml');
  const root = doc.documentElement;
  // Safari (esp. older iPadOS) resolves relative <image> hrefs against the
  // DOMParser document, not the page — absolutize against the SVG URL.
  const baseUrl = response.url || new URL(assetUrl, window.location.href).href;
  absolutizeSvgImageHrefs(root, baseUrl);
  svgTemplateCache[pictureId] = root;
  return root;
}

function absolutizeSvgImageHrefs(svgRoot, baseUrl) {
  const images = svgRoot.querySelectorAll('image');
  for (let i = 0; i < images.length; i++) {
    const img = images[i];
    const href = img.getAttribute('href') || img.getAttributeNS(XLINK_NS, 'href');
    if (!href || href.indexOf('data:') === 0 || href.indexOf('blob:') === 0) continue;
    let absolute;
    try {
      absolute = new URL(href, baseUrl).href;
    } catch (error) {
      continue;
    }
    img.setAttribute('href', absolute);
    img.setAttributeNS(XLINK_NS, 'href', absolute);
  }
}

async function preloadPictures() {
  await Promise.all(ALL_PICTURE_IDS.map(loadPictureTemplate));
}

function viewBoxSize(viewBox) {
  const parts = String(viewBox || '').trim().split(/[\s,]+/);
  if (parts.length !== 4) return null;
  const width = Number(parts[2]);
  const height = Number(parts[3]);
  if (!width || !height) return null;
  return { width: width, height: height };
}

function refreshSvgImages(svg) {
  // WebKit can drop <image> loads from DOMParser-cloned SVGs until href is re-applied.
  const images = svg.querySelectorAll('image');
  for (let i = 0; i < images.length; i++) {
    const image = images[i];
    const href = image.getAttribute('href') || image.getAttributeNS(XLINK_NS, 'href');
    if (!href) continue;
    let absolute = href;
    try {
      absolute = new URL(href, window.location.href).href;
    } catch (error) {
      // Keep original href if URL parsing fails.
    }
    image.removeAttribute('href');
    image.removeAttributeNS(XLINK_NS, 'href');
    image.setAttribute('href', absolute);
    image.setAttributeNS(XLINK_NS, 'href', absolute);
  }
}

function clonePictureSvg(pictureId, fills, onSectionClick, className) {
  const meta = pictureMeta(pictureId);
  const template = svgTemplateCache[pictureId];
  const svg = template.cloneNode(true);
  const classes = ['paint-svg'];
  if (className !== 'preview-svg') {
    classes.push('paint-svg--' + pictureId);
  }
  if (className) classes.push(className);
  svg.setAttribute('class', classes.join(' '));
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', meta.name);
  if (!svg.getAttribute('viewBox')) svg.setAttribute('viewBox', meta.viewBox);

  // Explicit width/height keep Safari from treating the SVG as 0x0 in flex layouts.
  const size = viewBoxSize(svg.getAttribute('viewBox') || meta.viewBox);
  if (size) {
    svg.setAttribute('width', String(size.width));
    svg.setAttribute('height', String(size.height));
  }
  if (!svg.getAttribute('preserveAspectRatio')) {
    svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  }

  refreshSvgImages(svg);

  svg.querySelectorAll('.paint-section').forEach(function(node) {
    const sectionId = node.id;
    if (!sectionId) return;
    node.setAttribute('fill', fills[sectionId] || '#fff');
    if (onSectionClick) {
      bindTap(node, function(event) {
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
