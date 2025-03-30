#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\subwaySvc.py
import logging
import blue
import evecamera
import evegraphics.settings as gfxsettings
import geo2
import telemetry
import trinity
import uthread2
from carbon.common.script.sys.service import Service
from carbon.common.script.util import mathCommon
from carbonui.uicore import uicore
from eve.client.script.parklife import states
from eve.client.script.parklife.sceneManager import GetSceneManager
from eve.client.script.ui.camera.jumpCamera import JumpCamera
from eve.client.script.ui.inflight.overview.overviewWindowUtil import GetOverviewWndIfOpen
from eve.common.lib import appConst
from eve.common.script.sys.idCheckers import IsSolarSystem, IsStargate
from evegraphics.spaceSubway.spaceSubwayEffect import SpaceSubwayEffect, SpaceSubwayCamera
from fsdBuiltData.client.travelEffects import IsTravelEffect
from tacticalNavigation.ballparkFunctions import GetBallpark, GetBall
log = logging.getLogger(__name__)

def GetSubwayService():
    return sm.GetService('subway')


def FadeUI(out = False):
    fadePanels = [ child for child in uicore.layer.inflight.children if getattr(child, '__renderObject__', None) != trinity.Tr2Sprite2d ]
    try:
        overView = GetOverviewWndIfOpen()
        fadePanels.append(overView.GetScrollContent())
    except AttributeError:
        log.error('FadeUI: Could not gather overview content for fading')

    fadeFunction = uicore.animations.FadeIn
    if out:
        fadeFunction = uicore.animations.FadeOut
    for fadePanel in fadePanels:
        fadeFunction(fadePanel, duration=1)

    fadeValue = 0.0 if out else 1.0
    for fadePanel in fadePanels:
        fadePanel.opacity = fadeValue


def PreJumpServiceCalls(gateID, destinationID):
    sm.ScatterEvent('OnJumpStarted', gateID, destinationID)
    sm.GetService('flightControls').Stop()
    uthread2.StartTasklet(FadeUI, True)


def PostJumpServiceCalls(gateID):
    uthread2.StartTasklet(FadeUI, False)
    ballpark = sm.GetService('michelle').GetBallpark(doWait=True)
    if ballpark is None:
        return
    sm.GetService('flightControls').Start()
    sm.ScatterEvent('OnJumpExecuted', gateID)


def GetPriorityLoads(gateID):
    priorityList = [gateID]
    if gateID and IsStargate(gateID):
        gateItem = GetBallpark().GetInvItem(gateID)
        if gateItem is not None:
            destGate, destSystem = gateItem.jumps[0]
            systemItems = sm.GetService('map').GetSolarsystemItems(destSystem, False)
            stargateRow = systemItems.Filter('itemID')[destGate][0]
            stargatePos = (stargateRow.x, stargateRow.y, stargateRow.z)
            maxDistSq = (appConst.AU * 0.5) ** 2
            for each in systemItems:
                if each.itemID == gateID:
                    continue
                pos = (each.x, each.y, each.z)
                dist = geo2.Vec3DistanceSq(stargatePos, pos)
                if dist < maxDistSq:
                    priorityList.append(each.itemID)

    return priorityList


class EveSpaceSubwayCamera(SpaceSubwayCamera):

    def __init__(self):
        super(EveSpaceSubwayCamera, self).__init__()
        self.camera = GetSceneManager().GetOrCreateCamera(evecamera.CAM_JUMP)
        GetSceneManager().SetPrimaryCamera(JumpCamera.cameraID)

    @property
    def position(self):
        return self.camera.eyePosition

    @position.setter
    def position(self, pos):
        self.camera.eyePosition = pos

    @property
    def fov(self):
        return self.camera.fov

    @fov.setter
    def fov(self, fov):
        self.camera.fov = fov

    @property
    def pointOfInterest(self):
        return self.camera.atPosition

    @pointOfInterest.setter
    def pointOfInterest(self, poi):
        self.camera.atPosition = poi

    def UnLink(self):
        super(EveSpaceSubwayCamera, self).UnLink()
        primaryView = sm.GetService('viewState').GetPrimaryView()
        cam = primaryView.ActivatePrimaryCamera()
        cam.StopShaking()

    def TransitionToShip(self, endLookatID):
        camera = GetSceneManager().GetActivePrimaryCamera()
        uthread2.Sleep(self.camera.transitionDelay + 0.1)
        if camera.cameraID == evecamera.CAM_SHIPORBIT:
            if sm.GetService('autoPilot').GetState():
                uthread2.Sleep(1.0)
                camera.Track(endLookatID, speed=10, duration=5.5)


