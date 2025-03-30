#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\essMainBankTheft.py
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class EssMainBankTheft(BaseNotificationFormatter):
    subjectLabel = ''
    bodyLabel = ''
    subtextLabel = ''

    def __init__(self, localizationImpl = None):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel, subtextLabel=self.subtextLabel)

    def Format(self, notification):
        data = notification.data
        notification.subject = GetByLabel('Notifications/subjEssMainBankTheft')
        notification.body = GetByLabel('Notifications/bodyEssMainBankTheft', solarSystemID=data['solarSystemID'])
        notification.subtext = GetByLabel('Notifications/bodyEssMainBankTheft', solarSystemID=data['solarSystemID'])
