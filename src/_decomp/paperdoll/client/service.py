#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\paperdoll\client\service.py
import uthread
from carbon.common.script.sys.service import Service

class PaperdollSvc(Service):
    __guid__ = 'svc.paperdoll'
    __servicename__ = 'paperdoll service'
    __displayname__ = 'Paperdoll Service'

    def Run(self, *etc):
        super(PaperdollSvc, self).Run(*etc)
        self.currentCharsPaperDollData = {}

    def GetMyPaperDollData(self, charID):
        currentCharsPaperDollData = self.currentCharsPaperDollData.get(charID, None)
        if currentCharsPaperDollData is not None:
            return currentCharsPaperDollData
        uthread.Lock(self)
        try:
            if self.currentCharsPaperDollData.get(charID, None) is None:
                paperDollServer = sm.RemoteSvc('paperDollServer')
                paperDollData = paperDollServer.GetMyPaperDollData(charID)
                self.currentCharsPaperDollData[charID] = paperDollData
            return self.currentCharsPaperDollData.get(charID, None)
        finally:
            uthread.UnLock(self)

    def ClearCurrentPaperDollData(self):
        self.currentCharsPaperDollData = {}
