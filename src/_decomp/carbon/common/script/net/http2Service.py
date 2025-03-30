#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\http2Service.py
from carbon.common.script.net import machoNet
from carbon.common.script.sys.service import Service
from eveprefs import prefs

class CherryServer(Service):
    __guid__ = 'svc.http2'
    __startupdependencies__ = ['machoNet', 'WSGIService']
    __exportedcalls__ = {}
    __configvalues__ = {}
    __notifyevents__ = []

    def Run(self, memStream = None):
        self.servers = []
        if not prefs.GetValue('http2', 1):
            self.LogNotice('http2 service not booting up CherryPy ESP app because prefs.http2=0')
            return
        from carbon.common.script.net.httpServer import InitializeEspApp
        cherryTree = InitializeEspApp()
        transport_key = 'tcp:raw:http2' if prefs.GetValue('httpServerMode', 'ccp').lower() == 'ccp' else 'tcp:raw:http'
        port = self.machoNet.GetBasePortNumber() + machoNet.offsetMap[machoNet.mode][transport_key]
        server = self.WSGIService.StartServer(cherryTree, port)
        self.servers.append(server)
        self.LogNotice('CherryPy ESP app server running on port %s' % port)

    def Stop(self, memStream):
        for server in self.servers:
            self.WSGIService.StopServer(server)
