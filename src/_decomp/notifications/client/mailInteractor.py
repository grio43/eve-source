#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\mailInteractor.py
import eve.common.script.util.notificationconst as notificationConst
import blue
from eve.client.script.ui.shared.neocom.evemail import MailWindow

class MailInteractor(object):

    def GetMailWindow(self):
        return MailWindow.Open()

    def SelectGroupId(self, groupID):
        notificationForm = self.GetNotificationForm()
        notificationForm.SelectGroupById(groupID)

    def SleepIfTrue(self, sleep):
        if sleep:
            blue.pyos.synchro.SleepWallclock(50)

    def GetNotificationForm(self, doSleep = True):
        wnd = self.GetMailWindow()
        self.SleepIfTrue(doSleep)
        wnd.SelectNotificationTab()
        self.SleepIfTrue(doSleep)
        return wnd.sr.notifications

    def SelectGroupForTypeID(self, notificationTypeID):
        groupID = self.FindGroupForNotificationID(notificationTypeID)
        if groupID:
            self.SelectGroupId(groupID)

    def SelectByNotificationID(self, notificationID, notificationTypeID):
        self.SelectGroupForTypeID(notificationTypeID)
        notificationForm = self.GetNotificationForm(doSleep=False)
        notificationForm.SelectNodeByNotificationID(notificationID)

    def FindGroupForNotificationID(self, notificationTypeID):
        for groupID, notificationList in notificationConst.groupTypes.iteritems():
            for notificationid in notificationList:
                if notificationTypeID == notificationid:
                    return groupID
