const SVG_NS = 'http://www.w3.org/2000/svg';
const XLINK_NS = 'http://www.w3.org/1999/xlink';

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

// Older iOS Safari sometimes drops click on SVG shapes; pair with touchend.
function bindTap(node, handler) {
  let touched = false;
  node.style.cursor = 'pointer';
  node.addEventListener('touchend', function(event) {
    if (event.touches && event.touches.length > 0) return;
    touched = true;
    event.preventDefault();
    handler(event);
  }, { passive: false });
  node.addEventListener('click', function(event) {
    if (touched) {
      touched = false;
      event.preventDefault();
      event.stopPropagation();
      return;
    }
    handler(event);
  });
}
