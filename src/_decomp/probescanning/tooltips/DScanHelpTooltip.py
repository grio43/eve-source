#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\probescanning\tooltips\DScanHelpTooltip.py
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.client.script.ui.control import tooltips
import localization

class DScanHelpTooltip(TooltipBaseWrapper):

    def __init__(self):
        super(DScanHelpTooltip, self).__init__()

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/Inflight/Scanner/DirectionalScanHelp'), wrapWidth=300)
        return self.tooltipPanel
