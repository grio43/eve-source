#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\client\sovHub\hubConst.py
import inventorycommon.const as invConst
from sovereignty.workforce import workforceConst
LACKING_REAGENTS = -1
LACKING_REAGENT_STARTUP = -2
LACKING_POWER = -3
LACKING_WORKFORCE = -4
SuperCapitalConstructionVFX = 'scc'
AdvancedLogisticsNetworkVFX = 'aln'
CynosauralSuppressionVFX = 'cs'
CynosauralNavigationVFX = 'cn'
TritaniumProspectSmallVFX = 'mutri_s'
TritaniumProspectMediumVFX = 'mutri_m'
TritatiumProspectLargeVFX = 'mutri_l'
PyeriteProspectingSmallVFX = 'mupye_s'
PyeriteProspectingMediumVFX = 'mupye_m'
PyeriteProspectingLargeVFX = 'mupye_l'
MexallonProspectingSmallVFX = 'mumex_s'
MexallonProspectingMediumVFX = 'mumex_m'
MexallonProspectingLargeVFX = 'mumex_l'
IsogenProspectingSmallVFX = 'muiso_s'
IsogenProspectingMediumVFX = 'muiso_m'
IsogenProspectingLargeVFX = 'muiso_l'
NocxiumProspectingSmallVFX = 'munoc_s'
NocxiumProspectingMediumVFX = 'munoc_m'
NocxiumProspectingLargeVFX = 'munoc_l'
ZydrineProspectingSmallVFX = 'muzyd_s'
ZydrineProspectingMediumVFX = 'muzyd_m'
ZydrineProspectingLargeVFX = 'muzyd_l'
MegacyteProspectingSmallVFX = 'mumeg_s'
MegacyteProspectingMediumVFX = 'mumeg_m'
MegacyteProspectingLargeVFX = 'mumeg_l'
LimitedPirateDetectionVFX = 'lpda'
StandardPirateDetectionVFX = 'spda'
ImprovedPirateDetectionVFX = 'lpda'
AdvancedPirateDetectionVFX = 'apda'
ElitePirateDetectionVFX = 'epda'
OptimizedPirateDetectionVFX = 'opda'
PopulationTransportVFX = 'sh'
UPGRADES_MAPPINGS = [[SuperCapitalConstructionVFX, invConst.typeSuperCapitalConstruction],
 [AdvancedLogisticsNetworkVFX, invConst.typeAdvancedLogisticsNetwork],
 [CynosauralSuppressionVFX, invConst.typeCynosauralSuppression],
 [CynosauralNavigationVFX, invConst.typeCynosauralNavigation],
 [TritaniumProspectSmallVFX, invConst.typeTritaniumProspectSmall],
 [TritaniumProspectMediumVFX, invConst.typeTritaniumProspectMedium],
 [TritatiumProspectLargeVFX, invConst.typeTritaniumProspectLarge],
 [PyeriteProspectingSmallVFX, invConst.typePyeriteProspectingSmall],
 [PyeriteProspectingMediumVFX, invConst.typePyeriteProspectingMedium],
 [PyeriteProspectingLargeVFX, invConst.typePyeriteProspectingLarge],
 [MexallonProspectingSmallVFX, invConst.typeMexallonProspectingSmall],
 [MexallonProspectingMediumVFX, invConst.typeMexallonProspectingMedium],
 [MexallonProspectingLargeVFX, invConst.typeMexallonProspectingLarge],
 [IsogenProspectingSmallVFX, invConst.typeIsogenProspectingSmall],
 [IsogenProspectingMediumVFX, invConst.typeIsogenProspectingMedium],
 [IsogenProspectingLargeVFX, invConst.typeIsogenProspectingLarge],
 [NocxiumProspectingSmallVFX, invConst.typeNocxiumProspectingSmall],
 [NocxiumProspectingMediumVFX, invConst.typeNocxiumProspectingMedium],
 [NocxiumProspectingLargeVFX, invConst.typeNocxiumProspectingLarge],
 [ZydrineProspectingSmallVFX, invConst.typeZydrineProspectingSmall],
 [ZydrineProspectingMediumVFX, invConst.typeZydrineProspectingMedium],
 [ZydrineProspectingLargeVFX, invConst.typeZydrineProspectingLarge],
 [MegacyteProspectingSmallVFX, invConst.typeMegacyteProspectingSmall],
 [MegacyteProspectingMediumVFX, invConst.typeMegacyteProspectingMedium],
 [MegacyteProspectingLargeVFX, invConst.typeMegacyteProspectingLarge],
 [LimitedPirateDetectionVFX, invConst.typeLimitedPirateDetection],
 [StandardPirateDetectionVFX, invConst.typeStandardPirateDetection],
 [ImprovedPirateDetectionVFX, invConst.typeImprovedPirateDetection],
 [AdvancedPirateDetectionVFX, invConst.typeAdvancedPirateDetection],
 [ElitePirateDetectionVFX, invConst.typeElitePirateDetection],
 [OptimizedPirateDetectionVFX, invConst.typePirateDetectionArrayALvl3]]
MINING_UPGRADES = [invConst.typeTritaniumProspectSmall,
 invConst.typeTritaniumProspectMedium,
 invConst.typePyeriteProspectingSmall,
 invConst.typePyeriteProspectingMedium,
 invConst.typeMexallonProspectingSmall,
 invConst.typeMexallonProspectingMedium,
 invConst.typeIsogenProspectingSmall,
 invConst.typeIsogenProspectingMedium,
 invConst.typeNocxiumProspectingSmall,
 invConst.typeNocxiumProspectingMedium,
 invConst.typeZydrineProspectingSmall,
 invConst.typeZydrineProspectingMedium,
 invConst.typeMegacyteProspectingSmall,
 invConst.typeMegacyteProspectingMedium]
WORKFORCE_MAPPINGS = {workforceConst.MODE_TRANSIT: 0.0,
 workforceConst.MODE_EXPORT: 1.0,
 workforceConst.MODE_IMPORT: 2.0}
CTRL_ON = 1.0
CTRL_OFF = 0.0
CTRL_IS_BUILT = '_01_isBuilt'
CTRL_LOW_POWER = '_01_lowPower'
CTRL_MINING = 'muActive'
CTRL_TRANSPORT_STATE = '_populationMode'
