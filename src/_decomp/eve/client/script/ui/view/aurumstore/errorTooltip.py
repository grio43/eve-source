#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\errorTooltip.py
import carbonui.const as uiconst
from eve.client.script.ui.control import tooltips
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
ERROR_COLOR = (1.0, 0.0, 0.0, 0.4)

class ErrorTooltip(TooltipBaseWrapper):

    def __init__(self, errorTitle = '', errorMessage = '', *args, **kwargs):
        super(ErrorTooltip, self).__init__(errorTitle, errorMessage, *args, **kwargs)
        self.errorTitle = errorTitle
        self.errorMessage = errorMessage
        self.tooltipPanel = None

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx, bgColor=ERROR_COLOR)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        if self.errorTitle:
            self.tooltipPanel.AddLabelMedium(text=self.errorTitle)
        if self.errorMessage:
            self.tooltipPanel.AddLabelMedium(text=self.errorMessage)
        return self.tooltipPanel

    def Close(self):
        if self.tooltipPanel:
            self.tooltipPanel.Close()
            self.tooltipPanel = None
