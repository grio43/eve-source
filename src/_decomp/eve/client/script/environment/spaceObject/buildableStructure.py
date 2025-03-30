#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\buildableStructure.py
from eve.client.script.environment.spaceObject.LargeCollidableStructure import LargeCollidableStructure
from fsdBuiltData.common.graphicIDs import GetExplosionBucketID
from evegraphics.utils import BuildSOFDNAFromGraphicID
import locks
NANO_CONTAINER_GRAPHIC_ID = 20930

class BuildableStructure(LargeCollidableStructure):

    def __init__(self):
        LargeCollidableStructure.__init__(self)
        self.overlayEffects = {}
        self.nanoContainerModel = None
        self.nanoContainerModelLoadedEvent = locks.Event()
        self.structureModel = None
        self.structureModelLoadedEvent = locks.Event()
        self.isConstructing = False
        self.oldClipSphereCenter = (0.0, 0.0, 0.0)

    def Prepare(self):
        self.logger.debug('BuildableStructure: Preparing')
        self.LoadStructureModel()
        LargeCollidableStructure.Prepare(self)

    def LoadNanoContainerModel(self):
        self.logger.debug('BuildableStructure: Loading nano container model')
        self.nanoContainerModel = self.LoadAdditionalModel(sofDna=BuildSOFDNAFromGraphicID(NANO_CONTAINER_GRAPHIC_ID))
        self.nanoContainerModel.name += '_nanocontainer'
        self.nanoContainerModelLoadedEvent.set()

    def LoadStructureModel(self):
        self.logger.debug('BuildableStructure: Loading structure model')
        structureModel = self.LoadAdditionalModel()
        self.SetupAnimationInformation(structureModel)
        self.structureModel = structureModel
        self.structureModelLoadedEvent.set()

    def SetModelDisplay(self, model, display):
        if model is not None:
            model.display = display

    def LoadUnLoadedModels(self):
        if self.structureModel is None:
            self.LoadStructureModel()

    def SetupModel(self, unanchored):
        sendOutModelLoadedEvent = self.model is None
        self.explosionBucketID = GetExplosionBucketID(self.typeData.get('graphicID', None))
        showStructureModel = True
        if self.isConstructing:
            self.model = self.GetStructureModel()
            self.GetNanoContainerModel()
            self.model.display = True
            self.Assemble()
        elif unanchored:
            showStructureModel = False
            self.model = self.GetNanoContainerModel()
            self.explosionBucketID = GetExplosionBucketID(NANO_CONTAINER_GRAPHIC_ID)
        else:
            self.model = self.GetStructureModel()
        if sendOutModelLoadedEvent:
            self.NotifyModelLoaded()
        if self.structureModel is not None:
            self.structureModel.display = showStructureModel

    def GetNanoContainerModel(self):
        if self.nanoContainerModel is None:
            self.LoadNanoContainerModel()
        return self.nanoContainerModel

    def GetStructureModel(self):
        if self.structureModel is None:
            self.logger.debug('BuildableStructure: waiting for structure model')
            self.structureModelLoadedEvent.wait()
            self.logger.debug('BuildableStructure: done waiting for structure model')
        if self.structureModel is None:
            self.logger.warning('BuildableStructure: Failed to get a valid structure model')
            return
        return self.structureModel

    def HasModels(self):
        return self.nanoContainerModel is not None or self.structureModel is not None

    def ClearAndRemoveAllModels(self, scene):
        LargeCollidableStructure.ClearAndRemoveAllModels(self, scene)
        self.RemoveAndClearModel(self.nanoContainerModel, scene)
        self.RemoveAndClearModel(self.structureModel, scene)
        self.nanoContainerModel = None
        self.structureModel = None
        self.model = None

    def RemoveAllModelsFromScene(self, scene):
        LargeCollidableStructure.RemoveAllModelsFromScene(self, scene)
        scene.objects.fremove(self.nanoContainerModel)
        scene.objects.fremove(self.structureModel)

    def PreBuildingSteps(self):
        self.isConstructing = True
        self.SetupModel(False)
        self.StartNanoContainerAnimation()

    def PostBuildingSteps(self, built):
        self.isConstructing = False
        if built:
            self.RemoveAndClearModel(self.nanoContainerModel)
            self.nanoContainerModel = None
        else:
            self.EndNanoContainerAnimation()

    def StartNanoContainerAnimation(self, deployScale = 1):
        if self.nanoContainerModel is not None:
            self.nanoContainerModel.PlayAnimationEx('Deploy', 1, 0, deployScale)
            self.nanoContainerModel.ChainAnimationEx('OpenLoop', 0, 0, 1)

    def EndNanoContainerAnimation(self):
        if self.nanoContainerModel is not None:
            self.nanoContainerModel.PlayAnimation('Pack')
