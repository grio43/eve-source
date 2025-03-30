#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\Jump.py
import logging
import random
import blue
import carbon.common.script.util.mathCommon as mathCommon
import carbonui.const as uiconst
import evecamera
import evecamera.shaker as shaker
import evefisfx.jumptransitioncamera as transitioncam
import geo2
import inventorycommon.const as invconst
import trinity
import uthread
from carbon.common.script.util.exceptionEater import ExceptionEater
from carbonui.uicore import uicore
from eve.client.script.environment.effects.GenericEffect import GenericEffect, ShipEffect, STOP_REASON_DEFAULT
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.script.sys.idCheckers import IsAbyssalSpaceSystem
from eve.common.script.sys.idCheckers import IsTriglavianSystem
from fsdBuiltData.common.graphicIDs import GetGraphicFile
logger = logging.getLogger(__name__)

class JumpTransitionTunnel(object):
    __guid__ = 'effects.JumpTransitionTunnel'

    def __init__(self, tunnelEffect):
        self.tunnelEffect = tunnelEffect
        self.destinationSceneApplied = False
        self.startCamDurationS = 1.0
        self.endCamDurationS = 1.0
        self.camOffsetStart = 1000000
        self.camOffsetEnd = 500000
        self.initToStartDelay = 850
        self.normDir = (0, 0, 1)
        self.effect = None
        self.effectRoot = None
        self.initCS = None
        self.startCS = None
        self.stopCS = None
        self.mainCS = None
        self.shakeDampCurve = None
        self.shakeScaleOut = None
        self.shakeScaleIn = None
        self.randomSoundNumber = 0
        self.cameraLookAnimation = None
        self.fxSequencer = sm.GetService('FxSequencer')

    def _FindCurveSets(self, model):
        self.initCS = None
        self.startCS = None
        self.stopCS = None
        self.mainCS = None
        for each in model.curveSets:
            if each.name == 'init':
                self.initCS = each
            elif each.name == 'start':
                self.startCS = each
            elif each.name == 'stop':
                self.stopCS = each
            elif each.name == 'valuePropagation':

                def propValue(*args):
                    source, dest = args
                    dest.value = source.value

                each.bindings[2].copyValueCallable = propValue
            elif each.name == 'main':
                self.mainCS = each

    def SetScene(self, scene):
        self.scene = scene
        scene.warpTunnel = self.effectRoot

    def _ApplyTexturePath(self, effect, name, path):
        for each in effect.resources:
            if each.name == name:
                each.resourcePath = path

    def _CreateCameraShakeCurves(self):
        shakeScaleOut = trinity.Tr2CurveScalar()
        shakeScaleOut.AddKey(0.0, 0.125, trinity.Tr2CurveInterpolation.LINEAR)
        shakeScaleOut.AddKey(0.5, 4.0, trinity.Tr2CurveInterpolation.LINEAR)
        shakeScaleOut.AddKey(2.5, 1.0, trinity.Tr2CurveInterpolation.LINEAR)
        shakeScaleIn = trinity.Tr2CurveScalar()
        shakeScaleIn.AddKey(0.0, 1.0, trinity.Tr2CurveInterpolation.LINEAR)
        shakeScaleIn.AddKey(0.4, 2.0, trinity.Tr2CurveInterpolation.LINEAR)
        shakeScaleIn.AddKey(0.6, 4.0, trinity.Tr2CurveInterpolation.LINEAR)
        shakeScaleIn.AddKey(0.8, 1.0, trinity.Tr2CurveInterpolation.LINEAR)
        shakeScaleIn.AddKey(1.1, 0.0, trinity.Tr2CurveInterpolation.LINEAR)
        shakeDampCurve = trinity.TriPerlinCurve()
        shakeDampCurve.offset = 0.07
        shakeDampCurve.scale = 1
        shakeDampCurve.alpha = 0.75
        shakeDampCurve.speed = 4
        shakeDampCurve.N = 4
        self.shakeJumpInit = shaker.ShakeBehavior('JumpInit')
        self.shakeJumpInit.noiseScale = 0.125
        self.shakeJumpInit.dampCurve = shakeDampCurve
        self.shakeJumpOut = shaker.ShakeBehavior('JumpOut')
        self.shakeJumpOut.scaleCurve = shakeScaleOut
        self.shakeJumpOut.dampCurve = shakeDampCurve
        self.shakeJumpIn = shaker.ShakeBehavior('JumpIn')
        self.shakeJumpIn.scaleCurve = shakeScaleIn
        self.shakeJumpIn.dampCurve = shakeDampCurve

    def Prepare(self, shipBall, destSystem = None):
        self.shipBall = shipBall
        self.ending = False
        self.effectRoot = trinity.EveRootTransform()
        self.effect = blue.resMan.LoadObject(self.tunnelEffect)
        self.dust = self.effect.children.FindByName('Dust')
        self.dust.display = True
        self.effectRoot.children.append(self.effect)
        self._FindCurveSets(self.effect)
        sceneMan = sm.GetService('sceneManager')
        self.camera = sceneMan.SetPrimaryCamera(evecamera.CAM_JUMP)
        transition = sm.GetService('viewState').GetTransitionByName('inflight', 'inflight')
        transition.SetTransitionEffect(self)
        self.transition = transition
        sceneManager = sm.GetService('sceneManager')
        if destSystem is not None:
            destNebulaPath = sceneManager.GetNebulaPathForSystem(destSystem)
            self._ApplyTexturePath(self.effect.mesh.transparentAreas[0].effect, 'NebulaMap', destNebulaPath)
        self._CreateCameraShakeCurves()

    def Start(self):
        uthread.new(self._DelayedStart)

    def _PlayInitSequence(self):
        self.StartGateEffectAudio()
        blue.synchro.SleepSim(850)
        if self.initCS is not None:
            self.initCS.Play()
            self.StartWarpTransitionAudio()
        blue.synchro.SleepSim(1500)
        self.GetCamera().shakeController.DoCameraShake(self.shakeJumpInit)

    def GetCamera(self):
        return sm.GetService('sceneManager').GetOrCreateCamera(evecamera.CAM_JUMP)

    def _PlayTunnelSequence(self):
        if self.ending:
            self.fxSequencer.LogWarn('Jump Transition: Trying to play tunnel start sequence while ending.')
            return
        normDir = geo2.QuaternionTransformVector(self.effectRoot.rotation, (0, 0, 1))
        self.normDir = normDir
        camera = self.GetCamera()
        camera.shakeController.DoCameraShake(self.shakeJumpOut)
        if self.initCS is not None:
            self.initCS.Stop()
        if self.startCS is not None:
            self.startCS.Play()
        camera.animationController.Schedule(transitioncam.OutFOV(self.startCamDurationS))
        blue.synchro.SleepSim(500)

    def _PlayMidTransitionCurves(self):
        self.transition.ApplyDestinationScene()
        self.destinationSceneApplied = True
        if self.mainCS is not None:
            self.mainCS.Play()
            self.StopWarpTransitionAudio()

    def _DelayedStart(self):
        with ExceptionEater('JumpTransitionTunnelStart'):
            self.DoCameraLookAnimation()
            self._PlayInitSequence()
            blue.synchro.SleepSim(self.initToStartDelay)
            self.FadeUIOut()
            self._PlayTunnelSequence()
            self._PlayMidTransitionCurves()

    def Stop(self):
        self._EarlyCleanup()
        self.ending = True
        if self.cameraLookAnimation is not None:
            self.cameraLookAnimation.Stop()
        camera = self.GetCamera()
        camera.shakeController.EndCameraShake('JumpIn')
        sm.GetService('viewState').GetView(ViewState.Space).ActivatePrimaryCamera()
        with ExceptionEater('JumpTransitionTunnelEnd'):
            if not self.destinationSceneApplied:
                self.transition.ApplyDestinationScene()
            camera = self.GetCamera()
            anim = camera.animationController
            offset = geo2.Vec3Scale(self.normDir, -self.camOffsetEnd)
            anim.Schedule(transitioncam.InFOV(self.endCamDurationS))
            camera.shakeController.DoCameraShake(self.shakeJumpIn)
        if self.startCS is not None:
            self.startCS.Stop()
        if self.mainCS is not None:
            self.mainCS.Stop()
        if self.stopCS is not None:
            self.stopCS.Play()
        if self.dust is not None:
            self.dust.display = False
        self.FadeUIIn()
        uthread.new(self.BlinkSystemName)
        uthread.new(self._DelayedCleanup)
        self.cameraLookAnimation.OnJumpDone()

    def _EarlyCleanup(self):
        pass

    def _DelayedCleanup(self):
        blue.synchro.SleepSim(2000)
        if self.stopCS is not None:
            self.stopCS.Stop()
        if self.scene.warpTunnel == self.effectRoot:
            self.scene.warpTunnel = None
        self.effect = None
        self.effectRoot = None
        self.dust = None

    def DoCameraLookAnimation(self):
        if self.cameraLookAnimation is not None:
            self.cameraLookAnimation.Start()

    def BlinkSystemName(self):
        blue.synchro.Sleep(1000)
        infoPanelSvc = sm.GetService('infoPanel')
        panel = infoPanelSvc.GetPanelByTypeID(infoPanelConst.PANEL_LOCATION_INFO)
        if panel is not None:
            uicore.animations.FadeOut(panel.headerLabelCont, loops=4, duration=0.5, curveType=uiconst.ANIM_WAVE)

    def GetUIToFade(self):
        toFade = []
        from eve.client.script.ui.inflight.overview.overviewWindowUtil import GetOverviewWndIfOpen
        overview = GetOverviewWndIfOpen()
        if overview is not None:
            try:
                toFade.append(overview.GetScrollContent())
            except:
                self.fxSequencer.LogWarn('Failed to get overview contents to fade while jumping')

        return toFade

    def FadeUIOut(self):
        if self.ending:
            self.fxSequencer.LogWarn('Jump Transition: Trying to fade out ui while ending.')
            return
        uicore.animations.FadeOut(uicore.layer.bracket, duration=1)
        objs = self.GetUIToFade()
        for obj in objs:
            uicore.animations.FadeOut(obj, duration=1)

        uicore.layer.bracket.opacity = 0.0
        if not self.ending:
            for obj in objs:
                obj.display = False

    def FadeUIIn(self):
        uicore.animations.FadeIn(uicore.layer.bracket, duration=1)
        objs = self.GetUIToFade()
        for obj in objs:
            obj.display = True
            uicore.animations.FadeIn(obj, duration=1, sleep=True)

        uicore.layer.bracket.opacity = 1.0
        for obj in objs:
            obj.opacity = 1.0
            obj.display = True

    def StartWarpTransitionAudio(self):
        eventName = 'transition_jump_play_%02d' % self.randomSoundNumber
        sm.GetService('audio').SendUIEvent(eventName)

    def StartGateEffectAudio(self):
        self.randomSoundNumber = random.randint(1, 10)
        eventName = 'jumpgate_new_play_%02d' % self.randomSoundNumber
        sm.GetService('audio').SendUIEvent(eventName)

    def StopWarpTransitionAudio(self):
        eventName = 'transition_jump_arrival_play_%02d' % self.randomSoundNumber
        sm.GetService('audio').SendUIEvent(eventName)


