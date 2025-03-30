#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\fwWarzoneSvc.py
import random
from caching import Memoize
from carbon.common.script.sys.service import Service
from fwwarzone.heroNotifications import SystemFlipped, SystemChangedAdjacency, ObjectiveCompletedInSystem, BattlefieldWon, DungeonConquered, DungeonDefended
OCCUPATION_STATE_UNKNOWN = (None, None)

class FwWarzoneSvc(Service):
    __guid__ = 'svc.fwWarzoneSvc'
    __displayname__ = 'FW Warzone client service'
    __startupdependencies__ = ['machoNet', 'heroNotification']
    __notifyevents__ = ['OnSessionChanged',
     'OnWarzoneOccupationStateUpdated',
     'OnFwObjectiveCompletedInSolarSystem',
     'OnFwScoreboardWon',
     'OnFacWarDungeonCompleted']
    _localOccupationSystemAndState = OCCUPATION_STATE_UNKNOWN
    _currentBattlefields = set()

    def _OccupationStateLock(self):
        return self.LockedService('OccupationState')

    def OnSessionChanged(self, isremote, session, change):
        if 'solarsystemid2' in change:
            self._localOccupationSystemAndState = OCCUPATION_STATE_UNKNOWN

    def GetLocalOccupationState(self):
        if self._localOccupationSystemAndState[0] != session.solarsystemid2:
            with self._OccupationStateLock():
                if self._localOccupationSystemAndState[0] != session.solarsystemid2:
                    self.LogInfo('GetLocalOccupationState - localOccupationState is unknown - asking the server')
                    solarsystemID, occupationState = sm.RemoteSvc('fwWarzoneSolarsystem').GetLocalOccupationState()
                    if solarsystemID != session.solarsystemid2:
                        solarsystemID, occupationState = sm.RemoteSvc('fwWarzoneSolarsystem').GetLocalOccupationState()
                    if solarsystemID == session.solarsystemid2:
                        self._localOccupationSystemAndState = (solarsystemID, occupationState)
                    else:
                        raise RuntimeError('fwWarzoneSvc.GetLocalOccupationState failed to get state from server despite retrying')
        return self._localOccupationSystemAndState[1]

    def GetOccupationState(self, solarsystemID):
        if solarsystemID == session.solarsystemid2:
            return self.GetLocalOccupationState()
        occupationStatesBySolarsystemByWarzone = self.GetAllOccupationStates()
        for occupationStatesBySolarsystem in occupationStatesBySolarsystemByWarzone.itervalues():
            if solarsystemID in occupationStatesBySolarsystem:
                return occupationStatesBySolarsystem[solarsystemID]

    def GetAllOccupationStates(self):
        return sm.RemoteSvc('fwWarzoneSolarsystem').GetAllWarzonesOccupationStates()

    def GetAllOccupationStatesUncached(self):
        return sm.RemoteSvc('fwWarzoneSolarsystem').GetAllWarzonesOccupationStatesUncached()

    def OnWarzoneOccupationStateUpdated(self, solarsystemID, newOccupationState):
        self.LogInfo('fwWarzoneSvc.OnWarzoneOccupationStateUpdated', solarsystemID, newOccupationState)
        with self._OccupationStateLock():
            if solarsystemID != session.solarsystemid2:
                return
            if self._localOccupationSystemAndState == (solarsystemID, newOccupationState):
                return
            oldOccupationState = self._localOccupationSystemAndState[1]
            self._localOccupationSystemAndState = (solarsystemID, newOccupationState)
        sm.ScatterEvent('OnWarzoneOccupationStateUpdated_Local')
        if oldOccupationState:
            if oldOccupationState.occupierID != newOccupationState.occupierID:
                self.ShowFlipFanfare(solarsystemID, newOccupationState)
            elif oldOccupationState.adjacencyState != newOccupationState.adjacencyState:
                self.ShowChangedAdjacency(solarsystemID, newOccupationState)

    def OnFwObjectiveCompletedInSolarSystem(self, solarSystemID, targetFactionID, objectiveMode):

        def PlayVideo(parent, cancellation_token):
            ObjectiveCompletedInSystem(parent, solarSystemID, targetFactionID, objectiveMode)

        self.heroNotification.play(PlayVideo, 1)

    def OnFwScoreboardWon(self, solarSystemID, scoreboardItemID, winnerFactionID):

        def PlayVideo(parent, cancellation_token):
            BattlefieldWon(parent, solarSystemID, winnerFactionID)

        self.heroNotification.play(PlayVideo, 1)

    def OnFacWarDungeonCompleted(self, wasConquered, factionID):
        if wasConquered:

            def PlayVideo(parent, cancellation_token):
                DungeonConquered(parent, factionID)

        else:

            def PlayVideo(parent, cancellation_token):
                DungeonDefended(parent, factionID)

        self.heroNotification.play(PlayVideo, 1)

    def IsWarzoneSolarSystem(self, solarsystemID):
        if solarsystemID == session.solarsystemid2:
            occupationState = self.GetLocalOccupationState()
            return bool(occupationState)
        occupationStatesBySolarsystemByWarzone = self.GetAllOccupationStates()
        for occupationStatesBySolarsystem in occupationStatesBySolarsystemByWarzone.itervalues():
            if solarsystemID in occupationStatesBySolarsystem:
                return True

        return False

    def GetSystemOccupier(self, solarSystemID):
        occupationState = self.GetOccupationState(solarSystemID)
        if occupationState is not None:
            return occupationState.occupierID

    def BattleFieldAdded(self, itemID, typeID, score):
        if itemID not in self._currentBattlefields:
            self._currentBattlefields.add(itemID)
            sm.ScatterEvent('OnFwBattlefieldAdded', itemID, typeID, score)

    def BattleFieldRemoved(self, itemID):
        if itemID in self._currentBattlefields:
            self._currentBattlefields.discard(itemID)
            sm.ScatterEvent('OnFwBattlefieldUpdated')

    def GetBattleFieldScoreboards(self):
        return self._currentBattlefields

    def GetBattlefieldInstances(self):
        return sm.RemoteSvc('dungeonInstanceCacheMgr').GetFactionWarfareBattlefieldInstances()

    def ShowFlipFanfare(self, solarSystemID, newOccupationState):
        if solarSystemID != session.solarsystemid2:
            return

        def PlayVideo(parent, cancellation_token):
            SystemFlipped(parent, solarSystemID, newOccupationState)

        self.heroNotification.play(PlayVideo, 1)

    def ShowChangedAdjacency(self, solarSystemID, newOccupationState):
        if solarSystemID != session.solarsystemid2:
            return

        def PlayVideo(parent, cancellation_token):
            SystemChangedAdjacency(parent, solarSystemID, newOccupationState)

        self.heroNotification.play(PlayVideo, 0)

    def GetWarzoneIdForFaction(self, factionID):
        allWarzones = self.GetAllWarzones()
        for zoneID, teams in allWarzones.iteritems():
            if factionID in teams:
                return zoneID

        return random.choice(allWarzones.keys())

    def GetFactionHQSystem(self, factionId):
        factionIdToHQSystem = self.GetAllHQSystems()
        if factionId in factionIdToHQSystem:
            return factionIdToHQSystem[factionId]

    def GetAdjacencyState(self, solarsystemID):
        fwOccupationState = self.GetOccupationState(solarsystemID)
        if fwOccupationState:
            return fwOccupationState.adjacencyState

    @Memoize
    def GetAllWarzones(self):
        return sm.RemoteSvc('fwWarzoneSolarsystem').GetAllWarzones()

    @Memoize
    def GetAllHQSystems(self):
        return sm.RemoteSvc('fwWarzoneSolarsystem').GetHQSystemIDs()
