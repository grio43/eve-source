#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\asteroidBeltSystemContentPiece.py
import inventorycommon.const as invConst
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.asteroidBeltContentPiece import AsteroidBeltContentPiece
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.comtool.constants import CHANNEL_MINING
from eve.common.lib import appConst
from evedungeons.client.oreTypesInDungeons.util import get_consolidated_ore_types_in_system
from localization import GetByLabel

class AsteroidBeltSystemContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_ASTEROIDBELTS

    def __init__(self, *args, **kwargs):
        super(AsteroidBeltSystemContentPiece, self).__init__(*args, **kwargs)
        self.contentPieces = [ self.ConstructAsteroidBeltContentPiece(asteroidBeltContentPiece) for asteroidBeltContentPiece in self.GetAllAsteroidBeltsInSystem() ]

    def ConstructAsteroidBeltContentPiece(self, asteroidBelt):
        return AsteroidBeltContentPiece(solarSystemID=self.solarSystemID, locationID=asteroidBelt.itemID, typeID=asteroidBelt.typeID, itemID=asteroidBelt.itemID, orbitIndex=asteroidBelt.orbitIndex, celestialIndex=asteroidBelt.celestialIndex)

    def GetName(self):
        return cfg.evelocations.Get(self.solarSystemID).locationName

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(self.solarSystemID, appConst.typeSolarSystem)

    def GetCardSortValue(self):
        isCurrentSystem = self.solarSystemID == session.solarsystemid2
        return (-int(isCurrentSystem), -self.GetSystemSecurityStatus(), self.GetJumpsToSelfFromCurrentLocation())

    def GetAllAsteroidBeltsInSystem(self):
        celestials = cfg.GetLocationsLocalBySystem(self.solarSystemID, requireLocalizedTexts=False)
        asteroidBelts = sorted([ celestial for celestial in celestials if celestial.groupID == appConst.groupAsteroidBelt ], key=lambda x: (x.celestialIndex, x.orbitIndex))
        return asteroidBelts

    def GetBlurbText(self):
        return GetByLabel('UI/Agency/Blurbs/AsteroidBelt')

    def GetEnemyOwnerID(self):
        regionID = cfg.mapSystemCache.Get(self.solarSystemID).regionID
        pirateFactionIDs = sm.GetService('faction').GetPirateFactionsOfRegion(regionID)
        if pirateFactionIDs:
            return pirateFactionIDs[0]

    def GetModulesRequiredTypeIDs(self):
        return (invConst.typeMiningLaser,)

    def GetRewardTypes(self):
        return (agencyConst.REWARDTYPE_ASTEROID,)

    def GetChatChannelID(self):
        return CHANNEL_MINING

    def GetResourceTypeIDs(self):
        return get_consolidated_ore_types_in_system(self.solarSystemID)
