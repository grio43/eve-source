#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\essInventoryFull.py
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class EssInventoryFull(BaseNotificationFormatter):
    subjectLabel = ''
    bodyLabel = ''
    subtextLabel = ''

    def __init__(self, localizationImpl = None):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel, subtextLabel=self.subtextLabel)

    def Format(self, notification):
        notification.subject = GetByLabel('Notifications/subjEssInventoryFull')
        notification.body = GetByLabel('Notifications/bodyEssInventoryFull')
        notification.subtext = GetByLabel('Notifications/bodyEssInventoryFull')
