#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\skillInjected.py
import evetypes
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class SkillInjectedFormatter(BaseNotificationFormatter):

    def Format(self, notification):
        notification.subject = GetByLabel('Notifications/NotificationNames/SkillInjected')
        typeID = notification.data['typeID']
        groupName = evetypes.GetGroupName(typeID)
        notification.subtext = GetByLabel('Notifications/SkillInjected', groupName=groupName, typeID=typeID)
