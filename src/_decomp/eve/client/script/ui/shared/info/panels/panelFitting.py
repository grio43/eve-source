#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelFitting.py
import collections
import itertools
import carbonui.const as uiconst
import dogma.data
import evetypes
import eveicon
from carbon.common.script.util.format import FmtAmt
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.util.various_unsorted import SortListOfTuples
from dogma.attributes.format import GetFormattedAttributeAndValue
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.shared.fittingScreen.tryFit import GetParentShipInfo
from eve.common.lib import appConst as const
from eve.common.script.sys import eveCfg, idCheckers
from localization import GetByLabel, GetByMessageID
FITTING_SLOT_INFO = [{'label': 'UI/InfoWindow/FittingHighPowerSlot',
  'attributeID': const.attributeHiSlots,
  'flags': const.hiSlotFlags,
  'effectID': const.effectHiPower},
 {'label': 'UI/InfoWindow/FittingMediumPowerSlots',
  'attributeID': const.attributeMedSlots,
  'flags': const.medSlotFlags,
  'effectID': const.effectMedPower},
 {'label': 'UI/InfoWindow/FittingLowPowerSlots',
  'attributeID': const.attributeLowSlots,
  'flags': const.loSlotFlags,
  'effectID': const.effectLoPower},
 {'label': 'UI/InfoWindow/FittingRigSlots',
  'attributeID': const.attributeUpgradeSlotsLeft,
  'flags': const.rigSlotFlags,
  'effectID': const.effectRigSlot},
 {'label': 'UI/InfoWindow/FittingServiceSlots',
  'attributeID': const.attributeServiceSlots,
  'flags': const.serviceSlotFlags,
  'effectID': const.effectServiceSlot},
 {'label': 'UI/InfoWindow/FittingSubsystemSlots',
  'attributeID': const.attributeSubSystemSlot,
  'flags': const.subsystemSlotFlags,
  'effectID': const.effectSubSystem}]

