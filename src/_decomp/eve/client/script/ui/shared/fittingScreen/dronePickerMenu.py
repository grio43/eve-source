#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\dronePickerMenu.py
import carbonui.const as uiconst
import uthread
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.entries.mouse_inside_scroll_entry import MouseInsideScrollEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge, EveLabelSmall
from eve.client.script.ui.control.eveWindowUnderlay import RaisedUnderlay
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from eve.client.script.ui.shared.fittingScreen.droneTooltip import DroneFittingTooltipWrapper
from eve.client.script.ui.shared.fittingScreen.itemPickerMenu import ItemPickerMenu, ItemPickerBase, GetMaxQty
from eve.common.lib import appConst as const
from localization import GetByLabel
from signals.signalUtil import ChangeSignalConnect

class ItemDronePicker(ItemPickerBase):
    __guid__ = 'listentry.ItemDronePicker'
    ENTRYHEIGHT = 64
    ICONWIDTH = ENTRYHEIGHT - 4
    NUM_CONT_WIDTH = 50
    REMOVE_PADDING = 36
    haveSkillsLabelPath = 'UI/Fitting/FittingWindow/HaveSkillsForDrone'
    dontHaveSkillsLabelPath = 'UI/Fitting/FittingWindow/MissingSkillsForDrone'

    def ApplyAttributes(self, attributes):
        ItemPickerBase.ApplyAttributes(self, attributes)
        self.tooltipPanelClassInfo = DroneFittingTooltipWrapper()
        fromBottom = 15
        self.selectedLabel = EveLabelSmall(text=GetByLabel('UI/Fitting/FittingWindow/SelectedDrones'), parent=self.restCont, left=0, top=fromBottom, state=uiconst.UI_DISABLED, color=None, maxLines=1, align=uiconst.BOTTOMLEFT)
        self.selectedLabel.SetRGBA(0.75, 0.75, 0.75, 0.75)
        left = self.selectedLabel.width + 2
        self.dronePickingCont = DronePickingBoxCont(parent=self.restCont, align=uiconst.BOTTOMLEFT, top=fromBottom, left=left, boxClickedFunc=self.OnBoxClicked)
        self.label.top = 10
        self.label.SetAlign(uiconst.TOPLEFT)
        if self.sr.node.get('isDynamic'):
            self.numItemsCont.Hide()

    def Load(self, node):
        ItemPickerBase.Load(self, node)
        self.dronePickingCont.LoadBoxes(node)

    def OnBoxClicked(self, box):
        if self.changeActive:
            numWanted = box.boxIdx + 1
            self.changeActive(self.sr.node, numWanted)

    @classmethod
    def GetEntryWidth(cls, node):
        maxActiveDrones = node.get('maxActiveDrones', 5)
        label = node['label']
        textwidth, _ = EveLabelMedium.MeasureTextSize(label, maxLines=1)
        selectedTw, _ = EveLabelSmall.MeasureTextSize(GetByLabel('UI/Fitting/FittingWindow/SelectedDrones'), maxLines=1)
        boxContWidth = (DronePickingBoxCont.boxSize + DronePickingBoxCont.boxPadding) * maxActiveDrones
        centerWidth = max(textwidth, selectedTw + boxContWidth)
        w = cls.NUM_CONT_WIDTH + cls.ENTRYHEIGHT + centerWidth + cls.REMOVE_PADDING + 40
        return w

    def GetHeight(self, *args):
        node, width = args
        node.height = ItemDronePicker.ENTRYHEIGHT
        return node.height

    def GetDroneActivityDescription(self):
        return ''

    def GetDroneStateDescription(self):
        return ''