class JumpTransitionGate(JumpTransitionTunnel):
    __guid__ = 'effects.JumpTransitionGate'

    def __init__(self, tunnelEffect):
        JumpTransitionTunnel.__init__(self, tunnelEffect)

    def Prepare(self, shipBall, stargateID, stargateBall):
        destStargate, destSystem = sm.GetService('michelle').GetBallpark().GetInvItem(stargateID).jumps[0]
        JumpTransitionTunnel.Prepare(self, shipBall, destSystem)
        model = stargateBall.GetModel()
        if model is not None:
            self.effectRoot.rotation = model.rotationCurve.value
            gateSize = model.boundingSphereRadius
        else:
            gateSize = 2500
        self.transition.InitializeGateTransition(destSystem, destStargate)
        finalTranslation = self.shipBall.radius * 10
        self.cameraLookAnimation = transitioncam.LookAnimation(self.camera, self.effectRoot.rotation, startFocusID=stargateID, endFocusID=destStargate, startTranslation=gateSize * 3, endTranslation=finalTranslation)


class JumpTransitionShipCaster(JumpTransitionGate):
    __guid__ = 'effects.JumpShipCaster'


class JumpTransitionCyno(JumpTransitionTunnel):
    __guid__ = 'effects.JumpTransitionCyno'

    def __init__(self, tunnelEffect, gateID = None):
        JumpTransitionTunnel.__init__(self, tunnelEffect)
        self.gateID = gateID

    def Prepare(self, shipBall, destSystemID, rotation):
        JumpTransitionTunnel.Prepare(self, shipBall, destSystemID)
        self.effectRoot.rotation = rotation
        self.transition.InitializeCynoTransition(destSystemID)
        self.initToStartDelay = 0
        if self.gateID is not None:
            model = self.fxSequencer.GetBall(self.gateID).GetModel()
            if model is None:
                radius = 7000
            else:
                radius = model.boundingSphereRadius
            self.cameraLookAnimation = transitioncam.LookAnimation(self.camera, self.effectRoot.rotation, startFocusID=self.gateID, startTranslation=5 * radius)
        else:
            self.cameraLookAnimation = transitioncam.LookAnimation(self.camera, self.effectRoot.rotation)


