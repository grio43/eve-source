#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\dogma\clientDogma.py
from eve.common.script.dogma.baseDogma import BaseDogma

class ClientDogma(BaseDogma):
    __guid__ = 'svc.dogma'

    def Run(self, *args):
        BaseDogma.Run(self, *args)

    def GetDogmaIM(self):
        if self.dogmaIM is None:
            self.dogmaIM = sm.GetService('dogmaStaticSvc')
        return self.dogmaIM

    def GetEffectCompiler(self):
        if self.effectCompiler is None:
            self.effectCompiler = sm.GetService('clientEffectCompiler')
        return self.effectCompiler
