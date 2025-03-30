#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\structure\structureServices.py
import structures
from carbon.common.script.sys.service import Service
from eve.client.script.ui.station import stationServiceConst

class StructureServices(Service):
    __guid__ = 'svc.structureServices'
    __notifyevents__ = ['OnSessionChanged', 'OnStructureServiceChanged']

    def Run(self, *args):
        self.onlineServices = None
        self.structureID = None

    def OnSessionChanged(self, isRemote, session, change):
        if 'structureid' in change and session.structureid:
            self._FetchOnlineServices()

    def GetPossibleStructureServices(self):
        return structures.SERVICES_ACCESS_SETTINGS.keys()

    def CharacterGetServices(self, structureID):
        if structureID == session.structureid:
            if self.onlineServices is None or self.structureID != session.structureid:
                self._FetchOnlineServices()
            return self.onlineServices
        return sm.RemoteSvc('structureSettings').CharacterGetServices(structureID)

    def IsServiceAvailableForCharacter(self, serviceID):
        if serviceID in structures.ONLINE_SERVICES_UNRESTRICTED_ACCESS:
            return True
        if serviceID == stationServiceConst.serviceIDAlwaysPresent:
            return True
        if serviceID in self.CharacterGetServices(session.structureid):
            return True
        if serviceID == structures.SERVICE_INDUSTRY:
            return bool(structures.INDUSTRY_SERVICES & set(self.onlineServices.keys()))

    def OnStructureServiceChanged(self, structureID):
        if structureID == session.structureid:
            self._FetchOnlineServices()
        sm.ScatterEvent('OnStructureServiceUpdated')

    def _FetchOnlineServices(self):
        if session.structureid is not None:
            self.onlineServices = sm.RemoteSvc('structureSettings').CharacterGetServices(session.structureid)
        self.structureID = session.structureid
