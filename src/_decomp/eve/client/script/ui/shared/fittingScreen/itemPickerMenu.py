#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\itemPickerMenu.py
import carbonui.const as uiconst
from collections import defaultdict
import evetypes
import uthread2
import dynamicitemattributes
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.util.sortUtil import SortListOfTuples
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.mouse_inside_scroll_entry import MouseInsideScrollEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.labelEditable import LabelEditable
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from eve.client.script.ui.shared.fittingScreen.skillRequirements import GetMissingSkills_HighestLevelByTypeID
from eve.client.script.ui.util.uix import QtyPopup, GetTechLevelIcon
from localization import GetByLabel
import inventorycommon.const as invConst
from shipfitting.fittingWarningConst import WARNING_LEVEL_SKILL
from shipfitting.fittingWarnings import GetColorForLevel
from signals.signalUtil import ChangeSignalConnect
from utillib import KeyVal
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
from eve.common.lib import appConst as const

class ItemPickerBase(MouseInsideScrollEntry):
    isDragObject = True
    ENTRYHEIGHT = 32
    ICONWIDTH = ENTRYHEIGHT - 4
    NUM_CONT_WIDTH = 80
    REMOVE_PADDING = 36
    haveSkillsLabelPath = 'UI/Fitting/FittingWindow/HaveSkillsForItem'
    dontHaveSkillsLabelPath = 'UI/Fitting/FittingWindow/MissingSkillsForItem'

    def ApplyAttributes(self, attributes):
        MouseInsideScrollEntry.ApplyAttributes(self, attributes)
        self.fittingWarning = None
        node = attributes.node
        self.sr.node = node
        self.updateNumThread = None
        self.InitializeFuncs(node)
        leftContWidth = self.NUM_CONT_WIDTH + self.ENTRYHEIGHT
        leftCont = Container(name='leftCont', parent=self, align=uiconst.TOLEFT, width=leftContWidth)
        self.numItemsCont = Container(name='numItemsCont', parent=leftCont, align=uiconst.TOLEFT, width=self.NUM_CONT_WIDTH, state=uiconst.UI_NORMAL)
        self.restCont = Container(name='restCont', parent=self, align=uiconst.TOALL, left=10, width=self.REMOVE_PADDING)
        self.iconCont = Container(name='iconCont', parent=leftCont, align=uiconst.TORIGHT, width=self.ENTRYHEIGHT)
        self.typeIcon = Icon(parent=self.iconCont, pos=(0,
         0,
         self.ICONWIDTH,
         self.ICONWIDTH), align=uiconst.CENTERRIGHT, idx=0, state=uiconst.UI_DISABLED)
        self.techIcon = Sprite(name='techIcon', parent=self.iconCont, left=1, width=16, height=16, idx=0)
        self.label = EveLabelMedium(text='', parent=self.restCont, left=0, top=0, state=uiconst.UI_DISABLED, color=None, maxLines=1, align=uiconst.CENTER)
        self.AddRemoveBtn()
        self.numItems = LabelEditable(name='numDrones_LabelEditable', parent=self.numItemsCont, align=uiconst.CENTERRIGHT, pos=(0, 1, 0, 0), text='10', hint=GetByLabel('UI/Fitting/FittingWindow/ClickToEdit'), configName='numDrones', maxLength=6, minLength=1, minValue=0, maxValue=1000000, defaultText='0', fontsize=18, onEditFieldChanged=self.OnEditFieldChanged, textEditFieldSwitchCallback=self.OnTextEditFieldChanges)
        self.numItemsCont.OnClick = self.numItems.OnLabelClicked
        self.numItemsCont.GetMenu = self.GetMenu
        self.numItemsCont.isDragObject = True
        self.numItemsCont.GetDragData = self.GetDragData
        self.numItemsCont.hint = GetByLabel('UI/Fitting/FittingWindow/ClickToEdit')
        self.xLabel = EveLabelLarge(text='x', parent=self.numItemsCont, left=self.numItems.left + 9, top=1, state=uiconst.UI_DISABLED, color=None, maxLines=1, align=uiconst.CENTERRIGHT)

    def ConstructFittingWarning(self):
        if self.fittingWarning and not self.fittingWarning.destroyed:
            return
        self.fittingWarning = Sprite(parent=self.iconCont, name='fittingWarning', state=uiconst.UI_DISABLED, align=uiconst.BOTTOMLEFT, pos=(4, 4, 16, 16), texturePath='res:/UI/Texture/classes/Fitting/slotWarningIcon.png', idx=0)

    def Load(self, node):
        self.typeID = node.typeID
        self.label.text = node.label
        self.typeIcon.SetSize(self.ENTRYHEIGHT - 4, self.ENTRYHEIGHT - 4)
        self.typeIcon.LoadIconByTypeID(typeID=self.typeID, size=self.ICONWIDTH, ignoreSize=True, isCopy=getattr(node, 'isCopy', False))
        techSprite = GetTechLevelIcon(self.techIcon, 1, self.typeID)
        techSprite.left = 4
        self.numItems.SetValue(node.qty)
        self.SetEditFieldRange()

    def InitializeFuncs(self, node):
        self.addToActiveFunc = node.addToActive
        self.removeFromActiveFunc = node.removeFromActive
        self.changeActive = node.changeActive
        self.changeNumFunc = node.changeNum

    def OnTextEditFieldChanges(self, *args):
        if self.numItems.editField.display:
            self.xLabel.display = False
        else:
            self.xLabel.display = True

    def OnEditFieldChanged(self, *args):
        LabelEditable.OnEditFieldChanged(self.numItems, *args)
        if not self.updateNumThread:
            self.updateNumThread = uthread2.call_after_wallclocktime_delay(self.UpdateNumbers_thread, 0.25)

    def UpdateNumbers_thread(self):
        self.updateNumThread = None
        numWanted = self.numItems.GetValue()
        if self.changeNumFunc:
            self.changeNumFunc(self.sr.node.typeID, numWanted)

    def SetEditFieldRange(self):
        node = self.sr.node
        self.numItems.editField.SetMinValue(node.intRange[0])
        self.numItems.editField.SetMaxValue(node.intRange[1])

    def AddRemoveBtn(self):
        self.removeBtn = ButtonIcon(texturePath='res:/UI/Texture/Icons/73_16_210.png', pos=(2, 0, 16, 16), align=uiconst.CENTERRIGHT, parent=self, hint=GetByLabel('UI/Generic/RemoveItem'), idx=0, func=self.RemoveItem)
        self.haveSkillIcon = Sprite(name='haveIcon', parent=self, pos=(20, 0, 16, 16), align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL)
        self.haveSkillIcon.display = False

    def RemoveItem(self):
        node = self.sr.node
        if node.Get('removeFunc', None):
            node.removeFunc(node)

    def GetDragData(self):
        typeID = self.sr.node.typeID
        keyVal = KeyVal(__guid__='listentry.GenericMarketItem', typeID=typeID, label=evetypes.GetName(typeID), flagID=self.sr.node.flagID)
        return [keyVal]

    def GetHeight(self, *args):
        node, width = args
        node.height = ItemPickerBase.ENTRYHEIGHT
        return node.height

    @classmethod
    def GetEntryWidth(cls, node):
        label = node['label']
        textwidth, _ = EveLabelMedium.MeasureTextSize(label, maxLines=1)
        w = cls.NUM_CONT_WIDTH + cls.ENTRYHEIGHT + textwidth + cls.REMOVE_PADDING + 40
        return w

    def GetMenu(self):
        if self.sr.node.itemIDs:
            itemID = list(self.sr.node.itemIDs)[0]
        else:
            itemID = None
        return GetMenuService().GetMenuFromItemIDTypeID(itemID, self.sr.node.typeID, includeMarketDetails=True)

    def SetFittingWarningColor(self, color):
        if color is None:
            if self.fittingWarning:
                self.fittingWarning.display = False
        else:
            self.ConstructFittingWarning()
            self.fittingWarning.display = True
            self.fittingWarning.SetRGBA(*color)