class JumpTransitionWormhole(object):
    __guid__ = 'effects.JumpTransitionWormhole'

    def __init__(self):
        self.graphicInfo = None
        self.resPath = 'res:/fisfx/jump/wormholes/transition.red'
        self.model = None
        self.scene = None
        self.startCS = None
        self.stopCS = None
        self.midCS = None
        self.triglavianCS = None
        self.mainSequenceFinished = False

    def SetScene(self, scene):
        if self.model is None:
            return
        if self.scene is not None:
            self.scene.objects.fremove(self.model)
        scene.objects.append(self.model)
        self.scene = scene

    def Prepare(self, wormholeItem, destNebulaPath, srcNebulaPath, graphicInfo):
        if self.resPath is not None:
            self.model = trinity.Load(self.resPath)
        transition = sm.GetService('viewState').GetTransitionByName('inflight', 'inflight')
        transition.InitializeWormholeTransition(GetGraphicFile(wormholeItem.nebulaType))
        self.transition = transition
        self.graphicInfo = graphicInfo
        cubeParams = self.model.Find('trinity.TriTextureParameter')
        for cube in cubeParams:
            if cube.name == 'SourceNebulaMap':
                cube.resourcePath = srcNebulaPath
            elif cube.name == 'ReflectionMap':
                cube.resourcePath = destNebulaPath

        for each in self.model.curveSets:
            if each.name == 'start':
                self.startCS = each
            elif each.name == 'stop':
                self.stopCS = each
            elif each.name == 'middle':
                self.midCS = each
            elif each.name == 'destination_tspace':
                self.triglavianCS = each

        transition.SetTransitionEffect(self)
        self.itemID = wormholeItem.itemID
        sceneMan = sm.GetService('sceneManager')
        self.camera = sceneMan.SetPrimaryCamera(evecamera.CAM_JUMP)

    def _PlayMidCurves(self):
        if self.triglavianCS is not None and IsTriglavianSystem(self.graphicInfo[0]):
            self.triglavianCS.Play()
        blue.synchro.Sleep(500)
        if self.startCS is not None:
            self.startCS.Play()
        blue.synchro.Sleep(1000)
        self.transition.ApplyDestinationScene()
        if self.midCS is not None:
            self.midCS.Play()
        self.mainSequenceFinished = True

    def GetCamera(self):
        return sm.GetService('sceneManager').GetActiveSpaceCamera()

    def Start(self):
        camera = self.GetCamera()
        camera.LookAt(self.itemID, force=True)
        uthread.new(self._PlayMidCurves)
        sm.GetService('audio').SendUIEvent('worldobject_wormhole_travel_play')

    def Abort(self):
        self.transition.Abort()

        def _waitForFinish():
            while not self.mainSequenceFinished:
                blue.synchro.Yield()

            self.Stop()

        uthread.new(_waitForFinish)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        uthread.new(self.BlinkSystemName)
        if self.model is None:
            return
        uthread.new(self._DelayedStop)

    def _DelayedStop(self):
        if self.startCS is not None:
            self.startCS.Stop()
        if self.stopCS is not None:
            self.stopCS.Play()
        blue.synchro.SleepSim(500)
        sm.GetService('viewState').GetView(ViewState.Space).ActivatePrimaryCamera()
        blue.synchro.SleepSim(1500)
        if self.scene is not None:
            self.scene.objects.fremove(self.model)
            self.scene = None
        self.model = None

    def BlinkSystemName(self):
        blue.synchro.Sleep(1000)
        infoPanelSvc = sm.GetService('infoPanel')
        panel = infoPanelSvc.GetPanelByTypeID(infoPanelConst.PANEL_LOCATION_INFO)
        uicore.animations.FadeOut(panel.headerLabelCont, loops=4, duration=0.5, curveType=uiconst.ANIM_WAVE)

    def FadeOut(self, obj):
        uicore.animations.FadeOut(obj, duration=1)

    def FadeIn(self, obj):
        uicore.animations.FadeIn(obj, duration=1)


