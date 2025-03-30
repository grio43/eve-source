#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\shutdownNotificationAdapter.py
import blue
import localization
import eve.common.script.util.notificationconst as notificationConst
from carbon.common.script.util.format import FmtDate
from eve.common.lib import appConst as const
from notifications.common.notification import Notification

class ShutdownNotificationAdapter(object):
    __notifyevents__ = ['OnClusterShutdownInitiated', 'OnClusterShutdownCancelled']

    def OnClusterShutdownInitiated(self, explanationLabel, when, duration):
        now = blue.os.GetWallclockTime()
        subtitle = localization.GetByLabel('UI/Shared/ShutdownNotificationSubtitleNoDelay')
        message = localization.GetByLabel(explanationLabel, intervalRemaining=localization.formatters.FormatTimeIntervalWritten(max(when - now, 500), showTo=localization.formatters.TIME_CATEGORY_MINUTE), shutdownTime=FmtDate(when, 'ns'))
        if duration:
            subtitle = localization.GetByLabel('UI/Shared/ShutdownNotificationSubtitleWithDelay', delay=localization.formatters.FormatTimeIntervalWritten(when - now, showTo=localization.formatters.TIME_CATEGORY_MINUTE))
            message += localization.GetByLabel('/EVE-Universe/ClusterBroadcast/DowntimeMessageSuffix', downtimeInterval=localization.formatters.FormatTimeIntervalWritten(duration * const.MIN, showTo=localization.formatters.TIME_CATEGORY_MINUTE))
        notification = Notification(notificationID=1, typeID=notificationConst.notificationTypeServerShutdown, senderID=None, receiverID=session.charid, processed=0, created=blue.os.GetWallclockTime(), data={'text': message})
        notification.subject = localization.GetByLabel('UI/Shared/ShutdownNotificationTitle')
        notification.subtext = subtitle
        sm.ScatterEvent('OnNewNotificationReceived', notification)

    def OnClusterShutdownCancelled(self, explanationLabel):
        notification = Notification(notificationID=1, typeID=notificationConst.notificationTypeServerShutdown, senderID=None, receiverID=session.charid, processed=0, created=blue.os.GetWallclockTime(), data={'text': localization.GetByLabel(explanationLabel)})
        notification.subject = localization.GetByLabel('UI/Shared/ShutdownNotificationTitle')
        notification.subtext = localization.GetByLabel('UI/Shared/ClusterShutdownDelayed')
        sm.ScatterEvent('OnNewNotificationReceived', notification)
