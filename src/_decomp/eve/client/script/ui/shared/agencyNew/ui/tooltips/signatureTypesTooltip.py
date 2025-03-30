#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\signatureTypesTooltip.py
from carbonui import uiconst
from carbonui.util.color import Color
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByLabel

class SignatureTypesTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Exploration/CosmicSignatures/CombatSites'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH, color=Color.WHITE)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Exploration/CosmicSignatures/CombatSitesDescription'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH, state=uiconst.UI_NORMAL)
        self.tooltipPanel.AddSpacer(height=10)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Exploration/CosmicSignatures/DataSites'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH, color=Color.WHITE)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Exploration/CosmicSignatures/DataSitesDescription'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH, state=uiconst.UI_NORMAL)
        self.tooltipPanel.AddSpacer(height=10)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Exploration/CosmicSignatures/GasSites'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH, color=Color.WHITE)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Exploration/CosmicSignatures/GasSitesDescription'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH, state=uiconst.UI_NORMAL)
        self.tooltipPanel.AddSpacer(height=10)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Exploration/CosmicSignatures/GhostSites'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH, color=Color.WHITE)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Exploration/CosmicSignatures/GhostSitesDescription'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH, state=uiconst.UI_NORMAL)
        self.tooltipPanel.AddSpacer(height=10)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Exploration/CosmicSignatures/RelicSites'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH, color=Color.WHITE)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Exploration/CosmicSignatures/RelicSitesDescription'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH, state=uiconst.UI_NORMAL)
        self.tooltipPanel.AddSpacer(height=10)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Exploration/CosmicSignatures/SleeperSites'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH, color=Color.WHITE)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Exploration/CosmicSignatures/SleeperSitesDescription'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH, state=uiconst.UI_NORMAL)
        self.tooltipPanel.AddSpacer(height=10)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Chat/ChannelNames/Wormholes'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH, color=Color.WHITE)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Exploration/CosmicSignatures/WormholesDescription'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH)
        return self.tooltipPanel
