#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\LargeCollidableStructure.py
import evetypes
import uthread
from eve.client.script.environment.model.turretSet import TurretSet
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from cosmetics.common.structures.fitting import StructurePaintwork
from cosmetics.common.structures.const import StructurePaintSlot
import paints.data.dataLoader as dl
from cosmetics.client.structures.fittingSignals import on_structure_cosmetic_state_changed
from evegraphics.graphicEffects.skinChange import RemoveAllTemporaryModels, ChangeStructureSkin
from uthread2 import StartTasklet
import blue
from eve.client.script.environment.spaceObject.spaceObject import modify_dna
from cosmetics.common.structures.const import PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS

class LargeCollidableStructure(SpaceObject):

    def __init__(self):
        super(LargeCollidableStructure, self).__init__()
        self.fitted = False
        self.turrets = []
        self.modules = {}
        self.paintwork = None
        on_structure_cosmetic_state_changed.connect(self._on_cosmetic_state_changed)

    def _on_cosmetic_state_changed(self, structure_id, paintwork):
        if structure_id == self.id:
            self.paintwork = paintwork
            newDna = self.GetDNA()
            self._skinChangeTasklets.append(StartTasklet(self.ChangeSkin, newDna))

    def _get_material_name(self, slot):
        if slot is not None:
            return dl.get_paint_material_name(slot)

    def set_cosmetic_state(self, state):
        for slot_name, paint_id in state.items():
            self.paintwork.set_slot(slot_name, paint_id)

    def ChangeSkin(self, newDna = None):
        if self.model is None:
            return
        oldModel = self.nextModel or self.model
        nextModel = self._LoadModelResource(None)
        blue.resMan.Wait()
        handled = False
        if sm.GetService('subway').InJump():
            handled = sm.GetService('subway').HandleSkinChange(nextModel)
        if not handled:
            self.fitted = False
            self.nextModel = self._SetupModelAndAddToScene(loadedModel=nextModel, addToScene=False)
            if self.nextModel is None:
                return
            self.SetupAnimationInformation(self.nextModel)
            self._SetupModelAttributes(self.nextModel, '%d' % self.id)
            self.ChangingSkin(self.nextModel)
            ChangeStructureSkin(oldModel, self.nextModel, self.spaceMgr.GetScene(), newDna=newDna, paintwork=self.paintwork, postSkinChangeCallback=self.PostSkinChangeCallback)

    def OnSlimItemUpdated(self, slimItem):
        super(LargeCollidableStructure, self).OnSlimItemUpdated(slimItem)
        if not slimItem.state and set([ i[0] for i in slimItem.modules or [] if evetypes.GetGraphicID(i[1]) is not None ]) != set(self.modules.keys()):
            uthread.new(self.ReloadHardpoints)

    def ReloadHardpoints(self):
        self.UnfitHardpoints()
        self.FitHardpoints()

    def UnfitHardpoints(self):
        if not self.fitted:
            return
        self.logger.debug('Unfitting hardpoints')
        newModules = {}
        for key, val in self.modules.iteritems():
            if val not in self.turrets:
                newModules[key] = val

        self.modules = newModules
        del self.turrets[:]
        self.fitted = False

    def FitHardpoints(self, blocking = False):
        if self.fitted:
            return
        if self.model is None:
            self.logger.warning('FitHardpoints - No model')
            return
        self.logger.debug('Fitting hardpoints')
        self.fitted = True
        newTurretSetDict = TurretSet.FitTurrets(self.id, self.model, self.typeData.get('sofFactionName', None))
        self.turrets = []
        for key, val in newTurretSetDict.iteritems():
            self.modules[key] = val
            self.turrets.append(val)

    def LookAtMe(self):
        if not self.model:
            return
        if not self.fitted:
            self.FitHardpoints()

    def Assemble(self):
        if self.model is not None:
            self.model.rotationCurve = None
        self.SetStaticRotation()
        if hasattr(self.model, 'ChainAnimationEx'):
            self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        self.SetupSharedAmbientAudio()
        self.SetStaticRotation()
        self.ReloadHardpoints()

        def _load_cosmetics():
            state = sm.GetService('cosmeticsSvc').get_cached_structure_cosmetic_state(self.id)
            if state is not None:
                self.set_cosmetic_state(state.get_slots())

        uthread.new(_load_cosmetics)

    def OnDamageState(self, damageState):
        self._OnDamageState(damageState)

    def LoadModel(self, fileName = None, loadedModel = None, notify = True, addToScene = True):

        def _load_cosmetics():
            state = sm.GetService('cosmeticsSvc').get_cached_structure_cosmetic_state(self.id)
            if state is not None:
                self.set_cosmetic_state(state.get_slots())

        uthread.new(_load_cosmetics)
        self.model = self._SetupModelAndAddToScene(fileName, loadedModel, addToScene)
        if self.model is None:
            return
        self.SetupAnimationInformation(self.model)
        if notify:
            self.NotifyModelLoaded()

    def GetDNA(self):
        sofDNA = super(LargeCollidableStructure, self).GetDNA()
        if self.typeID not in PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS:
            return sofDNA
        if not self.paintwork:
            state = sm.GetService('cosmeticsSvc').get_cached_structure_cosmetic_state(self.id)
            self.paintwork = StructurePaintwork()
            if state is not None:
                self.set_cosmetic_state(state.get_slots())
        if sofDNA is not None:
            mat1 = self._get_material_name(self.paintwork.get_slot(StructurePaintSlot.PRIMARY))
            mat2 = self._get_material_name(self.paintwork.get_slot(StructurePaintSlot.SECONDARY))
            mat3 = self._get_material_name(self.paintwork.get_slot(StructurePaintSlot.DETAILING))
            sofDNA = modify_dna(base_dna=sofDNA, mat1=mat1, mat2=mat2, mat3=mat3, isStructure=True)
        return sofDNA