class JumpTransitionAbyssal(JumpTransitionTunnel):
    __guid__ = 'effects.JumpTransitionAbyssal'

    def __init__(self, tunnelEffect):
        JumpTransitionTunnel.__init__(self, tunnelEffect)

    def Prepare(self, shipBall, destSolarSystemID, beaconID, beaconBall, beaconModel, nebulaGraphicID = None):
        JumpTransitionTunnel.Prepare(self, shipBall)
        self.transition.InitializeAbyssalTransition(destSolarSystemID, nebulaGraphicID)
        self.cameraLookAnimation = transitioncam.AbyssalLookAnimation(self.camera, beaconModel.boundingSphereRadius, self.effectRoot, startFocusID=beaconID)
        self.DoCameraLookAnimation()

    def _DelayedStart(self):
        with ExceptionEater('JumpTransitionTunnelStart'):
            self.FreezeEnvironments(True)
            self._PlayInitSequence()
            blue.synchro.SleepSim(self.initToStartDelay)
            self.FadeUIOut()
            self._PlayTunnelSequence()
            self._PlayMidTransitionCurves()
            self.ClearEnvironments()

    def _EarlyCleanup(self):
        if self.stopCS is not None:
            self.stopCS.Stop()
        try:
            self.scene.objects.remove(self.effectRoot)
        except:
            pass

        self.effect = None
        self.effectRoot = None
        self.dust = None

    def _DelayedCleanup(self):
        pass

    def Stop(self):
        scene = self.fxSequencer.GetScene()
        tunnel = self.scene.warpTunnel
        self.scene.warpTunnel = None
        scene.objects.append(tunnel)
        blue.pyos.synchro.SleepSim(2000)
        self.FreezeEnvironments(False)
        blue.pyos.synchro.SleepSim(500)
        JumpTransitionTunnel.Stop(self)

    def FreezeEnvironments(self, frozen):
        sm.GetService('environment').FreezeEnvironments(frozen)

    def ClearEnvironments(self):
        sm.GetService('environment').ClearAllEnvironments()


