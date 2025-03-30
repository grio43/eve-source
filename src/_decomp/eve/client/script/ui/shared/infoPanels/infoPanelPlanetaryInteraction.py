#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelPlanetaryInteraction.py
import carbonui.const as uiconst
import eveicon
import uthread
import eve.client.script.ui.shared.planet.planetCommon as planetCommon
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
from carbonui.button.group import ButtonGroup
from carbonui import AxisAlignment, ButtonVariant, Density
from carbonui.control.button import Button
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.cloneGrade.omegaRestrictedEntryInfoPanel import OmegaRestrictedEntryInfoPanel
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.const.infoPanelConst import PANEL_PLANETARY_INTERACTION
from eve.client.script.ui.shared.planet.resourceController import ResourceController
from eve.client.script.ui.shared.planet.planetEditModeContainer import PlanetEditModeContainer
from eve.client.script.ui.shared.planet.pinContainers.BasePinContainer import CaptionAndSubtext
from eve.client.script.ui.shared.shipTree.infoBubble import SkillEntry
from eve.common.lib import appConst
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel
from carbonui.uicore import uicore
EDITMODECONTAINER_HEIGHT = 105

class InfoPanelPlanetaryInteraction(InfoPanelBase):
    default_name = 'InfoPanelPlanetaryInteraction'
    panelTypeID = PANEL_PLANETARY_INTERACTION
    label = 'UI/Chat/ChannelNames/PlanetaryInteraction'
    hasSettings = False
    isCollapsable = False
    default_iconTexturePath = 'res:/UI/Texture/Classes/InfoPanels/PlanetaryInteraction.png'
    __notifyevents__ = ['OnEditModeChanged',
     'OnEditModeBuiltOrDestroyed',
     'OnPlanetCommandCenterDeployedOrRemoved',
     'OnSubscriptionChanged']

    def ApplyAttributes(self, attributes):
        InfoPanelBase.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.inEditMode = False
        self.omegaWarning = OmegaRestrictedEntryInfoPanel(parent=self.mainCont, align=uiconst.TOTOP, height=45, text=GetByLabel('UI/CloneState/PlanetExportingDisabled'), hint=GetByLabel('UI/CloneState/PlanetExportingDisabledHint'), padding=(0, 4, 0, 2))
        self.editModeContainer = Container(parent=self.mainCont, name='buttonContainer', align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, padding=(0, 0, 0, 5))
        self.editModeContent = Container(parent=self.editModeContainer, name='editModeContent', align=uiconst.TOALL, padding=(10, 6, 10, 6))
        Fill(parent=self.editModeContainer, color=Color.GetGrayRGBA(0.0, 0.3))
        Frame(parent=self.editModeContainer, color=Color.GetGrayRGBA(0.0, 0.2))
        self.modeButtonGroup = ToggleButtonGroup(parent=self.mainCont, align=uiconst.TOTOP, callback=self.OnButtonSelected, padding=(0, 4, 0, 4))
        self.tabPanelContainer = ContainerAutoSize(parent=self.mainCont, name='tabPanelContainer', align=uiconst.TOTOP)
        self.planetName = self.headerCls(parent=self.headerCont, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)
        self.resourceControllerTab = ResourceController(parent=self.tabPanelContainer)
        self.editModeTab = PlanetEditModeContainer(parent=self.tabPanelContainer)
        self.modeButtonGroup.AddButton('editModeTab', GetByLabel('UI/Common/Build'), self.editModeTab)
        scanBtn = self.modeButtonGroup.AddButton('resourceControllerTab', GetByLabel('UI/PI/Common/Scan'), self.resourceControllerTab)
        scanBtn.LoadTooltipPanel = self.LoadScanBtnTooltipPanel
        scanBtn.tooltipPointer = uiconst.POINT_LEFT_2
        btnID = settings.char.ui.Get('planetInfoPanelModeButtons', 'editModeTab')
        self.modeButtonGroup.SelectByID(btnID)
        BTNSIZE = 24
        exitBtn = ButtonIcon(parent=self.headerCont, align=uiconst.CENTERRIGHT, pos=(0,
         0,
         BTNSIZE,
         BTNSIZE), texturePath=eveicon.close, iconSize=16, func=self.ExitPlanetMode, hint=GetByLabel('UI/PI/Common/ExitPlanetMode'))
        homeBtn = ButtonIcon(parent=self.headerCont, align=uiconst.CENTERRIGHT, pos=(exitBtn.left + exitBtn.width + 2,
         0,
         BTNSIZE,
         BTNSIZE), texturePath=eveicon.house, iconSize=16, func=self.ViewCommandCenter, hint=GetByLabel('UI/PI/Common/ViewPlanetaryCommandCenter'))
        self.sr.homeBtn = homeBtn
        self.UpdatePlanetText()
        self.UpdateHomeButton()
        self.UpdateOmegaWarning()
        self.CreateEditModeContainer()
        planetUISvc = sm.GetService('planetUI')
        planetUISvc.SetModeController(self)
        uthread.new(self.OnEditModeChanged, planetUISvc.inEditMode)

    def LoadScanBtnTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/PI/Common/ScanRange'), colSpan=2, bold=True)
        tooltipPanel.AddRow(rowClass=SkillEntry, typeID=appConst.typeRemoteSensing, showLevel=False)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/PI/Common/ScanQuality'), colSpan=2, cellPadding=(0, 10, 0, 0), bold=True)
        tooltipPanel.AddRow(rowClass=SkillEntry, typeID=appConst.typePlanetology, showLevel=False)
        tooltipPanel.AddRow(rowClass=SkillEntry, typeID=appConst.typeAdvancedPlanetology, showLevel=False)

    def UpdateOmegaWarning(self):
        if not sm.GetService('cloneGradeSvc').IsOmega():
            self.omegaWarning.Show()
        else:
            self.omegaWarning.Hide()

    @staticmethod
    def IsAvailable():
        viewState = sm.GetService('viewState').GetCurrentView()
        if viewState and viewState.name == 'planet':
            return True
        return False

    def UpdatePlanetText(self):
        planetUI = sm.GetService('planetUI')
        planetID = planetUI.planetID
        planetData = sm.GetService('map').GetPlanetInfo(planetID)
        self.planetName.text = '<color=white url=showinfo:%s//%s>%s</url>' % (planetData.typeID, planetID, cfg.evelocations.Get(planetID).locationName)

    def OnButtonSelected(self, mode, *args):
        sm.GetService('audio').SendUIEvent('msg_pi_general_switch_play')
        if mode == 'resourceControllerTab':
            sm.GetService('planetUI').planetAccessRequired = True
        settings.char.ui.Set('planetInfoPanelModeButtons', mode)

    def ExitPlanetMode(self, *args):
        self.Disable()
        if not sm.GetService('viewState').CloseSecondaryView('planet'):
            self.Enable()

    def ViewCommandCenter(self, *args):
        sm.GetService('planetUI').FocusCameraOnCommandCenter()

    def OnPlanetCommandCenterDeployedOrRemoved(self, *args):
        self.UpdateHomeButton()

    def OnSubscriptionChanged(self):
        self.UpdateOmegaWarning()

    def UpdateHomeButton(self):
        if sm.GetService('planetUI').IsColonyPresent():
            self.sr.homeBtn.state = uiconst.UI_NORMAL
        else:
            self.sr.homeBtn.state = uiconst.UI_HIDDEN

    def CreateEditModeContainer(self):
        eveLabel.EveHeaderLarge(parent=self.editModeContent, text=GetByLabel('UI/PI/Common/EditsPending'), align=uiconst.RELATIVE)
        self.powerGauge = Gauge(parent=self.editModeContent, pos=(0, 22, 115, 34), color=planetCommon.PLANET_COLOR_POWER, label=GetByLabel('UI/PI/Common/PowerUsage'))
        self.cpuGauge = Gauge(parent=self.editModeContent, pos=(130, 22, 115, 34), color=planetCommon.PLANET_COLOR_CPU, label=GetByLabel('UI/PI/Common/CpuUsage'))
        self.UpdatePowerAndCPUGauges()
        self.costText = CaptionAndSubtext(parent=ContainerAutoSize(parent=self.editModeContent, align=uiconst.TOBOTTOM_NOPUSH), align=uiconst.TOPLEFT, width=120, padBottom=0, caption=GetByLabel('UI/Common/Cost'), subtext='')
        ButtonGroup(parent=self.editModeContent, align=uiconst.TOBOTTOM, button_alignment=AxisAlignment.END, density=Density.COMPACT, buttons=[Button(label=GetByLabel('UI/Common/Submit'), func=self.Submit, args=(), variant=ButtonVariant.PRIMARY), Button(label=GetByLabel('UI/Common/Cancel'), func=self.Cancel, args=())])

    def UpdatePowerAndCPUGauges(self):
        colony = sm.GetService('planetUI').GetCurrentPlanet().GetColony(session.charid)
        if not colony or colony.colonyData is None:
            return
        originalData = sm.GetService('planetUI').GetCurrentPlanet().GetEditModeData()
        if originalData is None:
            origCpu = 0
            origPower = 0
        else:
            origCpu = originalData.GetColonyCpuUsage()
            origPower = originalData.GetColonyPowerUsage()
        cpuOutput = float(colony.colonyData.GetColonyCpuSupply())
        powerOutput = float(colony.colonyData.GetColonyPowerSupply())
        cpu = colony.colonyData.GetColonyCpuUsage()
        power = colony.colonyData.GetColonyPowerUsage()
        cpuDiff = cpu - origCpu
        powerDiff = power - origPower
        self.cpuGauge.SetValue(cpu / cpuOutput if cpuOutput > 0 else 0)
        self.cpuGauge.HideAllMarkers()
        self.cpuGauge.ShowMarker(origCpu / cpuOutput if cpuOutput > 0 else 0)
        self.powerGauge.SetValue(power / powerOutput if powerOutput > 0 else 0)
        self.powerGauge.HideAllMarkers()
        self.powerGauge.ShowMarker(origPower / powerOutput if powerOutput > 0 else 0)
        if cpuDiff >= 0:
            GetByLabel('UI/PI/Common/TeraFlopsAmountIncrease', amount=cpuDiff)
        else:
            GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=cpuDiff)
        if powerDiff >= 0:
            GetByLabel('UI/PI/Common/MegaWattsAmountIncrease', amount=powerDiff)
        else:
            GetByLabel('UI/PI/Common/MegaWattsAmount', amount=powerDiff)
        self.cpuGauge.hint = GetByLabel('UI/PI/Common/TeraFlopsDiff', current=origCpu, after=cpu, maximum=cpuOutput)
        self.powerGauge.hint = GetByLabel('UI/PI/Common/MegaWattsDiff', current=origPower, after=power, maximum=powerOutput)

    def UpdateCostOfCurrentChanges(self):
        cost = sm.GetService('planetUI').GetCurrentPlanet().GetCostOfCurrentEdits()
        self.costText.SetSubtext(FmtISK(cost, showFractionsAlways=0))

    def Submit(self):
        sm.GetService('planetUI').planet.SubmitChanges()
        sm.GetService('audio').SendUIEvent('msg_pi_build_submit_play')

    def Cancel(self):
        sm.GetService('planetUI').RevertChanges()
        sm.GetService('audio').SendUIEvent('msg_pi_build_cancel_play')

    def OnEditModeChanged(self, isEdit):
        if not isEdit:
            uicore.animations.FadeOut(self.editModeContainer, duration=0.3, sleep=True)
            uicore.animations.MorphScalar(self.editModeContainer, 'height', self.editModeContainer.height, 0, duration=0.3, sleep=True)
            self.editModeContainer.state = uiconst.UI_HIDDEN
            self.inEditMode = False
        else:
            self.UpdatePowerAndCPUGauges()
            self.UpdateCostOfCurrentChanges()
            self.editModeContainer.state = uiconst.UI_NORMAL
            uicore.animations.MorphScalar(self.editModeContainer, 'height', 0, EDITMODECONTAINER_HEIGHT, duration=0.3, sleep=True)
            uicore.animations.FadeTo(self.editModeContainer, 0.0, 1.0, duration=0.3, sleep=True)
            self.inEditMode = True
        self.editModeTab.UpdateButtons(self.inEditMode)

    def OnEditModeBuiltOrDestroyed(self, planetID):
        planetUI = sm.GetService('planetUI')
        if planetUI.planetID != planetID:
            return
        if not self.inEditMode:
            self.editModeContainer.state = uiconst.UI_NORMAL
            uicore.animations.MorphScalar(self.editModeContainer, 'height', 0, EDITMODECONTAINER_HEIGHT, duration=0.3, sleep=True)
            uicore.animations.FadeTo(self.editModeContainer, 0.0, 1.0, duration=0.3, sleep=True)
            self.inEditMode = True
        self.UpdatePowerAndCPUGauges()
        self.UpdateCostOfCurrentChanges()
        self.editModeTab.UpdateButtons(self.inEditMode)
