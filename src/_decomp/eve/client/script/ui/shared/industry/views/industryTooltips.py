#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\views\industryTooltips.py
from collections import defaultdict
import math
from carbonui import const as uiconst, fontconst, TextColor
from carbonui.primitives.fill import Fill
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from menu import MenuLabel
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.util.color import Color
from dogma.const import attributeManufactureSlotLimit, attributeMaxLaborotorySlots, attributeReactionSlotLimit
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label, EveHeaderMedium, EveHeaderLarge
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.shared.cloneGrade import ORIGIN_INDUSTRY
from eve.client.script.ui.shared.cloneGrade.omegaTooltipPanelCell import OmegaTooltipPanelCell
from eve.client.script.ui.shared.industry import industryUIConst
from eve.client.script.ui.shared.industry.systemCostIndexGauge import SystemCostIndexGauge
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame
from eve.client.script.ui.shared.industry.views.industryCaptionLabel import IndustryCaptionLabel
from eve.client.script.ui.shared.shipTree.infoBubble import SkillEntry
from eve.common.script.util import industryCommon
from eve.common.script.util.eveFormat import FmtISK
import evetypes
import industry
from inventorycommon import const
import localization
from localization import GetByLabel
from localization.formatters import FormatNumeric
from carbonui.primitives.container import Container
from eveservices.menu import GetMenuService
import structures
from eve.client.script.ui import eveColor
MARGIN = (8, 8, 8, 0)
PADBOTTOM = (0, 0, 0, 8)

def AddMaterialGroupRow(materialGroupID, panel):
    cont = ContainerAutoSize(align=uiconst.TOPLEFT)
    icon = Sprite(parent=cont, align=uiconst.TOPLEFT, texturePath=industryUIConst.ICON_BY_INDUSTRYGROUP[materialGroupID], pos=(4, 0, 12, 12), color=industryUIConst.COLOR_FRAME)
    label = IndustryCaptionLabel(parent=cont, align=uiconst.TOPLEFT, text=localization.GetByLabel(industryUIConst.LABEL_BY_INDUSTRYGROUP[materialGroupID]), left=24)
    panel.AddCell(cont, colSpan=3, cellPadding=(0, 0, 0, 5))


def AddItemRow(panel, materialData):
    panel.AddCell(MaterialIconAndLabel(materialData=materialData), cellPadding=(0, 0, 0, 3))
    available = FormatNumeric(materialData.available, useGrouping=True)
    quantity = FormatNumeric(materialData.quantity, useGrouping=True)
    color = industryUIConst.COLOR_NOTREADY if materialData.errors else industryUIConst.COLOR_READY
    colorHex = Color.RGBtoHex(*color)
    label = EveLabelMedium(align=uiconst.CENTERRIGHT, text='<color=%s>%s / %s' % (colorHex, available, quantity))
    panel.AddCell(label, cellPadding=(8, 0, 0, 3))


def AddOutcomeRow(panel, product):
    panel.AddCell(MaterialIconAndLabel(materialData=product), cellPadding=(0, 0, 0, 0))
    label = EveLabelMedium(align=uiconst.CENTERRIGHT, text='x %s' % product.quantity)
    panel.AddCell(label, cellPadding=(8, 0, 0, 0))
    panel.AddSpacer(width=0, height=8, colSpan=2)


def AddPriceRow(panel, price):
    if not price:
        iskPrice = localization.GetByLabel('UI/Inventory/PriceUnavailable')
    else:
        iskPrice = FmtISK(price)
    label = EveLabelMedium(text=localization.GetByLabel('UI/Industry/TotalEstimatedPrice'), color=Color.GRAY)
    panel.AddCell(label)
    label = EveLabelMedium(align=uiconst.TOPRIGHT, text=iskPrice)
    panel.AddCell(label, cellPadding=(8, 0, 0, 0))
    panel.AddCell(cellPadding=PADBOTTOM, colSpan=2)


def AddVolumeRow(panel, value):
    label = EveLabelMedium(text=localization.GetByLabel('UI/Common/Volume'), color=Color.GRAY)
    panel.AddCell(label)
    text = localization.GetByLabel('UI/Inventory/ContainerCapacity', capacity=value)
    label = EveLabelMedium(align=uiconst.TOPRIGHT, text=text)
    panel.AddCell(label, cellPadding=(8, 0, 0, 0))
    panel.AddCell(cellPadding=PADBOTTOM, colSpan=2)


def AddTypeBonusRow(panel, text, bonusME = None, bonusTE = None):
    label = EveLabelMedium(text=text, color=Color.GRAY)
    panel.AddCell(label)
    if bonusME:
        label = EveLabelMedium(align=uiconst.TOPRIGHT, text=bonusME)
        panel.AddCell(label, cellPadding=(8, 0, 0, 0))
    if bonusTE:
        label = EveLabelMedium(align=uiconst.TOPRIGHT, text=bonusTE)
        panel.AddCell(label, cellPadding=(8, 0, 0, 0))
    panel.FillRow()
    panel.AddCell(cellPadding=PADBOTTOM, colSpan=2)


