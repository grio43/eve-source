#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\incursionSystemContentPiece.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.contentPieces.incursionSiteContentPiece import IncursionSiteContentPiece
from eve.client.script.ui.shared.incursions.incursionConst import SCENETYPE_DATA
from eve.common.lib import appConst
from localization import GetByLabel
from talecommon.const import scenesTypes

class IncursionSystemContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_INCURSIONS

    def __init__(self, sceneType = None, hasFinalEncounter = False, *args, **kwargs):
        super(IncursionSystemContentPiece, self).__init__(*args, **kwargs)
        self.sceneType = sceneType
        self.contentPieces = self._ConstructSiteContentPieces()
        self.hasFinalEncounter = hasFinalEncounter

    def HasFinalEncounter(self):
        return self.sceneType == scenesTypes.headquarters and self.hasFinalEncounter

    def GetSiteContentPieces(self):
        return self.contentPieces

    def _ConstructSiteContentPieces(self):
        if self.solarSystemID == session.solarsystemid2:
            return [ self.ConstructContentPieceIncursionSite(slimItem, ball) for slimItem, ball in self.GetAllIncursionSites() ]
        else:
            return []

    def ConstructContentPieceIncursionSite(self, slimItem, ball):
        return IncursionSiteContentPiece(solarSystemID=session.solarsystemid2, ownerID=appConst.factionCONCORDAssembly, enemyOwnerID=slimItem.ownerID, itemID=slimItem.itemID, locationID=slimItem.itemID, slimItem=slimItem, ball=ball)

    def GetAllIncursionSites(self):
        bp = sm.GetService('michelle').GetBallpark()
        ret = []
        if not bp:
            return ret
        for slimItem in bp.slimItems.values():
            archetypeID = getattr(slimItem, 'archetypeID', None)
            if archetypeID and archetypeID in appConst.dunArchetypesIncursionSites:
                ret.append((slimItem, bp.GetBall(slimItem.itemID)))

        return ret

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(self.solarSystemID, appConst.typeSolarSystem)

    def GetSceneType(self):
        return self.sceneType

    def GetSceneTypeName(self):
        return GetByLabel(SCENETYPE_DATA[self.sceneType].subTitle)

    def GetSceneTypeHint(self):
        return GetByLabel(SCENETYPE_DATA[self.sceneType].hint)

    def GetSceneTypeIcon(self):
        return SCENETYPE_DATA[self.sceneType].severityIcon

    def GetCardID(self):
        return (self.contentType, self.itemID, self.solarSystemID)
