#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerFiles\probeScannerPalette.py
import functools
import weakref
import blue
import eve.common.lib.appConst as appConst
import evetypes
import gametime
import localization
import probescanning.formations as formations
import trinity
import uthread
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys import service
from carbon.common.script.util.format import FmtDist, FmtAmt
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import TextColor, uiconst
from carbonui.button.const import HEIGHT_COMPACT
from carbonui.window.segment.underlay import WindowSegmentUnderlay
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label
from eve.client.script.ui.control.tooltips import ShortcutHint
from eve.client.script.ui.inflight.scannerFiles.scannerToolsUIComponents import FilterBox, IgnoredBox, ProbeTooltipButtonRow, ProbeTooltipCheckboxRow, FormationButton
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import IsProbeScanPanelEmbedded
from eve.client.script.ui.inflight.scannerFiles.scanResults import ScanResults
from eve.client.script.ui.inflight.scannerfiltereditor import ScannerFilterEditor
from eve.client.script.ui.util.uix import QtyPopup
from eve.common.script.sys.idCheckers import IsAbyssalSpaceSystem, IsVoidSpaceSystem
from eveexceptions import UserError
from inventorycommon.const import groupSurveyProbe
from localization import GetByLabel
from probescanning.analyzeButton import AnalyzeButton, AnalyzeButtonController
from probescanning.const import probeStateIdle, probeStateInactive, probeLauncherTypeID
from probescanning.scanBonusController import ScanBonusController
from probescanning.tooltips.scanBonusTooltip import ScanBonusTooltip
from probescanning.tooltips.scanProbeTooltip import ScanProbeTooltip
from fsdBuiltData.common.iconIDs import GetIconFile
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
CORE_SCANNER_PROBE_TYPE_ID = 30013

def AddFilter(*args):
    filterOptions = sm.GetService('scanSvc').GetFilterOptions()
    customFilters = [ (filterName, filterID) for filterName, filterID in filterOptions if filterID > 0 ]
    if len(customFilters) >= 25:
        raise UserError('TooManyFilters')
    editor = ScannerFilterEditor.Open()
    editor.LoadData(None)


def UserErrorIfScanning(action, *args, **kwargs):

    @functools.wraps(action)
    def wrapper(*args, **kwargs):
        if sm.GetService('scanSvc').IsScanning():
            raise UserError('ScanInProgressGeneric')
        return action(*args, **kwargs)

    return wrapper


