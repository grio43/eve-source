#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\regionalui\addictionwarningnotification.py
import carbonui.const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.common.script.util.notificationconst import notificationTypeAddictionWarning
from notifications.client.controls.notificationEntry import NotificationEntry
from notifications.client.notificationUIConst import NOTIFICATION_CENTER_PADDING_H
from regionalui.utils import get_addiction_warning_text, get_playtime_text

class AddictionWarningNotification(object):

    def __init__(self):
        self.subject = get_playtime_text()
        self.subtext = get_addiction_warning_text()
        self.body = None
        self.typeID = notificationTypeAddictionWarning
        self.senderID = None
        self.data = {}


class AddictionWarningNotificationEntry(ContainerAutoSize):
    default_name = 'AddictionWarningNotificationContainer'
    default_state = uiconst.UI_DISABLED
    POPUP_PADDING_H = NOTIFICATION_CENTER_PADDING_H
    POPUP_PADDING_V = 4

    def ApplyAttributes(self, attributes):
        super(AddictionWarningNotificationEntry, self).ApplyAttributes(attributes)
        entry = NotificationEntry(name='AddictionWarningNotificationEntry', parent=self, align=uiconst.TOTOP, width=self.width - 2 * self.POPUP_PADDING_H, padding=(self.POPUP_PADDING_H,
         self.POPUP_PADDING_V,
         self.POPUP_PADDING_H,
         self.POPUP_PADDING_V), created=0, notification=AddictionWarningNotification(), bgColor=(0.0, 0.0, 0.0, 0.7))
        entry.LoadContent()
