#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipHud\shipUI.py
import evetypes
import trinity
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.control.layer import LayerCore
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.util import colorblind
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.inflight.shipscan import CargoScan, ShipScan
from eve.client.script.ui.view import overlaySettings
from eve.client.script.ui.view.viewStateConst import ViewOverlay
from eveexceptions import UserError
from menu import MenuLabel
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from eve.client.script.parklife import states
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.inflight.notifySettingsWindow import NotifySettingsWindow
from eve.client.script.ui.inflight.radialMenuScanner import RadialMenuScanner
from eve.client.script.ui.inflight.shipAlert import ShipAlertContainer
from eve.client.script.ui.inflight.shipHud.capacitorContainer import CapacitorContainer
from eve.client.script.ui.inflight.shipHud.buffBarContainer import BuffBarContainer
from eve.client.script.ui.inflight.shipHud.heatGauges import HeatGauges
from eve.client.script.ui.inflight.shipHud.hpGauges import HPGauges
from eve.client.script.ui.inflight.shipHud.hudButtonsCont import HudButtonsCont
from eve.client.script.ui.inflight.shipHud.hudReadout import HudReadout
from eve.client.script.ui.inflight.shipHud.hudShape import HUDShape, StructureHUDShape
from eve.client.script.ui.inflight.shipHud.releaseControlBtn import ReleaseControlBtn
from eve.client.script.ui.inflight.shipHud.activeShipController import ActiveShipController
from eve.client.script.ui.inflight.shipHud.shipHudConst import SHIP_UI_HEIGHT, SHIP_UI_WIDTH
from eve.client.script.ui.inflight.shipHud.slotsContainer import SlotsContainer
from eve.client.script.ui.inflight.shipHud.speedGauge import SpeedGauge
from eve.client.script.ui.inflight.shipSafetyButton import SafetyButton
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
from eve.client.script.ui.inflight.squadrons.squadronsUI import SquadronsUI
from eve.client.script.ui.inflight.stanceButtons import StanceButtons
from eve.client.script.ui.moonmining.moonminingExtraHudBtns import MoonminingExtraHudBtns
from eve.client.script.ui.services.menuSvcExtras import movementFunctions
from eve.client.script.ui.util.uix import GetSlimItemName
from eve.client.script.util.settings import IsShipHudTopAligned, SetShipHudTopAligned
from eve.common.script.sys.eveCfg import IsControllingStructure
from gametime import GetDurationInClient
from localization import GetByLabel
from menucheckers import CelestialChecker
from menucheckers.sessionChecker import SessionChecker
from sensorsuite.overlay.sitecompass import Compass
import blue
import telemetry
import uthread
from carbonui.uicore import uicore
import threadutils
from structures import IsDrillingPlatform
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import log
from structures.types import IsFlexStructure
from uihider import UiHiderMixin
SLOTS_CONTAINER_LEFT = SHIP_UI_WIDTH / 2.0 + 70
SLOTS_CONTAINER_TOP = -1
SLOTS_CONTAINER_WIDTH = 512
SLOTS_CONTAINER_HEIGHT = 152
EWAR_CONTAINER_WIDTH = 480
EWAR_CONTAINER_HEIGHT = 44

