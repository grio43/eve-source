#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\client\iceTypesInDungeon\const.py
from collections import OrderedDict
import eve.common.lib.appConst as appConst
import inventorycommon.const as invConst
ICE_TYPES_BY_VALUE = (invConst.typeKrystallos,
 invConst.typeGlareCrust,
 invConst.typeDarkGlitter,
 invConst.typeGelidus,
 invConst.typeThickBlueIce,
 invConst.typePristineWhiteGlaze,
 invConst.typeSmoothGlacialMass,
 invConst.typeEnrichedClearIcicle,
 invConst.typeBlueIce,
 invConst.typeWhiteGlaze,
 invConst.typeGlacialMass,
 invConst.typeClearIcicle)
UNIQUE_ICE_BY_FACTION = {appConst.factionAmarrEmpire: invConst.typeClearIcicle,
 appConst.factionCaldariState: invConst.typeWhiteGlaze,
 appConst.factionGallenteFederation: invConst.typeBlueIce,
 appConst.factionMinmatarRepublic: invConst.typeGlacialMass}
UNIQUE_ICE_BY_SEC_STATUS = OrderedDict()
UNIQUE_ICE_BY_SEC_STATUS[0.3] = (invConst.typeGlareCrust,)
UNIQUE_ICE_BY_SEC_STATUS[0.1] = (invConst.typeDarkGlitter,)
UNIQUE_ICE_BY_SEC_STATUS[0.0] = (invConst.typeGelidus, invConst.typeKrystallos)
ISOTOPES_BY_ICE_TYPE = {invConst.typeClearIcicle: invConst.typeHeliumIsotopes,
 invConst.typeWhiteGlaze: invConst.typeNitrogenIsotopes,
 invConst.typeBlueIce: invConst.typeOxygenIsotopes,
 invConst.typeGlacialMass: invConst.typeHydrogenIsotopes}
