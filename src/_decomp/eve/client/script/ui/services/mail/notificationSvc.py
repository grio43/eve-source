#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\mail\notificationSvc.py
import copy
import sys
import yaml
import blue
import carbon.common.script.util.format as fmtUtils
import carbonui.const as uiconst
import eve.common.lib.appConst as const
import eve.common.script.util.notificationUtil as notificationUtil
import localization
import log
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING
from eve.client.script.ui.shared.neocom.evemail import MailReadingWnd
from eve.common.script.util.notificationconst import GetTypeGroup, IsTypeInCommunications, depricatedNotifications
from eveexceptions import UserError
from notifications.common.formatting.notificationFormatMapping import GetFormatterForType
from notifications.common.notification import Notification

class notificationSvc(Service):
    __guid__ = 'svc.notificationSvc'
    __displayname__ = 'Notification service'
    __exportedcalls__ = {}
    __notifyevents__ = ['OnNotificationReceived',
     'OnNotificationDeleted',
     'OnNotificationUndeleted',
     'OnSessionReset']
    __startupdependencies__ = ['settings']

    def Run(self, ms = None):
        self.state = SERVICE_RUNNING
        self.notificationMgr = sm.RemoteSvc('notificationMgr')
        self.notifications = {}
        self.unreadCount = {}
        self.unreadNotifications = None
        self.allNotifications = None
        self.blinkTab = False
        self.blinkNeocom = False
        self.delayedNotificationsByID = {const.notificationTypeCloneActivationMsg: set(),
         const.notificationTypeCloneActivationMsg2: set()}
        self.isEnabled = True

    def EnableNotifications(self):
        self.isEnabled = True

    def DisableNotifications(self):
        self.isEnabled = False

    def ClearCache(self):
        self.notifications = {}
        self.unreadCount = {}
        self.unreadNotifications = None

    def OnSessionReset(self):
        self.ClearCache()

    def GetNotificationsByGroupID(self, groupID):
        if groupID not in self.notifications:
            self.notifications[groupID] = []
            cache = self.notifications[groupID]
            newNotifications = self.notificationMgr.GetByGroupID(groupID)
            newSenders = []
            for newNotification in newNotifications:
                notificationObj = Notification.FromDTO(newNotification)
                if IsTypeInCommunications(notificationObj.typeID):
                    cache.append(notificationObj)
                    newSenders.append(newNotification.senderID)

            sm.GetService('mailSvc').PrimeOwners(newSenders)
        return self.notifications[groupID]

    def MakeAndScatterNotification(self, type, data):
        sm.ScatterEvent('OnNotificationReceived', -1, type, session.charid, blue.os.GetWallclockTime(), data=data)

    def GetAllNotifications(self, fromID = 0):
        if self.allNotifications is None:
            allServerNotifications = self._GetAllNotifications(fromID)
            newSenders = set()
            allClientNotifications = []
            for notification in allServerNotifications:
                allClientNotifications.append(Notification.FromDTO(notification))
                newSenders.add(notification.senderID)

            sm.GetService('mailSvc').PrimeOwners(newSenders)
            self.allNotifications = allClientNotifications
        return self.allNotifications

    def _GetAllNotifications(self, fromID):
        notifications = self.notificationMgr.GetAllNotifications(fromID=fromID)
        return [ notification for notification in notifications if notification.typeID not in depricatedNotifications ]

    def ClearAllNotificationsCache(self):
        self.allNotifications = None

    def GetAllFormattedNotifications(self, fromID = 0):
        return self.FormatNotifications(self.GetAllNotifications(fromID=fromID))

    def GetUnreadNotifications(self):
        self.LogInfo('Getting unread notifications')
        if self.unreadNotifications is None:
            unreadNotifications = []
            newNotifications = self.notificationMgr.GetUnprocessed()
            newSenders = []
            for newNotification in newNotifications:
                notificationObj = Notification.FromDTO(newNotification)
                if IsTypeInCommunications(notificationObj.typeID):
                    unreadNotifications.append(Notification.FromDTO(newNotification))
                    newSenders.append(newNotification.senderID)
                    groupID = GetTypeGroup(newNotification.typeID)
                    if groupID in self.unreadCount:
                        self.unreadCount[groupID] += 1
                    else:
                        self.unreadCount[groupID] = 1

            self.unreadNotifications = unreadNotifications
            sm.GetService('mailSvc').PrimeOwners(newSenders)
        return self.unreadNotifications

    def GetUnreadCountDictionary(self):
        if self.unreadNotifications is None:
            self.GetUnreadNotifications()
        return self.unreadCount

    def GetAllUnreadCount(self):
        unreadCounts = self.GetUnreadCountDictionary().copy()
        unreadGroupCounter = 0
        for counter in unreadCounts.itervalues():
            unreadGroupCounter += counter

        unreadCounts[const.notificationGroupUnread] = unreadGroupCounter
        return unreadCounts

    def GetFormattedNotifications(self, groupID):
        notifications = self.GetNotificationsByGroupID(groupID)
        ret = self.FormatNotifications(notifications)
        return ret

    def GetFormattedUnreadNotifications(self):
        notifications = self.GetUnreadNotifications()
        ret = self.FormatNotifications(notifications)
        return ret

    def TryUnYamlNotificationData(self, notification):
        try:
            if isinstance(notification.data, basestring):
                notification.data = yaml.load(notification.data, Loader=yaml.CSafeLoader)
        except Exception as e:
            self.LogWarn('Exception while un-yamling notification data', repr(notification.data), e)
            sys.exc_clear()

    def UnYamlNotificationsData(self, notifications):
        for notification in notifications:
            self.TryUnYamlNotificationData(notification)

    def FormatNotifications(self, notifications):
        self.UnYamlNotificationsData(notifications)
        self.PrimeNotificationLinkInfo(notifications)
        ret = []
        for notification in notifications:
            notificationCopy = notification.copy()
            newFormatter = GetFormatterForType(notification.typeID)
            if newFormatter:
                try:
                    newFormatter.Format(notificationCopy)
                except Exception as e:
                    log.LogException('Error processing notification of type %s, error=%s' % (notification.typeID, e))
                    notificationCopy.subject = localization.GetByLabel('Notifications/subjBadNotificationMessage')
                    notificationCopy.body = localization.GetByLabel('Notifications/bodyBadNotificationMessage', id=notification.notificationID)

            else:
                subject, body = notificationUtil.Format(notification)
                notificationCopy.subject = subject
                notificationCopy.body = body
            if not notificationCopy.subject and not notificationCopy.body:
                log.LogWarn('Processed notification has empty subject and body (notification type %s)' % notification.typeID)
            ret.append(notificationCopy)

        return ret

    def PrimeNotificationLinkInfo(self, notifications):
        locationKeys = ('solarsystemid', 'stationid', 'clonestationid', 'corpstationid', 'moonid', 'locationid', 'structureid')
        ownerKeys = ('characterid', 'charid', 'corporationid', 'corpid', 'allianceid', 'deptorid', 'creditorid', 'aggressorid', 'aggressorcorpid', 'aggressorallianceid', 'factionid', 'podkillerid', 'againstid', 'declaredbyid', 'ownerid', 'oldownerid', 'newownerid', 'locationownerid', 'victimid')
        locationIDs = set()
        ownerIDs = set()
        for notification in notifications:
            data = notification.data
            if data is not None and isinstance(data, dict):
                for key, value in data.iteritems():
                    if isinstance(value, (int, long)):
                        if key.lower() in locationKeys:
                            locationIDs.add(value)
                        elif key.lower() in ownerKeys:
                            ownerIDs.add(value)

        cfg.evelocations.Prime(locationIDs)
        cfg.eveowners.Prime(ownerIDs)

    def MarkAllReadInGroup(self, groupID):
        notifications = self.GetNotificationsByGroupID(groupID)
        toMarkRead = []
        for read in notifications:
            for unread in self.unreadNotifications:
                if unread.notificationID == read.notificationID:
                    toMarkRead.append(read.notificationID)

        if len(toMarkRead) < 1:
            return
        if eve.Message('EvemailNotificationsMarkGroupRead', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.notificationMgr.MarkGroupAsProcessed(groupID)
            self.UpdateCacheAfterMarkingRead(toMarkRead)
            sm.ScatterEvent('OnNotificationsRefresh')

    def MarkAllRead(self):
        if not self.unreadNotifications:
            return
        self.notificationMgr.MarkAllAsProcessed()
        toMarkRead = []
        for notification in self.unreadNotifications:
            toMarkRead.append(notification.notificationID)

        self.UpdateCacheAfterMarkingRead(toMarkRead)
        sm.ScatterEvent('OnNotificationsRefresh')

    def MarkAsRead(self, notificationIDs):
        if self.unreadNotifications is None:
            return
        notificationIDsToMarkAsRead = set()
        for notificationID in notificationIDs:
            for notification in self.unreadNotifications:
                if notificationID == notification.notificationID:
                    notificationIDsToMarkAsRead.add(notificationID)

        numToMark = len(notificationIDsToMarkAsRead)
        if numToMark < 1:
            return
        if numToMark > const.notificationsMaxUpdated:
            txt = localization.GetByLabel('UI/Mail/Notifications/TooManySelected', num=numToMark, max=const.notificationsMaxUpdated)
            raise UserError('CustomInfo', {'info': txt})
        notificationsList = list(notificationIDsToMarkAsRead)
        self.notificationMgr.MarkAsProcessed(notificationsList)
        self.UpdateCacheAfterMarkingRead(notificationsList)

    def UpdateCacheAfterMarkingRead(self, notificationIDs):
        for readID in notificationIDs:
            wasUnread = False
            typeID = None
            for unread in self.unreadNotifications:
                if unread.notificationID == readID:
                    typeID = unread.typeID
                    self.unreadNotifications.remove(unread)
                    wasUnread = True
                    break

            if not wasUnread:
                continue
            groupID = GetTypeGroup(typeID)
            if groupID in self.notifications:
                for grouped in self.notifications[groupID]:
                    if grouped.notificationID == readID:
                        grouped.processed = True
                        break

            if groupID in self.unreadCount:
                self.unreadCount[groupID] = self.unreadCount[groupID] - 1

    def DeleteAllFromGroup(self, groupID):
        notifications = self.GetNotificationsByGroupID(groupID)
        if len(notifications) < 1:
            return
        self.notificationMgr.DeleteGroupNotifications(groupID)
        deleted = []
        for notification in notifications:
            deleted.append(notification.notificationID)

        self.UpdateCacheAfterDeleting(deleted)
        sm.ScatterEvent('OnNotificationsRefresh')

    def DeleteAll(self):
        self.notificationMgr.DeleteAllNotifications()
        self.unreadNotifications = []
        self.allNotifications = []
        self.unreadCount = {}
        if self.notifications is not None:
            for groupID in self.notifications.iterkeys():
                self.notifications[groupID] = []

        sm.ScatterEvent('OnNotificationsRefresh')

    def DeleteNotifications(self, notificationIDs):
        numToDelete = len(notificationIDs)
        if numToDelete < 1:
            return
        if numToDelete > const.notificationsMaxUpdated:
            txt = localization.GetByLabel('UI/Mail/Notifications/TooManySelected', num=numToDelete, max=const.notificationsMaxUpdated)
            raise UserError('CustomInfo', {'info': txt})
        self.notificationMgr.DeleteNotifications(notificationIDs)
        self.UpdateCacheAfterDeleting(notificationIDs)

    def UpdateCacheAfterDeleting(self, notificationIDs):
        toclear = copy.copy(notificationIDs)
        if self.unreadNotifications is not None:
            for deletedID in notificationIDs:
                for unread in self.unreadNotifications:
                    if unread.notificationID == deletedID:
                        groupID = GetTypeGroup(unread.typeID)
                        self.unreadNotifications.remove(unread)
                        if groupID in self.unreadCount:
                            self.unreadCount[groupID] = self.unreadCount[groupID] - 1
                        if groupID in self.notifications:
                            for grouped in self.notifications[groupID]:
                                if grouped.notificationID == deletedID:
                                    self.notifications[groupID].remove(grouped)
                                    break

                        toclear.remove(deletedID)
                        break

        if len(toclear) > 0:
            for groupID in self.notifications:
                for deletedID in copy.copy(toclear):
                    for grouped in self.notifications[groupID]:
                        if grouped.notificationID == deletedID:
                            self.notifications[groupID].remove(grouped)
                            toclear.remove(deletedID)
                            break

    def OnNotificationDeleted(self, notificationIDs):
        toclear = copy.copy(notificationIDs)
        if self.unreadNotifications is not None:
            for deletedID in notificationIDs:
                for unread in self.unreadNotifications:
                    if unread.notificationID == deletedID:
                        groupID = GetTypeGroup(self.unreadNotifications[deletedID].typeID)
                        self.unreadNotifications.remove(unread)
                        if groupID in self.unreadCount:
                            self.unreadCount[groupID] = self.unreadCount[groupID] - 1
                        if groupID in self.notifications:
                            for grouped in self.notifications[groupID]:
                                if grouped.notificationID == deletedID:
                                    self.notifications[groupID].remove(grouped)
                                    break

                        toclear.remove(deletedID)
                        break

        if len(toclear) > 0:
            for groupID in self.notifications:
                for deletedID in copy.copy(toclear):
                    for grouped in self.notifications[groupID]:
                        if grouped.notificationID == deletedID:
                            self.notifications[groupID].remove(grouped)
                            toclear.remove(deletedID)
                            break

        sm.ScatterEvent('OnNotificationsRefresh')

    def OnNotificationUndeleted(self, notificationIDs):
        self.ClearCache()
        sm.ScatterEvent('OnNotificationsRefresh')

    def InsertNotification(self, groupID, notification):
        if groupID in self.notifications:
            self.notifications[groupID].insert(0, notification)

    def AddToUnread(self, groupID, notification):
        if self.unreadNotifications is not None:
            if groupID in self.unreadCount:
                self.unreadCount[groupID] += 1
            else:
                self.unreadCount[groupID] = 1
            self.unreadNotifications.insert(0, notification)

    def OnNotificationReceived(self, notificationID, typeID, senderID, created, data = {}):
        if not self.isEnabled:
            return
        notification = Notification(notificationID=notificationID, typeID=typeID, senderID=senderID, receiverID=session.charid, processed=False, created=created, data=data)
        groupID = GetTypeGroup(typeID)
        if groupID is not None and IsTypeInCommunications(typeID):
            self.InsertNotification(groupID, notification)
            self.AddToUnread(groupID, notification)
        if typeID in self.delayedNotificationsByID:
            self.delayedNotificationsByID[typeID].add(notification)
        else:
            self.ProcessNotification(notification)

    def ProcessNotification(self, notification):
        n = self.FormatNotifications([notification])
        first = n[0]
        self.ScatterNotificationEvent(first)

    def ScatterNotificationEvent(self, notification):
        sm.ScatterEvent('OnNewNotificationReceived', notification)

    def ProcessDelayedNotifications(self, notificationTypeID):
        delayedNotifications = self.delayedNotificationsByID.get(notificationTypeID, None)
        if delayedNotifications is None:
            return
        for eachNotification in delayedNotifications:
            self.ProcessNotification(eachNotification)

        self.delayedNotificationsByID[notificationTypeID] = set()

    def GetReadingText(self, senderID, subject, created, message):
        if senderID == -1:
            senderID = const.ownerSystem
        sender = cfg.eveowners.Get(senderID)
        senderTypeID = sender.typeID
        if senderTypeID is not None and senderTypeID > 0:
            senderText = '<a href="showinfo:%(senderType)s//%(senderID)s">%(senderName)s</a>' % {'senderType': senderTypeID,
             'senderID': senderID,
             'senderName': sender.name}
        else:
            senderText = sender.name
        date = fmtUtils.FmtDate(created, 'ls')
        newmsgText = localization.GetByLabel('UI/Mail/NotificationText', subject=subject, sender=senderText, date=date, body=message)
        return newmsgText

    def OpenNotificationReadingWnd(self, info, *args):
        wndName = 'mail_readingWnd_%s' % info.notificationID
        wnd = MailReadingWnd.Open(windowID=wndName, mail=None, msgID=info.notificationID, txt='', toolbar=False, trashed=False, type=const.mailTypeNotifications)
        if not info.processed:
            self.MarkAsRead([info.notificationID])
            sm.ScatterEvent('OnNotificationReadOutside', info.notificationID)
        if wnd is not None:
            wnd.Maximize()
            blue.pyos.synchro.SleepWallclock(1)
            txt = sm.GetService('notificationSvc').GetReadingText(info.senderID, info.subject, info.created, info.body)
            wnd.SetText(txt)
