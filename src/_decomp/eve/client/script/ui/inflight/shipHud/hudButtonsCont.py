#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipHud\hudButtonsCont.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui.inflight.shipHud.leftSideButton import LeftSideButtonScanner, LeftSideButtonTactical, LeftSideButtonAutopilot, LeftSideButtonZoomIn, LeftSideButtonZoomOut, LeftSideButtonCameraOrbit, LeftSideButtonCameraTactical, LeftSideButtonCameraPOV, LeftSideButtonStructureAmmoHold
from eve.client.script.ui.inflight.shipHud.leftSideButtons.leftSideButtonCargo import LeftSideButtonCargo
import telemetry
from eve.common.script.sys.eveCfg import IsControllingStructure
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from eve.common.script.sys.idCheckers import IsZarzakh
from eveuniverse.solar_systems import is_scanning_suppressed, is_directional_scanner_suppressed, is_solarsystem_map_suppressed
from uihider import UiHiderMixin
COL1 = 0
COL2 = 28
COL3 = 56
HEIGHT = 16

class HudButtonsCont(UiHiderMixin, ContainerAutoSize):
    uniqueUiName = pConst.UNIQUE_NAME_HUD_BUTTONS
    default_name = 'HudButtonsCont'
    isAutoSizeEnabled = False

    def ApplyAttributes(self, attributes):
        super(HudButtonsCont, self).ApplyAttributes(attributes)
        self.cameraTactical = None
        self.cameraOrbit = None
        self.cameraPov = None
        self.tacticalOverlay = None
        self.autopilotBtn = None

    def AnimateReveal(self):
        PlaySound('onboarding_ui_sfx_play')
        self.opacity = 0
        self.Show()
        animations.BlinkIn(self, startVal=0.2, endVal=1.0, loops=3)

    def Hide(self, *args):
        super(HudButtonsCont, self).Hide(*args)
        self.opacity = 0

    def Show(self, *args, **kwargs):
        super(HudButtonsCont, self).Show(*args, **kwargs)
        self.opacity = 1.0

    @telemetry.ZONE_METHOD
    def InitButtons(self):
        self.Flush()
        self.cameraTactical = LeftSideButtonCameraTactical(parent=self, left=COL1, top=HEIGHT)
        self.cameraOrbit = LeftSideButtonCameraOrbit(parent=self, left=COL1, top=3 * HEIGHT)
        self.cameraPov = LeftSideButtonCameraPOV(parent=self, left=COL1, top=5 * HEIGHT)
        self.AddCargoBtn(COL2)
        self.tacticalOverlay = LeftSideButtonTactical(parent=self, left=COL2, top=2 * HEIGHT)
        scannerBtn = LeftSideButtonScanner(parent=self, left=COL2, top=4 * HEIGHT)
        ssID = session.solarsystemid2
        if is_scanning_suppressed(ssID) and is_directional_scanner_suppressed(ssID) and is_solarsystem_map_suppressed(ssID):
            scannerBtn.Disable()
        self.autopilotBtn = LeftSideButtonAutopilot(parent=self, left=COL2, top=6 * HEIGHT)
        showZoomBtns = settings.user.ui.Get('showZoomBtns', 0)
        if showZoomBtns:
            LeftSideButtonZoomIn(parent=self, left=COL3, top=HEIGHT)
            LeftSideButtonZoomOut(parent=self, left=COL3, top=3 * HEIGHT)
        if IsControllingStructure():
            self.autopilotBtn.Disable()
        else:
            self.autopilotBtn.Enable()
        self.EnableAutoSize()
        self.DisableAutoSize()

    def AddCargoBtn(self, left):
        if IsControllingStructure():
            cargoClass = LeftSideButtonStructureAmmoHold
        else:
            cargoClass = LeftSideButtonCargo
        cargoClass(parent=self, left=left, top=0)
