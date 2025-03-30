#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\activities\newActivityNotify.py
import uthread
from eve.client.script.ui.shared.activities.window import ActivitiesWindow

def CheckOpenNewActivitiesNotifyWindow():
    if not session.charid:
        return False
    uthread.new(OpenNewActivitiesWindow)
    return True


def OpenNewActivitiesWindow():
    ActivitiesWindow.ToggleOpenClose()
