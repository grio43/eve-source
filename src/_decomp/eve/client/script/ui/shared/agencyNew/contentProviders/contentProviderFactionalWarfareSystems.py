#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderFactionalWarfareSystems.py
import telemetry
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters
from eve.client.script.ui.shared.agencyNew.agencyConst import ADJACENCY_BY_FILTER_VALUE
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.factionalWarfareSystemContentPiece import FactionalWarfareSystemContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProviderCosmicAnomalies import BaseContentProviderCosmicAnomalies
from inventorycommon import const as invConst

class ContentProviderFactionalWarfareSystems(BaseContentProviderCosmicAnomalies):
    contentType = agencyConst.CONTENTTYPE_FACTIONALWARFARESYSTEM
    contentGroup = contentGroupConst.contentGroupFactionalWarfareSystems
    DUNGEON_TRACKER_ID = 'factional_warfare'

    def __init__(self):
        super(ContentProviderFactionalWarfareSystems, self).__init__()
        self.facWarSvc = sm.GetService('facwar')
        self.fwVictoryPointSvc = sm.GetService('fwVictoryPointSvc')

    def ConstructContentPiece(self, solarSystemID, dungeonInstances):
        occupierID = self.facWarSvc.GetSystemOccupier(solarSystemID)
        return FactionalWarfareSystemContentPiece(solarSystemID=solarSystemID, typeID=invConst.typeSolarSystem, itemID=solarSystemID, ownerID=occupierID, enemyOwnerID=occupierID, myFactionID=self.GetMyWarFactionID(), dungeonInstances=dungeonInstances)

    def CheckCriteria(self, solarSystemID):
        if not self.CheckFactionCriteria(self.facWarSvc.GetSystemOccupier(solarSystemID)):
            return False
        if not self.CheckDistanceCriteria(solarSystemID):
            return False
        if not self.CheckAdjacencyCriteria(self._GetAdjacencyStateFromSystemID(solarSystemID)):
            return False
        return True

    def CheckFactionCriteria(self, factionID):
        if factionID is None:
            return False
        else:
            selectedFaction = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_SYSTEMFACTION)
            if selectedFaction == agencyConst.FILTERVALUE_ANY:
                return True
            return selectedFaction == factionID

    def CheckAdjacencyCriteria(self, adjacencyState):
        if adjacencyState is None:
            return False
        selectedAdjacencyValue = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_FWADJACENCY)
        if selectedAdjacencyValue == agencyConst.FILTERVALUE_ANY:
            return True
        selectedAdjacency = ADJACENCY_BY_FILTER_VALUE.get(selectedAdjacencyValue, None)
        return selectedAdjacency == adjacencyState

    def GetMyWarFactionID(self):
        return self.facWarSvc.GetPreferredOccupierFactionID()

    @telemetry.ZONE_METHOD
    def _GetSystemSortKey(self, solarSystemID):
        victoryPointState = self.fwVictoryPointSvc.GetVictoryPointState(solarSystemID)
        return (-victoryPointState.contestedFraction, self.GetNumJumpsToSystem(solarSystemID))

    def _GetAdjacencyStateFromSystemID(self, solarSystemID):
        fwOccupationState = sm.GetService('fwWarzoneSvc').GetOccupationState(solarSystemID)
        if fwOccupationState:
            return fwOccupationState.adjacencyState
