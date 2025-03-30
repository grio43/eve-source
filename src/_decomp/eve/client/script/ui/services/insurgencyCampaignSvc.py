#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\insurgencyCampaignSvc.py
from characterdata import factions
from localization import GetByLabel
import uthread2
from caching import Memoize
if False:
    from typing import Optional, List
from carbon.common.script.sys.service import Service
from pirateinsurgency.campaignClientSnapshot import CampaignClientSnapshot
from pirateinsurgency.const import CAMPAIGN_STATE_FORECASTING, CAMPAIGN_STATE_ACTIVE, CAMPAIGN_STATE_PIRATE_WIN, CAMPAIGN_STATE_ANTIPIRATE_WIN, CAMPAIGN_STATE_NO_WINNER
from eve.common.script.util import notificationconst
from carbonui.uicore import uicore
LOCAL_CAMPAIGN_UNKNOWN = 'LOCAL_CAMPAIGN_UNKNOWN'

class InsurgencyCampaignSvc(Service):
    __guid__ = 'svc.insurgencyCampaignSvc'
    __displayname__ = 'Insurgency Campaign client service'
    __startupdependencies__ = []
    __notifyevents__ = ['OnSessionChanged',
     'OnInsurgencyCampaignStartedForLocation',
     'OnInsurgencyCampaignUpdatedForLocation',
     'OnInsurgencyCampaignEndingForLocation',
     'OnInsurgencyStateChangedForFaction',
     'OnSystemFullyCorruptedForFaction',
     'OnSystemFullySuppressedForFaction',
     'OnEnterSpace']
    _localCampaignSnapshot = LOCAL_CAMPAIGN_UNKNOWN

    def __init__(self):
        super(InsurgencyCampaignSvc, self).__init__()
        self.GetCurrentCampaignSnapshots_Memoized.clear_memoized()

    def OnSessionChanged(self, isremote, session, change):
        if 'solarsystemid2' in change:
            self._localCampaignSnapshot = LOCAL_CAMPAIGN_UNKNOWN

    def _LocalCampaignSnapshotLock(self):
        return self.LockedService('LocalCampaignSnapshot')

    def GetLocalCampaignSnapshot(self):
        if self._localCampaignSnapshot is LOCAL_CAMPAIGN_UNKNOWN:
            with self._LocalCampaignSnapshotLock():
                if self._localCampaignSnapshot is LOCAL_CAMPAIGN_UNKNOWN:
                    self.LogInfo('GetLocalCampaignSnapshot - _localCampaignSnapshot is unknown - asking the server')
                    solarsystemID, campaignSnapshot = sm.RemoteSvc('insurgencySolarsystem').GetLocalCampaignClientSnapshot()
                    if solarsystemID != session.solarsystemid2:
                        solarsystemID, campaignSnapshot = sm.RemoteSvc('insurgencySolarsystem').GetLocalCampaignClientSnapshot()
                    if solarsystemID == session.solarsystemid2:
                        self._localCampaignSnapshot = campaignSnapshot
        return self._localCampaignSnapshot

    def OnInsurgencyCampaignStartedForLocation(self, campaignSnapshot):
        self.GetCurrentCampaignSnapshots_Memoized.clear_memoized()
        with self._LocalCampaignSnapshotLock():
            if session.solarsystemid2 not in campaignSnapshot.coveredSolarsystemIDs:
                return
            self.LogWarn('insurgencyCampaignSvc.OnInsurgencyCampaignStartedForLocation', campaignSnapshot)
            self._localCampaignSnapshot = campaignSnapshot
            sm.ScatterEvent('OnInsurgencyCampaignStartedForLocation_Local', campaignSnapshot)
            self.ShowInsurgencyCampaignStartedForLocation()

    def OnInsurgencyCampaignUpdatedForLocation(self, campaignSnapshot):
        self.GetCurrentCampaignSnapshots_Memoized.clear_memoized()
        with self._LocalCampaignSnapshotLock():
            if session.solarsystemid2 not in campaignSnapshot.coveredSolarsystemIDs:
                return
            self.LogWarn('insurgencyCampaignSvc.OnInsurgencyCampaignUpdatedForLocation', campaignSnapshot)
            self._localCampaignSnapshot = campaignSnapshot
            sm.ScatterEvent('OnInsurgencyCampaignUpdatedForLocation_Local', campaignSnapshot)
            self.ShowInsurgencyCampaignUpdatedForLocation(campaignSnapshot)

    def OnInsurgencyCampaignEndingForLocation(self, solarsystemID):
        self.GetCurrentCampaignSnapshots_Memoized.clear_memoized()
        with self._LocalCampaignSnapshotLock():
            if session.solarsystemid2 != solarsystemID:
                return
            self.LogWarn('insurgencyCampaignSvc.OnInsurgencyCampaignEndingForLocation')
            self._localCampaignSnapshot = None
            sm.ScatterEvent('OnInsurgencyCampaignEndingForLocation_Local')
            self.ShowInsurgencyCampaignEndingForLocation()

    def GetCurrentCampaignSnapshots(self):
        snapshots = sm.RemoteSvc('insurgencySolarsystem').GetAllVisibleCampaigns()
        return snapshots

    @Memoize(0.5)
    def GetCurrentCampaignSnapshots_Memoized(self):
        return self.GetCurrentCampaignSnapshots()

    def GetSolarsystemPirateFactionForCampaign(self, solarSystemID):
        for campaign in self.GetCurrentCampaignSnapshots_Memoized():
            if solarSystemID in campaign.coveredSolarsystemIDs:
                return campaign.pirateFactionID

    def IsInsurgencyOriginSolarsystemID(self, solarSystemID):
        for campaign in self.GetCurrentCampaignSnapshots_Memoized():
            if campaign.originSolarsystemID == solarSystemID:
                return True

        return False

    def GetActiveFobStructureIdAndSystemIdForFaction(self, factionID):
        for campaign in self.GetCurrentCampaignSnapshots_Memoized():
            if campaign.pirateFactionID == factionID and campaign.fsmState in (CAMPAIGN_STATE_FORECASTING, CAMPAIGN_STATE_ACTIVE, CAMPAIGN_STATE_PIRATE_WIN):
                return (campaign.structureID, campaign.originSolarsystemID)

        return (None, None)

    def OnInsurgencyStateChangedForFaction(self, campaignState, pirateFactionID, originSolarsystemID):
        if campaignState == CAMPAIGN_STATE_FORECASTING:
            sm.GetService('notificationSvc').MakeAndScatterNotification(notificationconst.notificationTypeInsurgencyStarting, data={'pirateFactionID': pirateFactionID,
             'originSolarsystemID': originSolarsystemID})
        elif campaignState == CAMPAIGN_STATE_ACTIVE:
            sm.GetService('notificationSvc').MakeAndScatterNotification(notificationconst.notificationTypeInsurgencyStarted, data={'pirateFactionID': pirateFactionID})
        elif campaignState == CAMPAIGN_STATE_PIRATE_WIN:
            sm.GetService('notificationSvc').MakeAndScatterNotification(notificationconst.notificationTypeInsurgencyEndedPiratesWin, data={'pirateFactionID': pirateFactionID})
        elif campaignState == CAMPAIGN_STATE_ANTIPIRATE_WIN:
            sm.GetService('notificationSvc').MakeAndScatterNotification(notificationconst.notificationTypeInsurgencyEndedAntiPiratesWin, data={'pirateFactionID': pirateFactionID})
        elif campaignState == CAMPAIGN_STATE_NO_WINNER:
            sm.GetService('notificationSvc').MakeAndScatterNotification(notificationconst.notificationTypeInsurgencyEndedNoOneWins, data={'pirateFactionID': pirateFactionID})

    def OnSystemFullyCorruptedForFaction(self, solarsystemID, pirateFactionID, piratePoints, pointsRequired):
        sm.GetService('notificationSvc').MakeAndScatterNotification(notificationconst.notificationTypeInsurgencyStage5Corruption, data={'solarSystemID': solarsystemID,
         'pirateFactionID': pirateFactionID,
         'numberOfCorruptedSystems': piratePoints,
         'totalNumberOfSystems': pointsRequired})

    def OnSystemFullySuppressedForFaction(self, solarsystemID, antipiratePoints, pointsRequired):
        sm.GetService('notificationSvc').MakeAndScatterNotification(notificationconst.notificationTypeInsurgencyStage5Suppression, data={'solarSystemID': solarsystemID,
         'numberOfSuppressedSystems': antipiratePoints,
         'totalNumberOfSystems': pointsRequired})

    def OnEnterSpace(self):
        uthread2.call_after_wallclocktime_delay(self.ShowActiveInsurgencyNotification, 4)

    def ShowActiveInsurgencyNotification(self):
        snapshot = self.GetLocalCampaignSnapshot()
        if snapshot is not None:
            if snapshot.fsmState == CAMPAIGN_STATE_ACTIVE:
                pirateFaction = factions.get_faction_name(snapshot.pirateFactionID)
                uicore.Message('CustomNotify', {'notify': GetByLabel('UI/PirateInsurgencies/Notifications/InsurgencyNotification', pirateFaction=pirateFaction)})

    def ShowInsurgencyCampaignStartedForLocation(self):
        uicore.Message('CustomNotify', {'notify': GetByLabel('UI/PirateInsurgencies/Notifications/InsurgencyStartingInLocation')})

    def ShowInsurgencyCampaignUpdatedForLocation(self, campaign):
        if campaign.fsmState == CAMPAIGN_STATE_ACTIVE:
            uicore.Message('CustomNotify', {'notify': GetByLabel('UI/PirateInsurgencies/Notifications/InsurgencyStartedInLocation')})

    def ShowInsurgencyCampaignEndingForLocation(self):
        uicore.Message('CustomNotify', {'notify': GetByLabel('UI/PirateInsurgencies/Notifications/InsurgencyEndedInLocation')})