def AddDescriptionRow(panel, text, cellPadding = PADBOTTOM):
    if text:
        description = EveLabelMedium(text=text, color=Color.GRAY, align=uiconst.TOTOP)
        panel.AddCell(description, colSpan=2, cellPadding=cellPadding)


def AddSkillRow(panel, typeID, level = None, cellPadding = PADBOTTOM):
    if level is None:
        showLevel = False
        level = 1
    else:
        showLevel = True
    panel.AddRow(rowClass=SkillEntry, typeID=typeID, level=level, showLevel=showLevel)


def AddErrorRow(panel, error, errorArgs):
    text = industryCommon.GetErrorLabel(error, *errorArgs)
    if not text:
        text = error.name
    description = EveLabelMedium(text=text, align=uiconst.TOPLEFT)
    cell = panel.AddCell(description, colSpan=2, cellPadding=(8, 4, 8, 4))
    frame = ErrorFrame(bgParent=cell)
    frame.Show()


def AddModifierRow(name, value, panel, hint = None):
    state = uiconst.UI_NORMAL if hint else uiconst.UI_DISABLED
    label = panel.AddLabelMedium(text=name, align=uiconst.TOPLEFT, cellPadding=(0, 0, 0, 2), state=state)
    label.hint = hint
    panel.AddLabelMedium(text=value, align=uiconst.TOPRIGHT, cellPadding=(12, 0, 0, 2))


def AddModifierRows(caption, modifiers, panel):
    label = IndustryCaptionLabel(text=caption, width=220)
    panel.AddCell(label, colSpan=panel.columns, cellPadding=(0, 0, 0, 2))
    for modifier in modifiers:
        AddModifierRow(modifier.GetName(), modifier.GetPercentageLabel(), panel)


def AddJobModifierRows(panel, modifierCls, jobData):
    modifiers = jobData.GetModifiers(modifierCls)
    if not modifiers:
        return
    caption = jobData.GetModifierCaption(modifierCls)
    AddModifierRows(caption, modifiers, panel)
    panel.AddSpacer(0, 6, colSpan=2)


def AddSystemCostIndexRow(activityID, facilityData, tooltipPanel, cellPadding = (8, 0, 0, 8)):
    text = '<color=gray>' + localization.GetByLabel('UI/Industry/SystemCostIndex')
    tooltipPanel.AddLabelMedium(text=text, align=uiconst.TOPLEFT, cellPadding=(0, 0, 0, 0))
    height = 13
    gauge = SystemCostIndexGauge(gaugeHeight=height, align=uiconst.TOPRIGHT, pos=(0,
     2,
     50,
     height), facilityData=facilityData, activityID=activityID)
    tooltipPanel.AddCell(gauge, cellPadding=cellPadding)


def AddTaxRateRows(panel, taxRates):
    for serviceID, taxRate in taxRates.iteritems():
        if taxRate is None:
            continue
        text = '<color=gray>%s %s:' % (localization.GetByLabel(structures.GetServiceLabel(serviceID)), localization.GetByLabel('UI/Industry/Tax'))
        panel.AddLabelMedium(text=text, align=uiconst.TOPLEFT, cellPadding=(0, 0, 0, 0))
        color = '<color=red>' if taxRate > 0 else '<color=green>'
        panel.AddLabelSmall(text='%s%.2f%%' % (color, taxRate), align=uiconst.TOPRIGHT, cellPadding=(0, 0, 0, 0))


class MaterialTooltipPanel:

    def __init__(self, jobData, materialData, tooltipPanel):
        self.jobData = jobData
        self.materialData = materialData
        self.tooltipPanel = tooltipPanel
        tooltipPanel.margin = MARGIN
        tooltipPanel.columns = 2
        self.Reconstruct()
        self.jobData.on_updated.connect(self.Reconstruct)

    def Reconstruct(self, *args):
        if self.tooltipPanel.destroyed:
            return
        self.tooltipPanel.Flush()
        AddItemRow(self.tooltipPanel, self.materialData)
        self.tooltipPanel.AddCell(cellPadding=(0, 0, 0, 4), colSpan=2)
        price = self.materialData.GetEstimatedUnitPrice() * self.materialData.quantity
        AddPriceRow(self.tooltipPanel, price)


