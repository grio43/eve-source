#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\const.py
from carbonui.util.color import Color
from eve.common.lib import appConst
from evegraphics.gateLogoConst import AMARR_EMPIRE, CALDARI_STATE, GALLENTE_FEDERATION, MINMATAR_REPUBLIC
from factionwarfare.const import ADJACENCY_STATE_BACKLINE, ADJACENCY_STATE_FRONTLINE, ADJACENCY_STATE_SECONDLINE
from localization import GetByLabel
GALENTE_GREEN = Color.HextoRGBA('#FF40AA5E')
CALDARI_BLUE = Color.HextoRGBA('#FF00ACD1')
AMARR_GOLD = Color.HextoRGBA('#FFE7B815')
MINMATAR_RED = Color.HextoRGBA('#FFFE3743')
PLACEHOLDER_PINK_COLOR = Color.HextoRGBA('#FFCB3BEF')
ANGEL_COLOR = Color.HextoRGBA('#FFE1B0')
GURISTAS_COLOR = Color.HextoRGBA('#E54500')
BLUE_COLOR = Color.HextoRGBA('#FF00ACD1')
RED_COLOR = Color.HextoRGBA('#FFFE3743')
FACTION_ID_TO_COLOR_BACKGROUND = {CALDARI_STATE: 'res:/UI/Texture/classes/frontlines/progression/caldari_color_bg.png',
 AMARR_EMPIRE: 'res:/UI/Texture/classes/frontlines/progression/amarr_color_bg.png',
 MINMATAR_REPUBLIC: 'res:/UI/Texture/classes/frontlines/progression/minmatar_color_bg.png',
 GALLENTE_FEDERATION: 'res:/UI/Texture/classes/frontlines/progression/gallente_color_bg.png'}
FACTION_ID_TO_FLAT_ICON = {appConst.factionCaldariState: 'res:/UI/Texture/Classes/SkillPlan/factionButtons/iconCaldari.png',
 appConst.factionGallenteFederation: 'res:/UI/Texture/Classes/SkillPlan/factionButtons/iconGallente.png',
 appConst.factionMinmatarRepublic: 'res:/UI/Texture/Classes/SkillPlan/factionButtons/iconMinmatar.png',
 appConst.factionAmarrEmpire: 'res:/UI/Texture/Classes/SkillPlan/factionButtons/iconAmarr.png',
 appConst.factionGuristasPirates: 'res:/UI/Texture/Classes/SkillPlan/factionButtons/iconGuristas.png',
 appConst.factionAngelCartel: 'res:/UI/Texture/Classes/SkillPlan/factionButtons/iconAngels.png'}
FACTION_ID_TO_ENLIST_PROMPT = {appConst.factionCaldariState: GetByLabel('UI/FactionWarfare/frontlinesDashboard/CTACaldari'),
 appConst.factionGallenteFederation: GetByLabel('UI/FactionWarfare/frontlinesDashboard/CTAGallente'),
 appConst.factionMinmatarRepublic: GetByLabel('UI/FactionWarfare/frontlinesDashboard/CTAMinmatar'),
 appConst.factionAmarrEmpire: GetByLabel('UI/FactionWarfare/frontlinesDashboard/CTAAmarr'),
 appConst.factionAngelCartel: GetByLabel('UI/FactionWarfare/frontlinesDashboard/CTAAngels'),
 appConst.factionGuristasPirates: GetByLabel('UI/FactionWarfare/frontlinesDashboard/CTAGuristas')}
FACTION_ID_TO_COLOR = {appConst.factionCaldariState: CALDARI_BLUE,
 appConst.factionGallenteFederation: GALENTE_GREEN,
 appConst.factionMinmatarRepublic: MINMATAR_RED,
 appConst.factionAmarrEmpire: AMARR_GOLD,
 appConst.factionAngelCartel: ANGEL_COLOR,
 appConst.factionGuristasPirates: GURISTAS_COLOR}

class _AdvantageContentInfoLineData:

    def __init__(self, iconTexturePath, text, tooltipText, adjacency_settings = []):
        self.adjacency_settings = adjacency_settings
        self.tooltipText = tooltipText
        self.text = text
        self.iconTexturePath = iconTexturePath


ADVANTAGE_CONTENT_DATA = [_AdvantageContentInfoLineData('res:/UI/Texture/Shared/Brackets/beacon.png', GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/battlefieldComplexes'), GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/battlefieldComplexesTooltip'), adjacency_settings=[ADJACENCY_STATE_FRONTLINE]),
 _AdvantageContentInfoLineData('res:/UI/Texture/Shared/Brackets/beacon.png', GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/propagandaBroadcastStructure'), GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/propagandaBroadcastStructureTooltip')),
 _AdvantageContentInfoLineData('res:/UI/Texture/Shared/Brackets/beacon.png', GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/listeningOutput'), GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/listeningOutpostTooltip')),
 _AdvantageContentInfoLineData('res:/UI/Texture/Shared/Brackets/beacon.png', GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/supplyDepot'), GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/supplyDepotTooltip')),
 _AdvantageContentInfoLineData('res:/UI/Texture/Shared/Brackets/beacon.png', GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/supplyCache'), GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/supplyCacheTooltip')),
 _AdvantageContentInfoLineData('res:/UI/Texture/Shared/Brackets/beacon.png', GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/operationCenters'), GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/operationCentersTooltip'), adjacency_settings=[ADJACENCY_STATE_BACKLINE]),
 _AdvantageContentInfoLineData('res:/UI/Texture/Shared/Brackets/beacon.png', GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/rendezvouzPoint'), GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/rendezvouzPointTooltip'), adjacency_settings=[ADJACENCY_STATE_FRONTLINE, ADJACENCY_STATE_SECONDLINE])]