class PanelFitting(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.item = attributes.get('item', None)
        self.itemID = attributes.get('itemID', None)
        if self.itemID is None and self.item is not None:
            self.itemID = self.item.itemID
        if self.item is None and self.itemID is not None:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            if dogmaLocation.IsItemLoaded(self.itemID):
                self.item = dogmaLocation.GetItem(self.itemID)

    def Load(self):
        self.Flush()
        fittingScroll = Scroll(name='fittingScroll', parent=self, padding=const.defaultPadding)
        turretSlotsUsed = 0
        launcherSlotsUsed = 0
        entryList = []
        inventory = self.GetShipContents()
        for slotKey, slotInfo in enumerate(FITTING_SLOT_INFO):
            modulesByType = collections.defaultdict(list)
            chargesByFlag = collections.defaultdict(list)
            for item in filter(lambda item: item.flagID in slotInfo['flags'], inventory):
                if IsCharge(item):
                    chargesByFlag[item.flagID].append(item)
                else:
                    modulesByType[item.typeID].append(item)

            usedSlotCount = 0
            for typeID, items in modulesByType.iteritems():
                if HasEffect(typeID, slotInfo['effectID']):
                    usedSlotCount += len(items)
                if HasEffect(typeID, const.effectTurretFitted):
                    turretSlotsUsed += len(items)
                if HasEffect(typeID, const.effectLauncherFitted):
                    launcherSlotsUsed += len(items)
                lowestFlagID = min((item.flagID for item in items))
                sortKey = (slotKey, lowestFlagID)
                entry = self.GetFittingEntry(typeID, len(items))
                entryList.append((sortKey, entry))
                chargeQuantityByType = collections.defaultdict(int)
                for charge in itertools.chain.from_iterable((chargesByFlag[item.flagID] for item in items)):
                    chargeQuantityByType[charge.typeID] += max(charge.quantity, 1)

                for chargeType, chargeQuantity in chargeQuantityByType.iteritems():
                    sortKey = (slotKey, lowestFlagID, chargeType)
                    entry = self.GetFittingEntry(chargeType, chargeQuantity, isCharge=True)
                    entryList.append((sortKey, entry))

            sortKey = (slotKey,)
            entry = self.GetFittingSlotEntry(slotInfo, usedSlotCount)
            entryList.append((sortKey, entry))

        sortedEntryList = sm.GetService('info').GetAttributeScrollListForItem(itemID=self.itemID, typeID=self.typeID, attrList=[const.attributeCpuOutput, const.attributePowerOutput, const.attributeUpgradeCapacity])
        sortedEntryList.append(self.GetHardpointsEntry(turretSlotsUsed, launcherSlotsUsed))
        sortedEntryList.extend(SortListOfTuples(entryList))
        sortedEntryList.extend(self.GetDroneEntries(inventory))
        fittingScroll.Load(contentList=filter(None, sortedEntryList))

    def GetFittingSlotEntry(self, slotInfo, moduleCount):
        slotCount = self.GetTotalSlotCount(slotInfo)
        if slotCount <= 0 and moduleCount <= 0:
            return
        isMyActiveShip = self.itemID is not None and eveCfg.GetActiveShip() == self.itemID
        isOwnedByMe = self.item is not None and self.item.ownerID == session.charid
        if isMyActiveShip or isOwnedByMe:
            return GetFromClass(FittingSlotEntry, {'label': self.GetFittingSlotEntryLabel(slotInfo),
             'text': GetByLabel('UI/InfoWindow/FittingSlotsUsedAndTotal', usedSlots=moduleCount, slotCount=slotCount),
             'iconID': dogma.data.get_attribute_icon_id(slotInfo['attributeID']),
             'line': 1})
        else:
            return GetFromClass(LabelTextSides, {'label': self.GetFittingSlotEntryLabel(slotInfo),
             'text': FmtAmt(slotCount),
             'iconID': dogma.data.get_attribute_icon_id(slotInfo['attributeID']),
             'line': 1})

    def GetFittingEntry(self, typeID, quantity, isCharge = False):
        itemName = evetypes.GetName(typeID)
        if quantity > 1:
            label = GetByLabel('UI/InfoWindow/FittingItemLabelWithQuantity', quantity=quantity, itemName=itemName)
        else:
            label = itemName
        return GetFromClass(FittingItemEntry, {'typeID': typeID,
         'label': label,
         'getIcon': True,
         'indentLevel': 2 if isCharge else 1})

    def GetHardpointsEntry(self, turretSlotsUsed, launcherSlotsUsed):
        turretSlotCount = self.GetAttributeValue(const.attributeTurretSlotsLeft)
        launcherSlotCount = self.GetAttributeValue(const.attributeLauncherSlotsLeft)
        if self.itemID == eveCfg.GetActiveShip():
            turretSlotCount += turretSlotsUsed
            launcherSlotCount += launcherSlotsUsed
        if turretSlotCount <= 0 and launcherSlotCount <= 0:
            return None
        return GetFromClass(TurretAndLauncherSlotEntry, {'turretSlotsUsed': turretSlotsUsed,
         'turretSlotCount': turretSlotCount,
         'launcherSlotsUsed': launcherSlotsUsed,
         'launcherSlotCount': launcherSlotCount})

    def GetDroneEntries(self, items):
        if not idCheckers.IsShipType(self.typeID):
            return []
        totalDroneCapacity = dogma.data.get_type_attribute(self.typeID, const.attributeDroneCapacity)
        if not totalDroneCapacity:
            return []
        dronesByType = collections.defaultdict(int)
        for item in items:
            if item.flagID == const.flagDroneBay:
                dronesByType[item.typeID] += item.stacksize

        usedCapacity = sum([ evetypes.GetVolume(typeID) * amount for typeID, amount in dronesByType.iteritems() ])
        isMyActiveShip = self.itemID is not None and eveCfg.GetActiveShip() == self.itemID
        isOwnedByMe = self.item is not None and self.item.ownerID == session.charid
        if isMyActiveShip or isOwnedByMe:
            headerClass = FittingSlotEntry
            headerText = GetByLabel('UI/Inventory/ContainerQuantityAndCapacity', quantity=usedCapacity, capacity=totalDroneCapacity)
        else:
            headerClass = LabelTextSides
            headerText = GetByLabel('UI/Inventory/ContainerCapacity', capacity=totalDroneCapacity)
        dronesHeaderEntry = GetFromClass(headerClass, {'label': GetByLabel('UI/Drones/Drones'),
         'text': headerText,
         'iconID': eveicon.drones,
         'line': 1})
        result = [dronesHeaderEntry]
        result.extend([ self.GetFittingEntry(typeID, quantity) for typeID, quantity in sorted(dronesByType.items(), key=lambda d: evetypes.GetName(d[0])) ])
        return result

    def GetTotalSlotCount(self, slotInfo):
        if slotInfo['attributeID'] == const.attributeUpgradeSlotsLeft:
            return self.GetTypeAttributeValue(slotInfo['attributeID'])
        else:
            return self.GetAttributeValue(slotInfo['attributeID'])

    def GetFittingSlotEntryLabel(self, slotInfo):
        if slotInfo['attributeID'] == const.attributeUpgradeSlotsLeft:
            rigSize = self.GetAttributeValue(const.attributeRigSize)
            formattedRigSize = GetFormattedAttributeAndValue(const.attributeRigSize, rigSize)
            return GetByLabel(slotInfo['label'], rigSize=getattr(formattedRigSize, 'value', ''))
        return GetByLabel(slotInfo['label'])

    def GetShipContents(self):
        if self.itemID is None:
            return []
        if session.shipid == self.itemID:
            shipinfo = sm.GetService('godma').GetItem(self.itemID)
            if shipinfo is not None and getattr(shipinfo, 'inventory', None) is not None:
                return shipinfo.inventory.List()
        if self.item is None:
            return []
        if not self.item.singleton:
            return []
        if self.item.ownerID == session.charid and self.item.locationID:
            dockableLocationID = self.item.locationID
            solarSystemID = None
            if self.item.flagID in (const.flagCargo, const.flagShipHangar):
                parentShipInfo = GetParentShipInfo(self.item)
                if parentShipInfo:
                    dockableLocationID, solarSystemID = parentShipInfo
            inventoryMgr = sm.GetService('invCache').GetInventoryMgr()
            try:
                return inventoryMgr.GetContainerContents(self.item.itemID, dockableLocationID, solarSystemID)
            except AttributeError:
                pass

        return []

    def GetAttributeValue(self, attributeID):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if dogmaLocation.IsItemLoaded(self.itemID):
            return dogmaLocation.GetAccurateAttributeValue(self.itemID, attributeID)
        return self.GetTypeAttributeValue(attributeID)

    def GetTypeAttributeValue(self, attributeID):
        info = sm.GetService('godma').GetStateManager().GetShipType(self.typeID)
        return getattr(info, dogma.data.get_attribute_name(attributeID))


def IsCharge(item):
    return item.categoryID == const.categoryCharge


def HasEffect(typeID, effectID):
    return sm.GetService('clientDogmaStaticSvc').TypeHasEffect(typeID, effectID)


class FittingItemEntry(Item):

    def Load(self, node):
        Item.Load(self, node)
        indentLevel = node.get('indentLevel', 0)
        if indentLevel > 0:
            self.sr.icon.left = 16 * indentLevel
            self.sr.label.left = 16 * indentLevel + self.sr.icon.width + 4


class FittingSlotEntry(LabelTextSides):

    def Startup(self, *args):
        super(FittingSlotEntry, self).Startup(*args)
        FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT)


