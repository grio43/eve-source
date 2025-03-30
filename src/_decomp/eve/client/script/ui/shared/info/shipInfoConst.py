#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\shipInfoConst.py
import eveicon
import evetypes
import localization
import mathext
import math
from eve.client.script.ui.shared.cloneGrade import open_omega_upgrade_window, ORIGIN_SHOWINFO
from eve.client.script.ui.shared.tooltip.itemObject import ItemObject
from eve.common.lib import appConst
TAB_OVERVIEW = 1
TAB_ATTRIBUTES = 2
TAB_FITTING = 3
TAB_SKILLS = 4
TAB_VARIATIONS = 5
TAB_INDUSTRY = 6
TAB_SKINS = 7
INFO_TABS = [TAB_OVERVIEW,
 TAB_ATTRIBUTES,
 TAB_FITTING,
 TAB_SKILLS,
 TAB_VARIATIONS,
 TAB_INDUSTRY,
 TAB_SKINS]
FULLY_MINIMIZED = 0
MINIMIZED = 1
EXPANDED = 2
CONTENT_PADDING = {FULLY_MINIMIZED: 8,
 MINIMIZED: 8,
 EXPANDED: 24}
LIGHT_RIG_GRAPHIC_ID = 27949
ANIM_DURATION_SMALL = 0.8
ANIM_DURATION_MID = 0.9
ANIM_DURATION_LONG = 2.5
MAX_MASS = 2500000000L
LOCKED_ICON = eveicon.mastery_locked
UNLOCKED_ICON = eveicon.mastery_level_0
MASTERY_ICONS = {1: eveicon.mastery_level_1,
 2: eveicon.mastery_level_2,
 3: eveicon.mastery_level_3,
 4: eveicon.mastery_level_4,
 5: eveicon.mastery_level_5}

def GetAnimDuration(mass):
    return GetMassBasedLerp(mass, ANIM_DURATION_SMALL, ANIM_DURATION_LONG)


def GetMassBasedSoundOffset(mass, soundOffsetMin = 0.4, soundOffsetMax = 0.55):
    return GetMassBasedLerp(mass, soundOffsetMin, soundOffsetMax)


def GetMassBasedLerp(mass, a, b):
    ratio = mass / MAX_MASS
    ratio = 1 - ratio
    ratio = mathext.pow(ratio, 5)
    ratio = 1 - ratio
    return mathext.lerp(a, b, ratio)


SOUND_PANEL_FADE_IN = 'ship_info_window_fade_in_play'
SOUND_INSURANCE = 'ship_info_window_button_insurance_play'
SOUND_INSURANCE_SELECT = 'ship_info_window_button_select_play'
SOUND_ROTATION_SMALL = ('ship_info_window_ship_small_move_play', 'ship_info_window_ship_small_move_stop')
SOUND_ROTATION_MEDIUM = ('ship_info_window_ship_medium_move_play', 'ship_info_window_ship_medium_move_stop')
SOUND_ROTATION_LARGE = ('ship_info_window_ship_large_move_play', 'ship_info_window_ship_large_move_stop')
SOUND_GROUP_SMALL = [appConst.groupCapsule,
 appConst.groupCorvette,
 appConst.groupShuttle,
 appConst.groupFrigate,
 appConst.groupAssaultFrigate,
 appConst.groupLogisticsFrigate,
 appConst.groupExpeditionFrigate,
 appConst.groupInterceptor,
 appConst.groupElectronicAttackShips,
 appConst.groupCovertOps,
 appConst.groupStealthBomber,
 appConst.groupDestroyer,
 appConst.groupCommandDestroyer,
 appConst.groupTacticalDestroyer,
 appConst.groupInterdictor]
SOUND_GROUP_MEDIUM = [appConst.groupCruiser,
 appConst.groupCombatReconShip,
 appConst.groupForceReconShip,
 appConst.groupHeavyAssaultCruiser,
 appConst.groupHeavyInterdictors,
 appConst.groupLogistics,
 appConst.groupStrategicCruiser,
 appConst.groupBattlecruiser,
 appConst.groupAttackBattlecruiser,
 appConst.groupCommandShip,
 appConst.groupIndustrial,
 appConst.groupTransportShip,
 appConst.groupMiningBarge,
 appConst.groupExhumer,
 appConst.groupIndustrialCommandShip,
 appConst.groupFlagCruiser]
SOUND_GROUP_LARGE = [appConst.groupCapitalIndustrialShip,
 appConst.groupFreighter,
 appConst.groupJumpFreighter,
 appConst.groupDreadnought,
 appConst.groupLancerDreadnought,
 appConst.groupForceAux,
 appConst.groupCarrier,
 appConst.groupSupercarrier,
 appConst.groupTitan,
 appConst.groupBattleship,
 appConst.groupBlackOps,
 appConst.groupMarauders]

