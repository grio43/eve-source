#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\missions\client\missionObjectivesTracker.py
from carbon.common.script.sys.service import Service
from carbonui.util.bunch import Bunch
from carbonui.util.sortUtil import SortListOfTuples
from collections import defaultdict
from eveexceptions.exceptionEater import ExceptionEater
from eve.common.lib.appConst import agentMissionStateAccepted, agentMissionAccepted, agentMissionQuit, agentMissionModified
from eve.common.script.sys import idCheckers
from gametime import GetWallclockTime
import inventorycommon.const as const
from .ui.missionObjectiveData import CreateObjective
from .active_agent_mission import ActiveAgentMission
AGENT_FOR_LAST_ACCEPTED_MISSION_SETTING = 'AgentForLastAcceptedMission'
DELAY_ON_DUNGEON_TRIGGER_SECS = 1.0
MISSION_UPDATE_DELAY_MSEC = 3000

class MissionObjectivesTracker(Service):
    __guid__ = 'svc.missionObjectivesTracker'
    __notifyevents__ = ['OnItemsChanged',
     'OnMissionsUpdated',
     'OnAgentMissionChanged',
     'OnAgentMissionObjectivesCompleted',
     'OnAgentMissionObjectivesFailed',
     'OnClientEvent_WarpFinished',
     'OnSessionChanged',
     'OnSessionReset',
     'OnBallparkSetState']
    __startupdependencies__ = ['journal']

    def Run(self, *args):
        super(MissionObjectivesTracker, self).Run(*args)
        self.Initialize()

    def Initialize(self):
        self.agentList = []
        self.agentMissions = {}
        self.waitingForTypeIDs = defaultdict(lambda : [])
        self.agentsWaitingForStuff = {}
        self.destinationTriggers = defaultdict(lambda : [])
        self.currentAgentMissionInfo = None
        self.missionObjectives = defaultdict(lambda : None)
        self.missionTrackerMgr = sm.RemoteSvc('missionTrackerMgr')

    def GetAgentMissions(self, *args):
        allMissionsList = []
        missions = self.journal.GetMyAgentJournalDetails()[0]
        HOMEBASE = 0
        NOTHOMEBASE = 1
        if missions:
            for mission in missions:
                missionState, _, _, missionNameID, agentID, expirationTime, bookmarks, _, _, contentID = mission
                if missionState != agentMissionStateAccepted or expirationTime and expirationTime < GetWallclockTime():
                    continue
                homeBaseBms = []
                otherBms = []
                foundHomeBaseBm = False
                for bm in bookmarks:
                    if bm.locationType == 'agenthomebase':
                        homeBaseBms.append((HOMEBASE, bm))
                    elif 'isAgentBase' in bm.__dict__ and bm.isAgentBase:
                        foundHomeBaseBm = True
                        otherBms.append((HOMEBASE, bm))
                    else:
                        otherBms.append((NOTHOMEBASE, bm))

                bookmarksIwant = otherBms
                if not foundHomeBaseBm:
                    bookmarksIwant.extend(homeBaseBms)
                bookmarksIwant = SortListOfTuples(bookmarksIwant)
                bmInfo = Bunch(missionNameID=missionNameID, contentID=contentID, bookmarks=bookmarksIwant, agentID=agentID)
                allMissionsList.append((expirationTime, bmInfo))

            allMissionsList = SortListOfTuples(allMissionsList)
        return allMissionsList

    def OnClientEvent_WarpFinished(self, *args, **kwargs):
        self._ResetAgentMissionInfoForAllMissions()
        self.UpdateMissionsPanel()

    def OnSessionChanged(self, isRemote, sess, change):
        if not session.charid:
            return
        self.UpdateMissionStatusForSessionChange(change)
        self.UpdateMissionsPanel()

    def OnSessionReset(self):
        self.Initialize()

    def OnBallparkSetState(self, *args):
        self.UpdateMissionsPanel()

    def OnItemsChanged(self, items, change, locationData):
        relevantDestinations = [const.flagCargo,
         const.flagGeneralMiningHold,
         const.flagSpecialAsteroidHold,
         const.flagSpecializedIceHold,
         const.flagSpecializedGasHold,
         const.flagSpecializedMineralHold,
         const.flagSpecializedSalvageHold,
         const.flagSpecializedShipHold,
         const.flagSpecializedSmallShipHold,
         const.flagSpecializedMediumShipHold,
         const.flagSpecializedLargeShipHold,
         const.flagSpecializedIndustrialShipHold,
         const.flagJunkyardTrashed]
        if session.stationid:
            relevantDestinations.append(const.flagHangar)
        agentList = []
        for item in items:
            if item.typeID in self.waitingForTypeIDs.keys():
                if item.flagID in relevantDestinations:
                    agentID = self.waitingForTypeIDs[item.typeID]
                    agentList += agentID

        if agentList:
            self.UpdateMissionStatusData(agentList)

    def _WantNotificationWhenTypeIDArrives(self, info):
        if not info:
            return False
        if info[0].startswith('MissionFetch'):
            return True
        for key in ('TransportItemsMissing', 'DropOffItemsMissing', 'AllObjectivesComplete'):
            if key in info:
                return True

        return False

    def OnMissionsUpdated(self, missions):
        for mission in missions:
            agentID = mission['agentID']
            info = mission['info'] or None
            if self._WantNotificationWhenTypeIDArrives(info):
                self.NotifyTrackerWhenTypeIDArrives(agentID, int(info[1]))
            else:
                self.StopNotifyingTrackerForTypeID(agentID)
            isUpdateRequired = self.currentAgentMissionInfo.get(agentID, None) != info
            self.missionObjectives[agentID] = None
            self.SetCurrentAgentMissionInfo(agentID, info)
            if agentID in self.agentMissions:
                self.agentMissions[agentID].update_objective(info)
            if isUpdateRequired:
                sm.ScatterEvent('OnAgentMissionChange', agentMissionModified, agentID)

    def OnAgentMissionChanged(self, missionEvent, agentID):
        if missionEvent != agentMissionModified:
            self.SetCurrentAgentMissionInfo(agentID, None)
        self.missionObjectives[agentID] = None
        self._UpdateAgentMissions()
        with ExceptionEater('exception during - missiontracker remove/add agent'):
            if missionEvent == agentMissionQuit:
                if agentID in self.agentList:
                    self.agentList.remove(agentID)
                    self.RemoveDestinationNotificationTrigger(agentID)
            elif missionEvent == agentMissionAccepted:
                if agentID not in self.agentList:
                    self.agentList.append(agentID)
                self.UpdateMissionStatusData((agentID,))
                self._SetAgentForLastAcceptedMission(agentID)
        callback = sm.GetService('infoPanel').UpdateExpandedAgentMission if missionEvent == agentMissionAccepted else None
        self.UpdateMissionsPanel(callback)

    def OnAgentMissionObjectivesCompleted(self, agentID):
        self._UpdateCurrentAgentMissionInfo(agentID)

    def OnAgentMissionObjectivesFailed(self, agentID):
        self._UpdateCurrentAgentMissionInfo(agentID)

    def NotifyTrackerWhenTypeIDArrives(self, agentID, typeID):
        if idCheckers.IsNPCCharacter(typeID):
            activeMission = self.agentMissions.get(agentID)
            if activeMission and activeMission.context:
                typeID = activeMission.context.get_value('deliver_items', {}).get('type_id', typeID)
        self.agentsWaitingForStuff[agentID] = typeID
        if agentID not in self.waitingForTypeIDs[typeID]:
            self.waitingForTypeIDs[typeID].append(agentID)

    def StopNotifyingTrackerForTypeID(self, agentID):
        if not self.agentsWaitingForStuff.has_key(agentID):
            return
        typeID = self.agentsWaitingForStuff[agentID]
        if agentID in self.waitingForTypeIDs[typeID]:
            self.waitingForTypeIDs[typeID].remove(agentID)
            del self.agentsWaitingForStuff[agentID]

    def UpdateMissionStatusForSessionChange(self, change):
        if change.has_key('locationid'):
            if change['locationid'][0] in self.destinationTriggers.keys():
                self.UpdateMissionStatusData(self.destinationTriggers[change['locationid'][0]])
            if change['locationid'][1] in self.destinationTriggers.keys():
                self.UpdateMissionStatusData(self.destinationTriggers[change['locationid'][1]])
        self._ResetAgentMissionInfoForAllMissions()

    def UpdateMissionStatusData(self, agentList):
        with ExceptionEater('Exception during missiontracker.UpdateAllMissions'):
            if agentList:
                self.missionTrackerMgr.UpdateAllMissions(agentList)

    def SetDestinationNotificationTrigger(self, locationID, agentID):
        if agentID not in self.destinationTriggers[locationID]:
            self.destinationTriggers[locationID].append(agentID)

    def RemoveDestinationNotificationTrigger(self, agentID):
        for locationID in self.destinationTriggers.keys():
            if agentID in self.destinationTriggers[locationID]:
                self.destinationTriggers[locationID].remove(agentID)

    def RegisterMissionTracking(self):
        with ExceptionEater('exception during RegisterMissionTracking'):
            self._UpdateAgentMissions()
            missions = self.journal.GetMyAgentJournalDetails()[0]
            for mission in missions:
                missionState, _, _, _, agentID, expirationTime, _, _, _, _ = mission
                if missionState != agentMissionStateAccepted or expirationTime and expirationTime < GetWallclockTime():
                    continue
                if agentID not in self.agentList:
                    self.agentList.append(agentID)

            self.UpdateMissionStatusData(self.agentList)

    def _UpdateAgentMissions(self):
        missions = self.journal.GetMyAgentJournalDetails()[0]
        activeMissions = set()
        for mission in missions:
            missionState = mission[0]
            agentID = mission[4]
            expirationTime = mission[5]
            if missionState == agentMissionStateAccepted and not (expirationTime and expirationTime < GetWallclockTime()):
                activeMissions.add(agentID)
                if agentID not in self.agentMissions:
                    self.agentMissions[agentID] = ActiveAgentMission(mission)

        for agentID in self.agentMissions.keys():
            if agentID not in activeMissions:
                self.agentMissions[agentID].stop()
                del self.agentMissions[agentID]

    def _InitializeCurrentAgentMissionInfo(self):
        self.currentAgentMissionInfo = {}
        for mission in self.GetAgentMissions():
            self._UpdateCurrentAgentMissionInfo(mission.agentID)

    def _UpdateCurrentAgentMissionInfo(self, agentID):
        missionInfo = self.missionTrackerMgr.GetMissionInfoItems(agentID)
        self.currentAgentMissionInfo[agentID] = missionInfo or None
        if missionInfo and agentID in self.agentMissions:
            self.agentMissions[agentID].update_objective(missionInfo)

    def SetCurrentAgentMissionInfo(self, agentID, info):
        if self.currentAgentMissionInfo is None:
            self._InitializeCurrentAgentMissionInfo()
        self.currentAgentMissionInfo[agentID] = info

    def GetCurrentAgentMissionInfo(self, agentID):
        if self.currentAgentMissionInfo is None:
            self._InitializeCurrentAgentMissionInfo()
        return self.currentAgentMissionInfo.get(agentID, None)

    def GetCurrentMissionObjective(self, agentID):
        currentMissionInfo = self.GetCurrentAgentMissionInfo(agentID)
        objectiveData = CreateObjective(currentMissionInfo, agentID)
        return objectiveData

    def _ResetAgentMissionInfoForAllMissions(self):
        self._InitializeCurrentAgentMissionInfo()
        self.missionObjectives = defaultdict(lambda : None)

    def HasActiveMission(self, agentID):
        for mission in self.GetAgentMissions():
            if mission.agentID == agentID:
                return True

        return False

    def GetAllAgentMissionInfo(self, agentID):
        if not self.missionObjectives[agentID]:
            self.missionObjectives[agentID] = self.missionTrackerMgr.GetAllMissionObjectives(agentID)
        return self.missionObjectives[agentID]

    def GetAgentForLastAcceptedMission(self):
        return settings.char.ui.Get(AGENT_FOR_LAST_ACCEPTED_MISSION_SETTING, None)

    def _SetAgentForLastAcceptedMission(self, agentID):
        settings.char.ui.Set(AGENT_FOR_LAST_ACCEPTED_MISSION_SETTING, agentID)

    def IsInActiveMissionDungeon(self, agentID):
        return self.missionTrackerMgr.IsInActiveDungeonID(agentID)

    def UpdateMissionsPanel(self, callback = None):
        sm.GetService('infoPanel').UpdateMissionsPanel(callback)
