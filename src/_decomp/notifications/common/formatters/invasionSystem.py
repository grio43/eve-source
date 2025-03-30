#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\invasionSystem.py
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class InvasionSystemLoginNotification(BaseNotificationFormatter):
    subjectLabel = 'Notifications/subjInvasionSystemLogin'
    bodyLabel = 'Notifications/bodyInvasionSystemLogin'

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        notification.subject = GetByLabel(self.subjectLabel)
        notification.body = GetByLabel(self.bodyLabel)


class InvasionSystemStartNotification(BaseNotificationFormatter):
    subjectLabel = 'Notifications/subjInvasionSystemStart'
    bodyLabel = 'Notifications/bodyInvasionSystemStart'

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        notification.subject = GetByLabel(self.subjectLabel)
        notification.body = GetByLabel(self.bodyLabel)
