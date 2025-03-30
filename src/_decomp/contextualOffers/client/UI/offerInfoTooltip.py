#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contextualOffers\client\UI\offerInfoTooltip.py
from carbonui import uiconst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.client.script.ui.control import tooltips

class OfferInfoTooltip(TooltipBaseWrapper):

    def __init__(self, header, description, wrapWidth):
        super(OfferInfoTooltip, self).__init__()
        self.header = header
        self.description = description
        self.wrapWidth = wrapWidth

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.state = uiconst.UI_NORMAL
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.AddLabelLarge(text=self.header, bold=True, wrapWidth=self.wrapWidth, align=uiconst.CENTERTOP, padTop=4, padBottom=10)
        self.tooltipPanel.AddLabelMedium(text=self.description, padBottom=15)
        return self.tooltipPanel
