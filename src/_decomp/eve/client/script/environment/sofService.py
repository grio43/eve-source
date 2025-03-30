#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\sofService.py
import trinity
import blue
import uthread2
from carbon.common.script.sys.service import Service

def GetSofService():
    return sm.GetService('sofService')


class sofService(Service):
    __guid__ = 'svc.sofService'
    __displayname__ = 'Space Object Factory'
    __servicename__ = 'sofService'

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        self.spaceObjectFactory = SpaceObjectFactoryWrapper()
        self.spaceObjectFactory.Load()

    def Stop(self, stream):
        Service.Stop(self)
        self.spaceObjectFactory = None


class SpaceObjectFactoryWrapper(object):

    def __init__(self):
        self._dataFile = 'res:/dx9/model/spaceobjectfactory/data.red'
        self._sof = trinity.EveSOF()
        self._loaded = False
        self._loadingTasklet = None
        self.sofDB = None

    def Load(self):
        self._loadingTasklet = uthread2.start_tasklet(self._Load)

    def _Load(self):
        self.sofDB = trinity.Load(self._dataFile)
        self._sof.dataMgr.SetData(self.sofDB)
        self._loaded = True
        self._loadingTasklet = None

    def GetSofDB(self):
        self._LoadOrYield()
        return self.sofDB

    def _LoadOrYield(self):
        if self._loaded:
            return
        if not self._loadingTasklet:
            self.Load()
        uthread2.wait([self._loadingTasklet], 300)

    def Build(self, *args, **kwargs):
        self._LoadOrYield()
        return self._sof.Build(*args, **kwargs)

    def BuildFromDNA(self, *args, **kwargs):
        self._LoadOrYield()
        return self._sof.BuildFromDNA(*args, **kwargs)

    def ValidateDNA(self, *args, **kwargs):
        self._LoadOrYield()
        return self._sof.ValidateDNA(*args, **kwargs)

    def SetupTurretMaterialFromDNA(self, *args, **kwargs):
        self._LoadOrYield()
        return self._sof.SetupTurretMaterialFromDNA(*args, **kwargs)

    def SetupTurretMaterialFromFaction(self, *args, **kwargs):
        self._LoadOrYield()
        return self._sof.SetupTurretMaterialFromFaction(*args, **kwargs)
