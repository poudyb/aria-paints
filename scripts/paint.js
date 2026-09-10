function toggleFill(pictureId, sectionId, fills) {
  // A tap paints the catalog-defined static group (compound section or
  // fully cross-linked neighbors), never nearby-by-proximity patches.
  const group = fillGroup(pictureId, sectionId);
  if (fills[sectionId] === state.selectedColor) {
    group.forEach(function(id) {
      if (fills[id] === state.selectedColor) delete fills[id];
    });
  } else {
    group.forEach(function(id) { fills[id] = state.selectedColor; });
  }
}

function hasAnyFill(fills) {
  return Object.keys(fills).length > 0;
}

function isComplete(pictureId, fills) {
  return pictureMeta(pictureId).sections.every(function(sectionId) {
    return !!fills[sectionId];
  });
}
