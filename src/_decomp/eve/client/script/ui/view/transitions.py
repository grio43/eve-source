#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\transitions.py
from carbonui.primitives.container import Container
from carbonui.util.color import Color
from eve.client.script.ui.camera.cameraUtil import GetBallWaitForModel, IsDynamicCameraMovementEnabled
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.services.viewStateSvc import Transition
from eve.client.script.ui.shared.dockedUI.lobbyWnd import LobbyWnd
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.lib import appConst as const
import evecamera
import carbonui.const as uiconst
import blue
import localization
import log
import uthread
from carbonui.uicore import uicore

class FadeToBlackTransition(Transition):
    __guid__ = 'viewstate.FadeToBlackTransition'

    def __init__(self, fadeTimeMS = 1000, fadeInTimeMS = None, fadeOutTimeMS = None, **kwargs):
        Transition.__init__(self, **kwargs)
        self.fadeInTimeMS = fadeInTimeMS or fadeTimeMS
        self.fadeOutTimeMS = fadeOutTimeMS or fadeTimeMS

    def StartTransition(self, fromView, toView):
        Transition.StartTransition(self, fromView, toView)
        sm.GetService('loading').FadeIn(self.fadeInTimeMS)

    def EndTransition(self, fromView, toView):
        Transition.EndTransition(self, fromView, toView)
        sm.GetService('loading').FadeOut(self.fadeOutTimeMS, opacityStart=1.0, color=Color.BLACK)


class EmptyTransition(Transition):
    __guid__ = 'viewstate.EmptyTransition'


class FadeToBlackLiteTransition(Transition):
    __guid__ = 'viewstate.FadeToBlackLiteTransition'

    def __init__(self, fadeTimeMS = 1000, fadeInTimeMS = None, fadeOutTimeMS = None, **kwargs):
        Transition.__init__(self, **kwargs)
        self.fadeInTimeMS = fadeInTimeMS or fadeTimeMS
        self.fadeOutTimeMS = fadeOutTimeMS or fadeTimeMS
        self.fadeLayer = None

    def StartTransition(self, fromView, toView):
        Transition.StartTransition(self, fromView, toView)
        viewState = sm.GetService('viewState')
        fadeTimeInSeconds = self.fadeInTimeMS / 1000.0
        sm.GetService('sceneManager').FadeIn(duration=fadeTimeInSeconds)
        self.fadeLayer = Container(name='transition_overlay', parent=viewState.overlayLayerParent, pickState=uiconst.TR2_SPS_OFF, bgColor=Color.BLACK, opacity=0.0)
        uicore.animations.FadeIn(self.fadeLayer, duration=fadeTimeInSeconds, sleep=True)

    def EndTransition(self, fromView, toView):
        fadeTimeInSeconds = self.fadeInTimeMS / 1000.0
        uicore.animations.FadeOut(self.fadeLayer, duration=fadeTimeInSeconds)
        sm.GetService('sceneManager').FadeOut(duration=fadeTimeInSeconds, sleep=True)
        self.fadeLayer.Close()
        del self.fadeLayer
        Transition.EndTransition(self, fromView, toView)


