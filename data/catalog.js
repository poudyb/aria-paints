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
    viewBox: '0 0 1024 576',
    sections: [
      'sunRays', 'sunCenter',
      'flowerStem', 'flowerLeafLeft', 'flowerLeafRight',
      'flowerPetal1', 'flowerPetal2', 'flowerPetal3', 'flowerPetal4', 'flowerCenter',
      'palmTrunk', 'palmFrond1', 'palmFrond2', 'palmFrond3', 'palmFrond4', 'palmFrond5', 'palmFrond6',
      'roof', 'chimney', 'atticWindow', 'houseWall',
      'windowPane1', 'windowPane2', 'windowPane3', 'windowPane4', 'door',
      'bowLoopLeft', 'bowLoopRight', 'bowTailLeft', 'bowTailRight', 'bowHeart'
    ],
    neighbors: {
      // Sun: intentionally no neighbors — the whole ray ring is a single
      // compound path, and the center circle is its own second element.
      // Bow: one tap anywhere colors the entire bow.
      'bowLoopLeft': ['bowLoopRight', 'bowTailLeft', 'bowTailRight', 'bowHeart'],
      'bowLoopRight': ['bowLoopLeft', 'bowTailLeft', 'bowTailRight', 'bowHeart'],
      'bowTailLeft': ['bowLoopLeft', 'bowLoopRight', 'bowTailRight', 'bowHeart'],
      'bowTailRight': ['bowLoopLeft', 'bowLoopRight', 'bowTailLeft', 'bowHeart'],
      'bowHeart': ['bowLoopLeft', 'bowLoopRight', 'bowTailLeft', 'bowTailRight'],
      // Flower: a petal colors its two adjacent petals; leaves pair with stem.
      'flowerPetal1': ['flowerPetal2', 'flowerPetal4'],
      'flowerPetal2': ['flowerPetal1', 'flowerPetal3'],
      'flowerPetal3': ['flowerPetal2', 'flowerPetal4'],
      'flowerPetal4': ['flowerPetal3', 'flowerPetal1'],
      'flowerStem': ['flowerLeafLeft', 'flowerLeafRight'],
      'flowerLeafLeft': ['flowerStem', 'flowerLeafRight'],
      'flowerLeafRight': ['flowerStem', 'flowerLeafLeft'],
      // House: roof pairs with chimney; a window pane colors all four panes.
      'roof': ['chimney'],
      'chimney': ['roof'],
      'windowPane1': ['windowPane2', 'windowPane3', 'windowPane4'],
      'windowPane2': ['windowPane1', 'windowPane3', 'windowPane4'],
      'windowPane3': ['windowPane1', 'windowPane2', 'windowPane4'],
      'windowPane4': ['windowPane1', 'windowPane2', 'windowPane3'],
      // Palm: a frond colors its adjacent fronds.
      'palmFrond1': ['palmFrond2'],
      'palmFrond2': ['palmFrond1', 'palmFrond3'],
      'palmFrond3': ['palmFrond2', 'palmFrond4'],
      'palmFrond4': ['palmFrond3', 'palmFrond5'],
      'palmFrond5': ['palmFrond4', 'palmFrond6'],
      'palmFrond6': ['palmFrond5']
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
    name: 'Seaworld',
    viewBox: '0 0 1000 600',
    sections: [
      'seaworld-octoHead', 'seaworld-octoTent1', 'seaworld-octoTent2', 'seaworld-octoTent3', 'seaworld-octoTent4', 'seaworld-octoTent5', 'seaworld-octoTent6',
      'seaworld-fishBody', 'seaworld-fishTail', 'seaworld-fishFinTop', 'seaworld-fishFinBottom',
      'seaworld-dolphinBody', 'seaworld-dolphinBelly', 'seaworld-dolphinFinDorsal', 'seaworld-dolphinFlipper', 'seaworld-dolphinTail', 'seaworld-dolphinSplash',
      'seaworld-crabBody', 'seaworld-crabClawLeft', 'seaworld-crabClawRight', 'seaworld-crabLegsLeft', 'seaworld-crabLegsRight', 'seaworld-crabEyeLeft', 'seaworld-crabEyeRight',
      'seaworld-whaleBody', 'seaworld-whaleBelly', 'seaworld-whaleTail', 'seaworld-whaleSpout'
    ],
    // Neighbor groups stay inside one animal so a clumsy tap never colors a
    // different creature. The blue wave background is decor, not a section.
    neighbors: {
      // Octopus: head pairs with the middle tentacles; tentacles chain sideways.
      'seaworld-octoHead': ['seaworld-octoTent3', 'seaworld-octoTent4'],
      'seaworld-octoTent1': ['seaworld-octoTent2', 'seaworld-octoHead'],
      'seaworld-octoTent2': ['seaworld-octoTent1', 'seaworld-octoTent3'],
      'seaworld-octoTent3': ['seaworld-octoTent2', 'seaworld-octoHead'],
      'seaworld-octoTent4': ['seaworld-octoTent5', 'seaworld-octoHead'],
      'seaworld-octoTent5': ['seaworld-octoTent4', 'seaworld-octoTent6'],
      'seaworld-octoTent6': ['seaworld-octoTent5', 'seaworld-octoHead'],
      // Fish
      'seaworld-fishBody': ['seaworld-fishFinTop', 'seaworld-fishFinBottom'],
      'seaworld-fishTail': ['seaworld-fishBody', 'seaworld-fishFinTop'],
      'seaworld-fishFinTop': ['seaworld-fishBody', 'seaworld-fishTail'],
      'seaworld-fishFinBottom': ['seaworld-fishBody', 'seaworld-fishTail'],
      // Dolphin
      'seaworld-dolphinBody': ['seaworld-dolphinFinDorsal', 'seaworld-dolphinTail'],
      'seaworld-dolphinBelly': ['seaworld-dolphinBody', 'seaworld-dolphinFlipper'],
      'seaworld-dolphinFinDorsal': ['seaworld-dolphinBody', 'seaworld-dolphinTail'],
      'seaworld-dolphinFlipper': ['seaworld-dolphinBelly', 'seaworld-dolphinBody'],
      'seaworld-dolphinTail': ['seaworld-dolphinBody', 'seaworld-dolphinSplash'],
      'seaworld-dolphinSplash': ['seaworld-dolphinTail', 'seaworld-dolphinBody'],
      // Crab
      'seaworld-crabBody': ['seaworld-crabLegsLeft', 'seaworld-crabLegsRight'],
      'seaworld-crabClawLeft': ['seaworld-crabBody', 'seaworld-crabLegsLeft'],
      'seaworld-crabClawRight': ['seaworld-crabBody', 'seaworld-crabLegsRight'],
      'seaworld-crabLegsLeft': ['seaworld-crabBody', 'seaworld-crabClawLeft'],
      'seaworld-crabLegsRight': ['seaworld-crabBody', 'seaworld-crabClawRight'],
      'seaworld-crabEyeLeft': ['seaworld-crabEyeRight', 'seaworld-crabBody'],
      'seaworld-crabEyeRight': ['seaworld-crabEyeLeft', 'seaworld-crabBody'],
      // Whale
      'seaworld-whaleBody': ['seaworld-whaleBelly', 'seaworld-whaleTail'],
      'seaworld-whaleBelly': ['seaworld-whaleBody', 'seaworld-whaleTail'],
      'seaworld-whaleTail': ['seaworld-whaleBody', 'seaworld-whaleBelly'],
      'seaworld-whaleSpout': ['seaworld-whaleBody', 'seaworld-whaleBelly']
    }
  }
};

const STANDALONE_PICTURE_IDS = ['butterfly', 'giraffe', 'christmasTree', 'turtle', 'house', 'seaworld'];

const COMING_SOON_ITEMS = [
  { id: 'fish', label: 'Fish' },
  { id: 'land', label: 'Land World' },
  { id: 'sea', label: 'Sea World' }
];

const ALL_PICTURE_IDS = Object.keys(PICTURE_CATALOG);
