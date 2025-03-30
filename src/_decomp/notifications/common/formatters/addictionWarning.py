#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\addictionWarning.py
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class AddictionWarningFormatter(BaseNotificationFormatter):

    def Format(self, notification):
        notification.subject = notification.data['subject']
        notification.subtext = notification.data['subtext']
        notification.Activate = None
