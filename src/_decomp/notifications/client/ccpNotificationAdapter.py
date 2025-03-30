#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\ccpNotificationAdapter.py
from notifications.common.notification import Notification
import blue

class CCPNotificationAdapter(object):
    __notifyevents__ = ['OnCCPNotification']

    def OnCCPNotification(self, title, subtitle, text, notificationTypeID, language = None, reference_id = None):
        if language is None or language == session.languageID:
            notification = Notification(notificationID=1, typeID=notificationTypeID, senderID=None, receiverID=session.charid, processed=0, created=blue.os.GetWallclockTime(), data={'text': text,
             'reference_id': reference_id})
            notification.subject = title
            notification.subtext = subtitle
            sm.ScatterEvent('OnNewNotificationReceived', notification)
