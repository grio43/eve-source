#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\service.py
import signals
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceManager import ServiceManager

class ExpertSystemService(Service):
    __guid__ = 'svc.expertSystemSvc'
    __servicename__ = 'expertSystemSvc'
    __displayname__ = 'Expert Systems Client Service'
    __notifyevents__ = ['OnExpertSystemsUpdated', 'OnSessionChanged']
    __startupdependencies__ = ['loading', 'machoNet', 'uiColor']

    def __init__(self):
        super(ExpertSystemService, self).__init__()
        self._myExpertSystems = None
        self.on_expert_systems_updated = signals.Signal()

    @staticmethod
    def instance():
        return ServiceManager.Instance().GetService(ExpertSystemService.__servicename__)

    @property
    def remote(self):
        return ServiceManager.Instance().RemoteSvc('expertSystemMgr')

    def OnSessionChanged(self, isRemote, session, change):
        if 'charid' in change:
            self._myExpertSystems = None

    def GetMyExpertSystems(self):
        if self._myExpertSystems is None:
            self._myExpertSystems = self.remote.GetMyExpertSystems()
        return self._myExpertSystems

    def OnExpertSystemsUpdated(self, expertSystems, expertSystemAdded, expertSystemTypeID):
        self.LogInfo('OnExpertSystemsUpdated', expertSystems)
        self._myExpertSystems = expertSystems
        if expertSystemAdded:
            self._ShowExpertSystemsFanfare(expertSystemTypeID)
        ServiceManager.Instance().ScatterEvent('OnExpertSystemsUpdated_Local')
        self.on_expert_systems_updated()

    def _ShowExpertSystemsFanfare(self, expertSystemTypeID):
        from expertSystems.client.ui.fanfare import ExpertSystemFanfareWindow
        wnd = ExpertSystemFanfareWindow.GetIfOpen()
        if wnd:
            wnd.AddAnotherExpertSystemToFanfare(expertSystemTypeID)
        else:
            ExpertSystemFanfareWindow.ShowFanfare(expertSystemTypeID)

    def RemoveExpertSystem(self, expertSystemTypeID):
        self.remote.RemoveMyExpertSystem(expertSystemTypeID)
