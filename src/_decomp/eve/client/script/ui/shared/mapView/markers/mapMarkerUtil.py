#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerUtil.py
import evetypes
import inventorycommon.const as invconst
from eve.common.lib import appConst
from probescanning.const import probeResultInformative, probeResultGood
import dogma.const as dogmaConst
COLOR_RED = (1.0, 0.0, 0.0, 1.0)
COLOR_ORANGE = (0.9, 0.5, 0.0, 1.0)
COLOR_YELLOW = (1.0, 1.0, 0.1, 1.0)
COLOR_GREEN = (0.0, 0.8, 0.0, 1.0)
ICONS_BY_SCANGROUP = {dogmaConst.attributeScanGravimetricStrength: 'res:/UI/Texture/Shared/Brackets/ore_site_16.png',
 dogmaConst.attributeScanLadarStrength: 'res:/UI/Texture/Shared/Brackets/harvestableCloud.png',
 dogmaConst.attributeScanMagnetometricStrength: 'res:/UI/Texture/Shared/Brackets/relic_site_16.png',
 dogmaConst.attributeScanRadarStrength: 'res:/UI/Texture/Shared/Brackets/data_site_16.png',
 dogmaConst.attributeScanWormholeStrength: 'res:/UI/Texture/Shared/Brackets/wormhole.png',
 dogmaConst.attributeScanAllStrength: 'res:/UI/Texture/Shared/Brackets/combatSite_16.png'}

def GetSiteBracketIcon(archetypeID):
    if archetypeID in (appConst.dunArchetypeOreAnomaly, appConst.dunArchetypeIceBelt):
        return 'res:/UI/Texture/Shared/Brackets/ore_site_16.png'
    elif archetypeID == appConst.dunArchetypeGasClouds:
        return ('res:/UI/Texture/Shared/Brackets/harvestableCloud.png',)
    elif archetypeID in (appConst.dunArchetypeRelicSites, appConst.dunArchetypeSitesOfInterest):
        return 'res:/UI/Texture/Shared/Brackets/relic_site_16.png'
    elif archetypeID in (appConst.dunArchetypeDataSites, appConst.dunArchetypeCombatHacking):
        return 'res:/UI/Texture/Shared/Brackets/data_site_16.png'
    elif archetypeID in (appConst.dunArchetypeCombatSites,
     appConst.dunArchetypeDrifterSites,
     appConst.dunArchetypeGhostSites,
     appConst.dunArchetypeEventSites,
     appConst.dunArchetypeHomefrontSites):
        return 'res:/UI/Texture/Shared/Brackets/combatSite_16.png'
    elif archetypeID == appConst.dunArchetypeWormhole:
        return 'res:/UI/Texture/Shared/Brackets/wormhole.png'
    else:
        return 'res:/UI/Texture/classes/MapView/scanResultLocation.png'


def GetResultTexturePath(resultData):
    if isinstance(resultData.data, float) or not isinstance(resultData.data, (tuple, list)):
        return 'res:/UI/Texture/classes/MapView/scanResultLocation.png'
    elif resultData.strengthAttributeID and resultData.strengthAttributeID in ICONS_BY_SCANGROUP:
        return ICONS_BY_SCANGROUP[resultData.strengthAttributeID]
    else:
        typeID, groupID, categoryID = GetTypeGroupCategoryID(resultData)
        return GetIconByCertainty(typeID, groupID, categoryID, resultData.certainty)


def GetTypeGroupCategoryID(resultData):
    if resultData.certainty >= probeResultInformative:
        typeID = resultData.Get('typeID', None)
        groupID = resultData.groupID
        categoryID = None
    elif resultData.certainty >= probeResultGood:
        typeID = None
        groupID = resultData.Get('groupID', None)
        categoryID = evetypes.GetCategoryIDByGroup(groupID)
    else:
        typeID = None
        groupID = None
        categoryID = None
    return (typeID, groupID, categoryID)


def GetIconByCertainty(typeID, groupID, categoryID, certainty):
    if groupID in (invconst.groupCosmicAnomaly, invconst.groupCosmicSignature):
        bracketData = sm.GetService('bracket').GetBracketDataByGroupID(invconst.groupBeacon)
    elif categoryID == const.categoryShip and groupID is None:
        bracketData = sm.GetService('bracket').GetBracketDataByGroupID(invconst.groupFrigate)
    elif typeID:
        bracketIconPath = sm.GetService('bracket').GetBracketIcon(typeID)
        if bracketIconPath:
            return bracketIconPath
    elif groupID:
        bracketData = sm.GetService('bracket').GetBracketDataByGroupID(groupID)
    else:
        bracketData = None
    if bracketData:
        texturePath = bracketData.texturePath
    else:
        texturePath = 'res:/UI/Texture/Shared/Brackets/planet.png'
    return texturePath


def GetResultColor(certainty):
    if certainty is None or certainty <= 0.25:
        return COLOR_RED
    elif 0.25 < certainty <= 0.75:
        return COLOR_ORANGE
    elif 0.75 < certainty < 1.0:
        return COLOR_YELLOW
    else:
        return COLOR_GREEN
