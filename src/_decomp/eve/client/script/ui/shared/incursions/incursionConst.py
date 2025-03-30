#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\incursions\incursionConst.py
import utillib
from carbonui.util.color import Color
from eve.common.lib import appConst
from localization import GetByLabel
from talecommon.const import scenesTypes
SCENETYPE_DATA = {scenesTypes.staging: utillib.KeyVal(severityIcon='res:/UI/Texture/classes/Incursions/incursionStaging.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionSanshaStaging.png', hint='UI/Incursion/HUD/StagingClassHint', subTitle='UI/Incursion/HUD/SubtitleStaging'),
 scenesTypes.vanguard: utillib.KeyVal(severityIcon='res:/UI/Texture/classes/Incursions/incursionLight.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionSanshaLight.png', hint='UI/Incursion/HUD/VanguardClassHint', subTitle='UI/Incursion/HUD/SubtitleVanguard'),
 scenesTypes.assault: utillib.KeyVal(severityIcon='res:/UI/Texture/classes/Incursions/IncursionMedium.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionSanshaMedium.png', hint='UI/Incursion/HUD/AssaultClassHint', subTitle='UI/Incursion/HUD/SubtitleAssault'),
 scenesTypes.headquarters: utillib.KeyVal(severityIcon='res:/UI/Texture/classes/Incursions/incursionHeavy.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionSanshaHeavy.png', hint='UI/Incursion/HUD/HeadquarterClassHint', subTitle='UI/Incursion/HUD/SubtitleHeadquarters'),
 scenesTypes.boss: utillib.KeyVal(severityIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionHeavyInfestation.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionSanshaHeavy.png', hint='UI/Incursion/HUD/HeadquarterClassHint', subTitle='UI/Incursion/HUD/SubtitleHeadquarters'),
 scenesTypes.incursionStaging: utillib.KeyVal(severityIcon='', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionDriftersStaging.png', hint='UI/Incursion/HUD/IncursionStagingClassHint', subTitle='UI/Incursion/HUD/SubtitleIncursionStaging'),
 scenesTypes.incursionLightInfestation: utillib.KeyVal(severityIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionLightInfestation.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionDriftersLight.png', hint='UI/Incursion/HUD/IncursionLightInfestationClassHint', subTitle='UI/Incursion/HUD/SubtitleIncursionLightInfestation'),
 scenesTypes.incursionMediumInfestation: utillib.KeyVal(severityIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionMediumInfestation.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionDriftersMedium.png', hint='UI/Incursion/HUD/IncursionMediumInfestationClassHint', subTitle='UI/Incursion/HUD/SubtitleIncursionMediumInfestation'),
 scenesTypes.incursionHeavyInfestation: utillib.KeyVal(severityIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionHeavyInfestation.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionDriftersHeavy.png', hint='UI/Incursion/HUD/IncursionHeavyInfestationClassHint', subTitle='UI/Incursion/HUD/SubtitleIncursionHeavyInfestation'),
 scenesTypes.incursionFinalEncounter: utillib.KeyVal(severityIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionHeavyInfestation.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionDriftersHeavy.png', hint='UI/Incursion/HUD/IncursionHeavyInfestationClassHint', subTitle='UI/Incursion/HUD/SubtitleIncursionHeavyInfestation')}
INACTIVE_STATE = -1
INCURSION_STATES = [appConst.incursionStateEstablished, appConst.incursionStateMobilizing, appConst.incursionStateWithdrawing]
COLOR_ESTABLISHED = '#ff39b54a'
COLOR_MOBILIZING = '#fff15a24'
COLOR_WITHDRAWING = '#ffbe292f'
COLOR_BY_INCURSION_STATE = {INACTIVE_STATE: (0.5, 0.5, 0.5, 0.2),
 appConst.incursionStateEstablished: Color.HextoRGBA(COLOR_ESTABLISHED),
 appConst.incursionStateMobilizing: Color.HextoRGBA(COLOR_MOBILIZING),
 appConst.incursionStateWithdrawing: Color.HextoRGBA(COLOR_WITHDRAWING)}
NAME_BY_INCURSION_STATE = {appConst.incursionStateEstablished: GetByLabel('UI/Incursion/Journal/Established'),
 appConst.incursionStateMobilizing: GetByLabel('UI/Incursion/Journal/Mobilizing'),
 appConst.incursionStateWithdrawing: GetByLabel('UI/Incursion/Journal/Withdrawing')}
HINT_BY_INCURSION_STATE = {appConst.incursionStateEstablished: GetByLabel('UI/Incursion/Journal/EstablishedHint', color=COLOR_ESTABLISHED),
 appConst.incursionStateMobilizing: GetByLabel('UI/Incursion/Journal/MobilizingHint', color=COLOR_MOBILIZING),
 appConst.incursionStateWithdrawing: GetByLabel('UI/Incursion/Journal/WithdrawingHint', color=COLOR_WITHDRAWING)}