class DronePickerMenu(ItemPickerMenu):
    entryClass = ItemDronePicker
    emptyLabelPath = 'UI/Fitting/FittingWindow/NoDronesSimulated'
    flagID = const.flagDroneBay

    def __init__(self, controller, menuParent):
        ItemPickerMenu.__init__(self, controller, menuParent)
        self.controller = controller
        self.ChangeSignalConnection(connect=True)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_warning_display_changed, self.HiliteProblematicEntries)]
        ChangeSignalConnect(signalAndCallback, connect)

    def DisconnectController(self):
        with EatSignalChangingErrors(errorMsg='DronePickerMenu'):
            self.ChangeSignalConnection(connect=False)
        self.controller = False

    def GetItems(self):
        shipDogmaItem = self.fittingDogmaLocation.GetShip()
        if shipDogmaItem:
            return shipDogmaItem.GetDrones()
        else:
            return {}

    def GetHeaderEntry(self, activeItemsSet):
        allDroneIDs = set(self.GetItems().keys())
        numActive = len(allDroneIDs.intersection(activeItemsSet))
        numSelectable = self.GetMaxActiveDrones()
        entry = GetFromClass(DronePickingHeader, {'itemIDs': set(allDroneIDs),
         'numActive': numActive,
         'numSelectable': numSelectable})
        return entry

    def GetExtraData(self):
        activeItemsCopy = self.GetActiveItems()
        totalCanActivate = self.GetTotalCanActivate(len(activeItemsCopy))
        maxActiveDrones = self.GetMaxActiveDrones()
        bandwidthLeft = self.GetBandwidthLeft()
        extraData = {'totalCanActivate': totalCanActivate,
         'bandwidthLeft': bandwidthLeft,
         'maxActiveDrones': maxActiveDrones}
        return extraData

    def GetExtraDataForType(self, itemIDs, activeItemsSet, typeID):
        activeOfType = activeItemsSet.intersection(itemIDs)
        numActive = len(activeOfType)
        dynamicItemSvc = sm.GetService('dynamicItemSvc')
        if dynamicItemSvc.IsDynamicItem(typeID):
            attributes = dynamicItemSvc.GetDynamicItemAttributes(list(itemIDs)[0])
            droneBandwidth = attributes[const.attributeDroneBandwidthUsed]
        else:
            droneBandwidth = self.fittingDogmaLocation.dogmaStaticMgr.GetTypeAttribute(typeID, const.attributeDroneBandwidthUsed)
        return {'numActive': numActive,
         'droneBandwidth': droneBandwidth,
         'isDynamic': dynamicItemSvc.IsDynamicItem(typeID)}

    def GetExtraDataFuncs(self):
        extraDataFunc = {'changeActive': self.ChangeActiveNum,
         'addToActive': self.AddDroneToActive,
         'changeNum': self.ChangeNumDrones,
         'removeFromActive': self.RemoveDroneFromActive}
        return extraDataFunc

    def GetTotalCanActivate(self, numActive):
        return max(0, self.GetMaxActiveDrones() - numActive)

    def RemoveItem(self, node):
        typeID = node.typeID
        itemID = list(node.itemIDs)[0]
        dynamicItemSvc = sm.GetService('dynamicItemSvc')
        allDrones = self.GetItems()
        allDronesOfType = [ droneID for droneID, d in allDrones.iteritems() if d.itemID == itemID or d.typeID == typeID and not dynamicItemSvc.IsDynamicItem(typeID) ]
        sm.GetService('ghostFittingSvc').UnfitDrones(allDronesOfType)
        self.LoadItemScroll()

    def ChangeActiveNum(self, node, wantNumActive):
        itemIDs = node.itemIDs
        activeOfType = self.GetActiveOfType(itemIDs)
        if len(activeOfType) == wantNumActive:
            wantNumActive = max(0, wantNumActive - 1)
        diff = wantNumActive - len(activeOfType)
        if activeOfType and diff < 0:
            numToRemove = -diff
            self.RemoveDroneFromActive(activeOfType, numToRemove)
        elif diff > 0:
            self.AddDroneToActive(itemIDs, numToAdd=diff)

    def GetActiveOfType(self, itemIDs):
        activeOfType = itemIDs.intersection(self.GetActiveItems())
        return activeOfType

    def AddDroneToActive(self, itemIDs, numToAdd = 1):
        activeOfType = self.GetActiveOfType(itemIDs)
        notActiveItemIDs = itemIDs.difference(activeOfType)
        try:
            for i, eachItemID in enumerate(notActiveItemIDs):
                if i >= numToAdd:
                    break
                self.fittingDogmaLocation.SetDroneActivityState(eachItemID, setActive=True)

        finally:
            sm.GetService('ghostFittingSvc').SendOnStatsUpdatedEvent()
            self.UpdateNodes()

    def RemoveDroneFromActive(self, itemIDs, numToRemove = 1):
        activeOfType = self.GetActiveOfType(itemIDs)
        try:
            for i, eachItemID in enumerate(list(activeOfType)):
                if i >= numToRemove:
                    break
                self.fittingDogmaLocation.SetDroneActivityState(eachItemID, setActive=False)

        finally:
            sm.GetService('ghostFittingSvc').SendOnStatsUpdatedEvent()
            self.UpdateNodes()

    def ChangeNumDrones(self, typeID, numWanted):
        allDrones = self.GetItems()
        allDronesOfType = [ droneID for droneID, d in allDrones.iteritems() if d.typeID == typeID ]
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        diff = numWanted - len(allDronesOfType)
        if diff > 0:
            ghostFittingSvc.TryFitDronesToDroneBay({(typeID, None): diff})
        elif diff < 0:
            activeDrones = self.GetActiveItems()
            allDronesOfType.sort(key=lambda x: x in activeDrones)
            dronesToUnfit = allDronesOfType[:-diff]
            ghostFittingSvc.UnfitDrones(dronesToUnfit)
        else:
            return
        uthread.new(self.UpdateNodes)

    def GetActiveItems(self):
        activeItemsCopy = self.fittingDogmaLocation.GetActiveDrones()
        return activeItemsCopy

    def GetMaxActiveDrones(self):
        return max(5, int(self.fittingDogmaLocation.GetMaxActiveDrones()))

    def GetBandwidthLeft(self):
        shipID = self.fittingDogmaLocation.GetCurrentShipID()
        activeDrones = self.fittingDogmaLocation.GetActiveDrones()
        from shipfitting.droneUtil import GetDroneBandwidth
        bandwidthUsed, shipBandwith = GetDroneBandwidth(shipID, self.fittingDogmaLocation, activeDrones)
        return shipBandwith - bandwidthUsed

    def HiliteProblematicEntries(self, warningSlotDict):
        warningLevel = warningSlotDict.get(self.flagID, None)
        self.UpdateProblematicEntries(warningLevel)

    def UpdateNodes(self):
        allItems = self.GetItems()
        activeItemsSet = set(self.GetActiveItems())
        extraData = self.GetExtraData()
        dynamicItemSvc = sm.GetService('dynamicItemSvc')
        for eachNode in self.scroll.GetNodes():
            typeID = eachNode.typeID
            if eachNode.decoClass == DronePickingHeader:
                eachNode.numActive = len(activeItemsSet)
                eachNode.itemIDs = set(self.GetItems().keys())
                continue
            if eachNode.itemIDs:
                itemID = list(eachNode.itemIDs)[0]
            else:
                itemID = None
            allItemsOfType = {eachItemID:item for eachItemID, item in allItems.iteritems() if item.itemID == itemID or item.typeID == typeID and not dynamicItemSvc.IsDynamicItem(item.typeID)}
            itemIDs = set(allItemsOfType.keys())
            eachNode.itemIDs = itemIDs
            currentQty = sum((v.stacksize for v in allItemsOfType.itervalues()))
            maxExtraQty = GetMaxQty(self.fittingDogmaLocation, const.flagDroneBay, {typeID: 1}) or 0
            eachNode.intRange = (0, currentQty + maxExtraQty)
            eachNode.qty = currentQty
            eachNode.update(extraData)
            extraDataForType = self.GetExtraDataForType(itemIDs, activeItemsSet, typeID)
            eachNode.update(extraDataForType)

        for eachNode in self.scroll.GetNodes():
            if eachNode.panel:
                eachNode.panel.Load(eachNode)