class OutcomeTooltipPanel:

    def __init__(self, jobData, tooltipPanel):
        self.jobData = jobData
        self.tooltipPanel = tooltipPanel
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.margin = MARGIN
        tooltipPanel.columns = 2
        if self.jobData.IsProductSelectable() and not self.jobData.IsInstalled():
            AddDescriptionRow(self.tooltipPanel, GetByLabel('UI/Industry/SelectOutcome'))
            scroll = Scroll(align=uiconst.TOPLEFT, width=250)
            scroll.OnSelectionChange = self.OnScrollSelectionChange
            scrollList = self.GetScrollContent()
            scroll.Load(contentList=scrollList)
            scroll.ScrollToSelectedNode()
            scroll.height = min(len(scrollList) * 29 + 2, 200)
            scroll.Confirm = self.Confirm
            self.tooltipPanel.AddCell(scroll, colSpan=3, cellPadding=PADBOTTOM)
        else:
            AddOutcomeRow(self.tooltipPanel, self.jobData.product)
            price = self.jobData.product.GetEstimatedUnitPrice() * self.jobData.product.quantity
            AddPriceRow(self.tooltipPanel, price)
            if hasattr(self.jobData.product, 'GetPackagedVolume'):
                volume = self.jobData.product.GetPackagedVolume() * self.jobData.product.quantity
                AddVolumeRow(self.tooltipPanel, volume)

    def GetScrollContent(self):
        entries = []
        for product in self.jobData.products:
            entry = GetFromClass(Item, {'typeID': product.typeID,
             'label': evetypes.GetName(product.typeID),
             'getIcon': True,
             'isCopy': not product.original,
             'hint': evetypes.GetDescription(product.typeID),
             'isSelected': self.jobData.GetProductTypeID() == product.typeID,
             'OnDblClick': self.OnNodeDblClick})
            entries.append(entry)

        entries = sorted(entries, key=lambda x: (x.typeID is not None, x.label))
        return entries

    def Confirm(self, *args):
        self.tooltipPanel.Close()

    def OnNodeDblClick(self, node):
        self.tooltipPanel.Close()

    def OnScrollSelectionChange(self, nodes):
        if not nodes:
            return
        self.jobData.product = nodes[0].typeID


class MaterialGroupTooltipPanel:

    def __init__(self, materialsByGroupID, tooltipPanel, jobData):
        tooltipPanel.margin = MARGIN
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.columns = 2
        self.materialsByGroupID = materialsByGroupID
        self.jobData = jobData
        self.tooltipPanel = tooltipPanel
        self.Reconstruct()
        self.jobData.on_updated.connect(self.Reconstruct)

    def Reconstruct(self, *args):
        if self.tooltipPanel.destroyed:
            return
        self.tooltipPanel.Flush()
        for materialGroupID, materials in self.materialsByGroupID:
            AddMaterialGroupRow(materialGroupID, self.tooltipPanel)
            materials = filter(lambda m: m.typeID is not None, materials)
            if materials:
                materials.sort(key=lambda x: x.GetName())
                for materialData in materials:
                    AddItemRow(self.tooltipPanel, materialData)

                self.tooltipPanel.AddCell(cellPadding=(0, 0, 0, 10), colSpan=2)
            else:
                label = EveLabelMedium(align=uiconst.CENTERLEFT, left=16, text=localization.GetByLabel('UI/Industry/NoItemSelected'))
                self.tooltipPanel.AddCell(label, cellPadding=(8, 0, 0, 10), colSpan=2)

        estPrice, volume = self.GetTotalEstimatedPriceAndVolume()
        AddPriceRow(self.tooltipPanel, estPrice)
        AddVolumeRow(self.tooltipPanel, volume)
        AddJobModifierRows(self.tooltipPanel, industry.MaterialModifier, self.jobData)

    def GetTotalEstimatedPriceAndVolume(self):
        totalPrice = 0.0
        totalVolume = 0.0
        for _, materials in self.materialsByGroupID:
            for material in materials:
                if material.typeID:
                    totalPrice += material.GetEstimatedUnitPrice() * material.quantity
                    totalVolume += material.GetPackagedVolume() * material.quantity

        return (totalPrice, totalVolume)


