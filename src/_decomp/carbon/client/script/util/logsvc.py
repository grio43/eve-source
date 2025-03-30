#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\client\script\util\logsvc.py
from carbon.common.script.sys.service import Service

class LoggingSvc(Service):
    __guid__ = 'svc.log'
    __exportedcalls__ = {'Log': []}

    def Run(self, *etc):
        Service.Run(self, *etc)
        self.channels = {}

    def Stop(self, *etc):
        Service.Stop(self, *etc)
        self.channels = None

    def Log(self, channelName, flag, *what):
        if self.channels is not None:
            if channelName not in self.channels:
                import log
                self.channels[channelName] = log.GetChannel('nonsvc.' + channelName)
            if self.channels[channelName].IsOpen(flag):
                try:
                    self.channels[channelName].Log(u' '.join(map(unicode, what)).replace('\x00', '\\x00'), flag, 3)
                except:
                    pass
