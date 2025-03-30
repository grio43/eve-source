#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerFiles\directionalScannerPalette.py
import math
import weakref
import blue
import evetypes
import trinity
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_WORLDMOD
from carbon.common.script.util.format import FmtDist
from carbonui import ButtonVariant, Density, TextColor, uiconst
from carbonui.button import styling
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.scrollentries import ScrollEntryNode
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.slider import Slider
from carbonui.window.segment.underlay import WindowSegmentUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.gradientSprite import GradientConst, GradientSprite
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.services.setting import UserSettingEnum
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.tooltips import ShortcutHint
from eve.client.script.ui.inflight.overview import overviewUtil
from eve.client.script.ui.inflight.scannerFiles import scanButton
from eve.client.script.ui.inflight.scannerFiles.directionalScanResultEntry import DirectionalScanResultEntry
from eve.client.script.ui.inflight.scannerFiles.directionalScanUtil import ConvertAuToKm, ConvertKmToAu, GetActiveScanMode, GetScanAngle, GetScanRange, IsDscanConeShown, MAX_RANGE_AU, MIN_RANGE_AU, RANGEMODE_AU, RANGEMODE_KM, SCANMODE_CAMERA, SetScanAngle, SetScanConeDisplayState, SetScanRange, ToggleScanMode
from eve.client.script.ui.inflight.scannerFiles.scannerToolsUIComponents import FilterBox
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import COLOR_DSCAN, IsDirectionalScanPanelEmbedded
from eve.client.script.ui.shared.mapView.controls.mapViewCheckbox import MapViewCheckbox
from eve.client.script.ui.shared.maps.browserwindow import MapBrowserWnd
from eve.common.lib import appConst
from localization import GetByLabel
from qtyTooltip.qtyConst import EDIT_INPUT_TYPE_NO_NUMBERHINT
from signals import Signal
ANGLE_INCREMENTS = [5,
 15,
 30,
 60,
 90,
 180,
 360]
MIN_WINDOW_WIDTH = 320
MIN_WINDOW_HEIGHT = 200
TOP_CONT_HEIGHT = 18
RANGE_EDIT_MODE_SETTING = UserSettingEnum('scanner_rangeEditMode', RANGEMODE_AU, options=[RANGEMODE_KM, RANGEMODE_AU])

def ToggleRangeEditModeSetting(*args):
    if RANGE_EDIT_MODE_SETTING.is_equal(RANGEMODE_AU):
        RANGE_EDIT_MODE_SETTING.set(RANGEMODE_KM)
    else:
        RANGE_EDIT_MODE_SETTING.set(RANGEMODE_AU)


