#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\sensorSuiteService.py
import math
import audio2
import bluepy
import gametime
import locks
import signals
import trinity
import uthread
import uthread2
from carbon.common.lib.const import SEC
from carbon.common.script.sys import service
from carbon.common.script.util.logUtil import LogException
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import IsUnder
from eve.common.lib.appConst import AU
from eve.common.script.sys import eveCfg
from eveexceptions import UserError
from eveuniverse.solar_systems import is_sensor_overlay_suppressed
from sensorsuite.error import InvalidClientStateError
import sensorsuite.overlay.const as overlayConst
from sensorsuite.overlay import sitetype
from sensorsuite.overlay.const import SWEEP_CYCLE_TIME, SWEEP_START_GRACE_TIME_SEC, SWEEP_START_GRACE_TIME, SUPPRESS_GFX_WARPING, SUPPRESS_GFX_NO_UI
from sensorsuite.overlay.anomalies import AnomalyHandler
from sensorsuite.overlay.bookmarks import BookmarkHandler, SharedBookmarkHandler
from sensorsuite.overlay.controllers.probescanner import ProbeScannerController
from sensorsuite.overlay.gfxhandler import GfxHandler
from sensorsuite.overlay.missions import MissionHandler
from sensorsuite.overlay.signatures import SignatureHandler
from sensorsuite.overlay.spacesitecontroller import SpaceSiteController
from sensorsuite.overlay.staticsites import StaticSiteHandler
from sensorsuite.overlay.structures import StructureHandler
SENSOR_SUITE_ENABLED = 'sensorSuiteEnabled'
MAX_MOUSEOVER_RANGE = 40.0
MAX_MOUSEOVER_RANGE_SQUARED = MAX_MOUSEOVER_RANGE ** 2
MAX_OVERLAPPING_RANGE_SQUARED = 900.0
MAX_RTPC_VALUE = 99
BRACKET_OVERLAP_DISTANCE = 8
SWEEP_CYCLE_TIME_SEC = float(SWEEP_CYCLE_TIME) / SEC
UPDATE_STRUCTURES_DELAY = 1000
UPDATE_SITES_DELAY = 200