class JumpTransitionAbyssalGate(JumpTransitionAbyssal):
    __guid__ = 'effects.JumpTransitionAbyssalGate'

    def Prepare(self, shipBall, destSolarSystemID, gateID, gateBall, gateModel, nebulaGraphicID = None):
        JumpTransitionTunnel.Prepare(self, shipBall)
        self.transition.InitializeAbyssalTransition(destSolarSystemID, nebulaGraphicID if IsAbyssalSpaceSystem(destSolarSystemID) else None)
        rotation = gateModel.rotationCurve.value if gateModel.rotationCurve is not None else geo2.QuaternionIdentity()
        distance = gateModel.boundingSphereRadius
        self.effectRoot.rotation = rotation
        self.cameraLookAnimation = transitioncam.AbyssalGateLookAnimation(self.camera, distance * 3, rotation, gateID)
        self.DoCameraLookAnimation()


class JumpTransitionAbyssalBetween(JumpTransitionAbyssal):
    __guid__ = 'effects.JumpTransitionAbyssalGate'

    def Prepare(self, shipBall, gateID, gateBall, gateModel):
        JumpTransitionTunnel.Prepare(self, shipBall)
        rotation = gateModel.rotationCurve.value if gateModel.rotationCurve is not None else geo2.QuaternionIdentity()
        distance = gateModel.boundingSphereRadius
        self.effectRoot.rotation = rotation
        self.cameraLookAnimation = transitioncam.AbyssalGateLookAnimation(self.camera, distance * 3, rotation, gateID)
        self.DoCameraLookAnimation()


class JumpDriveIn(ShipEffect):
    __guid__ = 'effects.JumpDriveIn'

    def Start(self, duration):
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        if shipBall is None:
            self.fxSequencer.LogError(self.__guid__, ' could not find a ball')
            return
        ShipEffect.Start(self, duration)

    def DelayedHide(self, shipBall, delay):
        blue.pyos.synchro.SleepSim(delay)
        if shipBall is not None and shipBall.model is not None:
            shipBall.model.display = False


class JumpDriveInBO(JumpDriveIn):
    __guid__ = 'effects.JumpDriveInBO'


