#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\officeleases.py
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class OfficeLeaseCanceledInsufficientStandings(BaseNotificationFormatter):
    subjectLabel = 'Notifications/subjOfficeLeaseCanceledInsufficientStandings'
    bodyLabel = 'Notifications/bodyOfficeLeaseCanceledInsufficientStandings'

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        data = notification.data
        notification.subject = GetByLabel(self.subjectLabel, **data)
        notification.body = GetByLabel(self.bodyLabel, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'standings_from_id': 98000001,
         'required_standing': 7.89,
         'current_standing': -1.23,
         'station_id': 60015147}
