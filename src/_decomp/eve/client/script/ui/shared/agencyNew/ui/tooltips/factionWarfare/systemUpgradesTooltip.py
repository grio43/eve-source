#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\factionWarfare\systemUpgradesTooltip.py
from carbonui import uiconst
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByLabel

class SystemUpgradesTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        labelPath = 'UI/Agency/Tooltips/Encounters/FactionWarfare/SystemUpgradesDescription2'
        self.tooltipPanel.AddLabelMedium(text=GetByLabel(labelPath), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH)
        self.tooltipPanel.AddSpacer(0, 5)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/SystemUpgradeBonuses'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH)
        self.tooltipPanel.AddSpacer(0, 10)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/AvailableUpgrades'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH)
        return self.tooltipPanel
