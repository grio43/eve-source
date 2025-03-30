#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\tooltip\item.py
import carbonui.uiconst as uiconst
import eveformat
import expertSystems.client
import inventorycommon.const as invconst
import localization
import menucheckers
from carbonui.primitives.container import Container
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.cloneGrade import ORIGIN_INVENTORY
from eve.client.script.ui.shared.tooltip.blueprints import AddBlueprintInfo
from eve.client.script.ui.shared.tooltip.dynamicItem import AddDynamicItemAttributes
from eve.client.script.ui.shared.tooltip.itemBtns import ActivateSkinButton, ActivateAndApplySkinButton, ConsumeSkinDesignComponentButton
from eve.client.script.ui.shared.tooltip.itemObject import ItemObject
from eve.client.script.ui.shared.tooltip.skill_requirement import AddSkillActionAndRequirementsForType
from eve.client.script.ui.util import uix
from eve.common.script.util.eveFormat import FmtISKAndRound, GetAveragePrice
from solarsysteminterference.util import SystemCanHaveInterference
from spacecomponents.common.componentConst import LINK_WITH_SHIP
from spacecomponents.common.data import get_space_component_for_type

class InventoryItemTooltip(object):

    def __init__(self, tooltipPanel, item):
        self.panel = tooltipPanel
        self.item = item
        self.Layout()

    def Layout(self):
        self.panel.Flush()
        self.panel.LoadGeneric2ColumnTemplate()
        self.AddName()
        estimatedPriceText = self.GetEstimatedPriceText()
        if estimatedPriceText:
            self.panel.AddLabelMedium(text=estimatedPriceText, colSpan=2, opacity=0.5)
        self.panel.AddLabelMedium(text=eveformat.volume_from_item(self.item, include_per_unit=True), colSpan=2, opacity=0.5)
        AddDynamicItemAttributes(self.panel, self.item.itemID, self.item.typeID)
        AddBlueprintInfo(self.panel, self.item.itemID, self.item.typeID)
        AddCharacterEnergyInfo(self.panel, self.item.typeID)
        AddSkillRequirementsAndActions(self.panel, self.item.typeID, self.item, origin=ORIGIN_INVENTORY)

    def AddName(self):
        self.panel.AddCell(eveLabel.EveLabelMediumBold(text=self.GetNameAndQuantityText()), colSpan=2)

    def GetNameAndQuantityText(self):
        name = uix.GetItemName(self.item)
        quantity = self.item.stacksize
        if menucheckers.ItemChecker(self.item).IsCrate():
            if quantity > 1:
                return localization.GetByLabel('UI/Inventory/OpenCrateMultiple', quantity=quantity, crateName=name)
            return localization.GetByLabel('UI/Inventory/OpenCrate', crateName=name)
        if quantity > 1:
            return localization.GetByLabel('UI/Inventory/QuantityAndName', quantity=quantity, name=name)
        return name

    def GetEstimatedPriceText(self):
        price = GetAveragePrice(self.item)
        if price is None:
            return
        else:
            priceStr = FmtISKAndRound(price * self.item.stacksize, showFractionsAlways=False)
            if self.item.stacksize > 1:
                showFraction = price < 100
                return localization.GetByLabel('UI/Inventory/ItemStackEstimatedPrice', estPrice=priceStr, estPricePerUnit=FmtISKAndRound(price, showFractionsAlways=showFraction))
            return localization.GetByLabel('UI/Inventory/ItemEstimatedPrice', estPrice=priceStr)


def AddSkillRequirementsAndActions(panel, typeID, item = None, origin = None):
    grid = LayoutGrid(state=uiconst.UI_NORMAL, columns=2)
    AddExpertSystemInfo(grid, typeID)
    AddSkillActionAndRequirementsForType(grid, typeID, item, origin)
    AddSkinAction(grid, typeID, item)
    AddSkinDesignComponentAction(grid, typeID, item)
    if len(grid.children) > 0:
        panel.state = uiconst.UI_NORMAL
        grid.AddCell(Container(align=uiconst.TOPLEFT, width=250), colSpan=grid.columns)
        panel.AddCell(grid, colSpan=panel.columns)


