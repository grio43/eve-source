#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\incursions\incursionMechanicsTooltip.py
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByLabel
from talecommon.const import VANGUARD_PENALTY, ASSAULT_PENALTY, HEADQUARTERS_PENALTY
WRAP_WIDTH = 250

class IncursionMechanicsTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/IncursionMechanics', establishedColor=Color.RGBtoHex(*Color.GREEN), mobilizedColor=Color.RGBtoHex(*Color.ORANGE), withdrawingColor=Color.RGBtoHex(*Color.RED)), wrapWidth=WRAP_WIDTH, colSpan=2)
        self.ConstructIconLabel(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/CynoJamPenalty', highlightColor=Color.RGBtoHex(*Color.WHITE)), texturePath='res:/UI/Texture/classes/InfluenceBar/effectCyno.png')
        self.ConstructIconLabel(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/BountyPenalty', highlightColor=Color.RGBtoHex(*Color.WHITE)), texturePath='res:/UI/Texture/classes/InfluenceBar/effectTax.png')
        self.ConstructIconLabel(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/ResistancePenalty', highlightColor=Color.RGBtoHex(*Color.WHITE)), texturePath='res:/UI/Texture/classes/InfluenceBar/effectResistanceDecrease.png')
        self.tooltipPanel.AddSpacer(height=10, colSpan=2)
        self.tooltipPanel.AddLabelValue(label=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/SiteType'), value=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/ResistancesPenalty'), opacity=0.75)
        self.tooltipPanel.AddDivider()
        self.ConstructPenaltyTable()
        self.ConstructIconLabel(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/DamageReduction', highlightColor=Color.RGBtoHex(*Color.WHITE)), texturePath='res:/UI/Texture/classes/InfluenceBar/effectDamageDecrease.png')
        self.tooltipPanel.AddSpacer(height=10, colSpan=2)
        self.tooltipPanel.AddLabelValue(label=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/SiteType'), value=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/DamagePenalty'), opacity=0.75)
        self.tooltipPanel.AddDivider()
        self.ConstructPenaltyTable()
        self.tooltipPanel.AddSpacer(height=10, colSpan=2)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/MothershipDescription'), wrapWidth=WRAP_WIDTH, colSpan=2)
        return self.tooltipPanel

    def ConstructPenaltyTable(self):
        self.tooltipPanel.AddLabelValue(label=GetByLabel('UI/Incursion/Distributions/SanshaIncursion/Vanguard'), value='%s%%' % VANGUARD_PENALTY, wrapWidth=125, valueColor=Color.WHITE)
        self.tooltipPanel.AddLabelValue(label=GetByLabel('UI/Incursion/Distributions/SanshaIncursion/Assault'), value='%s%%' % ASSAULT_PENALTY, wrapWidth=125, valueColor=Color.WHITE)
        self.tooltipPanel.AddLabelValue(label=GetByLabel('UI/Incursion/Distributions/SanshaIncursion/Headquarters'), value='%s%%' % HEADQUARTERS_PENALTY, wrapWidth=125, valueColor=Color.WHITE)

    def ConstructIconLabel(self, text, texturePath):
        iconLabelContainer = ContainerAutoSize(align=uiconst.CENTERLEFT, top=4)
        Sprite(parent=iconLabelContainer, align=uiconst.CENTERLEFT, width=22, height=22, texturePath=texturePath)
        Label(parent=iconLabelContainer, text=text, align=uiconst.CENTERLEFT, color=Color.GRAY, left=30, maxWidth=230)
        self.tooltipPanel.AddCell(iconLabelContainer, colSpan=2)