class ItemPickerMenu(object):
    entryClass = ItemPickerBase
    emptyLabelPath = 'UI/Fitting/FittingWindow/NoCargoItemsSimulated'

    def __init__(self, controller, menuParent):
        self.scrollWidth = 100
        self.fittingDogmaLocation = sm.GetService('clientDogmaIM').GetFittingDogmaLocation()
        self.ghostFittingSvc = sm.GetService('ghostFittingSvc')
        self.scroll = Scroll(parent=menuParent, align=uiconst.TOTOP, height=100, padding=4)
        self.btnCont = ContainerAutoSize(parent=menuParent, align=uiconst.TOTOP, padTop=4, padBottom=4)
        removeBtn = Button(parent=self.btnCont, label=GetByLabel('UI/Fitting/FittingWindow/RemoveAll'), func=self.RemoveAll, align=uiconst.CENTER)
        self.scroll.GetEntryWidth = self.GetEntryWidth

    def LoadItemScroll(self):
        self.scroll.Clear()
        sortedItemInfo = self.GetSortedItemsInfo()
        activeItemsSet = set(self.GetActiveItems())
        extraData = self.GetExtraData()
        extraDataFunc = self.GetExtraDataFuncs()
        maxWidth = 100
        scrollList = []
        for itemInfo in sortedItemInfo:
            hasSkills = sm.GetService('skills').IsSkillRequirementMet(itemInfo.typeID)
            qty = itemInfo.qty
            maxExtraQty = GetMaxQty(self.fittingDogmaLocation, self.flagID, {itemInfo.typeID: 1}) or 0
            intRange = (0, qty + maxExtraQty)
            label = itemInfo.typeName
            data = {'label': label,
             'itemIDs': itemInfo.itemIDs,
             'intRange': intRange,
             'typeID': itemInfo.typeID,
             'isDynamic': itemInfo.isDynamic,
             'getIcon': True,
             'OnClick': self.OnItemClicked,
             'removeFunc': self.RemoveItemClicked,
             'hasSkills': hasSkills,
             'qty': qty,
             'flagID': self.flagID}
            data.update(extraData)
            data.update(extraDataFunc)
            extraDataForType = self.GetExtraDataForType(itemInfo.itemIDs, activeItemsSet, itemInfo.typeID)
            data.update(extraDataForType)
            width = self.entryClass.GetEntryWidth(data)
            maxWidth = max(maxWidth, width)
            entry = GetFromClass(self.entryClass, data)
            scrollList.append(entry)

        if scrollList:
            entry = self.GetHeaderEntry(activeItemsSet)
            if entry:
                scrollList.insert(0, entry)
            self.scrollWidth = maxWidth
            self.btnCont.display = True
        else:
            scrollList = self.GetNoItemEntryAndSetWidth()
            if not self.DoShowBtnWhenScollIsEmpty():
                self.btnCont.display = False
        self.scroll.AddNodes(0, scrollList)
        self.UpdateScrollSize()

    def RefrehsScroll(self):
        self.scroll.RefreshNodes()

    def DoShowBtnWhenScollIsEmpty(self):
        return False

    def UpdateNodes(self):
        pass

    def IsItemChecked(self, itemID, activeItemsCopy):
        return True

    def GetActiveItems(self):
        return {}

    def GetItems(self):
        return {}

    def GetTotalCanActivate(self, numActive):
        return 0

    def OnItemClicked(self, *args):
        pass

    def UpdateScrollSize(self):
        contentHeight = self.scroll.GetContentHeight() + 2
        self.scroll.height = min(contentHeight, 400)

    def GetEntryWidth(self, *args):
        return self.scrollWidth

    def RemoveItemClicked(self, node):
        self.RemoveItem(node)
        self.scroll.RemoveNodes([node])
        if not self.scroll.GetNodes():
            scrollList = self.GetNoItemEntryAndSetWidth()
            if not self.DoShowBtnWhenScollIsEmpty():
                self.btnCont.display = False
            self.scroll.AddNodes(0, scrollList)
        self.UpdateScrollSize()

    def RemoveItem(self, node):
        itemIDs = node.itemIDs
        if not itemIDs:
            return
        itemID = list(itemIDs)[0]
        self.ghostFittingSvc.UnfitModule(itemID)

    def GetNoItemEntryAndSetWidth(self):
        data = {'label': GetByLabel(self.emptyLabelPath)}
        data.update(self.GetNoItemDropFunc())
        scrollList = [GetFromClass(NoItemEntry, data)]
        width = NoItemEntry.GetEntryWidth(NoItemEntry, data)
        self.scrollWidth = width
        return scrollList

    def GetNoItemDropFunc(self):
        return {}

    def GetSortedItemsInfo(self):
        itemsToSort = self.GetItems()
        unsortedEntries = {}
        dynamicItemSvc = sm.GetService('dynamicItemSvc')
        for eachItem in itemsToSort.itervalues():
            identifier = None
            if dynamicItemSvc.IsDynamicItem(eachItem.typeID):
                identifier = eachItem.itemID
            itemKey = (eachItem.typeID, identifier)
            itemEntryData = unsortedEntries.get(itemKey)
            if not itemEntryData:
                itemEntryData = ItemPickerItemEntryData(typeID=eachItem.typeID, typeName=evetypes.GetName(eachItem.typeID), isDynamic=identifier is not None, itemIDs=set(), qty=0)
                unsortedEntries[itemKey] = itemEntryData
            itemEntryData.itemIDs.add(eachItem.itemID)
            itemEntryData.qty += getattr(eachItem.invItem, 'quantity', None) or getattr(eachItem, 'stacksize', 1)

        return sorted(unsortedEntries.values(), key=lambda data: data.typeName)

    def RemoveAll(self, *args):
        for eachNode in self.scroll.GetNodes():
            self.RemoveItem(eachNode)

        self.ghostFittingSvc.SendOnStatsUpdatedEvent()
        self.LoadItemScroll()

    def GetExtraData(self):
        return {}

    def GetExtraDataFuncs(self):
        return {}

    def GetExtraDataForType(self, itemIDs, itemIdSet, typeID):
        return {}

    def GetHeaderEntry(self, extraInfo):
        return None

    def GetAllTypeIDsInScroll(self):
        allTypeIDsInScroll = filter(None, {n.typeID for n in self.scroll.GetNodes()})
        return allTypeIDsInScroll

    def HiliteProblematicEntries(self, warningSlotDict):
        pass

    def UpdateProblematicEntries(self, warningLevel):
        typeIDsToUpdate = self.GetAllTypeIDsInScroll()
        if warningLevel and warningLevel == WARNING_LEVEL_SKILL:
            _, typeIDsToUpdate = GetMissingSkills_HighestLevelByTypeID(typeIDsToUpdate)
        color = GetColorForLevel(warningLevel)
        for eachNode in self.scroll.GetNodes():
            if not eachNode.typeID:
                continue
            elif eachNode.typeID not in typeIDsToUpdate:
                eachNode.warningLevel = None
                continue
            eachNode.warningLevel = warningLevel
            if eachNode.panel and getattr(eachNode.panel, 'SetFittingWarningColor', None):
                eachNode.panel.SetFittingWarningColor(color)