class DeathTransition(Transition):
    __guid__ = 'viewstate.DeathTransition'
    DELAYED_NOTIFICATIONS = (const.notificationTypeCloneActivationMsg, const.notificationTypeCloneActivationMsg2)

    def __init__(self, **kwargs):
        Transition.__init__(self, **kwargs)
        self.keyDownCookie = None
        self.maxWaitSeconds = 10
        self.minWaitSeconds = 2
        self.notifyContainer = None
        self.startTime = None

    def StartTransition(self, fromView, toView):
        Transition.StartTransition(self, fromView, toView)
        duration = max(blue.os.desiredSimDilation, 0.1) * 0.3
        self.AnimateUIOut(duration=duration)
        sm.GetService('audio').SendUIEvent('transition_pod_dead_play')
        self.StartDeathScene()
        sm.GetService('loading').FadeOut(2500)
        self.WaitForMouseUp()
        sm.GetService('loading').FadeIn(500)

    def EndTransition(self, fromView, toView):
        sm.GetService('audio').SendUIEvent('transition_pod_reanimate')
        self.notifyContainer.Close()
        sm.GetService('loading').FadeOut(500)
        duration = max(blue.os.desiredSimDilation, 0.3) * 2
        self.AnimateUIIn(duration=duration)
        Transition.EndTransition(self, fromView, toView)
        for notificationTypeID in self.DELAYED_NOTIFICATIONS:
            sm.GetService('notificationSvc').ProcessDelayedNotifications(notificationTypeID)

        sm.ScatterEvent('OnDeathTransitionEnded')

    def StartDeathScene(self):
        log.LogNotice('DeathTransition:: Starting death scene %s')
        sceneManager = sm.GetService('sceneManager')
        deathHandler = sm.GetService('gameui').playerDeathHandler
        deathScene = getattr(deathHandler, 'podDeathScene', None)
        if deathScene:
            try:
                deathHandler.podDeathScene = None
                sceneManager.SetPrimaryCamera(evecamera.CAM_DEATHSCENE)
                corpse = deathHandler.GetCorpseModel()
                if corpse is not None:
                    corpse.name = 'myCorpse'
                    deathScene.objects.insert(0, corpse)
                else:
                    log.LogWarn('Failed to load corpse model for character %s' % session.charid, channel='svc.viewState')
                pod = deathHandler.GetCapsuleModel()
                deathScene.objects.append(pod)
                sceneManager.SetActiveScene(deathScene)
            except Exception as e:
                log.LogTraceback('Failed at loading podDeathScene: %s' % repr(e), channel='svc.viewState')

        else:
            log.LogTraceback('Unable to load podDeathScene', channel='svc.viewState')
        self.notifyContainer = Container(name='notifyContainer', parent=uicore.desktop, state=uiconst.UI_DISABLED, align=uiconst.BOTTOMLEFT, pos=(20, 0, 500, 100))
        uthread.new(self.WriteCloneActivationText_thread)

    def WriteCloneActivationText_thread(self, *args):
        blue.synchro.SleepSim(1000)
        redColor = (0.9, 0.1, 0.1)
        cloneText = localization.GetByLabel('UI/Inflight/ActivatingClone')
        currentLocation = session.stationid or session.structureid
        if currentLocation:
            locationName = cfg.evelocations.Get(currentLocation).name
        else:
            locationName = ''
        cloneSubText = localization.GetByLabel('UI/Inflight/ActivatingCloneSubText', locationName=locationName)
        cloneSubTextLabel = eveLabel.EveLabelLarge(parent=self.notifyContainer, name='cloneSubTextLabel', text=cloneSubText, align=uiconst.TOPLEFT, bold=True)
        cloneText = localization.GetByLabel('UI/Inflight/ActivatingClone')
        cloneActivatingLabel = eveLabel.EveCaptionLarge(parent=self.notifyContainer, name='cloneActivatingLabel', text='', align=uiconst.TOPLEFT, top=cloneSubTextLabel.top + cloneSubTextLabel.textheight, bold=True)
        uicore.animations.BlinkIn(cloneActivatingLabel, startVal=0.0, endVal=1.0, duration=1.0, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
        cloneSubTextLabel.text = ''
        for char in cloneSubText:
            cloneSubTextLabel.text += char
            sm.GetService('audio').SendUIEvent('ui_text_singlechar_play')
            blue.synchro.SleepSim(20)

        for char in cloneText:
            cloneActivatingLabel.text += char
            sm.GetService('audio').SendUIEvent('ui_text_singlechar_play')
            blue.synchro.SleepSim(20)

    def WaitForMouseUp(self):
        now = blue.os.GetWallclockTime()
        self.startTime = now
        self.endWaitTime = now + self.maxWaitSeconds * const.SEC
        self.breakFromLoop = False
        self.mouseDownCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.ClearBlock)
        while not self.breakFromLoop and blue.os.GetWallclockTime() < self.endWaitTime:
            blue.synchro.Yield()

        uicore.event.UnregisterForTriuiEvents(self.mouseDownCookie)
        self.mouseDownCookie = None
        self.endWaitTime = None
        self.startTime = None
        self.breakFromLoop = False

    def ClearBlock(self, *args):
        now = blue.os.GetWallclockTime()
        if now < self.startTime + self.minWaitSeconds * const.SEC:
            return 1
        self.breakFromLoop = True
        return 1


class SpaceToStationTransition(Transition):
    __guid__ = 'viewstate.SpaceToStationTransition'

    def __init__(self, **kwargs):
        Transition.__init__(self, **kwargs)
        self.hangarDock = ToHangarTransition()
        self.cloning = DeathTransition()

    def StartTransition(self, fromView, toView):
        Transition.StartTransition(self, fromView, toView)
        if self.transitionReason == 'clone':
            self.cloning.StartTransition(fromView, toView)
        else:
            self.hangarDock.StartTransition(fromView, toView)

    def EndTransition(self, fromView, toView):
        if self.transitionReason == 'clone':
            self.cloning.EndTransition(fromView, toView)
        else:
            self.hangarDock.EndTransition(fromView, toView)
        Transition.EndTransition(self, fromView, toView)


class SpaceToStructureTransition(Transition):
    __guid__ = 'viewstate.SpaceToStructureTransition'

    def __init__(self, **kwargs):
        Transition.__init__(self, **kwargs)
        self.dock = self.GetDockTransition()
        self.cloning = DeathTransition()

    def GetDockTransition(self):
        return Transition()

    def StartTransition(self, fromView, toView):
        Transition.StartTransition(self, fromView, toView)
        if self.transitionReason == 'clone':
            self.cloning.StartTransition(fromView, toView)
        else:
            self.dock.StartTransition(fromView, toView)
            sm.ScatterEvent('OnDockingTransitionStart')

    def EndTransition(self, fromView, toView):
        if self.transitionReason == 'clone':
            self.cloning.EndTransition(fromView, toView)
        else:
            self.dock.EndTransition(fromView, toView)
            sm.ScatterEvent('OnDockingTransitionEnd')
        Transition.EndTransition(self, fromView, toView)


