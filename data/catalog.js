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
    neighbors: {
      'leftUpperSpot': ['leftUpperOval', 'leftUpperBlob', 'leftUpperDot', 'leftUpperInner'],
      'leftUpperOval': ['leftUpperSpot', 'leftUpperBlob', 'leftUpperDot', 'leftUpperInner'],
      'leftUpperBlob': ['leftUpperSpot', 'leftUpperOval', 'leftUpperDot', 'leftUpperInner'],
      'leftUpperDot': ['leftUpperSpot', 'leftUpperOval', 'leftUpperBlob', 'leftUpperInner'],
      'leftUpperInner': ['leftUpperSpot', 'leftUpperOval', 'leftUpperBlob', 'leftUpperDot'],
      'rightUpperSpot': ['rightUpperOval', 'rightUpperBlob', 'rightUpperDot', 'rightUpperInner'],
      'rightUpperOval': ['rightUpperSpot', 'rightUpperBlob', 'rightUpperDot', 'rightUpperInner'],
      'rightUpperBlob': ['rightUpperSpot', 'rightUpperOval', 'rightUpperDot', 'rightUpperInner'],
      'rightUpperDot': ['rightUpperSpot', 'rightUpperOval', 'rightUpperBlob', 'rightUpperInner'],
      'rightUpperInner': ['rightUpperSpot', 'rightUpperOval', 'rightUpperBlob', 'rightUpperDot'],
      'leftLowerSpot': ['leftLowerOval', 'leftLowerBlob', 'leftLowerMid'],
      'leftLowerOval': ['leftLowerSpot', 'leftLowerBlob', 'leftLowerMid'],
      'leftLowerBlob': ['leftLowerSpot', 'leftLowerOval', 'leftLowerMid'],
      'leftLowerMid': ['leftLowerSpot', 'leftLowerOval', 'leftLowerBlob'],
      'rightLowerSpot': ['rightLowerOval', 'rightLowerBlob', 'rightLowerMid'],
      'rightLowerOval': ['rightLowerSpot', 'rightLowerBlob', 'rightLowerMid'],
      'rightLowerBlob': ['rightLowerSpot', 'rightLowerOval', 'rightLowerMid'],
      'rightLowerMid': ['rightLowerSpot', 'rightLowerOval', 'rightLowerBlob']
    }
  },
  giraffe: {
    name: 'Giraffe',
    viewBox: '0 0 1024 618',
    sections: [
      'giraffe-shape01', 'giraffe-shape02', 'giraffe-shape03', 'giraffe-shape04', 'giraffe-shape05', 'giraffe-shape06', 'giraffe-shape07', 'giraffe-shape08',
      'giraffe-shape09', 'giraffe-shape10', 'giraffe-shape11', 'giraffe-shape12', 'giraffe-shape13', 'giraffe-shape14', 'giraffe-shape15', 'giraffe-shape16',
      'giraffe-shape17', 'giraffe-shape18', 'giraffe-shape19', 'giraffe-shape20', 'giraffe-shape21', 'giraffe-shape22', 'giraffe-shape23', 'giraffe-shape24',
      'giraffe-shape25', 'giraffe-shape26', 'giraffe-shape27', 'giraffe-shape28', 'giraffe-shape29', 'giraffe-shape30', 'giraffe-shape31', 'giraffe-shape32',
      'giraffe-shape33', 'giraffe-shape34', 'giraffe-shape35', 'giraffe-shape36', 'giraffe-shape37', 'giraffe-shape38', 'giraffe-shape39', 'giraffe-shape40',
      'giraffe-shape41', 'giraffe-shape42', 'giraffe-shape43', 'giraffe-shape44', 'giraffe-shape45', 'giraffe-shape46', 'giraffe-shape47', 'giraffe-shape48',
      'giraffe-shape49', 'giraffe-shape50', 'giraffe-shape51', 'giraffe-shape52', 'giraffe-shape53', 'giraffe-shape54', 'giraffe-shape55', 'giraffe-shape56',
      'giraffe-shape57', 'giraffe-shape58', 'giraffe-shape59', 'giraffe-shape60', 'giraffe-shape61', 'giraffe-shape62', 'giraffe-shape63', 'giraffe-shape64',
      'giraffe-shape65', 'giraffe-shape66', 'giraffe-shape67', 'giraffe-shape68', 'giraffe-shape69', 'giraffe-shape70', 'giraffe-shape71', 'giraffe-shape72',
      'giraffe-shape73', 'giraffe-shape74', 'giraffe-shape75', 'giraffe-shape76', 'giraffe-shape77'
    ],
    neighbors: {
      'giraffe-shape02': ['giraffe-shape42', 'giraffe-shape58'],
      'giraffe-shape03': ['giraffe-shape72', 'giraffe-shape77'],
      'giraffe-shape04': ['giraffe-shape16', 'giraffe-shape06'],
      'giraffe-shape05': ['giraffe-shape16', 'giraffe-shape07'],
      'giraffe-shape06': ['giraffe-shape16', 'giraffe-shape07'],
      'giraffe-shape07': ['giraffe-shape16', 'giraffe-shape05'],
      'giraffe-shape08': ['giraffe-shape35', 'giraffe-shape04'],
      'giraffe-shape09': ['giraffe-shape38', 'giraffe-shape11'],
      'giraffe-shape10': ['giraffe-shape15', 'giraffe-shape20'],
      'giraffe-shape11': ['giraffe-shape49', 'giraffe-shape47'],
      'giraffe-shape12': ['giraffe-shape20', 'giraffe-shape10'],
      'giraffe-shape13': ['giraffe-shape17', 'giraffe-shape29'],
      'giraffe-shape14': ['giraffe-shape26', 'giraffe-shape17'],
      'giraffe-shape15': ['giraffe-shape10', 'giraffe-shape18'],
      'giraffe-shape16': ['giraffe-shape04', 'giraffe-shape07'],
      'giraffe-shape17': ['giraffe-shape13', 'giraffe-shape14'],
      'giraffe-shape18': ['giraffe-shape19', 'giraffe-shape15'],
      'giraffe-shape19': ['giraffe-shape18', 'giraffe-shape26'],
      'giraffe-shape20': ['giraffe-shape12', 'giraffe-shape10'],
      'giraffe-shape21': ['giraffe-shape24', 'giraffe-shape27'],
      'giraffe-shape22': ['giraffe-shape29', 'giraffe-shape62'],
      'giraffe-shape23': ['giraffe-shape31', 'giraffe-shape58'],
      'giraffe-shape24': ['giraffe-shape21', 'giraffe-shape27'],
      'giraffe-shape25': ['giraffe-shape35', 'giraffe-shape04'],
      'giraffe-shape26': ['giraffe-shape14', 'giraffe-shape19'],
      'giraffe-shape27': ['giraffe-shape30', 'giraffe-shape24'],
      'giraffe-shape28': ['giraffe-shape66', 'giraffe-shape36'],
      'giraffe-shape29': ['giraffe-shape22', 'giraffe-shape13'],
      'giraffe-shape30': ['giraffe-shape32', 'giraffe-shape27'],
      'giraffe-shape31': ['giraffe-shape23', 'giraffe-shape42'],
      'giraffe-shape32': ['giraffe-shape34', 'giraffe-shape30'],
      'giraffe-shape33': ['giraffe-shape54', 'giraffe-shape36'],
      'giraffe-shape34': ['giraffe-shape40', 'giraffe-shape32'],
      'giraffe-shape35': ['giraffe-shape08', 'giraffe-shape25'],
      'giraffe-shape36': ['giraffe-shape28', 'giraffe-shape33'],
      'giraffe-shape37': ['giraffe-shape51', 'giraffe-shape42'],
      'giraffe-shape38': ['giraffe-shape71', 'giraffe-shape52'],
      'giraffe-shape39': ['giraffe-shape51', 'giraffe-shape45'],
      'giraffe-shape40': ['giraffe-shape43', 'giraffe-shape34'],
      'giraffe-shape41': ['giraffe-shape58', 'giraffe-shape23'],
      'giraffe-shape42': ['giraffe-shape58', 'giraffe-shape37'],
      'giraffe-shape43': ['giraffe-shape46', 'giraffe-shape40'],
      'giraffe-shape44': ['giraffe-shape63', 'giraffe-shape48'],
      'giraffe-shape45': ['giraffe-shape61', 'giraffe-shape39'],
      'giraffe-shape46': ['giraffe-shape50', 'giraffe-shape43'],
      'giraffe-shape47': ['giraffe-shape49', 'giraffe-shape54'],
      'giraffe-shape48': ['giraffe-shape61', 'giraffe-shape45'],
      'giraffe-shape49': ['giraffe-shape54', 'giraffe-shape47'],
      'giraffe-shape50': ['giraffe-shape55', 'giraffe-shape46'],
      'giraffe-shape51': ['giraffe-shape37', 'giraffe-shape39'],
      'giraffe-shape52': ['giraffe-shape38', 'giraffe-shape71'],
      'giraffe-shape53': ['giraffe-shape62', 'giraffe-shape55'],
      'giraffe-shape54': ['giraffe-shape49', 'giraffe-shape33'],
      'giraffe-shape55': ['giraffe-shape62', 'giraffe-shape50'],
      'giraffe-shape56': ['giraffe-shape60', 'giraffe-shape59'],
      'giraffe-shape57': ['giraffe-shape59', 'giraffe-shape60'],
      'giraffe-shape58': ['giraffe-shape42', 'giraffe-shape41'],
      'giraffe-shape59': ['giraffe-shape57', 'giraffe-shape60'],
      'giraffe-shape60': ['giraffe-shape56', 'giraffe-shape59'],
      'giraffe-shape61': ['giraffe-shape45', 'giraffe-shape48'],
      'giraffe-shape62': ['giraffe-shape55', 'giraffe-shape53'],
      'giraffe-shape63': ['giraffe-shape44', 'giraffe-shape48'],
      'giraffe-shape64': ['giraffe-shape69', 'giraffe-shape75'],
      'giraffe-shape65': ['giraffe-shape72', 'giraffe-shape67'],
      'giraffe-shape66': ['giraffe-shape28', 'giraffe-shape52'],
      'giraffe-shape67': ['giraffe-shape74', 'giraffe-shape65'],
      'giraffe-shape68': ['giraffe-shape72', 'giraffe-shape75'],
      'giraffe-shape69': ['giraffe-shape64', 'giraffe-shape73'],
      'giraffe-shape70': ['giraffe-shape76', 'giraffe-shape73'],
      'giraffe-shape71': ['giraffe-shape38', 'giraffe-shape52'],
      'giraffe-shape72': ['giraffe-shape68', 'giraffe-shape65'],
      'giraffe-shape73': ['giraffe-shape70', 'giraffe-shape69'],
      'giraffe-shape74': ['giraffe-shape77', 'giraffe-shape67'],
      'giraffe-shape75': ['giraffe-shape68', 'giraffe-shape64'],
      'giraffe-shape76': ['giraffe-shape70', 'giraffe-shape77'],
      'giraffe-shape77': ['giraffe-shape76', 'giraffe-shape74']
    }
  },
  house: {
    name: 'House',
    viewBox: '0 0 1024 574',
    sections: [
      'house-shape01', 'house-shape02', 'house-shape03', 'house-shape04', 'house-shape05', 'house-shape06', 'house-shape07', 'house-shape08',
      'house-shape09', 'house-shape10', 'house-shape11', 'house-shape12', 'house-shape13', 'house-shape14', 'house-shape15', 'house-shape16',
      'house-shape17', 'house-shape18', 'house-shape19', 'house-shape20', 'house-shape21', 'house-shape22', 'house-shape23', 'house-shape24',
      'house-shape25', 'house-shape26', 'house-shape27', 'house-shape28', 'house-shape29', 'house-shape30', 'house-shape31', 'house-shape32',
      'house-shape33', 'house-shape34', 'house-shape35', 'house-shape36', 'house-shape37', 'house-shape38', 'house-shape39', 'house-shape40',
      'house-shape41', 'house-shape42', 'house-shape43', 'house-shape44', 'house-shape45', 'house-shape46'
    ],
    neighbors: {
      'house-shape01': ['house-shape03', 'house-shape02'],
      'house-shape02': ['house-shape06', 'house-shape01'],
      'house-shape03': ['house-shape01'],
      'house-shape06': ['house-shape28', 'house-shape02'],
      'house-shape07': ['house-shape16', 'house-shape09'],
      'house-shape08': ['house-shape16', 'house-shape10'],
      'house-shape09': ['house-shape16', 'house-shape10'],
      'house-shape10': ['house-shape16', 'house-shape08'],
      'house-shape11': ['house-shape38', 'house-shape07'],
      'house-shape12': ['house-shape19', 'house-shape23'],
      'house-shape13': ['house-shape23', 'house-shape12'],
      'house-shape15': ['house-shape20', 'house-shape34'],
      'house-shape16': ['house-shape07', 'house-shape10'],
      'house-shape17': ['house-shape35', 'house-shape20'],
      'house-shape18': ['house-shape25', 'house-shape26'],
      'house-shape19': ['house-shape12', 'house-shape21'],
      'house-shape20': ['house-shape15', 'house-shape17'],
      'house-shape21': ['house-shape22', 'house-shape19'],
      'house-shape22': ['house-shape21', 'house-shape35'],
      'house-shape23': ['house-shape13', 'house-shape12'],
      'house-shape24': ['house-shape38', 'house-shape07'],
      'house-shape25': ['house-shape26', 'house-shape29'],
      'house-shape26': ['house-shape25', 'house-shape30'],
      'house-shape27': ['house-shape31', 'house-shape33'],
      'house-shape28': ['house-shape06'],
      'house-shape29': ['house-shape30', 'house-shape25'],
      'house-shape30': ['house-shape29', 'house-shape26'],
      'house-shape31': ['house-shape27', 'house-shape33'],
      'house-shape32': ['house-shape34', 'house-shape44'],
      'house-shape33': ['house-shape31', 'house-shape36'],
      'house-shape34': ['house-shape32', 'house-shape15'],
      'house-shape35': ['house-shape17', 'house-shape22'],
      'house-shape36': ['house-shape37', 'house-shape33'],
      'house-shape37': ['house-shape39', 'house-shape36'],
      'house-shape38': ['house-shape11', 'house-shape24'],
      'house-shape39': ['house-shape40', 'house-shape37'],
      'house-shape40': ['house-shape41', 'house-shape39'],
      'house-shape41': ['house-shape42', 'house-shape40'],
      'house-shape42': ['house-shape43', 'house-shape41'],
      'house-shape43': ['house-shape45', 'house-shape42'],
      'house-shape44': ['house-shape46', 'house-shape45'],
      'house-shape45': ['house-shape46', 'house-shape43'],
      'house-shape46': ['house-shape45', 'house-shape44']
    }
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

const COMING_SOON_ITEMS = [
  { id: 'fish', label: 'Fish' },
  { id: 'land', label: 'Land World' }
];

const ALL_PICTURE_IDS = Object.keys(PICTURE_CATALOG);
