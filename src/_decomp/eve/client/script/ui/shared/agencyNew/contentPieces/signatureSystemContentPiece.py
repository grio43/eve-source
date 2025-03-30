#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\signatureSystemContentPiece.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.contentPieces.signatureContentPiece import SignatureContentPiece
from eve.client.script.ui.shared.agencyNew.contentPieces.siteSystemContentPiece import SiteSystemContentPiece
from eve.common.lib import appConst
from localization import GetByLabel

class SignatureSystemContentPiece(SiteSystemContentPiece):
    contentType = agencyConst.CONTENTTYPE_SIGNATURES

    def _ConstructSiteContentPieces(self, dungeonInstances):
        if self.IsInCurrentSolarSystem():
            signatures = self.GetAllSignatures()
        else:
            signatures = dungeonInstances
        return [ self._ConstructSiteContentPiece(site) for site in signatures ]

    def GetAllSignatures(self):
        sensorSuiteSvc = sm.GetService('sensorSuite')
        sensorSuiteSvc.UpdateSignalTracker()
        sites = sensorSuiteSvc.GetSignatures()
        return sites

    def _ConstructSiteContentPiece(self, site):
        if site is None:
            return UnknownSignatureContentPiece(solarSystemID=self.solarSystemID)
        else:
            return SignatureContentPiece(solarSystemID=self.solarSystemID, enemyOwnerID=site.factionID, itemID=site.siteID, locationID=site.siteID, site=site, dungeonNameID=site.dungeonNameID, position=site.position)

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(self.solarSystemID, appConst.typeSolarSystem)


class UnknownSignatureContentPiece(BaseContentPiece):

    def GetName(self):
        return GetByLabel('UI/Agency/UnknownCosmicSignature')

    def GetCardID(self):
        return (self.solarSystemID, self.contentType, self.itemID)
