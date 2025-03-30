#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\hangarBehaviours\modularHangarBehaviours.py
import blue
import random as rnd
import geo2
import trinity
import math
import uthread
import logging
import modularHangarBehavioursConstants as hConst
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from eve.common.script.sys.idCheckers import IsJunkLocation
from inventorycommon import const
from uthread2 import call_after_simtime_delay
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from baseHangarBehaviours import BaseHangarShipBehaviour, BaseHangarShipDroneBehaviour
from modularHangarBehavioursConstants import GetShipSizeClass, IsInLookUpTable
import evecamera
from evetypes import GetGroupID
from gametime import GetSecondsUntilSimTime
from appConst import factionAngelCartel, factionGuristasPirates
logger = logging.getLogger(__name__)

class Dock(object):

    def __init__(self, pos, rot):
        self.translation = pos
        self.rotation = rot
        self.isPlayer = False
        self.dockMultiEffect = None
        self.dockedShip = None
        self.isActive = False
        self.childObject = None
        self.dockedShipItemID = 0
        self.exitPoint = (0.0, 0.0, 0.0)
        self.hallwayPoint = (0.0, 0.0, 0.0)
        self.relativeMEExitPoint = (0.0, 0.0, 0.0)
        self.cameraExitPoint = (0.0, 0.0, 0.0)

    def Setup(self, pos, rot):
        self.translation = pos
        self.rotation = rot

    def shipDeparture(self):
        pass

    def shipDocking(self):
        pass


