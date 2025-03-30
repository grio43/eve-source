#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\pirateInsurgencySystemContentPiece.py
from carbonui.util.bunch import Bunch
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.contentPieces.pirateInsurgencySiteContentPiece import PirateInsurgencySiteContentPiece
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.common.lib import appConst
from eve.common.script.sys.idCheckers import IsCorporation
from localization import GetByLabel

class PirateInsurgencySystemContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_PIRATEINSURGENCESYSTEM

    def __init__(self, dungeonInstances = None, pirateFactionID = None, isFobSystem = False, **kwargs):
        super(PirateInsurgencySystemContentPiece, self).__init__(**kwargs)
        self.pirateFactionID = pirateFactionID
        self.isFobSystem = isFobSystem
        self.corruptionSuppressionSvc = sm.GetService('corruptionSuppressionSvc')
        self.contentPieces = self._ConstructPirateInsurgencySiteContentPieces(dungeonInstances)

    def _ConstructPirateInsurgencySiteContentPieces(self, dungeonInstances):
        return filter(None, [ self.ConstructPirateInsurgencySiteContentPiece(site) for site in dungeonInstances ])

    def ConstructPirateInsurgencySiteContentPiece(self, site):
        return PirateInsurgencySiteContentPiece(solarSystemID=self.solarSystemID, ownerID=site.factionID, enemyOwnerID=site.factionID, itemID=site.siteID, locationID=site.siteID, site=site, dungeonNameID=site.dungeonNameID, position=site.position)

    def _GetButtonState(self):
        return agencyUIConst.ACTION_SETDESTINATION

    def GetCardID(self):
        return (self.contentType, self.solarSystemID)

    def GetOwnerTypeID(self, ownerID):
        if IsCorporation(ownerID):
            return appConst.typeCorporation
        return appConst.typeFaction

    def GetDragData(self):
        dragData = Bunch()
        dragData.__guid__ = 'xtriui.ListSurroundingsBtn'
        dragData.itemID = self.itemID
        dragData.typeID = self.typeID
        dragData.label = cfg.evelocations.Get(self.solarSystemID).name
        return [dragData]

    def GetCorruptionStageText(self):
        stage = self.corruptionSuppressionSvc.GetSystemCorruptionStage(self.solarSystemID)
        if stage is None:
            return ''
        return GetByLabel('UI/Agency/PirateIncursions/CorruptionStageX', stage=stage)

    def GetSuppressionStageText(self):
        stage = self.corruptionSuppressionSvc.GetSystemSuppressionStage(self.solarSystemID)
        if stage is None:
            return ''
        return GetByLabel('UI/Agency/PirateIncursions/SuppressionStageX', stage=stage)

    def GetPirateText(self):
        if not self.pirateFactionID:
            return ''
        factionName = cfg.eveowners.Get(self.pirateFactionID).name
        if self.isFobSystem:
            return GetByLabel('UI/PirateInsurgencies/FOBSystem', factionName=factionName)
        return GetByLabel('UI/PirateInsurgencies/FactionInsurgencySystem', factionName=factionName)

    def GetPirateFactionID(self):
        return self.pirateFactionID

    def GetFobOwnerInSystem(self):
        if not self.isFobSystem:
            return
        return self.pirateFactionID
