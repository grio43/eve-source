#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\loginrewards\client\tooltips.py
from carbonui import uiconst, fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from clonegrade import COLOR_OMEGA_ORANGE
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelMediumBold
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.shared.cloneGrade.upgradeButton import UpgradeButton
import evetypes
from localization import GetByLabel
from loginrewards.client.util import open_vgs_to_buy_omega_time
TOOLTIP_LABEL_WIDTH = 280
ICON_SIZE = 64
UPGRADE_BUTTON_WIDTH = 110
UPGRADE_BUTTON_HEIGHT = 24
STRETCH_TEXTURE = 'res:/UI/Texture/Classes/CloneGrade/omegaClaimBG.png'
TOOLTIP_ICON_PATH = 'res:/UI/Texture/classes/LoginCampaign/dailyLogin_icon.png'

class OmegaIconToolTip(TooltipBaseWrapper):

    def __init__(self, upgradeFunc = None):
        super(OmegaIconToolTip, self).__init__()
        self.upgradeFunc = upgradeFunc or open_vgs_to_buy_omega_time

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.isOmega = getattr(self, 'isOmega', False)
        if self.isOmega:
            self.tooltipPanel.LoadGeneric1ColumnTemplate()
            header = GetByLabel('UI/LoginRewards/Tooltips/OmegaTooltipHeader')
            self.tooltipPanel.AddLabelMedium(text=header, state=uiconst.UI_NORMAL, wrapWidth=TOOLTIP_LABEL_WIDTH)
            self.tooltipPanel.FillRow()
            self.tooltipPanel.AddDivider(color=(0.0, 0.0, 0.0, 0.0))
            upsellCont = UpgradeButton(align=uiconst.CENTER, state=uiconst.UI_NORMAL, text=GetByLabel('UI/CloneState/AddOmegaTime'), onClick=self.upgradeFunc, onMouseEnterCallback=None, onMouseExitCallback=None, fontsize=fontconst.EVE_SMALL_FONTSIZE, upperCase=False, width=UPGRADE_BUTTON_WIDTH, height=UPGRADE_BUTTON_HEIGHT, stretchTexturePath=STRETCH_TEXTURE, hiliteTexturePath='res:/UI/Texture/Classes/CloneGrade/claimHilite.png', textureEdgeSize=8)
            self.tooltipPanel.AddCell(upsellCont, cellPadding=(0, 0, 0, 0))
        else:
            self.tooltipPanel.LoadGeneric2ColumnTemplate()
            header = GetByLabel('UI/CloneState/UpgradeToOmega')
            description = GetByLabel('UI/CloneState/BenefitSummary')
            self.tooltipPanel.AddLabelMedium(text=header, state=uiconst.UI_NORMAL, wrapWidth=TOOLTIP_LABEL_WIDTH, bold=True)
            self.tooltipPanel.AddDivider(color=(0.0, 0.0, 0.0, 0.0))
            self.tooltipPanel.AddLabelMedium(text=description, state=uiconst.UI_NORMAL, wrapWidth=200, color=Color.GRAY5)
            self.tooltipPanel.FillRow()
            self.tooltipPanel.AddDivider(color=(0.0, 0.0, 0.0, 0.0))
            self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/LoginRewards/RetroClaimSell'), state=uiconst.UI_NORMAL, wrapWidth=200, color=Color.GRAY5)
            self.tooltipPanel.AddDivider(color=(0.0, 0.0, 0.0, 0.0))
            upsellCont = Container(align=uiconst.CENTER, width=220, height=30)
            UpgradeButton(parent=upsellCont, align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL, text=GetByLabel('UI/CloneState/Upgrade'), onClick=self.upgradeFunc, onMouseEnterCallback=None, onMouseExitCallback=None, fontsize=fontconst.EVE_SMALL_FONTSIZE, upperCase=False, width=UPGRADE_BUTTON_WIDTH, height=UPGRADE_BUTTON_HEIGHT, stretchTexturePath=STRETCH_TEXTURE, hiliteTexturePath='res:/UI/Texture/Classes/CloneGrade/claimHilite.png', textureEdgeSize=8)
            EveLabelMediumBold(parent=upsellCont, text=GetByLabel('UI/CloneState/UpgradeToOmega'), align=uiconst.CENTERLEFT, color=COLOR_OMEGA_ORANGE)
            self.tooltipPanel.AddCell(upsellCont, cellPadding=(0, 0, 0, 0))
        return self.tooltipPanel


class TooltipButtonTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        header = owner.GetTooltipHeader()
        description = owner.GetTooltipDesc()
        texturePath = owner.GetTooltipTexturePath()
        if texturePath:
            iconSprite = Sprite(texturePath=texturePath, width=ICON_SIZE, height=ICON_SIZE, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, padRight=5)
            self.tooltipPanel.AddCell(iconSprite)
        textContainer = ContainerAutoSize(align=uiconst.CENTER, state=uiconst.UI_NORMAL, width=TOOLTIP_LABEL_WIDTH)
        EveLabelMediumBold(text=header, width=TOOLTIP_LABEL_WIDTH, parent=textContainer, align=uiconst.TOTOP, padBottom=5)
        EveLabelMedium(text=description, width=TOOLTIP_LABEL_WIDTH, parent=textContainer, align=uiconst.TOTOP, color=Color.GRAY5)
        self.tooltipPanel.AddCell(textContainer)
        return self.tooltipPanel


class RewardTooltip(TooltipBaseWrapper):

    def __init__(self, typeID):
        self.typeID = typeID
        super(RewardTooltip, self).__init__()

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        textContainer = ContainerAutoSize(align=uiconst.CENTER, state=uiconst.UI_NORMAL, width=TOOLTIP_LABEL_WIDTH)
        EveLabelMediumBold(text=evetypes.GetName(self.typeID), width=TOOLTIP_LABEL_WIDTH, parent=textContainer, align=uiconst.TOTOP, padBottom=5)
        EveLabelMedium(text=evetypes.GetDescription(self.typeID), width=TOOLTIP_LABEL_WIDTH, parent=textContainer, align=uiconst.TOTOP, color=Color.GRAY5)
        self.tooltipPanel.AddCell(textContainer)
        return self.tooltipPanel
