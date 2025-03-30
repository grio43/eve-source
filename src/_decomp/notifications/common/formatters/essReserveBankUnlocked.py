#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\essReserveBankUnlocked.py
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class EssReserveBankUnlocked(BaseNotificationFormatter):
    subjectLabel = ''
    bodyLabel = ''
    subtextLabel = ''

    def __init__(self, localizationImpl = None):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel, subtextLabel=self.subtextLabel)

    def Format(self, notification):
        notification.subject = GetByLabel('Notifications/subjEssReserveBankUnlocked')
        notification.body = GetByLabel('Notifications/bodyEssReserveBankUnlocked')
        notification.subtext = GetByLabel('Notifications/bodyEssReserveBankUnlocked')
