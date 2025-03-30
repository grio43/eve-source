#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\podGuide\podGuideService.py
from carbon.common.script.sys.service import Service
from eve.client.script.ui.podGuide.podGuideUI import PodGuideWindow

class PodGuideService(Service):
    __update_on_reload__ = 1
    __guid__ = 'svc.podguide'
    __displayname__ = 'Pod Guide service'
    __slashhook__ = True

    def cmd_podguide_show(self, p):
        PodGuideWindow.ToggleOpenClose()
