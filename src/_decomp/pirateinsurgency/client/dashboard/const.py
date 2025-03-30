#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pirateinsurgency\client\dashboard\const.py
import carbonui
import eveicon
from carbonui import uiconst, TextAlign
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.common.lib import appConst
from eve.common.script.util import facwarCommon
from eveui import Sprite
from fwwarzone.client.dashboard.const import FACTION_ID_TO_COLOR
from localization import GetByLabel
SUPPRESSION_STAGES = 5
CORRUPTION_STAGES = 5
WARZONE_ID_TO_PIRATE_FACTION_ID = {2: appConst.factionGuristasPirates,
 1: appConst.factionAngelCartel}
_CORRUPTION_FILL_COLOR = Color.HextoRGBA('#7E8A00')
_CORRUPTION_STROKE_COLOR = Color.HextoRGBA('#9EFF00')
_SUPPRESSION_FILL_COLOR = eveColor.WHITE
_SUPPRESSION_STROKE_COLOR = eveColor.WHITE
_CORRUPTION_STAGE_TO_ICON = {0: 'res:/UI/Texture/classes/pirateinsurgencies/widgets/corr_0.png',
 1: 'res:/UI/Texture/classes/pirateinsurgencies/widgets/corr_1.png',
 2: 'res:/UI/Texture/classes/pirateinsurgencies/widgets/corr_2.png',
 3: 'res:/UI/Texture/classes/pirateinsurgencies/widgets/corr_3.png',
 4: 'res:/UI/Texture/classes/pirateinsurgencies/widgets/corr_4.png',
 5: 'res:/UI/Texture/classes/pirateinsurgencies/widgets/corr_5.png'}
_SUPPRESSION_STAGE_TO_ICON = {0: 'res:/UI/Texture/classes/pirateinsurgencies/widgets/supp_0.png',
 1: 'res:/UI/Texture/classes/pirateinsurgencies/widgets/supp_1.png',
 2: 'res:/UI/Texture/classes/pirateinsurgencies/widgets/supp_2.png',
 3: 'res:/UI/Texture/classes/pirateinsurgencies/widgets/supp_3.png',
 4: 'res:/UI/Texture/classes/pirateinsurgencies/widgets/supp_4.png',
 5: 'res:/UI/Texture/classes/pirateinsurgencies/widgets/supp_5.png'}
_FACTION_ID_TO_FILL_COLOR = {appConst.factionGuristasPirates: Color.HextoRGBA('#FF7F00'),
 appConst.factionAngelCartel: Color.HextoRGBA('#FFE1B0'),
 appConst.factionCaldariState: Color.HextoRGBA('#00ACD1'),
 appConst.factionGallenteFederation: Color.HextoRGBA('#40AA5E'),
 appConst.factionMinmatarRepublic: Color.HextoRGBA('#FE3743'),
 appConst.factionAmarrEmpire: Color.HextoRGBA('#E7B815')}
_FACTION_ID_TO_STROKE_COLOR = {appConst.factionGuristasPirates: Color.HextoRGBA('#E54500'),
 appConst.factionAngelCartel: Color.HextoRGBA('#FFE1B0'),
 appConst.factionCaldariState: Color.HextoRGBA('#105379'),
 appConst.factionGallenteFederation: Color.HextoRGBA('#3E6530'),
 appConst.factionMinmatarRepublic: Color.HextoRGBA('#922B44'),
 appConst.factionAmarrEmpire: Color.HextoRGBA('#83591B')}
FACTION_ID_TO_BADGE_96PX = {appConst.factionGuristasPirates: 'res:/UI/Texture/classes/pirateinsurgencies/faction_badges/96p/Guristas96px.png',
 appConst.factionAngelCartel: 'res:/UI/Texture/classes/pirateinsurgencies/faction_badges/96p/AngelCartel96px.png',
 appConst.factionCaldariState: 'res:/UI/Texture/Classes/pirateinsurgencies/faction_badges/96p/Caldari96px.png',
 appConst.factionGallenteFederation: 'res:/UI/Texture/Classes/pirateinsurgencies/faction_badges/96p/Gallente96px.png',
 appConst.factionMinmatarRepublic: 'res:/UI/Texture/Classes/pirateinsurgencies/faction_badges/96p/Minmatar96px.png',
 appConst.factionAmarrEmpire: 'res:/UI/Texture/Classes/pirateinsurgencies/faction_badges/96p/Amarr96px.png'}
FACTION_ID_TO_BADGE_80PX = {appConst.factionAmarrEmpire: 'res:/UI/Texture/Classes/Enlistment/logos/amarr.png',
 appConst.factionCaldariState: 'res:/UI/Texture/Classes/Enlistment/logos/caldari.png',
 appConst.factionGallenteFederation: 'res:/UI/Texture/Classes/Enlistment/logos/gallente.png',
 appConst.factionMinmatarRepublic: 'res:/UI/Texture/Classes/Enlistment/logos/minmatar.png',
 appConst.factionAngelCartel: 'res:/UI/Texture/Classes/Enlistment/logos/angels.png',
 appConst.factionGuristasPirates: 'res:/UI/Texture/Classes/Enlistment/logos/guristas.png'}
_PIRATE_FACTION_DISPLAY_ORDER = {appConst.factionAngelCartel: 0,
 appConst.factionGuristasPirates: 1}
