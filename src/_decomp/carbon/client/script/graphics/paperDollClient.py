#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\client\script\graphics\paperDollClient.py
import collections
import telemetry
from carbon.common.script.sys.service import Service
from eve.client.script.paperDoll.paperDollImpl import Factory
from eve.client.script.paperDoll.paperDollSpawnWrappers import PaperDollManager
from eve.common.script.paperDoll.paperDollConfiguration import PerformanceOptions
from eve.common.script.paperDoll.paperDollDefinitions import GENDER

class PaperDollClientComponent(object):

    def __init__(self):
        self.doll = None
        self.typeID = None
        self.dna = None
        self.gender = None


class PaperDollClient(Service):
    __guid__ = 'svc.paperDollClient'
    __notifyevents__ = []
    __dependencies__ = ['cacheDirectoryLimit']
    __componentTypes__ = ['paperdoll']

    def lazyprop(fn):
        attr_name = '_lazy_' + fn.__name__

        @property
        def _lazyprop(self):
            if not hasattr(self, attr_name):
                setattr(self, attr_name, fn(self))
            return getattr(self, attr_name)

        return _lazyprop

    @lazyprop
    def dollFactory(self):
        factory = Factory()
        factory.compressTextures = True
        factory.allowTextureCache = True
        return factory

    @lazyprop
    def paperDollManager(self):
        pdm = PaperDollManager(self.dollFactory, keyFunc=lambda doll: doll.GetName())
        return pdm

    def Run(self, *etc):
        PerformanceOptions.EnableOptimizations()
        self._AppPerformanceOptions()
        self.renderAvatars = True

    def _AppPerformanceOptions(self):
        raise NotImplementedError('This needs to be implemented in application specific, derived class.')

    def CreateComponent(self, name, state):
        component = PaperDollClientComponent()
        component.gender = state.get('gender', None)
        component.dna = state.get('dna', None)
        component.typeID = state.get('typeID', None)
        return component

    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        report['gender'] = self.GetDBGenderToPaperDollGender(component.gender)
        report['autoLOD'] = component.doll.autoLod
        report['overrideLod'] = component.doll.doll.overrideLod
        return report

    def GetDBGenderToPaperDollGender(self, gender):
        if gender:
            return GENDER.MALE
        return GENDER.FEMALE

    def SetupComponent(self, entity, component):
        trinityScene = sm.GetService('graphicClient').GetScene(entity.scene.sceneID)
        gender = self.GetDBGenderToPaperDollGender(component.gender)
        resolution = self.GetInitialTextureResolution()
        realDna = self.GetDollDNA(trinityScene, entity, gender, component.dna, session.bloodlineID)
        if entity.entityID == session.charid:
            shouldLOD = False
            spawnAtLOD = -1
        else:
            shouldLOD = True
            spawnAtLOD = 0
        component.doll = self.SpawnDoll(trinityScene, entity, gender, realDna, shouldLOD, textureResolution=resolution, spawnAtLOD=spawnAtLOD)
        component.doll.avatar.display = self.renderAvatars
        if entity.HasComponent('animation'):
            component.doll.avatar.animationUpdater = entity.GetComponent('animation').GetUpdater()
        else:
            self.LogError('Entity ' + entity + " doesn't have an animation component, so the PaperDoll component didn't load an animationUpdater!")
        component.doll.avatar.name = str(entity.entityID)

    def RegisterComponent(self, entity, component):
        positionComponent = entity.GetComponent('position')
        if positionComponent:
            pass

    def GetPaperDollByEntityID(self, entID):
        return self.paperDollManager.GetPaperDollCharacterByKey(str(entID))

    def PackUpForSceneTransfer(self, component, destinationSceneID):
        return {'gender': component.gender,
         'dna': component.dna,
         'typeID': component.typeID}

    def UnPackFromSceneTransfer(self, component, entity, state):
        component.gender = state.get('gender', None)
        component.dna = state.get('dna', None)
        component.typeID = state.get('typeID', None)
        return component

    def GetInitialTextureResolution(self):
        return None

    def GetDollDNA(self, scene, entity, dollGender, dollDnaInfo, bloodlineID):
        return dollDnaInfo

    @telemetry.ZONE_METHOD
    def SpawnDoll(self, scene, entity, dollGender, dollDnaInfo, shouldLod, textureResolution = None, spawnAtLOD = 0):
        positionComponent = entity.GetComponent('position')
        if dollDnaInfo is not None:
            doll = self.paperDollManager.SpawnPaperDollCharacterFromDNA(scene, str(entity.entityID), dollDnaInfo, position=positionComponent.position, gender=dollGender, lodEnabled=shouldLod, textureResolution=textureResolution, spawnAtLOD=spawnAtLOD)
        else:
            doll = self.paperDollManager.SpawnDoll(scene, point=positionComponent.position, gender=dollGender, autoLOD=shouldLod, lod=spawnAtLOD)
        return doll

    def UnRegisterComponent(self, entity, component):
        if component.callback and entity.HasComponent('position'):
            entity.GetComponent('position').UnRegisterPlacementObserverWrapper(component.callback)
            component.callback = None

    def TearDownComponent(self, entity, component):
        component.doll.avatar.animationUpdater = None
        component.doll.avatar.worldTransformUpdater = None
        self.paperDollManager.RemovePaperDollCharacter(component.doll)
        component.doll = None

    def ToogleRenderAvatars(self):
        self.renderAvatars = not self.renderAvatars
        for doll in self.paperDollManager:
            doll.avatar.display = self.renderAvatars