class SensorSuiteService(service.Service):
    __guid__ = 'svc.sensorSuite'
    __notifyevents__ = ['DoBallRemove',
     'DoBallsRemove',
     'OnAgentMissionChanged',
     'OnBallAdded',
     'OnBallparkSetState',
     'OnEnterSpace',
     'OnHideUI',
     'OnClientEvent_JumpStarted',
     'OnClientEvent_JumpExecuted',
     'OnRefreshBookmarks',
     'OnReleaseBallpark',
     'OnShowUI',
     'OnSignalTrackerAnomalyUpdate',
     'OnSignalTrackerFullState',
     'OnSignalTrackerSignatureUpdate',
     'OnSignalTrackerStructureUpdate',
     'OnSpecialFX',
     'OnStructuresVisibilityUpdated',
     'OnSystemScanDone',
     'OnUpdateWindowPosition',
     'OnClientEvent_WarpStarted',
     'OnClientEvent_WarpFinished']
    __dependencies__ = ['audio',
     'bookmarkSvc',
     'michelle',
     'scanSvc',
     'sceneManager',
     'viewState']
    __startupdependencies__ = []

    def Run(self, *args):
        service.Service.Run(self)
        self.isOverlayActive = True
        self.toggleLock = locks.RLock()
        self.resultEffectsThread = None
        self.messenger = signals.Messenger()
        self.gfxHandler = GfxHandler(self, self.sceneManager, self.michelle)
        self.siteController = SpaceSiteController(self, self.michelle)
        self.siteController.AddSiteHandler(sitetype.ANOMALY, AnomalyHandler())
        self.siteController.AddSiteHandler(sitetype.SIGNATURE, SignatureHandler())
        self.siteController.AddSiteHandler(sitetype.STATIC_SITE, StaticSiteHandler())
        self.siteController.AddSiteHandler(sitetype.BOOKMARK, BookmarkHandler(self, self.bookmarkSvc))
        self.siteController.AddSiteHandler(sitetype.SHARED_BOOKMARK, SharedBookmarkHandler(self, self.bookmarkSvc))
        self.siteController.AddSiteHandler(sitetype.MISSION, MissionHandler(self.bookmarkSvc))
        self.siteController.AddSiteHandler(sitetype.STRUCTURE, StructureHandler())
        self.Initialize()
        self.UpdateVisibleStructures()

    def IsSweepDone(self):
        return self.systemReadyTime and not self.sensorSweepActive

    def IsSolarSystemReady(self):
        if session.solarsystemid is None:
            return False
        bp = self.michelle.GetBallpark()
        if bp is None:
            return False
        if not bp.ego:
            return False
        return True

    def NotifySweepStartedIfRequired(self, handler, messageName):
        if messageName is overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SWEEP_STARTED and self.sweepStartedData is not None:
            uthread.new(handler, *self.sweepStartedData)

    def Subscribe(self, messageName, handler):
        self.NotifySweepStartedIfRequired(handler, messageName)
        self.messenger.SubscribeToMessage(messageName, handler)

    def Unsubscribe(self, messageName, handler):
        self.messenger.UnsubscribeFromMessage(messageName, handler)

    def SendMessage(self, messageName, *args, **kwargs):
        self.messenger.SendMessage(messageName, *args, **kwargs)

    def Initialize(self):
        self.siteController.Clear()
        self.probeScannerController = ProbeScannerController(self.scanSvc, self.michelle, self.siteController)
        self.locatorFadeInTimeSec = 0.25
        self.doMouseTrackingUpdates = False
        self.systemReadyTime = None
        self.sitesUnderCursor = set()
        leftPush, rightPush = uicore.layer.sidePanels.GetSideOffset()
        self.OnUpdateWindowPosition(leftPush, rightPush)
        self.sensorSweepActive = False
        self.sweepStartedData = None

    def UpdateScanner(self, removedSites):
        targetIDs = []
        for siteData in removedSites:
            if siteData.GetSiteType() in (sitetype.ANOMALY, sitetype.SIGNATURE):
                targetIDs.append(siteData.targetID)

        if targetIDs:
            self.scanSvc.ClearResults(*targetIDs)

    def InjectScannerResults(self, siteType):
        sitesById = self.siteController.siteMaps.GetSiteMapByKey(siteType)
        self.probeScannerController.InjectSiteScanResults(sitesById.itervalues())

    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, *args, **kw):
        if shipID == session.shipid:
            if guid is not None and 'effects.JumpOut' in guid:
                self.LogInfo('Jumping out, hiding the overlay')
                self._Hide()

    def OnEnterSpace(self):
        self.Reset()
        if session.solarsystemid and session.structureid is None:
            self.Initialize()
            self._SetOverlayActive(settings.char.ui.Get(SENSOR_SUITE_ENABLED, True))
            self.LogInfo('Entered new system', session.solarsystemid)
            try:
                sm.RemoteSvc('scanMgr').SignalTrackerRegister()
            except UserError as e:
                if e.msg == 'UnMachoDestination':
                    self.LogInfo('Entered new system failed due to match as session seems to have changed')
                    return
                raise

            for siteType in (sitetype.BOOKMARK, sitetype.MISSION, sitetype.SHARED_BOOKMARK):
                self.siteController.GetSiteHandler(siteType).LoadSites(session.solarsystemid)

            if self.IsOverlaySuppressed():
                self._Hide()
                self.messenger.SendMessage(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_DISABLED)
            elif self.isOverlayActive:
                self._Show()
                self.messenger.SendMessage(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_ENABLED)
            ballpark = self.michelle.GetBallpark()
            if ballpark and ballpark.ego:
                self._InitiateSensorSweep()

    def OnReleaseBallpark(self):
        self.Reset()

    def OnBallparkSetState(self):
        if session.solarsystemid and session.structureid is None and not sm.GetService('subway').InJump():
            self._InitiateSensorSweep()

    def _InitiateSensorSweep(self):
        self.LogInfo('Ballpark is ready so we start the sweep timer')
        self.systemReadyTime = gametime.GetSimTime()
        self.StartSensorSweep()

    def Reset(self):
        self.LogInfo('Clearing all overlay objects')
        if self.resultEffectsThread:
            self.resultEffectsThread.kill()
            self.resultEffectsThread = None
        self.siteController.ClearFromBallpark()
        self.siteController.Clear()
        uicore.layer.sensorSuite.Flush()
        self.gfxHandler.StopGfxSwipe()
        self.gfxHandler.StopSwipeThread()

    def IsOverlaySuppressed(self):
        return is_sensor_overlay_suppressed(session.solarsystemid)

    def IsOverlayActive(self):
        if self.IsOverlaySuppressed():
            return False
        return self.isOverlayActive

    def ToggleOverlay(self):
        if self.IsOverlaySuppressed():
            return
        with self.toggleLock:
            self.LogInfo('Toggle Overlay')
            if self.isOverlayActive:
                self.DisableSensorOverlay()
            else:
                self.EnableSensorOverlay()

    def DisableSensorOverlay(self):
        self.LogInfo('DisableSensorOverlay')
        if self.isOverlayActive:
            self._SetOverlayActive(False)
            if not self.sensorSweepActive:
                self._Hide()
            self.messenger.SendMessage(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_DISABLED)

    def EnableSensorOverlay(self):
        self.LogInfo('EnableSensorOverlay')
        if not self.isOverlayActive:
            self._SetOverlayActive(True)
            if not self.sensorSweepActive:
                self._Show()
            self.messenger.SendMessage(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_ENABLED)

    def _SetOverlayActive(self, isActive):
        self.isOverlayActive = isActive
        settings.char.ui.Set(SENSOR_SUITE_ENABLED, isActive)

    def _Show(self):
        self.LogInfo('Showing overlay')
        try:
            if not self.sensorSweepActive:
                self.UpdateVisibleSites()
                self.UpdateVisibleStructures()
                self.audio.SendUIEvent('ui_scanner_stop')
                self.EnableMouseTracking()
        except InvalidClientStateError:
            pass

    def _Hide(self):
        self.LogInfo('Hiding overlay')
        self.gfxHandler.StopGfxSwipe()
        self.UpdateVisibleSites()
        self.UpdateVisibleStructures()
        self.audio.SendUIEvent('ui_scanner_stop')
        self.doMouseTrackingUpdates = False

    def EnableMouseTracking(self):
        if not self.doMouseTrackingUpdates:
            self.doMouseTrackingUpdates = True
            uthread.new(self.UpdateMouseTracking).context = 'sensorSuite::UpdateMouseTracking'

    def StartSensorSweep(self):
        uthread.new(self._DoSystemEnterScan)

    def TryFadeOutBracketAndReturnCurveSet(self, curveSet, points, siteData, totalDuration):
        try:
            locatorData = self.siteController.spaceLocations.GetBySiteID(siteData.siteID)
            curveSet = animations.FadeTo(locatorData.bracket, startVal=0.0, endVal=1.0, duration=totalDuration, curveType=points, curveSet=curveSet)
        except KeyError:
            pass

        return curveSet

    def GetSiteListOrderedByDelay(self, ballpark, sweepCycleTimeSec, viewAngleInPlane):
        if ballpark is None:
            raise InvalidClientStateError("We don't have a ballpark")
        myBall = ballpark.GetBall(ballpark.ego)
        if myBall is None:
            raise InvalidClientStateError("We don't have an active ship in the park")
        mx, mz = myBall.x, myBall.z
        sitesOrdered = []
        pi2 = math.pi * 2
        for siteData in self.GetVisibleSites():
            if sitetype.IsSiteInstantlyAccessible(siteData):
                sitesOrdered.append((0, siteData))
                continue
            x, y, z = siteData.position
            dx, dz = x - mx, z - mz
            angle = math.atan2(-dz, dx) - viewAngleInPlane
            angle %= pi2
            ratioOfCircle = angle / pi2
            delay = SWEEP_START_GRACE_TIME_SEC + sweepCycleTimeSec * ratioOfCircle
            sitesOrdered.append((delay, siteData))

        sitesOrdered.sort()
        return sitesOrdered

    def GetVisibleSites(self):
        return self.siteController.GetVisibleSites()

    def SetupSiteSweepAnimation(self, sitesOrdered):
        curveSet = animations.CreateCurveSet(useRealTime=False)
        for delay, siteData in sitesOrdered:
            points, totalDuration = self.GetLocationFlashCurve(delay)
            curveSet = self.TryFadeOutBracketAndReturnCurveSet(curveSet, points, siteData, totalDuration)

    def _DoSystemEnterScan(self):
        self.LogInfo('_DoSystemEnterScan entered')
        if not eveCfg.InSpace():
            return
        self.sensorSweepActive = True
        try:
            self.CreateResults()
            viewAngleInPlane = self.gfxHandler.GetViewAngleInPlane()
            self.LogInfo('Sensor sweep stating from angle', viewAngleInPlane)
            ballpark = self.michelle.GetBallpark()
            sitesOrdered = self.GetSiteListOrderedByDelay(ballpark, SWEEP_CYCLE_TIME_SEC, viewAngleInPlane)
        except InvalidClientStateError:
            self.sensorSweepActive = False
            return

        if self.IsOverlayActive():
            self.SetupSiteSweepAnimation(sitesOrdered)
            self.gfxHandler.StartGfxSwipeThread(viewAngleInPlane=viewAngleInPlane)
            self.audio.SendUIEvent('ui_scanner_start')
            self.resultEffectsThread = uthread.new(self.PlayResultEffects, sitesOrdered)
        else:
            self.sensorSweepActive = False
            self._Hide()
        self.LogInfo('Sweep started observers notified')
        self.sweepStartedData = (self.systemReadyTime,
         SWEEP_CYCLE_TIME_SEC,
         viewAngleInPlane,
         sitesOrdered,
         SWEEP_START_GRACE_TIME_SEC)
        self.SendMessage(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SWEEP_STARTED, *self.sweepStartedData)

    def ShowSiteDuringSweep(self, locatorData, scene, siteData, sleepTimeSec, soundLocators, vectorCurve):
        ball = locatorData.ballRef()
        if ball is None:
            return
        audio = audio2.AudEmitter('sensor_overlay_site_%s' % str(siteData.siteID))
        obs = trinity.TriObserverLocal()
        obs.observer = audio
        vectorSequencer = trinity.TriVectorSequencer()
        vectorSequencer.operator = trinity.TRIOP_MULTIPLY
        vectorSequencer.functions.append(ball)
        vectorSequencer.functions.append(vectorCurve)
        tr = trinity.EveRootTransform()
        tr.name = 'sensorSuiteSoundLocator_%s' % str(siteData.siteID)
        tr.translationCurve = vectorSequencer
        tr.observers.append(obs)
        scene.objects.append(tr)
        soundLocators.append(tr)
        uthread2.SleepSim(sleepTimeSec)
        if siteData.GetSiteType() == sitetype.ANOMALY:
            audio.SendEvent('ui_scanner_result_anomaly')
        elif siteData.GetSiteType() == sitetype.SIGNATURE:
            audio.SendEvent('ui_scanner_result_signature')
        locatorData.bracket.DoEntryAnimation(enable=False)
        locatorData.bracket.state = uiconst.UI_DISABLED

    def PlayResultEffects(self, sitesOrdered):
        self.LogInfo('PlayResultEffects')
        scene = self.sceneManager.GetRegisteredScene('default')
        soundLocators = []
        invAU = 1.0 / AU
        vectorCurve = trinity.Tr2CurveVector3()
        vectorCurve.AddKey(0, (invAU, invAU, invAU))
        try:
            if self.systemReadyTime is None:
                return
            startTimeSec = float(self.systemReadyTime) / SEC
            for delaySec, siteData in sitesOrdered:
                if not self.siteController.spaceLocations.ContainsSite(siteData.siteID):
                    continue
                if sitetype.IsSiteInstantlyAccessible(siteData):
                    continue
                locatorData = self.siteController.spaceLocations.GetBySiteID(siteData.siteID)
                playTimeSec = startTimeSec + delaySec
                now = float(gametime.GetSimTime()) / SEC
                sleepTimeSec = max(0, playTimeSec - now)
                self.ShowSiteDuringSweep(locatorData, scene, siteData, sleepTimeSec, soundLocators, vectorCurve)

            currentTimeSec = float(gametime.GetSimTime()) / SEC
            endTimeSec = startTimeSec + SWEEP_START_GRACE_TIME_SEC + SWEEP_CYCLE_TIME_SEC
            timeLeftSec = endTimeSec - currentTimeSec
            if timeLeftSec > 0:
                uthread2.SleepSim(timeLeftSec)
            self.audio.SendUIEvent('ui_scanner_stop')
            self.sensorSweepActive = False
            if not self.IsOverlayActive():
                self._Hide()
            else:
                for locatorData in self.siteController.spaceLocations.IterLocations():
                    if not sitetype.IsSiteInstantlyAccessible(locatorData.siteData):
                        locatorData.bracket.DoEnableAnimation()
                        locatorData.bracket.state = uiconst.UI_NORMAL

            uthread2.SleepSim(1.0)
            self.DoScanEnded(sitesOrdered)
            self.audio.SendUIEvent('ui_scanner_stop')
            self.SendMessage(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SWEEP_ENDED)
            self.UpdateVisibleSites()
        finally:
            self.sensorSweepActive = False
            if scene is not None:
                for tr in soundLocators:
                    if tr in scene.objects:
                        scene.objects.remove(tr)

    def DoScanEnded(self, sitesOrdered):
        self.LogInfo('DoScanEnded')
        if len(sitesOrdered) > 0:
            self.audio.SendUIEvent('ui_scanner_result_positive')
        else:
            self.audio.SendUIEvent('ui_scanner_result_negative')

    def CreateResults(self):
        self.LogInfo('CreateResults')
        self.gfxHandler.WaitForSceneReady()
        for siteData in self.GetVisibleSites():
            self.siteController.AddSiteToSpace(siteData, animate=False)

    def GetLocationFlashCurve(self, delay):
        totalDuration = delay + self.locatorFadeInTimeSec
        points = []
        totalTime = 0
        for keyDuration, keyValue in ((delay, 0.0), (self.locatorFadeInTimeSec, 1.0)):
            totalTime += keyDuration
            points.append((totalTime / totalDuration, keyValue))

        return (points, totalDuration)

    def IsSiteBall(self, ballID):
        return self.GetBracketByBallID(ballID) is not None

    def GetBracketByBallID(self, ballID):
        return self.siteController.spaceLocations.GetBracketByBallID(ballID)

    def GetBracketBySiteID(self, siteID):
        return self.siteController.spaceLocations.GetBracketBySiteID(siteID)

    def OnRefreshBookmarks(self):
        self.LogInfo('OnRefreshBookmarks')
        if session.solarsystemid:
            for siteType in (sitetype.BOOKMARK, sitetype.SHARED_BOOKMARK):
                self.siteController.GetSiteHandler(siteType).UpdateSites(session.solarsystemid)

            self.UpdateVisibleSites()

    def OnAgentMissionChanged(self, *args, **kwargs):
        self.siteController.GetSiteHandler(sitetype.MISSION).UpdateSites(session.solarsystemid)

    def OnSignalTrackerFullState(self, solarSystemID, fullState, shouldRemoveOldSites = False):
        self.LogInfo('OnSignalTrackerFullState', solarSystemID, fullState)
        anomalies, signatures, staticSites, structures = fullState
        for siteType, rawSites in ((sitetype.ANOMALY, anomalies),
         (sitetype.SIGNATURE, signatures),
         (sitetype.STATIC_SITE, staticSites),
         (sitetype.STRUCTURE, structures)):
            addedSites = rawSites or dict()
            removedSites = set()
            siteHandler = self.siteController.GetSiteHandler(siteType)
            if shouldRemoveOldSites:
                sites = siteHandler.GetSites().keys()
                for siteID in sites:
                    if siteID not in addedSites:
                        removedSites.add(siteID)

            if addedSites or removedSites:
                siteHandler.ProcessSiteUpdate(addedSites, removedSites)

        self.probeScannerController.InjectSiteScanResults(self.siteController.siteMaps.IterSitesByKeys(sitetype.ANOMALY, sitetype.SIGNATURE))
        sm.GetService('scanSvc').PruneSites()

    def OnSignalTrackerAnomalyUpdate(self, solarSystemID, addedAnomalies, removedAnomalies):
        self.LogInfo('OnSignalTrackerAnomalyUpdate', solarSystemID, addedAnomalies, removedAnomalies)
        self.siteController.GetSiteHandler(sitetype.ANOMALY).ProcessSiteUpdate(addedAnomalies, removedAnomalies)

    def OnSignalTrackerSignatureUpdate(self, solarSystemID, addedSignatures, removedSignatures):
        self.LogInfo('OnSignalTrackerSignatureUpdate', solarSystemID, addedSignatures, removedSignatures)
        self.siteController.GetSiteHandler(sitetype.SIGNATURE).ProcessSiteUpdate(addedSignatures, removedSignatures)

    def OnSignalTrackerStructureUpdate(self, solarSystemID, addedStructures, removedStructures):
        self.LogInfo('OnSignalTrackerStructureUpdate', solarSystemID, addedStructures, removedStructures)
        self.siteController.GetSiteHandler(sitetype.STRUCTURE).ProcessSiteUpdate(addedStructures, removedStructures)

    def OnUpdateWindowPosition(self, leftPush, rightPush):
        uicore.layer.sensorsuite.padLeft = -leftPush
        uicore.layer.sensorsuite.padRight = -rightPush

    def IsMouseInSpaceView(self):
        if self.viewState.IsViewActive('inflight'):
            mouseOver = uicore.uilib.mouseOver
            for uiContainer in (uicore.layer.inflight, uicore.layer.sensorsuite, uicore.layer.bracket):
                if mouseOver is uiContainer or IsUnder(mouseOver, uiContainer):
                    return True

        return False

    @bluepy.TimedFunction('sensorSuiteService::UpdateMouseHoverSound')
    def UpdateMouseHoverSound(self, activeBracket, bestProximity, closestBracket, lastSoundStrength):
        soundStrength = bestProximity or 0
        if closestBracket is not None:
            if soundStrength != 0 or lastSoundStrength != 0:
                if lastSoundStrength == 0 or activeBracket != closestBracket:
                    signalStrength = MAX_RTPC_VALUE
                    self.audio.SendUIEvent(closestBracket.data.hoverSoundEvent)
                    self.audio.SetGlobalRTPC('scanner_signal_strength', min(signalStrength, MAX_RTPC_VALUE))
                    self.audio.SendUIEvent('ui_scanner_state_difficulty_easy')
                    self.audio.SendUIEvent('ui_scanner_mouseover')
                    activeBracket = closestBracket
                self.audio.SetGlobalRTPC('scanner_mouseover', soundStrength)
        elif soundStrength == 0 and lastSoundStrength > 0:
            self.DisableMouseOverSound()
            activeBracket = None
        lastSoundStrength = soundStrength
        return (activeBracket, lastSoundStrength)

    @bluepy.TimedFunction('sensorSuiteService::UpdateMouseTracking')
    def UpdateMouseTracking(self):
        self.LogInfo('Mouse tracking update thread started')
        lastSoundStrength = 0.0
        activeBracket = None
        self.sitesUnderCursor = set()
        self.audio.SetGlobalRTPC('scanner_mouseover', 0)
        while self.doMouseTrackingUpdates:
            try:
                if not self.IsMouseInSpaceView():
                    if activeBracket is not None:
                        self.DisableMouseOverSound()
                        activeBracket = None
                        lastSoundStrength = 0.0
                    continue
                desktopWidth = uicore.desktop.width
                desktopHeight = uicore.desktop.height
                mouseX = uicore.uilib.x
                mouseY = uicore.uilib.y
                self.currentOverlapCoordinates = (mouseX, mouseY)
                closestBracket = None
                bestProximity = None
                for data in self.siteController.spaceLocations.IterLocations():
                    self.sitesUnderCursor.discard(data.siteData)
                    bracket = data.bracket
                    if bracket is None or bracket.destroyed:
                        continue
                    if bracket.state == uiconst.UI_DISABLED:
                        continue
                    centerX = bracket.left + bracket.width / 2
                    centerY = bracket.top + bracket.height / 2
                    if centerX < 0:
                        continue
                    if centerX > desktopWidth:
                        continue
                    if centerY < 0:
                        continue
                    if centerY > desktopHeight:
                        continue
                    if mouseX < centerX - MAX_MOUSEOVER_RANGE:
                        continue
                    if mouseX > centerX + MAX_MOUSEOVER_RANGE:
                        continue
                    if mouseY < centerY - MAX_MOUSEOVER_RANGE:
                        continue
                    if mouseY > centerY + MAX_MOUSEOVER_RANGE:
                        continue
                    dx = centerX - mouseX
                    dy = centerY - mouseY
                    if -BRACKET_OVERLAP_DISTANCE <= dx <= BRACKET_OVERLAP_DISTANCE and -BRACKET_OVERLAP_DISTANCE <= dy <= BRACKET_OVERLAP_DISTANCE:
                        self.sitesUnderCursor.add(data.siteData)
                    if data.siteData.hoverSoundEvent is None:
                        continue
                    distanceSquared = dx * dx + dy * dy
                    if distanceSquared >= MAX_MOUSEOVER_RANGE_SQUARED:
                        continue
                    proximity = MAX_RTPC_VALUE - distanceSquared / MAX_MOUSEOVER_RANGE_SQUARED * MAX_RTPC_VALUE
                    if closestBracket is not None:
                        if proximity < bestProximity:
                            closestBracket = bracket
                            bestProximity = proximity
                    else:
                        closestBracket = bracket
                        bestProximity = proximity

                activeBracket, lastSoundStrength = self.UpdateMouseHoverSound(activeBracket, bestProximity, closestBracket, lastSoundStrength)
            except (ValueError, OverflowError):
                pass
            except Exception:
                LogException('The sound update loop errored out')
            finally:
                uthread2.Sleep(0.025)

        if activeBracket is not None:
            self.DisableMouseOverSound()
        self.LogInfo('Mouse tracking update thread ended')

    def DisableMouseOverSound(self):
        self.audio.SendUIEvent('ui_scanner_mouseover_stop')
        self.audio.SetGlobalRTPC('scanner_mouseover', 0)

    def OnClientEvent_WarpStarted(self, *args):
        self.LogInfo('OnClientEvent_WarpStarted hiding the sweep gfx')
        self.gfxHandler.DisableGfx(SUPPRESS_GFX_WARPING)

    def OnClientEvent_WarpFinished(self, *args):
        self.LogInfo('OnClientEvent_WarpFinished showing the sweep gfx')
        self.gfxHandler.EnableGfx(SUPPRESS_GFX_WARPING)

    def OnShowUI(self):
        self.LogInfo('OnShowUI showing the sweep gfx')
        uicore.layer.sensorsuite.display = True
        self.gfxHandler.EnableGfx(SUPPRESS_GFX_NO_UI)

    def OnHideUI(self):
        self.LogInfo('OnHideUI hiding the sweep gfx')
        uicore.layer.sensorsuite.display = False
        self.gfxHandler.DisableGfx(SUPPRESS_GFX_NO_UI)

    def OnSystemScanDone(self):
        self.probeScannerController.UpdateProbeResultBrackets()

    def GetOverlappingSites(self):
        overlappingBrackets = []
        for siteData in self.sitesUnderCursor:
            bracket = self.siteController.spaceLocations.GetBracketBySiteID(siteData.siteID)
            if bracket:
                overlappingBrackets.append(bracket)

        return overlappingBrackets

    def GetAnomalies(self):
        return self.siteController.GetSiteHandler(sitetype.ANOMALY).GetSites().values()

    def GetAnomaly(self, instanceID):
        anomalies = self.GetAnomalies()
        for anomaly in anomalies:
            if anomaly.instanceID == instanceID:
                return anomaly

    def GetStaticSites(self):
        return self.siteController.GetSiteHandler(sitetype.STATIC_SITE).GetSites().values()

    @uthread2.debounce(1.0)
    def FullyUpdateSignalTrackerDebounced(self):
        self.OnSignalTrackerFullState(session.solarsystemid2, self.scanSvc.GetScanMan().GetFullState(), shouldRemoveOldSites=True)

    def UpdateSignalTracker(self):
        self.OnSignalTrackerFullState(session.solarsystemid2, self.scanSvc.GetScanMan().GetFullState(), shouldRemoveOldSites=False)

    def GetSignatures(self):
        return self.siteController.GetSiteHandler(sitetype.SIGNATURE).GetSites().values()

    def GetLocatedSignatures(self):
        return [ signature for signature in self.GetSignatures() if signature.IsAccurate() ]

    def GetUnknownSignatures(self):
        return [ signature for signature in self.GetSignatures() if not signature.IsAccurate() ]

    def SetSiteFilter(self, siteType, enabled):
        handler = self.siteController.GetSiteHandler(siteType)
        handler.SetFilterEnabled(enabled)
        if siteType in sitetype.STRUCTURE_SITE_TYPES:
            self.UpdateVisibleStructures()
        else:
            self.UpdateVisibleSites()

    def OnStructuresVisibilityUpdated(self):
        self.UpdateVisibleStructures()

    def OnBallAdded(self, slimItem):
        if slimItem.categoryID == const.categoryStructure:
            self.UpdateVisibleStructures()

    def DoBallRemove(self, ball, slimItem, terminal):
        if slimItem.categoryID == const.categoryStructure:
            self.UpdateVisibleStructures()

    def DoBallsRemove(self, pythonBalls, isRelease):
        for _ball, slimItem, _terminal in pythonBalls:
            if slimItem.categoryID == const.categoryStructure:
                self.UpdateVisibleStructures()
                return

    @bluepy.TimedFunction('sensorSuiteService::UpdateVisibleStructures')
    def UpdateVisibleStructures(self):
        setattr(self, 'updateVisibleStructuresTimerThread', AutoTimer(UPDATE_STRUCTURES_DELAY, self._UpdateVisibleStructures))

    @bluepy.TimedFunction('sensorSuiteService::_UpdateVisibleStructures')
    def _UpdateVisibleStructures(self):
        self.LogInfo('UpdateVisibleStructures')
        try:
            if not self.IsSolarSystemReady():
                return
            self.siteController.UpdateSiteVisibility(siteTypesToUpdate=sitetype.STRUCTURE_SITE_TYPES)
        finally:
            self.updateVisibleStructuresTimerThread = None

    @bluepy.TimedFunction('sensorSuiteService::UpdateVisibleSites')
    def UpdateVisibleSites(self):
        setattr(self, 'updateVisibleSitesTimerThread', AutoTimer(UPDATE_SITES_DELAY, self._UpdateVisibleSites))

    @bluepy.TimedFunction('sensorSuiteService::_UpdateVisibleSites')
    def _UpdateVisibleSites(self):
        self.LogInfo('UpdateVisibleSites')
        try:
            if not self.IsSolarSystemReady():
                return
            self.siteController.UpdateSiteVisibility(siteTypesToUpdate=sitetype.NON_STRUCTURE_SITE_TYPES)
        finally:
            self.updateVisibleSitesTimerThread = None

    def GetPositionalSiteItemIDFromTargetID(self, targetID):
        for site in self.siteController.siteMaps.IterSitesByKeys(sitetype.ANOMALY, sitetype.STRUCTURE):
            if site.targetID == targetID:
                return (site.siteID, site.groupID)

        return (None, None)

    def OnClientEvent_JumpStarted(self, *args):
        self._Hide()

    def OnClientEvent_JumpExecuted(self, itemID):
        self._Show()
        self._InitiateSensorSweep()