class EveSpaceSubwayEffectState(object):
    SCENE_STATE_SOURCE = 0
    SCENE_STATE_TRANSITION = 1
    SCENE_STATE_DESTINATION = 2
    CAMERA_STATE_NOT_SET = -1
    CAMERA_STATE_DETACHED = 0
    CAMERA_STATE_ATTACHED = 1
    POST_JUMP_CALLBACKS_STATE_NOT_CALLED = 0
    POST_JUMP_CALLBACKS_STATE_CALLED = 1
    CLEANUP_STATE_NOT_DONE = 0
    CLEANUP_STATE_STARTED = 1
    CLEANUP_STATE_DONE = 2
    STOP_REQUESTED_STATE_NO = 0
    STOP_REQUESTED_STATE_YES = 1

    def __init__(self):
        self.scene = self.SCENE_STATE_SOURCE
        self.camera = self.CAMERA_STATE_NOT_SET
        self.postJumpCallback = self.POST_JUMP_CALLBACKS_STATE_NOT_CALLED
        self.cleanup = self.CLEANUP_STATE_NOT_DONE
        self.stopRequested = self.STOP_REQUESTED_STATE_NO

    def StartedCleaning(self):
        return self.cleanup >= self.CLEANUP_STATE_STARTED

    def StartCleaning(self):
        self.cleanup = self.CLEANUP_STATE_STARTED

    def IsCameraDetached(self):
        return self.camera == self.CAMERA_STATE_DETACHED

    def AttachCamera(self):
        self.camera = self.CAMERA_STATE_ATTACHED

    def DetachCamera(self):
        self.camera = self.CAMERA_STATE_DETACHED

    def IsInDestScene(self):
        return self.scene == self.SCENE_STATE_DESTINATION

    def IsInTranitionScene(self):
        return self.scene == self.SCENE_STATE_TRANSITION

    def EnterDestinationScene(self):
        self.scene = self.SCENE_STATE_DESTINATION

    def EnterTransitionScene(self):
        self.scene = self.SCENE_STATE_TRANSITION

    def CallPostJumpCallbacks(self):
        self.postJumpCallback = self.POST_JUMP_CALLBACKS_STATE_CALLED

    def HavePostJumpCallbacksBeenCalled(self):
        return self.postJumpCallback == self.POST_JUMP_CALLBACKS_STATE_CALLED

    def Stop(self):
        self.stopRequested = self.STOP_REQUESTED_STATE_YES

    def HasStopped(self):
        return self.stopRequested == self.STOP_REQUESTED_STATE_YES

    def info(self):
        return {'scene': self.scene,
         'camera': self.camera,
         'postJumpCallback': self.postJumpCallback,
         'cleanup': self.cleanup,
         'stopRequested': self.stopRequested}


