#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\simpleTextTooltip.py
from carbonui import uiconst
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper

class SimpleTextTooltip(TooltipBaseWrapper):

    def __init__(self, text, margin = tooltipConst.TOOLTIP_MARGIN, *args, **kwargs):
        super(SimpleTextTooltip, self).__init__(*args, **kwargs)
        self.text = text
        self.margin = margin
        self.tooltipPanel = None
        self.textLabel = None

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = self.margin
        self.textLabel = self.tooltipPanel.AddLabelMedium(text=self.text, wrapWidth=tooltipConst.LABEL_WRAP_WIDTH, state=uiconst.UI_NORMAL)
        return self.tooltipPanel
