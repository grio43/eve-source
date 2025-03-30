#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\boosterConsumedFormatter.py
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class BoosterConsumedFormatter(BaseNotificationFormatter):

    def Format(self, notification):
        notification.subject = GetByLabel('Notifications/NotificationNames/BoosterConsumed')
        typeID = notification.data['typeID']
        slotNum = getattr(sm.GetService('godma').GetType(typeID), 'boosterness', None)
        notification.subtext = GetByLabel('Notifications/BoosterConsumed', typeID=typeID, slotNum=slotNum)
