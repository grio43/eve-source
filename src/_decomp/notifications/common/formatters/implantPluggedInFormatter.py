#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\implantPluggedInFormatter.py
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class ImplantPluggedInFormatter(BaseNotificationFormatter):

    def Format(self, notification):
        notification.subject = GetByLabel('Notifications/NotificationNames/ImplantPluggedIn')
        typeID = notification.data['typeID']
        slotNum = getattr(sm.GetService('godma').GetType(typeID), 'implantness', None)
        notification.subtext = GetByLabel('Notifications/ImplantPluggedIn', typeID=typeID, slotNum=slotNum)
