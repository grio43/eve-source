#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\achievements\client\achievementSvc.py
import blue
import threadutils
from achievements.client.eventHandler import EventHandler
from achievements.common.achievementGroups import GetAchievementGroup, GetTaskIds
from achievements.common.achievementLoader import AchievementLoader
from achievements.common.statsTracker import StatsTracker
from achievements.common.util import AreOpportunitiesEnabled, UpdateAndGetNewAchievements, GetClientAchievements, GetAchievementsByEventsDict
from carbon.common.script.sys.service import Service

class AchievementTrackerClientService(Service):
    __guid__ = 'svc.achievementSvc'
    service = 'svc.achievementSvc'
    __startupdependencies__ = ['machoNet']
    __dependencies__ = ['machoNet']
    __notifyevents__ = ['OnServerAchievementUnlocked',
     'OnAchievementsReset',
     'OnSessionChanged',
     'OnSessionReset',
     'ProcessShutdown']
    _debugStatsForCharacter = None
    remoteService = None
    hasAllData = False
    achievementsEnabled = False

    def Run(self, memStream = None, remoteService = None, scatterService = sm):
        self.scatterService = scatterService
        self.ReInitialize()

    def ReInitialize(self):
        self.hasAllData = False
        self.eventHandler = EventHandler(self)
        self._allAchievements = self.LoadAchievements(getDisabled=True)
        self.clientAchievements = GetClientAchievements(self._allAchievements)
        self.achievementsByEventsDict = GetAchievementsByEventsDict(self.clientAchievements)
        self.clientStatsTracker = StatsTracker()
        self.completedDict = {}
        self.scatterService.ScatterEvent('OnAchievementsDataInitialized')

    def GetAllAchievements(self):
        return self._allAchievements

    def GetCompletedTaskIds(self):
        return self.completedDict.keys()

    def UpdateEnabledStatus(self):
        self.achievementsEnabled = AreOpportunitiesEnabled()

    def IsEnabled(self):
        return self.achievementsEnabled

    def GetDebugStatsFromCharacter(self, force = False):
        if self._debugStatsForCharacter is None or force is True:
            self._debugStatsForCharacter = self.remoteService.GetDebugStatsFromCharacter(session.charid)
        return self._debugStatsForCharacter

    def HasData(self):
        return self.hasAllData

    def GetFullAchievementList(self):
        return self._allAchievements.values()

    def OnAchievementsReset(self):
        self.completedDict = {}
        self.FetchMyAchievementStatus()
        self.scatterService.ScatterEvent('OnAchievementsDataInitialized')

    def ResetAllForCharacter(self):
        self.remoteService.ResetAllForChar()

    def SetActiveAchievementGroupID(self, groupID, emphasize = False):
        pass

    def GetActiveAchievementGroupID(self):
        return None

    def GetAchievementTask(self, achievementTaskID):
        return self._allAchievements.get(achievementTaskID, None)

    def OnServerAchievementUnlocked(self, achievementsInfo):
        if AreOpportunitiesEnabled():
            achievementDict = achievementsInfo['achievementDict']
            self.HandleAchievementsUnlocked(achievementDict)

    def HandleAchievementsUnlocked(self, achievementDict, taskIdsForMe = None):
        self.MarkAchievementAsCompleted(achievementDict)
        if not self.IsEnabled():
            return
        taskIdsForMyGroup = taskIdsForMe
        if taskIdsForMyGroup is None:
            taskIdsForMyGroup = GetTaskIds()
        for achievementID in achievementDict:
            if achievementID not in self._allAchievements:
                continue
            if achievementID not in taskIdsForMyGroup:
                continue
            achievement = self._allAchievements[achievementID]
            isActiveGroupCompleted = self.IsGroupForTaskActiveAndCompleted(achievementID)
            sm.ScatterEvent('OnAchievementChanged', achievement, activeGroupCompleted=isActiveGroupCompleted)

    def MarkAchievementAsCompleted(self, achievementDict):
        for taskID, timestamp in achievementDict.iteritems():
            if taskID not in self._allAchievements:
                continue
            self.completedDict[taskID] = timestamp

    def SendNotification(self, notificationData, notificationType):
        sm.ScatterEvent('OnNotificationReceived', 123, notificationType, session.charid, blue.os.GetWallclockTime(), data=notificationData)

    def FetchMyAchievementStatus(self):
        achievementAndEventInfo = self.remoteService.GetCompletedAchievementsAndClientEventCount()
        self.completedDict = achievementAndEventInfo['completedDict']
        self.PopulateEventHandler(achievementAndEventInfo['eventDict'])
        self.UpdateAchievementList()
        self.hasAllData = True

    def PopulateEventHandler(self, eventCountDict):
        for eventName, eventCount in eventCountDict.iteritems():
            if eventCount < 1:
                self.clientStatsTracker.statistics[eventName] = 0
            else:
                self.clientStatsTracker.LogStatistic(eventName, eventCount, addToUnlogged=False)

    def IsGroupForTaskActiveAndCompleted(self, taskID):
        activeGroupID = self.GetActiveAchievementGroupID()
        if activeGroupID and self.IsAchievementInGroup(taskID, activeGroupID):
            activeGroupCompleted = self._IsActiveGroupCompleted()
        else:
            activeGroupCompleted = False
        return activeGroupCompleted

    def _IsActiveGroupCompleted(self):
        currentGroupID = self.GetActiveAchievementGroupID()
        if not currentGroupID:
            return False
        achievementGroup = GetAchievementGroup(currentGroupID)
        return achievementGroup.IsCompleted()

    def UpdateAchievementList(self):
        for achievementID in self.completedDict:
            if achievementID in self._allAchievements:
                self._allAchievements[achievementID].completed = True

    def LoadAchievements(self, getDisabled = False):
        return AchievementLoader().GetAchievements(getDisabled=getDisabled)

    def IsAchievementCompleted(self, achievementID):
        return achievementID in self.completedDict

    def IsAchievementInGroup(self, achievementID, groupID):
        achievementGroup = GetAchievementGroup(groupID)
        if achievementGroup:
            return achievementGroup.HasAchievement(achievementID)
        else:
            return False

    def OnSessionChanged(self, isRemote, session, change):
        if 'charid' in change and not self.HasData():
            if self.remoteService is None:
                self.remoteService = sm.RemoteSvc('achievementTrackerMgr')
            self.FetchMyAchievementStatus()
            self.UpdateEnabledStatus()

    def OnSessionReset(self):
        self.ReInitialize()

    def ProcessShutdown(self):
        try:
            self.UpdateClientAchievementsAndCountersOnServer()
        except Exception as e:
            self.LogError('Failed at storing client achievement events, e = ', e)

    def LogClientEvent(self, eventName, value = 1):
        achievementsWithEvent = self.achievementsByEventsDict.get(eventName, set())
        achievementsLeft = achievementsWithEvent - set(self.completedDict.keys())
        if not achievementsLeft:
            return
        self.clientStatsTracker.LogStatistic(eventName, value, addToUnlogged=False)
        achievementsWereCompleted = self.CheckAchievementStatus()
        if not achievementsWereCompleted:
            self.UpdateClientAchievementsAndCountersOnServer_throttled()

    def CheckAchievementStatus(self):
        newAchievementSet = self.GetNewAchievementsForCharacter()
        if newAchievementSet:
            self.HandleAchievementsUnlocked(newAchievementSet)
            self.UpdateClientAchievementsAndCountersOnServer()
            return True
        return False

    @threadutils.throttled(180)
    def UpdateClientAchievementsAndCountersOnServer_throttled(self):
        self.UpdateClientAchievementsAndCountersOnServer()

    def UpdateClientAchievementsAndCountersOnServer(self):
        if session.charid:
            stats = self.clientStatsTracker.GetStatistics()
            self.remoteService.UpdateClientAchievmentsAndCounters(self.completedDict, dict(stats))

    def GetNewAchievementsForCharacter(self):
        return UpdateAndGetNewAchievements(self.clientAchievements, self.completedDict, self.clientStatsTracker)
