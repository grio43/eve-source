#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\essLinkDisconnected.py
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class EssLinkDisconnected(BaseNotificationFormatter):
    subjectLabel = ''
    bodyLabel = ''
    subtextLabel = ''

    def __init__(self, localizationImpl = None):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel, subtextLabel=self.subtextLabel)

    def Format(self, notification):
        data = notification.data
        characterID = data['characterID']
        if characterID == session.charid:
            notification.body = GetByLabel('Notifications/bodyEssLinkDisconnected', solarSystemID=data['solarSystemID'])
            notification.subtext = GetByLabel('Notifications/bodyEssLinkDisconnected', solarSystemID=data['solarSystemID'])
        else:
            notification.body = GetByLabel('Notifications/bodyEssLinkDisconnectedSomeoneElse', solarSystemID=data['solarSystemID'])
            notification.subtext = GetByLabel('Notifications/bodyEssLinkDisconnectedSomeoneElse', solarSystemID=data['solarSystemID'])
        notification.subject = GetByLabel('Notifications/subjEssLinkDisconnected')
