#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\client\rewardTooltip.py
import carbonui.const as uiconst
from carbonui import fontconst
from carbonui.util.color import Color
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.shared.cloneGrade.upgradeButton import UpgradeButton
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByLabel
from loginrewards.client.util import open_vgs_to_buy_omega_time
from seasons.client.const import POINTS_ICON_PATH_18, GREEN_TEXT_COLOR
MAX_TOOLTIP_WIDTH = 280
UPGRADE_BUTTON_WIDTH = 110
UPGRADE_BUTTON_HEIGHT = 24
UPGRADE_BUTTON_TEXTURE_NORMAL = 'res:/UI/Texture/Classes/CloneGrade/omegaClaimBG.png'
UPGRADE_BUTTON_TEXTURE_MOUSEOVER = 'res:/UI/Texture/Classes/CloneGrade/claimHilite.png'
UPGRADE_BUTTON_PADDING = 4
LABEL_ITEM_DESCRIPTION = 'UI/Seasons/RewardDescription'
LABEL_CLICK_TO_CLAIM = 'UI/Seasons/ClickToClaim'
LABEL_POINTS_TO_UNLOCK = 'UI/Seasons/PointsToUnlock'
LABEL_OMEGA_ONLY_REWARD = 'UI/Seasons/OmegaOnlyReward'
LABEL_UPGRADE_OPTION = 'UI/CloneState/UpgradeToOmega'
LABEL_UPGRADE_BUTTON = 'UI/CloneState/Upgrade'
POINTS_ICON_SIZE = 22
COLOR_EXTRA_TEXT = Color.GRAY5
COLOR_CLICK_TO_CLAIM = GREEN_TEXT_COLOR
COLOR_OMEGA_TITLE = (0.8, 0.55, 0.22, 1.0)

class RewardTooltip(TooltipBaseWrapper):

    def __init__(self, type_id, amount, points, *args, **kwargs):
        super(RewardTooltip, self).__init__(*args, **kwargs)
        self.description = GetByLabel(LABEL_ITEM_DESCRIPTION, quantity=amount, typeID=type_id)
        self.points = points
        self.is_claimed = True
        self.is_achieved = True
        self.is_available = True

    def update_reward(self, is_claimed, is_achieved, is_available):
        self.is_claimed = is_claimed
        self.is_achieved = is_achieved
        self.is_available = is_available

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        self.tooltipPanel.cellPadding = (0, 3, 0, 3)
        self.add_item_description()
        if not self.is_claimed:
            if self.is_achieved:
                if self.is_available:
                    self.add_click_to_claim()
                else:
                    self.add_omega_upgrade_option()
            elif self.is_available:
                self.add_points()
            else:
                self.add_points()
                self.add_omega_upgrade_option()
        return self.tooltipPanel

    def _add_label(self, text, isBold = False, isSmall = True, color = None, colSpan = 1):
        func = self.tooltipPanel.AddLabelSmall if isSmall else self.tooltipPanel.AddLabelMedium
        func(text=text, align=uiconst.CENTERLEFT, bold=isBold, color=color, wrapWidth=MAX_TOOLTIP_WIDTH, colSpan=colSpan)

    def add_item_description(self):
        self._add_label(text=self.description, isBold=True, colSpan=2)

    def add_click_to_claim(self):
        text = GetByLabel(LABEL_CLICK_TO_CLAIM)
        self._add_label(text=text, isBold=True, isSmall=False, color=COLOR_CLICK_TO_CLAIM, colSpan=2)

    def add_points(self):
        self.tooltipPanel.AddSpriteLabel(texturePath=POINTS_ICON_PATH_18, label=GetByLabel(LABEL_POINTS_TO_UNLOCK, points=self.points), iconSize=POINTS_ICON_SIZE, iconColor=COLOR_EXTRA_TEXT, color=COLOR_EXTRA_TEXT)

    def add_omega_upgrade_option(self):
        self.tooltipPanel.AddDivider()
        disclaimer = GetByLabel(LABEL_OMEGA_ONLY_REWARD)
        self._add_label(text=disclaimer, isSmall=False, colSpan=2)
        action = GetByLabel(LABEL_UPGRADE_OPTION)
        self._add_label(text=action, isBold=True, isSmall=False, color=COLOR_OMEGA_TITLE)
        button_action = GetByLabel(LABEL_UPGRADE_BUTTON)
        UpgradeButton(name='upgradeOptionButton', parent=self.tooltipPanel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, left=4, text=button_action, onClick=open_vgs_to_buy_omega_time, fontSize=fontconst.EVE_SMALL_FONTSIZE, upperCase=False, height=UPGRADE_BUTTON_HEIGHT, stretchTexturePath=UPGRADE_BUTTON_TEXTURE_NORMAL, hiliteTexturePath=UPGRADE_BUTTON_TEXTURE_MOUSEOVER, textureEdgeSize=8)
