#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\warPermit.py
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class BaseWarPermitFormatter(BaseNotificationFormatter):
    subjectLabel = ''
    bodyLabel = ''

    def __init__(self, localizationImpl = None):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        notification.subject = GetByLabel(self.subjectLabel)
        notification.body = GetByLabel(self.bodyLabel)


class CorpBecameWarEligible(BaseWarPermitFormatter):
    subjectLabel = 'Notifications/subjCorpBecameWarEligible'
    bodyLabel = 'Notifications/bodyCorpBecameWarEligible'


class CorpNoLongerWarEligible(BaseWarPermitFormatter):
    subjectLabel = 'Notifications/subjCorpNoLongerWarEligible'
    bodyLabel = 'Notifications/bodyCorpNoLongerWarEligible'
