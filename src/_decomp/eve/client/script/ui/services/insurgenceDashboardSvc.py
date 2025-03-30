#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\insurgenceDashboardSvc.py
from evePathfinder.core import IsUnreachableJumpCount
import uthread
import signals
import uthread2
from caching import Memoize
from carbon.common.script.sys.service import Service
from localization import GetByLabel
from pirateinsurgency.client.dashboard.const import SUPPRESSION_STAGES, CORRUPTION_STAGES, ConstructErrorMessageCont
from stackless_response_router.exceptions import UnpackException, TimeoutException

class InsurgencyDashboardSvc(Service):
    __guid__ = 'svc.insurgencyDashboardSvc'
    __startupdependencies__ = ['insurgencyCampaignSvc',
     'corruptionSuppressionSvc',
     'clientPathfinderService',
     'facwar']

    def __init__(self):
        super(InsurgencyDashboardSvc, self).__init__()
        self.SIGNAL_solarSystemSelectedFromMap = signals.Signal(signalName='solarSystemSelected')

    def Run(self, memStream = None):
        super(InsurgencyDashboardSvc, self).Run(memStream=memStream)

    def GetPersonalStats(self):
        return self.facwar.GetStats_Personal()

    def GetCurrentRank(self):
        currentRank = 1
        currRank = self.facwar.GetCharacterRankInfo(session.charid)
        if currRank:
            currentRank = currRank.currentRank
        rankName, rankDescription = self.facwar.GetRankLabel(session.warfactionid, currentRank)
        return (rankName, rankDescription)

    def IsSystemAffectedByInsurgency(self, systemID):
        if self.GetCampaignSnapshotForSystem(systemID) is None:
            return False
        return True

    def GetCampaignSnapshotForSystem(self, systemID):
        snapshots = self.insurgencyCampaignSvc.GetCurrentCampaignSnapshots_Memoized()
        for s in snapshots:
            if systemID in s.coveredSolarsystemIDs:
                return s

    def IsLocalSystemAffectedByInsurgency(self):
        snapshot = self.insurgencyCampaignSvc.GetLocalCampaignSnapshot()
        if snapshot is None:
            return False
        return True

    def GetLocalCampaignSnapshot(self):
        return self.insurgencyCampaignSvc.GetLocalCampaignSnapshot()

    def IsFOBSystem(self, systemID):
        snapshots = self.insurgencyCampaignSvc.GetCurrentCampaignSnapshots_Memoized()
        for s in snapshots:
            if systemID == s.originSolarsystemID:
                return True

        return False

    def GetSystemWarzoneID(self, systemID):
        snapshots = self.insurgencyCampaignSvc.GetCurrentCampaignSnapshots_Memoized()
        for s in snapshots:
            if systemID in s.coveredSolarsystemIDs:
                return s.warzoneID

    def OnSolarSystemSelectedFromMap(self, systemID):
        self.SIGNAL_solarSystemSelectedFromMap(systemID)

    def GetNumJumpsString(self, systemID):
        numJumps = self.clientPathfinderService.GetAutopilotJumpCount(session.solarsystemid2, systemID)
        if IsUnreachableJumpCount(numJumps):
            jumpsString = '-'
        else:
            jumpsString = str(numJumps)
        return GetByLabel('UI/FactionWarfare/frontlinesDashboard/jumps', numJumps=jumpsString)

    def GetCurrentCampaignSnapshots(self):
        return self.insurgencyCampaignSvc.GetCurrentCampaignSnapshots_Memoized()

    def GetCurrentCampaignSnapshotByID(self, campaignID):
        for snapshot in self.insurgencyCampaignSvc.GetCurrentCampaignSnapshots_Memoized():
            if snapshot.campaignID == campaignID:
                return snapshot

    def RequestAllCorruptionAndSuppressionValuesForCampaignID(self, campaignID, callback):

        def run():
            try:
                data = self._BlockingGetAllCorruptionAndSuppressionValues(campaignID)
            except (TimeoutException, UnpackException):
                callback(None)
                return

            callback(data)

        uthread2.StartTasklet(run)

    def RequestCurrentSuppressionStage(self, campaignID, callback):

        def calculation_callback(data):
            if data is None:
                callback(None)
                return
            values = [ d.stage for d in data ]
            result = self._GetNumberOfMaxes(values, SUPPRESSION_STAGES)
            callback(result)

        self.RequestAllCurrentSuppressionValues(campaignID, calculation_callback)

    def RequestCurrentCorruptionStage(self, campaignID, callback):

        def calculation_callback(data):
            if data is None:
                callback(None)
                return
            values = [ d.stage for d in data ]
            result = self._GetNumberOfMaxes(values, CORRUPTION_STAGES)
            callback(result)

        self.RequestAllCurrentCorruptionValues(campaignID, calculation_callback)

    def _GetNumberOfMaxes(self, values, max):
        n = 0
        for v in values:
            if v >= max:
                n += 1

        return n

    def RequestAllCurrentSuppressionValues(self, campaignID, callback):
        snapshot = None
        for s in self.insurgencyCampaignSvc.GetCurrentCampaignSnapshots_Memoized():
            if s.campaignID == campaignID:
                snapshot = s

        if snapshot is None:
            raise RuntimeError('no snapshot with campaignID %s' % campaignID)
        uthread2.StartTasklet(self._AsyncGetAllPerSystemData, snapshot, self.corruptionSuppressionSvc.GetSystemSuppression, callback)

    def RequestAllCurrentCorruptionValues(self, campaignID, callback):
        snapshot = None
        for s in self.insurgencyCampaignSvc.GetCurrentCampaignSnapshots_Memoized():
            if s.campaignID == campaignID:
                snapshot = s

        if snapshot is None:
            raise RuntimeError('no snapshot with campaignID %s' % campaignID)
        uthread2.StartTasklet(self._AsyncGetAllPerSystemData, snapshot, self.corruptionSuppressionSvc.GetSystemCorruption, callback)

    def RequestSystemSuppression(self, systemID, callback):

        def run():
            try:
                data = self.corruptionSuppressionSvc.GetSystemSuppression(systemID)
            except (TimeoutException, UnpackException):
                callback(None)
                return

            callback(data)

        uthread2.StartTasklet(run)

    def RequestSystemCorruption(self, systemID, callback):

        def run():
            try:
                data = self.corruptionSuppressionSvc.GetSystemCorruption(systemID)
            except (TimeoutException, UnpackException):
                callback(None)
                return

            callback(data)

        uthread2.StartTasklet(run)

    def RequestLocalSystemCorruption(self, callback):

        def run():
            try:
                data = self.corruptionSuppressionSvc.GetCurrentSystemCorruption_Cached()
            except (TimeoutException, UnpackException):
                callback(None)
                return

            callback(data)

        uthread2.StartTasklet(run)

    def RequestLocalSystemSuppression(self, callback):

        def run():
            try:
                data = self.corruptionSuppressionSvc.GetCurrentSystemSuppression_Cached()
            except (TimeoutException, UnpackException):
                callback(None)
                return

            callback(data)

        uthread2.StartTasklet(run)

    def RequestSuppressionStages(self, callback):

        def run():
            try:
                data = self.corruptionSuppressionSvc.GetSuppressionStages()
            except (TimeoutException, UnpackException):
                callback(None)
                return

            callback(data)

        uthread2.StartTasklet(run)

    def RequestCorruptionStages(self, callback):

        def run():
            try:
                data = self.corruptionSuppressionSvc.GetCorruptionStages()
            except (TimeoutException, UnpackException):
                callback(None)
                return

            callback(data)

        uthread2.StartTasklet(run)

    def _BlockingGetAllCorruptionAndSuppressionValues(self, campaignID):
        snapshot = self.GetCurrentCampaignSnapshotByID(campaignID)
        rawData = uthread.parallel([(self._BlockingGetAllPerSystemData, (snapshot, self.corruptionSuppressionSvc.GetSystemCorruption)), (self._BlockingGetAllPerSystemData, (snapshot, self.corruptionSuppressionSvc.GetSystemSuppression))])
        data = {'corruption': {data.systemID:data for data in rawData[0]},
         'suppression': {data.systemID:data for data in rawData[1]}}
        return data

    def _AsyncGetAllPerSystemData(self, campaign, request_fun, callback):
        try:
            data = self._BlockingGetAllPerSystemData(campaign, request_fun)
        except (TimeoutException, UnpackException):
            callback(None)
            return

        callback(data)

    def _BlockingGetAllPerSystemData(self, campaign, request_fun):
        return uthread.parallel([ (request_fun, (systemID,)) for systemID in campaign.coveredSolarsystemIDs ])

    @Memoize(3)
    def GetIceHeistInstances_Memoized(self):
        return sm.RemoteSvc('dungeonInstanceCacheMgr').GetPirateInsurgencyIceHeistInstances()


def WrapCallbackWithErrorHandling(callbackFun, parentContainer = None, errorMessageLabel = 'UI/PirateInsurgencies/insurgencyDataError', onErrorCallback = None, fullErrorBox = True):

    def _fun(data):
        if data is None:
            if onErrorCallback is not None:
                onErrorCallback()
            if parentContainer is not None:
                ConstructErrorMessageCont(parentContainer, errorMessageLabel, fullErrorBox=fullErrorBox)
        else:
            callbackFun(data)

    return _fun