class JumpDriveOut(JumpDriveIn):
    __guid__ = 'effects.JumpDriveOut'

    def Start(self, duration):
        shipID = self.ballIDs[0]
        gateID = self.ballIDs[1]
        shipBall = self.fxSequencer.GetBall(shipID)
        here = sm.GetService('map').GetItem(session.solarsystemid2)
        there = sm.GetService('map').GetItem(self.graphicInfo[0])
        yaw, pitch = mathCommon.GetYawAndPitchAnglesRad((here.x, here.y, here.z), (there.x, there.y, there.z))
        quat = geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, 0)
        self.gfxModel.rotation = quat
        if eve.session.shipid == shipID:
            self.playerEffect = JumpTransitionCyno(self.secondaryGraphicFile, gateID)
            self.playerEffect.Prepare(shipBall, self.graphicInfo[0], quat)
            self.playerEffect.SetScene(self.fxSequencer.GetScene())
            self.playerEffect.Start()
        ShipEffect.Start(self, duration)
        uthread.new(self.DelayedHide, shipBall, 180)


class JumpDriveOutBO(JumpDriveOut):
    __guid__ = 'effects.JumpDriveOutBO'


class JumpIn(JumpDriveIn):
    __guid__ = 'effects.JumpIn'

    def Start(self, duration):
        scaling = self.gfxModel.scaling
        self.gfxModel.scaling = (scaling[0] * 0.005, scaling[1] * 0.005, scaling[2] * 0.005)
        JumpDriveIn.Start(self, duration)


class JumpOut(ShipEffect):
    __guid__ = 'effects.JumpOut'

    def Start(self, duration):
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        uthread.new(self.DelayedHide, shipBall)
        targetID = self.ballIDs[1]
        targetBall = self.fxSequencer.GetBall(targetID)
        if session.shipid == shipID:
            if hasattr(shipBall, 'KillBooster'):
                shipBall.KillBooster()
            self.playerEffect = JumpTransitionGate(self.secondaryGraphicFile)
            self.playerEffect.Prepare(shipBall, targetID, targetBall)
            self.playerEffect.SetScene(self.fxSequencer.GetScene())
            self.playerEffect.Start()

    def DelayedHide(self, shipBall):
        blue.pyos.synchro.SleepSim(880)
        self.fxSequencer.OnSpecialFX(shipBall.id, None, None, None, None, 'effects.Uncloak', 0, 0, 0)
        if shipBall is not None and shipBall.model is not None:
            shipBall.model.display = False


class JumpOutWormhole(JumpDriveIn):
    __guid__ = 'effects.JumpOutWormhole'

    def Start(self, duration):
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        if getattr(shipBall, 'model', None) is not None:
            self.fxSequencer.OnSpecialFX(shipID, None, None, None, None, 'effects.CloakRegardless', 0, 1, 0, -1, None)
        uthread.new(self.DelayedHide, shipBall, 2000)
        wormholeID = self.ballIDs[1]
        wormholeBall = self.fxSequencer.GetBall(wormholeID)
        if eve.session.shipid == shipID:
            if hasattr(shipBall, 'KillBooster'):
                shipBall.KillBooster()
            scene = self.fxSequencer.GetScene()
            self.playerEffect = JumpTransitionWormhole()
            srcNebula = scene.envMapResPath
            targetNebula = getattr(wormholeBall, 'targetNebulaPath', None)
            wormholeItem = self.fxSequencer.GetItem(wormholeID)
            self.playerEffect.Prepare(wormholeItem, targetNebula, srcNebula, self.graphicInfo)
            self.playerEffect.SetScene(scene)
            self.playerEffect.Start()
        self.PlayNamedAnimations(wormholeBall.model, 'Activate')

    def Stop(self, reason = STOP_REASON_DEFAULT):
        JumpDriveIn.Stop(self, reason)
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        if shipBall is not None and shipBall.model is not None:
            shipBall.model.display = True