class TurretAndLauncherSlotEntry(SE_BaseClassCore):

    def Startup(self, *args):
        turretTopContainer = Container(parent=self, align=uiconst.TOLEFT_PROP, width=0.5, state=uiconst.UI_NORMAL)
        turretTopContainer.LoadTooltipPanel = self.LoadTooltipPanelForTurret
        Sprite(name='turretHardpointsIcon', texturePath='res:/UI/Texture/Icons/26_64_1.png', parent=turretTopContainer, align=uiconst.TOPLEFT, pos=(1, 2, 24, 24), ignoreSize=True, state=uiconst.UI_DISABLED)
        self.sr.turretBubbles = []
        for i in range(8):
            x = i * 14 + 26
            bubble = Sprite(parent=turretTopContainer, pos=(x,
             7,
             14,
             16), useSizeFromTexture=True, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
            self.sr.turretBubbles.append(bubble)

        launcherTopContainer = Container(parent=self, align=uiconst.TOLEFT_PROP, width=0.5, state=uiconst.UI_NORMAL)
        launcherTopContainer.LoadTooltipPanel = self.LoadTooltipPanelForLauncher
        Sprite(name='launcherHardpointsIcon', texturePath='res:/UI/Texture/Icons/81_64_16.png', parent=launcherTopContainer, align=uiconst.TOPRIGHT, pos=(1, 2, 24, 24), ignoreSize=True, state=uiconst.UI_DISABLED)
        self.sr.launcherBubbles = []
        for i in range(8):
            x = i * 14 + 26
            bubble = Sprite(parent=launcherTopContainer, pos=(x,
             7,
             14,
             16), useSizeFromTexture=True, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED)
            self.sr.launcherBubbles.append(bubble)

    def Load(self, node):
        self.sr.node = node
        self.FillBubbles(self.sr.turretBubbles, node.get('turretSlotsUsed', 0), node.get('turretSlotCount', 0))
        self.FillBubbles(self.sr.launcherBubbles, node.get('launcherSlotsUsed', 0), node.get('launcherSlotCount', 0))

    def FillBubbles(self, bubbles, slotsUsed, slotCount):
        for i, bubble in enumerate(bubbles):
            if i < slotsUsed:
                bubble.display = True
                bubble.texturePath = 'res:/UI/Texture/classes/Fitting/slotTaken.png'
            elif i < slotCount:
                bubble.display = True
                bubble.texturePath = 'res:/UI/Texture/classes/Fitting/slotLeft.png'
            else:
                bubble.display = False

    def GetHeight(self, *args):
        node, width = args
        node.height = 30
        return 30

    def LoadTooltipPanelForTurret(self, tooltipPanel, *args):
        turretsFitted = int(self.sr.node.get('turretSlotsUsed', 0))
        turretSlotsCount = int(self.sr.node.get('turretSlotCount', 0))
        counterText = GetByLabel('Tooltips/FittingWindow/TurretHardPointBubbles_description', hardpointsUsed=turretsFitted, hardpointsTotal=turretSlotsCount)
        return self.LoadTooltipPanelForTurretsAndLaunchers(tooltipPanel, const.attributeTurretSlotsLeft, counterText)

    def LoadTooltipPanelForLauncher(self, tooltipPanel, *args):
        turretsFitted = int(self.sr.node.get('launcherSlotsUsed', 0))
        turretSlotsCount = int(self.sr.node.get('launcherSlotCount', 0))
        counterText = GetByLabel('Tooltips/FittingWindow/LauncherHardPointBubbles_description', hardpointsUsed=turretsFitted, hardpointsTotal=turretSlotsCount)
        return self.LoadTooltipPanelForTurretsAndLaunchers(tooltipPanel, const.attributeLauncherSlotsLeft, counterText)

    def LoadTooltipPanelForTurretsAndLaunchers(self, tooltipPanel, attributeID, counterText):
        attribute = dogma.data.get_attribute(attributeID)
        headerText = GetByMessageID(attribute.tooltipTitleID)
        descriptionText = GetByMessageID(attribute.tooltipDescriptionID)
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=headerText, bold=True)
        tooltipPanel.AddLabelMedium(text=counterText, bold=True, align=uiconst.TOPRIGHT, cellPadding=(20, 0, 0, 0))
        tooltipPanel.AddLabelMedium(text=descriptionText, wrapWidth=200, colSpan=tooltipPanel.columns, color=(0.6, 0.6, 0.6, 1))

    @classmethod
    def GetCopyData(cls, node):
        return '%s\t%s\n%s\t%s' % (dogma.data.get_attribute_display_name(const.attributeTurretSlotsLeft),
         node.get('turretSlotCount', 0),
         dogma.data.get_attribute_display_name(const.attributeLauncherSlotsLeft),
         node.get('launcherSlotCount', 0))