def AddCharacterEnergyInfo(panel, typeID):
    if typeID not in [invconst.typeConcordRogueAnalysisBeacon]:
        return
    if not SystemCanHaveInterference(session.solarsystemid2):
        return
    energyState = sm.GetService('characterEnergySvc').GetEnergyStateNow()
    interferenceState = sm.GetService('solarsystemInterferenceSvc').GetLocalInterferenceStateNow()
    normalisedEnergyLevel = energyState.normalisedEnergyLevel
    label = EveLabelMedium(text=localization.GetByLabel('UI/CharacterEnergy/AvailableEnergy'))
    gauge = Gauge(value=normalisedEnergyLevel, color=Color.HextoRGBA('#40BBEC'), align=uiconst.CENTERRIGHT)
    attributes = get_space_component_for_type(typeID, LINK_WITH_SHIP)
    if attributes.characterEnergyCost is not None:
        maxActivations = int(round(energyState.quiescentEnergyLevel / attributes.characterEnergyCost))
        for i in range(maxActivations):
            gauge.ShowMarker(float(i) / maxActivations, color=Color.BLACK, width=3)

    interferenceCost = attributes.solarsystemInterferenceCost
    warningLabel = EveLabelMedium(text=localization.GetByLabel('UI/CharacterEnergy/WarnInterferenceWillIncrease'), align=uiconst.CENTER)
    warningLabel.maxWidth = 190
    interferenceLabel = EveLabelMedium()
    interferenceLabel.maxWidth = 160
    tooMuchInterference = False
    if interferenceCost is not None and not interferenceState.CanAffordCost(interferenceCost):
        interferenceLabel.SetText(localization.GetByLabel('UI/CharacterEnergy/TooMuchInterference'))
        tooMuchInterference = True
    activatableLabel = EveLabelMedium()
    activatableLabel.maxWidth = 160
    enoughEnergyIcon = Sprite(name='enoughEnergy', width=36, height=36)
    tooMuchInterferenceIcon = Sprite(name='warningIcon', texturePath='res:/UI/Texture/classes/crab/warningIcon.png', width=36, height=36)
    if attributes.characterEnergyCost is not None and not energyState.CanAffordCost(attributes.characterEnergyCost):
        activatableLabel.SetText(localization.GetByLabel('UI/CharacterEnergy/YouDoNotHaveEnergy'))
        enoughEnergyIcon.SetTexturePath('res:/UI/Texture/classes/crab/warningIcon.png')
    else:
        activatableLabel.SetText(localization.GetByLabel('UI/CharacterEnergy/YouHaveEnergy'))
        enoughEnergyIcon.SetTexturePath('res:/UI/Texture/classes/SkillPlan/completedIcon.png')
    interferenceStateGrid = LayoutGrid(state=uiconst.UI_NORMAL, columns=2)
    interferenceStateGrid.AddCell(tooMuchInterferenceIcon, rowSpan=2)
    interferenceStateGrid.AddCell(interferenceLabel, colSpan=2, cellPadding=(0, 0, 0, 5))
    energyStateGrid = LayoutGrid(state=uiconst.UI_NORMAL, columns=2)
    energyStateGrid.AddCell(enoughEnergyIcon, rowSpan=2)
    energyStateGrid.AddCell(activatableLabel, colSpan=1, cellPadding=(0, 0, 0, 5))
    infoGrid = LayoutGrid(state=uiconst.UI_NORMAL, columns=1)
    infoGrid.AddCell(warningLabel)
    grid = LayoutGrid(state=uiconst.UI_NORMAL, columns=2)
    grid.AddCell(label, colSpan=1)
    grid.AddCell(gauge, colSpan=1, cellPadding=(5, 2, 0, 0))
    if tooMuchInterference:
        panel.AddCell(interferenceStateGrid, colSpan=panel.columns, cellPadding=(0, 5, 0, 0))
    panel.AddCell(energyStateGrid, colSpan=panel.columns, cellPadding=(0, 5, 0, 0))
    panel.AddCell(infoGrid, colSpan=panel.columns, cellPadding=(0, 5, 0, 0))
    panel.AddCell(grid, colSpan=panel.columns, cellPadding=(0, 5, 0, 0))


def AddExpertSystemInfo(panel, typeID):
    expertSystems.add_type_unlocked_by_expert_systems(panel, typeID, padding=(0, 12, 0, 0))


def AddSkinAction(grid, typeID, item):
    itemObject = ItemObject(typeID, item)
    if itemObject.CanActivateSkinLicense():
        AddSkinRow(grid, item, itemObject)
        return


def AddSkinDesignComponentAction(grid, typeID, item):
    itemObject = ItemObject(typeID, item)
    if itemObject.CanConsumeSkinDesignComponent():
        AddConsumeSkinDesignComponentRow(grid, item)
        return


def AddSkinRow(grid, item, itemObject):
    grid.AddCell(cellPadding=(0, 12, 0, 0), colSpan=grid.columns)
    btn = ActivateSkinButton(align=uiconst.CENTER, fixedheight=30, item=item)
    other_btn = ActivateAndApplySkinButton(align=uiconst.CENTER, fixedheight=30, item=item, can_apply=itemObject.CanApplySkin())
    grid.AddCell(btn, colSpan=grid.columns)
    grid.AddCell(cellPadding=(0, 12, 0, 0), colSpan=grid.columns)
    grid.AddCell(other_btn, colSpan=grid.columns)


def AddConsumeSkinDesignComponentRow(grid, item):
    grid.AddCell(cellPadding=(0, 12, 0, 0), colSpan=grid.columns)
    btn = ConsumeSkinDesignComponentButton(align=uiconst.CENTER, fixedheight=30, fixedwidth=120, item=item)
    grid.AddCell(btn, colSpan=grid.columns)
