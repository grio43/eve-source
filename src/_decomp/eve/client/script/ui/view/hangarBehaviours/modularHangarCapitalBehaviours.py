#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\hangarBehaviours\modularHangarCapitalBehaviours.py
import blue
import geo2
import trinity
import math
import logging
import uthread
import modularHangarBehavioursConstants as hConst
from uthread2 import call_after_simtime_delay
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from modularHangarBehaviours import ModularHangarShipBehaviour, ModularHangarDroneBehaviour
from evetypes import GetGroupID
import inventorycommon.const as invC
import evecamera
log = logging.getLogger(__name__)
EXIT_POINT_FROM_SHIP_OFFSET = (0, 0, 10000)

class ModularCapitalHangarShipBehaviour(ModularHangarShipBehaviour):

    def __init__(self):
        super(ModularCapitalHangarShipBehaviour, self).__init__()
        self.shipTranslation = (0, 0, 0)
        self.shipRotation = (0, 0, 0, 0)
        self.playerShipItemID = 0
        self.playerShipTypeID = 0
        self.shipOffset = (0, 0, 0)
        self.exitLocation = (0, 0, 0)
        self.hangarScene = None
        self.hangarModel = None
        self.playerShip = None
        self.dockMultiEffect = None
        self.dockedShipItemID = 0

    def SetAnchorPoint(self, hangarModel, hangarScene):
        if hangarModel is None:
            self.log.error('ModularHangarShipBehaviour.SetAnchorPoint: Setting anchor point when hangarModel is None')
            return
        self.hangarScene = hangarScene
        self.hangarModel = hangarModel
        self._CreateDock(hangarModel, hangarScene)

    def GetCamera(self):
        return sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_MODULARHANGAR_CAPITAL)

    def GetAllDockedShips(self):
        return [self.playerShip]

    def _CreateDock(self, hangarModel, hangarScene):
        shipPlacement = hangarModel.locatorSets.FindByName('ship_placement')
        MEResPath = GetGraphicFile(hConst.DOCKER_CAPITAL_MULTIEFFECT_GRAPHIC_ID)
        if shipPlacement is None or len(shipPlacement.locators) != 1:
            self.log.error('ModularHangarShipBehaviour._CreateDock: ship_placement locatorSet missconfigured')
            return
        for locator in shipPlacement.locators:
            self.shipTranslation = locator[0]
            self.shipRotation = locator[1]
            ME = blue.resMan.LoadObject(MEResPath)
            self.exitLocation = geo2.Vec3Add(locator[0], EXIT_POINT_FROM_SHIP_OFFSET)
            self.dockMultiEffect = ME
            self.dockMultiEffect.SetParameter('docking_dock', hangarModel)
            self.dockMultiEffect.SetControllerVariable('isCapital', 1.0)

    def _ConfigureShipTransform(self, ship, offset):
        platformRotation = trinity.Tr2CurveConstant()
        platformRotation.value = self.shipRotation
        shipTranslation = trinity.Tr2CurveCombiner()
        platformTranslation = trinity.Tr2TranslationAdapter()
        platformTranslation.value = geo2.Add(offset, self.shipTranslation)
        multiEffectTranslation = trinity.Tr2TranslationAdapter()
        multiEffectTranslation.rotationOffset = self.shipRotation
        shipTranslation.curves.append(platformTranslation)
        shipTranslation.curves.append(multiEffectTranslation)
        displayOffset = ship.locatorSets.FindByName(hConst.LOCATORSET_DISPLAY_OFFSET)
        if displayOffset is not None and len(displayOffset.locators) == 1:
            displayOffsetCurve = trinity.Tr2TranslationAdapter()
            displayOffsetCurve.value = displayOffset.locators[0][0]
            displayOffsetCurve.rotationOffset = self.shipRotation
            shipTranslation.curves.append(displayOffsetCurve)
        ship.translationCurve = shipTranslation
        ship.rotationCurve = platformRotation
        ship.modelRotationCurve = trinity.Tr2RotationAdapter()
        ship.modelTranslationCurve = trinity.Tr2TranslationAdapter()

    def PrepareFSB(self, vfxMultiEffect):
        self.dockMultiEffect.SetParameter('docking_ship', None)

    def FinishFSB(self):
        self.dockMultiEffect.SetParameter('docking_ship', self.playerShip)
        self.dockMultiEffect.SetControllerVariable('materialize', 1.0)
        self.dockMultiEffect.SetControllerVariable('_previousState', 1.0)
        self.dockMultiEffect.SetControllerVariable('materializeDelay', 0.0)
        self.dockMultiEffect.StartControllers()

    def GetActiveDock(self):
        return None

    def PlaceShip(self, itemID, typeID, skipDockingAnimation = False):
        if self.playerShipItemID == self.dockedShipItemID:
            return self.playerShip
        firstTime = self.playerShip is None
        model = self.LoadShipModel(itemID, typeID)
        trinity.WaitForResourceLoads()
        try:
            counter = 0
            maxYields = 10
            while counter < maxYields:
                modelBB = model.GetLocalBoundingBox()
                if modelBB[0][0] != 0.0 and modelBB[0][2] != 0.0:
                    break
                counter = counter + 1
                blue.synchro.Yield()
                if counter is maxYields - 1:
                    self.log.error('modularHangarCapitalBehaviour.PlaceShip: failed waiting for boundingBox, model: %s' % model)

        except IndexError:
            self.log.error('modularHangarCapitalBehaviour.PlaceShip: bounding box missconfigured')

        self.shipOffset = geo2.QuaternionTransformVector(self.shipRotation, self.GetShipOffset(model, typeID))
        self._ConfigureShipTransform(model, self.shipOffset)
        model.clipSphereFactor = 1.0
        self.playerShip = model
        self.hangarScene.objects.append(model)
        self.GetCamera().SetShip(model, typeID)
        if skipDockingAnimation:
            self._ReplaceShipInDock(self, model, None, skipAnimation=True)
            self.dockMultiEffect.SetControllerVariable('_previousState', 1.0)
            self.dockMultiEffect.SetControllerVariable('materialize', 1.0)
            self.dockMultiEffect.SetControllerVariable('materializeDelay', 0.0)
            self.dockMultiEffect.SetControllerVariable('docked', 1.0)
        elif firstTime:
            self.dockMultiEffect = self._ReplaceShipInDock(model, None, True)
            self.dockMultiEffect.SetControllerVariable('_previousState', 1.0)
            self.dockMultiEffect.SetControllerVariable('materialize', 1.0)
            self.dockMultiEffect.SetControllerVariable('materializeDelay', 0.0)
            self.dockMultiEffect.SetControllerVariable('docked', 0.0)
        else:
            self.dockMultiEffect = self._ReplaceShipInDock(model, None)
        self.dockMultiEffect.SetParameter('docking_ship', model)
        self.dockMultiEffect.SetParameter('docking_dock', self.hangarModel)
        self.hangarModel.SetControllerVariable('isActivePlayerDock', 1.0)
        self.dockMultiEffect.SetControllerVariable('isCapital', 1.0)
        groupID = GetGroupID(typeID)
        shipClass = 0.0
        if groupID == invC.groupTitan:
            shipClass = 2.0
        elif groupID in (invC.groupDreadnought,
         invC.groupSupercarrier,
         invC.groupForceAux,
         invC.groupLancerDreadnought):
            shipClass = 1.0
        self.hangarModel.SetControllerVariable('chShipClass', shipClass)
        self.dockedShipItemID = self.playerShipItemID
        if model.boosters is not None:
            model.boosters.display = True
        self.dockMultiEffect.StartControllers()
        return model

    def OnShipCosmeticsChanged(self, ship_id, cosmetics_types):
        if self.playerShip is not None:
            uthread.new(self.cosmeticsLoader.SetCosmeticsOnShip, self.playerShip, cosmetics_types)

    @staticmethod
    def GetShipOffset(model, typeID):
        localBB = model.GetLocalBoundingBox()
        width = abs(localBB[0][2])
        return (0.0, 0.0, -2 * width)

    def GetShipCenter(self, model, typeID):
        translation = model.translationCurve.currentValue if model.translationCurve is not None else None
        modelTranslation = model.translationCurve.currentValue if model.translationCurve is not None else None
        return geo2.Vec3Add(translation or (0.0, 0.0, 0.0), modelTranslation or (0.0, 0.0, 0.0))

    def GetAnimEndPosition(self):
        return (0.0, 0.0, 0.0)

    def GetAnimStartPosition(self):
        return (0.0, 0.0, 0.0)

    def SetFlightPath(self, exit1, hallway1, hallway2, exit2, dockPos):
        pass

    def populateDocksWithInventoryShips(self, ships, scene, hangar):
        pass

    def UpdateUndockStatus(self, isUndocking):
        if self.dockMultiEffect is not None:
            self.dockMultiEffect.SetControllerVariable('docked', 1.0 - isUndocking)

    def _ReplaceShipInDock(self, model, dock, skipCleanup = False, skipAnimation = False):

        def cleanUp(hangarScene, ship, multiEffect):
            if hangarScene is None:
                return
            for param in multiEffect.parameters:
                param.object = None

            multiEffect.bindings.removeAt(-1)
            if ship is not None and ship in hangarScene.objects:
                hangarScene.objects.remove(ship)
            if multiEffect is not None and multiEffect in hangarScene.objects:
                hangarScene.objects.remove(multiEffect)

        newME = blue.resMan.LoadObject(GetGraphicFile(hConst.DOCKER_CAPITAL_MULTIEFFECT_GRAPHIC_ID))
        newExit = newME.curveSets.FindByName('docking_cs').curves.FindByName('exit_point')
        oldExit = self.dockMultiEffect.curveSets.FindByName('docking_cs').curves.FindByName('exit_point')
        newExit.value = oldExit.value
        oldME = self.dockMultiEffect
        self.dockMultiEffect = newME
        self.hangarScene.objects.append(newME)
        newME.SetControllerVariable('materialize', 1.0)
        if skipCleanup or skipAnimation:
            newME.SetControllerVariable('_previousState', 1.0)
            newME.SetControllerVariable('docked', 0.0 if skipCleanup else 1.0)
        else:
            newME.SetControllerVariable('_previousState', 0.0)
            newME.SetControllerVariable('docked', 1.0)
            newME.SetControllerVariable('materializeDelay', 4.0)
        oldME.SetControllerVariable('materialize', 0.0)
        oldShip = oldME.parameters.FindByName('docking_ship').object
        if skipAnimation:
            oldME.SetControllerVariable('_previousState', 0.0)
            oldME.StartControllers()
        if not skipCleanup:
            call_after_simtime_delay(cleanUp, 15.0, self.hangarScene, oldShip, oldME)
        return newME

    def AnimateShipEntry(self, newModel, typeID, scene = None, duration = 5.0):
        self.PlaceShip(newModel, typeID)

    def UpdateActiveShipIDs(self, typeID, itemID):
        self.playerShipItemID = itemID
        self.playerShipTypeID = typeID

    def LoadShipModel(self, itemID, typeID, playerShip = True):
        model = self._LoadSOFShipModel(itemID, typeID)
        model.name = str(itemID)
        if playerShip:
            model.FreezeHighDetailMesh()
            self.playerShipItemID = itemID
            self.playerShipTypeID = typeID
            self.SetShipDamage(itemID, model)
            self.FitTurrets(itemID, typeID, model)
        self.SetShipDirtLevel(itemID, model)
        self.SetShipKillCounter(itemID, model)
        self.SetupShipAnimation(model, typeID, itemID)
        return model

    def ProcessSkinChange(self, newModel):
        if self.playerShip is None:
            return
        if self.playerDock is not None and self.playerDock.dockMultiEffect is not None:
            self.playerDock.dockedShip = newModel
        if newModel.boosters is not None:
            newModel.boosters.display = True
        self._AddDetailsToShipModel(self.playerShipItemID, self.playerShipTypeID, newModel, playerShip=False)
        self.playerShip = newModel
        self.dockMultiEffect.SetParameter('docking_ship', newModel)
        self.dockMultiEffect.SetControllerVariable('materialize', 1.0)
        self.dockMultiEffect.SetControllerVariable('materializeDelay', 0.0)
        self.dockMultiEffect.SetControllerVariable('_previousState', 1.0)
        self.dockMultiEffect.SetControllerVariable('skinChange', 1.0)
        self.dockMultiEffect.SetControllerVariable('docked', 1.0)
        newModel.SetControllerVariable('IsWarping', 0.0)
        newModel.StartControllers()
        for curveSet in self.dockMultiEffect.curveSets:
            curveSet.Play()

        for controller in self.dockMultiEffect.controllers:
            controller.Start()

    def ProcessCamera(self, camera, newModel, typeID):
        pass

    def _shipRequiresBigDock(self, ship):
        pass

    def OnItemChangeProcessed(self, item, itemInfo):
        pass


class ModularCapitalHangarDroneBehaviour(ModularHangarDroneBehaviour):

    def SetRepairDroneCount(self, boundingRadius):
        count = int(math.ceil(boundingRadius / 60.0))
        if self.repairDroneBehaviourGroup:
            self.repairDroneBehaviourGroup.SetCount(count)
