#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\spaceSubway\spaceSubwayEffect.py
import trinity
import blue
import logging
import uthread2
from eveexceptions import ExceptionEater
from evegraphics.graphicEffects.skinChange import ChangeSkin
from evegraphics.spaceSubway.const import GetRegionValue
import fsdBuiltData.client.travelEffects as travelEffects
from uthread2.delayedcalls import call_after_simtime_delay
log = logging.getLogger(__name__)

def ReCurvenizeObject(obj):
    if obj is None:
        return
    obj.translationCurve = CreateTranslationAdapter(obj.translationCurve)
    obj.rotationCurve = CreateRotationAdapter(obj.rotationCurve)
    if obj.modelRotationCurve is None:
        obj.modelRotationCurve = trinity.Tr2RotationAdapter()
    if obj.modelTranslationCurve is None:
        obj.modelTranslationCurve = trinity.Tr2TranslationAdapter()


def CreateTranslationAdapter(curve):
    adapter = trinity.Tr2TranslationAdapter()
    if hasattr(curve, 'GetVectorAt'):
        value = curve.GetVectorAt(blue.os.GetSimTime())
        adapter.value = (value.x, value.y, value.z)
    elif hasattr(curve, 'value'):
        adapter.value = curve.value
    elif hasattr(curve, 'currentValue'):
        adapter.value = curve.currentValue
    return adapter


def CreateRotationAdapter(curve):
    adapter = trinity.Tr2RotationAdapter()
    if hasattr(curve, 'GetQuaternionAt'):
        value = curve.GetQuaternionAt(blue.os.GetSimTime())
        adapter.value = (value.x,
         value.y,
         value.z,
         value.w)
    elif hasattr(curve, 'value'):
        adapter.value = curve.value
    elif hasattr(curve, 'currentValue'):
        adapter.value = curve.currentValue
    adapter.UpdateQuaternion(blue.os.GetSimTime())
    return adapter


class SpaceSubwayCamera(object):

    def __init__(self):
        self.lastPosition = None
        self.lastFov = None
        self.lastPointOfInterest = None
        self.updateThread = None
        self.isUpdating = False

    @property
    def position(self):
        raise NotImplementedError()

    @position.setter
    def position(self, newPos):
        raise NotImplementedError()

    @property
    def fov(self):
        raise NotImplementedError()

    @fov.setter
    def fov(self, newFov):
        raise NotImplementedError()

    @property
    def pointOfInterest(self):
        raise NotImplementedError()

    @pointOfInterest.setter
    def pointOfInterest(self, newPointOfInterest):
        raise NotImplementedError()

    def Link(self, pos, poi, fov):
        self.isUpdating = True
        self.updateThread = uthread2.start_tasklet(self.UpdateCamera, pos, poi, fov)

    def UpdateCamera(self, pos, poi, fov):
        log.info('Started updating jump camera')
        while self.isUpdating:
            newPos = pos.GetValue() if pos else self.position
            newPoi = poi.GetValue() if poi else self.pointOfInterest
            with ExceptionEater('Got error while updating camera'):
                if newPos != (0, 0, 0) and newPoi != (0, 0, 0):
                    self.position = pos.GetValue() if pos else self.position
                    self.pointOfInterest = poi.GetValue() if poi else self.pointOfInterest
                    self.fov = fov.GetValue() if fov else self.fov
            uthread2.Yield()

        log.info('Stopped updating jump camera')

    def UnLink(self):
        self.isUpdating = False