_FACTION_ID_TO_BANNER = {appConst.factionAmarrEmpire: 'res:/UI/Texture/classes/pirateinsurgencies/banners/amarr.png',
 appConst.factionCaldariState: 'res:/UI/Texture/classes/pirateinsurgencies/banners/caldari.png',
 appConst.factionGallenteFederation: 'res:/UI/Texture/Classes/pirateinsurgencies/banners/gallente.png',
 appConst.factionMinmatarRepublic: 'res:/UI/Texture/Classes/pirateinsurgencies/banners/minmatar.png',
 appConst.factionAngelCartel: 'res:/UI/Texture/Classes/pirateinsurgencies/banners/angel_cartel.png',
 appConst.factionGuristasPirates: 'res:/UI/Texture/Classes/pirateinsurgencies/banners/guristas.png'}

def ConstructErrorMessageCont(parentContainer, errorMessageLabel, fullErrorBox = True):
    container = ContainerAutoSize(parent=parentContainer, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, name='errorCont')
    if fullErrorBox:
        Fill(bgParent=container, color=eveColor.BLACK, opacity=0.25)
    else:
        container.hint = GetByLabel(errorMessageLabel)
    Sprite(parent=Container(parent=container, align=uiconst.TOTOP, height=16), texturePath=eveicon.difficulty, color=eveColor.DANGER_RED, width=16, height=16, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
    if fullErrorBox:
        carbonui.TextBody(parent=container, align=uiconst.TOTOP, color=eveColor.DANGER_RED, text=GetByLabel(errorMessageLabel), textAlign=TextAlign.CENTER, state=uiconst.UI_DISABLED)


def GetCorruptionIconForStage(stage):
    return _CORRUPTION_STAGE_TO_ICON[stage]


def GetSuppressionIconForStage(stage):
    return _SUPPRESSION_STAGE_TO_ICON[stage]


def GetFactionColorFromPerspectiveOfMilitia(fromPerspectiveMilitia, militia, fill = True):
    if facwarCommon.IsOccupierFWFaction(militia):
        return GetSuppressionColor(fill)
    genericCorruptionColor = _CORRUPTION_FILL_COLOR
    colorMap = _FACTION_ID_TO_FILL_COLOR
    if not fill:
        colorMap = _FACTION_ID_TO_STROKE_COLOR
        genericCorruptionColor = _CORRUPTION_STROKE_COLOR
    if fromPerspectiveMilitia is None:
        return genericCorruptionColor
    elif facwarCommon.IsOccupierFWFaction(fromPerspectiveMilitia):
        return genericCorruptionColor
    elif facwarCommon.IsPirateFWFaction(fromPerspectiveMilitia) and militia == fromPerspectiveMilitia:
        return colorMap[militia]
    else:
        return genericCorruptionColor


def GetGenericCorruptionColor(fill = True):
    if fill:
        return _CORRUPTION_FILL_COLOR
    else:
        return _CORRUPTION_STROKE_COLOR


def GetSuppressionColor(fill = True):
    if fill:
        return _SUPPRESSION_FILL_COLOR
    else:
        return _SUPPRESSION_STROKE_COLOR


def GetBannerPathFromFactionID(factionID):
    return _FACTION_ID_TO_BANNER[factionID]


def GetPirateFactionIDFromWarzoneID(factionID):
    return WARZONE_ID_TO_PIRATE_FACTION_ID[factionID]


def GetPirateFactionDisplayOrder(factionID):
    return _PIRATE_FACTION_DISPLAY_ORDER.get(factionID, -1)


def GetFactionBadge(factionID):
    return FACTION_ID_TO_BADGE_96PX[factionID]


def GetFactionBadgeSmall(factionID):
    return FACTION_ID_TO_BADGE_80PX[factionID]


_FACTION_ID_TO_COLOR = {}
_FACTION_ID_TO_COLOR.update(FACTION_ID_TO_COLOR)

def GetFactionColor(factionID):
    return _FACTION_ID_TO_COLOR.get(factionID, None)


STAGE_TO_BLOB_SIZE = {0: 48,
 1: 72,
 2: 96,
 3: 128,
 4: 160,
 5: 200}
STAGE_TO_BLOB_TEXTURE = {0: 'res:/UI/Texture/classes/pirateinsurgencies/map/CorruptionCircle00.png',
 1: 'res:/UI/Texture/classes/pirateinsurgencies/map/CorruptionCircle01.png',
 2: 'res:/UI/Texture/classes/pirateinsurgencies/map/CorruptionCircle02.png',
 3: 'res:/UI/Texture/classes/pirateinsurgencies/map/CorruptionCircle03.png',
 4: 'res:/UI/Texture/classes/pirateinsurgencies/map/CorruptionCircle04.png',
 5: 'res:/UI/Texture/classes/pirateinsurgencies/map/CorruptionCircle05.png'}
STAGE_TO_STROKE_TEXTURE = {0: 'res:/UI/Texture/classes/pirateinsurgencies/map/CorruptionStroke00.png',
 1: 'res:/UI/Texture/classes/pirateinsurgencies/map/CorruptionStroke01.png',
 2: 'res:/UI/Texture/classes/pirateinsurgencies/map/CorruptionStroke02.png',
 3: 'res:/UI/Texture/classes/pirateinsurgencies/map/CorruptionStroke03.png',
 4: 'res:/UI/Texture/classes/pirateinsurgencies/map/CorruptionStroke04.png',
 5: 'res:/UI/Texture/classes/pirateinsurgencies/map/CorruptionStroke05.png'}
