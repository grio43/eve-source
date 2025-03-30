#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\ess\essBountiesOutputTooltip.py
from carbonui import uiconst
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByLabel

class EssBountiesOutputTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        timeInMinutes = sm.RemoteSvc('dynamicResourceCacheMgr').GetDynamicResourceSettings()['timeIntervalSeconds'] * const.SEC
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Exploration/ESS/BountiesOutputTooltip', bountiesOutputTimeInterval=timeInMinutes), wrapWidth=250)
        return self.tooltipPanel