class DistanceEditCont(Container):

    def ApplyAttributes(self, attributes):
        super(DistanceEditCont, self).ApplyAttributes(attributes)
        RANGE_EDIT_MODE_SETTING.on_change.connect(self.OnRangeEditModeSettingChanged)
        self.on_changing = Signal('on_changing')
        self.on_changed = Signal('on_changed')
        self.ConstructLayout()
        self.UpdateInputVisibility()

    def ConstructLayout(self):
        self.rangeLabel = EveLabelMedium(text=GetByLabel('UI/Inflight/Scanner/Range'), parent=ContainerAutoSize(parent=self, align=uiconst.TOLEFT), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, padRight=4)
        self.unitToggleButton = Button(parent=self, align=uiconst.TORIGHT, func=ToggleRangeEditModeSetting, density=Density.COMPACT, padLeft=4, variant=ButtonVariant.GHOST)
        self.UpdateUnitToggleButtonLabel()
        self.auInput = SingleLineEditFloat(name='auInput', parent=self, align=uiconst.TOALL, OnReturn=self.OnEditChanged, OnFocusLost=self.OnEditChanging, OnChange=self.OnEditChanging, inputType=EDIT_INPUT_TYPE_NO_NUMBERHINT, state=uiconst.UI_HIDDEN, minValue=MIN_RANGE_AU, maxValue=MAX_RANGE_AU, decimalPlaces=True)
        self.auInput.SetHistoryVisibility(False)
        self.kmInput = SingleLineEditInteger(name='kmInput', parent=self, align=uiconst.TOALL, OnReturn=self.OnEditChanged, OnFocusLost=self.OnEditChanging, OnChange=self.OnEditChanging, inputType=EDIT_INPUT_TYPE_NO_NUMBERHINT, state=uiconst.UI_HIDDEN, minValue=ConvertAuToKm(MIN_RANGE_AU), maxValue=ConvertAuToKm(MAX_RANGE_AU))

    def GetScanRangeAU(self):
        if RANGE_EDIT_MODE_SETTING.is_equal(RANGEMODE_KM):
            scanRange = self.kmInput.GetValue()
            scanRangeAU = ConvertKmToAu(scanRange)
            SetScanRange(scanRange)
        else:
            scanRangeAU = self.auInput.GetValue()
            SetScanRange(ConvertAuToKm(scanRangeAU))
        return scanRangeAU

    def SetScanRangeAU(self, scanRangeAU):
        if RANGE_EDIT_MODE_SETTING.is_equal(RANGEMODE_KM):
            kmValue = ConvertAuToKm(scanRangeAU)
            self.kmInput.SetValue(kmValue, docallback=False)
        else:
            self.auInput.SetValue(scanRangeAU, docallback=False)

    def IsRangeEditInFocus(self):
        return uicore.registry.GetFocus() in (self.kmInput, self.auInput)

    def OnEditChanged(self, *args):
        self.on_changed()

    def OnEditChanging(self, *args):
        self.on_changing()

    def ShowKMInput(self):
        self.kmInput.Show()
        self.auInput.Hide()

    def ShowAUInput(self):
        self.auInput.Show()
        self.kmInput.Hide()

    def UpdateUnitToggleButtonLabel(self):
        if RANGE_EDIT_MODE_SETTING.is_equal(RANGEMODE_AU):
            self.unitToggleButton.SetLabel(GetByLabel('UI/Inflight/Scanner/UnitAU'))
        else:
            self.unitToggleButton.SetLabel(GetByLabel('UI/Inflight/Scanner/UnitKm'))

    def OnRangeEditModeSettingChanged(self, *args):
        self.UpdateInputVisibility()

    def UpdateInputVisibility(self):
        if RANGE_EDIT_MODE_SETTING.is_equal(RANGEMODE_AU):
            scanRangeAU = ConvertKmToAu(GetScanRange())
            self.ShowAUInput()
            self.auInput.SetValue(scanRangeAU)
            self.unitToggleButton.SetLabel(GetByLabel('UI/Inflight/Scanner/UnitAU'))
        else:
            self.ShowKMInput()
            self.kmInput.SetValue(GetScanRange())
            self.unitToggleButton.SetLabel(GetByLabel('UI/Inflight/Scanner/UnitKm'))

    def _OnSizeChange_NoBlock(self, width, height):
        self.rangeLabel.display = width > 150


