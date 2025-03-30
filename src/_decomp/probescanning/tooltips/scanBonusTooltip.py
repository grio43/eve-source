#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\probescanning\tooltips\scanBonusTooltip.py
import carbonui.const as uiconst
import localization
from carbon.common.script.util.format import FmtAmt
from carbonui import TextColor
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control import tooltips, eveLabel
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
TOOLTIP_WIDTH = 75
BONUS_COLOR = (0.0, 0.5, 0.0, 1)

class ScanBonusTooltip(TooltipBaseWrapper):

    def __init__(self, name, iconPath, totalValueFunc, baseValueFunc, skillBonusFunc, implantBonusFunc, moduleBonusFunc, shipBonusFunc, totalBonusFunc):
        super(ScanBonusTooltip, self).__init__(self)
        self.name = name
        self.iconPath = iconPath
        self.totalValueFunc = totalValueFunc
        self.baseValueFunc = baseValueFunc
        self.skillBonusFunc = skillBonusFunc
        self.implantBonusFunc = implantBonusFunc
        self.moduleBonusFunc = moduleBonusFunc
        self.shipBonusFunc = shipBonusFunc
        self.totalBonusFunc = totalBonusFunc

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        self.CreateNameLabel()
        self.tooltipPanel.AddSpacer(1, 8, 2)
        self.CreateExplanation()
        self.tooltipPanel.AddSpacer(1, 8, 2)
        self.CreateBaseValueLabel()
        self.tooltipPanel.AddSpacer(1, 8, 2)
        self.CreateSkillsBonusLabel()
        self.CreateModulesBonusLabel()
        self.CreateImplantBonusLabel()
        if self.name.lower() in ('strength', 'deviation'):
            self.CreateShipBonusLabel()
        self.tooltipPanel.AddSpacer(1, 8, 2)
        self.CreateTotalBonusLabel()
        self.tooltipPanel.AddSpacer(1, 2, 2)
        self.CreateTotalValueLabel()
        return self.tooltipPanel

    def CreateNameLabel(self):
        nameIconContainer = ContainerAutoSize(align=uiconst.CENTERLEFT)
        Sprite(parent=nameIconContainer, align=uiconst.CENTERLEFT, width=14, height=14, texturePath=self.iconPath)
        eveLabel.EveLabelLarge(parent=nameIconContainer, text=localization.GetByLabel('UI/Inflight/Scanner/Scan%s' % self.name), align=uiconst.CENTERLEFT, left=19)
        self.tooltipPanel.AddCell(nameIconContainer, colSpan=2)

    def CreateExplanation(self):
        self.tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/Inflight/Scanner/Scan%sHelp' % self.name), colSpan=2, wrapWidth=175, color=TextColor.SECONDARY, align=uiconst.CENTER)

    def CreateBaseValueLabel(self):
        baseValue = self.baseValueFunc()
        if self.name.lower() == 'deviation':
            baseValue = str(baseValue) + ' AU'
        elif self.name.lower() == 'duration':
            baseValue /= 1000
            baseValue = str(baseValue) + 's'
        self.tooltipPanel.AddLabelValue(label=localization.GetByLabel('UI/Inflight/Scanner/BaseValue'), value=baseValue)

    def CreateSkillsBonusLabel(self):
        value = self.skillBonusFunc()
        color = self.GetColor(value)
        if value > 0:
            value = '+%s' % FmtAmt(value, showFraction=2)
        self.tooltipPanel.AddLabelValue(label=localization.GetByLabel('UI/Inflight/Scanner/SkillsBonus'), value='%s%%' % value, valueColor=color)

    def CreateModulesBonusLabel(self):
        value = self.moduleBonusFunc()
        color = self.GetColor(value)
        if value > 0:
            value = '+%s' % FmtAmt(value, showFraction=2)
        self.tooltipPanel.AddLabelValue(label=localization.GetByLabel('UI/Inflight/Scanner/ModulesBonus'), value='%s%%' % value, valueColor=color)

    def CreateImplantBonusLabel(self):
        value = self.implantBonusFunc()
        color = self.GetColor(value)
        if value > 0:
            value = '+%s' % FmtAmt(value, showFraction=2)
        self.tooltipPanel.AddLabelValue(label=localization.GetByLabel('UI/Inflight/Scanner/ImplantBonus'), value='%s%%' % value, valueColor=color)

    def CreateShipBonusLabel(self):
        value = self.shipBonusFunc()
        color = self.GetColor(value)
        if value > 0:
            value = '+%s' % FmtAmt(value, showFraction=2)
        self.tooltipPanel.AddLabelValue(label=localization.GetByLabel('UI/Inflight/Scanner/ShipBonus'), value='%s%%' % value, valueColor=color)

    def CreateTotalBonusLabel(self):
        value = self.totalBonusFunc()
        color = self.GetColor(value)
        if value > 0:
            value = '+%s' % FmtAmt(value, showFraction=2)
        self.tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/Inflight/Scanner/TotalBonus'), align=uiconst.CENTERLEFT, bold=True, cellPadding=(0, 0, 7, 0))
        self.tooltipPanel.AddLabelMedium(text='%s%%' % value, align=uiconst.CENTERRIGHT, color=color, cellPadding=(7, 0, 0, 0), bold=True)

    def CreateTotalValueLabel(self):
        totalValue = FmtAmt(self.totalValueFunc(), showFraction=self.GetFractions())
        self.tooltipPanel.AddLabelValue(label=localization.GetByLabel('UI/Inflight/Scanner/TotalValue'), value=self.AddSuffix(totalValue))

    def AddSuffix(self, totalValue):
        if self.name.lower() == 'deviation':
            totalValue = str(totalValue) + ' AU'
        elif self.name.lower() == 'duration':
            totalValue = str(totalValue) + 's'
        return totalValue

    def GetFractions(self):
        fractions = 0
        if self.name.lower() == 'strength':
            fractions += 1
        elif self.name.lower() == 'deviation':
            fractions += 3
        return fractions

    def GetColor(self, value):
        if value == 0:
            color = tooltips.COLOR_NUMBERVALUE
        else:
            color = BONUS_COLOR
        return color