class ItemPickerItemEntryData(object):

    def __init__(self, typeID, itemIDs, isDynamic, typeName, qty):
        self.typeID = typeID
        self.itemIDs = itemIDs
        self.isDynamic = isDynamic
        self.typeName = typeName
        self.qty = qty


class BaseHoldItemPickerMenu(ItemPickerMenu):
    entryClass = ItemPickerBase
    flagID = const.flagCargo

    def GetItems(self):
        items = self.fittingDogmaLocation.GetHoldItems(self.flagID)
        return items

    def RemoveAll(self, *args):
        self.fittingDogmaLocation.RemoveAllItemsFromHold(self.flagID)
        self.ghostFittingSvc.SendOnStatsUpdatedEvent()
        self.LoadItemScroll()

    def GetExtraDataFuncs(self):
        return {'changeNum': self.ChangeNumItems}

    def ChangeNumItems(self, typeID, numWanted):
        self.ghostFittingSvc.ModifyHoldItemStackSize(typeID, numWanted, self.flagID)
        self.UpdateNodes()

    def HiliteProblematicEntries(self, warningSlotDict):
        warningLevel = warningSlotDict.get(self.flagID, None)
        self.UpdateProblematicEntries(warningLevel)

    def UpdateNodes(self):
        qtyByTypeID = {itemInfo.typeID:itemInfo.qty for itemInfo in self.GetSortedItemsInfo()}
        for eachNode in self.scroll.GetNodes():
            typeID = eachNode.typeID
            if not typeID:
                continue
            qty = qtyByTypeID.get(typeID, 0)
            maxExtraQty = GetMaxQty(self.fittingDogmaLocation, eachNode.flagID, {typeID: 1}) or 0
            intRange = (0, qty + maxExtraQty)
            eachNode.intRange = intRange

        for eachNode in self.scroll.GetNodes():
            if eachNode.panel:
                eachNode.panel.SetEditFieldRange()


