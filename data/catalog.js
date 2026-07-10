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
    viewBox: '0 0 771 1024',
    sections: [
      'shape01', 'shape02', 'shape03', 'shape04', 'shape05', 'shape06', 'shape07', 'shape08',
      'shape09', 'shape10', 'shape11', 'shape12', 'shape13', 'shape14', 'shape15', 'shape16',
      'shape17', 'shape18', 'shape19', 'shape20', 'shape21', 'shape22', 'shape23', 'shape24',
      'shape25', 'shape26', 'shape27', 'shape28', 'shape29', 'shape30', 'shape31', 'shape32',
      'shape33', 'shape34', 'shape35', 'shape36', 'shape37', 'shape38', 'shape39', 'shape40',
      'shape41', 'shape42', 'shape43', 'shape44', 'shape45', 'shape46', 'shape47', 'shape48',
      'shape49', 'shape50', 'shape51'
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

const STANDALONE_PICTURE_IDS = ['butterfly', 'giraffe'];

const COMING_SOON_ITEMS = [
  { id: 'house', label: 'House' },
  { id: 'fish', label: 'Fish' },
  { id: 'land', label: 'Land World' },
  { id: 'sea', label: 'Sea World' }
];

const ALL_PICTURE_IDS = Object.keys(PICTURE_CATALOG);
