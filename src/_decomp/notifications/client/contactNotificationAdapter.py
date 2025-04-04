#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\contactNotificationAdapter.py
from notifications.common.notification import Notification
import blue
import localization

class ContactNotificationAdapter(object):
    __notifyevents__ = ['OnContactLoggedOn', 'OnContactLoggedOff', 'OnContactAddedToWatchlist']

    def OnContactLoggedOn(self, charID):
        labelText = self._GetLabelTextForChar(charID)
        loggedOnNotification = Notification.MakeContactLoggedOnNotification(contactCharID=charID, currentCharID=session.charid, created=blue.os.GetWallclockTime(), subject=localization.GetByLabel('UI/Common/UserIsOnline', charid=charID), labelText=labelText)
        sm.ScatterEvent('OnNewNotificationReceived', loggedOnNotification)

    def _GetLabelTextForChar(self, charID):
        labelMask = sm.GetService('addressbook').GetLabelMask(charID)
        labelText = sm.GetService('addressbook').GetLabelText(labelMask, 'contact')
        return labelText

    def OnContactLoggedOff(self, charID):
        labelText = self._GetLabelTextForChar(charID)
        loggedOffNotification = Notification.MakeContactLoggedOffNotification(contactCharID=charID, currentCharID=session.charid, created=blue.os.GetWallclockTime(), subject=localization.GetByLabel('UI/Common/UserIsOffline', charid=charID), labelText=labelText)
        sm.ScatterEvent('OnNewNotificationReceived', loggedOffNotification)

    def OnContactAddedToWatchlist(self, charID, isOnline):
        if isOnline:
            self.OnContactLoggedOn(charID)