class DirectionalScannerPalette(Container):
    __notifyevents__ = ['OnOverviewPresetSaved',
     'OnBallparkSetState',
     'OnDirectionalScanComplete',
     'OnDirectionalScanStarted',
     'OnDirectionalScannerScanModeChanged',
     'OnDirectionalScannerRangeChanged',
     'OnDirectionalScannerUndocked',
     'OnDirectionalScannerDocked']
    performAnotherScan = False
    filteredBoxTooltip = None

    def ApplyAttributes(self, attributes):
        super(DirectionalScannerPalette, self).ApplyAttributes(attributes)
        scanOnOpen = attributes.Get('scanOnOpen', True)
        self.window = attributes.Get('window', None)
        self.scanSvc = sm.GetService('directionalScanSvc')
        self.scanresult = []
        sm.RegisterNotify(self)
        self.ConstructLayout()
        if scanOnOpen and not self.scanSvc.IsScanning():
            self.DirectionalScan()
        self.UpdateScroll()

    def Reconstruct(self):
        self.Flush()
        self.headerCont.Flush()
        self.ConstructLayout()
        self.UpdateScroll()

    def Close(self, *args, **kwds):
        Container.Close(self, *args, **kwds)

    def Confirm(self, *args):
        self.scanButtonController.click()

    def ToggleFitlerShortcut(self, vkey):
        localShortCuts = (uiconst.VK_1,
         uiconst.VK_2,
         uiconst.VK_3,
         uiconst.VK_4,
         uiconst.VK_5,
         uiconst.VK_6,
         uiconst.VK_7,
         uiconst.VK_8)
        if vkey not in localShortCuts:
            return False
        shortCutIndex = localShortCuts.index(vkey)
        presetOptions = self.GetPresetOptions()
        filterName, filterID = presetOptions[shortCutIndex]
        try:
            uthread.new(self.OnFilterChange, filterID, True)
        except IndexError:
            pass

        return True

    def ConstructLayout(self):
        padTop = self.window.content_padding[0] if self.window else 8
        self.bottomCont = Container(name='bottomCont', parent=self, align=uiconst.TOBOTTOM, padTop=padTop, height=styling.get_height(Density.NORMAL))
        if self.window:
            pad_left, _, pad_right, pad_bottom = self.window.content_padding
            WindowSegmentUnderlay(bgParent=self.bottomCont, padding=(-pad_left,
             -pad_bottom,
             -pad_right,
             -pad_bottom))
        self.ConstructScanButton()
        self.sliderCont = Container(name='sliderCont', parent=self.bottomCont)
        self.ConstructDistanceCont()
        self.ConstructAngleCont()
        if self._IsCompactHeaderWindow():
            self.headerCont = self.window.header.extra_content
        else:
            self.headerCont = Container(parent=self, name='headerCont', align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, padBottom=2, height=styling.get_height(Density.NORMAL))
        self.ConstructScroll()
        self.ReconstructHeader()

    def ConstructScanButtonCarbon(self):
        self.scanButtonController = scanButton.ScanButtonController(directional_scan_service=self.scanSvc, service_manager=sm)
        self.scanButton = scanButton.ScanButton(parent=self.bottomCont, align=uiconst.CENTERRIGHT, cmd=uicore.cmd.commandMap.GetCommandByName('CmdRefreshDirectionalScan'), controller=self.scanButtonController)

    def ConstructDistanceSliderCarbon(self):
        self.rangeLabel = EveLabelSmall(text=GetByLabel('UI/Inflight/Scanner/Range'), parent=self.bottomCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, left=2)
        self.rangeFlowCont = FlowContainer(parent=self.bottomCont, padding=(self.rangeLabel.left + self.rangeLabel.width + 6,
         0,
         self.scanButton.width + 2,
         0), align=uiconst.TOTOP, contentSpacing=(4, 2))
        startingKmValue = GetScanRange()
        startingAuValue = ConvertKmToAu(startingKmValue)
        minIncrement = max(MIN_RANGE_AU, 0.1)
        self.distanceSlider = Slider(name='distanceSlider', parent=self.rangeFlowCont, minValue=0, maxValue=MAX_RANGE_AU, callback=self.EndSetDistanceSliderValue, on_dragging=self.OnSetDistanceSliderValue, increments=[minIncrement,
         1,
         5,
         10,
         MAX_RANGE_AU], width=90, align=uiconst.NOALIGN, barHeight=10)
        self.distanceSlider.SetValue(startingAuValue)
        self.distanceSlider.barCont.LoadTooltipPanel = self.LoadDistanceSliderTooltipPanel
        subGrid = ContainerAutoSize(align=uiconst.NOALIGN, height=14, parent=self.rangeFlowCont)
        self.auInput = SingleLineEditFloat(name='auInput', parent=subGrid, align=uiconst.TOLEFT, top=0, OnReturn=self.OnScanRangeEditReturn, OnFocusLost=self.OnScanRangeEditChange, OnChange=self.OnScanRangeEditChange, inputType=EDIT_INPUT_TYPE_NO_NUMBERHINT, state=uiconst.UI_HIDDEN)
        self.auInput.SetHistoryVisibility(False)
        self.kmInput = SingleLineEditInteger(name='kmInput', parent=subGrid, align=uiconst.TOLEFT, top=0, OnReturn=self.OnScanRangeEditReturn, OnFocusLost=self.OnScanRangeEditChange, OnChange=self.OnScanRangeEditChange, inputType=EDIT_INPUT_TYPE_NO_NUMBERHINT, state=uiconst.UI_HIDDEN)
        self.unitToggleButton = Button(parent=subGrid, align=uiconst.TOLEFT, func=ToggleRangeEditModeSetting, padLeft=3)
        SetScanRange(startingKmValue)
        self.UpdateRangeInput(startingKmValue)

    def ConstructAngleSliderCarbon(self):
        subGrid = LayoutGrid(parent=self.bottomCont, align=uiconst.TOTOP, padding=(2,
         0,
         self.scanButton.width + 2,
         0), columns=3, cellSpacing=(4, 2))
        self.angleLabel = EveLabelSmall(parent=Container(parent=subGrid, align=uiconst.CENTERLEFT, width=32, height=20), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, text=GetByLabel('UI/Inflight/Scanner/Angle'))
        increments = [5,
         15,
         30,
         60,
         90,
         180,
         360]
        startingAngle = int(round(math.degrees(GetScanAngle())))
        if startingAngle not in increments:
            startingAngle = increments[-1]
        self.angleSlider = Slider(name='angleSlider', parent=subGrid, align=uiconst.CENTERLEFT, value=startingAngle, minValue=5, maxValue=360, increments=increments, isEvenIncrementsSlider=True, callback=self.EndSetAngleSliderValue, on_dragging=self.UpdateAngleSliderLabel, width=90, height=20, barHeight=10)
        self.angleSliderLabel = EveLabelSmall(text=GetByLabel('UI/Inflight/Scanner/AngleDegrees', value=startingAngle), parent=subGrid, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=4)

    def ConstructScanButton(self):
        self.scanButtonController = scanButton.ScanButtonController(directional_scan_service=self.scanSvc, service_manager=sm)
        scanButtonCont = ContainerAutoSize(name='scanButtonCont', align=uiconst.TORIGHT, parent=self.bottomCont, padLeft=8)
        self.scanButton = scanButton.ScanButton(parent=scanButtonCont, align=uiconst.CENTERRIGHT, cmd=uicore.cmd.commandMap.GetCommandByName('CmdRefreshDirectionalScan'), controller=self.scanButtonController)

    def ConstructDistanceCont(self):
        distanceCont = Container(name='distanceCont', parent=self.sliderCont, align=uiconst.TOLEFT_PROP, width=0.5, padRight=4)
        self.distanceEditCont = DistanceEditCont(parent=distanceCont, align=uiconst.TOTOP, height=TOP_CONT_HEIGHT)
        self.distanceEditCont.on_changing.connect(self.OnScanRangeEditChange)
        self.distanceEditCont.on_changed.connect(self.OnScanRangeEditReturn)
        self.ConstructDistanceSlider(distanceCont)

    def UpdateUnitToggleButtonLabel(self):
        if RANGE_EDIT_MODE_SETTING.is_equal(RANGEMODE_AU):
            self.unitToggleButton.SetLabel(GetByLabel('UI/Inflight/Scanner/UnitAU'))
        else:
            self.unitToggleButton.SetLabel(GetByLabel('UI/Inflight/Scanner/UnitKm'))

    def ConstructDistanceSlider(self, distanceCont):
        startingKmValue = GetScanRange()
        startingAuValue = ConvertKmToAu(startingKmValue)
        minIncrement = max(MIN_RANGE_AU, 0.1)
        self.distanceSlider = Slider(name='distanceSlider', parent=distanceCont, minValue=0, maxValue=MAX_RANGE_AU, callback=self.EndSetDistanceSliderValue, on_dragging=self.OnSetDistanceSliderValue, increments=[minIncrement,
         1,
         5,
         10,
         MAX_RANGE_AU], align=uiconst.TOTOP, barHeight=10, top=3)
        self.distanceSlider.SetValue(startingAuValue)
        self.distanceSlider.barCont.LoadTooltipPanel = self.LoadDistanceSliderTooltipPanel

    def ConstructAngleCont(self):
        angleCont = Container(name='angleCont', parent=self.sliderCont, align=uiconst.TOLEFT_PROP, width=0.5, padLeft=4)
        topCont = Container(name='topCont', parent=angleCont, align=uiconst.TOTOP, height=TOP_CONT_HEIGHT)
        self.angleLabel = EveLabelMedium(parent=ContainerAutoSize(parent=topCont, align=uiconst.TOLEFT), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
        self.UpdateAngleSliderLabel()
        startingAngle = int(round(math.degrees(GetScanAngle())))
        if startingAngle not in ANGLE_INCREMENTS:
            startingAngle = ANGLE_INCREMENTS[-1]
        self.angleSlider = Slider(name='angleSlider', parent=angleCont, align=uiconst.TOTOP, value=startingAngle, minValue=5, maxValue=360, increments=ANGLE_INCREMENTS, isEvenIncrementsSlider=True, callback=self.EndSetAngleSliderValue, on_dragging=self.UpdateAngleSliderLabel, height=20, barHeight=10, top=3)

    def ConstructScroll(self):
        self.scroll = Scroll(name='dirscroll', parent=self)
        self.scroll.sr.fixedColumns = DirectionalScanResultEntry.GetFixedColumns()
        self.scroll.sr.defaultColumnWidth = DirectionalScanResultEntry.GetColumnsDefaultSize()
        self.scroll.sr.id = 'scanner_dirscroll'
        self.scroll.OnChar = None
        self.animBGCont = Container(parent=self.scroll)
        self.animBG = GradientSprite(parent=self.animBGCont, align=uiconst.TORIGHT_PROP, width=1.0, colorType=uiconst.COLORTYPE_FLASH, blendMode=trinity.TR2_SBM_ADD, rotation=0.0, color=COLOR_DSCAN, rgbData=[(0, (1, 1, 1))], alphaData=[(0, 0),
         (0.95, 0.3),
         (0.99, 0.5),
         (1, 1)], alphaInterp=GradientConst.INTERP_LINEAR, colorInterp=GradientConst.INTERP_LINEAR, opacity=0)

    def ReconstructHeader(self):
        self.headerCont.Flush()
        if not self._IsCompactHeaderWindow():
            EveLabelMedium(text=GetByLabel('UI/Inflight/Scanner/ScanResults'), parent=self.headerCont, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, left=2)
        self.filteredBox = FilterBox(parent=self.headerCont, text='-', state=uiconst.UI_NORMAL, align=uiconst.CENTERRIGHT if self._IsCompactHeaderWindow() else uiconst.TORIGHT, padLeft=4, density=Density.COMPACT, maxWidth=120)
        self.filteredBox.LoadTooltipPanel = self.LoadFilterTooltipPanel
        buttonCont = ContainerAutoSize(name='buttonCont', align=uiconst.TOLEFT if self._IsCompactHeaderWindow() else uiconst.TORIGHT, parent=self.headerCont)
        self.alignWithCameraBtn = ButtonIcon(name='alignWithCameraBtn', parent=buttonCont, align=uiconst.TOLEFT, width=16, iconSize=16, texturePath='res:/UI/Texture/classes/MapView/alignwithCamera.png', func=self.OnAlignWithCameraBtn, hint=GetByLabel('UI/Inflight/Scanner/AlignWithCamera'))
        self.UpdateAlignWithCameraBtn()
        self.showConeBtn = ButtonIcon(name='showConeBtn', parent=buttonCont, align=uiconst.TOLEFT, padLeft=4, width=16, iconSize=16, texturePath='res:/UI/Texture/classes/MapView/dScanIcon.png', func=self.OnShowConeBtn, hint=GetByLabel('UI/Inflight/Scanner/ShowScanCone'))
        self.UpdateShowConeButton()
        self.mapButton = ButtonIcon(name='solarSystemMapButton', parent=buttonCont, align=uiconst.TOLEFT, iconSize=16, width=16, padLeft=8, texturePath='res:/UI/Texture/Shared/Brackets/solarSystem.png', hint=GetByLabel('UI/Map/MapPallet/btnSolarsystemMap'), func=self.MapBtnClicked)
        self.mapButton.display = not IsDirectionalScanPanelEmbedded()

    def _IsCompactHeaderWindow(self):
        return self.window and self.window.compact and not self.window.stacked and not self.window.collapsed

    def MapBtnClicked(self, *args):
        uicore.cmd.GetCommandAndExecute('CmdToggleSolarSystemMap')

    def LoadDistanceSliderTooltipPanel(self, tooltipPanel, *args):
        if IsDirectionalScanPanelEmbedded():
            tooltipPanel.LoadGeneric2ColumnTemplate()
            shortcutTxt = self.scanButton.cmd.GetShortcutAsString()
            tooltipPanel.AddLabelShortcut(GetByLabel('UI/Inflight/Scanner/AdjustRange'), GetByLabel('UI/Inflight/Scanner/AdjustRangeShortcut', shortcut=shortcutTxt))

    def UpdateAlignWithCameraBtn(self):
        if GetActiveScanMode() == SCANMODE_CAMERA:
            self.alignWithCameraBtn.SetSelected()
        else:
            self.alignWithCameraBtn.SetDeselected()

    def OnAlignWithCameraBtn(self):
        ToggleScanMode()
        self.UpdateAlignWithCameraBtn()

    def OnClick(self, *args):
        uicore.registry.SetFocus(self.scroll)

    def UpdateShowConeButton(self):
        if IsDscanConeShown():
            self.showConeBtn.SetSelected()
        else:
            self.showConeBtn.SetDeselected()

    def OnShowConeBtn(self):
        SetScanConeDisplayState(not IsDscanConeShown())
        self.UpdateShowConeButton()

    def LoadFilterTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.Flush()
        tooltipPanel.columns = 1
        tooltipPanel.cellPadding = 2
        tooltipPanel.state = uiconst.UI_NORMAL
        header = eveLabel.EveLabelLarge(text=GetByLabel('UI/Inflight/Scanner/ShowResultsFor'), align=uiconst.CENTERLEFT, color=TextColor.HIGHLIGHT, padding=(0, 2, 0, 2))
        tooltipPanel.AddCell(header, colSpan=tooltipPanel.columns, cellPadding=(7, 3, 5, 3))
        tooltipPanel.scroll = Scroll(parent=tooltipPanel, align=uiconst.TOPLEFT, width=220, height=200)
        tooltipPanel.scroll.OnUpdatePosition = self.OnScrollPositionChanged
        self.filteredBoxTooltip = weakref.ref(tooltipPanel)
        self.LoadFilters()

    def LoadFilters(self):
        filteredBoxTooltip = self.filteredBoxTooltip()
        if not filteredBoxTooltip:
            return
        scrollPosition = settings.char.ui.Get('directionalScanFilterPos', 0.0)
        presetSelected = settings.user.ui.Get('scanner_presetInUse', None)
        presetOptions = self.GetPresetOptions()
        scrollEntries = []
        for i, (filterName, filterID) in enumerate(presetOptions):
            if i < 10:
                filterIndex = (i + 1) % 10
            else:
                filterIndex = None
            scrollNode = ScrollEntryNode(label=filterName, checked=filterID == presetSelected, cfgname=filterID, OnChange=self.OnFilterCheckBoxChange, entryWidth=210, decoClass=FilterOptionEntry, filterIndex=filterIndex, group='directionalScannerFilterGroup')
            scrollEntries.append(scrollNode)

        filteredBoxTooltip.scroll.Load(contentList=scrollEntries, scrollTo=scrollPosition)
        filteredBoxTooltip.scroll.height = min(200, filteredBoxTooltip.scroll.GetContentHeight() + 2)

    def OnScrollPositionChanged(self, *args, **kwargs):
        filteredBoxTooltip = self.filteredBoxTooltip()
        if filteredBoxTooltip:
            settings.char.ui.Set('directionalScanFilterPos', filteredBoxTooltip.scroll.GetScrollProportion())

    def OnFilterCheckBoxChange(self, checkbox, *args):
        settingKey = checkbox.GetSettingsKey()
        self.OnFilterChange(settingKey, True)

    def OnFilterChange(self, settingKey, settingState, *args):
        settings.user.ui.Set('scanner_presetInUse', settingKey)
        if self.scanresult:
            uthread.new(self.UpdateScroll)
        else:
            self.DirectionalScan()
        self.ReloadFilteredBoxTooltip()

    def ReloadFilteredBoxTooltip(self):
        if not self.filteredBoxTooltip or self.destroyed:
            return
        filteredBoxTooltip = self.filteredBoxTooltip()
        if filteredBoxTooltip is not None:
            self.LoadFilters()

    def UpdateRangeInput(self, scanRangeKM):
        if RANGE_EDIT_MODE_SETTING.is_equal(RANGEMODE_AU):
            scanRangeAU = ConvertKmToAu(scanRangeKM)
            self.ShowAUInput()
            self.auInput.SetMinValue(MIN_RANGE_AU)
            self.auInput.SetMaxValue(MAX_RANGE_AU)
            self.auInput.decimalPlaces = 1
            self.auInput.SetValue(scanRangeAU)
            self.auInput.width = 45
            self.unitToggleButton.SetLabel(GetByLabel('UI/Inflight/Scanner/UnitAU'))
        else:
            self.ShowKMInput()
            self.kmInput.SetMinValue(ConvertAuToKm(MIN_RANGE_AU))
            self.kmInput.SetMaxValue(ConvertAuToKm(MAX_RANGE_AU))
            self.kmInput.SetValue(scanRangeKM)
            self.unitToggleButton.SetLabel(GetByLabel('UI/Inflight/Scanner/UnitKm'))
            self.kmInput.width = 90
        self.UpdateUnitToggleButtonLabel()

    def ShowKMInput(self):
        self.kmInput.Show()
        self.auInput.Hide()

    def ShowAUInput(self):
        self.auInput.Show()
        self.kmInput.Hide()

    def OnRangeEditModeSettingChanged(self, *args):
        self.UpdateRangeInput(GetScanRange())

    def GetPresetOptions(self):
        presetSvc = sm.GetService('overviewPresetSvc')
        options = [(GetByLabel('UI/Inflight/Scanner/UseActiveOverviewSettings'), None)]
        for presetName in overviewUtil.GetCustomFiltersSorted() + overviewUtil.GetDefaultFiltersSorted():
            options.append((presetSvc.GetPresetDisplayName(presetName), presetName))

        return options

    def OnScanConeAligned(self):
        self.DirectionalScan()

    def OnBallparkSetState(self):
        if not self.destroyed:
            self.DirectionalScan()

    def OnOverviewPresetSaved(self):
        uthread.new(self.UpdateScroll)

    def OnDirectionalScannerScanModeChanged(self, scanMode):
        self.UpdateAlignWithCameraBtn()

    def OnDirectionalScannerUndocked(self):
        self.mapButton.Show()

    def OnDirectionalScannerDocked(self):
        self.mapButton.Hide()

    def UpdateAngleSliderLabel(self, *args):
        startingAngle = int(round(math.degrees(GetScanAngle())))
        self.angleLabel.text = u'{}: {}'.format(GetByLabel('UI/Inflight/Scanner/Angle'), GetByLabel('UI/Inflight/Scanner/AngleDegrees', value=startingAngle))

    def OnScanRangeEditChange(self, *args):
        PlaySound('msg_newscan_directional_shape_play')
        self._UpdateScanRange()

    def OnScanRangeEditReturn(self):
        self._UpdateScanRange()
        self.DirectionalScan()

    def _UpdateScanRange(self):
        scanRangeAU = self._GetScanRangeAU()
        self.distanceSlider.SetValue(scanRangeAU)

    def _GetScanRangeAU(self):
        return self.distanceEditCont.GetScanRangeAU()

    def OnDirectionalScannerRangeChanged(self, range):
        value = ConvertKmToAu(range / 1000)
        if value > 0.5:
            value = round(value, 3)
        self.distanceSlider.SetValue(value)
        rangeInputFocused = self.distanceEditCont.IsRangeEditInFocus()
        if not rangeInputFocused:
            self.UpdateDistanceFromSlider()

    def UpdateDistanceFromSlider(self):
        scanRangeAU = self.distanceSlider.GetValue()
        self.distanceEditCont.SetScanRangeAU(scanRangeAU)

    def EndSetDistanceSliderValue(self, *args):
        self.UpdateDistanceFromSlider()
        PlaySound('msg_newscan_directional_shape_play')
        self._GetScanRangeAU()
        if not self.scanSvc.IsScanning():
            self.DirectionalScan()

    def OnSetDistanceSliderValue(self, slider, *args):
        if not slider.isDragging:
            return
        self.UpdateDistanceFromSlider()

    def EndSetAngleSliderValue(self, slider):
        angle = math.radians(slider.GetValue())
        PlaySound('msg_newscan_directional_shape_play')
        SetScanAngle(angle)
        if not self.scanSvc.IsScanning():
            self.DirectionalScan()
        self.UpdateAngleSliderLabel()

    def DirectionalScan(self, direction = None):
        uthread.new(self._DirectionalScan, direction)

    def _DirectionalScan(self, direction = None, *args, **kwds):
        self.scanSvc.DirectionalScan(direction)

    def OnDirectionalScanComplete(self, scanangle, scanRange, direction, results):
        self.scanresult = results
        uthread.new(self.AnimFlashOnScanDone)
        self.UpdateScroll()

    def AnimFlashOnScanDone(self):
        duration = 1.7
        animations.FadeTo(self.animBG, 1.0, 0.0, duration=duration)
        animations.MorphScalar(self.animBG, 'width', 1.0, 0.0, duration=duration)

    def OnDirectionalScanStarted(self):
        self.scanresult = []

    def UpdateScroll(self, *args):
        selectedValue = settings.user.ui.Get('scanner_presetInUse', None)
        if selectedValue is None:
            selectedValue = sm.GetService('overviewPresetSvc').GetActiveOverviewPresetName()
        filters = sm.GetService('overviewPresetSvc').GetValidGroups(presetName=selectedValue)
        ballpark = sm.GetService('michelle').GetBallpark()
        filtered = 0
        scrolllist = []
        if self.scanresult and ballpark:
            scanresult = self.scanresult[:]
            prime = []
            for celestialRec in scanresult:
                if celestialRec.id not in ballpark.balls:
                    prime.append(celestialRec.id)

            if prime:
                cfg.evelocations.Prime(prime)
            for celestialRec in scanresult:
                if self.destroyed:
                    return
                if celestialRec.groupID not in filters:
                    filtered += 1
                    continue
                if not session.role & (ROLE_GML | ROLE_WORLDMOD):
                    if evetypes.GetGroupID(celestialRec.typeID) == appConst.groupCloud:
                        continue
                entry = self.GetScrollEntry(ballpark, celestialRec)
                scrolllist.append(entry)
                blue.pyos.BeNice()

        filteredText = GetByLabel('UI/Inflight/Scanner/Filtered', noFiltered=filtered)
        activeFilterName = sm.GetService('overviewPresetSvc').GetDefaultOverviewDisplayName(selectedValue)
        self.filteredBox.SetText('%s (%s)' % (filteredText, activeFilterName))
        headers = DirectionalScanResultEntry.GetColumns()
        self.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=GetByLabel('UI/Inflight/Scanner/DirectionalNoResult'))

    def GetScrollEntry(self, ballpark, celestialRec):
        typeName = evetypes.GetName(celestialRec.typeID)
        if evetypes.GetGroupID(celestialRec.typeID) == appConst.groupHarvestableCloud:
            entryname = GetByLabel('UI/Inventory/SlimItemNames/SlimHarvestableCloud', typeName)
        elif evetypes.GetCategoryID(celestialRec.typeID) == appConst.categoryAsteroid:
            entryname = GetByLabel('UI/Inventory/SlimItemNames/SlimAsteroid', typeName)
        else:
            try:
                entryname = cfg.evelocations.Get(celestialRec.id).name
            except KeyError:
                entryname = None

        if not entryname:
            entryname = typeName
        itemID = celestialRec.id
        typeID = celestialRec.typeID
        ball = ballpark.GetBall(celestialRec.id)
        if ball is not None:
            dist = ball.surfaceDist
            diststr = FmtDist(dist, maxdemicals=1)
        else:
            dist = 0
            diststr = '-'
        groupID = evetypes.GetGroupID(typeID)
        groupName = evetypes.GetGroupName(typeID)
        node = Bunch(__guid__='listentry.DirectionalScanResults', decoClass=DirectionalScanResultEntry, sortValues=(groupName,
         entryname,
         typeName,
         dist), charIndex=entryname, entryName=entryname, typeName=typeName, itemID=itemID, typeID=typeID, groupID=groupID, diststr=diststr)
        return node

    def SetMapAngle(self, angle):
        wnd = MapBrowserWnd.GetIfOpen()
        if wnd:
            wnd.SetTempAngle(angle)

    def EndSetSliderValue(self, *args):
        self.DirectionalScan()


class FilterOptionEntry(MapViewCheckbox):

    def Startup(self, *args):
        MapViewCheckbox.Startup(self, *args)
        if self.sr.node.filterIndex is not None:
            shortcutObj = ShortcutHint(parent=self, text=str(self.sr.node.filterIndex), left=2, top=2)
            self.TEXTRIGHT = shortcutObj.width + 4
