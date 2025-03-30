#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\client\oreTypesInDungeons\const.py
from collections import OrderedDict
import inventorycommon.const as invConst
ORE_TYPES_BY_VALUE = (invConst.typeVeldspar,
 invConst.typeScordite,
 invConst.typePyroxeres,
 invConst.typePlagioclase,
 invConst.typeOmber,
 invConst.typeKernite,
 invConst.typeJaspet,
 invConst.typeHemorphite,
 invConst.typeHedbergite,
 invConst.typeGneiss,
 invConst.typeDarkOchre,
 invConst.typeCrokite,
 invConst.typeSpodumain,
 invConst.typeBistot,
 invConst.typeArkonor,
 invConst.typeMercoxit)
ORE_TYPES_BY_SEC_STATUS = OrderedDict()
ORE_TYPES_BY_SEC_STATUS[0.9] = (invConst.typeVeldspar,
 invConst.typePyroxeres,
 invConst.typePlagioclase,
 invConst.typeScordite)
ORE_TYPES_BY_SEC_STATUS[0.4] = (invConst.typeCrokite,
 invConst.typeDarkOchre,
 invConst.typeGneiss,
 invConst.typeHedbergite,
 invConst.typeHemorphite,
 invConst.typeJaspet,
 invConst.typeKernite,
 invConst.typeOmber,
 invConst.typePyroxeres)
ORE_TYPES_BY_SEC_STATUS[0.0] = (invConst.typeArkonor,
 invConst.typeBistot,
 invConst.typeKernite,
 invConst.typeMercoxit,
 invConst.typePyroxeres)
