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
    ]
  },
  giraffe: {
    name: 'Giraffe',
    viewBox: '0 0 408 526',
    sections: [
      'neckPatch1', 'neckPatch2', 'neckPatch3', 'neckPatch4', 'neckPatch5',
      'bodyPatch1', 'bodyPatch2', 'bodyPatch3', 'bodyPatch4',
      'bodyPatch5', 'bodyPatch6', 'bodyPatch7', 'bodyPatch8'
    ]
  },
  house: {
    name: 'House',
    viewBox: '0 0 400 400',
    sections: [
      'sun', 'yard', 'path',
      'houseWall', 'roof', 'chimney', 'smoke',
      'windowLeft', 'windowRight', 'door',
      'treeTrunk', 'treeFoliage1', 'treeFoliage2',
      'flower1Stem', 'flower1Petal1', 'flower1Petal2', 'flower1Petal3', 'flower1Petal4', 'flower1Center',
      'flower2Stem', 'flower2Petal1', 'flower2Petal2', 'flower2Petal3', 'flower2Petal4', 'flower2Center',
      'flower3Stem', 'flower3Petal1', 'flower3Petal2', 'flower3Petal3', 'flower3Petal4', 'flower3Center',
      'flower4Stem', 'flower4Petal1', 'flower4Petal2', 'flower4Petal3', 'flower4Petal4', 'flower4Center'
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
  }
};

const STANDALONE_PICTURE_IDS = ['butterfly'];

const COMING_SOON_ITEMS = [
  { id: 'giraffe', label: 'Giraffe' },
  { id: 'house', label: 'House' },
  { id: 'fish', label: 'Fish' },
  { id: 'land', label: 'Land World' },
  { id: 'sea', label: 'Sea World' }
];

const ALL_PICTURE_IDS = Object.keys(PICTURE_CATALOG);
