#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\rewardTooltip.py
import evetypes
from carbonui.util.bunch import Bunch
from carbonui.util.color import Color
from eve.client.script.ui.shared.tooltip.blueprints import AddBlueprintInfo
from eve.common.script.util import industryCommon
from inventorycommon.const import categoryBlueprint
from localization import GetByLabel
from loginrewards.common.rewardUtils import GetTierColor, GetTierName, ShouldShowQty

def LoadTooltipPanelForReward(tooltipPanel, rewardInfo):
    tooltipPanel.LoadGeneric1ColumnTemplate()
    tooltipLabelWidth = 280
    rewardName = rewardInfo.GetRewardName()
    if ShouldShowQty(rewardInfo):
        typeNameText = '<b>%s</b>' % GetByLabel('UI/LoginRewards/NumType', qty=rewardInfo.qty, typeName=rewardName)
    else:
        typeNameText = '<b>%s</b>' % rewardName
    tooltipPanel.AddLabelMedium(text=typeNameText, wrapWidth=tooltipLabelWidth)
    tier = rewardInfo.tier
    if tier:
        color = GetTierColor(tier) or (1, 1, 1, 1)
        tierHintPath = GetTierName(tier)
        if tierHintPath:
            hexColor = Color.RGBtoHex(*color)
            tierHintText = '<color=%s><b>%s</b></color>' % (hexColor, GetByLabel(tierHintPath))
            tooltipPanel.AddLabelMedium(text=tierHintText, wrapWidth=tooltipLabelWidth)
    if evetypes.GetCategoryID(rewardInfo.typeID) == categoryBlueprint:
        if rewardInfo.blueprintProductivityLevel or rewardInfo.blueprintMaterialLevel:
            bpData = industryCommon.BlueprintInstance(Bunch(typeID=rewardInfo.typeID, timeEfficiency=rewardInfo.blueprintProductivityLevel or 0, materialEfficiency=rewardInfo.blueprintMaterialLevel or 0, runs=rewardInfo.qty, quantity=-2))
            AddBlueprintInfo(tooltipPanel, bpData=bpData)
        else:
            text = GetByLabel('UI/Industry/CopyRunsRemaining', runsRemaining=rewardInfo.qty)
            tooltipPanel.AddLabelMedium(text=text, wrapWidth=tooltipLabelWidth)
    if rewardInfo.messageID:
        tooltipPanel.AddSpacer(height=10)
        tooltipPanel.AddLabelMedium(text=GetByLabel(rewardInfo.messageID), wrapWidth=tooltipLabelWidth)
