#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderAsteroidBelts.py
import telemetry
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.asteroidBeltSystemContentPiece import AsteroidBeltSystemContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProvider import BaseContentProvider
from evedungeons.client.oreTypesInDungeons.data import get_asteroid_types_by_solar_system
from evedungeons.client.oreTypesInDungeons.util import get_consolidated_ore_types_in_system

class ContentProviderAsteroidBelts(BaseContentProvider):
    contentType = agencyConst.CONTENTTYPE_ASTEROIDBELTS
    contentGroup = contentGroupConst.contentGroupAsteroidBelts
    contentTypeFilters = (agencyConst.CONTENTTYPE_SUGGESTED, agencyConst.CONTENTTYPE_MINING)
    __notifyevents__ = BaseContentProvider.__notifyevents__ + ['OnSessionChanged']

    def __init__(self):
        self.validSolarSystemIDs = []
        super(ContentProviderAsteroidBelts, self).__init__()

    def OnSessionChanged(self, isRemote, sess, change):
        if 'solarsystemid' in change:
            self.InvalidateSystemCache()

    def InvalidateSystemCache(self):
        self.validSolarSystemIDs = []

    def OnAgencyFilterChanged(self, contentGroupID, filterType, value):
        if contentGroupID != self.contentGroup:
            return
        self.InvalidateSystemCache()
        super(ContentProviderAsteroidBelts, self).OnAgencyFilterChanged(contentGroupID, filterType, value)

    @telemetry.ZONE_METHOD
    def _ConstructContentPieces(self):
        if not self.validSolarSystemIDs:
            self.validSolarSystemIDs = self.GetValidSolarSystemIDs()[:agencyConst.MAX_CONTENT_PIECES_MAX]
        self.ExtendContentPieces([ self.ConstructSystemContentPiece(solarSystemID) for solarSystemID in self.validSolarSystemIDs ])

    def ConstructSystemContentPiece(self, solarSystemID):
        return AsteroidBeltSystemContentPiece(solarSystemID=solarSystemID, itemID=solarSystemID)

    def GetValidSolarSystemIDs(self):
        return [ solarSystemID for solarSystemID in self.GetAllSolarSystemIDsWithinJumpRange() if self.CheckSystemCriteria(solarSystemID) ]

    def CheckSystemCriteria(self, solarSystemID):
        return self.CheckSystemHasBelts(solarSystemID) and self.CheckDistanceCriteria(solarSystemID) and self.CheckSecurityStatusFilterCriteria(solarSystemID) and self.CheckOreTypeCriteria(solarSystemID)

    def CheckSystemHasBelts(self, solarSystemID):
        return bool(get_asteroid_types_by_solar_system(solarSystemID))

    def CheckOreTypeCriteria(self, solarSystemID):
        selectedOreType = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_ORETYPE)
        if selectedOreType == agencyConst.FILTERVALUE_ANY:
            return True
        oreTypesInSystem = get_consolidated_ore_types_in_system(solarSystemID)
        return selectedOreType in oreTypesInSystem