class StationToSpaceTransition(FadeToBlackTransition):

    def EndTransition(self, fromView, toView):
        GetBallWaitForModel(session.shipid)
        blue.synchro.SleepWallclock(10)
        FadeToBlackTransition.EndTransition(self, fromView, toView)

    def GetCameraID(self):
        currCamID = sm.GetService('viewState').GetView(ViewState.Space).GetRegisteredCameraID()
        if IsDynamicCameraMovementEnabled() and currCamID == evecamera.CAM_SHIPORBIT:
            return evecamera.CAM_UNDOCK


class CharSelectCreateToSpaceTransition(Transition):

    def __init__(self, fadeTimeMS = 1000, fadeInTimeMS = 250, fadeOutTimeMS = 2000, **kwargs):
        Transition.__init__(self, **kwargs)
        self.fadeInTimeMS = fadeInTimeMS or fadeTimeMS
        self.fadeOutTimeMS = fadeOutTimeMS or fadeTimeMS

    def StartTransition(self, fromView, toView):
        Transition.StartTransition(self, fromView, toView)
        if self._ShouldFadeLoadingLayer():
            sm.GetService('loading').FadeIn(self.fadeInTimeMS)
        sm.GetService('gameui').ResetResourceLoadingIndicatorPosition()

    def EndTransition(self, fromView, toView):
        Transition.EndTransition(self, fromView, toView)
        uthread.new(self._EndTransition)

    def _EndTransition(self):
        sm.ScatterEvent('OnCurrSessionSpaceEnteredFirstTime')
        GetBallWaitForModel(session.shipid)
        if self._ShouldFadeLoadingLayer():
            sm.GetService('loading').FadeOut(self.fadeOutTimeMS, opacityStart=1.0)

    def _ShouldFadeLoadingLayer(self):
        return not sm.GetService('cc').IsIntroPlaying()

    def GetCameraID(self):
        cameraID = sm.GetService('viewState').GetView(ViewState.Space).GetRegisteredCameraID()
        if IsDynamicCameraMovementEnabled():
            if cameraID in (evecamera.CAM_SHIPORBIT, evecamera.CAM_SHIPORBIT_ABYSSAL_SPACE, evecamera.CAM_SHIPORBIT_HAZARD):
                return evecamera.CAM_ENTERSPACE


class ToHangarTransition(FadeToBlackTransition):

    def __init__(self, fadeTimeMS = 500, fadeInTimeMS = 500, fadeOutTimeMS = 2000, **kwargs):
        FadeToBlackTransition.__init__(self, fadeTimeMS, fadeInTimeMS, fadeOutTimeMS, **kwargs)

    def StartTransition(self, fromView, toView):
        sm.ScatterEvent('OnDockingTransitionStart')
        super(ToHangarTransition, self).StartTransition(fromView, toView)

    def EndTransition(self, fromView, toView):
        if session.stationid or session.structureid:
            sm.GetService('viewState').GetView(ViewState.Hangar).OnDocking()
            sm.ScatterEvent('OnDockingTransitionEnd')
            FadeToBlackTransition.EndTransition(self, fromView, toView)


class ToCharCreationTransition(FadeToBlackTransition):

    def StartTransition(self, fromView, toView):
        FadeToBlackTransition.StartTransition(self, fromView, toView)
        sm.GetService('michelle').RemoveBallpark()


class ToStructureFromCharCreationTransition(FadeToBlackTransition):

    def EndTransition(self, fromView, toView):
        self._LoadSceneForCurrentSolarSystem()
        FadeToBlackTransition.EndTransition(self, fromView, toView)

    def _LoadSceneForCurrentSolarSystem(self):
        sceneManager = sm.GetService('sceneManager')
        sceneRes = sceneManager.GetSceneForSystem(session.solarsystemid)
        sceneManager.LoadScene(sceneRes, registerKey='default', applyScene=False)


class HangarToHangarTransition(FadeToBlackLiteTransition):

    def __init__(self, **kwargs):
        super(HangarToHangarTransition, self).__init__(**kwargs)
        self.hangarView = sm.GetService('viewState').GetView(ViewState.Hangar)

    def StartTransition(self, fromView, toView):
        super(HangarToHangarTransition, self).StartTransition(fromView, toView)
        self.hangarView.ClearScene()
        self.hangarView.SetUpModels()

    def EndTransition(self, fromView, toView):
        self.hangarView.OnHangarToHangar()
        FadeToBlackLiteTransition.EndTransition(self, fromView, toView)
