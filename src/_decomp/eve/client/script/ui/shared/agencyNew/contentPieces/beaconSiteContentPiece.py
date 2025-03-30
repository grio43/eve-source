#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\beaconSiteContentPiece.py
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToItem
from eve.client.script.ui.shared.agencyNew.contentPieces.siteContentPiece import SiteContentPiece
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from localization import GetByMessageID

class BeaconSiteContentPiece(SiteContentPiece):

    def __init__(self, slimItem = None, ball = None, **kwargs):
        SiteContentPiece.__init__(self, **kwargs)
        self.slimItem = slimItem
        self.ball = ball

    def GetMenu(self):
        return sm.GetService('menu').CelestialMenu(self.slimItem.itemID)

    def GetSiteArchetype(self):
        return getattr(self.slimItem, 'archetypeID', None)

    def GetSubSolarSystemPosition(self):
        return (self.ball.x, self.ball.y, self.ball.z)

    def GetSiteName(self):
        return GetByMessageID(getattr(self.slimItem, 'dungeonNameID', None))

    def GetDungeonID(self):
        return self.slimItem.dungeonID

    def _ExecutePrimaryFunction(self, actionID):
        if actionID == agencyUIConst.ACTION_WARPTO:
            if self.locationID:
                WarpToItem(self.locationID)
        else:
            super(BeaconSiteContentPiece, self)._ExecutePrimaryFunction(actionID)
