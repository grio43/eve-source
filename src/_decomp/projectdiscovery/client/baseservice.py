#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\baseservice.py
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceManager import ServiceManager
from projectdiscovery.client.const import Events

class CommonProjectDiscoveryClientService(Service):
    __servicename__ = 'ProjectDiscoveryClient'
    __displayname__ = 'ProjectDiscoveryClient'
    __guid__ = 'svc.ProjectDiscoveryClient'
    __notifyevents__ = ['OnAnalysisKreditsChange']

    def __init__(self):
        super(CommonProjectDiscoveryClientService, self).__init__()
        self._remote_service = None
        self._is_enabled = None

    def Run(self, *args, **kwargs):
        Service.Run(self, *args, **kwargs)

    @property
    def remote_service(self):
        if not self._remote_service:
            sm = ServiceManager.Instance()
            self._remote_service = sm.RemoteSvc('ProjectDiscovery')
        return self._remote_service

    def OnAnalysisKreditsChange(self):
        sm = ServiceManager.Instance()
        sm.ScatterEvent(Events.UpdateAnalysisKredits)

    def is_enabled(self):
        if self._is_enabled is None:
            self._is_enabled = self.remote_service.is_enabled()
        return self._is_enabled
