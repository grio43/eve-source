#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\controls\notificationSettingChange.py
import uthread2
from notifications.client.notificationSettings.notificationSettingHandler import NotificationSettingHandler

def GetSettingsForNotification(notificationTypeID):
    notificationSettingHandler = NotificationSettingHandler()
    notificationSettingData = notificationSettingHandler.LoadSettings()
    settingsForNotification = notificationSettingData[notificationTypeID]
    return (settingsForNotification.showAtAll, settingsForNotification.showPopup)


def ChangeShowAtAllSettingForNotification(notificationTypeID, onValue = True):
    _ChangeSettingForNotification(notificationTypeID, 'showAtAll', onValue)


def ChangePopupSettingForNotification(notificationTypeID, onValue = True):
    _ChangeSettingForNotification(notificationTypeID, 'showPopup', onValue)


def _ChangeSettingForNotification(notificationTypeID, attributeName, value):
    notificationSettingHandler = NotificationSettingHandler()
    notificationSettingData = notificationSettingHandler.LoadSettings()
    notificationData = notificationSettingData[notificationTypeID]
    setattr(notificationData, attributeName, value)
    notificationSettingHandler.SaveSettings(notificationSettingData)
    ReloadSettingWnd()


@uthread2.BufferedCall(1000)
def ReloadSettingWnd():
    from notifications.client.controls.notificationSettingsWindow import NotificationSettingsWindow
    wnd = NotificationSettingsWindow.GetIfOpen()
    if wnd and not wnd.destroyed:
        wnd.ReloadSettings()
