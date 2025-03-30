#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipHud\leftSideButton.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from eve.client.script.environment.invControllers import ShipCargo
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.camera.cameraUtil import IsAutoTrackingEnabled
from eve.client.script.ui.control import eveIcon
from eve.client.script.ui.inflight.radialMenuScanner import RadialMenuScanner
from eve.client.script.ui.view.viewStateConst import ViewState
import evecamera
from eveuniverse.solar_systems import is_tactical_camera_suppressed
from localization import GetByLabel
import uthread
from eve.client.script.ui.shared.inventory.invWindow import Inventory
import localization
import trinity
from carbonui.uicore import uicore
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
BTN_SIZE = 36
ICON_SIZE = 32

class LeftSideButton(Container):
    default_texturePath = None
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPRIGHT
    default_width = BTN_SIZE
    default_height = BTN_SIZE
    cmdName = None

    def __init__(self, **kwargs):
        self.busy = None
        super(LeftSideButton, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        super(LeftSideButton, self).ApplyAttributes(attributes)
        texturePath = attributes.get('texturePath', self.default_texturePath)
        self.orgTop = None
        self.pickRadius = self.width / 2
        self.icon = eveIcon.Icon(parent=self, name='icon', pos=(0,
         0,
         ICON_SIZE,
         ICON_SIZE), align=uiconst.CENTER, state=uiconst.UI_DISABLED, icon=texturePath)
        self.transform = Transform(parent=self, name='icon', pos=(0,
         0,
         ICON_SIZE,
         ICON_SIZE), align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.hilite = Sprite(parent=self, name='hilite', align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnBaseAndShadow.png', color=(0.63, 0.63, 0.63, 1.0), blendMode=trinity.TR2_SBM_ADD)
        Sprite(parent=self, name='slot', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnBaseAndShadow.png')
        self.busyContainer = Container(parent=self, name='busyContainer', align=uiconst.TOALL, clipChildren=True)
        self.busy = Sprite(parent=self.busyContainer, name='busy', align=uiconst.TOPLEFT, width=self.width, height=self.height, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnGlow.png', color=self._get_busy_color())
        self.blinkBG = Sprite(parent=self, name='blinkBG', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/utilBtnGlow.png', opacity=0.0, blendMode=trinity.TR2_SBM_ADD)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.cmdName:
            tooltipPanel.LoadGeneric2ColumnTemplate()
            cmd = uicore.cmd.commandMap.GetCommandByName(self.cmdName)
            commandTooltipResult = tooltipPanel.AddCommandTooltip(cmd)
            self.AddMoreToTooltipPanel(tooltipPanel)
            return commandTooltipResult
        return (None, None)

    def AddMoreToTooltipPanel(self, panel):
        pass

    def LoadIcon(self, iconPath):
        self.icon.LoadIcon(iconPath)

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        sm.GetService('ui').StopBlink(self.icon)

    def OnMouseDown(self, btn, *args):
        if getattr(self, 'orgTop', None) is None:
            self.orgTop = self.top
        self.top = self.orgTop + 2

    def OnMouseUp(self, *args):
        if getattr(self, 'orgTop', None) is not None:
            self.top = self.orgTop

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self.hilite.state = uiconst.UI_DISABLED

    def OnMouseExit(self, *args):
        self.hilite.state = uiconst.UI_HIDDEN
        if getattr(self, 'orgTop', None) is not None:
            self.top = self.orgTop

    def Blink(self, loops = 3):
        uicore.animations.FadeTo(self.blinkBG, 0.0, 0.9, duration=0.15, loops=loops, callback=self._BlinkFadeOut)

    def _BlinkFadeOut(self):
        uicore.animations.FadeOut(self.blinkBG, duration=0.6)

    def Enable(self, *args):
        Container.Enable(self, *args)
        self.opacity = 1.0

    def Disable(self, *args):
        Container.Disable(self, *args)
        self.opacity = 0.3

    def OnColorThemeChanged(self):
        if self.busy is not None:
            self.busy.color = self._get_busy_color()

    @staticmethod
    def _get_busy_color():
        return tuple(eveThemeColor.THEME_FOCUS[:3]) + (0.6,)


def ExpandRadialMenu(button, radialClass):
    if button.destroyed:
        return
    uicore.layer.menu.Flush()
    if not uicore.uilib.leftbtn:
        return
    radialMenu = radialClass(name='radialMenu', parent=uicore.layer.menu, state=uiconst.UI_HIDDEN, align=uiconst.TOPLEFT, anchorObject=button)
    uicore.layer.menu.radialMenu = radialMenu
    uicore.uilib.SetMouseCapture(radialMenu)
    radialMenu.state = uiconst.UI_NORMAL


class LeftSideButtonStructureAmmoHold(LeftSideButton):
    default_name = 'inFlightStructureAmmoBtn'
    default_texturePath = 'res:/UI/Texture/icons/44_32_10.png'
    cmdName = 'OpenCargoHoldOfActiveShip'
    cmdDescription_override = 'Tooltips/Hud/CargoHoldStructure_description'

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        Inventory.OpenOrShow(toggle=True)

    def OnDropData(self, dragObj, nodes):
        ShipCargo().OnDropData(nodes)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        l, d = LeftSideButton.LoadTooltipPanel(self, tooltipPanel)
        if d:
            detailedDescription = GetByLabel(self.cmdDescription_override)
            d.text = detailedDescription


class LeftSideButtonScanner(LeftSideButton):
    default_name = 'inFlightScannerBtn'
    uniqueUiName = pConst.UNIQUE_NAME_SCANNER_BTN
    default_texturePath = 'res:/UI/Texture/classes/SensorSuite/radar.png'
    label = 'UI/Generic/Scanner'
    cmdName = 'ToggleProbeScanner'

    def ApplyAttributes(self, attributes):
        LeftSideButton.ApplyAttributes(self, attributes)
        self.sweep = Sprite(parent=self.transform, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/SensorSuite/radar_sweep.png')

    def OnMouseDown(self, *args):
        uthread.new(ExpandRadialMenu, self, RadialMenuScanner)

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelShortcut(localization.GetByLabel('Tooltips/Hud/Scanners'), '')
        tooltipPanel.AddLabelMedium(text=localization.GetByLabel('Tooltips/Hud/Scanners_description'), wrapWidth=200, colSpan=tooltipPanel.columns, color=(0.6, 0.6, 0.6, 1))


class LeftSideButtonTactical(LeftSideButton):
    default_name = 'inFlightTacticalBtn'
    uniqueUiName = pConst.UNIQUE_NAME_TACTICAL_BTN
    default_texturePath = 'res:/UI/Texture/Icons/44_32_42.png'
    label = 'UI/Generic/Tactical'
    cmdName = 'CmdToggleTacticalOverlay'
    __notifyevents__ = ['OnTacticalOverlayChange', 'OnActiveCameraChanged']

    def ApplyAttributes(self, attributes):
        LeftSideButton.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.UpdateButtonState()

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        sm.GetService('tactical').ToggleOnOff()

    def OnActiveCameraChanged(self, cameraID):
        self.UpdateButtonState()

    def OnTacticalOverlayChange(self):
        self.UpdateButtonState()

    def UpdateButtonState(self):
        if sm.GetService('tactical').IsTacticalOverlayAllowed():
            self.Enable()
        else:
            self.Disable()
        isActive = sm.GetService('tactical').IsTacticalOverlayActive()
        if isActive:
            self.busy.state = uiconst.UI_DISABLED
            self.hint = localization.GetByLabel('UI/Inflight/HideTacticalOverview')
        else:
            self.busy.state = uiconst.UI_HIDDEN
            self.hint = localization.GetByLabel('UI/Inflight/ShowTacticalOverlay')


class LeftSideButtonAutopilot(LeftSideButton):
    default_name = 'inFlightAutopilotBtn'
    uniqueUiName = pConst.UNIQUE_NAME_AUTOPILOT_BTN
    default_texturePath = 'res:/UI/Texture/Icons/44_32_12.png'
    label = 'UI/Generic/Autopilot'
    cmdName = 'CmdToggleAutopilot'
    __notifyevents__ = ['OnAutoPilotOn', 'OnAutoPilotOff']

    def ApplyAttributes(self, attributes):
        LeftSideButton.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        apActive = sm.GetService('autoPilot').GetState()
        if apActive:
            self.OnAutoPilotOn()
        else:
            self.OnAutoPilotOff()

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        self.AutoPilotOnOff(not sm.GetService('autoPilot').GetState())

    def AutoPilotOnOff(self, onoff, *args):
        if onoff:
            sm.GetService('autoPilot').SetOn()
        else:
            sm.GetService('autoPilot').SetOff('toggled by shipUI')

    def OnAutoPilotOn(self):
        self.busy.state = uiconst.UI_DISABLED
        self.hint = localization.GetByLabel('UI/Inflight/DeactivateAutopilot')
        self.hint += self._GetShortcutForCommand(self.cmdName)

    def OnAutoPilotOff(self):
        self.busy.state = uiconst.UI_HIDDEN
        self.hint = localization.GetByLabel('UI/Inflight/ActivateAutopilot')
        self.hint += self._GetShortcutForCommand(self.cmdName)

    def _GetShortcutForCommand(self, cmdName):
        if cmdName:
            shortcut = uicore.cmd.GetShortcutStringByFuncName(cmdName)
            if shortcut:
                return localization.GetByLabel('UI/Inflight/ShortcutFormatter', shortcut=shortcut)
        return ''


class LeftSideButtonZoomIn(LeftSideButton):
    default_name = 'inFlightZoomInBtn'
    default_texturePath = 'res:/UI/Texture/Icons/44_32_43.png'
    label = 'UI/Inflight/ZoomIn'
    cmdName = 'CmdZoomIn'

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        uicore.cmd.GetCommandAndExecute('CmdZoomIn')


class LeftSideButtonZoomOut(LeftSideButton):
    default_name = 'inFlightZoomOutBtn'
    default_texturePath = 'res:/UI/Texture/Icons/44_32_44.png'
    label = 'UI/Inflight/ZoomOut'
    cmdName = 'CmdZoomOut'

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        uicore.cmd.GetCommandAndExecute('CmdZoomOut')


class LeftSideButtonCameraBase(LeftSideButton):
    __notifyevents__ = ['OnActiveCameraChanged']

    def ApplyAttributes(self, attributes):
        LeftSideButton.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.UpdateButtonState()

    def OnActiveCameraChanged(self, cameraID):
        self.UpdateButtonState()

    def UpdateButtonState(self):
        activeCamera = sm.GetService('sceneManager').GetActivePrimaryCamera()
        if activeCamera.IsLocked():
            self.Disable()
        else:
            self.Enable()
        if self.IsActive():
            self.busy.state = uiconst.UI_DISABLED
        else:
            self.busy.state = uiconst.UI_HIDDEN

    def IsActive(self):
        cameraID = sm.GetService('viewState').GetView(ViewState.Space).GetRegisteredCameraID()
        return cameraID == self.cameraID


class LeftSideButtonCameraPOV(LeftSideButtonCameraBase):
    default_name = 'cameraButtonPOV'
    uniqueUiName = pConst.UNIQUE_NAME_CAMERA_POV
    default_texturePath = 'res:/UI/Texture/classes/ShipUI/iconCameraFirstPerson.png'
    cmdName = 'CmdSetCameraPOV'
    cameraID = evecamera.CAM_SHIPPOV

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        uicore.cmd.GetCommandAndExecute('CmdSetCameraPOV')

    def LoadTooltipPanel(self, tooltipPanel, *args):
        LeftSideButtonCameraBase.LoadTooltipPanel(self, tooltipPanel, *args)
        tooltipPanel.AddSpacer(width=0, height=5)
        for cmdName in ('CmdFlightControlsUp', 'CmdFlightControlsDown', 'CmdFlightControlsLeft', 'CmdFlightControlsRight'):
            cmd = uicore.cmd.commandMap.GetCommandByName(cmdName)
            tooltipPanel.AddCommandTooltip(cmd)
            tooltipPanel.AddSpacer(width=0, height=1)


class LeftSideButtonCameraOrbit(LeftSideButtonCameraBase):
    default_name = 'cameraButtonOrbit'
    uniqueUiName = pConst.UNIQUE_NAME_CAMERA_ORBIT
    default_texturePath = 'res:/UI/Texture/classes/ShipUI/iconCameraOrbit.png'
    cmdName = 'CmdSetCameraOrbit'
    cameraID = evecamera.CAM_SHIPORBIT

    def ApplyAttributes(self, attributes):
        LeftSideButtonCameraBase.ApplyAttributes(self, attributes)
        self.UpdateIcon()
        settings.char.Subscribe('ui', 'orbitCameraAutoTracking', self.OnAutoTrackingChanged)

    def Close(self):
        super(LeftSideButtonCameraOrbit, self).Close()
        settings.char.Unsubscribe('ui', 'orbitCameraAutoTracking', self.OnAutoTrackingChanged)

    def UpdateIcon(self):
        if IsAutoTrackingEnabled():
            self.LoadIcon('res:/UI/Texture/classes/ShipUI/iconCameraTracking.png')
        else:
            self.LoadIcon('res:/UI/Texture/classes/ShipUI/iconCameraOrbit.png')

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        uicore.cmd.GetCommandAndExecute('CmdSetCameraOrbit')

    def LoadTooltipPanel(self, tooltipPanel, *args):
        LeftSideButtonCameraBase.LoadTooltipPanel(self, tooltipPanel, *args)
        tooltipPanel.AddSpacer(width=0, height=5)
        tooltipPanel.AddLabelShortcut(GetByLabel('Tooltips/Hud/FOVZoom'), GetByLabel('Tooltips/Hud/AltPlusZoom'))
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdToggleAutoTracking')
        tooltipPanel.AddSpacer(width=0, height=1)
        tooltipPanel.AddCommandTooltip(cmd)

    def OnAutoTrackingChanged(self):
        self.UpdateIcon()
        self.Blink(3)

    def GetMenu(self):
        return [(GetByLabel('UI/Commands/CmdToggleAutoTracking'), uicore.cmd.GetCommandToExecute('CmdToggleAutoTracking'))]

    def IsActive(self):
        cameraID = sm.GetService('viewState').GetView(ViewState.Space).GetRegisteredCameraID()
        return cameraID in (evecamera.CAM_SHIPORBIT,
         evecamera.CAM_SHIPORBIT_ABYSSAL_SPACE,
         evecamera.CAM_SHIPORBIT_HAZARD,
         evecamera.CAM_SHIPORBIT_RESTRICTED)


class LeftSideButtonCameraTactical(LeftSideButtonCameraBase):
    default_name = 'cameraButtonTactical'
    uniqueUiName = pConst.UNIQUE_NAME_CAMERA_TACTICAL
    default_texturePath = 'res:/UI/Texture/classes/ShipUI/iconCameraGrid.png'
    cmdName = 'CmdSetCameraTactical'
    cameraID = evecamera.CAM_TACTICAL

    def ApplyAttributes(self, attributes):
        LeftSideButton.ApplyAttributes(self, attributes)
        if is_tactical_camera_suppressed(session.solarsystemid2):
            self.Disable()
        sm.RegisterNotify(self)
        self.UpdateButtonState()

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        uicore.cmd.GetCommandAndExecute('CmdSetCameraTactical')

    def LoadTooltipPanel(self, tooltipPanel, *args):
        LeftSideButtonCameraBase.LoadTooltipPanel(self, tooltipPanel, *args)
        tooltipPanel.AddSpacer(width=0, height=5)
        tooltipPanel.AddLabelShortcut(GetByLabel('Tooltips/Hud/Pan'), GetByLabel('Tooltips/Hud/RightMouse'))