def get_sound_by_type_id(typeID):
    groupID = evetypes.GetGroupID(typeID)
    if groupID in SOUND_GROUP_SMALL:
        return SOUND_ROTATION_SMALL
    if groupID in SOUND_GROUP_MEDIUM:
        return SOUND_ROTATION_MEDIUM
    if groupID in SOUND_GROUP_LARGE:
        return SOUND_ROTATION_LARGE


FRONT = 0
REAR = 1
RIGHT = 2
LEFT = 3
FRONT_RIGHT = 4
FRONT_LEFT = 5
REAR_RIGHT = 6
REAR_LEFT = 7
DOWN_FRONT = 8
DOWN_REAR = 9
DOWN_RIGHT = 10
DOWN_LEFT = 11
DOWN_FRONT_LEFT = 12
DOWN_FRONT_RIGHT = 13
DOWN_REAR_LEFT = 14
DOWN_REAR_RIGHT = 15
TOP_DOWN_NOSE_UP = 16
TOP_DOWN_NOSE_DOWN = 17
TOP_DOWN_NOSE_RIGHT = 18
TOP_DOWN_NOSE_LEFT = 19
TOP_DOWN_NOSE_UP_ALT = 20
UP_FRONT_LEFT = 21
ANGLE_FITTING = 22
ANGLE_SKILLS = 23
ANGLE_SKINS = 24
TALL_SHIP_POSITION_REPLACEMENTS = {TOP_DOWN_NOSE_UP: LEFT,
 TOP_DOWN_NOSE_LEFT: LEFT,
 TOP_DOWN_NOSE_RIGHT: RIGHT,
 TOP_DOWN_NOSE_DOWN: RIGHT,
 TOP_DOWN_NOSE_UP_ALT: LEFT}
WIDE_SHIP_POSITION_REPLACEMENTS = {TOP_DOWN_NOSE_UP: TOP_DOWN_NOSE_RIGHT,
 TOP_DOWN_NOSE_DOWN: TOP_DOWN_NOSE_LEFT,
 TOP_DOWN_NOSE_UP_ALT: TOP_DOWN_NOSE_LEFT}
SHIP_POSITIONS = {FRONT: (90, 180),
 REAR: (90, 0),
 RIGHT: (90, 90),
 LEFT: (90, 270),
 FRONT_LEFT: (90, 135),
 FRONT_RIGHT: (90, 45),
 DOWN_FRONT: (72, 180),
 DOWN_REAR: (72, 0),
 DOWN_RIGHT: (72, 45),
 DOWN_LEFT: (72, 135),
 DOWN_FRONT_LEFT: (65, -225),
 DOWN_FRONT_RIGHT: (72, 205),
 DOWN_REAR_LEFT: (72, -20),
 DOWN_REAR_RIGHT: (72, 20),
 TOP_DOWN_NOSE_UP: (0, 0),
 TOP_DOWN_NOSE_DOWN: (0, 180),
 TOP_DOWN_NOSE_RIGHT: (0, 90),
 TOP_DOWN_NOSE_LEFT: (0, 270),
 TOP_DOWN_NOSE_UP_ALT: (0, 0),
 UP_FRONT_LEFT: (120, 135),
 ANGLE_FITTING: (35, -225),
 ANGLE_SKILLS: (35, 225),
 ANGLE_SKINS: (72, -205)}
NO_FACTION_BACKGROUND = 99
FACTION_BACKGROUND_LOGOS_IDS = {appConst.factionAmarrEmpire: 0,
 appConst.factionCaldariState: 1,
 appConst.factionMinmatarRepublic: 2,
 appConst.factionGallenteFederation: 3,
 appConst.factionGuristasPirates: 4,
 appConst.factionSistersOfEVE: 5,
 appConst.factionAngelCartel: 6,
 appConst.factionSanshasNation: 7,
 appConst.factionTheBloodRaiderCovenant: 8,
 appConst.factionTriglavian: 9,
 appConst.factionSerpentis: 10,
 appConst.factionORE: 11,
 appConst.factionMordusLegion: 12,
 appConst.factionEDENCOM: 13,
 appConst.factionTheSyndicate: 14,
 appConst.factionAmmatar: 15,
 appConst.factionDeathless: 16,
 appConst.factionCONCORDAssembly: 17,
 appConst.factionKhanidKingdom: 18,
 appConst.factionSocietyOfConsciousThought: 19,
 appConst.factionInterBus: 20,
 appConst.factionJoveEmpire: 21}

def get_faction_background(factionID):
    if factionID in FACTION_BACKGROUND_LOGOS_IDS:
        return FACTION_BACKGROUND_LOGOS_IDS[factionID]
    return NO_FACTION_BACKGROUND


