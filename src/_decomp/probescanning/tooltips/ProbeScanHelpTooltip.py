#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\probescanning\tooltips\ProbeScanHelpTooltip.py
from carbon.common.script.util.linkUtil import GetShowInfoLink
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.client.script.ui.control import tooltips
import carbonui.const as uiconst
import localization
from probescanning.const import probeLauncherTypeID, combatScannerProbeTypeID, coreScannerProbeTypeID, expandedProbeLauncherTypeID

class ProbeScanHelpTooltip(TooltipBaseWrapper):

    def __init__(self):
        super(ProbeScanHelpTooltip, self).__init__()

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        text = localization.GetByLabel('UI/Inflight/Scanner/ProbeScanHelp', core_probe_link=GetShowInfoLink(coreScannerProbeTypeID, localization.GetByLabel('UI/Inflight/Scanner/CoreProbes')), combat_probes_link=GetShowInfoLink(combatScannerProbeTypeID, localization.GetByLabel('UI/Inflight/Scanner/CombatProbes')), core_probe_launcher_link=GetShowInfoLink(probeLauncherTypeID, localization.GetByLabel('UI/Inflight/Scanner/ProbeLauncher')), expanded_launcher_link=GetShowInfoLink(expandedProbeLauncherTypeID, localization.GetByLabel('UI/Inflight/Scanner/ExpandedLauncher')))
        self.tooltipPanel.AddLabelMedium(text=text, state=uiconst.UI_NORMAL, wrapWidth=300)
        return self.tooltipPanel