class DronePickingHeader(MouseInsideScrollEntry):

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.label = EveLabelLarge(text='', parent=self, left=0, top=0, state=uiconst.UI_DISABLED, color=None, maxLines=1, align=uiconst.TOPLEFT)

    def Load(self, node):
        selectable = node.numSelectable
        self.label.text = GetByLabel('UI/Fitting/FittingWindow/NumActiveDrones', numActive=node.numActive, numSelectable=selectable)


class DronePickingBoxCont(Container):
    boxSize = 14
    boxPadding = 1

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.boxClickedFunc = attributes.boxClickedFunc
        self.boxes = []

    def LoadBoxes(self, node):
        boxNum = node.maxActiveDrones
        if node.isDynamic:
            boxNum = 1
        self.Flush()
        self.boxes = []
        for i in xrange(boxNum):
            b = DroneBox(parent=self, padLeft=self.boxPadding, padRight=self.boxPadding, pos=(0,
             0,
             self.boxSize,
             0), align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, boxIdx=i)
            b.OnMouseEnter = (self.OnMouseEnterBox, i)
            b.OnMouseExit = (self.OnMouseEnterBox, None)
            b.OnClick = (self.OnClickBox, b)
            self.boxes.append(b)

        contWidth = boxNum * (self.boxSize + self.boxPadding * 2)
        self.width = contWidth
        self.height = self.boxSize
        self.SetNumActive(node)

    def OnMouseEnterBox(self, boxIdx):
        for b in self.boxes:
            if boxIdx is not None and b.boxIdx <= boxIdx and b.isSelectable:
                b.underlay.OnMouseEnter()
            else:
                b.underlay.OnMouseExit()

    def SetNumActive(self, node):
        numTotalThisType = len(node.itemIDs)
        numActive = node.numActive
        totalCanActivate = node.totalCanActivate
        bandwidthLeft = node.bandwidthLeft
        droneBandwidth = node.droneBandwidth
        maxActiveDrones = node.maxActiveDrones
        numAfterActive = 0
        for i, b in enumerate(self.boxes):
            if i >= numTotalThisType:
                b.SetUnavailableNoMoreItems()
                continue
            if i >= numActive:
                numAfterActive += 1
                if numAfterActive <= totalCanActivate:
                    if numAfterActive * droneBandwidth <= bandwidthLeft:
                        b.SetAvailableForSelection()
                    else:
                        b.SetUnavailableBandwidth()
                else:
                    b.SetUnavailableTooManyActive(maxActiveDrones)
            else:
                b.SetSelected()

    def OnClickBox(self, box):
        if self.boxClickedFunc:
            self.boxClickedFunc(box)


