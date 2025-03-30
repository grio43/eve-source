#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\shipGroupUnlocked.py
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class ShipGroupUnlocked(BaseNotificationFormatter):

    def Format(self, notification):
        if notification.data['unlockCount'] > 1:
            notification.subject = GetByLabel('Notifications/ShipTree/NewShipsUnlockedTitle')
            notification.subtext = GetByLabel('Notifications/ShipTree/NewShipsUnlockedDescription')
        else:
            notification.subject = GetByLabel('Notifications/ShipTree/NewShipUnlockedTitle')
            notification.subtext = GetByLabel('Notifications/ShipTree/NewShipUnlockedDescription')

    def MakeSampleData(variant = 0):
        return {'unlockCount': 1}
