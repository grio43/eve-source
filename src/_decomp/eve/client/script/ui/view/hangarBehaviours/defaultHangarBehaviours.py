#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\hangarBehaviours\defaultHangarBehaviours.py
import geo2
import math
import trinity
from baseHangarBehaviours import BaseHangarShipBehaviour, BaseHangarShipDroneBehaviour
from carbonui.uicore import uicore

class DefaultHangarShipBehaviour(BaseHangarShipBehaviour):
    SHIP_FLOATING_HEIGHT = 360.0

    def __init__(self):
        BaseHangarShipBehaviour.__init__(self)
        self.startPos = (0, 0, 0)
        self.endPos = (0, 0, 0)
        self.isEnlistmentDockingEnabled = False

    def SetEnlistmentDockingEnabled(self, enabled):
        self.isEnlistmentDockingEnabled = enabled

    def SetDockingEffectGraphicID(self, graphicID):
        self.dockingEffectGraphicID = graphicID

    def SetAnchorPoint(self, hangarModel, hangarScene):
        if hangarModel is None:
            self.log.error('DefaultHangarShipBehaviour.SetAnchorPoint: Setting anchor point when scene is None')
            return
        anchorPointLocatorSets = [ locatorSet for locatorSet in getattr(hangarModel, 'locatorSets', []) if locatorSet.name == 'anchorpoint' ]
        if len(anchorPointLocatorSets) > 0:
            if len(getattr(anchorPointLocatorSets[0], 'locators', [])) > 0:
                self.shipAnchorPoint = anchorPointLocatorSets[0].locators[0][0]
                return
        if self.shipAnchorPoint == (0.0, 0.0, 0.0):
            self.shipAnchorPoint = (0.0, self.SHIP_FLOATING_HEIGHT)

    def PlaceShip(self, model, typeID):
        self.model = model
        trinity.WaitForResourceLoads()
        self.InitModelPosition()
        center = self.GetShipCenter(model, typeID)
        self.model.translationCurve.value = center
        self.endPos = self.model.translationCurve.value
        uicore.animations.StopAnimation(self.model.translationCurve, 'value')

    def GetShipCenter(self, model, typeID):
        boundingBoxYBottom = self.GetBoundingBoxYBottom(model)
        translation = geo2.Vec3Subtract(self.shipAnchorPoint, (0.0, boundingBoxYBottom, 0.0))
        offset = geo2.Vec3Scale(model.GetBoundingSphereCenter(), 0.5)
        return geo2.Vec3Add(translation, offset)

    def InitModelPosition(self):
        self.model.rotationCurve = trinity.Tr2RotationAdapter()
        self.model.rotationCurve.value = geo2.QuaternionRotationAxis((0, 1, 0), math.pi)
        self.model.translationCurve = trinity.Tr2TranslationAdapter()

    def AnimModelBoosters(self, duration):
        if not self.model.boosters:
            return
        self.model.translationCurve.value = self.startPos
        self.model.boosters.alwaysOnIntensity = 0.65
        self.model.boosters.alwaysOn = True
        self.model.boosters.display = True
        uicore.animations.MorphScalar(self.model.boosters, 'alwaysOnIntensity', self.model.boosters.alwaysOnIntensity, 0.0, duration=0.3 * duration, timeOffset=0.5 * duration)

    def AnimateShipEntry(self, model, typeID, scene = None, duration = 5.0):
        self.PlaceShip(model, typeID)
        dist = duration * 100
        self.startPos = geo2.Vec3Add(self.endPos, (0, 0, dist))
        self._createEntryCurveset(model.translationCurve, 'value', duration, callback=self.OnAnimShipEntryEnd)
        self.AnimModelBoosters(duration)

    def AnimateReflectionProbeEntry(self, reflectionProbe, duration = 5.0):
        if reflectionProbe:
            reflectionProbe.lockPosition = True
            self._createEntryCurveset(reflectionProbe, 'position', duration)

    def _createEntryCurveset(self, owner, attribute, duration, callback = None):
        cs = uicore.animations.MorphVector3(owner, attribute, self.startPos, self.endPos, duration=duration, callback=callback)
        tangent = geo2.Vec3Subtract(self.endPos, self.startPos)
        key = list(cs.curves[0].x.keys[0])
        key[3] = tangent[0] / duration
        cs.curves[0].x.keys[0] = tuple(key)
        key = list(cs.curves[0].y.keys[0])
        key[3] = tangent[1] / duration
        cs.curves[0].y.keys[0] = tuple(key)
        key = list(cs.curves[0].z.keys[0])
        key[3] = tangent[2] / duration
        cs.curves[0].z.keys[0] = tuple(key)

    def GetBoundingBoxYBottom(self, model):
        localBB = model.GetLocalBoundingBox()
        boundingBoxYBottom = localBB[0][1]
        return boundingBoxYBottom

    def GetAnimEndPosition(self):
        return self.endPos

    def GetAnimStartPosition(self):
        return self.startPos

    def OnAnimShipEntryEnd(self):
        initialPos = (0.0, 0.0, 0.0)
        yDelta = min(BaseHangarShipBehaviour.MIN_SHIP_BOBBING_HALF_DISTANCE, self.model.boundingSphereRadius * 0.05)
        delta = (0.0, yDelta, 0.0)
        bobTime = max(BaseHangarShipBehaviour.MIN_SHIP_BOBBING_TIME, self.model.boundingSphereRadius)
        bobTime = min(bobTime, BaseHangarShipBehaviour.MAX_SHIP_BOBBING_TIME)
        self.ApplyShipBobbing(self.model, initialPos, delta, bobTime)

    def UpdateUndockStatus(self, isUndocking):
        pass


class DefaultHangarDroneBehaviour(BaseHangarShipDroneBehaviour):

    def SetRepairDroneCount(self, boundingRadius):
        count = int(math.ceil(boundingRadius / 12.0))
        if self.repairDroneBehaviourGroup:
            self.repairDroneBehaviourGroup.SetCount(count)
