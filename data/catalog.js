function pictureMeta(pictureId) {
  return PICTURE_CATALOG[pictureId];
}

// Complete clusters: tapping any member paints every other member too.
function neighborCluster(ids) {
  const neighbors = {};
  ids.forEach(function(id) {
    neighbors[id] = ids.filter(function(other) { return other !== id; });
  });
  return neighbors;
}

function mergeNeighbors() {
  const out = {};
  Array.prototype.forEach.call(arguments, function(map) {
    Object.keys(map).forEach(function(key) {
      out[key] = map[key];
    });
  });
  return out;
}

function fillGroup(pictureId, sectionId) {
  const neighbors = pictureMeta(pictureId).neighbors || {};
  return [sectionId].concat(neighbors[sectionId] || []);
}

const PICTURE_CATALOG = {
  butterfly: {
    name: 'Butterfly',
    viewBox: '0 0 1024 716',
    sections: [
      'wing-left-upper', 'wing-left-lower', 'wing-right-upper', 'wing-right-lower',
      'leftUpperSpot', 'leftUpperOval', 'leftUpperBlob', 'leftUpperDot', 'leftUpperInner',
      'rightUpperSpot', 'rightUpperOval', 'rightUpperBlob', 'rightUpperDot', 'rightUpperInner',
      'leftLowerSpot', 'leftLowerOval', 'leftLowerBlob', 'leftLowerMid',
      'rightLowerSpot', 'rightLowerOval', 'rightLowerBlob', 'rightLowerMid'
    ],
    neighbors: mergeNeighbors(
      neighborCluster(['leftUpperSpot', 'leftUpperOval', 'leftUpperBlob', 'leftUpperDot', 'leftUpperInner']),
      neighborCluster(['rightUpperSpot', 'rightUpperOval', 'rightUpperBlob', 'rightUpperDot', 'rightUpperInner']),
      neighborCluster(['leftLowerSpot', 'leftLowerOval', 'leftLowerBlob', 'leftLowerMid']),
      neighborCluster(['rightLowerSpot', 'rightLowerOval', 'rightLowerBlob', 'rightLowerMid'])
    )
  },
  giraffe: {
    name: 'Giraffe',
    viewBox: '0 0 1024 618',
    sections: [
      'giraffe-shape01', 'giraffe-shape02', 'giraffe-shape03', 'giraffe-shape04', 'giraffe-shape05', 'giraffe-shape06', 'giraffe-shape07', 'giraffe-shape08'
    ]
  },
  house: {
    name: 'House',
    viewBox: '0 0 1024 574',
    sections: [
      'house-shape01', 'house-shape02', 'house-shape03', 'house-shape04', 'house-shape05', 'house-shape06', 'house-shape07', 'house-shape08',
      'house-shape09', 'house-shape10', 'house-shape11'
    ]
  },
  fish: {
    name: 'Fish',
    viewBox: '0 0 400 400',
    sections: ['body', 'tail', 'topFin', 'sideFin', 'eye', 'stripe1', 'stripe2', 'lips']
  },
  dolphin: {
    name: 'Dolphin',
    viewBox: '0 0 400 400',
    sections: ['body', 'belly', 'dorsalFin', 'tail', 'flipper', 'eye', 'snout', 'splash']
  },
  crab: {
    name: 'Crab',
    viewBox: '0 0 400 400',
    sections: ['body', 'clawLeft', 'clawRight', 'legLeft', 'legRight', 'eyeLeft', 'eyeRight', 'shellSpot']
  },
  whale: {
    name: 'Whale',
    viewBox: '0 0 400 400',
    sections: ['body', 'belly', 'tail', 'flipper', 'eye', 'spout', 'spot1', 'spot2']
  },
  turtle: {
    name: 'Turtle',
    viewBox: '0 0 562 334',
    sections: [
      'turtle-shape01', 'turtle-shape02', 'turtle-shape03', 'turtle-shape04', 'turtle-shape05', 'turtle-shape06', 'turtle-shape07', 'turtle-shape08',
      'turtle-shape09', 'turtle-shape10', 'turtle-shape11', 'turtle-shape12', 'turtle-shape13', 'turtle-shape14', 'turtle-shape15', 'turtle-shape16',
      'turtle-shape17', 'turtle-shape18', 'turtle-shape19', 'turtle-shape20', 'turtle-shape21', 'turtle-shape22', 'turtle-shape23'
    ]
  },
  christmasTree: {
    name: 'Christmas Tree',
    viewBox: '0 0 881 1024',
    sections: [
      'christmasTree-shape01', 'christmasTree-shape02', 'christmasTree-shape03', 'christmasTree-shape04', 'christmasTree-shape05', 'christmasTree-shape06', 'christmasTree-shape07', 'christmasTree-shape08',
      'christmasTree-shape09', 'christmasTree-shape10', 'christmasTree-shape11', 'christmasTree-shape12', 'christmasTree-shape13', 'christmasTree-shape14', 'christmasTree-shape15', 'christmasTree-shape16',
      'christmasTree-shape17', 'christmasTree-shape18', 'christmasTree-shape19', 'christmasTree-shape20', 'christmasTree-shape21', 'christmasTree-shape22', 'christmasTree-shape23', 'christmasTree-shape24'
    ]
  },
  seaworld: {
    name: 'Sea World',
    viewBox: '0 0 794 794',
    sections: [
      'seaworld-shape01', 'seaworld-shape02', 'seaworld-shape03', 'seaworld-shape04', 'seaworld-shape05', 'seaworld-shape06', 'seaworld-shape07', 'seaworld-shape08'
    ]
  }
};

const STANDALONE_PICTURE_IDS = ['butterfly', 'giraffe', 'christmasTree', 'turtle', 'house', 'seaworld'];

const ALL_PICTURE_IDS = Object.keys(PICTURE_CATALOG);
