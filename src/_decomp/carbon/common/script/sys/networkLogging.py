#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\sys\networkLogging.py
import blue
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_SERVICE
from eveprefs import boot

class NetworkLogging(Service):
    __guid__ = 'svc.networkLogging'
    __displayname__ = 'Network Logging'
    __exportedcalls__ = {'StartNetworkLogging': [ROLE_SERVICE],
     'StopNetworkLogging': [ROLE_SERVICE],
     'GetLoggingState': [ROLE_SERVICE]}

    def StartNetworkLogging(self, server, port, threshold):
        if server and port:
            return blue.EnableNetworkLogging(server, int(port), boot.role, int(threshold))

    def StopNetworkLogging(self):
        return blue.DisableNetworkLogging()

    def GetLoggingState(self):
        return blue.GetNetworkLoggingState()
