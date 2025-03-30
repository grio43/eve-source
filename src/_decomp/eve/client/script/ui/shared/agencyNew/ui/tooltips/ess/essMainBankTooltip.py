#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\ess\essMainBankTooltip.py
from carbonui import uiconst
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByLabel

class EssMainBankTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        autoPayInterval = sm.RemoteSvc('dynamicResourceCacheMgr').GetDynamicResourceSettings()['autopaymentIntervalSeconds'] * const.SEC
        bufferTime = sm.RemoteSvc('dynamicResourceCacheMgr').GetDynamicResourceSettings()['bufferTimeSeconds'] * const.SEC
        payPercentile = sm.RemoteSvc('dynamicResourceCacheMgr').GetDynamicResourceSettings()['mainBankPayRatio'] * 100
        inversePayPercentile = 100 - payPercentile
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Exploration/ESS/ESSMainBankTooltip', autoPayInterval=autoPayInterval, bufferTime=bufferTime, payPercentile=payPercentile, inversePayPercentile=inversePayPercentile), wrapWidth=250)
        return self.tooltipPanel
