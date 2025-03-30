#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\shipInfoPanels\panelFitting.py
from collections import defaultdict
import collections
import itertools
import math
import trinity
import eveformat
import eveicon
import evetypes
import localization
import dogma.data
import uthread2
import dogma.data as dogma_data
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.transform import Transform
from carbonui.util.color import Color
from dogma import const as dogmaConst
from carbon.common.script.util.format import FmtAmt
from carbonui.control.scrollContainer import ScrollContainer
from dogma.attributes.format import GetFormattedAttributeAndValue, GetFormatAndValue
from eve.client.script.ui import eveColor
from eve.client.script.ui.services.menuSvcExtras.openFunctions import SimulateFitting
from eve.client.script.ui.shared.fittingMgmtWindow import ViewFitting
from eve.client.script.ui.shared.fittingScreen.fittingUtil import GetColoredText
from eve.client.script.ui.shared.fittingScreen.tryFit import GetParentShipInfo
from eve.client.script.ui.shared.info.shipInfoCollapsibleGroup import CollapsibleGroup
from eve.client.script.ui.shared.info.shipInfoPanels.panelConst import TAB_FITTING
from eve.client.script.ui.shared.traits import TraitsContainer
from eve.common.lib import appConst as const
from carbonui import Align, TextColor, TextBody, uiconst, Density, AxisAlignment
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.flowcontainer import FlowContainer
from eve.client.script.ui.shared.info.shipInfoConst import ANGLE_FITTING, CONTENT_PADDING, EXPANDED
from eve.client.script.ui.shared.info.shipInfoListEntries import _ListEntryBase, ListEntry, ListEntryStatusBarAttribute, ListEntryAttribute, ListEntryEveType
from eve.client.script.ui.shared.info.shipInfoPanels.panelBase import PanelBase
from eve.client.script.ui.shared.fitting.fittingControllerUtil import GetFittingController
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.util.eveFormat import FmtISK
from inventorycommon.typeHelpers import GetAveragePrice
from inventorycommon.util import IsSubsystemFlagVisible, IsModularShip
from localization import GetByLabel
from utillib import KeyVal
from fsdBuiltData.common.iconIDs import GetIconFile
BAD_COLOR = (70 / 256.0, 26 / 256.0, 13.0 / 256.0)
GOOD_COLOR = (240 / 256.0, 90 / 256.0, 50.0 / 256.0)
EMPTY_COLOR = (0.25,
 0.25,
 0.25,
 0.75)
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

