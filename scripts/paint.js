function toggleFill(pictureId, sectionId, fills) {
  // Little fingers are imprecise: a tap paints the tapped section plus its
  // catalog-defined neighbors (nearby spots, adjacent fronds/petals/segments).
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