def get_mastery_level_icon_and_message(typeID):
    skillSvc = sm.GetService('skills')
    certSvc = sm.GetService('certificates')
    unlocked = skillSvc.IsSkillRequirementMet(typeID)
    masteryLevel = certSvc.GetCurrCharMasteryLevel(typeID)
    itemObject = ItemObject(typeID)
    on_click = None
    if itemObject.NeedsOmegaUpgrade():
        texturePath = eveicon.mastery_omega_locked
        message = localization.GetByLabel('UI/InfoWindow/OmegaRequired')
        on_click = lambda *args, **kwargs: open_omega_upgrade_window(origin=ORIGIN_SHOWINFO)
    elif not unlocked:
        texturePath = LOCKED_ICON
        message = localization.GetByLabel('UI/InfoWindow/SkillRequirementsNotMet')
    elif masteryLevel == 0:
        texturePath = UNLOCKED_ICON
        message = localization.GetByLabel('UI/InfoWindow/SkillRequirementsMet')
    else:
        texturePath = MASTERY_ICONS[masteryLevel]
        message = localization.GetByLabel('UI/InfoWindow/MasteryLevelUnlocked', level=masteryLevel)
    return (texturePath, message, on_click)


KILLMARKS_AMARR = (eveicon.killmarks_amarr_1, eveicon.killmarks_amarr_2, eveicon.killmarks_amarr_3)
KILLMARKS_GALLENTE = (eveicon.killmarks_gallente_1, eveicon.killmarks_gallente_2, eveicon.killmarks_gallente_3)
KILLMARKS_CALDARI = (eveicon.killmarks_caldari_1, eveicon.killmarks_caldari_2, eveicon.killmarks_caldari_3)
KILLMARKS_MINMATAR = (eveicon.killmarks_minmatar_1, eveicon.killmarks_minmatar_2, eveicon.killmarks_minmatar_3)
KILLMARKS_ANGEL = (eveicon.killmarks_angel_cartel_1, eveicon.killmarks_angel_cartel_2, eveicon.killmarks_angel_cartel_3)
KILLMARKS_SANSHA = (eveicon.killmarks_sansha_1, eveicon.killmarks_sansha_2, eveicon.killmarks_sansha_3)
KILLMARKS_SOE = (eveicon.killmarks_soe_1, eveicon.killmarks_soe_2, eveicon.killmarks_soe_3)
KILLMARKS_CONCORD = (eveicon.killmarks_concord_1, eveicon.killmarks_concord_2, eveicon.killmarks_concord_3)
KILLMARKS_TRIGLAVIAN = (eveicon.killmarks_triglavian_1, eveicon.killmarks_triglavian_2, eveicon.killmarks_triglavian_3)
KILLMARKS_MORDUS = (eveicon.killmarks_mordus_legion_1, eveicon.killmarks_mordus_legion_2, eveicon.killmarks_mordus_legion_3)
KILLMARKS_JOVE = (eveicon.killmarks_jove_1, eveicon.killmarks_jove_2, eveicon.killmarks_jove_3)
KILLMARKS_SOCT = (eveicon.killmarks_soct_1, eveicon.killmarks_soct_2, eveicon.killmarks_soct_3)
DEFAULT_KILLMARKS = KILLMARKS_JOVE
KILLMARKS_BY_FACTION = {appConst.factionAmarrEmpire: KILLMARKS_AMARR,
 appConst.factionCaldariState: KILLMARKS_CALDARI,
 appConst.factionMinmatarRepublic: KILLMARKS_MINMATAR,
 appConst.factionGallenteFederation: KILLMARKS_GALLENTE,
 appConst.factionGuristasPirates: KILLMARKS_CALDARI,
 appConst.factionSistersOfEVE: KILLMARKS_SOE,
 appConst.factionAngelCartel: KILLMARKS_ANGEL,
 appConst.factionSanshasNation: KILLMARKS_SANSHA,
 appConst.factionTheBloodRaiderCovenant: KILLMARKS_AMARR,
 appConst.factionTriglavian: KILLMARKS_TRIGLAVIAN,
 appConst.factionSerpentis: KILLMARKS_GALLENTE,
 appConst.factionORE: KILLMARKS_JOVE,
 appConst.factionMordusLegion: KILLMARKS_MORDUS,
 appConst.factionEDENCOM: KILLMARKS_JOVE,
 appConst.factionTheSyndicate: KILLMARKS_GALLENTE,
 appConst.factionAmmatar: KILLMARKS_AMARR,
 appConst.factionDeathless: KILLMARKS_JOVE,
 appConst.factionCONCORDAssembly: KILLMARKS_CONCORD,
 appConst.factionKhanidKingdom: KILLMARKS_AMARR,
 appConst.factionSocietyOfConsciousThought: KILLMARKS_SOCT,
 appConst.factionInterBus: KILLMARKS_JOVE}

def get_killmark_for_faction(faction_id, tier = 2, default = DEFAULT_KILLMARKS):
    return KILLMARKS_BY_FACTION.get(faction_id, default)[tier]


def get_killmarks_for_faction(faction_id, default = DEFAULT_KILLMARKS):
    return KILLMARKS_BY_FACTION.get(faction_id, default)
