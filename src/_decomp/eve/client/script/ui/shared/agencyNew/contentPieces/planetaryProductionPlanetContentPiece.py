#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\planetaryProductionPlanetContentPiece.py
import evetypes
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToItem
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.common.lib import appConst

class PlanetaryProductionPlanetContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_PLANETARYPRODUCTION

    def __init__(self, planetName, *args, **kwargs):
        super(PlanetaryProductionPlanetContentPiece, self).__init__(*args, **kwargs)
        self.planetName = planetName
        self.isBlacklisted = self.itemID in cfg.planetBlacklist
        self.planetResources = None

    def GetName(self):
        return self.planetName

    def GetCardSortValue(self):
        if self.isBlacklisted:
            return -1

    def _ExecuteWarpTo(self):
        if not self.itemID:
            return
        WarpToItem(self.itemID)

    def GetPlanetResourceInfo(self):
        if self.planetResources:
            return self.planetResources
        planetObject = sm.GetService('planetSvc').GetPlanet(self.itemID)
        resourceInfo = planetObject.remoteHandler.GetPlanetResourceInfo()
        sortedList = []
        for typeID, quality in resourceInfo.iteritems():
            name = evetypes.GetName(typeID)
            sortedList.append((name, (typeID, quality / appConst.MAX_DISPLAY_QUALITY)))

        sortedList = SortListOfTuples(sortedList)
        self.planetResources = sortedList
        return self.planetResources

    def IsColonizedByMe(self):
        return sm.GetService('planetSvc').IsPlanetColonizedByMe(self.itemID)
