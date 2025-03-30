#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\notificationUI.py
import itertoolsext
from carbon.common.script.sys.service import CoreService
from notifications.client.bountyNotificationAdapter import BountyNotificationAdapter
from notifications.client.ccpNotificationAdapter import CCPNotificationAdapter
from notifications.client.essNotificationAdapter import ESSNotificationAdapter
from notifications.client.contactNotificationAdapter import ContactNotificationAdapter
from notifications.client.generator.notificationGenerator import NotificationGenerator
from notifications.client.notificationCenter import NotificationCenter
from notifications.client.notificationSettings.notificationSettingHandler import NotificationSettingHandler
from notifications.client.oreMinedNotificationAdapter import OreMinedNotificationAdapter
from notifications.client.rwPirateKilledNotificationAdapter import PirateKilledNotificationAdapter
from notifications.client.shutdownNotificationAdapter import ShutdownNotificationAdapter

class NotificationUIService(CoreService):
    __guid__ = 'svc.notificationUIService'
    __notifyevents__ = ['OnNewNotificationReceived',
     'OnSetDevice',
     'OnLocalNotificationSettingChanged',
     'OnNotificationReadOutside']
    __startupdependencies__ = ['settings',
     'mailSvc',
     'notificationSvc',
     'logger']

    def __init__(self):
        super(NotificationUIService, self).__init__()
        self.forceAlwaysEnabled = False

    def Run(self, memstream = None):
        self.notificationCenter = None
        self.notificationCache = None
        self.pendingNotificationCache = []
        self.cacheFillThread = None
        self.unreadCounter = 0
        self.notificationSettings = NotificationSettingHandler()
        self.notificationGenerator = NotificationGenerator()
        self.isEnabled = self.ShouldEnableNotifications()
        self.shouldShowOnEnable = False
        self.__developerMode = False
        self.adapterRegistry = [ContactNotificationAdapter(),
         CCPNotificationAdapter(),
         ESSNotificationAdapter(),
         ShutdownNotificationAdapter(),
         OreMinedNotificationAdapter(sm.GetService('logger')),
         BountyNotificationAdapter(sm.GetService('logger')),
         PirateKilledNotificationAdapter(sm.GetService('logger'))]
        for adapter in self.adapterRegistry:
            sm.RegisterNotify(adapter)

        self.lastSeenMessageTime = self.notificationSettings.GetLastSeenTime()
        self.lastHistoryTimeCleanTime = self.notificationSettings.GetLastHistoryTimeCleanTime()
        self.lastSeenNotificationId = self.notificationSettings.GetLastSeenNotificationId()
        self.lastClearedNotificationId = self.notificationSettings.GetLastClearedNotificationId()

    def SetNotificationsAlwaysEnabled(self, alwaysEnabled):
        self.forceAlwaysEnabled = alwaysEnabled

    def AreNotificationsAlwaysEnabled(self):
        return self.forceAlwaysEnabled

    def ShouldEnableNotifications(self):
        return self.notificationSettings.GetNotificationWidgetEnabled() or self.AreNotificationsAlwaysEnabled()

    def OnLocalNotificationSettingChanged(self):
        self.UpdateEnabledStatus()

    def Stop(self, memStream = None):
        CoreService.Stop(self, memStream)
        for adapter in self.adapterRegistry:
            sm.UnregisterNotify(adapter)

    def PlaySound(self, eventName):
        if self.notificationSettings.GetNotificationSoundEnabled():
            sm.GetService('audio').SendUIEvent(eventName)

    def ToggleDeveloperMode(self):
        print 'TogglingDeveloperMode'
        self.__developerMode = not self.__developerMode
        print 'DeveloperMode is ' + str(self.__developerMode)

    def IsDeveloperMode(self):
        return self.__developerMode

    def IsEnabled(self):
        return self.isEnabled

    def IsAvailable(self):
        return self.notificationCenter is not None

    def OnNewNotificationReceived(self, notification):
        if self.isEnabled:
            self._InsertNotification(notification)
            self._DisplayNotificationIfPossible(notification)

    def SpawnFakeNotifications(self):
        self.notificationGenerator.Start()

    def ResetUnreadCounter(self):
        if self.notificationCache and len(self.notificationCache) > 0:
            self._SetLastReadTime(self.notificationCache[0].created)
        self.unreadCounter = 0
        self._UpdateCounter()

    def _UpdateCounter(self):
        if self.notificationCenter:
            self.notificationCenter.SetBadgeValue(self.unreadCounter)
            if self.unreadCounter == 0:
                self.notificationCenter.hideBadge()
            else:
                self.notificationCenter.showBadge()

    def _IncrementCounter(self):
        self.unreadCounter = self.unreadCounter + 1
        self._UpdateCounter()

    def _SetLastReadTime(self, lastReadTimeStamp):
        self.lastSeenMessageTime = lastReadTimeStamp
        self.notificationSettings.SetLastSeenTime(self.lastSeenMessageTime)

    def _ShouldIncrementCounterForNotification(self, notification):
        notificationSetting = self.notificationSettings.LoadSettings()
        specificSetting = notificationSetting.get(notification.typeID)
        if specificSetting and specificSetting.showAtAll:
            return True
        return False

    def _IncrementCounterIfIShould(self, notification):
        if self._ShouldIncrementCounterForNotification(notification):
            self._IncrementCounter()

    def _InsertNotification(self, notification):
        self._IncrementCounterIfIShould(notification)
        if self.notificationCache is None:
            self.pendingNotificationCache.append(notification)
        else:
            self.notificationCache.insert(0, notification)

    def _DisplayNotificationIfPossible(self, notification):
        if self.notificationCenter:
            self.notificationCenter.DisplaySingleNotification(notification)

    def ClearHistory(self):
        self.lastHistoryTimeCleanTime = self.lastSeenMessageTime
        self.lastClearedNotificationId = self.lastSeenNotificationId
        self.notificationSettings.SetLastHistoryCleanTime(self.lastHistoryTimeCleanTime)
        self.notificationSettings.SetLastClearedNotificationId(self.lastClearedNotificationId)
        self.ClearCache()

    def UnClearHistory(self):
        self.lastHistoryTimeCleanTime = 0
        self.lastClearedNotificationId = 0
        self.lastSeenNotificationId = 0
        self.notificationSettings.SetLastHistoryCleanTime(self.lastHistoryTimeCleanTime)
        self.notificationSettings.SetLastClearedNotificationId(self.lastClearedNotificationId)
        self.SaveLastSeenNotificationId()
        self.ClearCache()

    def SaveLastSeenNotificationId(self):
        self.notificationSettings.SetLastSeenNotificationId(self.lastSeenNotificationId)

    def OnSetDevice(self):
        pass

    def _IsCacheInitialized(self):
        return self.notificationCache is not None

    def _CheckAndFillCache(self):
        if self.notificationCache is None:
            self.notificationCache = self._NotificationProvider(sortThem=False)
            tempNotifications = self.pendingNotificationCache
            for pendingNotification in tempNotifications:
                for notification in self.notificationCache:
                    if pendingNotification.notificationID == notification.notificationID and pendingNotification in self.pendingNotificationCache:
                        self.pendingNotificationCache.remove(pendingNotification)

            self.notificationCache.extend(self.pendingNotificationCache)
            self.pendingNotificationCache = []
            self._SortNotifications(self.notificationCache)
            counter = 0
            for notification in self.notificationCache:
                if notification.created > self.lastSeenMessageTime and self._ShouldIncrementCounterForNotification(notification):
                    counter += 1
                self.lastSeenNotificationId = max(notification.notificationID, self.lastSeenNotificationId)

            self.SaveLastSeenNotificationId()
            self.unreadCounter = counter
            self._UpdateCounter()
            self._NotifyInitialized()

    def OnNotificationReadOutside(self, notificationID):
        if not self.notificationCache:
            return
        n = itertoolsext.first_or_default(self.notificationCache, lambda x: x.notificationID == notificationID, None)
        if n:
            n.processed = True

    def _NotifyInitialized(self):
        if self.notificationCenter:
            self.notificationCenter.SetCacheIsInitialized(True)

    def _NotifyUnInitialized(self):
        if self.notificationCenter:
            self.notificationCenter.SetCacheIsInitialized(False)

    def UpdateEnabledStatus(self):
        if self.ShouldEnableNotifications():
            self.SetEnabled(True)
        else:
            self.SetEnabled(False)

    def SetEnabled(self, value):
        if value is self.isEnabled:
            return
        if self.shouldShowOnEnable and value is True:
            self.isEnabled = True
            self.Show()
        else:
            self.TearDown()
            self.isEnabled = value

    def _StartCheckAndFillCacheThread(self):
        import uthread
        uthread.new(self._CheckAndFillCache)

    def Show(self):
        if session.charid is None:
            return
        self.shouldShowOnEnable = True
        if self.isEnabled:
            self._ConstructNotificationCenter()
            sm.ScatterEvent('OnNotificationUiReady')
            self._StartCheckAndFillCacheThread()
        else:
            self.UpdateEnabledStatus()

    def ToggleEnabledFlag(self):
        if self.isEnabled and not self.AreNotificationsAlwaysEnabled():
            self.Hide()
            self.isEnabled = False
        else:
            self.isEnabled = True
            self.Show()

    def Hide(self):
        self.shouldShowOnEnable = False
        self.TearDown()

    def TearDown(self):
        if self.isEnabled:
            self._TearDownNotificationCenter()
        self.ClearCache(refillCache=False)

    def _TearDownNotificationCenter(self):
        if self.notificationCenter:
            self.notificationCenter.deconstruct()
            self.notificationCenter = None

    def _OnNotificationCenterReconstructed(self):
        self._UpdateCounter()

    def _ConstructNotificationCenter(self):
        if self.isEnabled:
            self._TearDownNotificationCenter()
            self.notificationCenter = NotificationCenter(onReconstructCallBack=self._OnNotificationCenterReconstructed, developerMode=self.IsDeveloperMode(), audioCallback=self.PlaySound)
            self.notificationCenter.Construct(notificationProviderFunction=self._PersonalCachedProvider)
            self.notificationCenter.SetCacheIsInitialized(self._IsCacheInitialized())
            self._UpdateCounter()

    def _PersonalCachedProvider(self):
        if self.notificationCache is None:
            self._CheckAndFillCache()
        else:
            self.ResetUnreadCounter()
        return self.notificationCache

    def _SortNotifications(self, notificationList):
        notificationList.sort(key=lambda notification: notification.created, reverse=True)

    def _NotificationProvider(self, sortThem = True):
        from notifications.client.development.skillHistoryProvider import SkillHistoryProvider
        skillNotifications = SkillHistoryProvider(onlyShowAfterDate=self.lastHistoryTimeCleanTime).provide()
        restOfNotifications = sm.GetService('notificationSvc').GetAllFormattedNotifications(fromID=self.lastClearedNotificationId)
        sortedList = skillNotifications + restOfNotifications
        if sortThem:
            self._SortNotifications(sortedList)
        return sortedList

    def ClearCache(self, refillCache = True):
        self.notificationCache = None
        sm.GetService('notificationSvc').ClearAllNotificationsCache()
        self._NotifyUnInitialized()
        if refillCache:
            self._CheckAndFillCache()
