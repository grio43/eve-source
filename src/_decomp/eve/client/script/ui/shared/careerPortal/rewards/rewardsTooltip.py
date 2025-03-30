#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\rewards\rewardsTooltip.py
import evetypes
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from inventorycommon.typeHelpers import GetIconFile

class RewardBundleTooltip(TooltipBaseWrapper):

    def __init__(self, rewards, *args, **kwargs):
        super(RewardBundleTooltip, self).__init__(*args, **kwargs)
        self.rewards = rewards

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric3ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        for reward in self.rewards:
            icon = GetIconFile(reward.type_id)
            label = evetypes.GetName(reward.type_id)
            value = reward.quantity
            iconObj, labelObj, valueObj = self.tooltipPanel.AddIconLabelValue(icon, label, value)
            valueObj.text = FmtAmt(value)
            sm.GetService('photo').GetIconByType(iconObj, reward.type_id)

        return self.tooltipPanel
