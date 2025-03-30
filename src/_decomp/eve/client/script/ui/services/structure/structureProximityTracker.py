#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\structure\structureProximityTracker.py
import telemetry
from caching.memoize import Memoize
from carbon.common.script.sys.service import Service
from carbon.common.script.util.timerstuff import AutoTimer
from collections import defaultdict
from eve.common.lib import appConst as const
from eve.client.script.ui.services.structure.error import InvalidStateOfRegistry
from eve.common.script.sys.idCheckers import IsStation
from evetypes import IsStructureAlwaysGlobal
from contextlib import contextmanager
UPDATE_STRUCTURE_VISIBILITY_TIMEOUT = 2000

class StructureProximityTracker(Service):
    __guid__ = 'svc.structureProximityTracker'
    __notifyevents__ = ['OnBallAdded',
     'DoBallRemove',
     'DoBallsRemove',
     'OnSessionChanged',
     'OnStructuresReloaded',
     'OnDockingAccessChangedForCurrentSolarSystem_Local']
    __dependencies__ = ['michelle', 'structureDirectory']

    def Run(self, *args):
        self.structureVisibilityRegistry = defaultdict(bool)
        self.dockableStructuresInSystem = defaultdict(bool)
        self.dockableStructuresInSystemHaveChanged = False
        self._TriggerStructureVisibilityUpdates()

    def IsStructureDockable(self, structureID):
        if self.dockableStructuresInSystemHaveChanged:
            self.RefreshDockability_Memoized()
        return self.dockableStructuresInSystem[structureID]

    def IsStructureInRange(self, structureID):
        return self.michelle.IsBallVisible(structureID)

    def IsStructureVisible(self, structureID):
        item = self.michelle.GetItem(structureID)
        if item and IsStructureAlwaysGlobal(item.typeID):
            return True
        return self.IsStructureDockable(structureID) or self.IsStructureInRange(structureID)

    def _SetStructureVisibility(self, structureID, isVisible):
        self.structureVisibilityRegistry[structureID] = isVisible
        sm.ScatterEvent('OnStructureVisibilityUpdated', structureID)

    def _ClearVisibilityRegistry(self):
        for structureID in self.structureVisibilityRegistry:
            self._SetStructureVisibility(structureID, False)

        self.structureVisibilityRegistry.clear()
        sm.ScatterEvent('OnStructuresVisibilityUpdated')

    def _ResetVisibility(self):
        for structureID in self.structureVisibilityRegistry:
            self._SetStructureVisibility(structureID, False)

        sm.ScatterEvent('OnStructuresVisibilityUpdated')

    @Memoize(3)
    def RefreshDockability_Memoized(self):
        self._RefreshDockability()

    @telemetry.ZONE_METHOD
    def _RefreshDockability(self):
        oldDockableStrucutures = {structureID for structureID, dockable in self.dockableStructuresInSystem.iteritems() if dockable == True}
        self.dockableStructuresInSystem.clear()
        hasVisibilityChangedForAnyStructure = False
        wereDockableStructuresOutdated = self.dockableStructuresInSystemHaveChanged
        self.dockableStructuresInSystemHaveChanged = False
        newDockableStructures = self._GetDockableStructures()
        for structureID in self.structureVisibilityRegistry:
            isStructureInRange = self.IsStructureInRange(structureID)
            wasStructureDockable = structureID in oldDockableStrucutures
            isStructureDockable = structureID in newDockableStructures
            self.dockableStructuresInSystem[structureID] = isStructureDockable
            hasVisibilityChanged = not isStructureInRange and wasStructureDockable != isStructureDockable
            if hasVisibilityChanged:
                hasVisibilityChangedForAnyStructure = True
                self._SetStructureVisibility(structureID, isStructureDockable)

        for structureID in newDockableStructures:
            self.dockableStructuresInSystem[structureID] = True

        if hasVisibilityChangedForAnyStructure:
            sm.ScatterEvent('OnStructuresVisibilityUpdated')
        if wereDockableStructuresOutdated:
            sm.ScatterEvent('OnStructureAccessUpdated')

    @telemetry.ZONE_METHOD
    def _GetDockableStructures(self):
        dockableStructures = []
        allDockableStructuresInSolarSystem = self.structureDirectory.GetStructuresInCurrentSystem()
        for structureID in allDockableStructuresInSolarSystem:
            shouldTrackStructure = not IsStation(structureID)
            if shouldTrackStructure:
                dockableStructures.append(structureID)

        return dockableStructures

    def _TriggerStructureVisibilityUpdates(self):
        setattr(self, 'updateStructureVisibilityTimerThread', AutoTimer(UPDATE_STRUCTURE_VISIBILITY_TIMEOUT, self._UpdateStructureVisibility))

    @telemetry.ZONE_METHOD
    def _UpdateStructureVisibility(self):
        hasVisibilityChangedForAnyStructure = False
        for structureID, wasVisible in self.structureVisibilityRegistry.iteritems():
            isVisible = self.IsStructureVisible(structureID)
            if wasVisible != isVisible:
                hasVisibilityChangedForAnyStructure = True
                self._SetStructureVisibility(structureID, isVisible)

        if hasVisibilityChangedForAnyStructure:
            sm.ScatterEvent('OnStructuresVisibilityUpdated')

    @contextmanager
    def CallFunctionWithStructureVisibilityUpdatesPaused(self):
        self.updateStructureVisibilityTimerThread = None
        try:
            yield
            self._TriggerStructureVisibilityUpdates()
        except InvalidStateOfRegistry:
            pass

    def OnSessionChanged(self, isRemote, session, change):
        hasSolarSystemChanged = 'solarsystemid' in change
        hasStructureIdChanged = 'structureid' in change
        if hasSolarSystemChanged:
            self.RefreshDockability_Memoized.clear_memoized()
            with self.CallFunctionWithStructureVisibilityUpdatesPaused():
                self._ClearVisibilityRegistry()
        elif hasStructureIdChanged:
            with self.CallFunctionWithStructureVisibilityUpdatesPaused():
                self._ResetVisibility()

    def OnStructuresReloaded(self):
        with self.CallFunctionWithStructureVisibilityUpdatesPaused():
            self._RefreshDockability()

    def OnBallAdded(self, slimItem):
        if slimItem.categoryID == const.categoryStructure:
            structureToAdd = slimItem.itemID
            with self.CallFunctionWithStructureVisibilityUpdatesPaused():
                self._AddStructureToRegistry(structureToAdd)

    def DoBallRemove(self, ball, slimItem, terminal):
        if slimItem.categoryID == const.categoryStructure:
            structureToRemove = slimItem.itemID
            with self.CallFunctionWithStructureVisibilityUpdatesPaused():
                self._RemoveStructureFromRegistry(structureToRemove)

    def DoBallsRemove(self, pythonBalls, isRelease):
        structuresToRemove = []
        for _ball, slimItem, _terminal in pythonBalls:
            if slimItem.categoryID == const.categoryStructure:
                structuresToRemove.append(slimItem.itemID)

        if structuresToRemove:
            with self.CallFunctionWithStructureVisibilityUpdatesPaused():
                self._RemoveStructuresFromRegistry(structuresToRemove)

    def _AddStructureToRegistry(self, structureToAdd):
        if structureToAdd in self.structureVisibilityRegistry:
            raise InvalidStateOfRegistry()
        isVisible = self.IsStructureVisible(structureToAdd)
        self.structureVisibilityRegistry[structureToAdd] = self._SetStructureVisibility(structureToAdd, isVisible)
        sm.ScatterEvent('OnStructuresVisibilityUpdated')

    def _RemoveStructureFromRegistry(self, structureToRemove):
        if structureToRemove not in self.structureVisibilityRegistry:
            raise InvalidStateOfRegistry()
        self._SetStructureVisibility(structureToRemove, False)
        del self.structureVisibilityRegistry[structureToRemove]
        sm.ScatterEvent('OnStructuresVisibilityUpdated')

    def _RemoveStructuresFromRegistry(self, structuresToRemove):
        for structureToRemove in structuresToRemove:
            self._RemoveStructureFromRegistry(structureToRemove)

    def OnDockingAccessChangedForCurrentSolarSystem_Local(self):
        self.dockableStructuresInSystemHaveChanged = True

    def HasDockingAccessChanged(self):
        return bool(self.dockableStructuresInSystemHaveChanged)
