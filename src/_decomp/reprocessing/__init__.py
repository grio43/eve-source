#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\reprocessing\__init__.py
import itertools
import evetypes
import dogma.const as dgmconst
import inventorycommon.const as invConst
NORMAL_ORES = {invConst.groupVeldspar,
 invConst.groupScordite,
 invConst.groupPyroxeres,
 invConst.groupOmber,
 invConst.groupKernite,
 invConst.groupPlagioclase,
 invConst.groupArkonor,
 invConst.groupBistot,
 invConst.groupCrokite,
 invConst.groupDarkOchre,
 invConst.groupHedbergite,
 invConst.groupHemorphite,
 invConst.groupJaspet,
 invConst.groupSpodumain,
 invConst.groupGneiss,
 invConst.groupMercoxit,
 invConst.groupDeadspaceAsteroids,
 invConst.groupTemporalResources,
 invConst.groupFluorite,
 invConst.groupTalassonite,
 invConst.groupRakovene,
 invConst.groupBezdnacine,
 invConst.groupDucinium,
 invConst.groupEifyrium,
 invConst.groupMordunium,
 invConst.groupYtirium,
 invConst.groupKylixium,
 invConst.groupNocxite,
 invConst.groupUeganite,
 invConst.groupHezorime,
 invConst.groupGriemeer}
ICE = {invConst.groupIce}
MOON_ORES = {invConst.groupUbiquitousMoonAsteroids,
 invConst.groupCommonMoonAsteroids,
 invConst.groupUncommonMoonAsteroids,
 invConst.groupRareMoonAsteroids,
 invConst.groupExceptionalMoonAsteroids}
TYPES_BY_REFINING_ATTRIBUTE = {dgmconst.attributeRefiningYieldNormalOre: set(itertools.chain(*(evetypes.GetTypeIDsByGroup(groupID) for groupID in NORMAL_ORES))),
 dgmconst.attributeRefiningYieldMoonOre: set(itertools.chain(*(evetypes.GetTypeIDsByGroup(groupID) for groupID in MOON_ORES))),
 dgmconst.attributeRefiningYieldIce: set(itertools.chain(*(evetypes.GetTypeIDsByGroup(groupID) for groupID in ICE)))}