class CargoItemPickerMenu(BaseHoldItemPickerMenu):
    entryClass = ItemPickerBase
    flagID = const.flagCargo

    def __init__(self, controller, menuParent):
        BaseHoldItemPickerMenu.__init__(self, controller, menuParent)
        self.controller = controller
        self.ChangeSignalConnection(connect=True)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_warning_display_changed, self.HiliteProblematicEntries)]
        ChangeSignalConnect(signalAndCallback, connect)

    def DisconnectController(self):
        with EatSignalChangingErrors(errorMsg='CargoItemPickerMenu'):
            self.ChangeSignalConnection(connect=False)
        self.controller = False


def GetModifiedQtyDict(fittingDogmaLocation, qtyByTypeIDs, flagID):
    if uicore.uilib.Key(uiconst.VK_SHIFT):
        qty = FindQty(fittingDogmaLocation, qtyByTypeIDs, flagID)
        if qty is None:
            return {}
        for eachTypeID in qtyByTypeIDs:
            qtyByTypeIDs[eachTypeID] = qty

    return qtyByTypeIDs


def FindQty(fittingDogmaLocation, qtyByTypeIDs, flagID):
    maxQty = GetMaxQty(fittingDogmaLocation, flagID, qtyByTypeIDs)
    if not maxQty:
        return
    ret = QtyPopup(maxvalue=maxQty, minvalue=1)
    if ret is None:
        qty = None
    else:
        qty = ret['qty']
    return qty


