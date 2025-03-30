#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pvpFilaments\client\pvpFilamentSvc.py
import blue
from caching import Memoize
from carbon.common.lib.const import MIN
from carbon.common.script.sys.service import CoreService
import signals
from pvpFilaments.client import PVPFilamentActivationWindow, PVPFilamentEventWindow
from pvpFilaments.common.util import GetEventID
LEADERBOARD_CACHE_TIME = 1 * MIN

class PVPFilamentService(CoreService):
    __guid__ = 'svc.pvpFilamentSvc'
    __displayname__ = 'PVP Filament Client Service'
    __notifyevents__ = ['OnPVPFilamentsCharacterStatistics', 'OnPVPFilamentsLeaderboard']

    def __init__(self):
        super(PVPFilamentService, self).__init__()
        self.onCharacterStatisticsChanged = signals.Signal(signalName='onCharacterStatisticsChanged')
        self.onLeaderboardChanged = signals.Signal(signalName='onLeaderboardChanged')
        self._eventData = {}

    def RequestToJoinPVPQueue(self, itemID, typeID):
        return sm.RemoteSvc('pvpFilamentMgr').JoinPVPQueue(itemID, typeID)

    def RequestToLeavePVPQueue(self, itemID, typeID):
        sm.RemoteSvc('pvpFilamentMgr').LeavePVPQueue(itemID, typeID)

    def GetLeaderboard(self, eventInfo):
        eventData = self.GetAllEventDataByEventID()[GetEventID(eventInfo)]
        if _ShouldFetchLeaderboard(eventData):
            self._FetchLeaderboard(eventData)
            return None
        return eventData.leaderboard

    def _FetchLeaderboard(self, eventData):
        eventData.fetchingLeaderboard = True
        eventData.leaderboard = None
        sm.RemoteSvc('pvpFilamentMgr').GetLeaderboard(eventData.info.matchTypeID, eventData.info.scheduleID)

    def OnPVPFilamentsLeaderboard(self, info):
        eventData = self.GetAllEventDataByEventID()[GetEventID(info)]
        leaderboard = info['entries']
        characterEntry = None
        if leaderboard:
            if leaderboard[-1]['character_id'] == session.charid:
                characterEntry = leaderboard[-1]
                if leaderboard[-1]['rank'] > 100:
                    leaderboard.pop()
            else:
                for entry in leaderboard:
                    if entry['character_id'] == session.charid:
                        characterEntry = entry
                        break

        if eventData.statistics and characterEntry:
            eventData.statistics['rank'] = characterEntry['rank']
            self.onCharacterStatisticsChanged()
        eventData.leaderboard = leaderboard
        eventData.leaderboardFetchTime = blue.os.GetWallclockTime()
        eventData.fetchingLeaderboard = False
        self.onLeaderboardChanged()

    def GetCharacterStatistics(self, eventInfo):
        eventData = self.GetAllEventDataByEventID()[GetEventID(eventInfo)]
        if not eventData.statistics and not eventData.fetchingStatistics:
            eventData.fetchingStatistics = True
            sm.RemoteSvc('pvpFilamentMgr').GetCharacterStatistics(eventInfo.matchTypeID, eventInfo.scheduleID)
        return eventData.statistics

    def OnPVPFilamentsCharacterStatistics(self, info):
        newRank = info['statistics']['rank']
        eventData = self.GetAllEventDataByEventID()[GetEventID(info)]
        lastRank = eventData.statistics['rank'] if eventData.statistics else float('inf')
        eventData.statistics = info['statistics']
        eventData.fetchingStatistics = False
        self.onCharacterStatisticsChanged()
        if not eventData.fetchingLeaderboard and newRank != 0 and lastRank != newRank and (lastRank <= 100 or newRank <= 100):
            self._FetchLeaderboard(eventData)

    @Memoize(5)
    def GetAllEvents(self):
        return sm.RemoteSvc('pvpFilamentMgr').GetAllEvents().values()

    @Memoize(5)
    def GetActiveEvents(self):
        return sm.RemoteSvc('pvpFilamentMgr').GetActiveEvents().values()

    @Memoize(5)
    def GetMostRecentEvent(self):
        return sm.RemoteSvc('pvpFilamentMgr').GetMostRecentEvent()

    def GetAllEventDataByEventID(self):
        if not self._eventData:
            for eventInfo in self.GetAllEvents():
                self._eventData[GetEventID(eventInfo)] = EventData(eventInfo)

        return self._eventData

    def GetActiveEventDataByTypeID(self):
        eventDataByTypeID = {}
        for eventInfo in self.GetActiveEvents():
            eventDataByTypeID[eventInfo['filamentTypeID']] = eventInfo

        return eventDataByTypeID

    @Memoize(5)
    def GetNextEventDate(self):
        return sm.RemoteSvc('pvpFilamentMgr').GetNextEventDate()

    def isEventActive(self, typeID):
        return typeID in self.GetActiveEventDataByTypeID()

    def GetActiveEventByTypeID(self, typeID):
        return self.GetActiveEventDataByTypeID()[typeID]

    def OpenPVPfilamentWindow(self, key_item):
        PVPFilamentActivationWindow.Open(item=key_item)

    def OpenPVPFilamentEventWindow(self, filamentTypeID = None):
        PVPFilamentEventWindow.Open(filament_type_id=filamentTypeID)


def _ShouldFetchLeaderboard(eventData):
    if eventData.fetchingLeaderboard:
        return False
    if eventData.leaderboard is None:
        return True
    if blue.os.GetWallclockTime() - eventData.leaderboardFetchTime > LEADERBOARD_CACHE_TIME:
        return True
    return False


class EventData(object):

    def __init__(self, eventInfo):
        self.info = eventInfo
        self.leaderboard = None
        self.fetchingLeaderboard = False
        self.leaderboardFetchTime = None
        self.statistics = None
        self.fetchingStatistics = False