class JumpOutAbyssal(JumpOut):
    __guid__ = 'effects.JumpOutAbyssal'

    def Start(self, duration):
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        uthread.new(self.DelayedHide, shipBall)
        targetID = self.ballIDs[1]
        targetBall = self.fxSequencer.GetBall(targetID)
        targetModel = targetBall.GetModel()
        targetType = targetBall.typeID
        player = session.shipid == shipID
        if player:
            if hasattr(shipBall, 'KillBooster'):
                shipBall.KillBooster()
        logger.debug('JumpOutAbyssal.Start graphicInfo=%s', self.graphicInfo)
        if targetType in (invconst.typeKnownToAbyssalBeacon, invconst.typeKnownToAbyssalSuspectBeacon):
            self.RemoveFromScene(targetModel)
            if player:
                uthread.new(self.DelayedJumpTunnel, shipBall, targetID, targetBall, targetModel)
            else:
                uthread.new(self.DelayedTearTrace, targetBall)
            self.fxSequencer.OnSpecialFX(targetID, None, None, None, None, 'effects.AbyssalSpaceTear', 0, 1, 0)
        elif player:
            uthread.new(self.DelayedJumpTunnelGate, shipBall, targetID, targetBall, targetModel)
            self.PlayActivationCurve(targetModel)

    def PlayActivationCurve(self, model):
        self.PlayNamedChildAnimations(model, 'Activation')

    def DelayedTearTrace(self, ball):
        blue.pyos.synchro.SleepSim(10000)
        model = ball.GetModel()
        if model is not None:
            self.AddToScene(model)

    def DelayedJumpTunnel(self, shipBall, targetID, targetBall, targetModel):
        self.playerEffect = JumpTransitionAbyssal(self.secondaryGraphicFile)
        self.StartEffect(shipBall, targetID, targetBall, targetModel)

    def DelayedJumpTunnelGate(self, shipBall, targetID, targetBall, targetModel):
        self.playerEffect = JumpTransitionAbyssalGate(self.secondaryGraphicFile)
        self.StartEffect(shipBall, targetID, targetBall, targetModel)

    def StartEffect(self, shipBall, targetID, targetBall, targetModel):
        self.playerEffect.Prepare(shipBall, self._GetDestinationSolarSystemID(), targetID, targetBall, targetModel, nebulaGraphicID=self._GetNebulaGraphicID())
        self.playerEffect.SetScene(self.fxSequencer.GetScene())
        blue.pyos.synchro.SleepSim(6000)
        self.playerEffect.Start()

    def _GetDestinationSolarSystemID(self):
        return self.graphicInfo[0]

    def _GetNebulaGraphicID(self):
        return self.graphicInfo[1]


class JumpOutAbyssalBetween(JumpOutAbyssal):
    __guid__ = 'effects.JumpOutAbyssalBetween'

    def Start(self, duration):
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        shipModel = shipBall.GetModel()
        if session.shipid != shipID:
            return
        uthread.new(self.DelayedHide, shipBall)
        targetID = self.ballIDs[1]
        targetBall = self.fxSequencer.GetBall(targetID)
        targetModel = targetBall.GetModel()
        targetType = targetBall.typeID
        if hasattr(shipBall, 'KillBooster'):
            shipBall.KillBooster()
        uthread.new(self.DelayedJumpTunnelBetween, shipBall, shipModel, targetID, targetBall, targetModel)
        self.PlayActivationCurve(targetModel)

    def DelayedJumpTunnelBetween(self, shipBall, shipModel, targetID, targetBall, targetModel):
        self.playerEffect = JumpTransitionAbyssalBetween(self.secondaryGraphicFile)
        self.playerEffect.Prepare(shipBall, targetID, targetBall, targetModel)
        self.playerEffect.SetScene(self.fxSequencer.GetScene())
        self.playerEffect.Start()
        blue.pyos.synchro.SleepSim(5000)
        shipModel.display = True
        self.playerEffect.Stop()


class GateActivity(GenericEffect):
    __guid__ = 'effects.GateActivity'

    def Prepare(self):
        gateBall = self.GetEffectShipBall()
        self.gfx = gateBall.model

    def Start(self, duration):
        gateID = self.ballIDs[0]
        gateBall = self.fxSequencer.GetBall(gateID)
        if gateBall is None:
            self.fxSequencer.LogError('GateActivity could not find a gate ball')
            return
        if gateBall.model is None:
            self.fxSequencer.LogError('GateActivity could not find a gate ball')
            return
        gateBall.Activate()
        gateBall.JumpArrival()


class WormholeActivity(GenericEffect):
    __guid__ = 'effects.WormholeActivity'

    def Start(self, duration):
        wormholeID = self.ballIDs[0]
        wormholeBall = self.fxSequencer.GetBall(wormholeID)
        if wormholeBall is None:
            self.fxSequencer.LogError('WormholeActivity could not find a wormhole ball')
            return
        if wormholeBall.model is None:
            self.fxSequencer.LogError('WormholeActivity could not find a wormhole ball')
            return
        self.PlayNamedAnimations(wormholeBall.model, 'Activate')