def GetMaxQty(fittingDogmaLocation, flagID, qtyByTypeIDs):
    shipID = fittingDogmaLocation.GetCurrentShipID()
    capacityInfo = fittingDogmaLocation.GetCapacity(shipID, None, flagID)
    volumeLeft = capacityInfo.capacity - capacityInfo.used
    maxQtyForType = 0
    allTypeVol = 0
    for typeID in qtyByTypeIDs:
        if isinstance(typeID, tuple):
            typeID = typeID[0]
        typeVolume = float(evetypes.GetVolume(typeID))
        allTypeVol += typeVolume
        maxQtyForType = max(maxQtyForType, int(volumeLeft / typeVolume))

    maxQty = 0
    if allTypeVol:
        maxQty = volumeLeft / allTypeVol
    if not maxQtyForType:
        return
    return int(maxQty)


def GetDronesInDamgeAmountOrder(fittingDogmaLocation, droneIDs):
    damageTypeAttibutes = [const.attributeEmDamage,
     const.attributeThermalDamage,
     const.attributeKineticDamage,
     const.attributeExplosiveDamage]
    topDamgeOrder = []
    GAV = fittingDogmaLocation.GetAttributeValue
    for eachDroneID in droneIDs:
        damageModifier = GAV(eachDroneID, const.attributeDamageMultiplier)
        dmg = sum({GAV(eachDroneID, x) for x in damageTypeAttibutes})
        totalDmg = damageModifier * dmg
        topDamgeOrder.append((totalDmg, eachDroneID))

    topDamgeOrder = SortListOfTuples(topDamgeOrder, reverse=True)
    return topDamgeOrder


class NoItemEntry(Generic):
    __guid__ = 'NoItemEntry'
    default_showHilite = False
    ENTRYHEIGHT = 28

    def GetHeight(self, *args):
        return NoItemEntry.ENTRYHEIGHT

    def GetEntryWidth(cls, node):
        label = node['label']
        textwidth, textheight = EveLabelMedium.MeasureTextSize(label, maxLines=1)
        return textwidth + 20

    def OnDropData(self, dragObj, nodes):
        onDroppedInListFunc = getattr(self.sr.node, 'onDroppedInListFunc', None)
        if onDroppedInListFunc:
            onDroppedInListFunc(nodes)


VALID_CHARGE_CATEGORIES = [invConst.categoryCharge, invConst.categoryImplant]
VALID_CHARGE_GROUPS = [invConst.groupIceProduct]
VALID_MODULE_CATEGORIES = [invConst.categoryModule, invConst.categorySubSystem]

def IsValidForHold(typeID, flagID):
    categoryID = evetypes.GetCategoryID(typeID)
    if flagID == const.flagCargo:
        if categoryID in VALID_CHARGE_CATEGORIES:
            return True
        if categoryID in VALID_MODULE_CATEGORIES:
            return True
        groupID = evetypes.GetGroupID(typeID)
        if groupID in VALID_CHARGE_GROUPS:
            return True
        if typeID in evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_FILAMENTS):
            return True
        if typeID in evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_OTHER_CARGO_HOLD_TYPES):
            return True
    if flagID == const.flagFighterBay:
        if categoryID == const.categoryFighter:
            return True
    return False


allowedCategories = [const.categoryAccessories,
 const.categoryAncientRelic,
 const.categoryApparel,
 const.categoryAsteroid,
 const.categoryBlueprint,
 const.categoryCharge,
 const.categoryCommodity,
 const.categoryDecryptors,
 const.categoryDeployable,
 const.categoryDrone,
 const.categoryImplant,
 const.categoryMaterial,
 const.categoryModule,
 const.categoryPlanetaryCommodities,
 const.categoryPlanetaryInteraction,
 const.categoryPlanetaryResources,
 const.categoryShip,
 const.categoryShipSkin,
 const.categorySkill,
 const.categoryInfrastructureUpgrade,
 const.categoryStructureModule,
 const.categorySubSystem,
 const.categorySpecialEditionAssets,
 const.categoryFighter]

def IsAllowedToAddAtAll(typeID):
    if dynamicitemattributes.IsDynamicType(typeID):
        return False
    categoryID = evetypes.GetCategoryID(typeID)
    return categoryID in allowedCategories