class EveSpaceSubwayEffect(SpaceSubwayEffect):

    def __init__(self, cleanupCallback = None, endFocusID = None, jumpInfo = None):
        super(EveSpaceSubwayEffect, self).__init__()
        self.endFocusID = endFocusID
        self.camera = None
        self.cleanupCallback = cleanupCallback
        self.cleanupCallbackEnabled = True
        self.jumpInfo = jumpInfo
        self.killThread = None
        self.state = EveSpaceSubwayEffectState()

    def DisableCleanupCallback(self):
        self.cleanupCallbackEnabled = False

    def CleanupLite(self):
        super(EveSpaceSubwayEffect, self).Cleanup()

    def Cleanup(self):
        if self.state.StartedCleaning():
            return
        self.state.StartCleaning()
        log.info('Cleaning up EveSpaceSubwayEffect')
        if not self.state.IsInDestScene():
            log.warning('Destination scene not enabled when we started cleaning, fixing that')
            self.SetScene(self.destinationScene)
        if not self.state.IsCameraDetached():
            log.warning('Camera not detached when we started cleaning, fixing that')
            self.DetachCamera()
        if not self.state.HavePostJumpCallbacksBeenCalled():
            log.warning('Post Jump Service calls not called when we started cleaning, fixing that')
            self.PostJumpServiceCalls()
        super(EveSpaceSubwayEffect, self).Cleanup()
        if self.cleanupCallback and self.cleanupCallbackEnabled:
            self.cleanupCallback()

    def StartedCleaning(self):
        return self.state.StartedCleaning()

    def GetCamera(self):
        if self.camera is None:
            self.camera = EveSpaceSubwayCamera()
        return self.camera

    def AttachCamera(self):
        self.state.AttachCamera()
        super(EveSpaceSubwayEffect, self).AttachCamera()

    def SetLook(self, nebulaPath, security, propagateToEffect = False):
        super(EveSpaceSubwayEffect, self).SetLook(nebulaPath, security, self.inTransitionScene)

    def GetJumpEndLookAtID(self):
        lookatID = self.endFocusID
        autoPilot = sm.GetService('autoPilot')
        starmapSvc = sm.GetService('starmap')
        destinationPath = starmapSvc.GetDestinationPath()
        if destinationPath is not None and len(destinationPath) > 0 and destinationPath[0] is not None:
            bp = GetBallpark()
            if bp is not None:
                destID = autoPilot.GetGateOrStationID(bp, destinationPath[0])
                if destID is not None:
                    lookatID = destID
        return lookatID

    def DetachCamera(self):
        self.state.DetachCamera()
        if self.IsWithinSystem():
            shipBall = sm.GetService('michelle').GetBall(session.shipid)
            shipBall.fitted = False
            shipBall.Prepare()
        super(EveSpaceSubwayEffect, self).DetachCamera()

    def TurnOnTransitionScene(self):
        super(EveSpaceSubwayEffect, self).TurnOnTransitionScene()
        if self.ship:
            self.ship.rotationCurve.value = self.tunnelEffect.rotationCurve.value
            for m in self.skinChangeModels:
                m.rotationCurve.value = self.tunnelEffect.rotationCurve.value

        self.state.EnterTransitionScene()

    def TurnOnEndScene(self):
        super(EveSpaceSubwayEffect, self).TurnOnEndScene()
        uthread2.StartTasklet(self.PostJumpServiceCalls)
        self.state.EnterDestinationScene()

    def PostJumpServiceCalls(self):
        PostJumpServiceCalls(self.jumpInfo['gateID'])
        self.JumpToSpaceTransitionCallback()
        self.state.CallPostJumpCallbacks()

    def JumpToSpaceTransitionCallback(self):
        endLookatID = self.GetJumpEndLookAtID()
        self.camera.TransitionToShip(endLookatID)
        sm.GetService('stateSvc').SetState(endLookatID, states.selected, 1)
        sm.ScatterEvent('OnJumpFinished', self.jumpInfo['gateID'], self.jumpInfo['originSystemID'])

    def SetScene(self, scene):
        if scene is None:
            log.error('Stopping you from setting the current scene to None, this would not have had good consequences. Good thing I caught you bro, but fix up your shitty code!')
            return
        if scene is self.transitionScene:
            log.info('Setting scene to transition scene')
            GetSceneManager().ApplyScene(scene, 'transition')
        else:
            log.info('Setting scene to destination scene')
            GetSceneManager().ApplyScene(scene, 'default')
            GetSceneManager().ApplySpaceScene()
            GetSceneManager().UnregisterScene('transition', ignoreCamera=True)

    def KillShot(self):
        uthread2.SleepSim(10)
        if not self.state.StartedCleaning():
            self.jumpInfo['effect_state'] = self.state.info()
            log.warning("The space subway effect didn't get cleaned up properly after 10 seconds in simtime. Killing it!", extra=self.jumpInfo)
            self.Cleanup()

    def Stop(self, forceKillSwitch = False):
        self.state.Stop()
        self.killThread = uthread2.StartTasklet(self.KillShot)
        if forceKillSwitch:
            return
        super(EveSpaceSubwayEffect, self).Stop()

    def IsShakeEnabled(self):
        setting = gfxsettings.Get(gfxsettings.UI_CAMERA_SHAKE_ENABLED)
        return setting is None or setting

    def OutOfSourceSystem(self):
        return self.state.IsInTranitionScene() or self.state.IsInDestScene()


