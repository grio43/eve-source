#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\abyssalDeadspaceRewardsTooltip.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.util.color import Color
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.common.lib import appConst
from localization import GetByLabel

class AbyssalDeadspaceRewardsTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/AbyssalDeadspace/RewardsFromDifficulty'), wrapWidth=250)
        self.tooltipPanel.AddSpacer(height=5)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/AbyssalDeadspace/TriglavianBlueprintReward'), wrapWidth=250, color=Color.WHITE)
        button = Button(name='openFwButton', align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/WindowIcons/ISIS.png', label=GetByLabel('UI/Agency/SeeTriglavianShipTree'), func=lambda x: sm.GetService('shipTreeUI').Open(appConst.factionTriglavian))
        self.tooltipPanel.AddCell(button, cellPadding=(0, 10, 0, 10))
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/AbyssalDeadspace/MutaplasmidRewards', color=Color.RGBtoHex(*Color.WHITE)), wrapWidth=250)
        return self.tooltipPanel
