#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\deathzone\deathzoneUIController.py
import gametime
import uthread2
from eve.client.script.ui.services.deathzone.deathzoneUIConst import DEATHZONE_VIGNETTE_PARAMS, _LocalUIState
from eve.common.script.mgt.buffBarConst import REMOVE_GENERIC_BUFFBAR_BUTTON_SIGNAL, ADD_GENERIC_BUFFBAR_BUTTON_SIGNAL, Slot_DeathZoneGracePeriod, Slot_DeathZoneProtected, Slot_DeathZoneDamage
from eve.client.script.parklife.sceneManagerConsts import SYSTEM_WIDE_CLOUD_NAME
from uthread2 import sleep_sim, StartTasklet

class DeathZoneUIController(object):
    VIGNETTE_MIN_INTENSITY = 1.25
    VIGNETTE_MAX_INTENSITY = 2.35
    VIGNETTE_MIN_OPACITY = 1.0
    VIGNETTE_MAX_OPACITY = 1.0

    def __init__(self, heroNotification, sceneManager):
        self.trackingData = None
        self.damageTrackerTasklet = None
        self.vignetteIntentisy = 0.0
        self.opacityIntensity = 0.0
        self.heroNotification = heroNotification
        self.sceneManager = sceneManager
        self.controllerTaskletRunning = False
        self.controllerTasklet = None
        self.systemWideCloud = None
        self.commandQueue = uthread2.queue_channel()

    def EnterSafeZoneState(self):
        self.EnsureCommandTaskletIsRunning()
        self.commandQueue.send(self._EnterSafeZoneStateCommand)
        self._HandleDynamicInfiniteCloud(False)

    def EnterDeathZoneState(self, trackingData):
        self.EnsureCommandTaskletIsRunning()
        self.commandQueue.send(self._CreateSetTrackingDataCommand(trackingData))
        self._HandleDynamicInfiniteCloud(True)

    def _HandleDynamicInfiniteCloud(self, isInDeathZone):
        if self.systemWideCloud is None:
            if hasattr(cfg.mapSolarSystemContentCache[session.solarsystemid], 'systemWideCloud'):
                scene = self.sceneManager.GetActiveScene()
                if scene:
                    self.systemWideCloud = scene.objects.FindByName(SYSTEM_WIDE_CLOUD_NAME)
        if self.systemWideCloud is not None:
            self.systemWideCloud.SetControllerVariable('isActive', float(isInDeathZone))

    def Remove(self):
        if self.controllerTasklet is None:
            return
        self.commandQueue.send(self._RemoveCommand)

    def EnsureCommandTaskletIsRunning(self):
        if self.controllerTasklet is None:
            self.controllerTaskletRunning = True
            self.controllerTasklet = StartTasklet(self.UICommandReceiver)

    def _RemoveCommand(self):
        self.trackingData = None
        self.controllerTaskletRunning = False
        self.controllerTasklet = None
        self.systemWideCloud = None
        self._FadeVignetteIntensityAndOpacity(intensity=0, opacity=0)
        self._EnsureBuffBarState(_LocalUIState.UNSPECIFIED)

    def _EnterSafeZoneStateCommand(self):
        if self.trackingData:
            self.trackingData = None
        self._FadeVignetteIntensityAndOpacity(intensity=0, opacity=0)
        self._EnsureBuffBarState(_LocalUIState.SAFE_ZONE)

    def _CreateSetTrackingDataCommand(self, trackingData):

        def fun():
            self.trackingData = trackingData

        return fun

    def UICommandReceiver(self):
        while self.controllerTaskletRunning:
            if self.trackingData is None:
                self.commandQueue.receive()()
            elif len(self.commandQueue) > 0:
                self.commandQueue.receive()()
            if self.trackingData:
                now = gametime.GetSimTime()
                if self.trackingData.IsDamageActive(now):
                    self._EnsureBuffBarState(_LocalUIState.DEATH_ZONE)
                    hullDamageFraction = self.trackingData.GetHullDamageFractionPerTick(now)
                    vignetteIntensity = max(self.VIGNETTE_MIN_INTENSITY, min(1.0, hullDamageFraction / self.VIGNETTE_MAX_INTENSITY))
                    self._FadeVignetteIntensityAndOpacity(intensity=self.VIGNETTE_MAX_INTENSITY, opacity=self.VIGNETTE_MAX_OPACITY)
                else:
                    self._FadeVignetteIntensityAndOpacity(intensity=self.VIGNETTE_MIN_INTENSITY, opacity=self.VIGNETTE_MIN_OPACITY)
                    self._EnsureBuffBarState(_LocalUIState.DEATH_ZONE_GRACE_PERIOD)
                sleep_sim(self.trackingData.damageTickPeriod)

    def _FadeVignetteIntensityAndOpacity(self, intensity, opacity, duration = 1, color = (1.0, 0.0, 0.0, 1.0)):
        self.sceneManager.FadeVignetteToIntensityAndOpacity(duration, DEATHZONE_VIGNETTE_PARAMS, color=color, fromIntensity=self.vignetteIntentisy, toIntensity=intensity, fromOpacity=self.opacityIntensity, toOpacity=opacity)
        self.vignetteIntentisy = intensity
        self.opacityIntensity = opacity

    def _EnsureBuffBarState(self, localUIState):
        if localUIState == _LocalUIState.DEATH_ZONE:
            REMOVE_GENERIC_BUFFBAR_BUTTON_SIGNAL(Slot_DeathZoneGracePeriod)
            REMOVE_GENERIC_BUFFBAR_BUTTON_SIGNAL(Slot_DeathZoneProtected)
            ADD_GENERIC_BUFFBAR_BUTTON_SIGNAL(Slot_DeathZoneDamage)
        elif localUIState == _LocalUIState.DEATH_ZONE_GRACE_PERIOD:
            REMOVE_GENERIC_BUFFBAR_BUTTON_SIGNAL(Slot_DeathZoneProtected)
            REMOVE_GENERIC_BUFFBAR_BUTTON_SIGNAL(Slot_DeathZoneDamage)
            ADD_GENERIC_BUFFBAR_BUTTON_SIGNAL(Slot_DeathZoneGracePeriod)
        elif localUIState == _LocalUIState.SAFE_ZONE:
            REMOVE_GENERIC_BUFFBAR_BUTTON_SIGNAL(Slot_DeathZoneDamage)
            REMOVE_GENERIC_BUFFBAR_BUTTON_SIGNAL(Slot_DeathZoneGracePeriod)
            ADD_GENERIC_BUFFBAR_BUTTON_SIGNAL(Slot_DeathZoneProtected)
        elif localUIState == _LocalUIState.UNSPECIFIED:
            REMOVE_GENERIC_BUFFBAR_BUTTON_SIGNAL(Slot_DeathZoneDamage)
            REMOVE_GENERIC_BUFFBAR_BUTTON_SIGNAL(Slot_DeathZoneGracePeriod)
            REMOVE_GENERIC_BUFFBAR_BUTTON_SIGNAL(Slot_DeathZoneProtected)