class MaterialIconAndLabel(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.materialData = attributes.materialData
        if isinstance(self.materialData, industry.Blueprint):
            bpData = self.materialData
        else:
            bpData = None
        icon = ItemIcon(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, pos=(0, 0, 20, 20), typeID=self.materialData.typeID, bpData=bpData, showOmegaOverlay=False)
        label = EveLabelMedium(parent=self, align=uiconst.CENTERLEFT, text=self.materialData.GetName(), left=24)

    def GetMenu(self):
        menu = GetMenuService().GetMenuFromItemIDTypeID(None, self.materialData.typeID, includeMarketDetails=True)
        menu.insert(0, (MenuLabel('UI/Inventory/ItemActions/BuyThisType'), GetMenuService().QuickBuy, (self.materialData.typeID, self.materialData.missing)))
        return menu

    def GetHint(self):
        return evetypes.GetDescription(self.materialData.typeID)


class SkillTooltipPanel:

    def __init__(self, skills, tooltipPanel):
        tooltipPanel.margin = 8
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.columns = 2
        self.tooltipPanel = tooltipPanel
        if not skills:
            description = EveLabelMedium(text=localization.GetByLabel('UI/Industry/NoSkillRequirements'), color=Color.GRAY, align=uiconst.TOPLEFT)
            tooltipPanel.AddCell(description, colSpan=2, cellPadding=(0, 0, 0, 8))
            return
        AddDescriptionRow(tooltipPanel, localization.GetByLabel('UI/Industry/RequiredSkills'), cellPadding=(0, 0, 0, 2))
        for typeID, level in skills:
            AddSkillRow(tooltipPanel, typeID, level, cellPadding=(0, 0, 0, 1))

        if self.IsCloneStateRestricted(skills):
            tooltipPanel.state = uiconst.UI_NORMAL
            tooltipPanel.AddRow(rowClass=OmegaTooltipPanelCell, cellPadding=(0, 6, 0, 6), text=GetByLabel('UI/CloneState/RequiresOmegaClone'), origin=ORIGIN_INDUSTRY)

    def IsCloneStateRestricted(self, skills):
        for typeID, level in skills:
            if sm.GetService('cloneGradeSvc').IsSkillLevelRestricted(typeID, level):
                return True

        return False


class SubmitButtonTooltipPanel:

    def __init__(self, status, errors, tooltipPanel):
        self.tooltipPanel = tooltipPanel
        self.Reconstruct(status, errors)

    def Reconstruct(self, status, errors):
        if self.tooltipPanel.destroyed:
            return
        self.tooltipPanel.margin = MARGIN
        numColumns = 2
        self.tooltipPanel.columns = numColumns
        self.tooltipPanel.Flush()
        if status == industry.STATUS_INSTALLED:
            self.tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/Industry/StopJobHint'), wrapWidth=200, colSpan=numColumns)
            spacerHeight = 8
        else:
            if not errors:
                return
            errors = {error[0].value:error for error in errors}.values()
            self.tooltipPanel.cellSpacing = (0, 4)
            for error, errorArgs in errors:
                AddErrorRow(self.tooltipPanel, error, errorArgs)

            spacerHeight = 4
        self.tooltipPanel.AddSpacer(width=0, height=spacerHeight, colSpan=numColumns)


class JobsSummaryTooltipPanel:

    def __init__(self, jobData, tooltipPanel):
        self.tooltipPanel = tooltipPanel
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.margin = 8
        tooltipPanel.columns = 2
        rangeLabel = industryUIConst.GetControlRangeLabel(jobData.max_distance)
        activityType = industryUIConst.GetActivityType(jobData.activityID)
        usedSlots = sm.GetService('industrySvc').GetJobCountForActivity(jobData.activityID)
        if activityType == industryUIConst.TYPE_MANUFACTURING:
            text = localization.GetByLabel('UI/Industry/JobSummaryManufacturing', used=usedSlots, max=jobData.max_slots)
            tooltipPanel.AddLabelMedium(text=text, width=320, cellPadding=(0, 0, 0, 2), colSpan=2)
            AddSkillRow(tooltipPanel, const.typeMassProduction, cellPadding=(0, 0, 0, 1))
            AddSkillRow(tooltipPanel, const.typeAdvancedMassProduction, cellPadding=(0, 0, 0, 1))
            text = localization.GetByLabel('UI/Industry/ControlRangeManufacturing', range=rangeLabel)
            tooltipPanel.AddLabelMedium(text=text, width=320, cellPadding=(0, 8, 0, 2), colSpan=2)
            AddSkillRow(tooltipPanel, const.typeSupplyChainManagement, cellPadding=(0, 0, 0, 1))
        elif activityType == industryUIConst.TYPE_SCIENCE:
            text = localization.GetByLabel('UI/Industry/JobSummaryScience', used=usedSlots, max=jobData.max_slots)
            tooltipPanel.AddLabelMedium(text=text, width=320, cellPadding=(0, 0, 0, 2), colSpan=2)
            AddSkillRow(tooltipPanel, const.typeLaboratoryOperation, cellPadding=(0, 0, 0, 1))
            AddSkillRow(tooltipPanel, const.typeAdvancedLaboratoryOperation, cellPadding=(0, 0, 0, 1))
            text = localization.GetByLabel('UI/Industry/ControlRangeScience', range=rangeLabel)
            tooltipPanel.AddLabelMedium(text=text, width=320, cellPadding=(0, 8, 0, 2), colSpan=2)
            AddSkillRow(tooltipPanel, const.typeScientificNetworking, cellPadding=(0, 0, 0, 1))
        elif activityType == industryUIConst.TYPE_REACTION:
            text = localization.GetByLabel('UI/Industry/JobSummaryReactions', used=usedSlots, max=jobData.max_slots)
            tooltipPanel.AddLabelMedium(text=text, width=320, cellPadding=(0, 0, 0, 2), colSpan=2)
            AddSkillRow(tooltipPanel, const.typeMassReactions, cellPadding=(0, 0, 0, 1))
            AddSkillRow(tooltipPanel, const.typeAdvancedMassReactions, cellPadding=(0, 0, 0, 1))
            text = localization.GetByLabel('UI/Industry/ControlRangeReactions', range=rangeLabel)
            tooltipPanel.AddLabelMedium(text=text, width=320, cellPadding=(0, 8, 0, 2), colSpan=2)
            AddSkillRow(tooltipPanel, const.typeRemoteReactions, cellPadding=(0, 0, 0, 1))


class AllJobsSummaryTooltipPanel:

    def __init__(self, tooltipPanel):
        self.tooltipPanel = tooltipPanel
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.margin = 8
        tooltipPanel.columns = 2
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        attributeValues = dogmaLocation.GetIndustryCharacterModifiers(session.charid)
        industrySvc = sm.GetService('industrySvc')
        for activityID, slotLimitAttributeID, labelPath, topPad, skills in [(industry.MANUFACTURING,
          attributeManufactureSlotLimit,
          'UI/Industry/JobSummaryManufacturing',
          0,
          (const.typeMassProduction, const.typeAdvancedMassProduction)), (industry.RESEARCH_TIME,
          attributeMaxLaborotorySlots,
          'UI/Industry/JobSummaryScience',
          8,
          (const.typeLaboratoryOperation, const.typeAdvancedLaboratoryOperation)), (industry.REACTION,
          attributeReactionSlotLimit,
          'UI/Industry/JobSummaryReactions',
          8,
          (const.typeMassReactions, const.typeAdvancedMassReactions))]:
            usedSlots = industrySvc.GetJobCountForActivity(activityID)
            maxSlots = int(attributeValues[slotLimitAttributeID])
            text = localization.GetByLabel(labelPath, used=usedSlots, max=maxSlots)
            tooltipPanel.AddLabelMedium(text=text, width=320, cellPadding=(0,
             topPad,
             0,
             2), colSpan=2)
            for eachSkillID in skills:
                AddSkillRow(tooltipPanel, eachSkillID, cellPadding=(0, 0, 0, 1))


class TimeContainerTooltipPanel:

    def __init__(self, jobData, tooltipPanel):
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.margin = (8, 8, 8, 7)
        tooltipPanel.columns = 2
        AddJobModifierRows(tooltipPanel, industry.TimeModifier, jobData)
        for typeID in jobData.GetTimeSkillTypes() or []:
            AddSkillRow(tooltipPanel, typeID, cellPadding=(0, 0, 0, 1))


class CostContainerTooltipPanel:
    LABEL_OFFSET = 4

    def __init__(self, jobData, tooltipPanel):
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.margin = MARGIN
        numColumns = 3
        tooltipPanel.columns = numColumns
        tooltipPanel.cellPadding = (0, 0)
        header, abbrLabel, costPercentage = self.GetHeaderAndAbbreviation(jobData)
        percText = ''
        if costPercentage:
            estValueLabel = GetByLabel('UI/Industry/EstimatedItemValue', numRuns=jobData.runs)
            costWithoutPercentage = FmtISK(jobData.base_cost / costPercentage, 0)
            percText = '%.1f%%' % (costPercentage * 100.0)
            percText = GetByLabel('UI/Industry/PercentageOfEIV', percentage=percText, startColorTag='')
            self.AddAmountRow(tooltipPanel, estValueLabel, costWithoutPercentage, fontColor=TextColor.NORMAL)
            tooltipPanel.AddSpacer(width=0, height=10, colSpan=tooltipPanel.columns)
        baseCostAsText = FmtISK(jobData.base_cost, 0)
        self.AddAmountRow(tooltipPanel, header, baseCostAsText, percText)
        tooltipPanel.AddSpacer(width=0, height=10, colSpan=tooltipPanel.columns)
        self.AddBodyFramedCont(tooltipPanel, GetByLabel('UI/Industry/JobGrossCost'))
        tooltipPanel.AddSpacer(width=0, height=10, colSpan=tooltipPanel.columns)
        systemIndex = jobData.facility.GetCostIndex(jobData.activityID)
        systemIndexAsText = '%.2f%%' % (systemIndex * 100.0)
        if abbrLabel:
            systemIndexAsText = GetByLabel(abbrLabel, percentage=systemIndexAsText, startColorTag='')
        systemIndexCost = systemIndex * jobData.base_cost
        systemIndexCostAsText = FmtISK(systemIndexCost, 0)
        self.AddRow(tooltipPanel, GetByLabel('UI/Industry/SystemCostIndex'), systemIndexAsText, systemIndexCostAsText)
        jobModifiers = 1.0
        mulModifiers = [ x for x in jobData.GetModifiers(industry.CostModifier) if not x.additive ]
        if mulModifiers:
            tooltipPanel.AddSpacer(width=0, height=14, colSpan=tooltipPanel.columns)
            for m in mulModifiers:
                jobModifiers *= m.amount

            bonusValue = systemIndexCost * (jobModifiers - 1.0)
            amountAsText, fontColor = self.GetAmountTextAndColor(bonusValue)
            self.AddAmountRow(tooltipPanel, GetByLabel('UI/Industry/CostBonuses'), amountAsText, fontColor=fontColor)
            for modifier in mulModifiers:
                color = modifier.GetModifierColor()
                self.AddRow(tooltipPanel, modifier.GetName(), modifier.GetPercentageLabel(), '', leftPadding=20, fontColor=color)
                tooltipPanel.AddSpacer(width=0, height=2, colSpan=tooltipPanel.columns)
                tooltipPanel.FillRow()

        tooltipPanel.AddSpacer(width=0, height=14, colSpan=tooltipPanel.columns)
        costWithoutAlphaTax = jobData.GetCostWithoutAlphaTax()
        costWithoutAlphaTaxAsText = FmtISK(costWithoutAlphaTax, 1)
        self.AddAmountRow(tooltipPanel, GetByLabel('UI/Industry/TotalJobGrossCost'), costWithoutAlphaTaxAsText, fontColor=TextColor.HIGHLIGHT)
        facilityTaxAmt = jobData.GetFacilityTax()
        taxRate = jobData.facility.tax
        if taxRate is None and jobData.activity:
            taxRate = jobData.activity.activity_tax(jobData.facility)
        totalTax = facilityTaxAmt or 0
        tooltipPanel.AddSpacer(width=0, height=10, colSpan=tooltipPanel.columns)
        self.AddBodyFramedCont(tooltipPanel, GetByLabel('UI/Industry/Taxes'))
        tooltipPanel.AddSpacer(width=0, height=10, colSpan=tooltipPanel.columns)
        if taxRate:
            taxLabel = '<color=%s>+%s%%</color>' % (Color.RGBtoHex(*eveColor.DANGER_RED), FormatNumeric(taxRate * 100, useGrouping=True, decimalPlaces=2))
            if abbrLabel:
                taxLabel = GetByLabel(abbrLabel, percentage=taxLabel, startColorTag='')
            self.AddIskRow(tooltipPanel, GetByLabel('UI/Industry/FacilityTax'), taxLabel, facilityTaxAmt)
            tooltipPanel.AddSpacer(width=0, height=10, colSpan=tooltipPanel.columns)
        cloneStateModifier = GetCloneStateModifier(jobData)
        if cloneStateModifier:
            alphaTax = jobData.base_cost * (cloneStateModifier.amount - 1.0)
            totalTax += alphaTax
            percText = cloneStateModifier.GetPercentageLabel(decimals=2)
            if abbrLabel:
                percText = GetByLabel(abbrLabel, percentage=percText, startColorTag='')
            self.AddIskRow(tooltipPanel, GetByLabel('UI/Industry/AlphaCloneTax'), percText, alphaTax)
            tooltipPanel.AddSpacer(width=0, height=10, colSpan=tooltipPanel.columns)
        scc_surcharge = jobData.scc_surcharge
        scc_surcharge_ratio = jobData.scc_surcharge_ratio
        if scc_surcharge:
            ratioText = '+%s%%' % FormatNumeric(scc_surcharge_ratio * 100, useGrouping=True, decimalPlaces=2)
            if abbrLabel:
                ratioText = GetByLabel(abbrLabel, percentage=ratioText, startColorTag='')
            totalTax += scc_surcharge
            self.AddIskRow(tooltipPanel, GetByLabel('UI/Industry/SccSurcharge'), ratioText, scc_surcharge)
            tooltipPanel.AddSpacer(width=0, height=10, colSpan=tooltipPanel.columns)
        totalTaxText = FmtISK(totalTax, 0)
        self.AddAmountRow(tooltipPanel, GetByLabel('UI/Industry/TotalTaxes'), totalTaxText, fontColor=TextColor.HIGHLIGHT)
        tooltipPanel.AddSpacer(width=0, height=6, colSpan=tooltipPanel.columns)
        totalCost = jobData.total_cost
        totalCostAsText = FmtISK(totalCost, 0)
        self.AddTotalFramedCont(tooltipPanel, totalCostAsText)

    def GetHeaderAndAbbreviation(self, jobData):
        costPercentage = None
        if jobData.activityID == industry.MANUFACTURING:
            return (GetByLabel('UI/Industry/EstimatedItemValue', numRuns=jobData.runs), 'UI/Industry/PercentageOfEIV', costPercentage)
        if jobData.activityID in (industry.RESEARCH_TIME, industry.RESEARCH_MATERIAL):
            return (GetByLabel('UI/Industry/ProcessTimeValue'), 'UI/Industry/PercentageOfPTV', costPercentage)
        if jobData.activityID in (industry.COPYING, industry.INVENTION):
            costPercentage = industry.COST_PERCENTAGE
            percText = FormatNumeric(industry.COST_PERCENTAGE * 100, useGrouping=True, decimalPlaces=1) + '%'
            return (GetByLabel('UI/Industry/HeaderPercentageOfEIV'), 'UI/Industry/PercentageOfPEIV', costPercentage)
        return (GetByLabel('UI/Industry/BaseItemCost'), '', costPercentage)

    def AddAmountRow(self, tooltipPanel, textLeft, amountAsText, percentage = '', fontColor = TextColor.NORMAL):
        return self.AddRow(tooltipPanel, textLeft, percentage, amountAsText, fontColor=fontColor)

    def AddBodyFramedCont(self, tooltipPanel, textLeft):
        fillColor = eveColor.WHITE[:3] + (0.1,)
        c, maxTextHeight = self._AddFramedCont(tooltipPanel, textLeft, '', bold=False, fillColor=fillColor)
        c.height = maxTextHeight + 10

    def AddTotalFramedCont(self, tooltipPanel, textRight):
        tooltipPanel.AddSpacer(width=0, height=4, colSpan=tooltipPanel.columns)
        c, maxTextHeight = self._AddFramedCont(tooltipPanel, GetByLabel('UI/Industry/JobCost'), textRight, EveHeaderLarge, bold=True, fillColor=eveColor.SMOKE_BLUE)
        c.height = maxTextHeight + 12
        tooltipPanel.AddSpacer(width=0, height=4, colSpan=tooltipPanel.columns)

    def _AddFramedCont(self, tooltipPanel, textLeft, textRight, rightLabelClass = EveLabelMedium, bold = False, fillColor = eveColor.WHITE):
        c = Container(align=uiconst.TOTOP)
        Fill(bgParent=c, color=fillColor)
        leftLabel = EveLabelMedium(parent=c, align=uiconst.CENTERLEFT, left=self.LABEL_OFFSET, text=textLeft)
        c.rightLabel = rightLabelClass(parent=c, align=uiconst.CENTERRIGHT, left=self.LABEL_OFFSET, text=textRight, bold=bold)
        textWidth = leftLabel.textwidth + c.rightLabel.textwidth + 20
        tooltipPanel.AddCell(cellObject=c, colSpan=tooltipPanel.columns)
        tooltipPanel.AddSpacer(width=textWidth, height=0, colSpan=tooltipPanel.columns)
        return (c, max(c.rightLabel.textheight, leftLabel.textheight))

    def AddIskRow(self, tooltipPanel, textLeft, textCenter, amount, fontColor = None):
        amountAsText, fc = self.GetAmountTextAndColor(amount)
        fontColor = fontColor or fc
        return self.AddRow(tooltipPanel, textLeft, textCenter, amountAsText, fontColor=fontColor)

    def GetAmountTextAndColor(self, amount):
        amountAsText = FmtISK(amount, 0)
        if amount > 0:
            amountAsText = '+%s' % amountAsText
            color = eveColor.DANGER_RED
        elif amount == 0:
            color = TextColor.NORMAL
        else:
            color = eveColor.SUCCESS_GREEN
        return (amountAsText, color)

    def AddRow(self, tooltipPanel, textLeft, textCenter, textRight, leftPadding = LABEL_OFFSET, fontColor = TextColor.NORMAL):
        tooltipPanel.AddLabelMedium(text=textLeft, align=uiconst.CENTERLEFT, left=leftPadding, color=fontColor)
        tooltipPanel.AddLabelMedium(text=textCenter, align=uiconst.CENTERRIGHT, cellPadding=(10, 0, 10, 1), color=fontColor)
        rowTotalLabel = tooltipPanel.AddLabelMedium(text=textRight, align=uiconst.CENTERRIGHT, color=fontColor, left=self.LABEL_OFFSET)
        tooltipPanel.FillRow()
        return rowTotalLabel


def GetCloneStateModifier(jobData):
    for modifier in jobData.input_modifiers:
        if modifier.reference == industry.Reference.CLONE_STATE:
            return modifier


class ProbabilityTooltipPanel:

    def __init__(self, jobData, tooltipPanel):
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.margin = MARGIN
        tooltipPanel.columns = 2
        AddJobModifierRows(tooltipPanel, industry.ProbabilityModifier, jobData)
        if jobData.activityID == industry.INVENTION:
            for skill in jobData.activity.skills:
                AddSkillRow(tooltipPanel, skill.typeID, cellPadding=(0, 0, 0, 2))

            tooltipPanel.AddSpacer(width=0, height=6)


class FacilityActivityTooltip:

    def __init__(self, facilityData, activityID, tooltipPanel):
        tooltipPanel.margin = MARGIN
        tooltipPanel.columns = 2
        tooltipPanel.state = uiconst.UI_NORMAL
        text = localization.GetByLabel(industryUIConst.ACTIVITY_NAMES.get(activityID))
        tooltipPanel.AddLabelMedium(text=text, cellPadding=PADBOTTOM, colSpan=2, bold=True)
        if activityID not in facilityData.activities:
            text = localization.GetByLabel('UI/Industry/ActivityNotSupported')
            tooltipPanel.AddLabelMedium(text=text, cellPadding=PADBOTTOM, colSpan=2)
            return
        if activityID in (industry.MANUFACTURING, industry.REACTION):
            activity = facilityData.activities[activityID]
            modifierData = self.GetTypesSupportedWithModifiers(activity, facilityData.modifiers)
            if modifierData:
                label = IndustryCaptionLabel(text=localization.GetByLabel('UI/Industry/ManufacturingTypesHint'))
                tooltipPanel.AddCell(label, colSpan=2)
                self.scroll = ScrollContainer(align=uiconst.TOTOP, showUnderlay=True)
                for text, modifierME, modifierTE in modifierData:
                    Label(parent=self.scroll, align=uiconst.TOTOP, text=text, padding=2)
                    if modifierME:
                        Label(parent=self.scroll, align=uiconst.TOTOP, text='<color=gray>%s:</color> %s (%s)' % (localization.GetByLabel('UI/Industry/MaterialConsumption'), modifierME.GetPercentageLabel(), localization.GetByLabel('UI/Industry/Specialities/Rigs')), fontsize=fontconst.EVE_SMALL_FONTSIZE, padding=(2, 0, 2, 2))
                    if modifierTE:
                        Label(parent=self.scroll, align=uiconst.TOTOP, text='<color=gray>%s</color> %s (%s)' % (localization.GetByLabel('UI/Industry/JobDuration'), modifierTE.GetPercentageLabel(), localization.GetByLabel('UI/Industry/Specialities/Rigs')), fontsize=fontconst.EVE_SMALL_FONTSIZE, padding=(2, -3, 2, 3))

                self.scroll.height = min(150, len(modifierData) * 20)
                tooltipPanel.AddCell(self.scroll, cellPadding=PADBOTTOM, colSpan=2)
        modifiers = facilityData.GetFacilityModifiersByActivityID().get(activityID, None)
        if modifiers:
            for modifierCls, label in ((industry.TimeModifier, 'UI/Industry/ModifierTimeCaption'), (industry.MaterialModifier, 'UI/Industry/ModifierMaterialCaption'), (industry.CostModifier, 'UI/Industry/ModifierCostCaption')):
                clsModifiers = [ modifier for modifier in modifiers if isinstance(modifier, modifierCls) ]
                if clsModifiers:
                    AddModifierRows(localization.GetByLabel(label), clsModifiers, tooltipPanel)
                    tooltipPanel.AddSpacer(0, 6, colSpan=2)

        costIndexes = facilityData.GetCostIndexByActivityID()
        costIndex = costIndexes.get(activityID, None)
        if costIndex:
            AddSystemCostIndexRow(activityID, facilityData, tooltipPanel)
        taxRates = facilityData.GetServiceTaxes()
        for serviceID in structures.INDUSTRY_SERVICES:
            if structures.GetActivityID(serviceID) != activityID:
                taxRates.pop(serviceID, None)

        AddTaxRateRows(tooltipPanel, taxRates)

    def GetMETEModifiers(self, modifiers):
        modifierME = modifierTE = None
        for modifier in modifiers:
            if isinstance(modifier, industry.TimeModifier):
                modifierTE = modifier
            elif isinstance(modifier, industry.MaterialModifier):
                modifierME = modifier

        return (modifierME, modifierTE)

    def GetTypesSupportedWithModifiers(self, activity, modifiers):
        ret = []
        modifiersByCategoryID = self.GetModifiersByCategoryID(modifiers)
        for categoryID in activity['categories']:
            if categoryID == const.categoryBlueprint:
                continue
            text = evetypes.GetCategoryNameByCategory(categoryID)
            modifierME, modifierTE = self.GetMETEModifiers(modifiersByCategoryID.get(categoryID, []))
            ret.append((text, modifierME, modifierTE))

        modifiersByGroupID = self.GetModifiersByGroupID(modifiers)
        for groupID in activity['groups']:
            text = evetypes.GetGroupNameByGroup(groupID)
            modifierME, modifierTE = self.GetMETEModifiers(modifiersByGroupID.get(groupID, []))
            if (modifierTE, modifierME) == (None, None):
                categoryID = evetypes.GetCategoryIDByGroup(groupID)
                if categoryID in modifiersByCategoryID:
                    modifierME, modifierTE = self.GetMETEModifiers(modifiersByCategoryID.get(categoryID, []))
            ret.append((text, modifierME, modifierTE))

        ret.sort()
        return ret

    def GetModifiersByCategoryID(self, modifiers):
        ret = defaultdict(list)
        for modifier in modifiers:
            if getattr(modifier, 'categoryID', None):
                ret[modifier.categoryID].append(modifier)

        return ret

    def GetModifiersByGroupID(self, modifiers):
        ret = defaultdict(list)
        for modifier in modifiers:
            if getattr(modifier, 'groupID', None):
                ret[modifier.groupID].append(modifier)

        return ret