class SpaceSubwayEffect(object):

    def __init__(self):
        self.originScene = None
        self.currentScene = None
        self.ship = None
        self.origin = None
        self.skinChangeModels = []
        self.multiEffect = None
        self.tunnelEffect = None
        self.transitionScene = None
        self.destinationScene = None
        self.hidingEffect = None
        self.shipHideDelay = 0
        self.currentEffect = None
        self.regionValue = None
        self.security = 0
        self.inTransitionScene = False

    def __CleanScene(self, scene, callback = None):
        if scene:
            if self.origin and self.origin in scene.objects:
                scene.objects.fremove(self.origin)
            if self.multiEffect and self.multiEffect in scene.objects:
                scene.objects.fremove(self.multiEffect)
            if self.ship and self.ship in scene.objects:
                scene.objects.fremove(self.ship)
            if self.tunnelEffect and self.tunnelEffect in scene.objects:
                scene.objects.fremove(self.tunnelEffect)
            if self.hidingEffect and self.hidingEffect in scene.objects:
                scene.objects.fremove(self.hidingEffect)
            for m in self.skinChangeModels:
                if m in scene.objects:
                    scene.objects.fremove(m)

        if callback:
            callback()

    def _CleanScene(self, scene, callback = None):
        uthread2.start_tasklet(self.__CleanScene, scene, callback)

    def Cleanup(self):
        log.info('Cleaning up')

        def inner():
            self.originScene = None
            self.transitionScene = None
            self.destinationScene = None
            self.currentScene = None
            self.origin = None
            self.ship = None
            self.tunnelEffect = None
            self.hidingEffect = None
            if self.multiEffect:
                for curveSet in self.multiEffect.curveSets:
                    for curveKey in curveSet.Find('trinity.Tr2ObjectFollowCurveKey'):
                        curveKey.object = None

            self.multiEffect = None
            self.currentEffect = None
            self.regionValue = None
            self.security = 0
            self.shipHideDelay = 0
            self.skinChangeModels = []

        self._CleanScene(self.originScene)
        self._CleanScene(self.transitionScene)
        self._CleanScene(self.destinationScene, callback=inner)

    def GetTunnelEffect(self):
        if self.tunnelEffect is None:
            self.tunnelEffect = trinity.Load(travelEffects.GetEffect(self.currentEffect))
        return self.tunnelEffect

    def GetMultiEffect(self):
        if self.multiEffect is None:
            self.multiEffect = trinity.Load(travelEffects.GetMultiEffect(self.currentEffect))
        return self.multiEffect

    def GetTransitionScene(self):
        if self.transitionScene is None:
            self.transitionScene = trinity.Load(travelEffects.GetTransitionScene(self.currentEffect))
        return self.transitionScene

    def GetHidingEffect(self):
        if self.hidingEffect is None:
            hidingEffectResPath = travelEffects.GetHidingEffectPath(self.currentEffect)
            if hidingEffectResPath is not None:
                self.hidingEffect = trinity.Load(hidingEffectResPath)
                if isinstance(self.hidingEffect, trinity.EveTransform):
                    root = trinity.EveRootTransform()
                    root.children.append(self.hidingEffect)
                    self.hidingEffect = root
        return self.hidingEffect

    def GetShipHideDelay(self):
        return travelEffects.GetShipHideDelay(self.currentEffect)

    def GetHidingEffectDuration(self):
        return travelEffects.GetHidingEffectDuration(self.currentEffect)

    def CreateOriginEffect(self, originOrientation):
        originEffect = travelEffects.GetOriginEffect(self.currentEffect)
        origin = None
        if originEffect:
            origin = trinity.Load(originEffect)
        if not origin:
            log.info('Creating a fake gate for %s' % self.currentEffect)
            origin = trinity.EveEffectRoot2()
            origin.name = 'FakeGate'
        origin.boundingSphereRadius = max(origin.boundingSphereRadius, 5000)
        origin.translationCurve = trinity.Tr2TranslationAdapter()
        origin.translationCurve.value = self.ship.translationCurve.value
        origin.rotationCurve = trinity.Tr2RotationAdapter()
        origin.rotationCurve.value = self.ship.rotationCurve.value
        if originOrientation is not None and isinstance(originOrientation, tuple):
            origin.rotationCurve.value = originOrientation
        if self.originScene is not None:
            self.originScene.objects.append(origin)
        return origin

    def IsWithinSystem(self):
        return travelEffects.IsJumpWithinSystem(self.currentEffect)

    def SetLook(self, nebulaPath, security, propagateToEffect = False):
        self.regionValue = GetRegionValue(nebulaPath)
        self.security = security
        if propagateToEffect:
            self.PropagateLookToEffect()

    def PropagateLookToEffect(self):
        self.tunnelEffect.SetControllerVariable('RegionLook', self.regionValue)
        self.tunnelEffect.SetControllerVariable('SecurityLook', self.security)

    def SetDestinationScene(self, scene):
        self.destinationScene = scene

    def SetEffect(self, effect):
        self.currentEffect = effect
        self.transitionScene = self.GetTransitionScene()
        self.multiEffect = self.GetMultiEffect()
        self.tunnelEffect = self.GetTunnelEffect()
        self.hidingEffect = self.GetHidingEffect()
        self.shipHideDelay = self.GetShipHideDelay()

    def SetOriginScene(self, scene):
        self.originScene = scene
        self.currentScene = scene

    def IsValid(self):
        if self.currentEffect is None:
            log.error('No effect is playing')
            return False
        if self.multiEffect is None:
            log.error('No multiEffect loaded for %s', self.currentEffect)
            return False
        if self.tunnelEffect is None:
            log.error('No tunnelEffect loaded for %s', self.currentEffect)
            return False
        return True

    def HideJumpingShip(self, ship, originOrientation = None, callback = None):
        log.info('Hiding jumping ship')
        if self.hidingEffect is not None:
            log.info('Playing ship hide effect')
            self.hidingEffect.translationCurve = ship.translationCurve
            if originOrientation is not None:
                if hasattr(self.hidingEffect, 'rotationCurve'):
                    self.hidingEffect.rotationCurve = trinity.Tr2RotationAdapter()
                    self.hidingEffect.rotationCurve.value = originOrientation
                else:
                    self.hidingEffect.rotation = originOrientation
            self.hidingEffect.scaling = tuple([ship.boundingSphereRadius] * 3)
            self.originScene.objects.append(self.hidingEffect)
            for curveSet in getattr(self.hidingEffect, 'curveSets', []):
                curveSet.Stop()

            for curveSet in getattr(self.hidingEffect, 'curveSets', []):
                curveSet.Play()

            if hasattr(self.hidingEffect, 'StartControllers'):
                self.hidingEffect.StartControllers()

            def HideShip(ship):
                log.info('Hiding ship')
                if ship:
                    ship.display = False
                for model in self.skinChangeModels:
                    model.display = False

            def RemoveEffect(scene, effect, callback = None):
                log.info('Removing hiding effect')
                if effect and scene and effect in scene.objects:
                    scene.objects.fremove(effect)
                if callback:
                    callback()

            call_after_simtime_delay(HideShip, self.GetShipHideDelay(), ship)
            call_after_simtime_delay(RemoveEffect, self.GetHidingEffectDuration(), self.originScene, self.hidingEffect, callback)

    def StartEffectForOwner(self, origin, ship, originOrientation = None):
        if not self.IsValid():
            return
        if ship:
            try:
                self.HideJumpingShip(ship, originOrientation)
            except Exception as e:
                log.exception('Got an exception while hiding the jumping ship %s', e)

        self.ship = ship
        ReCurvenizeObject(self.ship)
        self.origin = origin
        if self.origin is None:
            self.origin = self.CreateOriginEffect(originOrientation)
        ReCurvenizeObject(self.origin)
        self.tunnelEffect.translationCurve = trinity.Tr2TranslationAdapter()
        self.tunnelEffect.rotationCurve = trinity.Tr2RotationAdapter()
        self.multiEffect.SetParameter('ship', self.ship)
        self.multiEffect.SetParameter('origin', self.origin)
        self.multiEffect.SetParameter('tunnel', self.tunnelEffect)
        self.AddToScene(self.originScene)
        for curveSet in self.multiEffect.curveSets:
            self.LinkCurveSetToOrigin(curveSet)

        self.SetupCamera()
        for controller in self.multiEffect.controllers:
            controller.RegisterCallback('gotoTransitionScene', self.Callback('Transition Scene', self.TurnOnTransitionScene))
            controller.RegisterCallback('gotoDestinationScene', self.Callback('Destination Scene', self.TurnOnEndScene))
            controller.RegisterCallback('attachCamera', self.Callback('Attach Camera', self.AttachCamera))
            controller.RegisterCallback('detachCamera', self.Callback('Detach Camera', self.DetachCamera))
            controller.RegisterCallback('cleanup', self.Callback('Cleanup', self.Cleanup))

        self.PropagateLookToEffect()
        self.multiEffect.StartControllers()
        self.multiEffect.SetControllerVariable('tunneltrigger', 1.0)
        if self.IsWithinSystem():
            self.destinationScene = self.originScene
            call_after_simtime_delay(self.Stop, 5)

    def Callback(self, description, func):

        def startTasklet():
            log.info('Starting tasklet %s' % description)
            uthread2.StartTasklet(func)

        return startTasklet

    def Stop(self):
        log.info('Stopping space subway effect')
        multiEffect = self.GetMultiEffect()
        if multiEffect is not None:
            multiEffect.SetControllerVariable('tunneltrigger', 0.0)

    def Terminate(self):
        if self.currentEffect is None:
            return
        self.DetachCamera()

    def GetCamera(self):
        raise NotImplementedError('GetCamera needs to be implemented in child classes')

    def LinkCurveSetToOrigin(self, curveSet):
        for curveKey in curveSet.Find('trinity.Tr2ObjectFollowCurveKey'):
            curveKey.object = self.origin

    def SetupCamera(self):
        cam = self.GetCamera()
        if cam is None:
            return
        initialCameraPosParameter = self.multiEffect.externalParameters.FindByName('initialCameraPos')
        initialCameraTargetParameter = self.multiEffect.externalParameters.FindByName('initialCameraTarget')
        if initialCameraTargetParameter:
            initialCameraTargetParameter.SetValue(self.GetCamera().pointOfInterest)
        if initialCameraPosParameter:
            initialCameraPosParameter.SetValue(self.GetCamera().position)

    def AttachCamera(self):
        log.info('Attaching to camera')
        pos = self.multiEffect.externalParameters.FindByName('cameraPos')
        poi = self.multiEffect.externalParameters.FindByName('cameraTarget')
        fov = self.multiEffect.externalParameters.FindByName('cameraFOV')
        cam = self.GetCamera()
        if cam is None:
            return
        cam.Link(pos, poi, fov)

    def DetachCamera(self):
        log.info('Detaching from camera')
        cam = self.GetCamera()
        if cam is not None:
            log.info('Unlinking from camera curves')
            cam.UnLink()

    def AddToScene(self, scene):
        if self.multiEffect is not None:
            scene.objects.append(self.multiEffect)
        if self.tunnelEffect is not None:
            scene.objects.append(self.tunnelEffect)

    def TurnOnTransitionScene(self):
        log.info('Turning on transition scene')
        self.AddToScene(self.transitionScene)
        if self.ship is not None:
            self.transitionScene.objects.append(self.ship)
        for m in self.skinChangeModels:
            self.transitionScene.objects.append(m)

        self.PropagateLookToEffect()
        self.SetScene(self.transitionScene)
        self.currentScene = self.transitionScene
        self._CleanScene(self.originScene)
        self.inTransitionScene = True

    def TurnOnEndScene(self):
        log.info('Turning on end scene')
        self.AddToScene(self.destinationScene)
        self.PropagateLookToEffect()
        self.SetScene(self.destinationScene)
        self.currentScene = self.destinationScene
        self._CleanScene(self.transitionScene)

    def SetScene(self, scene):
        raise NotImplementedError()

    def ChangeSkin(self, newModel):
        if self.ship is None:
            return
        self.skinChangeModels.append(newModel)
        ChangeSkin(self.ship, newModel, self.currentScene)
        newModel.translationCurve = self.ship.translationCurve
        newModel.rotationCurve = self.ship.rotationCurve
        newModel.modelTranslationCurve = self.ship.modelTranslationCurve
        newModel.modelRotationCurve = self.ship.modelRotationCurve
        self.ship = newModel

    def IsShakeEnabled(self):
        return True

    def SetShake(self, shakeToggled):
        if self.multiEffect is not None:
            self.multiEffect.SetControllerVariable('TunnelShake', float(shakeToggled))