FACTION_ID_TO_POSTER = {appConst.factionCaldariState: 'res:/UI/Texture/classes/frontlines/portraits/caldariProp.png',
 appConst.factionGallenteFederation: 'res:/UI/Texture/classes/frontlines/portraits/gallenteProp.png',
 appConst.factionMinmatarRepublic: 'res:/UI/Texture/classes/frontlines/portraits/minmatarProp.png',
 appConst.factionAmarrEmpire: 'res:/UI/Texture/classes/frontlines/portraits/amarrProp.png'}
ADJACENCY_STATE_TO_ICON_PATH = {ADJACENCY_STATE_FRONTLINE: 'res:/UI/Texture/classes/frontlines/front_icon.png',
 ADJACENCY_STATE_SECONDLINE: 'res:/UI/Texture/classes/frontlines/HQ_icon.png',
 ADJACENCY_STATE_BACKLINE: 'res:/UI/Texture/classes/frontlines/support_icon.png'}
ADJACENCY_STATE_TO_ICON_PATH_SMALL = {ADJACENCY_STATE_FRONTLINE: 'res:/UI/Texture/classes/frontlines/front_icon_small.png',
 ADJACENCY_STATE_SECONDLINE: 'res:/UI/Texture/classes/frontlines/HQ_icon_small.png',
 ADJACENCY_STATE_BACKLINE: 'res:/UI/Texture/classes/frontlines/support_icon_small.png'}

def GetAdjacencyBrightness(adjacencyState):
    if adjacencyState == ADJACENCY_STATE_FRONTLINE:
        return 2
    if adjacencyState == ADJACENCY_STATE_SECONDLINE:
        return 1
    if adjacencyState == ADJACENCY_STATE_BACKLINE:
        return 0.2
    return 1


def GetAdjacencyOpacity(adjacencyState):
    if adjacencyState == ADJACENCY_STATE_FRONTLINE:
        return 1.0
    if adjacencyState == ADJACENCY_STATE_SECONDLINE:
        return 0.8
    if adjacencyState == ADJACENCY_STATE_BACKLINE:
        return 0.4
    return 1.0


ADVANTAGE_SWORD_BACKGROUND_TEXTURE_PATH = 'res:/UI/Texture/classes/frontlines/advantage_sword_background_rect.png'
ADVANTAGE_SWORD_RIGHT_TEXTURE_PATH = 'res:/UI/Texture/classes/frontlines/advantage_sword.png'
ADVANTAGE_SHIELD_TEXTURE_PATH = 'res:/UI/Texture/classes/frontlines/advantage_shield.png'
ADVANTAGE_ARROWS_RIGHT_TEXTURE_PATH = 'res:/UI/Texture/classes/frontlines/advantage_gauge_arrows_right.png'
FRONTLINE_TEXT = GetByLabel('UI/FactionWarfare/frontlines/frontline')
SECONDLINE_TEXT = GetByLabel('UI/FactionWarfare/frontlines/secondline')
BACKLINE_TEXT = GetByLabel('UI/FactionWarfare/frontlines/backline')
FRONTLINE_SYSTEM_TEXT = GetByLabel('UI/FactionWarfare/frontlines/FrontlineSystem')
SECONDLINE_SYSTEM_TEXT = GetByLabel('UI/FactionWarfare/frontlines/SecondlineSystem')
BACKLINE_SYSTEM_TEXT = GetByLabel('UI/FactionWarfare/frontlines/BacklineSystem')
PROGRESSION_SCREEN_FLAG_FRAME = 'res:/UI/Texture/classes/frontlines/progression/flag.png'
SYSTEM_NOT_PART_OF_WARZONE_TEXT = GetByLabel('UI/FactionWarfare/frontlinesDashboard/systemNotPartOfWarzone')
ADJACENCY_TO_DESC = {ADJACENCY_STATE_FRONTLINE: GetByLabel('UI/FactionWarfare/frontlines/frontlineDesc'),
 ADJACENCY_STATE_SECONDLINE: GetByLabel('UI/FactionWarfare/frontlines/secondlineDesc'),
 ADJACENCY_STATE_BACKLINE: GetByLabel('UI/FactionWarfare/frontlines/backlineDesc')}
ADJACENCY_TO_LABEL_TEXT = {ADJACENCY_STATE_FRONTLINE: FRONTLINE_TEXT,
 ADJACENCY_STATE_SECONDLINE: SECONDLINE_TEXT,
 ADJACENCY_STATE_BACKLINE: BACKLINE_TEXT}
ADJACENCY_TO_LABEL_SYSTEM_TEXT = {ADJACENCY_STATE_FRONTLINE: FRONTLINE_SYSTEM_TEXT,
 ADJACENCY_STATE_SECONDLINE: SECONDLINE_SYSTEM_TEXT,
 ADJACENCY_STATE_BACKLINE: BACKLINE_SYSTEM_TEXT}
