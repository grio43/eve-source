#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pirateinsurgency\client\dashboard\sidepanels\systeminfo.py
import carbonui
import eveformat
from carbonui import uiconst, TextColor
from carbonui.decorative.divider_line import DividerLine
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from characterdata.factions import get_faction_name
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.services.insurgenceDashboardSvc import WrapCallbackWithErrorHandling
from evelink.client import location_link
from localization import GetByLabel
from pirateinsurgency.client.dashboard.const import WARZONE_ID_TO_PIRATE_FACTION_ID, GetSuppressionIconForStage, GetCorruptionIconForStage
from pirateinsurgency.client.dashboard.widgets.gauge import SuppressionGauge, CorruptionGauge
from pirateinsurgency.client.utils import CalculateCurrentStageFromFraction

class SystemInfo(Container):
    default_clipChildren = True
    __notifyevents__ = ['OnCorruptionValueChanged_Local', 'OnSuppressionValueChanged_Local']

    def ApplyAttributes(self, attributes):
        super(SystemInfo, self).ApplyAttributes(attributes)
        self.dashboardSvc = attributes.get('dashboardSvc')
        sm.RegisterNotify(self)
        self.corruptionStages = None
        self.suppressionStages = None

    def OnSystemSelected(self, systemID):
        self.Flush()
        self.systemID = systemID
        self.loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER)
        self.ConstructLayout(systemID)
        self.loadingWheel.Hide()

    def ConstructLayout(self, systemID):
        cont = Container(parent=self, align=uiconst.TOALL, padding=(16, 0, 16, 0))
        secStatusText = eveformat.client.solar_system_security_status(systemID)
        systemLinkText = u'{} {}'.format(cfg.evelocations.Get(systemID).name, secStatusText)
        systemLink = location_link(systemID, systemLinkText)
        EveCaptionLarge(parent=cont, color=TextColor.HIGHLIGHT, align=uiconst.TOTOP, text=systemLink, state=uiconst.UI_NORMAL)
        if self.dashboardSvc.IsFOBSystem(systemID):
            warzoneID = self.dashboardSvc.GetSystemWarzoneID(systemID)
            pirateFaction = WARZONE_ID_TO_PIRATE_FACTION_ID[warzoneID]
            factionName = get_faction_name(pirateFaction)
            carbonui.TextBody(parent=cont, align=uiconst.TOTOP, text=GetByLabel('UI/PirateInsurgencies/FOBSystem', factionName=factionName), bold=True)
        carbonui.TextBody(parent=cont, align=uiconst.TOTOP, text=self.dashboardSvc.GetNumJumpsString(systemID))
        insurgencyLineText = GetByLabel('UI/PirateInsurgencies/systemNotAffectedByInsurgency')
        if self.dashboardSvc.IsSystemAffectedByInsurgency(systemID):
            insurgencyLineText = GetByLabel('UI/PirateInsurgencies/systemAffectedByInsurgency')
        carbonui.TextBody(parent=cont, align=uiconst.TOTOP, text=insurgencyLineText)
        DividerLine(parent=cont, padTop=16, align=uiconst.TOTOP)
        widgetsCont = ContainerAutoSize(parent=cont, align=uiconst.TOTOP, padding=(0, 16, 0, 16))
        self.corruptionWidgetCont = Container(parent=widgetsCont, align=uiconst.TOTOP, height=68)
        self.suppressionWidgetCont = Container(parent=widgetsCont, align=uiconst.TOTOP, height=68, padTop=16)
        suppressionLoadingWheel = LoadingWheel(parent=self.suppressionWidgetCont, align=uiconst.CENTER, state=uiconst.UI_NORMAL)
        corruptionLoadingWheel = LoadingWheel(parent=self.corruptionWidgetCont, align=uiconst.CENTER, state=uiconst.UI_NORMAL)
        self.dashboardSvc.RequestSuppressionStages(WrapCallbackWithErrorHandling(self.SuppressionStagesCallback, parentContainer=self.suppressionWidgetCont, onErrorCallback=suppressionLoadingWheel.Hide))
        self.dashboardSvc.RequestCorruptionStages(WrapCallbackWithErrorHandling(self.CorruptionStagesCallback, parentContainer=self.corruptionWidgetCont, onErrorCallback=corruptionLoadingWheel.Hide))

    def SuppressionStagesCallback(self, stages):
        self.suppressionWidgetCont.Flush()
        self.suppressionStages = stages
        self.suppressionGauge = SuppressionGauge(parent=self.suppressionWidgetCont, align=uiconst.TOLEFT, dashboardSvc=self.dashboardSvc, width=64, height=64, stages=stages, systemID=self.systemID)
        suppressionTextCont = Container(parent=self.suppressionWidgetCont, align=uiconst.TOALL, padLeft=16, padTop=7)
        carbonui.TextBody(parent=suppressionTextCont, align=uiconst.TOTOP, text=GetByLabel('UI/PirateInsurgencies/suppression'))
        self.suppressionStageLabal = carbonui.TextBody(parent=suppressionTextCont, align=uiconst.TOTOP, text=GetByLabel('UI/PirateInsurgencies/stageLabel', stage='-'), bold=True)
        self.suppressionPercentageLabel = carbonui.TextBody(parent=suppressionTextCont, align=uiconst.TOTOP, text='-', color=TextColor.SECONDARY, state=uiconst.UI_NORMAL)
        self.dashboardSvc.RequestSystemSuppression(self.systemID, WrapCallbackWithErrorHandling(self.SetSuppressionTextCallback, parentContainer=None))

    def CorruptionStagesCallback(self, stages):
        self.corruptionWidgetCont.Flush()
        self.corruptionStages = stages
        self.corruptionGauge = CorruptionGauge(parent=self.corruptionWidgetCont, align=uiconst.TOLEFT, dashboardSvc=self.dashboardSvc, width=64, height=64, stages=stages, systemID=self.systemID)
        corruptionTextCont = Container(parent=self.corruptionWidgetCont, align=uiconst.TOALL, padLeft=16, padTop=7)
        carbonui.TextBody(parent=corruptionTextCont, align=uiconst.TOTOP, text=GetByLabel('UI/PirateInsurgencies/corruption'))
        self.corruptionStageLabal = carbonui.TextBody(parent=corruptionTextCont, align=uiconst.TOTOP, text=GetByLabel('UI/PirateInsurgencies/stageLabel', stage='-'), bold=True)
        self.corruptionPercentageLabel = carbonui.TextBody(name='corruptionPercentageLabel', parent=corruptionTextCont, align=uiconst.TOTOP, text='-', color=TextColor.SECONDARY, state=uiconst.UI_NORMAL)
        self.dashboardSvc.RequestSystemCorruption(self.systemID, WrapCallbackWithErrorHandling(self.SetCorruptionTextCallback, parentContainer=None))

    def SetSuppressionTextCallback(self, data):
        return self.SetSuppressionText(data)

    def OnSuppressionValueChanged_Local(self, systemID, data):
        if systemID != self.systemID:
            return
        self.SetSuppressionText(data)

    def SetSuppressionText(self, data):
        currentSuppression = data.numerator
        maxSuppression = data.denominator
        stage = data.stage
        stageText = GetByLabel('UI/PirateInsurgencies/stageLabel', stage=stage)
        percentageText = '{:.1%}'.format(float(currentSuppression) / float(maxSuppression))
        vanguardContribution = 0
        if data.vanguardNumerator and data.vanguardDenominator:
            vanguardContribution = float(data.vanguardNumerator) / float(data.vanguardDenominator) * 100
        if vanguardContribution > 0.0:
            vanguardContributionText = eveformat.hint(hint=GetByLabel('UI/PirateInsurgencies/vanguardSuppressionContributionInfoHint'), text=GetByLabel('UI/PirateInsurgencies/vanguardContribution', contribution=vanguardContribution))
            self.suppressionPercentageLabel.SetText(u'{} - {}'.format(percentageText, vanguardContributionText))
        else:
            self.suppressionPercentageLabel.SetText(percentageText)
        self.suppressionStageLabal.SetText(stageText)
        self.suppressionGauge.SetIcon(GetSuppressionIconForStage(stage))

    def SetCorruptionTextCallback(self, data):
        return self.SetCorruptionText(data)

    def SetCorruptionText(self, data):
        if self.corruptionStages is None:
            return
        if self.corruptionPercentageLabel is None or self.corruptionStageLabal is None:
            return
        currentcorruption = data.numerator
        maxcorruption = data.denominator
        stage = data.stage
        stageText = GetByLabel('UI/PirateInsurgencies/stageLabel', stage=stage)
        percentageText = '{:.1%}'.format(float(currentcorruption) / float(maxcorruption))
        vanguardContribution = 0
        if data.vanguardNumerator and data.vanguardDenominator:
            vanguardContribution = float(data.vanguardNumerator) / float(data.vanguardDenominator) * 100
        if vanguardContribution > 0.0:
            vanguardContributionText = eveformat.hint(hint=GetByLabel('UI/PirateInsurgencies/vanguardCorruptionContributionInfoHint'), text=GetByLabel('UI/PirateInsurgencies/vanguardContribution', contribution=vanguardContribution))
            self.corruptionPercentageLabel.SetText(u'{} - {}'.format(percentageText, vanguardContributionText))
        else:
            self.corruptionPercentageLabel.SetText(percentageText)
        self.corruptionStageLabal.SetText(stageText)
        self.corruptionGauge.SetIcon(GetCorruptionIconForStage(stage))

    def OnCorruptionValueChanged_Local(self, systemID, data):
        if systemID != self.systemID:
            return
        self.SetCorruptionText(data)
