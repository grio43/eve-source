#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\probescanning\tooltips\scanProbeTooltip.py
import carbonui.const as uiconst
import evetypes
import localization
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbon.common.script.util.timerstuff import AutoTimer
from eve.client.script.ui.control import tooltips
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from probescanning.const import probeLauncherTypeID, combatScannerProbeTypeID, coreScannerProbeTypeID

def GetNoProbesTooltipText():
    return localization.GetByLabel('UI/Inflight/Scanner/NoProbesTooltip', core_probe_link=GetShowInfoLink(coreScannerProbeTypeID, localization.GetByLabel('UI/Inflight/Scanner/CoreProbes')), combat_probe_link=GetShowInfoLink(combatScannerProbeTypeID, localization.GetByLabel('UI/Inflight/Scanner/CombatProbes')), probe_launcher_link=GetShowInfoLink(probeLauncherTypeID, localization.GetByLabel('UI/Inflight/Scanner/ProbeLauncher')))


class ScanProbeTooltip(TooltipBaseWrapper):

    def __init__(self, probeTypeID, timeLeftFunc):
        super(ScanProbeTooltip, self).__init__()
        self.probeTypeID = probeTypeID
        self.timeLeftFunc = timeLeftFunc

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        if not self.probeTypeID:
            text = GetNoProbesTooltipText()
            self.tooltipPanel.AddLabelMedium(text=text, state=uiconst.UI_NORMAL, wrapWidth=200)
        else:
            self.CreateNameAndTimeLeftLabel()
            self.timer = AutoTimer(interval=1000, method=self.CreateNameAndTimeLeftLabel)
        return self.tooltipPanel

    def CreateNameAndTimeLeftLabel(self):
        self.tooltipPanel.Flush()
        time_left = self.timeLeftFunc()
        if time_left is None:
            time_left = localization.GetByLabel('UI/Inflight/Scanner/NoProbesLaunched')
        elif time_left > 0:
            time_left = localization.GetByLabel('UI/Inflight/Scanner/ProbeTimeLeft', timeLeft=time_left)
        else:
            time_left = localization.GetByLabel('UI/Inflight/Scanner/Expired')
        self.tooltipPanel.AddLabelMedium(text='%s: %s' % (evetypes.GetName(self.probeTypeID), time_left))
