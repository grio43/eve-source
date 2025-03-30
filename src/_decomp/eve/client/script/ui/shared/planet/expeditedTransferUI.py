#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\expeditedTransferUI.py
import math
import blue
import carbonui.const as uiconst
import eve.common.script.util.planetCommon as planetCommon
import evetypes
import localization
from carbon.common.script.util import timerstuff
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.status_bar import StatusBar
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.planet import planetCommon as planetCommonUI
from eve.client.script.ui.util import uix
from eveexceptions import UserError
from fsdBuiltData.common.planet import get_schematic_name

class ExpeditedTransferManagementWindow(Window):
    __guid__ = 'form.ExpeditedTransferManagementWindow'
    default_windowID = 'createTransfer'
    default_iconNum = 'res:/ui/Texture/WindowIcons/items.png'
    default_minSize = (500, 400)
    default_width = 800
    default_height = 500
    default_isStackable = False

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.planet = attributes.planet
        self.path = attributes.path
        if not self.path or len(self.path) < 2:
            raise UserError('CreateRouteTooShort')
        colony = self.planet.GetColony(session.charid)
        self.sourcePin = colony.GetPin(self.path[0])
        self.destinationPin = None
        minBandwidth = None
        prevID = None
        for pinID in self.path:
            pin = colony.GetPin(pinID)
            if not pin:
                raise UserError('RouteFailedValidationPinDoesNotExist')
            if prevID is None:
                prevID = pinID
                continue
            link = colony.GetLink(pin.id, prevID)
            if link is None:
                raise UserError('RouteFailedValidationLinkDoesNotExist')
            if minBandwidth is None or minBandwidth > link.GetTotalBandwidth():
                minBandwidth = link.GetTotalBandwidth()
            prevID = pinID

        self.availableBandwidth = minBandwidth
        sourceName = planetCommon.GetGenericPinName(self.sourcePin.typeID, self.sourcePin.id)
        self.SetCaption(localization.GetByLabel('UI/PI/Common/ExpeditedTransferFrom', sourceName=sourceName))
        self.ConstructLayout()
        self.SetSourcePinGaugeInfo()
        self.scope = uiconst.SCOPE_INGAME
        self.ResetPinContents()
        self.SetDestination(colony.GetPin(self.path[-1]))
        self.OnResizeUpdate()
        self.updateTimer = timerstuff.AutoTimer(100, self.SetNextTransferText)

    def ConstructLayout(self):
        self.bottomCont = Container(name='bottomCont', parent=self.sr.main, align=uiconst.TOBOTTOM, height=HEIGHT_NORMAL, padding=(0, 8, 0, 0))
        self.leftCont = Container(name='leftCont', parent=self.sr.main, align=uiconst.TOLEFT_PROP, width=0.33, clipChildren=True)
        self.middleCont = Container(name='middleCont', parent=self.sr.main, align=uiconst.TOLEFT_PROP, width=0.33, padding=(16, 0, 0, 0), clipChildren=True)
        self.rightCont = Container(name='rightCont', parent=self.sr.main, align=uiconst.TOALL, padding=(16, 0, 0, 0), clipChildren=True)
        colTopHeight = 80
        self.sourcePinHeader = Container(name='pinHeader', parent=self.leftCont, align=uiconst.TOTOP, height=colTopHeight)
        self.sourcePinList = Container(name='pinList', parent=self.leftCont, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.transferHeader = ContainerAutoSize(name='transferHeader', parent=self.middleCont, align=uiconst.TOTOP, height=colTopHeight)
        eveLabel.EveHeaderLarge(text=localization.GetByLabel('UI/PI/Common/ToBeTransferred'), parent=self.transferHeader, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.volumeText = eveLabel.EveLabelSmall(parent=self.transferHeader, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padTop=8)
        self.timeText = eveLabel.EveLabelSmall(parent=self.transferHeader, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/PI/Common/ExpeditedTransferProcessingHint'))
        self.cooldownTimeText = eveLabel.EveLabelSmall(parent=self.transferHeader, align=uiconst.TOTOP, hint=localization.GetByLabel('UI/PI/Common/CoolDownTimeHint'))
        self.transferListScroll = eveScroll.Scroll(parent=self.middleCont, name='transferList')
        self.transferListScroll.sr.id = 'transferListScroll'
        content = self.transferListScroll.sr.content
        content.OnDropData = self.OnTransferScrollDropData
        self.destPinHeader = Container(name='destPinHeader', parent=self.rightCont, align=uiconst.TOTOP, height=colTopHeight)
        self.destPinList = Container(name='destPinList', parent=self.rightCont, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.footerLeft = Container(name='footerLeft', parent=self.bottomCont, align=uiconst.TOLEFT_PROP, width=0.66)
        self.footerRight = Container(name='footerRight', parent=self.bottomCont, align=uiconst.TOALL)
        btns = [(localization.GetByLabel('UI/PI/Common/ExecuteTransfer'),
          self.GoForTransfer,
          (),
          None)]
        ButtonGroup(btns=btns, parent=self.footerRight)
        hint = localization.GetByLabel('UI/PI/Common/ExpeditedTransferSplitHint')
        btns = [(localization.GetByLabel('UI/PI/Common/Add'),
          self.AddBtnClicked,
          (),
          None,
          False,
          False,
          False,
          hint), (localization.GetByLabel('UI/PI/Common/Remove'),
          self.RemoveBtnClicked,
          (),
          None,
          False,
          False,
          False,
          hint)]
        ButtonGroup(btns=btns, parent=self.footerLeft)
        self.OnResizeUpdate()
        eveLabel.EveHeaderLarge(text=planetCommon.GetGenericPinName(self.sourcePin.typeID, self.sourcePin.id), parent=self.sourcePinHeader, align=uiconst.TOTOP, maxLines=1, state=uiconst.UI_NORMAL)
        self.sourcePinSubGauge = Gauge(parent=self.sourcePinHeader, value=0.0, color=planetCommonUI.PLANET_COLOR_STORAGE, label=localization.GetByLabel('UI/PI/Common/Capacity'), left=0, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padTop=8)
        self.sourcePinListScroll = eveScroll.Scroll(parent=self.sourcePinList, name='pinList')
        self.sourcePinListScroll.sr.id = 'sourcePinListScroll'
        content = self.sourcePinListScroll.sr.content
        content.OnDropData = self.OnSourceScrollDropData
        self.destPinText = eveLabel.EveHeaderLarge(text='', parent=self.destPinHeader, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, maxLines=1, padBottom=8)
        self.destPinSubText = eveLabel.EveLabelLarge(text='', parent=self.destPinHeader, align=uiconst.TOTOP, top=5, state=uiconst.UI_HIDDEN)
        self.destPinSubGauge = Gauge(parent=self.destPinHeader, value=0.0, color=planetCommonUI.PLANET_COLOR_STORAGE, label=localization.GetByLabel('UI/PI/Common/Capacity'), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, padTop=2)
        self.destPinListScroll = eveScroll.Scroll(parent=self.destPinList)
        self.destPinListScroll.sr.id = 'destPinListScroll'

    def OnTransferScrollDropData(self, dragObj, nodes, *args):
        if nodes[0].scroll.name == 'pinList':
            self.AddCommodity(nodes)

    def OnSourceScrollDropData(self, dragObj, nodes, *args):
        if nodes[0].scroll.name == 'transferList':
            self.RemoveCommodity(nodes)

    def AddBtnClicked(self, *args):
        selected = self.sourcePinListScroll.GetSelected()
        self.AddCommodity(selected)

    def RemoveBtnClicked(self, *args):
        selected = self.transferListScroll.GetSelected()
        self.RemoveCommodity(selected)

    def AddCommodity(self, selected):
        toMove = {}
        if len(selected) == 1 and uicore.uilib.Key(uiconst.VK_SHIFT):
            typeID = selected[0].typeID
            typeName = planetCommonUI.GetProductNameAndTier(typeID)
            ret = uix.QtyPopup(self.pinContents[typeID], 1, 1, None, localization.GetByLabel('UI/PI/Common/QuantityToTransfer', typeName=typeName))
            if ret and 'qty' in ret:
                toMove[typeID] = min(self.pinContents[typeID], max(1, ret['qty']))
        else:
            for entry in selected:
                toMove[entry.typeID] = self.pinContents[entry.typeID]

        if self.destPin.IsConsumer():
            toMove = self._ApplyConsumerFilter(toMove)
            if not toMove:
                raise UserError('ConsumerCantAcceptCommodities')
        elif self.destPin.IsStorage():
            toMove = self._ApplyMaxAmountFilter(toMove)
        for typeID, qty in toMove.iteritems():
            self.pinContents[typeID] -= qty
            if self.pinContents[typeID] <= 0:
                del self.pinContents[typeID]
            if typeID not in self.transferContents:
                self.transferContents[typeID] = 0
            self.transferContents[typeID] += qty

        self.RefreshLists()

    def _ApplyConsumerFilter(self, toMove):
        newToMove = {}
        for typeID, qty in toMove.iteritems():
            remainingSpace = self.destPin.CanAccept(typeID, -1)
            alreadyInTransfer = self.transferContents.get(typeID, 0)
            if remainingSpace:
                amount = min(remainingSpace - alreadyInTransfer, qty)
                if amount > 0:
                    newToMove[typeID] = amount

        return newToMove

    def _ApplyMaxAmountFilter(self, toMove):
        availableVolume = self.destPin.GetCapacity() - self.destPin.capacityUsed
        availableVolume -= planetCommon.GetCommodityTotalVolume(self.transferContents)
        transferVolume = planetCommon.GetCommodityTotalVolume(toMove)
        if transferVolume >= availableVolume:
            newToMove = {}
            if len(toMove) == 1:
                for typeID, quantity in toMove.iteritems():
                    commodityVolume = evetypes.GetVolume(typeID)
                    maxAmount = int(math.floor(availableVolume / commodityVolume))
                    newToMove[typeID] = maxAmount

            eve.Message('ExpeditedTransferNotEnoughSpace')
            return newToMove
        else:
            return toMove

    def RemoveCommodity(self, selected):
        toMove = {}
        if len(selected) == 1 and uicore.uilib.Key(uiconst.VK_SHIFT):
            typeID = selected[0].typeID
            typeName = planetCommonUI.GetProductNameAndTier(typeID)
            ret = uix.QtyPopup(self.transferContents[typeID], 1, 1, None, localization.GetByLabel('UI/PI/Common/QuantityToRemove', typeName=typeName))
            if ret and 'qty' in ret:
                toMove[typeID] = min(self.transferContents[typeID], max(1, ret['qty']))
        else:
            for entry in selected:
                toMove[entry.typeID] = self.transferContents[entry.typeID]

        for typeID, qty in toMove.iteritems():
            self.transferContents[typeID] -= qty
            if self.transferContents[typeID] <= 0:
                del self.transferContents[typeID]
            if typeID not in self.pinContents:
                self.pinContents[typeID] = 0
            self.pinContents[typeID] += qty

        self.RefreshLists()

    def GoForTransfer(self, *args):
        if len(self.transferContents) < 1:
            raise UserError('PleaseSelectCommoditiesToTransfer')
        for typeID, quantity in self.transferContents.iteritems():
            if typeID not in self.sourcePin.contents:
                raise UserError('RouteFailedValidationExpeditedSourceLacksCommodity', {'typeName': evetypes.GetName(typeID)})
            if quantity > self.sourcePin.contents[typeID]:
                raise UserError('RouteFailedValidationExpeditedSourceLacksCommodityQty', {'typeName': evetypes.GetName(typeID),
                 'qty': quantity})

        if not self.sourcePin.CanTransfer(self.transferContents):
            raise UserError('RouteFailedValidationExpeditedSourceNotReady')
        if len(self.transferContents) > 0:
            self.ShowLoad()
            try:
                self.planet.TransferCommodities(self.path, self.transferContents)
            finally:
                self.ResetPinContents()
                self.HideLoad()

            self.CloseByUser()

    def ResetPinContents(self, *args):
        self.pinContents = self.sourcePin.contents.copy()
        self.transferContents = {}
        self.RefreshLists()

    def RefreshLists(self, *args):
        pinListItems = []
        for typeID, qty in self.pinContents.iteritems():
            pinListItems.append(GetFromClass(ExpeditedDraggableItem, {'itemID': None,
             'typeID': typeID,
             'label': '<t>%d<t>%s' % (qty, planetCommonUI.GetProductNameAndTier(typeID)),
             'getIcon': 1,
             'quantity': qty,
             'OnDropData': self.OnSourceScrollDropData}))

        transferListItems = []
        for typeID, qty in self.transferContents.iteritems():
            transferListItems.append(GetFromClass(ExpeditedDraggableItem, {'itemID': None,
             'typeID': typeID,
             'label': '<t>%d<t>%s' % (qty, planetCommonUI.GetProductNameAndTier(typeID)),
             'getIcon': 1,
             'quantity': qty,
             'OnDropData': self.OnTransferScrollDropData}))

        self.sourcePinListScroll.Load(contentList=pinListItems, noContentHint=localization.GetByLabel('UI/PI/Common/StorehouseIsEmpty'), headers=[localization.GetByLabel('UI/Common/Type'), localization.GetByLabel('UI/Common/Quantity'), localization.GetByLabel('UI/Common/Name')])
        self.transferListScroll.Load(contentList=transferListItems, noContentHint=localization.GetByLabel('UI/PI/Common/NoItemsFound'), headers=[localization.GetByLabel('UI/Common/Type'), localization.GetByLabel('UI/Common/Quantity'), localization.GetByLabel('UI/Common/Name')])
        transferVolume = planetCommon.GetCommodityTotalVolume(self.transferContents)
        self.volumeText.text = localization.GetByLabel('UI/PI/Common/VolumeAmount', amount=transferVolume)
        self.SetNextTransferText()
        self.SetCooldownTimeText()

    def SetNextTransferText(self):
        if self.sourcePin.lastRunTime is None or self.sourcePin.lastRunTime <= blue.os.GetWallclockTime():
            self.timeText.text = localization.GetByLabel('UI/PI/Common/NextTransferNow')
        else:
            self.timeText.text = localization.GetByLabel('UI/PI/Common/NextTransferTime', time=self.sourcePin.lastRunTime - blue.os.GetWallclockTime())

    def SetCooldownTimeText(self):
        time = planetCommon.GetExpeditedTransferTime(self.availableBandwidth, self.transferContents)
        self.cooldownTimeText.text = localization.GetByLabel('UI/PI/Common/CooldownTime', time=time)

    def SetSourcePinGaugeInfo(self):
        self.sourcePinSubGauge.state = uiconst.UI_DISABLED
        self.sourcePinSubGauge.SetText(localization.GetByLabel('UI/PI/Common/Capacity'))
        usageRatio = self.sourcePin.capacityUsed / self.sourcePin.GetCapacity()
        self.sourcePinSubGauge.SetSubText(localization.GetByLabel('UI/PI/Common/CapacityProportionUsed', capacityUsed=self.sourcePin.capacityUsed, capacityMax=self.sourcePin.GetCapacity(), percentage=usageRatio * 100.0))
        self.sourcePinSubGauge.SetValue(usageRatio)

    def RefreshDestinationPinInfo(self):
        self.destPinSubText.state = uiconst.UI_HIDDEN
        self.destPinSubGauge.state = uiconst.UI_HIDDEN
        if not self.destPin:
            self.destPinText.text = localization.GetByLabel('UI/PI/Common/NoOriginSelected')
            self.destPinSubText.text = ''
            self.destPinSubText.state = uiconst.UI_DISABLED
            self.destPinListScroll.Load(contentList=[], noContentHint=localization.GetByLabel('UI/PI/Common/NoOriginSelected'))
            return
        self.destPinText.text = localization.GetByLabel('UI/PI/Common/TransferDestinationName', typeName=planetCommon.GetGenericPinName(self.destPin.typeID, self.destPin.id))
        scrollHeaders = []
        scrollContents = []
        scrollNoContentText = ''
        if self.destPin.IsConsumer():
            self.destPinSubText.state = uiconst.UI_DISABLED
            if self.destPin.schematicID is None:
                self.destPinSubText.text = localization.GetByLabel('UI/PI/Common/NoSchematicInstalled')
                scrollNoContentText = localization.GetByLabel('UI/PI/Common/NoSchematicInstalled')
            else:
                self.destPinSubText.text = localization.GetByLabel('UI/PI/Common/SchematicName', schematicName=get_schematic_name(self.destPin.schematicID))
                scrollHeaders = []
                demands = self.destPin.GetConsumables()
                for typeID, qty in demands.iteritems():
                    remainingSpace = self.destPin.CanAccept(typeID, -1)
                    load = qty - remainingSpace
                    fraction = load / float(qty)
                    entry = GetFromClass(StatusBar, {'label': planetCommonUI.GetProductNameAndTier(typeID),
                     'text': localization.GetByLabel('UI/PI/Common/UnitQuantityAndDemand', quantity=load, demand=qty),
                     'value': fraction,
                     'iconID': evetypes.GetIconID(typeID)})
                    scrollContents.append(entry)

        elif self.destPin.IsStorage():
            self.destPinSubGauge.state = uiconst.UI_DISABLED
            self.destPinSubGauge.SetText(localization.GetByLabel('UI/PI/Common/Capacity'))
            usageRatio = self.destPin.capacityUsed / self.destPin.GetCapacity()
            self.destPinSubGauge.SetSubText(localization.GetByLabel('UI/PI/Common/CapacityProportionUsed', capacityUsed=self.destPin.capacityUsed, capacityMax=self.destPin.GetCapacity(), percentage=usageRatio * 100.0))
            self.destPinSubGauge.SetValue(usageRatio)
            scrollHeaders = [localization.GetByLabel('UI/Common/Type'), localization.GetByLabel('UI/Common/Quantity'), localization.GetByLabel('UI/Common/Name')]
            contents = self.destPin.GetContents()
            for typeID, qty in contents.iteritems():
                lbl = '<t>%d<t>%s' % (qty, planetCommonUI.GetProductNameAndTier(typeID))
                scrollContents.append(GetFromClass(ExpeditedDraggableItem, {'itemID': None,
                 'typeID': typeID,
                 'label': lbl,
                 'getIcon': 1,
                 'quantity': qty}))

            scrollNoContentText = localization.GetByLabel('UI/PI/Common/StorehouseIsEmpty')
        self.destPinListScroll.Load(contentList=scrollContents, headers=scrollHeaders, noContentHint=scrollNoContentText)

    def SetDestination(self, destinationPin):
        self.destPin = destinationPin
        self.RefreshDestinationPinInfo()


class ExpeditedDraggableItem(Item):
    __guid__ = 'listentry.CustomsItem'

    def LoadTooltipPanel(self, tooltipPanel, *args):
        planetCommonUI.LoadProductTooltipPanel(tooltipPanel, self.sr.node.typeID)