class ProbeScannerPalette(Container):
    __notifyevents__ = ['OnProbeAdded',
     'OnProbeRemoved',
     'OnProbeRangeUpdated',
     'OnSystemScanFilterChanged',
     'OnSystemScanBegun',
     'OnSystemScanDone',
     'OnNewScannerFilterSet',
     'OnProbeStateUpdated',
     'OnProbePositionsUpdated',
     'OnScannerDisconnected',
     'OnRefreshScanResults',
     'OnBallparkSetState',
     'OnReconnectToProbesAvailable',
     'OnModuleFitted',
     'OnModuleOnlineChange',
     'OnChargeLoadedToModule',
     'OnProbeScannerUndocked',
     'OnProbeScannerDocked',
     'OnSessionChanged']
    __disallowanalysisgroups = [groupSurveyProbe]
    filteredBoxTooltip = None
    isBeingTransformed = False
    solarSystemView = None

    def ApplyAttributes(self, attributes):
        super(ProbeScannerPalette, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.window = attributes.Get('window', None)
        self.updateTimer = None
        self._filter_toggle_queue = set()
        self.scanSvc = sm.GetService('scanSvc')
        self.scanBonusController = ScanBonusController()
        self.isAnimatingProbeIcon = False
        self.ConstructLayout()
        self.UpdateControls()

    def UpdateControls(self):
        self.UpdateLabels()
        self.LoadProbeIcon()
        self.UpdateSizeSlider()
        self.ActivateBonusTooltips()
        self.CheckButtonStates()
        uthread.new(self.LoadResultList)

    def _IsCompactHeaderWindow(self):
        return self.window and self.window.compact and not self.window.stacked and not self.window.collapsed

    def Reconstruct(self):
        self.Flush()
        self.probeStateCont.Flush()
        self.ConstructLayout()
        self.UpdateControls()

    def ConstructLayout(self):
        self.ConstructFilterCont()
        self.ConstructBottomCont()
        self.ConstructProbeStateCont()
        self.ConstructFooter()
        self.ConstructScroll()

    def ConstructBottomCont(self):
        if self.window is None:
            pad_left = pad_right = pad_bottom = 4
        else:
            pad_left, _, pad_right, pad_bottom = self.window.content_padding
        self.bottomContainer = Container(name='BottomContainer', parent=self, align=uiconst.TOBOTTOM, height=64, padTop=pad_bottom)
        WindowSegmentUnderlay(bgParent=self.bottomContainer, padding=(-pad_left,
         -pad_bottom,
         -pad_right,
         -pad_bottom))

    def ConstructProbeStateCont(self):
        self.probeStateCont = Container(name='probeStateCont', parent=self.bottomContainer, align=uiconst.TOTOP, height=24, padBottom=4)
        self.probeInfoContainer = ContainerAutoSize(name='probeInfoContainer', parent=self.probeStateCont, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, padLeft=4)
        iconSize = 28
        self.probeSprite = Sprite(name='ProbeSprite', parent=self.probeInfoContainer, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, pos=(1,
         0,
         iconSize,
         iconSize))
        self.probesLaunchedLabel = EveLabelMedium(name='ProbesLaunchedLabel', parent=self.probeInfoContainer, align=uiconst.CENTERLEFT, left=iconSize + 4)
        self.recoverButton = ButtonIcon(name='RecoverProbesButton', parent=self.probeStateCont, iconSize=16, width=16, padLeft=4, hint=GetByLabel('UI/Inflight/Scanner/RecoverActiveProbes'), texturePath='res:/UI/Texture/Classes/ProbeScanner/16/recoverProbesIcon.png', func=self.RecoverActiveProbes, align=uiconst.TORIGHT, uniqueUiName=pConst.UNIQUE_NAME_RECOVER_PROBES)
        self.reconnectButton = ButtonIcon(hint=localization.GetByLabel('UI/Inflight/Scanner/ReconnectActiveProbes'), func=self.ReconnectToLostProbes, texturePath='res:/UI/Texture/Classes/ProbeScanner/16/reconnectProbesIcon.png', parent=self.probeStateCont, iconSize=16, width=16, align=uiconst.TORIGHT, padLeft=4)
        self.ConstructBonusIcons()
        if session.role & service.ROLE_QA:
            self.probeInfoContainer.GetMenu = self.QAGetMenu

    def OnSessionChanged(self, isRemote, session, change):
        self.LoadResultList()

    def QAGetMenu(self):
        return [('QA: Set Probe duration in seconds', self.QASetProbeDuration)]

    def QASetProbeDuration(self):
        qty = QtyPopup(7200, 30, 1)
        self.scanSvc.QAOverrideProbeExpiry(qty['qty'] * 1000)

    def LoadProbeIcon(self):
        typeID = self.scanSvc.GetActiveProbeTypeID()
        if not typeID:
            self.probeSprite.opacity = 0.3
            self.probeInfoContainer.tooltipPanelClassInfo = ScanProbeTooltip(typeID, self.GetProbeExpiryTimeLeft)
            typeID = probeLauncherTypeID
        else:
            self.probeSprite.opacity = 1.0
            self.probeInfoContainer.tooltipPanelClassInfo = ScanProbeTooltip(typeID, self.GetProbeExpiryTimeLeft)
        iconID = evetypes.GetIconID(typeID)
        texturePath = GetIconFile(iconID)
        self.probeSprite.texturePath = texturePath

    def ConstructBonusIcons(self):
        self.bonusesContainer = ContainerAutoSize(name='bonusesContainer', parent=self.probeStateCont, align=uiconst.TORIGHT, padRight=8)
        self.strengthBonusContainer = ContainerAutoSize(name='strengthBonusContainer', parent=self.bonusesContainer, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
        self.strengthIcon = Sprite(name='strengthIcon', parent=Container(parent=self.strengthBonusContainer, align=uiconst.TOLEFT, width=16), align=uiconst.CENTER, texturePath='res:/UI/Texture/Classes/ProbeScanner/16/Strength.png', width=16, height=16, state=uiconst.UI_DISABLED, color=eveColor.LED_GREY)
        self.strengthLabel = Label(parent=ContainerAutoSize(parent=self.strengthBonusContainer, align=uiconst.TOLEFT), align=uiconst.CENTER, state=uiconst.UI_DISABLED, padLeft=3)
        self.deviationBonusContainer = ContainerAutoSize(name='deviationBonusContainer', parent=self.bonusesContainer, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, padLeft=6)
        self.deviationIcon = Sprite(name='deviationIcon', parent=Container(parent=self.deviationBonusContainer, align=uiconst.TOLEFT, width=16), align=uiconst.CENTER, texturePath='res:/UI/Texture/Classes/ProbeScanner/16/Deviation.png', width=16, height=16, state=uiconst.UI_DISABLED, color=eveColor.LED_GREY)
        self.deviationLabel = Label(parent=ContainerAutoSize(parent=self.deviationBonusContainer, align=uiconst.TOLEFT), align=uiconst.CENTER, state=uiconst.UI_DISABLED, padLeft=3)
        self.durationBonusContainer = ContainerAutoSize(name='durationContainer', parent=self.bonusesContainer, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, padLeft=6)
        self.durationIcon = Sprite(name='durationIcon', parent=Container(parent=self.durationBonusContainer, align=uiconst.TOLEFT, width=16), align=uiconst.CENTER, texturePath='res:/UI/Texture/Classes/ProbeScanner/16/Time.png', width=16, height=16, state=uiconst.UI_DISABLED, color=eveColor.LED_GREY)
        self.durationLabel = Label(parent=ContainerAutoSize(parent=self.durationBonusContainer, align=uiconst.TOLEFT), align=uiconst.CENTER, state=uiconst.UI_DISABLED, padLeft=3)

    def ActivateBonusTooltips(self):
        self.strengthBonusContainer.tooltipPanelClassInfo = ScanBonusTooltip(name='Strength', iconPath='res:/UI/Texture/Classes/ProbeScanner/16/Strength.png', totalValueFunc=self.scanBonusController.GetTotalScanStrength, baseValueFunc=self.scanBonusController.GetBaseScanStrength, skillBonusFunc=self.scanBonusController.GetScanStrengthBonusFromSkills, implantBonusFunc=self.scanBonusController.GetScanStrengthBonusFromImplants, shipBonusFunc=self.scanBonusController.GetScanStrengthBonusFromShip, moduleBonusFunc=self.scanBonusController.GetScanStrengthBonusFromModules, totalBonusFunc=self.scanBonusController.GetTotalScanStrengthBonus)
        self.deviationBonusContainer.tooltipPanelClassInfo = ScanBonusTooltip(name='Deviation', iconPath='res:/UI/Texture/Classes/ProbeScanner/16/Deviation.png', totalValueFunc=self.scanBonusController.GetTotalScanDeviation, baseValueFunc=self.scanBonusController.GetBaseScanDeviation, skillBonusFunc=self.scanBonusController.GetScanDeviationBonusFromSkills, implantBonusFunc=self.scanBonusController.GetScanDeviationBonusFromImplants, shipBonusFunc=self.scanBonusController.GetScanDeviationBonusFromShip, moduleBonusFunc=self.scanBonusController.GetScanDeviationBonusFromModules, totalBonusFunc=self.scanBonusController.GetTotalScanDeviationBonus)
        self.durationBonusContainer.tooltipPanelClassInfo = ScanBonusTooltip(name='Duration', iconPath='res:/UI/Texture/Classes/ProbeScanner/16/Time.png', totalValueFunc=self.scanBonusController.GetTotalScanDuration, baseValueFunc=self.scanBonusController.GetBaseScanDuration, skillBonusFunc=self.scanBonusController.GetScanDurationBonusFromSkills, implantBonusFunc=self.scanBonusController.GetScanDurationBonusFromImplants, shipBonusFunc=self.scanBonusController.GetScanDurationBonusFromShip, moduleBonusFunc=self.scanBonusController.GetScanDurationBonusFromModules, totalBonusFunc=self.scanBonusController.GetTotalScanDurationBonus)

    def DeactivateBonusTooltips(self):
        self.strengthBonusContainer.tooltipPanelClassInfo = None
        self.deviationBonusContainer.tooltipPanelClassInfo = None
        self.durationBonusContainer.tooltipPanelClassInfo = None

    def ConstructFilterCont(self):
        padding = (0, 4, 0, 0) if self._IsCompactHeaderWindow() else 0
        self.filterCont = Container(name='filterCont', parent=self.window.header.extra_content if self._IsCompactHeaderWindow() else self, align=uiconst.TOTOP, height=HEIGHT_COMPACT, padding=padding)
        if not self._IsCompactHeaderWindow():
            EveLabelMedium(name='ScanResultsLabel', parent=self.filterCont, text=GetByLabel('UI/Inflight/Scanner/ScanResults'), align=uiconst.CENTERLEFT, left=2)
        self.ignoredBox = IgnoredBox(name='IgnoredBox', parent=self.filterCont, text=GetByLabel('UI/Inflight/Scanner/Ignored', noIgnored=0), state=uiconst.UI_NORMAL, align=uiconst.TORIGHT, padLeft=4)
        self.ignoredBox.LoadTooltipPanel = self.LoadIgnoredTooltipPanel
        self.filteredBox = FilterBox(name='FilteredBox', parent=self.filterCont, text=GetByLabel('UI/Inflight/Scanner/Filtered', noFiltered=0), state=uiconst.UI_NORMAL, align=uiconst.TORIGHT, uniqueUiName=pConst.UNIQUE_NAME_FILTER_SCAN_RESULTS, padLeft=4)
        self.filteredBox.LoadTooltipPanel = self.LoadFilterTooltipPanel
        self.mapButton = ButtonIcon(name='solarSystemMapButton', parent=self.filterCont, align=uiconst.TOLEFT if self._IsCompactHeaderWindow() else uiconst.TORIGHT, width=24, iconSize=16, texturePath='res:/UI/Texture/Shared/Brackets/solarSystem.png', hint=GetByLabel('UI/Map/MapPallet/btnSolarsystemMap'), func=self.MapBtnClicked)
        self.mapButton.display = not IsProbeScanPanelEmbedded()

    def MapBtnClicked(self, *args):
        uicore.cmd.GetCommandAndExecute('CmdToggleSolarSystemMap')

    def ConstructFooter(self):
        self.formationButtonsContainer = ContainerAutoSize(name='FormationButtonsContainer', parent=self.bottomContainer, align=uiconst.TOLEFT, uniqueUiName=pConst.UNIQUE_NAME_PROBE_FORMATIONS)
        self.ConstructFormationButtons()
        buttonCont = ContainerAutoSize(name='AnalyzeButtonContainer', uniqueUiName=pConst.UNIQUE_NAME_PROBE_REFRESH, parent=self.bottomContainer, align=uiconst.TORIGHT, padLeft=8)
        self.primaryButtonController = AnalyzeButtonController(self.scanSvc)
        self.primaryButton = AnalyzeButton(name='PrimaryButton', parent=buttonCont, align=uiconst.CENTER, cmd=uicore.cmd.commandMap.GetCommandByName('CmdRefreshProbeScan'), fixedwidth=100, controller=self.primaryButtonController)
        sliderCont = Container(name='sliderCont', parent=Container(parent=self.bottomContainer, padLeft=8), align=uiconst.TORIGHT_PROP, width=1.0, maxWidth=120)
        self.sliderLabel = EveLabelMedium(name='sliderLabel', align=uiconst.TOTOP, parent=sliderCont)
        self.sizeSlider = Slider(name='SizeSlider', parent=sliderCont, align=uiconst.TOTOP, minValue=1, maxValue=8, on_dragging=self.UpdateProbeSizeFromSliderInput, callback=self.UpdateProbeSizeFromSliderInput, increments=[ i for i in range(1, 9) ], barHeight=10, uniqueUiName=pConst.UNIQUE_NAME_PROBE_SIZE_MODIFIER, hint=localization.GetByLabel('UI/Inflight/Scanner/ProbeSize'))

    def ConstructFormationButtons(self):
        self.formationButtonsByID = {}
        buttonSize = 32
        self.pinpointFormationButton = ButtonIcon(parent=self.formationButtonsContainer, fixedheight=buttonSize, iconSize=buttonSize, iconPadding=0, hint=GetByLabel('UI/Inflight/Scanner/LaunchPinpointFormation'), texturePath='res:/UI/Texture/classes/ProbeScanner/32/pinpointFormation.png', func=lambda *args: self.LaunchFormation(formations.PINPOINT_FORMATION), align=uiconst.TOLEFT, soundClick='msg_newscan_probe_formation_play')
        self.formationButtonsByID[formations.PINPOINT_FORMATION] = self.pinpointFormationButton
        self.spreadFormationButton = ButtonIcon(parent=self.formationButtonsContainer, iconSize=buttonSize, hint=GetByLabel('UI/Inflight/Scanner/LaunchSpreadFormation'), texturePath='res:/UI/Texture/classes/ProbeScanner/32/spreadFormation.png', func=lambda *args: self.LaunchFormation(formations.SPREAD_FORMATION), align=uiconst.TOLEFT, padLeft=2, soundClick='msg_newscan_probe_formation_play')
        self.formationButtonsByID[formations.SPREAD_FORMATION] = self.spreadFormationButton
        self.customFormationButton = FormationButton(name='CustomFormationButton', parent=self.formationButtonsContainer, width=buttonSize, iconSize=buttonSize, align=uiconst.TOLEFT, padLeft=2, launchFunc=self.LaunchFormation)
        self.formationButtonsByID[formations.CUSTOM_FORMATION] = self.customFormationButton
        self.centerOnSelfFormationButton = ButtonIcon(parent=self.formationButtonsContainer, iconSize=buttonSize, hint=GetByLabel('UI/Inflight/Scanner/CenterOnSelf'), texturePath='res:/UI/Texture/classes/ProbeScanner/32/centerProbes.png', func=lambda *args: self.LaunchFormation(formations.SELF_CENTER_FORMATION), align=uiconst.TOLEFT, padLeft=2, soundClick='msg_newscan_probe_formation_play')
        self.formationButtonsByID[formations.SELF_CENTER_FORMATION] = self.centerOnSelfFormationButton

    def OnProbeAdded(self, probe):
        self.UpdateLabels()
        self.UpdateSizeSlider()
        self.LoadProbeIcon()

    def OnProbeScannerUndocked(self):
        self.mapButton.Show()

    def OnProbeScannerDocked(self):
        self.mapButton.Hide()

    def UpdateSizeSlider(self):
        probeData = self.scanSvc.GetProbeData()
        if len(probeData) < 1:
            median = 0
        else:
            rangeSteps = [ data.rangeStep for probe, data in probeData.iteritems() ]
            median = self.GetMedian(rangeSteps)
        self.sizeSlider.SetValue(median)

    def GetMedian(self, list):
        if len(list) < 1:
            return None
        sortedList = sorted(list)
        listLength = len(list)
        index = (listLength - 1) // 2
        return sortedList[index]

    def OnProbeRemoved(self, probe):
        self.UpdateLabels()
        self.UpdateSizeSlider()
        self.LoadProbeIcon()

    def OnProbeRangeUpdated(self, probeID, scanRange):
        self.UpdateSizeSliderLabel()
        self.UpdateSizeSlider()

    def GetProbeScanRangeText(self, probeData):
        probeScanRangeText = self.GetAverageSizeInAU(probeData)
        probeScanRangeText = '' if probeScanRangeText == 0 else probeScanRangeText
        return probeScanRangeText

    def GetAverageSizeInAU(self, probeData):
        if len(probeData) <= 0:
            return 0
        sizes = []
        for probeID, data in probeData.iteritems():
            sizes.append(data.scanRange)

        medianSize = self.GetMedian(sizes)
        if medianSize < appConst.AU:
            probeScanRangeText = FmtDist(medianSize, maxdemicals=2)
        else:
            probeScanRangeText = FmtDist(medianSize, maxdemicals=0)
        return probeScanRangeText

    def UpdateProbeSizeFromSliderInput(self, slider):
        probeData = self.scanSvc.GetProbeData()
        if not probeData:
            return
        newRange = int(slider.GetValue())
        if len(probeData) <= 0:
            medianRange = 0
        else:
            rangeSteps = [ data.rangeStep for probe, data in probeData.iteritems() ]
            medianRange = self.GetMedian(rangeSteps)
        if newRange != medianRange:
            scale = 1.0
            if newRange < medianRange:
                scale = 0.5
            elif newRange > medianRange:
                scale = 2.0
            for x in range(abs(medianRange - newRange)):
                self.scanSvc.ScaleFormation(scale)

        self.UpdateSizeSliderLabel()

    def UpdateSizeSliderLabel(self, *args):
        self.sliderLabel.SetText(self.GetProbeScanRangeText(self.scanSvc.GetProbeData()))

    def ConstructScroll(self):
        self.scanResultsContainer = Container(name='ScanResultsContainer', parent=self, align=uiconst.TOALL, clipChildren=True, padTop=0 if self._IsCompactHeaderWindow() else 4)
        self.resultScroll = ScanResults(name='resultScroll', parent=self.scanResultsContainer, id='probescannerwindow_resultScrollList', palette=self)

    def Close(self, *args):
        sm.UnregisterNotify(self)
        super(ProbeScannerPalette, self).Close()

    def GetSolarSystemView(self):
        from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
        solarSystemView = SolarSystemViewPanel.GetIfOpen()
        if solarSystemView and not solarSystemView.destroyed:
            return solarSystemView

    def ToggleFilterShortcut(self, vkey):
        localShortCuts = (uiconst.VK_1,
         uiconst.VK_2,
         uiconst.VK_3,
         uiconst.VK_4,
         uiconst.VK_5,
         uiconst.VK_6)
        if vkey not in localShortCuts:
            return False
        filterIndex = localShortCuts.index(vkey)
        self.ToggleFilter(filterIndex)
        return True

    def _ToggleShowAnomalies(self):
        toggleState = not settings.user.ui.Get('scannerShowAnomalies', True)
        settings.user.ui.Set('scannerShowAnomalies', toggleState)
        if toggleState:
            self.scanSvc.ShowAnomalies()
        else:
            self.scanSvc.StopShowingAnomalies()
        uthread.new(self.ReloadFilteredBoxTooltip)

    def ToggleFilter(self, filterIndex):
        if filterIndex in self._filter_toggle_queue:
            self._filter_toggle_queue.remove(filterIndex)
        else:
            self._filter_toggle_queue.add(filterIndex)
        self._UpdateFiltersThrottled()

    def _ToggleFilter(self, filterIndex):
        filterOptions = self.scanSvc.GetFilterOptions()
        filterOptionIDs = [ filterID for filterName, filterID in filterOptions if filterID < 0 ]
        filterID = filterOptionIDs[filterIndex - 1]
        activeFilters = self.scanSvc.GetActiveFilterSet()
        if filterID in activeFilters:
            self.scanSvc.RemoveFromActiveFilterSet(filterID)
        else:
            self.scanSvc.AddToActiveFilterSet(filterID)
        uthread.new(self.ReloadFilteredBoxTooltip)

    @uthread2.debounce(wait=0.1, leading=True)
    def _UpdateFiltersThrottled(self):
        while self._filter_toggle_queue:
            filter_index = self._filter_toggle_queue.pop()
            if filter_index == 0:
                self._ToggleShowAnomalies()
            else:
                self._ToggleFilter(filter_index)

    def OnSystemScanFilterChanged(self, *args):
        self.LoadResultList()

    def OnSystemScanBegun(self):
        self.Refresh()
        self.resultScroll.on_system_scan_started()

    def OnSystemScanDone(self):
        self.Refresh()
        self.resultScroll.on_system_scan_ended()

    def GetProbesTooltipPointer(self):
        return uiconst.POINT_TOP_3

    def LoadHelpTooltip(self, tooltipPanel, *args):
        tooltipPanel.columns = 2
        tooltipPanel.margin = (12, 4, 4, 4)
        tooltipPanel.cellPadding = (1, 1, 1, 1)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Inflight/Scanner/HelpToModify'), wrapWidth=120)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Inflight/Scanner/HelpHold'), align=uiconst.CENTERRIGHT)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Inflight/Scanner/FormationProbeRange'), wrapWidth=120)
        tooltipPanel.AddCell(ShortcutHint(text=trinity.app.GetKeyNameText(uiconst.VK_MENU), align=uiconst.TOPRIGHT), cellPadding=(6, 1, 1, 1))
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Inflight/Scanner/FormationSpread'), wrapWidth=120)
        tooltipPanel.AddCell(ShortcutHint(text=trinity.app.GetKeyNameText(uiconst.VK_CONTROL), align=uiconst.TOPRIGHT), cellPadding=(6, 1, 1, 1))
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Inflight/Scanner/OneProbe'), wrapWidth=120)
        tooltipPanel.AddCell(ShortcutHint(text=trinity.app.GetKeyNameText(uiconst.VK_SHIFT), align=uiconst.TOPRIGHT), cellPadding=(6, 1, 1, 1))

    def LoadFilterTooltipPanel(self, tooltipPanel, *args):
        return self._LoadFilterTooltipPanel(tooltipPanel, *args)

    def _LoadFilterTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.Flush()
        tooltipPanel.columns = 4
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.cellPadding = (5, 2, 5, 2)
        tooltipPanel.margin = (0, 1, 0, 1)
        header = eveLabel.EveLabelLarge(text=GetByLabel('UI/Inflight/Scanner/ShowResultsFor'), align=uiconst.CENTERLEFT, color=TextColor.HIGHLIGHT, padding=(0, 2, 0, 2))
        tooltipPanel.AddCell(header, colSpan=tooltipPanel.columns, cellPadding=(7, 3, 5, 3))
        tooltipPanel.AddRow(rowClass=ProbeTooltipCheckboxRow, text=GetByLabel('UI/Inflight/Scanner/AnomalySiteFilterLabel'), checked=settings.user.ui.Get('scannerShowAnomalies', True), func=self.OnShowAnomaliesCheckBoxChange, filterIndex=1)
        filterOptions = self.scanSvc.GetFilterOptions()
        activeFilters = self.scanSvc.GetActiveFilterSet()
        standardFilters = [ (filterName, filterID) for filterName, filterID in filterOptions if filterID < 0 ]
        for i, (filterName, filterID) in enumerate(standardFilters):
            if filterID < 0:
                tooltipPanel.AddRow(rowClass=ProbeTooltipCheckboxRow, text=filterName, checked=filterID in activeFilters, settingsKey=filterID, func=self.OnFilterCheckBoxChange, filterIndex=i + 2)

        customFilters = [ (filterName, filterID) for filterName, filterID in filterOptions if filterID > 0 ]
        if customFilters:
            for filterName, filterID in customFilters:
                if filterID > 0:
                    tooltipPanel.AddRow(rowClass=ProbeTooltipCheckboxRow, text=filterName, checked=filterID in activeFilters, settingsKey=filterID, func=self.OnFilterCheckBoxChange, deleteFunc=(self.DeleteFilter, (filterID,)), editFunc=(self.EditFilter, (filterID,)))

        buttonRow = tooltipPanel.AddRow(rowClass=ProbeTooltipButtonRow, text=GetByLabel('UI/Inflight/Scanner/CreateNewFilter'), texturePath='res:/UI/Texture/Classes/ProbeScanner/saveformationProbesIcon.png', func=AddFilter)
        self.filteredBoxTooltip = weakref.ref(tooltipPanel)

    def ReloadFilteredBoxTooltip(self):
        if not self.filteredBoxTooltip or self.destroyed:
            return
        filteredBoxTooltip = self.filteredBoxTooltip()
        if filteredBoxTooltip is not None:
            self._LoadFilterTooltipPanel(filteredBoxTooltip)

    def LoadIgnoredTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.Flush()
        tooltipPanel.margin = 3
        resultsIgnored = self.scanSvc.GetIgnoredResultsDesc()
        if not resultsIgnored:
            return
        scroll = ScrollContainer(align=uiconst.TOPLEFT, parent=tooltipPanel)
        scroll.isTabStop = False
        subGrid = LayoutGrid(parent=scroll, align=uiconst.TOPLEFT, columns=4)
        rowOrder = []
        if len(resultsIgnored) > 1:
            row = subGrid.AddRow(rowClass=ProbeTooltipButtonRow, text=GetByLabel('UI/Inflight/Scanner/ClearAllIgnoredResults'), texturePath='res:/UI/Texture/Classes/ProbeScanner/clearIgnoredMenu.png', func=self.ClearIgnoredResults, width=200)
            rowOrder.append(row)
        ids = sorted(resultsIgnored)
        for id, desc in ids:
            if desc:
                displayDesc = GetByLabel('UI/Inflight/Scanner/ResultIdAndDesc', id=id, desc=desc)
            else:
                displayDesc = id
            row = subGrid.AddRow(rowClass=ProbeTooltipButtonRow, text=displayDesc, texturePath='res:/UI/Texture/Classes/ProbeScanner/clearIgnoredMenu.png', func=self.UnIgnoreResult, funcArgs=(id,), width=200)
            rowOrder.append(row)

        subGrid.RefreshGridLayout()
        scroll.width = subGrid.width + (5 if len(rowOrder) > 10 else 0)
        totalHeight = 0
        for row in rowOrder[:10]:
            totalHeight += row.height

        scroll.height = totalHeight
        tooltipPanel.state = uiconst.UI_NORMAL
        self.ignoredTooltip = weakref.ref(tooltipPanel)

    def ClearIgnoredResults(self, *args):
        self.scanSvc.ClearIgnoredResults()
        ignoredTooltip = self.ignoredTooltip()
        if ignoredTooltip is not None:
            self.LoadIgnoredTooltipPanel(ignoredTooltip)

    def UnIgnoreResult(self, resultID, *args):
        self.scanSvc.ShowIgnoredResult(resultID)
        ignoredTooltip = self.ignoredTooltip()
        if ignoredTooltip is not None:
            self.LoadIgnoredTooltipPanel(ignoredTooltip)

    def OnShowAnomaliesCheckBoxChange(self, settingsKey, settingState, *args):
        settings.user.ui.Set('scannerShowAnomalies', settingState)
        if settingState:
            self.scanSvc.ShowAnomalies()
        else:
            self.scanSvc.StopShowingAnomalies()
        self.LoadResultList()

    def OnClick(self, *args):
        uicore.registry.SetFocus(self.resultScroll)

    def DeleteFilter(self, settingsKey):
        response = uicore.Message('DeleteFilter', {'filterName': self.scanSvc.resultFilter.GetFilterName(settingsKey)}, uiconst.YESNO, suppress=uiconst.ID_YES)
        if response != uiconst.ID_YES:
            return
        self.scanSvc.DeleteFilter(settingsKey)
        self.scanSvc.RemoveFromActiveFilterSet(settingsKey)
        uthread.new(self.ReloadFilteredBoxTooltip)

    def OnFilterCheckBoxChange(self, settingsKey, settingState, *args):
        if settingState:
            self.scanSvc.AddToActiveFilterSet(settingsKey)
        else:
            self.scanSvc.RemoveFromActiveFilterSet(settingsKey)

    def ValidateProbesState(self, probeIDs, isEntryButton = False):
        probeData = self.scanSvc.GetProbeData()
        for probeID in probeIDs:
            if probeID in probeData:
                probe = probeData[probeID]
                if isEntryButton:
                    if probe.state not in (probeStateIdle, probeStateInactive):
                        return False
                elif probe.state != probeStateIdle:
                    return False

        return True

    def LoadCurrentSolarSystem(self):
        self.LoadResultList()

    def OnNewScannerFilterSet(self, *args):
        self.LoadResultList()

    def OnProbePositionsUpdated(self):
        self.CheckButtonStates()

    def OnScannerDisconnected(self):
        self.LoadResultList()
        self.CheckButtonStates()
        self.UpdateLabels()

    def LaunchFormation(self, formationID):
        if formationID == formations.SELF_CENTER_FORMATION:
            self.scanSvc.CenterProbesOnMe()
        else:
            self.scanSvc.MoveProbesToFormation(formationID)
        self.UpdateSizeSlider()
        self.UpdateLabels()

    def EditFilter(self, filterID, *args):
        editor = ScannerFilterEditor.Open()
        editor.LoadData(filterID)

    def LoadResultList(self):
        if self.destroyed:
            return
        self.resultScroll.load_results()

    def CheckButtonStates(self):
        if self.destroyed:
            return
        canClaim = self.scanSvc.CanClaimProbes()
        if canClaim:
            self.recoverButton.Enable()
        else:
            self.recoverButton.Disable()
        probes = self.scanSvc.GetActiveProbes()
        allIdle = self.ValidateProbesState(probes)
        if probes and allIdle:
            self.recoverButton.Enable()
            self.sizeSlider.Show()
        else:
            self.recoverButton.Disable()
            self.sizeSlider.Hide()
        for formationID, button in self.formationButtonsByID.iteritems():
            try:
                canLaunch = self.scanSvc.CanLaunchFormation(formationID)
            except KeyError:
                if allIdle:
                    button.Enable()
                else:
                    button.Disable()
                continue

            if canLaunch and allIdle:
                button.Enable()
            else:
                button.Disable()

        self.UpdateProbeInfo()
        self.buttonRefreshTimer = AutoTimer(interval=500, method=self.CheckButtonStates)

    def GetProbeHandler(self):
        solarSystemView = self.GetSolarSystemView()
        if solarSystemView and solarSystemView.mapView:
            solarSystemHandler = solarSystemView.mapView.currentSolarsystem
            if solarSystemHandler and solarSystemHandler.solarsystemID == session.solarsystemid2:
                return solarSystemHandler.probeHandler

    def RefreshProbeResults(self):
        probeHandler = self.GetProbeHandler()
        if probeHandler:
            probeHandler.SetResultFilter([], update=True)

    @UserErrorIfScanning
    def ReconnectToLostProbes(self, *args):
        self.scanSvc.ReconnectToLostProbes()

    @UserErrorIfScanning
    def RecoverActiveProbes(self, *args):
        probes = self.scanSvc.GetActiveProbes()
        self.scanSvc.RecoverProbes(probes)
        self.StopAnimatingProbeIcon()

    @UserErrorIfScanning
    def Analyze(self, *args):
        if IsAbyssalSpaceSystem(session.solarsystemid2):
            key = 'ProbeScannerAbyssalSpaceWarning'
            response = eve.Message(key, buttons=uiconst.YESNO, suppress=uiconst.ID_YES)
            if response == uiconst.ID_NO:
                self.CheckButtonStates()
                return
        elif IsVoidSpaceSystem(session.solarsystemid2):
            raise UserError('ProbeScannerVoidSpaceHint')
        try:
            self.scanSvc.RequestScans()
        except UserError as e:
            self.CheckButtonStates()
            raise e
        finally:
            self.LoadResultList()

    def Confirm(self, *args):
        uthread.new(self.primaryButtonController.click)

    def Refresh(self):
        self.refreshTimer = AutoTimer(interval=200, method=self.DoRefresh)

    def DoRefresh(self):
        self.refreshTimer = None
        if self.destroyed:
            return
        self.CheckButtonStates()
        self.LoadResultList()
        self.UpdateLabels()

    def UpdateLabels(self):
        self.UpdateSizeSliderLabel()
        self.UpdateProbeInfo()

    def UpdateProbeInfoText(self):
        probeData = self.scanSvc.GetProbeData()
        numProbes = len(probeData)
        if numProbes:
            text = 'X %s' % numProbes
        elif not self.scanSvc.HasOnlineProbeLauncher():
            text = GetByLabel('UI/Inflight/Scanner/NoLauncherFitted')
        elif self.scanSvc.GetChargesInProbeLauncher():
            text = GetByLabel('UI/Inflight/Scanner/NoProbesLaunched')
        else:
            text = GetByLabel('UI/Inflight/Scanner/NoProbesInLauncher')
        self.probesLaunchedLabel.SetText(text)
        color = Label.default_color if numProbes else eveColor.WARNING_ORANGE
        self.probesLaunchedLabel.SetRGBA(*color)

    def UpdateBonusLabelsText(self):
        if self.scanSvc.GetProbeData():
            self.strengthLabel.SetText(self.FormatBonusAmount(self.scanBonusController.GetTotalScanStrength(), fractions=1))
            self.deviationLabel.SetText(self.FormatBonusAmount(self.scanBonusController.GetTotalScanDeviation(), fractions=3, suffix=' AU'))
            self.durationLabel.SetText(self.FormatBonusAmount(self.scanBonusController.GetTotalScanDuration(), fractions=0, suffix='s'))

    def UpdateBonusLabelVisibility(self):
        if self.scanSvc.GetProbeData():
            self.bonusesContainer.Show()
            self.strengthLabel.display = self.deviationLabel.display = self.durationLabel.display = False
        else:
            self.bonusesContainer.Hide()

    def UpdateReconnectButtonVisibility(self):
        if self.scanSvc.GetProbeData():
            self.reconnectButton.Hide()
        elif self.scanSvc.HasOnlineProbeLauncher():
            self.reconnectButton.Show()
        else:
            self.reconnectButton.Hide()

    def FormatBonusAmount(self, amount, fractions, suffix = ''):
        if amount == 0:
            return '-'
        else:
            return FmtAmt(amount, showFraction=fractions) + suffix

    def GetProbeExpiryTimeLeft(self):
        probeData = self.scanSvc.GetProbeData()
        if len(probeData) <= 0:
            return None
        else:
            timeLeft = 0
            for probeID, data in probeData.iteritems():
                timeLeft = long(gametime.GetSecondsUntilSimTime(data.expiry)) * gametime.SEC
                break

            if timeLeft <= 0:
                self.StopAnimatingProbeIcon()
                return timeLeft
            if timeLeft >= gametime.HOUR:
                self.StopAnimatingProbeIcon()
                return localization.formatters.FormatTimeIntervalShortWritten(timeLeft, showFrom='day', showTo='minute')
            if timeLeft <= gametime.MIN * 5:
                self.StartBlinkingProbeIcon()
            return localization.formatters.FormatTimeIntervalShortWritten(timeLeft, showFrom='day', showTo='second')

    def StartBlinkingProbeIcon(self):
        if not self.isAnimatingProbeIcon:
            PlaySound('msg_newscan_probe_expire_play')
            animations.BlinkIn(self.probeSprite, duration=1, loops=uiconst.ANIM_REPEAT, startVal=0.1, curveType=uiconst.ANIM_BOUNCE)
            self.isAnimatingProbeIcon = True

    def StopAnimatingProbeIcon(self):
        if self.isAnimatingProbeIcon:
            animations.StopAllAnimations(self.probeSprite)
            self.isAnimatingProbeIcon = False

    def OnRefreshScanResults(self):
        self.Refresh()

    def OnBallparkSetState(self):
        self.Refresh()

    def ShowFilteredAndIgnored(self, filtered, ignored, filteredAnomalies):
        self.filteredBox.SetText(GetByLabel('UI/Inflight/Scanner/Filtered', noFiltered=filtered + filteredAnomalies))
        self.ignoredBox.UpdateIgnoredAmount(ignored)

    def OnReconnectToProbesAvailable(self):
        self.CheckButtonStates()
        self.UpdateProbeInfo()

    def OnModuleFitted(self, charId, flag, typeID, groupID):
        self.UpdateProbeInfo()

    def OnModuleOnlineChange(self, item, oldValue, newValue):
        self.UpdateProbeInfo()

    def UpdateProbeInfo(self):
        if not self.destroyed:
            self.UpdateBonusLabelVisibility()
            self.UpdateBonusLabelsText()
            self.UpdateReconnectButtonVisibility()
            self.UpdateProbeInfoText()
            self.GetProbeExpiryTimeLeft()

    def OnChargeLoadedToModule(self):
        blue.synchro.Sleep(1000)
        self.UpdateProbeInfo()
        self.LoadProbeIcon()
