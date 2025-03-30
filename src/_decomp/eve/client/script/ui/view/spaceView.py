#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\spaceView.py
import evecamera
from carbon.common.script.sys.serviceConst import ROLE_CONTENT
from carbonui import uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.inflight.navigation import InflightLayer
from eve.client.script.ui.services.viewStateSvc import View
from eve.common.script.sys.eveCfg import IsDockedInStructure
from evecamera.locationalcamera import get_orbit_camera_by_solar_system, get_corrected_camera_id
from eveuniverse.solar_systems import is_orbit_camera_range_limited, is_tactical_camera_suppressed, is_orbit_camera_range_limited_moderate

class SpaceView(View):
    __guid__ = 'viewstate.SpaceView'
    __notifyevents__ = ['OnActiveCameraChanged']
    __dependencies__ = ['standing',
     'map',
     'wallet',
     'space',
     'stateSvc',
     'bracket',
     'target',
     'fleet',
     'surveyScan',
     'autoPilot',
     'neocom',
     'corp',
     'alliance',
     'skillqueue',
     'dungeonTracking',
     'transmission',
     'clonejump',
     'assets',
     'charactersheet',
     'trigger',
     'contracts',
     'certificates',
     'sov',
     'turret',
     'posAnchor',
     'michelle',
     'sceneManager',
     'structureProximityTracker',
     'uiHighlightingService',
     'dockingHeroNotification']
    __layerClass__ = InflightLayer
    __subLayers__ = [('l_spaceTutorial', None, None),
     ('l_space_ui', None, None),
     ('l_bracket', None, None),
     ('l_sensorSuite', None, None),
     ('l_tactical', None, None)]
    __overlays__ = {'shipui', 'sidePanels', 'target'}

    def __init__(self):
        View.__init__(self)
        self.solarSystemID = None
        self.keyDownEvent = None

    def LoadView(self, change = None, **kwargs):
        self.solarSystemID = session.solarsystemid
        if eve.session.role & ROLE_CONTENT:
            sm.StartService('scenario')
        self.bracket.Reload()

    def LoadCamera(self, cameraID = None, reopen = False):
        if cameraID is None:
            sceneMan = sm.GetService('sceneManager')
            currCam = sceneMan.GetActivePrimaryCamera()
            if currCam:
                if not currCam.IsLocked() or self._PrimaryCameraNeedsCorrecting(currCam):
                    self.ActivatePrimaryCamera()
            else:
                self.ActivatePrimaryCamera()
        else:
            sm.GetService('sceneManager').SetPrimaryCamera(cameraID)

    def UnloadView(self):
        self.LogInfo('unloading: removed ballpark and cleared effects')
        uicore.layer.main.state = uiconst.UI_PICKCHILDREN

    def ShowView(self, **kwargs):
        View.ShowView(self, **kwargs)
        self.keyDownEvent = uicore.event.RegisterForTriuiEvents([uiconst.UI_KEYDOWN], self.CheckKeyDown)

    def HideView(self):
        if self.keyDownEvent:
            uicore.event.UnregisterForTriuiEvents(self.keyDownEvent)
        View.HideView(self)

    def CheckShouldReopen(self, newKwargs, cachedKwargs):
        reopen = False
        if newKwargs == cachedKwargs or 'changes' in newKwargs and 'solarsystemid' in newKwargs['changes']:
            reopen = True
        return reopen

    def CheckKeyDown(self, *args):
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        alt = uicore.uilib.Key(uiconst.VK_MENU)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if not ctrl and alt and not shift and session.solarsystemid:
            self.bracket.ShowOwnShip()
        return 1

    def GetRegisteredCameraID(self):
        if IsDockedInStructure():
            return evecamera.CAM_SHIPORBIT
        solar_system_id = session.solarsystemid
        cameraID = settings.char.ui.Get('spaceCameraID', get_orbit_camera_by_solar_system(solar_system_id))
        cameraID = get_corrected_camera_id(cameraID, solar_system_id)
        return cameraID

    def _PrimaryCameraNeedsCorrecting(self, currCam):
        primaryCameraID = currCam.cameraID
        correctedPrimaryCameraID = get_corrected_camera_id(primaryCameraID, session.solarsystemid2)
        needsCorrecting = primaryCameraID != correctedPrimaryCameraID
        return needsCorrecting

    def OnActiveCameraChanged(self, cameraID):
        tacticalSvc = sm.GetService('tactical')
        if tacticalSvc.IsTacticalOverlayActive():
            tacticalSvc.ShowTacticalOverlay()
        else:
            tacticalSvc.HideTacticalOverlay()

    def ActivatePrimaryCamera(self):
        cameraID = self.GetRegisteredCameraID()
        sceneMan = sm.GetService('sceneManager')
        return sceneMan.SetPrimaryCamera(cameraID)