class PanelFitting(PanelBase):

    def ApplyAttributes(self, attributes):
        self.capCapacityAttribute = dogma_data.get_attribute(dogmaConst.attributeCapacitorCapacity)
        self.rechargeRateAttribute = dogma_data.get_attribute(dogmaConst.attributeRechargeRate)
        self.maxcap = None
        self.fitting_controller = None
        super(PanelFitting, self).ApplyAttributes(attributes)
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        self.item = None
        if dogmaLocation.IsItemLoaded(self.itemID):
            self.item = dogmaLocation.GetItem(self.itemID)

    def _construct_content(self):
        uthread2.Yield()
        self._construct_ship_overlay_section()
        self._construct_main_section()
        self._construct_sub_systems_for_type()

    def _gather_data(self):
        self.turretSlotsUsed = 0
        self.launcherSlotsUsed = 0
        self.entryList = []
        inventory = self._controller.get_ship_contents()
        for slotKey, slotInfo in enumerate(FITTING_SLOT_INFO):
            modulesByType = collections.defaultdict(list)
            chargesByFlag = collections.defaultdict(list)
            for item in filter(lambda item: item.flagID in slotInfo['flags'], inventory):
                if IsCharge(item):
                    chargesByFlag[item.flagID].append(item)
                else:
                    modulesByType[item.typeID].append(item)

            usedSlotCount = 0
            itemEntries = []
            for typeID, items in modulesByType.iteritems():
                if HasEffect(typeID, slotInfo['effectID']):
                    usedSlotCount += len(items)
                if HasEffect(typeID, const.effectTurretFitted):
                    self.turretSlotsUsed += len(items)
                if HasEffect(typeID, const.effectLauncherFitted):
                    self.launcherSlotsUsed += len(items)
                lowestFlagID = min((item.flagID for item in items))
                sortKey = (slotKey, lowestFlagID)
                entry = self.GetFittingEntry(typeID, len(items))
                itemEntries.append(entry)
                chargeQuantityByType = collections.defaultdict(int)
                for charge in itertools.chain.from_iterable((chargesByFlag[item.flagID] for item in items)):
                    chargeQuantityByType[charge.typeID] += max(charge.quantity, 1)

                for chargeType, chargeQuantity in chargeQuantityByType.iteritems():
                    sortKey = (slotKey, lowestFlagID, chargeType)
                    entry = self.GetFittingEntry(chargeType, chargeQuantity, isCharge=True)
                    itemEntries.append(entry)

            entry = self.GetFittingSlotEntry(slotInfo, usedSlotCount)
            self.entryList.append(entry)
            self.entryList.extend(itemEntries)

        self.entryList.extend(self.GetDroneEntries(inventory))
        if self.itemID != session.shipid:
            return
        dogma_location = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if not dogma_location.GetShipItem():
            return
        self.fitting_controller = GetFittingController(self.itemID)

    def _construct_main_section(self):
        self.scrollContainer = ScrollContainer(name='fittingScroll', parent=self.rightCont, align=Align.TOALL)
        self.attributeCont = ContainerAutoSize(name='fittingCont', parent=self.scrollContainer, align=Align.TOTOP)
        self.headerCont = Container(name='simulateCont', parent=self.attributeCont, align=Align.TOTOP, height=32, bgColor=(1, 1, 1, 0.1), padBottom=4, state=uiconst.UI_NORMAL)
        linkCont = Container(name='linkCont', parent=self.headerCont, align=Align.TOLEFT, width=16, padLeft=8)
        linkIcon = ButtonIcon(name='linkIcon', parent=linkCont, align=Align.CENTER, texturePath=eveicon.link, iconSize=16, state=uiconst.UI_NORMAL)
        linkIcon.OnClick = self.OnFittingIconClicked
        linkIcon.GetDragData = self.GetFittingDragData
        linkIcon.isDragObject = True
        Button(name='simulateButton', parent=self.headerCont, align=Align.CENTERRIGHT, density=Density.COMPACT, label=GetByLabel('UI/InfoWindow/SimulateButton'), padRight=4, func=self.OnSimulateClicked)
        textCont = Container(name='textCont', parent=self.headerCont, align=Align.TOALL)
        TextBody(name='label', parent=textCont, align=Align.CENTERLEFT, text=GetByLabel('UI/InfoWindow/FittingLabel'), padLeft=8)
        infoSvc = sm.GetService('info')
        attributeDictForType, attributeDict = infoSvc.GetAttributeDictForItem(self.itemID, self.typeID)
        modifiedAttributesDict = infoSvc.FindAttributesThatHaveBeenModified(attributeDictForType, attributeDict)
        for attributeID in [const.attributeCpuOutput, const.attributePowerOutput, const.attributeUpgradeCapacity]:
            modifiedAttribute = modifiedAttributesDict.get(attributeID, None)
            statusBarData = infoSvc.GetStatusBarDataForAttribute(attributeID, self.itemID, self.typeID, modifiedAttribute)
            if statusBarData:
                texturePath = GetIconFile(statusBarData['iconID'])
                ListEntryStatusBarAttribute(label=statusBarData['label'], text=statusBarData['text'], texturePath=texturePath, itemID=self.itemID, attributeID=statusBarData['attributeID'], modifiedAttribute=statusBarData['modifiedAttribute'], color=statusBarData['color'], value=statusBarData['value'], parent=self.attributeCont)
                continue
            if attributeID not in attributeDictForType:
                continue
            attributeData = infoSvc.GetDataForAttribute(attributeID, attributeDictForType[attributeID], self.itemID, self.typeID, modifiedAttribute)
            if attributeData:
                texturePath = GetIconFile(attributeData['iconID'])
                ListEntryAttribute(label=attributeData['label'], text=attributeData['text'], texturePath=texturePath, itemID=self.itemID, attributeID=attributeData['attributeID'], modifiedAttribute=attributeData['modifiedAttribute'], parent=self.attributeCont)

        self.GetHardpointsEntry(self.turretSlotsUsed, self.launcherSlotsUsed, self.attributeCont)
        for entry in self.entryList:
            if entry is None:
                continue
            ConstructFittingEntry(entry, self.attributeCont)

    def _construct_sub_systems_for_type(self):
        if not IsModularShip(self.typeID):
            return
        sub_system_header = Container(name='sub_system_header', parent=self.attributeCont, align=Align.TOTOP, height=32, bgColor=(1, 1, 1, 0.1), padBottom=8, padTop=8, state=uiconst.UI_NORMAL)
        textCont = Container(name='textCont', parent=sub_system_header, align=Align.TOALL)
        TextBody(name='label', parent=textCont, align=Align.CENTERLEFT, text=GetByLabel('UI/InfoWindow/FittingAvailableSubsystems'), padLeft=8)
        sub_systems_by_group = self.get_sub_systems_by_group()
        for group_id in sub_systems_by_group:
            group = CollapsibleGroup(parent=self.attributeCont, align=Align.TOTOP, groupName=evetypes.GetGroupNameByGroup(group_id), groupIcon=GetIconFile(evetypes.GetGroupIconIDByGroup(group_id)), padBottom=8, bold=False, iconSize=24, iconColor=(1, 1, 1, 1))
            for sub_system_type_id in sub_systems_by_group[group_id]:
                sub_system_entry = ListEntrySubsystem(parent=group.mainCont, text=evetypes.GetName(sub_system_type_id), typeID=sub_system_type_id, align=Align.TOTOP)

            group.SetCollapsed(True)

    def _construct_average_price(self):
        self.avgPriceCont = None
        avg_price = GetAveragePrice(self.typeID)
        if not avg_price:
            avg_price = 0
        fitting = self._controller.get_fitting_data()['fitData']
        for typeID, flag, qty in fitting:
            price = GetAveragePrice(typeID)
            if not price:
                continue
            avg_price += price * qty

        if not avg_price:
            return
        self.avgPriceCont = ContainerAutoSize(name='avgPriceCont', parent=self.leftCont, align=Align.TOTOP, height=32, padTop=8)
        labelCont = ContainerAutoSize(name='labelCont', parent=self.avgPriceCont, align=Align.TOTOP)
        label = TextBody(name='label', parent=labelCont, align=Align.TOPLEFT, text=localization.GetByLabel('UI/InfoWindow/EstimatedPrice'), color=TextColor.SECONDARY)
        valueCont = ContainerAutoSize(name='valueCont', parent=self.avgPriceCont, align=Align.TOTOP)
        iconCont = Sprite(name='iconCont', parent=valueCont, align=Align.TOPLEFT, height=16, width=16, texturePath=eveicon.isk)
        self.avg_price = TextBody(name='avgPrice', parent=valueCont, align=Align.TOPLEFT, padLeft=20, text=FmtISK(avg_price))

    def _construct_ship_overlay_section(self):
        self._construct_average_price()
        Sprite(parent=self.leftCont, align=Align.CENTER_PRESERVE_ASPECT, aspectRatio=1, texturePath='res:/UI/Texture/classes/ShipInfo/circle_flair.png', state=uiconst.UI_DISABLED, blendMode=trinity.TR2_SBM_ADD, padLeft=-CONTENT_PADDING[EXPANDED])
        if self.fitting_controller is None:
            return
        bottom = FlowContainer(name='bottom', parent=self.leftCont, align=Align.TOBOTTOM, contentSpacing=(16, 8), crossAxisAlignment=AxisAlignment.END)
        left = ContainerAutoSize(name='left', parent=bottom, align=Align.NOALIGN)
        right = ContainerAutoSize(name='right', parent=bottom, align=Align.NOALIGN)
        offenceLabel = TextBody(parent=left, align=Align.TOPLEFT, text=localization.GetByLabel('UI/Fitting/FittingWindow/Offense'))
        offenceValue = TextBody(parent=left, align=Align.TOPLEFT, text=localization.GetByLabel('UI/Fitting/FittingWindow/DpsLabel', dps=self.fitting_controller.GetTotalDps().value), color=TextColor.SECONDARY, padTop=offenceLabel.height)
        defenseLabel = TextBody(parent=left, align=Align.TOPLEFT, text=localization.GetByLabel('UI/Fitting/FittingWindow/Defense'), padTop=offenceValue.height + 4)
        defenseValue = TextBody(parent=left, align=Align.TOPLEFT, text=localization.GetByLabel('UI/Fitting/FittingWindow/ColoredEffectiveHp', effectiveHp=int(self.fitting_controller.GetEffectiveHp().value)), color=TextColor.SECONDARY, padTop=defenseLabel.height)
        alignLabel = TextBody(parent=left, align=Align.TOPLEFT, text=localization.GetByLabel('Tooltips/FittingWindow/AlignTime'), padTop=defenseValue.height + 4)
        TextBody(parent=left, align=Align.TOPLEFT, text=localization.GetByLabel('UI/Fitting/FittingWindow/AlignTime', value=self.fitting_controller.GetAlignTime().value), color=TextColor.SECONDARY, padTop=alignLabel.height)
        self.capCont = ContainerAutoSize(name='capCont', parent=right, align=Align.CENTERBOTTOM)
        self.construct_power_core_cont(self.capCont)
        self.construct_cap_labels(self.capCont)
        self.update_capacitor_stats()

    def construct_power_core_cont(self, parent):
        sizeWrapper = Container(name='powerCoreWrapper', parent=parent, align=Align.CENTERLEFT, width=50, height=50)
        self.powerCoreCont = Container(parent=sizeWrapper, name='powercore', pos=(0, 0, 50, 50), align=uiconst.CENTER, state=uiconst.UI_DISABLED)

    def construct_cap_labels(self, parent):
        textCont = ContainerAutoSize(name='textCont', parent=parent, align=uiconst.CENTERLEFT, padLeft=60)
        self.capStateLabel = TextBody(text='-', parent=textCont, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT)
        self.capAndRechargeLabel = TextBody(text='-', parent=textCont, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT, padTop=self.capStateLabel.height, color=TextColor.SECONDARY)
        self.capAndRechargeLabel.hint = GetByLabel('UI/Fitting/FittingWindow/CapacityAndRechargeRate')
        self.deltaLabel = TextBody(text='-', parent=textCont, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT, padTop=self.capAndRechargeLabel.height, color=TextColor.SECONDARY)
        self.deltaLabel.hint = GetByLabel('UI/Fitting/FittingWindow/ExcessCapacitor')

    def update_capacitor_stats(self):
        deltaInfo, deltaPercentageInfo, loadBalanceInfo, ttlInfo = self.fitting_controller.GetCapSimulatorInfos()
        self._set_capacitor_header_text(ttlInfo.value, loadBalanceInfo.value)
        self._set_capacitor_recharge_text()
        self._set_capacitor_delta_text(deltaInfo, deltaPercentageInfo)
        self._redraw_power_core()
        self._color_power_core(self.powerUnits, loadBalanceInfo.value, ttlInfo.value)

    def _set_capacitor_header_text(self, TTL, loadBalance):
        if loadBalance > 0:
            sustainableText = eveformat.color(GetByLabel('UI/Fitting/FittingWindow/Stable'), color=eveColor.SUCCESS_GREEN)
            capHint = GetByLabel('UI/Fitting/FittingWindow/ModulesSustainable')
        else:
            sustainableText = eveformat.color(GetByLabel('UI/Fitting/FittingWindow/CapacitorNotStable', time=long(TTL)), color=eveColor.DANGER_RED)
            capHint = GetByLabel('UI/Fitting/FittingWindow/ModulesNotSustainable')
        self.capStateLabel.text = GetByLabel('UI/InfoWindow/CapacitorStatus', status=sustainableText)
        if capHint:
            self.capStateLabel.hint = capHint

    def _set_capacitor_recharge_text(self):
        maxCapInfo = self.fitting_controller.GetCapacitorCapacity()
        maxCapFormattedValue = GetFormatAndValue(self.capCapacityAttribute, int(maxCapInfo.value))
        maxCapText = GetColoredText(isBetter=maxCapInfo.isBetterThanBefore, text=maxCapFormattedValue)
        rechargeRate = self.fitting_controller.GetCapRechargeRate()
        rechargeFormattedValue = GetFormatAndValue(self.rechargeRateAttribute, int(rechargeRate.value))
        rechargeRateText = GetColoredText(isBetter=rechargeRate.isBetterThanBefore, text=rechargeFormattedValue)
        capText = GetByLabel('UI/Fitting/FittingWindow/CapacitorCapAndRechargeTime', capacitorCapacity=maxCapText, capacitorRechargeTime=rechargeRateText, startColorTag1='', startColorTag2='', endColorTag='')
        self.capAndRechargeLabel.text = capText

    def _set_capacitor_delta_text(self, deltaInfo, deltaPercentageInfo):
        deltaText = GetByLabel('UI/Fitting/FittingWindow/CapacitorDelta', delta=deltaInfo.value, percentage=deltaPercentageInfo.value)
        deltaText = GetColoredText(isBetter=deltaInfo.isBetterThanBefore, text=deltaText)
        self.deltaLabel.text = deltaText

    def _redraw_power_core(self):

        def _add_power_column(parent, colIdx, rotationStep, columnWidth, columnHeight):
            rotation = math.radians(colIdx * -rotationStep)
            powerColumn = Transform(parent=parent, name='powerColumn', pos=(0,
             0,
             columnWidth,
             columnHeight), align=uiconst.CENTER, state=uiconst.UI_DISABLED, rotation=rotation, idx=0)
            return powerColumn

        def _add_power_cell(parent, cellIdx):
            newcell = Sprite(parent=parent, name='pmark', pos=(0,
             cellIdx * 6,
             12 - cellIdx * 4,
             7), align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/capacitorCell.png', color=(0.94, 0.35, 0.19, 1.0), idx=0, blendMode=trinity.TR2_SBM_ADD)
            return newcell

        self.powerCoreCont.Flush()
        maxCapInfo = self.fitting_controller.GetCapacitorCapacity()
        numcol = min(10, int(maxCapInfo.value / 50))
        rotStep = 360.0 / max(1, numcol)
        colWidth = max(12, min(16, numcol and int(192 / numcol)))
        colHeight = self.powerCoreCont.height
        self.powerUnits = []
        for colIndex in xrange(numcol):
            column = _add_power_column(self.powerCoreCont, colIndex, rotStep, colWidth, colHeight)
            for cellIndex in xrange(3):
                powerCell = _add_power_cell(column, cellIndex)
                self.powerUnits.insert(0, powerCell)

        self.maxcap = maxCapInfo.value

    def _color_power_core(self, powerUnits, loadBalance, TTL):

        def ScaleColor(colorTuple, scale):
            return Color(colorTuple[0] * scale, colorTuple[1] * scale, colorTuple[2] * scale)

        badColor = ScaleColor(BAD_COLOR, 1.0 - loadBalance)
        goodColor = ScaleColor(GOOD_COLOR, loadBalance)
        visible = max(0, min(len(powerUnits), int(loadBalance * len(powerUnits))))
        for cellIdx, each in enumerate(powerUnits):
            if cellIdx >= visible:
                each.SetRGBA(*EMPTY_COLOR)
            else:
                r = badColor.r + goodColor.r
                g = badColor.g + goodColor.g
                b = badColor.b + goodColor.b
                each.SetRGBA(r, g, b, 1.0)

        if loadBalance == 0:
            hint = GetByLabel('UI/Fitting/FittingWindow/CapRunsOutBy', ttl=long(TTL))
        else:
            hint = GetByLabel('UI/Fitting/FittingWindow/CapSustainableBy', balance=loadBalance * 100)
        self.hint = hint

    def _enable_expanded_view(self):
        self.attributeCont.SetParent(self.scrollContainer)

    def _enable_minimized_view(self):
        self.attributeCont.SetParent(self.content_scroll_minimized)

    @classmethod
    def get_name(cls):
        return localization.GetByLabel('UI/InfoWindow/TabNames/Fitting')

    @classmethod
    def get_icon(cls):
        return eveicon.fitting

    @classmethod
    def is_visible(cls, typeID, itemID = None, rec = None):
        groupID = evetypes.GetGroupID(typeID)
        return groupID not in (const.groupCapsule, const.groupShuttle)

    def get_camera_position(self):
        return ANGLE_FITTING

    def get_tab_type(self):
        return TAB_FITTING

    def _get_slots_used_and_total_text(self, used, total):
        if total == 0:
            return used
        return GetByLabel('UI/InfoWindow/FittingSlotsUsedAndTotal', usedSlots=used, slotCount=total)

    def GetFittingSlotEntry(self, slot_info, module_count):
        slot_count = self.GetTotalSlotCount(slot_info)
        if slot_count <= 0 and module_count <= 0:
            return
        is_my_active_ship = self.itemID is not None and eveCfg.GetActiveShip() == self.itemID
        is_owned_by_me = self.item is not None and self.item.ownerID == session.charid
        if is_my_active_ship or is_owned_by_me:
            return AsFittingEntry(ListEntryFittingSlot, label=self.GetFittingSlotEntryLabel(slot_info), text=self._get_slots_used_and_total_text(module_count, slot_count), iconID=GetIconFile(dogma.data.get_attribute_icon_id(slot_info['attributeID'])))
        else:
            return AsFittingEntry(ListEntry, label=self.GetFittingSlotEntryLabel(slot_info), text=FmtAmt(slot_count), iconID=GetIconFile(dogma.data.get_attribute_icon_id(slot_info['attributeID'])))

    def GetFittingEntry(self, typeID, quantity, isCharge = False):
        itemName = evetypes.GetName(typeID)
        if quantity > 1:
            text = GetByLabel('UI/InfoWindow/FittingItemLabelWithQuantity', quantity=quantity, itemName=itemName)
        else:
            text = itemName
        return AsFittingEntry(ListEntryEveType, typeID=typeID, text=text, indent=16 if isCharge else 0)

    def GetHardpointsEntry(self, turretSlotsUsed, launcherSlotsUsed, parent, align = Align.TOTOP):
        turretSlotCount = self.GetAttributeValue(const.attributeTurretSlotsLeft)
        launcherSlotCount = self.GetAttributeValue(const.attributeLauncherSlotsLeft)
        if self.itemID == eveCfg.GetActiveShip():
            turretSlotCount += turretSlotsUsed
            launcherSlotCount += launcherSlotsUsed
        if turretSlotCount <= 0 and launcherSlotCount <= 0:
            return None
        return ListEntryWeaponSlots(parent=parent, align=align, turretSlots=turretSlotCount, turretSlotsUsed=turretSlotsUsed, launcherSlots=launcherSlotCount, launcherSlotsUsed=launcherSlotsUsed)

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
            headerClass = ListEntryFittingSlot
            headerText = GetByLabel('UI/Inventory/ContainerQuantityAndCapacity', quantity=usedCapacity, capacity=totalDroneCapacity)
        else:
            headerClass = ListEntry
            headerText = GetByLabel('UI/Inventory/ContainerCapacity', capacity=totalDroneCapacity)
        dronesHeaderEntry = AsFittingEntry(headerClass, label=GetByLabel('UI/Drones/Drones'), text=headerText, iconID=eveicon.drones)
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

    def GetAttributeValue(self, attributeID):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if dogmaLocation.IsItemLoaded(self.itemID):
            return dogmaLocation.GetAccurateAttributeValue(self.itemID, attributeID)
        return self.GetTypeAttributeValue(attributeID)

    def GetTypeAttributeValue(self, attributeID):
        info = sm.GetService('godma').GetStateManager().GetShipType(self.typeID)
        return getattr(info, dogma.data.get_attribute_name(attributeID))

    def get_sub_systems_by_group(self):
        godma = sm.StartService('godma')
        subSystemsByGroupID = defaultdict(list)
        for groupID in evetypes.GetGroupIDsByCategory(const.categorySubSystem):
            for typeID in evetypes.GetTypeIDsByGroup(groupID):
                if not evetypes.IsPublished(typeID):
                    continue
                if godma.GetTypeAttribute(typeID, const.attributeFitsToShipType) != self.typeID:
                    continue
                if not IsSubsystemFlagVisible(int(godma.GetTypeAttribute(typeID, const.attributeSubSystemSlot))):
                    continue
                subSystemsByGroupID[groupID].append(typeID)

        return subSystemsByGroupID

    def GetFittingDragData(self):
        fitting = self._controller.get_fitting_data()
        entry = KeyVal()
        entry.fitting = fitting
        entry.label = fitting.name
        entry.displayText = fitting.name
        entry.__guid__ = 'listentry.FittingEntry'
        return [entry]

    def OnFittingIconClicked(self, *args):
        fitting = self._controller.get_fitting_data()
        windowID = 'Save_ViewFitting_%s' % fitting.shipTypeID
        wnd = ViewFitting.GetIfOpen(windowID=windowID)
        if wnd and not wnd.destroyed:
            wnd.ReloadWnd(windowID, fitting, truncated=None)
            wnd.Maximize()
        else:
            ViewFitting.Open(windowID=windowID, fitting=fitting, truncated=None)

    def OnSimulateClicked(self, *args):
        self._controller.open_simulation()


def ConstructFittingEntry(entryData, parent, align = Align.TOTOP):
    entryClass, label, text, typeID, iconID, getIcon, indent = entryData
    return entryClass(label=label, text=text, typeID=typeID, texturePath=iconID, getIcon=getIcon, indent=indent, parent=parent, align=align)


def AsFittingEntry(entryClass, label = None, text = None, typeID = None, iconID = None, getIcon = False, indent = 0):
    return (entryClass,
     label,
     text,
     typeID,
     iconID,
     getIcon,
     indent)


def IsCharge(item):
    return item.categoryID == const.categoryCharge


def HasEffect(typeID, effectID):
    return sm.GetService('clientDogmaStaticSvc').TypeHasEffect(typeID, effectID)


class ListEntryFittingSlot(_ListEntryBase):
    default_bgColor = (1, 1, 1, 0.05)

    def __init__(self, label = None, text = None, texturePath = None, indent = 0, **kw):
        self.label = label
        self.text = text
        self.texturePath = texturePath
        super(ListEntryFittingSlot, self).__init__(indent, **kw)

    def construct_layout(self):
        super(ListEntryFittingSlot, self).construct_layout()
        iconCont = Container(parent=self.content, align=Align.TOLEFT, width=24, padLeft=8, padRight=8)
        Sprite(parent=iconCont, align=Align.CENTER, texturePath=self.texturePath, width=24, height=24, color=TextColor.SECONDARY)
        textCont = ContainerAutoSize(parent=self.content, align=Align.TORIGHT, padRight=8)
        TextBody(parent=textCont, text=self.text, align=Align.CENTERRIGHT)
        labelCont = Container(parent=self.content, align=Align.TOALL, clipChildren=True, padRight=4)
        TextBody(parent=labelCont, align=Align.CENTERLEFT, text=self.label, autoFadeSides=16)


class ListEntryWeaponSlots(_ListEntryBase):

    def __init__(self, turretSlots, turretSlotsUsed, launcherSlots, launcherSlotsUsed, **kw):
        self.turretSlots = turretSlots
        self.turretSlotsUsed = turretSlotsUsed
        self.launcherSlots = launcherSlots
        self.launcherSlotsUsed = launcherSlotsUsed
        super(ListEntryWeaponSlots, self).__init__(indent=0, **kw)

    def construct_layout(self):
        super(ListEntryWeaponSlots, self).construct_layout()
        turretTopContainer = Container(parent=self.content, align=Align.TOLEFT_PROP, width=0.5, state=uiconst.UI_NORMAL)
        turretTopContainer.LoadTooltipPanel = self.LoadTooltipPanelForTurret
        Sprite(name='turretHardpointsIcon', texturePath='res:/UI/Texture/Icons/26_64_1.png', parent=turretTopContainer, align=uiconst.TOPLEFT, pos=(1, 2, 24, 24), ignoreSize=True, state=uiconst.UI_DISABLED)
        self.turretBubbles = []
        for i in range(8):
            x = i * 14 + 26
            bubble = Sprite(parent=turretTopContainer, pos=(x,
             7,
             14,
             16), useSizeFromTexture=True, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
            self.turretBubbles.append(bubble)

        launcherTopContainer = Container(parent=self.content, align=uiconst.TOLEFT_PROP, width=0.5, state=uiconst.UI_NORMAL)
        launcherTopContainer.LoadTooltipPanel = self.LoadTooltipPanelForLauncher
        Sprite(name='launcherHardpointsIcon', texturePath='res:/UI/Texture/Icons/81_64_16.png', parent=launcherTopContainer, align=uiconst.TOPRIGHT, pos=(1, 2, 24, 24), ignoreSize=True, state=uiconst.UI_DISABLED)
        self.launcherBubbles = []
        for i in range(8):
            x = i * 14 + 26
            bubble = Sprite(parent=launcherTopContainer, pos=(x,
             7,
             14,
             16), useSizeFromTexture=True, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED)
            self.launcherBubbles.append(bubble)

        self.FillBubbles(self.turretBubbles, self.turretSlotsUsed, self.turretSlots)
        self.FillBubbles(self.launcherBubbles, self.launcherSlotsUsed, self.launcherSlots)

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

    def LoadTooltipPanelForTurret(self, tooltipPanel, *args):
        counterText = localization.GetByLabel('Tooltips/FittingWindow/TurretHardPointBubbles_description', hardpointsUsed=self.turretSlotsUsed, hardpointsTotal=self.turretSlots)
        return self.LoadTooltipPanelForTurretsAndLaunchers(tooltipPanel, const.attributeTurretSlotsLeft, counterText)

    def LoadTooltipPanelForLauncher(self, tooltipPanel, *args):
        counterText = localization.GetByLabel('Tooltips/FittingWindow/LauncherHardPointBubbles_description', hardpointsUsed=self.launcherSlotsUsed, hardpointsTotal=self.launcherSlots)
        return self.LoadTooltipPanelForTurretsAndLaunchers(tooltipPanel, const.attributeLauncherSlotsLeft, counterText)

    def LoadTooltipPanelForTurretsAndLaunchers(self, tooltipPanel, attributeID, counterText):
        attribute = dogma.data.get_attribute(attributeID)
        headerText = localization.GetByMessageID(attribute.tooltipTitleID)
        descriptionText = localization.GetByMessageID(attribute.tooltipDescriptionID)
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=headerText, bold=True)
        tooltipPanel.AddLabelMedium(text=counterText, bold=True, align=uiconst.TOPRIGHT, cellPadding=(20, 0, 0, 0))
        tooltipPanel.AddLabelMedium(text=descriptionText, wrapWidth=200, colSpan=tooltipPanel.columns, color=(0.6, 0.6, 0.6, 1))


class ListEntrySubsystem(ListEntryEveType):

    def LoadTooltipPanel(self, tooltip_panel, *args):
        tooltip_panel.LoadGeneric1ColumnTemplate()
        wrapper = Container(align=Align.CENTERTOP, width=300, height=450)
        traitCont = TraitsContainer(parent=wrapper, typeID=self._typeID, align=uiconst.TOTOP, traitAttributeIcons=False)
        wrapper.height = traitCont.height + 32
        tooltip_panel.AddCell(wrapper)