class DroneBox(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        boxIdx = attributes.boxIdx
        self.isSelectable = False
        self.boxIdx = boxIdx
        self.checkMark = Container(parent=self, align=uiconst.TOALL)
        texturePath = 'res:/UI/Texture/Shared/checkboxChecked.png'
        checkMark = Sprite(parent=self.checkMark, pos=(0, 0, 16, 16), name='self_ok', state=uiconst.UI_DISABLED, texturePath=texturePath, align=uiconst.CENTER)
        fill = FillThemeColored(parent=self.checkMark, padding=0, colorType=uiconst.COLORTYPE_UIHILIGHT)
        self.checkMark.opacity = 1.0
        self.checkMark.display = False
        self.underlay = DroneSelectorUnderlay(parent=self, padding=0)

    def SetUnavailableNoMoreItems(self):
        self.opacity = 0.1
        self.checkMark.display = False
        self.isSelectable = False
        self.hint = ''

    def SetUnavailableCantSelect(self):
        self.SetOpacity(0.5)
        self.checkMark.display = False
        self.isSelectable = False

    def SetUnavailableTooManyActive(self, maxDrones):
        self.SetUnavailableCantSelect()
        self.hint = GetByLabel('UI/Fitting/FittingWindow/DroneCannotBeSelectedHint', numActive=maxDrones)

    def SetUnavailableBandwidth(self):
        self.SetUnavailableCantSelect()
        self.hint = GetByLabel('UI/Fitting/FittingWindow/DroneCannotBeSelectedBandwidthHint')

    def SetAvailableForSelection(self):
        self.SetOpacity(1.0)
        self.checkMark.display = False
        self.isSelectable = True
        self.hint = GetByLabel('UI/Fitting/FittingWindow/SelectDroneHint')

    def SetSelected(self):
        self.SetOpacity(1.0)
        self.checkMark.display = True
        self.isSelectable = True
        self.hint = ''


class DroneSelectorUnderlay(RaisedUnderlay):
    OPACITY_IDLE = 0.4
    OPACITY_HOVER = 1.0
    OPACITY_SELECTED = 1.0
