#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\contractAccepted.py
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
import localization

class ContractAcceptedFormatter(BaseNotificationFormatter):

    def __init__(self):
        pass

    def Format(self, notification):
        notification.subject = localization.GetByLabel('UI/Contracts/ContractsWindow/Contracts')
        notification.subtext = localization.GetByLabel('Notifications/NotificationNames/ContractAccepted')
