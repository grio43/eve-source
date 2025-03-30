#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihider\ui_hider_service.py
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceManager import ServiceManager
from logging import getLogger
from uihider.ui_hider import UiHider
logger = getLogger(__name__)

class UiHiderService(Service):
    __guid__ = 'svc.uihider'
    serviceName = 'svc.uihider'
    __displayname__ = 'uihider'
    __servicename__ = 'uihider'
    __notifyevents__ = ['OnSessionReset', 'OnUiRevealForced']

    def Run(self, memStream = None):
        self.ui_hider = UiHider()

    def OnSessionReset(self):
        self.ui_hider = UiHider()
        sm = ServiceManager.Instance()
        sm.ScatterEvent('OnUiHiderReset', self.ui_hider)

    def OnUiRevealForced(self):
        self.clear()

    def get_ui_hider(self):
        return self.ui_hider

    def set_template(self, template_id):
        self.ui_hider.set_active_template(template_id)

    def clear(self):
        self.ui_hider.reveal_everything()


_ui_hider_service = None

def get_ui_hider_service():
    global _ui_hider_service
    if _ui_hider_service is None:
        _ui_hider_service = ServiceManager.Instance().GetService('uihider')
    return _ui_hider_service
