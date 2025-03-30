#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fitting\shipSceneContainer.py
import math
import eveui
import geo2
from eve.client.script.ui.control.scenecontainer import SceneContainer
from eveSpaceObject import spaceobjanimation
import evetypes
from fsdBuiltData.common.graphicIDs import GetSofFactionName
from iconrendering2.renderers.renderer_hologram import ApplyIsisEffect
import log
from eve.client.script.environment.model.turretSet import TurretSet, StructureMoonMiningTurretSet
import trinity
import uthread
import blue
from inventorycommon.util import IsModularShip
from uthread2.callthrottlers import CallCombiner
from evegraphics.controllers.clientControllerRegistry import ChangeControllerStateFromSlimItem
from evegraphics.CosmeticsLoader import CosmeticsLoader
from shipcosmetics.client.fittingsgateway.fittingsSignals import on_ship_cosmetics_changed
import telemetry
import logging
from eve.client.script.environment.spaceObject.spaceObject import modify_dna
from eve.client.script.environment.spaceObject.cosmeticsManager import CosmeticsManager
from cosmetics.common.structures.const import StructurePaintSlot
from cosmetics.common.structures.fitting import StructurePaintwork
import paints.data.dataLoader as dl
from inventorycommon.const import categoryStructure
from eve.common.script.sys.idCheckers import IsStructure, IsShipType
from cosmetics.common.ships.skins.static_data.slot_configuration import is_skinnable_ship
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
logger = logging.getLogger(__name__)

