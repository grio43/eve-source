#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\contractRegionChangedToPochven.py
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
import localization

class ContractRegionChangedToPochvenFormatter(BaseNotificationFormatter):
    SUBJECT_LABEL = 'Notifications/subjContractRegionChangedToPochven'
    BODY_LABEL = 'Notifications/bodyContractRegionChangedToPochven'

    def __init__(self):
        super(ContractRegionChangedToPochvenFormatter, self).__init__(subjectLabel=self.SUBJECT_LABEL, bodyLabel=self.BODY_LABEL)

    def Format(self, notification):
        notification.subject = localization.GetByLabel(self.subjectLabel)
        notification.body = localization.GetByLabel(self.bodyLabel)