class ModularHangarShipBehaviour(BaseHangarShipBehaviour):

    def __init__(self):
        super(ModularHangarShipBehaviour, self).__init__()
        self.smallDocks = []
        self.bigDocks = []
        self.playerDock = None
        self.playerShipItemID = 0
        self.playerShipTypeID = 0
        self.shipOffset = (0, 0, 0)
        self.endPos = (0, 0, 0)
        self.isInitialized = False
        self.hangarScene = None
        self.reflectionProbeThread = None
        self.flightPath = {'exit1': (0.0, 0.0, 0.0),
         'hallway1': (0.0, 0.0, 0.0),
         'hallway2': (0.0, 0.0, 0.0),
         'exit2': (0.0, 0.0, 0.0)}
        self.isEnlistmentDockingEnabled = False

    def SetEnlistmentDockingEnabled(self, enabled):
        self.isEnlistmentDockingEnabled = enabled

    def SetDockingEffectGraphicID(self, graphicID):
        self.dockingEffectGraphicID = graphicID

    def SetAnchorPoint(self, hangarModel, hangarScene):
        if hangarModel is None:
            self.log.error('ModularHangarShipBehaviour.SetAnchorPoint: Setting anchor point when hangarModel is None')
            return
        self.hangarScene = hangarScene
        self._CreateDocks(hangarModel, hangarScene)

    def CleanScene(self):

        def _cleanMultiEffect(multiEffect):
            if multiEffect is not None:
                for param in multiEffect.parameters:
                    param.object = None

                multiEffect.bindings.removeAt(-1)

        def _cleanChildObject(obj):
            if obj is not None:
                obj.objects.removeAt(-1)
                for ctrlr in obj.controllers:
                    ctrlr.Stop()

                obj.controllers.removeAt(-1)

        for dock in self.smallDocks:
            dock.dockedShip = None
            _cleanChildObject(dock.childObject)
            dock.childObject = None
            _cleanMultiEffect(dock.dockMultiEffect)
            dock.dockMultiEffect = None

        for dock in self.bigDocks:
            dock.dockedShip = None
            _cleanChildObject(dock.childObject)
            dock.childObject = None
            _cleanMultiEffect(dock.dockMultiEffect)
            dock.dockMultiEffect = None

        self.GetCamera().ClearRefs()
        self.hangarScene = None
        self.playerDock = None
        self.smallDocks = None
        self.bigDocks = None
        self.flightPath = None
        self.isInitialized = False
        self.reflectionProbeThread = None

    def GetCamera(self):
        return sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_MODULARHANGAR)

    def _ReflectionProbePositionUpdateThread(self, probe):
        try:
            camera = self.GetCamera()
            while True:
                if camera is None or probe is None:
                    break
                probe.position = camera.GetZoomToPoint()
                blue.synchro.Yield()

        finally:
            self.reflectionProbeThread = None

    def PlaceReflectionProbe(self, reflectionProbe):
        if reflectionProbe:
            reflectionProbe.lockPosition = True
            if not self.reflectionProbeThread:
                self.reflectionProbeThread = uthread.new(self._ReflectionProbePositionUpdateThread, reflectionProbe)

    def _GetEnlistment(self):
        if not self.isEnlistmentDockingEnabled:
            return None
        else:
            enlistment, _, _ = sm.RemoteSvc('fwCharacterEnlistmentMgr').GetMyEnlistment()
            return enlistment or 0.0

    def _CreateDocks(self, hangarModel, hangarScene):
        enlistment = self._GetEnlistment()
        additionalSmallDocks, additionalBigDocks, smallDockSet, bigDockSet = ([],
         [],
         [],
         [])
        if enlistment is None:
            smallDockSet = hangarModel.locatorSets.FindByName(hConst.LOCATORSET_SMALL_DOCK_SHIPS)
            bigDockSet = hangarModel.locatorSets.FindByName(hConst.LOCATORSET_MEDIUM_DOCK_SHIPS)
        if enlistment is not None:
            smallDockSet = hangarModel.locatorSets.FindByName(hConst.LOCATORSET_SMALL_DEATHLESS_DOCK)
            bigDockSet = hangarModel.locatorSets.FindByName(hConst.LOCATORSET_MEDIUM_DEATHLESS_DOCK)
            if self.isEnlistmentDockingEnabled and enlistment == factionAngelCartel:
                additionalSmallDocks = hangarModel.locatorSets.FindByName(hConst.LOCATORSET_SMALL_ANGEL_DOCK)
                additionalBigDocks = hangarModel.locatorSets.FindByName(hConst.LOCATORSET_MEDIUM_ANGEL_DOCK)
            elif self.isEnlistmentDockingEnabled and enlistment == factionGuristasPirates:
                additionalSmallDocks = hangarModel.locatorSets.FindByName(hConst.LOCATORSET_SMALL_GURISTAS_DOCK)
                additionalBigDocks = hangarModel.locatorSets.FindByName(hConst.LOCATORSET_MEDIUM_GURISTAS_DOCK)
            if hasattr(additionalSmallDocks, 'locators'):
                for each in additionalSmallDocks.locators:
                    smallDockSet.locators.append(each)

            if hasattr(additionalBigDocks, 'locators'):
                for each in additionalBigDocks.locators:
                    bigDockSet.locators.append(each)

        hallwayLocatorSetName = hConst.LOCATORSET_HALLWAY_POINTS
        if smallDockSet is None or bigDockSet is None:
            self.log.error('ModularHangarShipBehaviour.SetAnchorPoint: not all required LocatorSets are defined.')
            return
        smallDockObjects = []
        smallDockObjectPosTuples = []
        bigDockObjects = []
        bigDockObjectPosTuples = []
        try:
            i = 0
            containerName = hConst.LOCATORSET_SMALL_DOCK_SHIPS
            for container in (cont for cont in hangarModel.effectChildren if cont.name == containerName or cont.name == containerName + '_potato'):
                for each in container.objects:
                    smallDockObjects.append(each)
                    pos = each.objects.FindByName('Hull').translation
                    smallDockObjectPosTuples.append((pos[0],
                     pos[1],
                     pos[2],
                     i))
                    i = i + 1

            i = 0
            for container in (cont for cont in hangarModel.effectChildren if cont.name == hConst.LOCATORSET_MEDIUM_DOCK_SHIPS):
                for each in container.objects:
                    bigDockObjects.append(each)
                    pos = each.objects.FindByName('Hull').translation
                    bigDockObjectPosTuples.append((pos[0],
                     pos[1],
                     pos[2],
                     i))
                    i = i + 1

        except AttributeError:
            self.log.error("modularHangarShipBehaviour._CreateDocks: can't find child objects")
            return

        def SetExitPoint(dock, shipPos, platformRotation):
            exitIndex = hangarModel.GetCloseLocatorIndex(shipPos, exitPointSetName)
            exitPos = hangarModel.GetLocatorPositionFromSet(exitIndex, True, exitPointSetName)
            relativePos = geo2.Subtract(exitPos, shipPos)
            relativePosRotated = geo2.QuaternionTransformVector(geo2.QuaternionInverse(platformRotation), relativePos)
            dock.relativeMEExitPoint = (relativePosRotated[0],
             relativePosRotated[1],
             relativePosRotated[2],
             0.0)
            return exitPos

        def GetClosestDockObject(isSmall, location):
            target = -1
            bestDist = 100
            dock = None
            if isSmall:
                for dockObj in smallDockObjectPosTuples:
                    x, y, z, index = dockObj
                    dist = geo2.Vec3DistanceSq(location, (x, y, z))
                    if dist < bestDist:
                        target = index
                        bestDist = dist

                if target != -1:
                    dock = smallDockObjects[target]
            else:
                for dockObj in bigDockObjectPosTuples:
                    x, y, z, index = dockObj
                    dist = geo2.Vec3DistanceSq(location, (x, y, z))
                    if dist < bestDist:
                        target = index
                        bestDist = dist

                if target != -1:
                    dock = bigDockObjects[target]
            if target is -1:
                return
            return dock

        def CreateDocks(locSet, setToAddTo, isSmall):
            for locator in locSet.locators:
                pos = locator[0]
                rot = locator[1]
                potentialChildObject = GetClosestDockObject(isSmall, pos)
                if potentialChildObject is None:
                    continue
                dock = Dock(pos, rot)
                dock.exitPoint = SetExitPoint(dock, pos, rot)
                cameraExitLocatorIndex = hangarModel.GetCloseLocatorIndex(pos, cameraExitPointSetName)
                dock.cameraExitPoint = hangarModel.GetLocatorPositionFromSet(cameraExitLocatorIndex, True, cameraExitPointSetName)
                dock.childObject = potentialChildObject
                hallwayLocatorIndex = hangarModel.GetCloseLocatorIndex(dock.cameraExitPoint, hallwayLocatorSetName)
                dock.hallwayPoint = hangarModel.GetLocatorPositionFromSet(hallwayLocatorIndex, True, hallwayLocatorSetName)
                setToAddTo.append(dock)

        exitPointSetName = hConst.LOCATORSET_SMALL_DOCK_EXITS
        cameraExitPointSetName = hConst.LOCATORSET_SMALL_DOCK_CAMERA_EXITS
        CreateDocks(smallDockSet, self.smallDocks, True)
        exitPointSetName = hConst.LOCATORSET_MEDIUM_DOCK_EXITS
        cameraExitPointSetName = hConst.LOCATORSET_MEDIUM_DOCK_CAMERA_EXITS
        CreateDocks(bigDockSet, self.bigDocks, False)

    def IsInitialized(self):
        return self.isInitialized

    def _GetPlayerDock(self):
        return self.playerDock

    def GetAllDockedShips(self):
        ships = []
        for each in self.smallDocks:
            if each.dockedShip is not None:
                ships.append(each.dockedShip)

        for each in self.bigDocks:
            if each.dockedShip is not None:
                ships.append(each.dockedShip)

        return ships

    def OnItemChangeProcessed(self, item, itemInfo):
        if item.itemID is None or item.typeID is None:
            return
        isT3cItem = False
        if item.groupID in const.subsystemSlotGroupIDs or item.groupID == const.groupStrategicCruiser:
            isT3cItem = True
        if item.flagID == const.flagHangar and item.quantity < 0:
            if IsJunkLocation(item.locationID):
                self._RemoveShipIfItsInTheScene(item.itemID, item.typeID)
            elif const.categoryTrading in itemInfo and not isT3cItem:
                self._SpawnANewShipIfThereIsRoom(item.itemID, item.typeID)
        elif item.flagID == const.flagJunkyardTrashed:
            self._RemoveShipIfItsInTheScene(item.itemID, item.typeID)

    def _ConfigureShipTransform(self, ship, offset, dock):
        platformRotation = trinity.Tr2CurveConstant()
        platformRotation.value = dock.rotation
        shipTranslation = trinity.Tr2CurveCombiner()
        platformTranslation = trinity.Tr2TranslationAdapter()
        platformTranslation.value = geo2.Add(offset, dock.translation)
        multiEffectTranslation = trinity.Tr2TranslationAdapter()
        multiEffectTranslation.rotationOffset = dock.rotation
        shipTranslation.curves.append(platformTranslation)
        shipTranslation.curves.append(multiEffectTranslation)
        displayOffset = ship.locatorSets.FindByName(hConst.LOCATORSET_DISPLAY_OFFSET)
        if displayOffset is not None and len(displayOffset.locators) == 1:
            displayOffsetCurve = trinity.Tr2TranslationAdapter()
            displayOffsetCurve.value = displayOffset.locators[0][0]
            displayOffsetCurve.rotationOffset = dock.rotation
            shipTranslation.curves.append(displayOffsetCurve)
        ship.translationCurve = shipTranslation
        ship.rotationCurve = platformRotation
        ship.modelRotationCurve = trinity.Tr2RotationAdapter()
        ship.modelTranslationCurve = trinity.Tr2TranslationAdapter()

    def _SpawnANewShipIfThereIsRoom(self, itemID, typeID):
        groupID = GetGroupID(typeID)
        if not IsInLookUpTable(groupID):
            return
        sizeClass = GetShipSizeClass(groupID)
        newDock = None
        if sizeClass > 2:
            return
        if sizeClass < 2:
            emptyDocks = [ dock for dock in self.smallDocks if not dock.isActive ]
            if len(emptyDocks) > 0:
                newDock = rnd.choice(emptyDocks)
        else:
            emptyDocks = [ dock for dock in self.bigDocks if not dock.isActive ]
            if len(emptyDocks) > 0:
                newDock = rnd.choice(emptyDocks)
        if newDock is None:
            return
        model = self.LoadShipModel(itemID, typeID, playerShip=False)
        if model is None:
            return
        newDock.dockedShipItemID = itemID
        self._ReplaceShipInDock(model, newDock, makeActiveShip=False)
        self._WaitForShipBoundingBox(model)
        shipOffset = geo2.QuaternionTransformVector(newDock.rotation, self.GetShipOffset(model, typeID))
        self._ConfigureShipTransform(model, shipOffset, newDock)
        newDock.dockedShip = model
        newDock.isActive = True
        if model.boosters is not None:
            model.boosters.display = True
        if newDock.dockMultiEffect is not None:
            newDock.dockMultiEffect.SetParameter('docking_ship', model)
            newDock.dockMultiEffect.SetControllerVariable('materializeDelay', 0.75)
            newDock.dockMultiEffect.SetControllerVariable('docked', 1.0)
            newDock.dockMultiEffect.StartControllers()
        self.hangarScene.objects.append(model)

    def _RemoveShipIfItsInTheScene(self, itemID, typeID):
        if self.playerShipItemID == itemID:
            return False
        groupID = GetGroupID(typeID)
        sizeClass = GetShipSizeClass(groupID)
        if sizeClass < 2:
            dock = next((dock for dock in self.smallDocks if dock.dockedShipItemID == itemID), None)
        else:
            dock = next((dock for dock in self.bigDocks if dock.dockedShipItemID == itemID), None)
        if dock is None:
            return False

        def cleanUp(hangarScene, ship, multiEffect):
            if hangarScene is None:
                return
            if ship is not None and ship in hangarScene.objects:
                hangarScene.objects.remove(ship)
            if multiEffect is not None and multiEffect in hangarScene.objects:
                for param in multiEffect.parameters:
                    param.object = None

                multiEffect.bindings.removeAt(-1)
                hangarScene.objects.remove(multiEffect)

        oldME = dock.dockMultiEffect
        oldME.SetControllerVariable('materialize', 0.0)
        oldME.SetControllerVariable('docked', 0.0)
        dock.childObject.SetControllerVariable('isDocked', 0.0)
        oldShip = oldME.parameters.FindByName('docking_ship').object
        dock.dockMultiEffect = None
        dock.childObject.SetControllerVariable('isDocked', 0.0)
        dock.childObject.SetControllerVariable('docked', 0.0)
        dock.dockedShip = None
        dock.isActive = False
        dock.dockedShipItemID = 0
        call_after_simtime_delay(cleanUp, 15.0, self.hangarScene, oldShip, oldME)

    def _FindPLayerShipInADock(self, sizeClass):
        if sizeClass < 2:
            dock = next((dock for dock in self.smallDocks if dock.dockedShipItemID == self.playerShipItemID), None)
        else:
            dock = next((dock for dock in self.bigDocks if dock.dockedShipItemID == self.playerShipItemID), None)
        return dock

    def _WaitForShipBoundingBox(self, model):
        if model is None:
            return
        try:
            counter = 0
            maxYields = 25
            while counter < maxYields:
                modelBB = model.GetLocalBoundingBox()
                if modelBB[0][0] != 0.0 and modelBB[0][2] != 0.0:
                    return
                counter = counter + 1
                blue.synchro.Yield()

        except IndexError:
            self.log.error('modularHangarShipBehaviour.populateDocksWithInventoryShips: bounding box missconfigured')

    def PrepareFSB(self, vfxMultiEffect):
        self.playerDock.dockMultiEffect.SetParameter('docking_ship', None)
        p = self.playerDock.cameraExitPoint
        self.SetFlightPath(p, p, p, p, p)
        self.GetCamera().SkipFlight()
        vfxMultiEffect.SetParameter('activeDock', self.playerDock.childObject)
        self.playerDock.childObject.SetControllerVariable('isActivePlayerDock', 0.0)
        self.playerDock.childObject.SetControllerVariable('isDocked', 1.0)
        self.playerDock.childObject.StartControllers()
        vfxMultiEffect.StartControllers()
        for ship in (obj for obj in self.hangarScene.objects if type(obj) == trinity.EveShip2):
            ship.SetControllerVariable('lightRigOn', 0.0)

    def FinishFSB(self):
        self.playerDock.dockMultiEffect.SetParameter('docking_ship', self.playerDock.dockedShip)
        self.playerDock.dockMultiEffect.SetControllerVariable('materialize', 1.0)
        self.playerDock.dockMultiEffect.SetControllerVariable('_previousState', 1.0)
        self.playerDock.dockMultiEffect.SetControllerVariable('materializeDelay', 0.0)
        self.playerDock.dockMultiEffect.StartControllers()
        self.GetCamera().zoomFactor = 0.2
        self.GetCamera().zoomTarget = 0.2
        for ship in (obj for obj in self.hangarScene.objects if type(obj) == trinity.EveShip2):
            ship.SetControllerVariable('lightRigOn', 1.0)

    def GetActiveDock(self):
        if self.playerDock is not None:
            return self.playerDock.childObject

    def PlaceShip(self, itemID, typeID, skipDockingAnimation = False):
        groupID = GetGroupID(typeID)
        sizeClass = GetShipSizeClass(groupID)
        firstDocking = self.playerDock is None
        foundDock = self._FindPLayerShipInADock(sizeClass)
        if foundDock is None:
            if firstDocking:
                if sizeClass < 2:
                    dock = next((dock for dock in self.smallDocks if dock.isPlayer), None)
                    unusedDock = next((dock for dock in self.bigDocks if dock.isPlayer), None)
                    if unusedDock is not None:
                        unusedDock.isPlayer = False
                        unusedDock.isActive = unusedDock.dockedShipItemID is not 0
                else:
                    dock = next((dock for dock in self.bigDocks if dock.isPlayer), None)
                    unusedDock = next((dock for dock in self.smallDocks if dock.isPlayer), None)
                    if unusedDock is not None:
                        unusedDock.isPlayer = False
                        unusedDock.isActive = unusedDock.dockedShipItemID is not 0
                if dock is None:
                    dock = rnd.choice(self.smallDocks) if sizeClass < 2 else rnd.choice(self.bigDocks)
                dock.dockedShipItemID = self.playerShipItemID
                model = self.LoadShipModel(itemID, typeID, True)
                self.playerDock = dock
                self._ReplaceShipInDock(model, dock)
                if dock.dockMultiEffect is not None:
                    dock.dockMultiEffect.SetControllerVariable('materialize', 1.0)
                    dock.dockMultiEffect.SetControllerVariable('_previousState', 1.0)
                    dock.dockMultiEffect.SetControllerVariable('materializeDelay', 0.0)
                    dock.dockMultiEffect.SetControllerVariable('docked', 1.0 if skipDockingAnimation else 0.0)
                    dock.dockMultiEffect.StartControllers()
                    if skipDockingAnimation:
                        dock.childObject.SetControllerVariable('isActivePlayerDock', 0.0)
                        dock.childObject.SetControllerVariable('isDocked', 1.0)
                        dock.childObject.StartControllers()
                        call_after_simtime_delay(dock.childObject.SetControllerVariable, 1.0, 'isActivePlayerDock', 1.0)
            else:
                try:
                    if sizeClass < 2:
                        emptyDocks = [ dock for dock in self.smallDocks if not dock.isActive ]
                        if len(emptyDocks) > 0:
                            newDock = rnd.choice(emptyDocks)
                        else:
                            newDock = rnd.choice([ dock for dock in self.smallDocks if not dock.isPlayer ])
                    else:
                        emptyDocks = [ dock for dock in self.bigDocks if not dock.isActive ]
                        if len(emptyDocks) > 0:
                            newDock = rnd.choice(emptyDocks)
                        else:
                            newDock = rnd.choice([ dock for dock in self.bigDocks if not dock.isPlayer ])
                except IndexError:
                    newDock = rnd.choice(self.smallDocks) if sizeClass < 2 else rnd.choice(self.bigDocks)

                self.playerDock.isPlayer = False
                newDock.isPlayer = True
                newDock.dockedShipItemID = itemID
                oldDock = self.playerDock
                if oldDock.childObject is not None:
                    oldDock.childObject.SetControllerVariable('isActivePlayerDock', 0.0)
                model = self.LoadShipModel(itemID, typeID, True)
                oldShip = newDock.dockedShip
                oldME = newDock.dockMultiEffect
                self._WaitForShipBoundingBox(model)
                self.playerDock = self._ReplaceShipInDock(model, newDock, skipMaterialization=skipDockingAnimation)
                shipOffset = geo2.QuaternionTransformVector(newDock.rotation, self.GetShipOffset(model, typeID))
                if not skipDockingAnimation:
                    self.SetFlightPath(oldDock.cameraExitPoint, oldDock.hallwayPoint, newDock.hallwayPoint, newDock.cameraExitPoint, geo2.Vec3Add(newDock.translation, shipOffset))
                dist = geo2.Vec3DistanceSq(oldDock.cameraExitPoint, newDock.cameraExitPoint)
                if not self.GetCamera().IsPointWithinViewAngle(newDock.translation, 75) and dist > 1000000 or skipDockingAnimation:
                    if oldShip is not None and oldShip in self.hangarScene.objects:
                        self.hangarScene.objects.remove(oldShip)
                    if oldME is not None and oldME in self.hangarScene.objects:
                        self.hangarScene.objects.remove(oldME)
                    newDock.dockMultiEffect.SetControllerVariable('materialize', 1.0)
                    newDock.dockMultiEffect.SetControllerVariable('_previousState', 1.0)
                    newDock.dockMultiEffect.SetControllerVariable('materializeDelay', 0.0)
                    newDock.childObject.SetControllerVariable('isDocked', 1.0 if skipDockingAnimation else 0.0)
                    newDock.childObject.StartControllers()
                    newDock.dockMultiEffect.SetControllerVariable('docked', 1.0 if skipDockingAnimation else 0.0)
                    newDock.dockMultiEffect.StartControllers()
        else:
            if foundDock == self.playerDock:
                if itemID == self.playerDock.dockedShipItemID:
                    if skipDockingAnimation:
                        docker = self.playerDock.dockMultiEffect
                        docker.SetControllerVariable('docked', 1.0 if skipDockingAnimation else 0.0)
                        docker.StartControllers()
                        self.playerDock.childObject.SetControllerVariable('isActivePlayerDock', 0.0)
                        self.playerDock.childObject.SetControllerVariable('isDocked', 1.0)
                        self.playerDock.childObject.StartControllers()
                        call_after_simtime_delay(self.playerDock.childObject.SetControllerVariable, 1.0, 'isActivePlayerDock', 1.0)
                    return self.playerDock.dockedShip
                model = self.LoadShipModel(itemID, typeID, True)
                self._ReplaceShipInDock(model, self.playerDock)
                self._WaitForShipBoundingBox(model)
                self.shipOffset = geo2.QuaternionTransformVector(self.playerDock.rotation, self.GetShipOffset(model, typeID))
                self._ConfigureShipTransform(model, self.shipOffset, self.playerDock)
                self.playerDock.dockedShip = model
                self.GetCamera().SetIsChangingSkin()
                self.GetCamera().SetShip(model, typeID, changingShip=False)
                self.GetCamera().SetCurrentShipSizeClass(sizeClass)
                self._AddDetailsToShipModel(itemID, typeID, model, playerShip=True)
                self.hangarScene.objects.append(model)
                if self.playerDock.dockMultiEffect is not None:
                    self.playerDock.dockMultiEffect.SetParameter('docking_ship', model)
                    self.playerDock.dockMultiEffect.SetParameter('docking_dock', self.playerDock.childObject)
                    self.playerDock.dockMultiEffect.StartControllers()
                return model
            if firstDocking:
                smalldock = next((dock for dock in self.smallDocks if dock.isPlayer), None)
                smalldock.isPlayer = False
                smalldock.isActive = False
                bigdock = next((dock for dock in self.bigDocks if dock.isPlayer), None)
                bigdock.isPlayer = False
                bigdock.isActive = False
                if foundDock.childObject is not None:
                    foundDock.childObject.SetControllerVariable('isActivePlayerDock', 1.0)
                if foundDock.dockedShip is not None:
                    foundDock.dockedShip.SetControllerVariable('isActivePlayerDock', 1.0)
                self.playerDock = foundDock
                foundDock.isActive = True
                foundDock.isPlayer = True
                while foundDock.dockedShip is None:
                    blue.synchro.Yield()

                foundDock.dockMultiEffect.SetControllerVariable('_previousState', 1.0)
                foundDock.dockMultiEffect.SetControllerVariable('docked', 1.0 if skipDockingAnimation else 0.0)
                self.GetCamera().SetShip(foundDock.dockedShip, typeID)
                self.GetCamera().SetCurrentShipSizeClass(sizeClass)
                foundDock.dockMultiEffect.StartControllers()
                sm.ScatterEvent('OnHangarGoingToShip', foundDock.dockedShip)
                self._AddDetailsToShipModel(itemID, typeID, foundDock.dockedShip, playerShip=True)
                if skipDockingAnimation:
                    foundDock.childObject.SetControllerVariable('isActivePlayerDock', 0.0)
                    foundDock.childObject.SetControllerVariable('isDocked', 1.0)
                    call_after_simtime_delay(foundDock.childObject.SetControllerVariable, 1.0, 'isActivePlayerDock', 1.0)
                return foundDock.dockedShip
            if self.playerDock.childObject is not None:
                self.playerDock.childObject.SetControllerVariable('isActivePlayerDock', 0.0)
            if self.playerDock.dockedShip is not None:
                self.playerDock.dockedShip.SetControllerVariable('isActivePlayerDock', 0.0)
            if foundDock.childObject is not None:
                foundDock.childObject.SetControllerVariable('isActivePlayerDock', 1.0)
            if foundDock.dockedShip is not None:
                foundDock.dockedShip.SetControllerVariable('isActivePlayerDock', 1.0)
            self.playerDock.isPlayer = False
            foundDock.isPlayer = True
            self.GetCamera().SetShip(foundDock.dockedShip, typeID)
            self.GetCamera().SetCurrentShipSizeClass(sizeClass)
            shipOffset = geo2.QuaternionTransformVector(foundDock.rotation, self.GetShipOffset(foundDock.dockedShip, typeID))
            self.SetFlightPath(self.playerDock.cameraExitPoint, self.playerDock.hallwayPoint, foundDock.hallwayPoint, foundDock.cameraExitPoint, geo2.Vec3Add(foundDock.translation, shipOffset))
            self.playerDock = foundDock
            self._AddDetailsToShipModel(itemID, typeID, foundDock.dockedShip, playerShip=True)
            sm.ScatterEvent('OnHangarGoingToShip', foundDock.dockedShip)
            return foundDock.dockedShip
        if self.playerDock is None or model is None:
            self.log.error('ModularHangarShipBehaviour.PlaceShip: Dock missconfigured')
            return
        self.playerDock.isActive = True
        self._WaitForShipBoundingBox(model)
        self.shipOffset = geo2.QuaternionTransformVector(self.playerDock.rotation, self.GetShipOffset(model, typeID))
        self._ConfigureShipTransform(model, self.shipOffset, self.playerDock)
        self.playerDock.dockedShip = model
        self.GetCamera().SetShip(model, typeID)
        self.GetCamera().SetCurrentShipSizeClass(sizeClass)
        if model.boosters is not None:
            model.boosters.display = True
        self._AddDetailsToShipModel(itemID, typeID, model, playerShip=True)
        if self.playerDock.dockMultiEffect is not None:
            self.playerDock.dockMultiEffect.SetParameter('docking_ship', model)
            self.playerDock.dockMultiEffect.SetParameter('docking_dock', self.playerDock.childObject)
            self.playerDock.dockMultiEffect.StartControllers()
        sm.ScatterEvent('OnHangarGoingToShip', model)
        self.hangarScene.objects.append(model)
        return model

    def GetShipOffset(self, model, typeID):
        if model is None:
            return (0.0, 0.0, 0.0)
        localBB = model.GetLocalBoundingBox()
        height = abs(localBB[0][0])
        width = abs(localBB[0][2])
        groupID = GetGroupID(typeID)
        sizeClass = GetShipSizeClass(groupID)
        if sizeClass < 2:
            shipOffset = hConst.SMALL_PLATFORM_SHIP_PLACEMENT_OFFSET
            return (0.0, shipOffset[2] + shipOffset[3] * height, shipOffset[0] + shipOffset[1] * width)
        shipOffset = hConst.MEDIUM_PLATFORM_SHIP_PLACEMENT_OFFSET
        return (0.0, shipOffset[2] + shipOffset[3] * height, shipOffset[0] + shipOffset[1] * width)

    def GetShipCenter(self, model, typeID):
        translation = model.translationCurve.currentValue if model.translationCurve is not None else None
        modelTranslation = model.translationCurve.currentValue if model.translationCurve is not None else None
        return geo2.Vec3Add(translation or (0.0, 0.0, 0.0), modelTranslation or (0.0, 0.0, 0.0))

    def GetAnimEndPosition(self):
        return (0.0, 0.0, 0.0)

    def GetAnimStartPosition(self):
        return (0.0, 0.0, 0.0)

    def _GetSizeClass(self, ship):
        assignedGroup = GetShipSizeClass(ship.groupID)
        if assignedGroup is None:
            return 1
        return assignedGroup

    def _GetDockingMultieffect(self):
        return blue.resMan.LoadObject(GetGraphicFile(self.dockingEffectGraphicID))

    def populateDocksWithInventoryShips(self, ships, scene, hangar):
        rnd.shuffle(ships)
        bigShips = []
        smallShips = []
        capitalShips = []
        for ship in ships:
            sizeClass = self._GetSizeClass(ship)
            if sizeClass < 2:
                smallShips.append(ship)
            elif sizeClass < 3:
                bigShips.append(ship)
            else:
                capitalShips.append(ship)

        smallDock = rnd.choice(self.smallDocks)
        bigDock = rnd.choice(self.bigDocks)
        smallDock.isPlayer = True
        smallDock.isActive = True
        bigDock.isPlayer = True
        bigDock.isActive = True

        def _placeShipInDock(ship, dock):
            multiEffect = self._GetDockingMultieffect()
            if multiEffect is None:
                return self.log.error('modularHangarShipBehaviour.populateDocksWithInventoryShips: MultiEffect broken')
            multiEffect.SetParameter('docking_dock', dock.childObject)
            try:
                curveSet = multiEffect.curveSets.FindByName('docking_cs')
                exitPoint = curveSet.curves.FindByName('exit_point')
                exitPoint.value = dock.relativeMEExitPoint
            except AttributeError:
                self.log.error('modularHangarShipBehaviour.populateDocksWithInventoryShips: MultiEffect Attributes broken')

            dock.dockMultiEffect = multiEffect
            scene.objects.append(multiEffect)
            model = self.LoadShipModel(ship.itemID, ship.typeID, False)
            self._WaitForShipBoundingBox(model)
            shipOffset = geo2.QuaternionTransformVector(dock.rotation, self.GetShipOffset(model, ship.typeID))
            self._ConfigureShipTransform(model, shipOffset, dock)
            scene.objects.append(model)
            dock.dockedShip = model
            dock.dockMultiEffect.SetParameter('docking_ship', model)
            dock.dockMultiEffect.SetControllerVariable('_previousState', 1.0)
            dock.dockMultiEffect.SetControllerVariable('docked', 1.0)
            dock.childObject.SetControllerVariable('isDocked', 1.0)
            dock.childObject.StartControllers()
            if ship.itemID != self.playerShipItemID:
                dock.dockMultiEffect.StartControllers()
            dock.dockMultiEffect.name = dock.dockMultiEffect.name + '_' + model.name

        for ship in smallShips:
            if sum((d.isActive is False for d in self.smallDocks)) == 0:
                break
            if ship.itemID == self.playerShipItemID:
                for smallDock in self.smallDocks:
                    if smallDock.isPlayer:
                        dock = smallDock

            else:
                dock = rnd.choice([ dock for dock in self.smallDocks if not dock.isActive ])
            dock.isActive = True
            dock.dockedShipItemID = ship.itemID
            if dock.isPlayer:
                _placeShipInDock(ship, dock)
            else:
                uthread.new(_placeShipInDock, ship, dock)

        for ship in bigShips:
            if sum((d.isActive is False for d in self.bigDocks)) == 0:
                break
            if ship.itemID == self.playerShipItemID:
                for bigDock in self.bigDocks:
                    if bigDock.isPlayer:
                        dock = bigDock

            else:
                dock = rnd.choice([ dock for dock in self.bigDocks if not dock.isActive ])
            dock.isActive = True
            dock.dockedShipItemID = ship.itemID
            if dock.isPlayer:
                _placeShipInDock(ship, dock)
            else:
                uthread.new(_placeShipInDock, ship, dock)

        def _LoadAndPlaceCapitalShip(ship):
            positionLocator = hangar.locatorSets.FindByName(hConst.LOCATORSET_CAPITAL_SHIP)
            if positionLocator is None or len(positionLocator.locators) != 1:
                self.log.info('ModularHangarShipBehaviour.populateDocksWithInventoryShips: capital locator missing')
                return
            model = self.LoadShipModel(ship.itemID, ship.typeID, False)
            if model is None:
                return
            self._WaitForShipBoundingBox(model)
            position = positionLocator.locators[0][0]
            rotation = positionLocator.locators[0][1]
            shipTranslation = trinity.Tr2TranslationAdapter()
            shipBBOffset = self.GetShipOffset(model, ship.typeID)
            shipTranslation.value = geo2.Vec3Add(position, shipBBOffset)
            shipRotation = trinity.Tr2CurveConstant()
            shipRotation.value = rotation
            model.translationCurve = shipTranslation
            model.rotationCurve = shipRotation
            scene.objects.append(model)

        if len(capitalShips) > 0:
            ship = rnd.choice(capitalShips)
            uthread.new(_LoadAndPlaceCapitalShip, ship)
        self.isInitialized = True

    def SetFlightPath(self, exit1, hallway1, hallway2, exit2, dockPos):
        self.flightPath['exit1'] = exit1
        self.flightPath['exit2'] = exit2
        self.flightPath['hallway1'] = hallway1
        self.flightPath['hallway2'] = hallway2
        self.GetCamera().SetFlightValueMap(exit1, hallway1, hallway2, exit2, dockPos)

    def UpdateStructureState(self, hangarViewState, hangarModel):
        try:
            if hangarViewState.upkeepState is not None:
                hangarModel.SetControllerVariable('upkeepState', hangarViewState.upkeepState - 1 or 0)
            if hangarViewState.operatingState is not None:
                if hangarViewState.operatingState == 102:
                    operatingState = 0
                else:
                    operatingState = hangarViewState.operatingState - 109
                hangarModel.SetControllerVariable('operatingState', operatingState)
            hangarModel.SetControllerVariable('hangarShieldDamage', hangarViewState.damageState[0] or 1.0)
            hangarModel.SetControllerVariable('hangarArmorDamage', hangarViewState.damageState[1] or 1.0)
            hangarModel.SetControllerVariable('hangarHullDamage', hangarViewState.damageState[2] or 1.0)
            if hangarViewState.timerProgress is not None and type(hangarViewState.timerProgress) == float:
                timerProgress = 1 + math.floor(hangarViewState.timerProgress * 15) or 0
                hangarModel.SetControllerVariable('timerProgress', timerProgress)
            hangarModel.SetControllerVariable('isRepairing', float(hangarViewState.timerIsProgressing) or 0)
            hangarModel.SetControllerVariable('isDamaged', float(hangarViewState.timerIsPaused) or 0)
            timeRemainingSec = GetSecondsUntilSimTime(hangarViewState.timerEndAt or 0)
            hangarModel.SetControllerVariable('remainingTime', timeRemainingSec or 0)
        except TypeError:
            self.log.error('modularHangarBehaviours.UpdateStructureState hangarViewState attribute error')

    def UpdateUndockStatus(self, isUndocking):
        dock = self._GetPlayerDock()
        if dock is not None and dock.dockMultiEffect is not None:
            dock.dockMultiEffect.SetControllerVariable('docked', 1.0 - isUndocking)

    def _ReplaceShipInDock(self, model, dock, skipCleanup = False, makeActiveShip = True, skipMaterialization = False):

        def cleanUp(hangarScene, ship, multiEffect):
            for param in multiEffect.parameters:
                param.object = None

            multiEffect.bindings.removeAt(-1)
            if ship is not None and ship in hangarScene.objects:
                hangarScene.objects.remove(ship)
            if multiEffect is not None and multiEffect in hangarScene.objects:
                hangarScene.objects.remove(multiEffect)

        if self.playerDock is None:
            return
        multiEffect = self._GetDockingMultieffect()
        multiEffect.name = multiEffect.name + '_' + model.name
        if dock.dockMultiEffect is None:
            if multiEffect is None:
                return self.log.error('modularHangarShipBehaviour._ReplaceShipInDock: MultiEffect broken')
            multiEffect.SetParameter('docking_dock', dock.childObject)
            curveSet = multiEffect.curveSets.FindByName('docking_cs')
            exitPoint = curveSet.curves.FindByName('exit_point')
            exitPoint.value = dock.relativeMEExitPoint
        else:
            newExit = multiEffect.curveSets.FindByName('docking_cs').curves.FindByName('exit_point')
            oldExit = dock.dockMultiEffect.curveSets.FindByName('docking_cs').curves.FindByName('exit_point')
            newExit.value = oldExit.value
            oldME = dock.dockMultiEffect
            multiEffect.SetParameter('docking_dock', dock.childObject)
            oldME.SetControllerVariable('materialize', 0.0)
            if skipMaterialization:
                oldME.SetControllerVariable('_previousState', 0.0)
                oldME.StartControllers()
            oldShip = oldME.parameters.FindByName('docking_ship').object
            if not skipCleanup:
                call_after_simtime_delay(cleanUp, 15.0, self.hangarScene, oldShip, oldME)
        dock.dockMultiEffect = multiEffect
        self.hangarScene.objects.append(multiEffect)
        multiEffect.SetControllerVariable('materialize', 1.0)
        multiEffect.SetControllerVariable('_previousState', 1.0 if skipMaterialization else 0.0)
        multiEffect.SetControllerVariable('docked', 1.0)
        multiEffect.SetControllerVariable('materializeDelay', 2.75)
        if dock.childObject is not None and makeActiveShip:
            call_after_simtime_delay(dock.childObject.SetControllerVariable, 0.1, 'isActivePlayerDock', 1.0)
        return dock

    def AnimateShipEntry(self, newModel, typeID, scene = None, duration = 5.0):
        pass

    def UpdateActiveShipIDs(self, typeID, itemID):
        self.playerShipItemID = itemID
        self.playerShipTypeID = typeID

    def OnShipCosmeticsChanged(self, ship_id, cosmetics_types):
        if self.smallDocks:
            for each in (dock for dock in self.smallDocks):
                if each.dockedShip is not None:
                    enabledCosmetics = sm.GetService('cosmeticsSvc').get_enabled_ship_cosmetics(each.dockedShipItemID, forceRefresh=False)
                    uthread.new(self.cosmeticsLoader.SetCosmeticsOnShip, each.dockedShip, enabledCosmetics)

        if self.bigDocks:
            for each in (dock for dock in self.bigDocks):
                if each.dockedShip is not None:
                    enabledCosmetics = sm.GetService('cosmeticsSvc').get_enabled_ship_cosmetics(each.dockedShipItemID, forceRefresh=False)
                    uthread.new(self.cosmeticsLoader.SetCosmeticsOnShip, each.dockedShip, enabledCosmetics)

    def OnSessionChanged(self, _isremote, _session, change):
        if 'corpid' or 'allianceid' in change:
            enabledCosmetics = sm.GetService('cosmeticsSvc').get_enabled_ship_cosmetics(session.shipid)
            self.OnShipCosmeticsChanged(session.shipid, enabledCosmetics)

    def _AddDetailsToShipModel(self, itemID, typeID, model, playerShip = False, skipSetupAnimation = False):
        try:
            if model is None:
                return
            if playerShip:
                self.SetShipDamage(itemID, model)
                self.FitTurrets(itemID, typeID, model)
                self.SetShipKillCounter(itemID, model)
                self.SetShipDirtLevel(itemID, model)
            if not skipSetupAnimation:
                self.SetupShipAnimation(model, typeID, itemID)
            enabledCosmetics = sm.GetService('cosmeticsSvc').get_enabled_ship_cosmetics(itemID, forceRefresh=True)
            if enabledCosmetics is not None:
                uthread.new(self.cosmeticsLoader.SetCosmeticsOnShip, model, enabledCosmetics)
        except RuntimeError:
            self.log.error('modularHangarBehaviours._AddDetailsToShipModel failed to get dogmaItem')

    def LoadShipModel(self, itemID, typeID, playerShip = False, skipSetupAnimation = False):
        model = self._LoadSOFShipModel(itemID, typeID)
        if model is not None:
            model.name = str(itemID)
        if playerShip:
            self.playerShipItemID = itemID
            self.playerShipTypeID = typeID
        if hasattr(model, 'boosters') and model.boosters is not None:
            model.boosters.display = True
        self._AddDetailsToShipModel(itemID, typeID, model, playerShip=playerShip, skipSetupAnimation=skipSetupAnimation)
        return model

    def OnShipsRepaired(self, itemIDs):
        for each in (dock for dock in self.smallDocks if dock.dockedShipItemID in itemIDs):
            each.dockMultiEffect.SetControllerVariable('isRepairing', 1.0)

        for each in (dock for dock in self.bigDocks if dock.dockedShipItemID in itemIDs):
            each.dockMultiEffect.SetControllerVariable('isRepairing', 1.0)

    def ProcessSkinChange(self, newModel):
        if self.playerDock is not None and self.playerDock.dockMultiEffect is not None:
            self.playerDock.dockedShip = newModel
        else:
            return
        if newModel.boosters is not None:
            newModel.boosters.display = True
        self.GetCamera().SetIsChangingSkin()
        self.GetCamera().SetShip(newModel, self.playerShipTypeID, changingShip=False)
        self._AddDetailsToShipModel(self.playerShipItemID, self.playerShipTypeID, newModel, playerShip=True)
        self.playerDock.dockMultiEffect.SetParameter('docking_ship', newModel)
        self.playerDock.dockMultiEffect.SetControllerVariable('materialize', 1.0)
        self.playerDock.dockMultiEffect.SetControllerVariable('materializeDelay', 0.0)
        self.playerDock.dockMultiEffect.SetControllerVariable('_previousState', 1.0)
        self.playerDock.dockMultiEffect.SetControllerVariable('skinChange', 1.0)
        self.playerDock.dockMultiEffect.SetControllerVariable('docked', 1.0)
        newModel.StartControllers()
        for curveSet in self.playerDock.dockMultiEffect.curveSets:
            curveSet.Play()

        for controller in self.playerDock.dockMultiEffect.controllers:
            controller.Start()

        skin_state = sm.GetService('cosmeticsSvc').GetAppliedSkinStateForCurrentSession(self.playerShipItemID)
        if skin_state is not None and skin_state.skin_type == ShipSkinType.FIRST_PARTY_SKIN:
            self._activeSkinID = sm.GetService('cosmeticsSvc').GetFirstPartySkinObjectForCurrentSession(skin_state.skin_data.skin_id)

    def ProcessCamera(self, camera, newModel, typeID):
        print 'process camera called with newModel typeID: ', typeID

    def _shipRequiresBigDock(self, ship):
        pass


class ModularHangarDroneBehaviour(BaseHangarShipDroneBehaviour):

    def SetRepairDroneCount(self, boundingRadius):
        count = int(math.ceil(boundingRadius / 60.0))
        if self.repairDroneBehaviourGroup:
            self.repairDroneBehaviourGroup.SetCount(count)
