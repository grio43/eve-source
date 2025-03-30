#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\probescanning\resultFilter.py
import inventorycommon.const
import localization
import probescanning.const
RESULTFILTERID_SHOWALL = 0
_defaultFilters = {RESULTFILTERID_SHOWALL: ('UI/Common/Show all', None),
 -1: ('UI/Inflight/Scanner/CosmicSignatures', probescanning.const.GetCosmicSignatureGroups()),
 -2: ('UI/Inflight/Scanner/DronesAndCharges', probescanning.const.GetDroneFighterAndChargeGroups()),
 -3: ('UI/Inflight/Scanner/Ships', probescanning.const.GetShipGroups()),
 -4: ('UI/Inflight/Scanner/Structures', probescanning.const.GetStructureGroups()),
 -5: ('UI/Inflight/Scanner/Deployables', probescanning.const.GetDeployableGroups())}
_defaultFilterSet = [-1,
 -2,
 -3,
 -4,
 -5]

class ResultFilter(object):
    __notifyevents__ = ['OnCharacterSessionChanged']

    def __init__(self):
        self.filters = {}
        self.activeFilterSet = set(_defaultFilterSet)
        sm.RegisterNotify(self)

    def GetNewFilterID(self):
        try:
            return max(self.filters.keys()) + 1
        except ValueError:
            return 1

    def CreateFilter(self, filterName, groups):
        filterID = self.GetNewFilterID()
        self.filters[filterID] = (filterName, groups)
        self._PersistFilters()
        return filterID

    def EditFilter(self, filterID, name, groups):
        if filterID == 0:
            raise RuntimeError("Can't Edit Show all Filter")
        if filterID < 0:
            self.DeleteFilter(filterID)
            filterID = self.CreateFilter(name, groups)
        else:
            self.filters[filterID] = (name, groups)
        self._PersistFilters()
        return filterID

    def GetMasterGroupsForActiveFilterSet(self):
        groups = self.GetActiveFilterSetGroupIDs()
        if groups is None:
            return probescanning.const.probeScanGroups.keys()
        masterGroups = set()
        for groupID in groups:
            for scanGroupID, scanGroup in probescanning.const.probeScanGroups.iteritems():
                if isinstance(groupID, tuple):
                    groupID = groupID[0]
                if groupID in scanGroup:
                    masterGroups.add(scanGroupID)

        return masterGroups

    def GetFilters(self):
        defaultFilters = [ (localization.GetByLabel(label), filterID) for filterID, (label, _) in _defaultFilters.iteritems() ]
        myFilters = [ (label, filterID) for filterID, (label, _) in self.filters.iteritems() ]
        return defaultFilters + myFilters

    def GetFilter(self, filterID):
        if filterID <= 0:
            label, groups = _defaultFilters[filterID]
            return (localization.GetByLabel(label), groups)
        elif filterID in self.filters:
            return self.filters[filterID]
        else:
            return ('', [])

    def GetFilterName(self, filterID):
        return self.GetFilter(filterID)[0]

    def DeleteFilter(self, filterID):
        if filterID > 0:
            del self.filters[filterID]
        self._PersistFilters()

    def GetActiveFilterSetGroupIDs(self):
        ret = set()
        for filterID in self.activeFilterSet:
            _, groupIDs = self.GetFilter(filterID)
            ret.update(set(groupIDs))

        return ret

    def GetActiveFilterSet(self):
        return self.activeFilterSet

    def AddToActiveFilterSet(self, filterID):
        self.activeFilterSet.add(filterID)
        self._PersistActiveFilterSet()

    def RemoveFromActiveFilterSet(self, filterID):
        if filterID in self.activeFilterSet:
            self.activeFilterSet.remove(filterID)
            self._PersistActiveFilterSet()

    def PrimePersistedFilters(self):
        self.filters = settings.user.ui.Get('probescanning.resultFilter.filters', self.filters)
        self.activeFilterSet = set(settings.user.ui.Get('probescanning.resultFilter.activeFilterSet', self.activeFilterSet))
        self.showingAnomalies = settings.user.ui.Get('probescanning.resultFilter.showingAnomalies', True)

    def IsFilteredOut(self, result):
        currentFilter = self.GetActiveFilterSetGroupIDs()
        if not currentFilter:
            return True
        masterGroups = self.GetMasterGroupsForActiveFilterSet()
        if currentFilter:
            if result.get('isIdentified', False):
                if result['groupID'] == inventorycommon.const.groupCosmicSignature:
                    if (result['groupID'], result['strengthAttributeID']) not in currentFilter:
                        return True
                elif result['groupID'] not in currentFilter:
                    return True
            elif result['scanGroupID'] not in masterGroups:
                return True
        return False

    def IsShowingAnomalies(self):
        return self.showingAnomalies

    def ShowAnomalies(self):
        self.showingAnomalies = True
        self._PersistShowingAnomalies()

    def StopShowingAnomalies(self):
        self.showingAnomalies = False
        self._PersistShowingAnomalies()

    def OnCharacterSessionChanged(self, _oldCharacterID, newCharacterID):
        if newCharacterID is not None:
            self.PrimePersistedFilters()

    def _PersistFilters(self):
        settings.user.ui.Set('probescanning.resultFilter.filters', self.filters)

    def _PersistActiveFilterSet(self):
        settings.user.ui.Set('probescanning.resultFilter.activeFilterSet', self.activeFilterSet)

    def _PersistShowingAnomalies(self):
        settings.user.ui.Set('probescanning.resultFilter.showingAnomalies', self.showingAnomalies)
