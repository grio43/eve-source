#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderPirateInsurgenceSystems.py
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.pirateInsurgencySystemContentPiece import PirateInsurgencySystemContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProviderCosmicAnomalies import BaseContentProviderCosmicAnomalies
from inventorycommon import const as invConst

class ContentProviderPirateInsurgenceSystems(BaseContentProviderCosmicAnomalies):
    contentType = agencyConst.CONTENTTYPE_PIRATEINSURGENCESYSTEM
    contentGroup = contentGroupConst.contentGroupPirateIncursions
    DUNGEON_TRACKER_ID = 'pirate_insurgency'

    def __init__(self):
        super(ContentProviderPirateInsurgenceSystems, self).__init__()
        self.fwWarzoneSvc = sm.GetService('fwWarzoneSvc')
        self.corruptionSuppressionSvc = sm.GetService('corruptionSuppressionSvc')
        self.insurgencyCampaignSvc = sm.GetService('insurgencyCampaignSvc')

    def ConstructContentPiece(self, solarSystemID, dungeonInstances):
        occupierID = self.fwWarzoneSvc.GetSystemOccupier(solarSystemID)
        pirateFactionID = self.insurgencyCampaignSvc.GetSolarsystemPirateFactionForCampaign(solarSystemID)
        isFobSystem = self.insurgencyCampaignSvc.IsInsurgencyOriginSolarsystemID(solarSystemID)
        return PirateInsurgencySystemContentPiece(solarSystemID=solarSystemID, typeID=invConst.typeSolarSystem, itemID=solarSystemID, ownerID=occupierID, dungeonInstances=dungeonInstances, pirateFactionID=pirateFactionID, isFobSystem=isFobSystem)

    def CheckCriteria(self, solarSystemID):
        if not self.CheckDistanceCriteria(solarSystemID):
            return False
        if not self.CheckCriteriaCorruptionStage(solarSystemID):
            return False
        if not self.CheckCriteriaSuppressionStage(solarSystemID):
            return False
        if not self.CheckFactionCriteria(solarSystemID):
            return False
        return True

    def CheckFactionCriteria(self, solarSystemID):
        selectedFactionID = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_SYSTEMFACTION)
        if selectedFactionID == agencyConst.FILTERVALUE_ANY:
            return True
        dungeonInstances = self.GetAllDungeonInstances()
        dungeonsInSystem = dungeonInstances.get(solarSystemID, [])
        for d in dungeonsInSystem:
            if d.factionID == selectedFactionID:
                return True

        return False

    def CheckCriteriaCorruptionStage(self, solarSystemID):
        selectedCorruptionStage = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_CORRUPTION)
        if selectedCorruptionStage < 0:
            return True
        currentStage = self.corruptionSuppressionSvc.GetSystemCorruptionStage(solarSystemID)
        if currentStage is None:
            return True
        if currentStage != selectedCorruptionStage:
            return False
        return True

    def CheckCriteriaSuppressionStage(self, solarSystemID):
        selectedSuppressionStage = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_SUPPRESSION)
        if selectedSuppressionStage < 0:
            return True
        currentStage = self.corruptionSuppressionSvc.GetSystemSuppressionStage(solarSystemID)
        if currentStage is None:
            return True
        if currentStage != selectedSuppressionStage:
            return False
        return True