class ShipSceneContainer(SceneContainer):
    __notifyevents__ = ['ProcessFittingWindowStartMinimize',
     'ProcessFittingWindowEndMinimize',
     'OnSessionChanged',
     'OnCorpLogoReady',
     'OnAllianceLogoReady']

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        SceneContainer.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.model = None
        if hasattr(self.controller, 'on_new_itemID'):
            self.controller.on_new_itemID.connect(self.ReloadShipWhenChangingShips)
        if hasattr(self.controller, 'on_subsystem_fitted'):
            self.controller.on_subsystem_fitted.connect(self.ReloadShipModelWithoutAnimation)
        if hasattr(self.controller, 'on_hardpoints_fitted'):
            self.controller.on_hardpoints_fitted.connect(self.UpdateHardpoints)
        if hasattr(self.controller, 'on_module_online_state'):
            self.controller.on_module_online_state.connect(self.ProcessOnlineStateChange)
        if hasattr(self.controller, 'on_skin_material_changed'):
            self.controller.on_skin_material_changed.connect(self.OnSkinChanged)
        if hasattr(self.controller, 'on_stance_activated'):
            self.controller.on_stance_activated.connect(self.OnStanceActive)
        on_ship_cosmetics_changed.connect(self.OnShipCosmeticsChanged)
        self.CreateActiveShipModelThrottled = CallCombiner(self.CreateActiveShipModel, 1.0)
        sm.RegisterNotify(self)

    def LoadShipModel(self):
        uthread.new(self.ReloadShipModel)

    def _SetModelOffsetWhenReady(self, model):
        if model is None:
            return
        maxDelay = 2.0
        currentDelay = 0.0
        checkDelay = 50.0
        while not max(model.generatedShapeEllipsoidRadius) != -1:
            if self.destroyed:
                return
            if currentDelay > maxDelay:
                return
            blue.synchro.SleepWallclock(checkDelay)
            currentDelay += checkDelay / 1000.0

        modelOffset = getattr(model, 'generatedShapeEllipsoidCenter', (0.0, 0.0, 0.0))
        locatorSets = getattr(model, 'locatorSets', None)
        if locatorSets:
            lookAtLocator = locatorSets.FindByName('camera_look_at')
            if lookAtLocator is not None and len(lookAtLocator.locators) > 0:
                modelOffset = lookAtLocator.locators[0][0]
        if model.translationCurve is None:
            model.translationCurve = trinity.Tr2CurveConstant()
        invertedModelOffset = geo2.Vec3Scale(modelOffset, -1.0)
        model.translationCurve.value = invertedModelOffset

    def PrepareSpaceScene(self, maxPitch = None, scenePath = None, offscreen = False, resetZoom = True):
        super(ShipSceneContainer, self).PrepareSpaceScene(maxPitch=None, scenePath='res:/dx9/scene/fitting/fitting.red', resetZoom=True, offscreen=False)
        if IsStructure(evetypes.GetCategoryID(self.controller.typeID)):
            self.scene.sunDirection = (0.6198, -0.1016, -0.7781)
            self.scene.nebulaIntensity = 1.25
            self.scene.reflectionIntensity = 1.55
            self.scene.sunDiffuseColor = (1.0,
             205.0 / 255.0,
             170.0 / 255.0,
             1.0)
            self.scene.postprocess.taa = None

    @eveui.skip_if_destroyed
    def OnSkinChanged(self):
        if self.controller.itemID != session.shipid:
            return
        self.ReloadShipModel(animate=False)

    def _get_material_name(self, slot):
        if slot is not None:
            return dl.get_paint_material_name(slot)

    def OnShipCosmeticsChanged(self, _, cosmetics_types):
        if self.controller.itemID != session.shipid:
            return
        enabledCosmetics = sm.GetService('cosmeticsSvc').get_enabled_ship_cosmetics(session.shipid)
        cosmeticsLoader = CosmeticsLoader((CosmeticsLoader.ALLIANCE, CosmeticsLoader.CORP))
        uthread.new(cosmeticsLoader.SetCosmeticsOnShip, self.model, enabledCosmetics)

    def OnCorpLogoReady(self, _corpID, _size):
        self._UpdateShipCosmetics()

    def OnAllianceLogoReady(self, _allianceID, _size):
        self._UpdateShipCosmetics()

    def OnSessionChanged(self, _isremote, _session, change):
        if 'corpid' in change or 'allianceid' in change:
            self._UpdateShipCosmetics()

    def _UpdateShipCosmetics(self):
        enabledCosmetics = sm.GetService('cosmeticsSvc').get_enabled_ship_cosmetics(session.shipid)
        self.OnShipCosmeticsChanged(session.shipid, enabledCosmetics)

    @eveui.skip_if_destroyed
    def ReloadShipModelWithoutAnimation(self, *args, **kwargs):
        self.ReloadShipModel(animate=False)

    @eveui.skip_if_destroyed
    def ReloadShipWhenChangingShips(self, shipID, oldShipID, shipTypeID, oldShipTypeID):
        animate = True
        if self.controller.IsSimulated() and shipTypeID == oldShipTypeID:
            animate = False
        self.ReloadShipModel(animate=animate)

    def _SearchAndRemoveObservers(self):
        while len(self.model.observers) > 0:
            self.model.observers.pop()

        emitters = [ observer.name for observer in self.model.Find('trinity.TriObserverLocal') ]
        childContainers = self.model.effectChildren.Find('trinity.EveChildContainer')
        for container in childContainers:
            if hasattr(container, 'observers'):
                while len(container.observers) > 0:
                    popped = container.observers.pop()
                    if popped.name in emitters:
                        emitters.remove(popped.name)

            if len(emitters) == 0:
                break

    @telemetry.ZONE_METHOD
    def ReloadShipModel(self, throttle = False, animate = True):
        if self.destroyed:
            return
        with self._reloadLock:
            self.model = None
            if throttle:
                self.model = self.CreateActiveShipModelThrottled()
            else:
                self.model = self.CreateActiveShipModel()
            if not self.model:
                try:
                    if IsModularShip(self.controller.typeID) and self.controller.IsSimulated():
                        del self.scene.objects[:]
                except StandardError:
                    pass

                return
            if IsStructure(evetypes.GetCategoryID(self.controller.typeID)):
                sof = sm.GetService('sofService').spaceObjectFactory
                dna = self.model.dna
                paintwork = sm.GetService('cosmeticsSvc').get_structure_cosmetic_state(session.structureid, session.solarsystemid, force_refresh=False)
                if paintwork is not None:
                    mat1 = self._get_material_name(paintwork.get_slot(StructurePaintSlot.PRIMARY))
                    mat2 = self._get_material_name(paintwork.get_slot(StructurePaintSlot.SECONDARY))
                    mat3 = self._get_material_name(paintwork.get_slot(StructurePaintSlot.DETAILING))
                    dna = modify_dna(base_dna=dna, mat1=mat1, mat2=mat2, mat3=mat3, isStructure=True)
                self.model = sof.BuildFromDNA(dna)
            self._SearchAndRemoveObservers()
            trinity.WaitForResourceLoads()
            self.model.FreezeHighDetailMesh()
            self.ModifyCameraToFitShip(animate, self.model)
            self.AddToScene(self.model)
            if self.controller.IsSimulated():
                ApplyIsisEffect(self.model)
                if self.controller.ControllerForCategory() != const.categoryStructure:
                    self._AddGridToScene(self.scene, self.model)
            if animate:
                self.AnimEntry(yaw1=1.2 * math.pi, pitch0=0.3, pitch1=0.5)
            shipTypeID = self.controller.typeID
            stanceBtnControllerClass = self.controller.GetStanceBtnControllerClass()
            if stanceBtnControllerClass is None:
                return
            stanceID = stanceBtnControllerClass().get_ship_stance(self.controller.itemID, shipTypeID)
            if not self.controller.IsSimulated():
                slimItem = sm.GetService('michelle').GetItem(self.controller.itemID)
                if slimItem is not None:
                    ChangeControllerStateFromSlimItem(shipTypeID, self.model, slimItem)
                    cosmeticsLoader = CosmeticsLoader((CosmeticsLoader.ALLIANCE, CosmeticsLoader.CORP))
                    cosmeticsLoader.Load(self.model, slimItem)
            spaceobjanimation.SetShipAnimationStance(self.model, stanceID)
            spaceobjanimation.TriggerDefaultStates(self.model)
            enabledCosmetics = sm.GetService('cosmeticsSvc').get_enabled_ship_cosmetics(session.shipid)
            cosmeticsLoader = CosmeticsLoader((CosmeticsLoader.ALLIANCE, CosmeticsLoader.CORP))
            uthread.new(cosmeticsLoader.SetCosmeticsOnShip, self.model, enabledCosmetics)
            if self.controller.IsSimulated():
                for eachEffect in getattr(self.model, 'effectChildren', []):
                    eachEffect.display = False

            else:
                self.UpdateHardpoints(self.model)

    def _AddGridToScene(self, scene, shipModel):
        rad = shipModel.GetBoundingSphereRadius()
        scaling = (4, 4, 4)
        translation = (0, -rad / 2, 0)
        grid = trinity.Load('res:/dx9/model/UI/ScanGrid.red')
        grid.scaling = scaling
        grid.translation = translation
        scene.objects.append(grid)
        grid2 = trinity.Load('res:/dx9/model/UI/ScanGrid.red')
        grid2.rotation = (0, 0, 1, 0)
        grid2.scaling = scaling
        grid2.translation = translation
        scene.objects.append(grid2)

    def ModifyCameraToFitShip(self, animate, shipModel):
        camera = self.camera
        if shipModel is not None and hasattr(shipModel, 'GetBoundingSphereCenter'):
            rad = shipModel.GetBoundingSphereRadius() + geo2.Vec3Length(shipModel.GetBoundingSphereCenter())
        else:
            rad = 1000.0
        minZoom = rad + camera.nearClip
        alpha = camera.fov / 2.0
        maxZoom = min(self.backClip - rad, rad * (1 / math.tan(alpha)) * 2)
        oldZoomDistance = self.minZoom + (self.maxZoom - self.minZoom) * self.zoom
        defaultZoom = minZoom / (maxZoom - minZoom)
        self.SetMinMaxZoom(minZoom, maxZoom)
        if animate or oldZoomDistance < minZoom or oldZoomDistance > maxZoom:
            self.SetZoom(defaultZoom)

    @telemetry.ZONE_METHOD
    def CreateActiveShipModel(self):
        newModel = self.controller.model
        if not newModel:
            return
        if hasattr(newModel, 'ChainAnimationEx'):
            newModel.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        newModel.display = 1
        newModel.name = str(self.controller.itemID)
        translation = trinity.Tr2CurveConstant()
        newModel.translationCurve = translation
        translation.value = geo2.Vec3Scale(newModel.GetBoundingSphereCenter(), -1)
        uthread.new(self._SetModelOffsetWhenReady, newModel)
        return newModel

    @telemetry.ZONE_METHOD
    @eveui.skip_if_destroyed
    def UpdateHardpoints(self, newModel = None):
        if newModel is None:
            newModel = self.GetSceneShip()
        if newModel is None:
            log.LogError('UpdateHardpoints - No model!')
            return
        factionName = GetSofFactionName(evetypes.GetGraphicID(self.controller.typeID))
        fittetTurretSets = TurretSet.FitTurrets(self.controller.itemID, newModel, factionName)
        for ts in fittetTurretSets.values():
            if isinstance(ts, StructureMoonMiningTurretSet):
                ts.Display()

    @telemetry.ZONE_METHOD
    def GetSceneShip(self):
        for model in self.scene.objects:
            if getattr(model, 'name', None) == str(self.controller.itemID):
                return model

    @telemetry.ZONE_METHOD
    def PlayDeploymentAnimation(self, slot, dogmaItem):
        sceneShip = self.GetSceneShip()
        if sceneShip is not None:
            for turret in getattr(sceneShip, 'turretSets', []):
                if turret.slotNumber != slot:
                    continue
                if dogmaItem.IsOnline():
                    turret.EnterStateIdle()
                else:
                    turret.EnterStateDeactive()
                    break

    @eveui.skip_if_destroyed
    def OnStanceActive(self, stanceID):
        spaceobjanimation.SetShipAnimationStance(self.GetSceneShip(), stanceID)

    def _OnClose(self, *args):
        sm.UnregisterNotify(self)
        SceneContainer._OnClose(self)

    @eveui.skip_if_destroyed
    def ProcessOnlineStateChange(self, dogmaItem):
        if self.destroyed:
            return
        slot = dogmaItem.flagID - const.flagHiSlot0 + 1
        if slot is not None:
            self.PlayDeploymentAnimation(slot, dogmaItem)

    def ProcessFittingWindowStartMinimize(self):
        self.Hide()

    def ProcessFittingWindowEndMinimize(self):
        self.Show()