class SubwayService(Service):
    __guid__ = 'svc.subway'
    __servicename__ = 'subway'
    __displayname__ = 'Space Subway Service'
    __exportedcalls__ = {}
    __notifyevents__ = ['OnSpecialFX', 'OnSessionChanged', 'OnGraphicSettingsChanged']
    __dependencies__ = ['sceneManager', 'michelle']
    __startupdependencies__ = []
    ENABLED = True
    JUMP_FINISH_DELAY = 0
    JUMP_EFFECT_OVERRIDE = None
    FORCE_KILL_SWITCH = False

    def __init__(self):
        super(SubwayService, self).__init__()
        self.originScene = None
        self.destinationScene = None
        self.spaceSubwayEffect = None
        self.gateID = None
        self.shipID = None
        self.originSystemID = None
        self.destSystemID = None
        self.lockedBalls = []

    def Enabled(self):
        return self.ENABLED

    def InJump(self):
        return self.spaceSubwayEffect is not None and not self.spaceSubwayEffect.StartedCleaning()

    def Toggle(self):
        self.ENABLED = not self.ENABLED

    def ToggleKillSwitch(self):
        self.FORCE_KILL_SWITCH = not self.FORCE_KILL_SWITCH

    def SetEffectOverride(self, effect_guid):
        self.JUMP_EFFECT_OVERRIDE = effect_guid

    def OkToDumpBallPark(self):
        return self.spaceSubwayEffect is not None and self.spaceSubwayEffect.OutOfSourceSystem()

    @telemetry.ZONE_METHOD
    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration = -1, repeat = None, startTime = None, timeFromStart = 0, graphicInfo = None):
        if self.ENABLED and IsTravelEffect(guid):
            destinationSystem = None
            if graphicInfo:
                destinationSystem = graphicInfo[0]
            guid = self.JUMP_EFFECT_OVERRIDE or guid
            if shipID == session.shipid:
                self.shipID = shipID
                self.gateID = targetID
                self.originSystemID = session.solarsystemid
                self.destSystemID = destinationSystem
                try:
                    self.StartJump(shipID, targetID, guid, destinationSystem)
                except Exception as e:
                    log.exception('Exception caught while jumping %s' % e)
                    PostJumpServiceCalls(self.gateID)
                    self.Cleanup()

                sm.GetService('space').PrioritizeLoadingForIDs(GetPriorityLoads(self.gateID))
            else:
                try:
                    self.StartJumpForAudience(shipID, guid, destinationSystem)
                except Exception as e:
                    log.exception('Exception caught while making non-ego ball jump %s' % e)

    def OnSessionChanged(self, isremote, session, change):
        if 'locationid' in change and self.InJump():
            oldLocation, newLocation = change['locationid']
            try:
                if IsSolarSystem(newLocation):
                    destinationScenePath, security = self._GetPathAndSecurity(self.destSystemID)
                    GetSceneManager().UnregisterScene('default', ignoreCamera=True)
                    GetSceneManager().RegisterScene(self.destinationScene, 'default')
                    if self.JUMP_FINISH_DELAY > 0:
                        log.error('DELAYING THE JUMP END BY %d ms' % self.JUMP_FINISH_DELAY)
                        blue.synchro.SleepSim(self.JUMP_FINISH_DELAY)
                    self.spaceSubwayEffect.SetLook(destinationScenePath, security)
                    self.spaceSubwayEffect.SetDestinationScene(self.destinationScene)
                else:
                    log.error('Jump got a session change without a new system location, got change from %s to %s. Ending this!' % (oldLocation, newLocation))
            finally:
                self.FinishJump()

    def StartJumpForAudience(self, shipID, jumpType, destinationSystem):
        self.LogInfo("Starting jump '%s' of %s for players on grid" % (jumpType, shipID))
        shipModel = self._GetModel(shipID, makeFake=False)
        if shipModel is None:
            self.LogInfo("Couldn't find the jumping ball, so no effect for you")
            return
        effect = EveSpaceSubwayEffect()
        effect.SetOriginScene(self.GetScene())
        effect.SetEffect(jumpType)
        originOrientation = None
        if destinationSystem is not None:
            originOrientation = self._GetOriginOrientation(destinationSystem)
        effect.HideJumpingShip(shipModel, originOrientation=originOrientation, callback=effect.CleanupLite)

    def StartJump(self, shipID, targetID, jumpType, destinationSystem):
        self.LogInfo("Starting jump '%s' for %s through %s (%s to %s)" % (jumpType,
         shipID,
         targetID,
         self.originSystemID,
         self.destSystemID))
        if self.spaceSubwayEffect is not None:
            self.spaceSubwayEffect.DisableCleanupCallback()
            self.spaceSubwayEffect = None
            self.LogInfo('Starting a jump with another still active, trying my best to make it not mess up anything')
        PreJumpServiceCalls(self.gateID, self.destSystemID)
        self.originScene = self.GetScene()
        if self.destSystemID is not None:
            destinationScenePath, security = self._GetPathAndSecurity(self.destSystemID)
            self.destinationScene, _ = GetSceneManager().LoadScene(destinationScenePath, registerKey='default', applyScene=False)
        destinationStargate = cfg.mapSolarSystemContentCache[session.solarsystemid].stargates.get(targetID, None)
        destinationID = None
        if destinationStargate is not None:
            destinationID = destinationStargate.destination
        jumpInfo = {'jumpType': jumpType,
         'shipID': self.shipID,
         'gateID': self.gateID,
         'originSystemID': self.originSystemID,
         'destinationSystemID': self.destSystemID}
        self.spaceSubwayEffect = EveSpaceSubwayEffect(self.Cleanup, destinationID, jumpInfo)
        self.spaceSubwayEffect.SetOriginScene(self.originScene)
        self.spaceSubwayEffect.SetEffect(jumpType)
        scenePath, security = self._GetPathAndSecurity(session.solarsystemid)
        self.spaceSubwayEffect.SetLook(scenePath, security)
        self.lockedBalls = []
        for ballID in [targetID, shipID]:
            ball = GetBall(ballID)
            if ball and hasattr(ball, 'LockFromRelease'):
                self.lockedBalls.append(ball)
                ball.LockFromRelease()

        shipModel = self._GetModel(shipID)
        if GetSceneManager().GetActivePrimaryCamera().cameraID == evecamera.CAM_SHIPPOV:
            shipModel.display = False
            shipModel = None
        targetBall = GetBall(targetID)
        gateModel = None
        originOrientation = None
        if targetBall:
            gateModel = targetBall.GetModel()
        elif destinationSystem is not None:
            originOrientation = self._GetOriginOrientation(destinationSystem)
        self.spaceSubwayEffect.StartEffectForOwner(gateModel, shipModel, originOrientation)

    def FinishJump(self):
        self.LogInfo('Finishing jump. Activating destination')
        self.spaceSubwayEffect.Stop(self.FORCE_KILL_SWITCH)

    def Cleanup(self):
        self.LogInfo('Final clean up. Releasing all balls from last system ')
        self.spaceSubwayEffect = None
        for ball in self.lockedBalls:
            ball.UnlockFromRelease(self.originScene)

        self.lockedBalls = []
        self.originScene = None
        self.destinationScene = None

    def GetScene(self):
        return GetSceneManager().GetRegisteredScene('default')

    def _GetOriginOrientation(self, destinationSystem):
        here = sm.GetService('map').GetItem(session.solarsystemid2)
        there = sm.GetService('map').GetItem(destinationSystem)
        yaw, pitch = mathCommon.GetYawAndPitchAnglesRad((here.x, here.y, here.z), (there.x, there.y, there.z))
        return geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, 0)

    def _GetPathAndSecurity(self, solarsystemID):
        system = cfg.mapSystemCache.get(solarsystemID, None)
        if system is None:
            return (None, None)
        security = system.securityStatus
        scenePath = GetSceneManager().GetSceneForSystem(solarsystemID)
        return (scenePath, security)

    def _GetModel(self, ballID, makeFake = True):
        model = None
        ball = GetBall(ballID)
        if ball is not None:
            try:
                model = ball.GetModel()
            except AttributeError:
                pass

            if not model and makeFake:
                model = trinity.EveEffectRoot2()
                model.translationCurve = ball
                model.rotationCurve = ball
        elif makeFake:
            model = trinity.EveEffectRoot2()
        return model

    def HandleSkinChange(self, newModel):
        if self.spaceSubwayEffect is not None:
            self.spaceSubwayEffect.ChangeSkin(newModel)
            return True
        return False

    def OnGraphicSettingsChanged(self, changes):
        if self.InJump() and gfxsettings.UI_CAMERA_SHAKE_ENABLED in changes:
            self.spaceSubwayEffect.SetShake(self.spaceSubwayEffect.IsShakeEnabled())
