#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\activitiesSvc.py
import eveexceptions
import localization
import uthread2
from carbon.common.script.sys.service import Service
from eve.client.script.ui.shared.activities.activity import ReleasedActivity
from eve.client.script.ui.shared.activities.newActivityNotify import CheckOpenNewActivitiesNotifyWindow
from eve.client.script.ui.shared.message_bus.newsCarouselMessenger import NewsCarouselMessenger
from fsdBuiltData.common.newActivitiesFSDLoader import NewActivitiesFSDLoader
from signals import Signal

class ActivitiesService(Service):
    __guid__ = 'svc.activities'
    __notifyevents__ = ['OnActivityRedDotUpdated']

    def Run(self, *args):
        super(ActivitiesService, self).Run(*args)
        self.Initialize()

    def Initialize(self):
        self._extensionsInitialized = False
        self.OnActivitySelected = Signal(signalName='OnActivitySelected')
        self.OnAfterExecution = Signal(signalName='OnAfterExecution')
        self.OnSetPopState = Signal(signalName='OnSetPopState')
        self.OnOpenActivityInfo = Signal(signalName='OnOpenActivityInfo')
        self.OnCloseActivityInfo = Signal(signalName='OnCloseActivityInfo')
        self._currId = None
        self._activities = None
        self._unseen = 0
        self._activitiesService = None
        self.message_bus = NewsCarouselMessenger(sm.GetService('publicGatewaySvc'))

    def _GetRemoteActivitiesService(self):
        if self._activitiesService is None:
            self._activitiesService = sm.RemoteSvc('activityMgr')
        return self._activitiesService

    def AfterLogout(self):
        self._extensionsInitialized = False

    def LoadActivityStatus(self):
        statuses = self._GetRemoteActivitiesService().GetActivityBadgeStatuses()
        self.activityStatuses = set(statuses)

    def CalcUnseenCountAndActivityStatus(self):
        self._unseen = 0
        for activity in self._activities:
            if activity.GetID() not in self.activityStatuses and not activity.IsCountdownVisible():
                self._unseen += 1
            else:
                activity.SetSeen()

    def LoadActivities(self):
        activites = [ ReleasedActivity(activityID, fsdData) for activityID, fsdData in self.GetFSDData().iteritems() ]
        self._activities = [ activity for activity in activites if activity.IsShown() ]
        if len(self._activities) == 0:
            return
        self._maxActivityID = max(self._activities, key=lambda x: x.GetID()).GetID()
        self._activities = sorted(self._activities, key=self._GetSortValue, reverse=True)
        self.dataDict = dict([ (element.GetID(), element) for element in self._activities ])
        self.firstID = None
        if self._activities is not None and len(self._activities) > 0:
            self.firstID = self._activities[0].GetID()
        self.LoadActivityStatus()
        self.CalcUnseenCountAndActivityStatus()
        self.OnActivityRedDotUpdated()

    def HasUnseenActivity(self):
        return self.GetUnseenActivityCount() > 0

    def GetUnseenActivityCount(self):
        return self._unseen

    def GetActivities(self):
        return self._activities

    def GetActivityCount(self):
        return self._activities and len(self._activities) or 0

    def _GetSortValue(self, activity):
        return activity.GetID()

    def GetFSDData(self):
        return NewActivitiesFSDLoader().GetData()

    def GetCurrentActivityInfo(self):
        activity = self.dataDict.get(self._currId)
        return activity.GetInfo()

    def OnBannerClicked(self):
        info = self.GetCurrentActivityInfo()
        if info:
            self.OnOpenActivityInfo(info)
        else:
            self.StartAction()

    def OnActivityInfoCloseClicked(self):
        self.OnCloseActivityInfo()

    def ExecuteAction(self):
        activity = self.dataDict.get(self._currId)
        activity.ExecuteCallToAction()
        self.OnAfterExecution(False)

    def StartAction(self):
        uthread2.start_tasklet(self.ExecuteAction)

    def IsCurrentActivityExecutable(self):
        return True

    def CheckIfLoginOpenWindowEnabled(self):
        if not localization.util.AmOnChineseServer():
            return
        if not session.charid:
            return
        if self._activities is None or len(self._activities) == 0:
            return
        if self.GetStatus() == 0:
            self.ToggleActivities()

    def ToggleActivities(self):
        CheckOpenNewActivitiesNotifyWindow()

    def GetCurrId(self):
        return self._currId

    def OnActivitySeen(self, activity):
        activityID = activity.GetID()
        if activityID in self.activityStatuses:
            return
        ret = self._GetRemoteActivitiesService().ActivitySeen(activityID)
        if not ret:
            return
        self.activityStatuses.add(activityID)
        self.CalcUnseenCountAndActivityStatus()
        self.OnActivityRedDotUpdated()

    def SelectActivity(self, activityID = None):
        isFirst = False
        if activityID is None:
            if self.firstID is None:
                return
            isFirst = True
            activityID = self.firstID
        self._LogDisplayed(activityID)
        self._currId = activityID
        activity = self.dataDict.get(self._currId)
        if not isFirst:
            self.OnActivitySeen(activity)
        self.OnActivitySelected(activity)

    def OnActivityRedDotUpdated(self):
        sm.ScatterEvent('OnActivityUpdated')

    def GetStatus(self):
        return self._GetRemoteActivitiesService().GetActivitiesPopState()

    def OnStatusChanged(self, state):
        self._LogAutoPopupToggled(state)
        ret = self._GetRemoteActivitiesService().SetActivitiesPopState(state)
        if not ret:
            self.OnSetPopState(1 if state == 0 else 0)

    @eveexceptions.EatsExceptions('protoClientLogs')
    def _LogAutoPopupToggled(self, checked):
        self.message_bus.auto_popup_toggled(checked)

    @eveexceptions.EatsExceptions('protoClientLogs')
    def _LogDisplayed(self, ad_id):
        self.message_bus.displayed(ad_id)

    def Reset(self):
        self._activities = None
        self.dataDict = None
        self.firstID = None
        self._currId = None
        self._unseen = 0
