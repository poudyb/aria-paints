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
      'giraffe-shape01', 'giraffe-shape02', 'giraffe-shape03', 'giraffe-shape04', 'giraffe-shape05', 'giraffe-shape06', 'giraffe-shape07', 'giraffe-shape08',
      'giraffe-shape09', 'giraffe-shape10', 'giraffe-shape11', 'giraffe-shape12', 'giraffe-shape13', 'giraffe-shape14', 'giraffe-shape15', 'giraffe-shape16',
      'giraffe-shape17', 'giraffe-shape18', 'giraffe-shape19', 'giraffe-shape20', 'giraffe-shape21', 'giraffe-shape22', 'giraffe-shape23', 'giraffe-shape24',
      'giraffe-shape25', 'giraffe-shape26', 'giraffe-shape27', 'giraffe-shape28', 'giraffe-shape29', 'giraffe-shape30', 'giraffe-shape31', 'giraffe-shape32',
      'giraffe-shape33', 'giraffe-shape34', 'giraffe-shape35', 'giraffe-shape36', 'giraffe-shape37', 'giraffe-shape38', 'giraffe-shape39', 'giraffe-shape40',
      'giraffe-shape41', 'giraffe-shape42', 'giraffe-shape43', 'giraffe-shape44', 'giraffe-shape45', 'giraffe-shape46', 'giraffe-shape47', 'giraffe-shape48',
      'giraffe-shape49', 'giraffe-shape50', 'giraffe-shape51'
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
  }
};

const STANDALONE_PICTURE_IDS = ['butterfly', 'giraffe', 'christmasTree', 'turtle'];

const COMING_SOON_ITEMS = [
  { id: 'house', label: 'House' },
  { id: 'fish', label: 'Fish' },
  { id: 'land', label: 'Land World' },
  { id: 'sea', label: 'Sea World' }
];

const ALL_PICTURE_IDS = Object.keys(PICTURE_CATALOG);
