#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\dogma\clientEffectCompiler.py
from eve.common.script.dogma.baseEffectCompiler import BaseEffectCompiler

class ClientEffectCompiler(BaseEffectCompiler):
    __guid__ = 'svc.clientEffectCompiler'
    __startupdependencies__ = ['dogma']
    __dependencies__ = ['clientDogmaStaticSvc']

    def Run(self, *args):
        super(ClientEffectCompiler, self).Run()
        self.SetupEffects()

    def GetDogmaStaticMgr(self):
        return self.clientDogmaStaticSvc
