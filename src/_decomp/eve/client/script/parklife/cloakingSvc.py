#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\cloakingSvc.py
from carbon.common.script.sys.service import Service
from carbonui.uicore import uicore

class CloakingSvc(Service):
    __dependencies__ = ['audio']
    __guid__ = 'svc.cloaking'
    __servicename__ = 'cloaking'
    __displayname__ = 'Cloaking service'
    __notifyevents__ = ['OnCloakModuleForceDeactivated']

    def OnCloakModuleForceDeactivated(self, notifyMsg, notifyArgs):
        self.audio.SendUIEvent('ui_forced_decloak_play')
        uicore.Message(notifyMsg, notifyArgs)