class ShipUI(LayerCore):
    __notifyevents__ = ['OnShipScanCompleted',
     'OnJamStart',
     'OnJamEnd',
     'OnCargoScanComplete',
     'DoBallRemove',
     'OnSetDevice',
     'OnAssumeStructureControl',
     'OnRelinquishStructureControl',
     'OnUIRefresh',
     'ProcessPendingOverloadUpdate',
     'DoBallsRemove',
     'OnSetCameraOffset',
     'ProcessShipEffect',
     'OnStateChange']

    def ApplyAttributes(self, attributes):
        self.fighterHudBinding = None
        LayerCore.ApplyAttributes(self, attributes)
        self.setupShipTasklet = None
        self.updateTasklet = None
        self.controller = ActiveShipController()
        self.controller.on_new_itemID.connect(self.OnShipChanged)
        self.compass = None
        self.stanceButtons = None
        self.extraButtons = None
        self.ResetSelf()
        colorblind.on_colorblind_mode_changed.connect(self.OnColorBlindModeChanged)

    def Close(self):
        LayerCore.Close(self)
        self.controller.Close()

    def OnSetCameraOffset(self, cameraOffset):
        self.UpdatePosition()

    def OnSetDevice(self):
        self.UpdatePosition()

    def UpdateUIScaling(self, value, oldValue):
        super(ShipUI, self).UpdateUIScaling(value, oldValue)
        self.OnUIRefresh()

    def OnUIRefresh(self):
        self.CloseView(recreate=False)
        self.OpenView()

    def OnColorBlindModeChanged(self):
        self.OnUIRefresh()

    @telemetry.ZONE_METHOD
    def ResetSelf(self):
        self.RemoveFighterHudBinding()
        self.safetyButton = None
        self.fighterHudBinding = None
        self.sr.selectedcateg = 0
        self.sr.pendingreloads = []
        self.sr.rampTimers = {}
        self.shipuiReady = False
        self.initing = None
        self.jammers = {}
        self.assumingdelay = None
        if self.updateTasklet is not None:
            self.updateTasklet.kill()
        self.updateTasklet = None
        if self.setupShipTasklet is not None:
            self.setupShipTasklet.kill()
        self.setupShipTasklet = None
        self.fighterCont = None
        self.Flush()

    def CheckSession(self, change):
        if sm.GetService('autoPilot').GetState():
            self.OnAutoPilotOn()
        else:
            self.OnAutoPilotOff()

    @telemetry.ZONE_METHOD
    def UpdatePosition(self):
        cameraOffset = sm.GetService('sceneManager').GetCameraOffset()
        halfWidth = uicore.desktop.width / 2
        baseOffset = -cameraOffset * halfWidth
        wndLeft = settings.char.windows.Get('shipuialignleftoffset', 0)
        maxRight, minLeft = self.GetShipuiOffsetMinMax()
        self.hudContainer.left = min(maxRight, max(minLeft, baseOffset + wndLeft))
        self.buffBarContainer.left = self.hudContainer.left
        if IsShipHudTopAligned():
            self.hudContainer.SetAlign(uiconst.CENTERTOP)
            self.buffBarContainer.SetAlign(uiconst.CENTERTOP)
            self.sr.indicationContainer.top = self.hudContainer.height + self.buffBarContainer.height
        else:
            self.hudContainer.SetAlign(uiconst.CENTERBOTTOM)
            self.buffBarContainer.SetAlign(uiconst.CENTERBOTTOM)
            self.sr.indicationContainer.top = -(self.buffBarContainer.height + self.sr.indicationContainer.height)
        if self.IsFightersDetached() and self.fighterCont:
            left, top = GetFightersDetachedPos()
            buttonWidth = 32
            left = min(left, uicore.desktop.width - buttonWidth)
            top = min(top, uicore.desktop.height - self.fighterCont.height)
            self.fighterCont.left = left
            self.fighterCont.top = top
            settings.char.ui.Set('fightersDetachedPosition', (left, top))
        self.AlignFighters()
        self.sr.shipAlertContainer.UpdatePosition()

    def MakeFighterHudBinding(self):
        self.RemoveFighterHudBinding()
        self.fighterHudBinding = trinity.CreatePythonBinding(uicore.uilib.bracketCurveSet, self, 'fighterContLeft', self.fighterCont, 'left')

    def RemoveFighterHudBinding(self):
        if self.fighterHudBinding:
            cs = uicore.uilib.bracketCurveSet
            cs.bindings.fremove(self.fighterHudBinding)
            self.fighterHudBinding = None

    def OnShipMouseDown(self, wnd, btn, *args):
        if btn != 0:
            return
        self.dragging = True
        if not self.hudContainer:
            return
        self.grab = [uicore.uilib.x, self.hudContainer.left]
        uthread.new(self.BeginDrag)

    def GetShipuiOffsetMinMax(self, *args):
        magicNumber = 275
        if self.CheckShipHasFighterBay():
            magicNumber = 300
        sidePanelsLeft, sidePanelsRight = uicore.layer.sidepanels.GetSideOffset()
        maxRight = uicore.desktop.width / 2 - self.slotsContainer.width / 2 - magicNumber - sidePanelsRight
        minLeft = -(uicore.desktop.width / 2 - 180) + sidePanelsLeft
        return (maxRight, minLeft)

    def OnToggleShipSelected(self, *args):
        if not self.CheckShipHasFighterBay():
            return
        if not self.IsFightersShown():
            self.DeselectShip()
            return
        x, y = self.grab
        currentX, currentY = uicore.uilib.x, self.hudContainer.left
        if x != currentX or y != currentY:
            return
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            if movementFunctions.IsSelectedForNavigation(session.shipid):
                self.DeselectShip()
            else:
                self.SelectShip()
        else:
            self.SelectShip()
            self.fighterCont.ClearSelection()

    def SelectShip(self):
        movementFunctions.SelectForNavigation(session.shipid)

    def DeselectShip(self):
        movementFunctions.DeselectForNavigation(session.shipid)

    def OnStateChange(self, itemID, flag, flagState, *args):
        if not self.CheckShipHasFighterBay():
            return
        if flag == states.selectedForNavigation and itemID == session.shipid:
            if flagState:
                self.ShowSelectionHilite()
            else:
                self.HideSelectionHilite()

    def ShowSelectionHilite(self):
        if self.shipSelectHilight.display:
            return
        self.shipSelectHilight.display = True
        self.ringSprite.opacity = 0.2
        self.bracketSprite.opacity = 3.0
        uicore.animations.FadeTo(self.ringSprite, self.ringSprite.opacity, 1.0, duration=0.2)
        uicore.animations.FadeTo(self.bracketSprite, self.bracketSprite.opacity, 1.0, duration=0.2)

    def HideSelectionHilite(self):
        self.shipSelectHilight.display = False

    def OnShipMouseUp(self, wnd, btn, *args):
        if btn != 0:
            return
        sm.StartService('ui').ForceCursorUpdate()
        self.dragging = False

    def BeginDrag(self, *args):
        cameraOffset = sm.GetService('sceneManager').GetCameraOffset()
        halfWidth = uicore.desktop.width / 2
        baseOffset = -cameraOffset * halfWidth
        while not self.hudContainer.destroyed and getattr(self, 'dragging', 0):
            uicore.uilib.SetCursor(uiconst.UICURSOR_DIVIDERADJUST)
            maxRight, minLeft = self.GetShipuiOffsetMinMax()
            grabMouseDiff = uicore.uilib.x - self.grab[0]
            combinedOffset = min(maxRight, max(minLeft, self.grab[1] + grabMouseDiff))
            dragOffset = combinedOffset - baseOffset
            if -8 <= dragOffset <= 8:
                settings.char.windows.Set('shipuialignleftoffset', 0)
                self.hudContainer.left = baseOffset
            else:
                self.hudContainer.left = combinedOffset
                settings.char.windows.Set('shipuialignleftoffset', dragOffset)
            self.buffBarContainer.left = self.hudContainer.left
            blue.pyos.synchro.SleepWallclock(1)

    def ConstructOverlayContainer(self):
        self.optionsCont = Container(parent=self.overlayContainer, name='optionsCont', pos=(190, 194, 16, 16), align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN)
        self.moduleToggleCont = Container(parent=self.overlayContainer, name='moduleToggleCont', pos=(self.moduleToggleContLeft,
         170,
         24,
         24), align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN)
        if not IsControllingStructure():
            self.stopButton = StopButton(parent=self.overlayContainer, align=uiconst.TOPLEFT, controller=self.controller, left=75, top=155)
            self.maxspeedButton = MaxSpeedButton(parent=self.overlayContainer, align=uiconst.TOPLEFT, controller=self.controller, left=168, top=155, uniqueUiName=pConst.UNIQUE_NAME_FULL_SPEED_BTN)

    @telemetry.ZONE_METHOD
    def OnOpenView(self, **kwargs):
        self.ResetSelf()
        self.state = uiconst.UI_HIDDEN
        self.hudContainer = HudContainer(name='hudContainer', parent=self, controller=self.controller, align=uiconst.CENTERBOTTOM, width=SHIP_UI_WIDTH, height=SHIP_UI_HEIGHT)
        self.centerParent = CenterHudContainer(name='centerParent', parent=self.hudContainer, align=uiconst.CENTERBOTTOM, pos=(0, 0, 185, 200))
        self.overlayContainer = Container(parent=self.centerParent, name='overlayContainer', pos=(0, 0, 256, 256), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN, idx=0)
        self.ConstructOverlayContainer()
        if IsControllingStructure():
            shipShape = StructureHUDShape(parent=self.centerParent, align=uiconst.CENTER)
        else:
            shipShape = HUDShape(parent=self.centerParent, align=uiconst.CENTER)
        self.shipuiMainShape = shipShape.shipuiMainShape
        self.capacitorContainer = CapacitorContainer(parent=self.centerParent, align=uiconst.CENTER, top=-1, controller=self.controller, uniqueUiName=pConst.UNIQUE_NAME_CAPACITOR)
        self.capacitorContainer.OnMouseDown = (self.OnShipMouseDown, self.capacitorContainer)
        self.capacitorContainer.OnMouseUp = (self.OnShipMouseUp, self.capacitorContainer)
        self.capacitorContainer.OnClick = self.OnToggleShipSelected
        heatPicker = Container(name='heatPicker', parent=self.centerParent, align=uiconst.CENTER, width=160, height=160, pickRadius=43, state=uiconst.UI_NORMAL)
        self.heatGauges = HeatGauges(parent=heatPicker, align=uiconst.CENTERTOP, controller=self.controller)
        self.hpGauges = HPGauges(name='healthGauges', parent=self.centerParent, align=uiconst.CENTER, pos=(0, -37, 148, 74), controller=self.controller, uniqueUiName=pConst.UNIQUE_NAME_SHIP_HEALTH)
        if IsControllingStructure():
            ReleaseControlBtn(parent=self.centerParent, top=29, align=uiconst.CENTERBOTTOM, func=self.ReleaseStructureControl, structureTypeID=self.controller.GetTypeID(), uniqueUiName=pConst.UNIQUE_NAME_RELEASE_CONTROL)
        else:
            self.speedGauge = SpeedGauge(parent=self.centerParent, top=29, align=uiconst.CENTERBOTTOM, controller=self.controller)
        if is_compass_enabled():
            self.compass = self.CreateCompass()
        self.shipSelectHilight = Container(name='navSelectHilight', parent=self.centerParent, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=self.shipSelectHilightSize, height=self.shipSelectHilightSize)
        self.ringSprite = Sprite(bgParent=self.shipSelectHilight, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/selectionRingLarge.png')
        self.bracketSprite = Sprite(bgParent=self.shipSelectHilight, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/selectionBracketLarge.png')
        self.shipSelectHilight.display = False
        self.slotsContainer = SlotsContainer(parent=self.hudContainer, pos=(self.slotsContLeft,
         SLOTS_CONTAINER_TOP,
         SLOTS_CONTAINER_WIDTH,
         SLOTS_CONTAINER_HEIGHT), align=uiconst.CENTERLEFT, state=uiconst.UI_PICKCHILDREN, controller=self.controller)
        self.stanceButtons = StanceButtons(parent=self.hudContainer, pos=(self.stanceButtonsLeft,
         1,
         40,
         120), name='stanceButtons', align=uiconst.CENTERLEFT, state=uiconst.UI_PICKCHILDREN, buttonSize=36)
        self.stanceButtons.Hide()
        self.extraButtons = MoonminingExtraHudBtns(parent=self.hudContainer, pos=(self.stanceButtonsLeft,
         -14,
         60,
         120), align=uiconst.CENTERLEFT, state=uiconst.UI_PICKCHILDREN)
        self.extraButtons.Hide()
        self.hudButtons = HudButtonsCont(name='hudButtons', parent=self.hudContainer, align=uiconst.CENTERRIGHT, left=self.hudButtonsLeft, top=15)
        self.buffBarContainer = BuffBarContainer(parent=self, align=uiconst.CENTERBOTTOM, top=SHIP_UI_HEIGHT, height=EWAR_CONTAINER_HEIGHT, width=EWAR_CONTAINER_WIDTH)
        self.sr.shipAlertContainer = ShipAlertContainer(parent=self.hudContainer)
        self.sr.indicationContainer = Container(parent=self.hudContainer, name='indicationContainer', align=uiconst.CENTERTOP, pos=(0, 0, 400, 68))
        self.safetyButton = SafetyButton(parent=self.overlayContainer, left=self.safetyButtonLeft, top=self.safetyButtonTop, uniqueUiName=pConst.UNIQUE_NAME_SAFETY_BUTTON)
        self.ConstructReadoutCont()
        self.settingsMenu = UtilMenu(name='hudSettingsMenu', uniqueUiName=pConst.UNIQUE_NAME_HUD_SETTINGS, menuAlign=uiconst.BOTTOMLEFT, parent=self.optionsCont, align=uiconst.TOPLEFT, GetUtilMenu=self.GetHUDOptionMenu, pos=(0, 0, 16, 16), texturePath='res:/UI/Texture/Icons/73_16_50.png', hint=GetByLabel('UI/Inflight/Options'))
        self.moduleToggleBtn = ButtonIcon(name='moduleToggleBtn', parent=self.moduleToggleCont, align=uiconst.TOPLEFT, width=24, height=24, iconSize=24, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/toggleModules_Up.png', func=self.OnToggleHudModules, hint=GetByLabel('UI/Inflight/HUDOptions/ClickToToggle'), uniqueUiName=pConst.UNIQUE_NAME_FIGHTERS_TOGGLE)
        self.moduleToggleBtn.display = False
        self.moduleToggleBtn.GetMenu = self.GetModuleToggleBtnMenu
        self.DrawFighters()
        self.hudContainer.state = uiconst.UI_PICKCHILDREN
        self.UpdatePosition()
        self.UpdateButtonPositions()
        self.shipuiReady = True
        self.SetupShip()
        Sprite(parent=self.centerParent, name='bgCircle', texturePath='res:/UI/Texture/classes/ShipUI/mainBGCircle.png', color=(0, 0, 0, 0.3), pos=(0, 0, 160, 160), align=uiconst.CENTER, state=uiconst.UI_DISABLED)

    def ReleaseStructureControl(self, structureTypeID):
        structureControlSvc = sm.GetService('structureControl')
        if IsFlexStructure(structureTypeID):
            structureControlSvc.BoardPreviousShip()
        else:
            return structureControlSvc.ReleaseControl()

    def DrawFighters(self):
        if self.fighterCont and not self.fighterCont.destroyed:
            self.fighterCont.Close()
        self.fighterCont = SquadronsUI(name='fighters', parent=self, state=uiconst.UI_PICKCHILDREN, parentFunc=self.OnToggleFightersDetached)
        self.AlignFighters()
        if self.IsFightersDetached():
            left, top = GetFightersDetachedPos()
            self.fighterCont.left = left
            self.fighterCont.top = top
            self.slotsContainer.display = True
        else:
            self.fighterCont.left = self.slotsContLeft
        self.SetFighterButtonsHint()
        self.fighterCont.KeepSelection()

    def SetFighterButtonsHint(self):
        isDetached = self.IsFightersDetached()
        if isDetached:
            self.fighterCont.fighterToggleBtn.hint = GetByLabel('UI/Inflight/HUDOptions/ClickToAttach')
        else:
            self.fighterCont.fighterToggleBtn.hint = GetByLabel('UI/Inflight/HUDOptions/DragToDetach')
        self.fighterCont.SetToggleBtnTexture(isDetached)

    def CheckShipHasFighterBay(self):
        if not session.shipid:
            return False
        godmaSM = sm.GetService('godma').GetStateManager()
        shipTypeID = self.controller.GetTypeID()
        if shipTypeID is None:
            return False
        fighterCapacity = godmaSM.GetType(shipTypeID).fighterCapacity
        return fighterCapacity > 0

    def OptionsBtnMouseEnter(self, *args):
        self.options.SetAlpha(1.0)

    def OptionsBtnMouseExit(self, *args):
        self.options.SetAlpha(0.8)

    def CheckControl(self):
        control = sm.GetService('pwn').GetCurrentControl()
        if control:
            self.OnAssumeStructureControl()

    def SetButtonState(self):
        if settings.user.ui.Get('hudButtonsExpanded', 1):
            self.hudButtons.state = uiconst.UI_PICKCHILDREN
            if IsControllingStructure():
                self.hudButtons.autopilotBtn.Disable()
            else:
                self.hudButtons.autopilotBtn.Enable()
        else:
            self.hudButtons.state = uiconst.UI_HIDDEN

    @telemetry.ZONE_METHOD
    def ConstructReadoutCont(self):
        self.readoutCont = HudReadout(parent=self.hudContainer, pos=(278, 22, 200, 0), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, controller=self.controller)

    def OnAssumeStructureControl(self, *args):
        now = blue.os.GetSimTime()
        self.assumingdelay = now
        uthread.new(self.DelayedOnAssumeStructureControl, now)

    def DelayedOnAssumeStructureControl(self, issueTime):
        blue.pyos.synchro.SleepSim(250)
        if self.assumingdelay is None:
            return
        issuedAt = self.assumingdelay
        if issuedAt != issueTime:
            return
        self.assumingdelay = None
        self.ShowStructureControl()

    def ShowStructureControl(self, *args):
        if self.controller.IsControllingTurret():
            self.initing = 1
            self.slotsContainer.InitSlots()
            self.hudButtons.InitButtons()
            self.initing = 0

    def OnRelinquishStructureControl(self, *args):
        self.SetupShip()

    @property
    def slotsContLeft(self):
        offset = 16 if is_compass_enabled() else 0
        if self.stanceButtons and self.stanceButtons.display or self.extraButtons and self.extraButtons.display:
            offset += 32
        return SLOTS_CONTAINER_LEFT + offset - 8

    @property
    def stanceButtonsLeft(self):
        offset = 16 if is_compass_enabled() else 0
        return SLOTS_CONTAINER_LEFT + 4 + offset - 8

    @property
    def fighterContLeft(self):
        offset = 8 if is_compass_enabled() else -8
        left = self.centerParent.GetAbsoluteRight()
        return left + offset

    @property
    def moduleToggleContLeft(self):
        if is_compass_enabled():
            return 202
        return 186

    @property
    def safetyButtonLeft(self):
        if is_compass_enabled():
            return 40
        return 50

    @property
    def safetyButtonTop(self):
        if is_compass_enabled():
            return 28
        return 38

    @property
    def hudButtonsLeft(self):
        if is_compass_enabled():
            return 690
        return 680

    @property
    def shipSelectHilightSize(self):
        if is_compass_enabled():
            return 206
        return 172

    def UpdateButtonsForShip(self):
        itemID = self.controller.GetItemID()
        typeID = self.controller.GetTypeID()
        self.extraButtons.Hide()
        if self.stanceButtons.HasStances():
            self.stanceButtons.Hide()
        self.stanceButtons.UpdateButtonsForShip(itemID, typeID)
        if self.stanceButtons.HasStances():
            self.stanceButtons.Show()
        elif self.ShouldShowExtraBtns(typeID):
            self.extraButtons.UpdateButtonsForHull()
            self.extraButtons.Show()
        self.UpdateButtonPositions()

    def ShouldShowExtraBtns(self, typeID):
        return IsDrillingPlatform(typeID)

    def ToggleCompass(self):
        settings.user.ui.Set('showSensorOverlay', not is_compass_enabled())
        if is_compass_enabled():
            self.compass = self.CreateCompass()
        else:
            self.compass.Close()
            self.compass = None
        self.UpdateButtonPositions()

    def CreateCompass(self):
        return Compass(parent=self.centerParent, uniqueUiName=pConst.UNIQUE_NAME_SENSOR_OVERLAY)

    def UpdateButtonPositions(self):
        self.slotsContainer.left = self.slotsContLeft
        self.stanceButtons.left = self.stanceButtonsLeft
        self.extraButtons.left = self.stanceButtonsLeft
        self.moduleToggleCont.left = self.moduleToggleContLeft
        self.safetyButton.left = self.safetyButtonLeft
        self.safetyButton.top = self.safetyButtonTop
        self.hudButtons.left = self.hudButtonsLeft
        self.shipSelectHilight.width = self.shipSelectHilightSize
        self.shipSelectHilight.height = self.shipSelectHilightSize

    def GetHUDOptionMenu(self, menuParent):
        showPassive = settings.user.ui.Get('showPassiveModules', 1)
        text = GetByLabel('UI/Inflight/HUDOptions/DisplayPassiveModules')
        menuParent.AddCheckBox(text=text, checked=showPassive, callback=self.ToggleShowPassive)
        showEmpty = settings.user.ui.Get('showEmptySlots', 0)
        text = GetByLabel('UI/Inflight/HUDOptions/DisplayEmptySlots')
        menuParent.AddCheckBox(text=text, checked=showEmpty, callback=self.ToggleShowEmpty)
        showReadout = settings.user.ui.Get('showReadout', 0)
        text = GetByLabel('UI/Inflight/HUDOptions/DisplayReadout')
        menuParent.AddCheckBox(text=text, checked=showReadout, callback=self.ToggleReadout)
        readoutType = settings.user.ui.Get('readoutType', 1)
        text = GetByLabel('UI/Inflight/HUDOptions/DisplayReadoutAsPercentage')
        if showReadout:
            callback = self.ToggleReadoutType
        else:
            callback = None
        menuParent.AddCheckBox(text=text, checked=readoutType, callback=callback)
        showHudButtons = settings.user.ui.Get('hudButtonsExpanded', 1)
        menuParent.AddCheckBox(text=GetByLabel('UI/Inflight/HUDOptions/DisplayUtilityButtons'), checked=showHudButtons, callback=self.ToggleHudButtons)
        menuParent.AddCheckBox(text=GetByLabel('UI/Inflight/HUDOptions/DisplayZoomButtons'), checked=settings.user.ui.Get('showZoomBtns', 0), callback=self.ToggleShowZoomBtns if showHudButtons else None)
        showTooltips = settings.user.ui.Get('showModuleTooltips', 1)
        text = GetByLabel('UI/Inflight/HUDOptions/DisplayModuleTooltips')
        menuParent.AddCheckBox(text=text, checked=showTooltips, callback=self.ToggleShowModuleTooltips)
        text = GetByLabel('UI/Inflight/HUDOptions/DisplaySensorOverlay')
        menuParent.AddCheckBox(text=text, checked=is_compass_enabled(), callback=self.ToggleCompass, uniqueUiName=pConst.UNIQUE_NAME_SENSOR_OVERLAY_SETTING)
        menuParent.AddDivider()
        lockModules = settings.user.ui.Get('lockModules', 0)
        text = GetByLabel('UI/Inflight/HUDOptions/LockModulesInPlace')
        menuParent.AddCheckBox(text=text, checked=lockModules, callback=self.ToggleLockModules)
        menuParent.AddCheckBox(text=GetByLabel('UI/Inflight/HUDOptions/BlinkCargo'), checked=self.GetCargoBlinkValue(), callback=self.ToggleBlinkCargo)
        lockOverload = settings.user.ui.Get('lockOverload', 0)
        text = GetByLabel('UI/Inflight/HUDOptions/LockOverloadState')
        menuParent.AddCheckBox(text=text, checked=lockOverload, callback=self.ToggleOverloadLock)
        text = GetByLabel('UI/Inflight/HUDOptions/AlignHUDToTop')
        cb = menuParent.AddCheckBox(text=text, checked=IsShipHudTopAligned(), callback=self.ToggleAlign)
        cb.isToggleEntry = False
        text = GetByLabel('/Carbon/UI/Controls/Window/AlwaysAboveFullScreenViews')
        menuParent.AddCheckBox(text=text, checked=overlaySettings.IsFullscreenOverlayModeEnabled(ViewOverlay.ShipUI), callback=lambda : overlaySettings.ToggleFullscreenOverlayMode(ViewOverlay.ShipUI))
        menuParent.AddDivider()
        text = GetByLabel('UI/Inflight/NotifySettingsWindow/DamageAlertSettings')
        iconPath = 'res:/UI/Texture/classes/UtilMenu/BulletIcon.png'
        menuParent.AddIconEntry(icon=iconPath, text=text, callback=self.ShowNotifySettingsWindow)
        if sm.GetService('logger').IsInDragMode():
            text = GetByLabel('UI/Accessories/Log/ExitMessageMovingMode')
            enterArgs = False
        else:
            text = GetByLabel('UI/Accessories/Log/EnterMessageMovingMode')
            enterArgs = True
        menuParent.AddIconEntry(icon='res:/UI/Texture/classes/UtilMenu/BulletIcon.png', text=text, callback=(sm.GetService('logger').MoveNotifications, enterArgs))

    def ShowNotifySettingsWindow(self):
        NotifySettingsWindow.Open()

    def ToggleAlign(self):
        SetShipHudTopAligned(not IsShipHudTopAligned())
        self.UpdatePosition()
        for each in uicore.layer.abovemain.children[:]:
            if each.name == 'message':
                each.Close()
                break

        msg = getattr(uicore.layer.target, 'message', None)
        if msg:
            msg.Close()

    def CheckShowReadoutCont(self):
        if settings.user.ui.Get('showReadout', 0):
            self.readoutCont.state = uiconst.UI_DISABLED
            self.hudButtons.top = 30
        else:
            self.readoutCont.state = uiconst.UI_HIDDEN
            self.hudButtons.top = 15

    def ToggleReadout(self):
        current = not settings.user.ui.Get('showReadout', 0)
        settings.user.ui.Set('showReadout', current)
        self.CheckShowReadoutCont()

    def GetCargoBlinkValue(self):
        return settings.user.ui.Get('BlinkCargoHudIcon', True)

    def ToggleBlinkCargo(self):
        settings.user.ui.Set('BlinkCargoHudIcon', not self.GetCargoBlinkValue())

    def ToggleReadoutType(self):
        current = settings.user.ui.Get('readoutType', 1)
        settings.user.ui.Set('readoutType', not current)

    def ToggleShowZoomBtns(self):
        settings.user.ui.Set('showZoomBtns', not settings.user.ui.Get('showZoomBtns', 0))
        self.hudButtons.InitButtons()

    def ToggleLockModules(self):
        settings.user.ui.Set('lockModules', not settings.user.ui.Get('lockModules', 0))
        self.slotsContainer.CheckGroupAllButton()

    def ToggleOverloadLock(self):
        settings.user.ui.Set('lockOverload', not settings.user.ui.Get('lockOverload', 0))

    def ToggleShowModuleTooltips(self):
        settings.user.ui.Set('showModuleTooltips', not settings.user.ui.Get('showModuleTooltips', 1))

    def ToggleHudButtons(self):
        isExpanded = self.hudButtons.state == uiconst.UI_PICKCHILDREN
        if isExpanded:
            PlaySound(uiconst.SOUND_COLLAPSE)
            self.hudButtons.state = uiconst.UI_HIDDEN
        else:
            PlaySound(uiconst.SOUND_EXPAND)
            self.hudButtons.state = uiconst.UI_PICKCHILDREN
        settings.user.ui.Set('hudButtonsExpanded', not isExpanded)

    def GetModuleToggleBtnMenu(self, *args):
        if self.IsFightersDetached():
            menuLabel = MenuLabel('UI/Inflight/ResetFighterPosition')
            return [[menuLabel, self.ResetSetFightersPos, ()]]
        return []

    def ResetSetFightersPos(self):
        ResetSetFightersDetachedPos()
        self.DrawFighters()

    def OnToggleHudModules(self, *args):
        if self.IsFightersDetached():
            self.OnToggleFightersDetached()
        else:
            settings.user.ui.Set('displayFighterUI', not settings.user.ui.Get('displayFighterUI', False))
            self.ShowHideFighters()

    def OnToggleFightersDetached(self, *args):
        isDetached = self.IsFightersDetached()
        settings.user.ui.Set('detachFighterUI', not isDetached)
        if isDetached:
            self.AttachHudModules()
        else:
            self.DetachHudModules()

    def AttachHudModules(self):
        self.AlignFighters()
        self.fighterCont.left = 0
        self.fighterCont.top = 10
        self.MakeFighterHudBinding()
        self.ShowHideFighters()
        self.SetFighterButtonsHint()

    def DetachHudModules(self):
        self.slotsContainer.display = True
        self.RemoveFighterHudBinding()
        self.DrawFighters()

    def InitFighters(self):
        if not self.IsFightersDetached():
            self.MakeFighterHudBinding()
            self.ShowHideFighters()
        else:
            self.DetachHudModules()
            self.slotsContainer.display = True

    def ShowHideFighters(self):
        displayFighters = self.IsFightersShown()
        isDetached = self.IsFightersDetached()
        if self.CheckShipHasFighterBay():
            if isDetached:
                self.fighterCont.display = True
                self.slotsContainer.display = True
                return
            if displayFighters == True:
                self.fighterCont.display = True
                self.slotsContainer.display = False
                return
        self.fighterCont.ClearSelection()
        self.fighterCont.display = False
        self.slotsContainer.display = True
        self.DeselectShip()

    def AlignFighters(self):
        if not self.fighterCont or self.fighterCont.destroyed:
            return
        if self.IsFightersDetached():
            self.fighterCont.SetAlign(uiconst.TOPLEFT)
        elif IsShipHudTopAligned():
            self.fighterCont.SetAlign(uiconst.TOTOP)
        else:
            self.fighterCont.SetAlign(uiconst.TOBOTTOM)
            self.fighterCont.top = 10

    def IsFightersDetached(self):
        return settings.user.ui.Get('detachFighterUI', False)

    def IsFightersShown(self):
        return settings.user.ui.Get('displayFighterUI', False)

    def Scanner(self, button):
        self.expandTimer = None
        uicore.layer.menu.Flush()
        radialMenu = RadialMenuScanner(name='radialMenu', parent=uicore.layer.menu, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT, anchorObject=button)
        uicore.layer.menu.radialMenu = radialMenu
        uicore.uilib.SetMouseCapture(radialMenu)

    def BlinkButton(self, key):
        self.slotsContainer.BlinkButton(key)

    def ChangeOpacityForRange(self, currentRange, *args):
        if getattr(self, 'slotContainer', None):
            self.slotsContainer.ChangeOpacityForRange(self, currentRange)

    def ResetModuleButtonOpacity(self, *args):
        if getattr(self, 'slotContainer', None):
            self.slotsContainer.ResetModuleButtonOpacity()

    def ToggleRackOverload(self, slotName):
        self.slotsContainer.ToggleRackOverload(slotName)

    def ProcessPendingOverloadUpdate(self, moduleIDs):
        self.slotsContainer.ProcessPendingOverloadUpdate(moduleIDs)

    def ResetSwapMode(self):
        self.slotsContainer.ResetSwapMode()

    def StartDragMode(self, itemID, typeID):
        self.slotsContainer.StartDragMode(itemID, typeID)

    def GetPosFromFlag(self, slotFlag):
        return self.slotsContainer.GetPosFromFlag(slotFlag)

    def GetSlotByName(self, name):
        return self.slotsContainer.FindChild(name)

    def ChangeSlots(self, toFlag, fromFlag):
        self.slotsContainer.ChangeSlots(toFlag, fromFlag)

    def SwapSlots(self, slotFlag1, slotFlag2):
        self.slotsContainer.SwapSlots(slotFlag1, slotFlag2)

    def LinkWeapons(self, master, slave, slotFlag1, slotFlag2, merge = False):
        self.slotsContainer.LinkWeapons(master, slave, slotFlag1, slotFlag2, merge)

    def GetModuleType(self, flag):
        return self.slotsContainer.GetModuleType(flag)

    def GetModuleFromID(self, moduleID):
        return self.slotsContainer.GetModuleFromID(moduleID)

    def ToggleShowEmpty(self):
        self.slotsContainer.ToggleShowEmpty()

    def ToggleShowPassive(self):
        self.slotsContainer.ToggleShowPassive()

    def GetModuleForFKey(self, key):
        return self.slotsContainer.GetModuleForFKey(key)

    def GetModule(self, moduleID):
        return self.slotsContainer.GetModule(moduleID)

    def OnF(self, sidx, gidx):
        if not self.CheckShipHasFighterBay():
            self.slotsContainer.OnF(sidx, gidx)
            return
        shipIsSelected, fightersSelected = movementFunctions.GetSelectedShipAndFighters()
        if self.IsFightersDetached():
            moduleIsActive = self.IsModuleActiveForFKey(sidx, gidx)
            isAllAbilitiesActiveOrInCooldown = GetShipFighterState().IsAllAbilitiesInSlotActiveOrInCooldown(sidx)
            if shipIsSelected:
                if isAllAbilitiesActiveOrInCooldown:
                    if moduleIsActive is not None:
                        self.slotsContainer.OnF(sidx, gidx)
                    if moduleIsActive is None or moduleIsActive == True:
                        self.TryActivateFighters(sidx, gidx)
                else:
                    self.TryActivateFighters(sidx, gidx)
                    if moduleIsActive == False:
                        self.slotsContainer.OnF(sidx, gidx)
            else:
                self.TryActivateFighters(sidx, gidx)
        elif self.IsFightersShown():
            self.TryActivateFighters(sidx, gidx)
        else:
            self.slotsContainer.OnF(sidx, gidx)

    def ActivateModuleByItemID(self, itemID):
        moduleButton = self.GetModule(itemID)
        if moduleButton:
            moduleButton.ActivateModule()

    def DeactivateModuleByItemID(self, itemID):
        moduleButton = self.GetModule(itemID)
        if moduleButton:
            moduleButton.DeactivateModule()

    def TryActivateFighters(self, sidx, gidx):
        if gidx != 0:
            return
        self.fighterCont.OnF(sidx)

    def GetModuleDefaultEffect(self, sidx, gidx):
        slot = self.slotsContainer.slotsByOrder.get((gidx, sidx), None)
        if not slot:
            return
        if not slot.sr.module:
            return
        if slot.sr.module.state != uiconst.UI_NORMAL:
            return
        if slot.sr.module.def_effect is None:
            return
        return slot.sr.module.def_effect

    def IsModuleActiveForFKey(self, sidx, gidx):
        defaultEffect = self.GetModuleDefaultEffect(sidx, gidx)
        if defaultEffect:
            return defaultEffect.isActive

    def OnFKeyOverload(self, sidx, gidx):
        self.slotsContainer.OnFKeyOverload(sidx, gidx)

    def OnReloadAmmo(self):
        self.slotsContainer.OnReloadAmmo()

    def OnCloseView(self):
        self.ResetSelf()
        settings.user.ui.Set('selected_shipuicateg', self.sr.selectedcateg)
        t = uthread.new(sm.GetService('space').OnShipUIReset)
        t.context = 'ShipUI::OnShipUIReset'

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        if isRelease:
            self.UnhookBall()
            self.jammers = {}
            return
        controllerBall = self.controller.GetBall()
        if controllerBall is not None:
            for ball, slimItem, terminal in pythonBalls:
                if ball and ball.id == controllerBall.id:
                    self.UnhookBall()
                    controllerBall = self.controller.GetBall()

        if self.jammers:
            uthread.new(self.UpdateJammersAfterBallRemoval, [ ball.id for ball, _, _ in pythonBalls if ball ])
        if isRelease and self.compass:
            self.compass.RemoveAll()

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return
        log.LogInfo('DoBallRemove::shipui', ball.id)
        if self.controller.GetBall() is not None and ball.id == self.controller.GetBall().id:
            self.UnhookBall()
        uthread.new(self.UpdateJammersAfterBallRemoval, (ball.id,))

    def UpdateJammersAfterBallRemoval(self, ballIDs):
        jams = self.jammers.keys()
        for jammingType in jams:
            jam = self.jammers[jammingType]
            for id in jam.keys():
                sourceBallID, moduleID, targetBallID = id
                if sourceBallID in ballIDs:
                    del self.jammers[jammingType][id]

    def ProcessShipEffect(self, godmaStm, effectState):
        if effectState.error is not None:
            uthread.new(uicore.Message, effectState.error[0], effectState.error[1])

    def OnJamStart(self, sourceBallID, moduleID, targetBallID, jammingType, startTime, duration):
        durationInClient = GetDurationInClient(startTime, duration)
        if durationInClient < 0.0:
            return
        if jammingType not in self.jammers:
            self.jammers[jammingType] = {}
        jammerID = (sourceBallID, moduleID, targetBallID)
        self.jammers[jammingType][jammerID] = (blue.os.GetSimTime(), durationInClient)
        if self.buffBarContainer and targetBallID == session.shipid:
            self.buffBarContainer.StartTimer(jammingType, jammerID, durationInClient)

    def OnJamEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        if jammingType in self.jammers:
            jammerID = (sourceBallID, moduleID, targetBallID)
            if jammerID in self.jammers[jammingType]:
                del self.jammers[jammingType][jammerID]

    def OnShipScanCompleted(self, shipID, capacitorCharge, capacitorCapacity, hardwareList):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        slimItem = bp.slimItems[shipID]
        wndName = GetByLabel('UI/Inflight/ScanWindowName', itemName=GetSlimItemName(slimItem), title=GetByLabel('UI/Inflight/ScanResult'))
        ShipScan.CloseIfOpen(windowID='shipscan', windowInstanceID=shipID)
        ShipScan.Open(windowID='shipscan', windowInstanceID=shipID, caption=wndName, shipID=shipID, results=(capacitorCharge, capacitorCapacity, hardwareList))

    def OnCargoScanComplete(self, shipID, cargoList):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        wnd = CargoScan.Open(windowID='cargoscanner', windowInstanceID=shipID, shipID=shipID, cargoList=cargoList)
        if wnd:
            wnd.LoadResult(cargoList)

    def UnhookBall(self):
        self.controller.InvalidateBall()

    def OnShipChanged(self, *args):
        self.SetupShip(animate=True)

    @threadutils.Throttled(1.5)
    def SetupShip(self, animate = False):
        if self.setupShipTasklet is not None:
            self.setupShipTasklet.kill()
        self.setupShipTasklet = uthread.new(self._SetupShip, animate)

    @telemetry.ZONE_METHOD
    def _SetupShip(self, animate = False):
        if self.destroyed or self.initing or not self.shipuiReady:
            return
        self.initing = True
        try:
            while not self.controller.IsLoaded():
                blue.synchro.Yield()

            if not sm.GetService('viewState').IsViewActive('planet') and sm.GetService('ui').IsUiVisible():
                self.state = uiconst.UI_PICKCHILDREN
            self.ResetUpdateTasklet()
            self.sr.rampTimers = {}
            self.slotsContainer.InitSlots(animate)
            self.hudButtons.InitButtons()
            self.SetButtonState()
            self.CheckControl()
            self.UpdateButtonsForShip()
            self.capacitorContainer.InitCapacitor()
            self.DrawFighters()
            self.InitFighters()
            self.ShowHideFighters()
            if self.CheckShipHasFighterBay():
                self.moduleToggleBtn.display = True
            else:
                self.moduleToggleBtn.display = False
                if self.shipSelectHilight.display:
                    self.shipSelectHilight.display = False
            blue.pyos.synchro.SleepWallclock(200)
        except Exception as e:
            log.LogException(e)
        finally:
            self.initing = False
            if self.display:
                sm.GetService('michelle').DetectAndFixMissingHudModules()

    def ResetUpdateTasklet(self):
        if self.updateTasklet:
            self.updateTasklet.kill()
        self.updateTasklet = uthread.new(self.UpdateGauges)

    def SetSpeed(self, speedRatio):
        self.controller.SetSpeed(speedRatio)

    def Hide(self):
        self.state = uiconst.UI_HIDDEN

    def Show(self):
        self.state = uiconst.UI_PICKCHILDREN

    def OnMouseEnter(self, *args):
        uicore.layer.inflight.HideTargetingCursor()

    def GetMenu(self):
        return self.controller.GetMenu()

    @telemetry.ZONE_FUNCTION
    def UpdateGauges(self):
        while not self.destroyed:
            try:
                if self.controller.IsLoaded():
                    self.heatGauges.Update()
                    self.hpGauges.Update()
                    self.UpdateReadouts()
            except Exception as e:
                log.LogException(e)

            blue.synchro.SleepWallclock(500)

    def UpdateReadouts(self):
        self.CheckShowReadoutCont()
        if self.readoutCont.state != uiconst.UI_HIDDEN:
            if settings.user.ui.Get('readoutType', 1):
                self.readoutCont.UpdateHpPercentages()
            else:
                self.readoutCont.UpdateHpAbsolutes()


class BaseSpeedButtonCont(Container):
    default_width = 12
    default_height = 12
    default_state = uiconst.UI_NORMAL
    default_texturePath = ''

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        texturePath = attributes.get('texturePath', self.default_texturePath)
        Sprite(parent=self, texturePath=texturePath, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.controller = attributes.controller

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.ExecuteCommand()

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def ExecuteCommand(self):
        pass


class MaxSpeedButton(BaseSpeedButtonCont):
    default_name = 'MaxSpeedButton'
    default_texturePath = 'res:/UI/Texture/classes/ShipUI/plus.png'

    def ExecuteCommand(self):
        self.controller.SetMaxSpeed()

    def GetHint(self):
        return GetByLabel('UI/Inflight/SetFullSpeed', maxSpeed=self.controller.GetSpeedMaxFormatted())


class StopButton(BaseSpeedButtonCont):
    default_name = 'StopButton'
    uniqueUiName = pConst.UNIQUE_NAME_STOP_BUTTON
    default_texturePath = 'res:/UI/Texture/classes/ShipUI/minus.png'
    default_hint = GetByLabel('UI/Inflight/StopTheShip')

    def ExecuteCommand(self, *args):
        self.controller.StopShip()


class CenterHudContainer(UiHiderMixin, Container):
    uniqueUiName = pConst.UNIQUE_NAME_HUD_CENTER

    def ApplyAttributes(self, attributes):
        super(CenterHudContainer, self).ApplyAttributes(attributes)

    def AnimateReveal(self):
        PlaySound('onboarding_ui_sfx_play')
        self.opacity = 0
        self.Show()
        animations.BlinkIn(self, startVal=0.2, endVal=1.0, loops=3)


class HudContainer(Container):
    default_name = 'hudContainer'
    default_width = SHIP_UI_WIDTH
    default_height = SHIP_UI_HEIGHT

    def set_protobuf_event_context(self, event):
        event.set_is_in_ship_hud()


def ResetSetFightersDetachedPos():
    return settings.char.ui.Delete('fightersDetachedPosition')


def GetFightersDetachedPos():
    return settings.char.ui.Get('fightersDetachedPosition', (uicore.desktop.width / 2, uicore.desktop.height / 2 - 60))


def is_compass_enabled():
    return settings.user.ui.Get('showSensorOverlay', False)
