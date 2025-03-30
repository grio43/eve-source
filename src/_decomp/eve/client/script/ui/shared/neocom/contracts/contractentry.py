#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\contracts\contractentry.py
import blue
import carbonui.const as uiconst
import evetypes
import localization
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbon.common.script.util.format import FmtAmt, FmtDate
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveIcon, eveLabel
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.util import uix
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.util.contractutils import GetContractIcon, GetContractTimeLeftText, FmtISKWithDescription
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from eve.common.script.util.contractscommon import GetContractTitle, GetContractTypeText, GetCurrentBid
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.shared.tooltip.blueprints import AddBlueprintInfo
from eve.client.script.ui.shared.tooltip.dynamicItem import AddDynamicItemAttributes
from eve.common.script.util import contractscommon as cc
from eveexceptions import UserError
from eveprefs import prefs
from eveservices.menu import GetMenuService
from menu import MenuLabel

class ContractStartPageEntry(ContainerAutoSize):
    default_padTop = 8
    default_padBottom = 8
    default_alignMode = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        super(ContractStartPageEntry, self).ApplyAttributes(attributes)
        node = attributes.node
        self.icon = eveIcon.Icon(parent=self, size=32, ignoreSize=True, left=4)
        self.header = eveLabel.EveLabelLarge(parent=self, padLeft=50, state=uiconst.UI_NORMAL, align=uiconst.TOTOP)
        self.text = eveLabel.EveLabelMedium(parent=self, padLeft=50, state=uiconst.UI_NORMAL, align=uiconst.TOTOP)
        if node.isSmall:
            self.header.Hide()
            self.icon.SetSize(16, 16)
            self.icon.LoadIcon(node.icon, ignoreSize=True)
            if node.header:
                self.text.text = node.header + '<br>' + node.text
            else:
                self.text.text = node.text
        else:
            self.header.state = uiconst.UI_NORMAL
            self.header.text = node.header
            self.text.text = node.text
            self.icon.SetSize(32, 32)
            self.icon.LoadIcon(node.icon, ignoreSize=True)


class ContractEntry(SE_BaseClassCore):
    __guid__ = 'listentry.ContractEntry'
    isDragObject = True
    OnSelectCallback = None

    def GetMenu(self):
        m = []
        c = self.sr.node.contract
        node = self.sr.node
        m.append((MenuLabel('UI/Contracts/ContractEntry/ViewContract'), self.ViewContract, (node,)))
        if c.startStationID:
            typeID = self.GetStationType(c.startStationID)
            m += [(MenuLabel('UI/Contracts/ContractEntry/PickupStation'), ('isDynamic', GetMenuService().CelestialMenu, (c.startStationID,
                None,
                None,
                typeID)))]
        if c.endStationID and c.endStationID != c.startStationID:
            typeID = self.GetStationType(c.endStationID)
            m += [(MenuLabel('UI/Contracts/ContractEntry/DropOffStation'), ('isDynamic', GetMenuService().CelestialMenu, (c.endStationID,
                None,
                None,
                typeID)))]
        if c.type == const.conTypeAuction and c.issuerID != eve.session.charid and c.status == const.conStatusOutstanding and c.dateExpired > blue.os.GetWallclockTime():
            m.append((MenuLabel('UI/Contracts/ContractEntry/PlaceBid'), self.PlaceBid, (node,)))
        if self.sr.node.Get('canDismiss', False):
            m.append((MenuLabel('UI/Contracts/ContractEntry/Dismiss'), self.Dismiss, (node,)))
        if self.sr.node.Get('canGetItems', False):
            m.append((MenuLabel('UI/Contracts/ContractEntry/GetItems'), self.GetItems, (node,)))
        if self.sr.node.Get('canGetMoney', False):
            m.append((MenuLabel('UI/Contracts/ContractEntry/GetMoney'), self.GetMoney, (node,)))
        if self.sr.node.Get('canIgnore', True) and c.issuerID != eve.session.charid:
            m.append((MenuLabel('UI/Contracts/ContractEntry/IgnoreFromThisIssuer'), self.AddIgnore, (node,)))
        typeID = self.sr.node.Get('typeID', None)
        if typeID and self.sr.node.contract.type != const.conTypeCourier:
            m.append(None)
            m.append((MenuLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, (typeID,)))
            if evetypes.GetMarketGroupID(typeID) is not None:
                sm.GetService('marketutils').AddMarketDetailsMenuOption(m, typeID)
        m.append(None)
        if c.issuerID == eve.session.charid:
            m.append((MenuLabel('UI/Contracts/ContractEntry/Delete'), self.Delete, (node,)))
        if session.role & ROLE_GML > 0:
            m.append(('GM - contractID: %s' % node.contract.contractID, blue.pyos.SetClipboardData, (str(node.contract.contractID),)))
            m.append(('GM - issuerID: %s' % node.contract.issuerID, blue.pyos.SetClipboardData, (str(node.contract.issuerID),)))
            m.append(('GM - Expire now', self._ExpireContract, (node.contract.contractID,)))
        return m

    @staticmethod
    def GetStationType(stationID):
        if idCheckers.IsStation(stationID):
            return sm.GetService('ui').GetStationStaticInfo(stationID).stationTypeID
        return sm.GetService('structureDirectory').GetStructureInfo(stationID).typeID

    def NoEvent(self, *args):
        pass

    def _ExpireContract(self, contractID):
        sm.ProxySvc('contractProxy').GM_ExpireContract(contractID)

    def FindMore(self, typeID, *args):
        sm.GetService('contracts').OpenAvailableTab(7, reset=True, typeID=typeID)

    def ViewContract(self, node = None, *args):
        node = node if node != None else self.sr.node
        sm.GetService('contracts').ShowContract(node.contract.contractID)

    def Delete(self, node = None, *args):
        node = node if node != None else self.sr.node
        sm.GetService('contracts').DeleteContract(node.contract.contractID)

    def PlaceBid(self, node = None, *args):
        node = node if node != None else self.sr.node
        if sm.GetService('contracts').PlaceBid(node.contract.contractID):
            self.Reload()

    def Dismiss(self, node = None, *args):
        node = node if node != None else self.sr.node
        if sm.GetService('contracts').DeleteNotification(node.contractID, node.Get('forCorp', False)):
            node.scroll.RemoveEntries([node])

    def GetItems(self, node = None, *args):
        node = node if node != None else self.sr.node
        if sm.GetService('contracts').FinishAuction(node.contract.contractID, isIssuer=False):
            node.scroll.RemoveEntries([node])

    def GetMoney(self, node = None, *args):
        node = node if node != None else self.sr.node
        if sm.GetService('contracts').FinishAuction(node.contract.contractID, isIssuer=True):
            node.scroll.RemoveEntries([node])

    def AddIgnore(self, node = None, *args):
        node = node if node != None else self.sr.node
        issuerID = node.contract.issuerID
        if node.contract.forCorp:
            issuerID = node.contract.issuerCorpID
        sm.GetService('contracts').AddIgnore(issuerID)

    def OnDblClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.ViewContract(*args)

    def GetDragData(self, *args):
        if self and not self.destroyed:
            return self.sr.node.scroll.GetSelectedNodes(self.sr.node)

    def OnSelect(self, *args):
        if getattr(self, 'OnSelectCallback', None):
            apply(self.OnSelectCallback, args)

    def _OnClose(self, *args):
        self.updatetimer = None

    def OnClick(self, *args):
        self.sr.node.scroll.SelectNode(self.sr.node)
        self.OnSelect(self)

    def Reload(self, *args):
        contract = sm.GetService('contracts').GetContract(self.sr.node.contractID)
        self.sr.node.contract = contract.contract
        self.sr.node.contractItems = contract.items
        self.sr.node.bids = contract.bids
        self.Load(self.sr.node)


class ContractEntrySmall(ContractEntry):
    __guid__ = 'listentry.ContractEntrySmall'

    def Startup(self, *etc):
        self.sr.label = eveLabel.EveLabelMedium(text='', parent=self, left=5, state=uiconst.UI_DISABLED, color=None, maxLines=1, align=uiconst.CENTERLEFT)
        self.sr.line = Container(name='lineparent', align=uiconst.TOBOTTOM, parent=self, height=1)

    def Load(self, node):
        self.sr.node = node
        c = node.contract
        self.sr.node.contractID = c.contractID
        self.sr.node.solarSystemID = c.startSolarSystemID
        items = node.contractItems
        name = GetContractTitle(c, items)
        self.sr.label.text = self.sr.node.label = node.label
        self.OnSelectCallback = node.Get('callback', None)
        if node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        self.state = uiconst.UI_NORMAL
        self.sr.claiming = 0
        self.sr.node.name = name

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        node = self.sr.node
        wrapWidth = 250
        c = node.contract
        items = node.contractItems
        jmps = None
        if c.startSolarSystemID > 0:
            n = sm.GetService('clientPathfinderService').GetAutopilotJumpCount(session.solarsystemid2, c.startSolarSystemID)
            if c.startStationID in {eve.session.stationid, eve.session.structureid}:
                jmps = localization.GetByLabel('UI/Generic/CurrentStation')
            elif c.startSolarSystemID == eve.session.solarsystemid2:
                jmps = localization.GetByLabel('UI/Generic/CurrentSystem')
            elif n == 1:
                jmps = localization.GetByLabel('UI/Contracts/OneJumpAway')
            elif n <= cc.NUMJUMPS_UNREACHABLE:
                jmps = localization.GetByLabel('UI/Contracts/ContractEntry/NumJumpsAway', numJumps=n)
            else:
                jmps = localization.GetByLabel('UI/Generic/NoGateToGateRoute')
        hintLine = localization.GetByLabel('UI/Contracts/ContractEntry/ContractTypeWithType', contractType=GetContractTypeText(c.type))
        tooltipPanel.AddLabelMedium(text=hintLine, wrapWidth=wrapWidth)
        if c.title != '':
            hintLine = localization.GetByLabel('UI/Contracts/ContractEntry/IssuerDescriptionWithDescription', description=c.title)
            tooltipPanel.AddLabelMedium(text=hintLine, wrapWidth=wrapWidth)
        if jmps:
            hintLine = localization.GetByLabel('UI/Contracts/ContractEntry/ContractLocation', location=c.startSolarSystemID, numJumpsInfo=jmps)
        else:
            labelText = localization.GetByLabel('UI/Contracts/ContractEntry/MenuLocation')
            hintLine = localization.GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=labelText)
        tooltipPanel.AddLabelMedium(text=hintLine, wrapWidth=wrapWidth)
        if c.assigneeID > 0:
            labelText = localization.GetByLabel('UI/Contracts/ContractEntry/PrivateContract')
            boldLabelText = localization.GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=labelText)
            tooltipPanel.AddLabelMedium(text=boldLabelText, wrapWidth=wrapWidth)
        if c.type in [const.conTypeAuction, const.conTypeItemExchange] and len(items) > 0:
            itemList = []
            itemReqList = []
            numItems = 0
            numItemsReq = 0
            for e in items:
                if e.inCrate:
                    itemInfo = cfg.FormatConvert(const.UE_TYPEIDANDQUANTITY, e.itemTypeID, max(1, e.quantity))
                    itemList.append(itemInfo)
                    numItems += 1
                else:
                    itemReqInfo = cfg.FormatConvert(const.UE_TYPEIDANDQUANTITY, e.itemTypeID, max(1, e.quantity))
                    itemReqList.append(itemReqInfo)
                    numItemsReq += 1

            if len(itemList) >= 2:
                itemList.append(localization.GetByLabel('UI/Common/MoreWithTrailing'))
            if len(itemReqList) >= 2:
                itemReqList.append(localization.GetByLabel('UI/Common/MoreWithTrailing'))
            if itemList:
                itemsText = localization.GetByLabel('UI/Contracts/ContractEntry/ItemsWithItemList', itemsString='')
                tooltipPanel.AddLabelMedium(text=itemsText, wrapWidth=wrapWidth)
                for eachItem in itemList:
                    tooltipPanel.AddLabelMedium(text=eachItem, wrapWidth=250, padLeft=10)

            else:
                itemsText = localization.GetByLabel('UI/Contracts/ContractEntry/ItemsWithItemList', itemsString=localization.GetByLabel('UI/Contracts/ContractEntry/NoneParen'))
                tooltipPanel.AddLabelMedium(text=itemsText, wrapWidth=wrapWidth)
            if len(itemReqList) > 0:
                itemsReqText = localization.GetByLabel('UI/Contracts/ContractEntry/ItemsRequiredWithItemList', reqItemsString='')
                tooltipPanel.AddLabelMedium(text=itemsReqText)
                for eachItem in itemReqList:
                    tooltipPanel.AddLabelMedium(text=eachItem, wrapWidth=wrapWidth, padLeft=10)

            if len(itemList) >= 2 or len(itemReqList) >= 2:
                tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/Contracts/ContractEntry/OpenForItems'), wrapWidth=250)

    def GetHeight(_self, *args):
        node, width = args
        node.height = 19
        return node.height

    @classmethod
    def GetCopyData(cls, node):
        return node.label


class ContractItemSelect(Item):
    __guid__ = 'listentry.ContractItemSelect'

    def ApplyAttributes(self, attributes):
        Item.ApplyAttributes(self, attributes)
        self.sr.overlay = Container(name='overlay', align=uiconst.TOPLEFT, parent=self, height=1)
        self.sr.tlicon = None

    def Startup(self, *args):
        Item.Startup(self, args)
        self.sr.checkbox = Checkbox(align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(6, 4, 0, 0), callback=self.CheckBoxChange, parent=self, idx=0)

    def Load(self, args):
        Item.Load(self, args)
        data = self.sr.node
        self.sr.checkbox.SetChecked(data.checked, 0)
        self.sr.icon.left = 24
        self.sr.label.left = self.sr.icon.left + self.sr.icon.width + 4
        self.sr.icon.state = uiconst.UI_PICKCHILDREN

    def CheckBoxChange(self, *args):
        self.sr.node.checked = self.sr.checkbox.checked
        self.sr.node.OnChange(self.sr.checkbox.GetValue(), self.sr.node.itemData)

    def OnClick(self, *args):
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        lastSelected = self.sr.node.scroll.sr.lastSelected
        if lastSelected is None:
            shift = 0
        idx = self.sr.node.idx
        self.sr.checkbox.ToggleState()
        isChecked = self.sr.checkbox.GetValue()
        if shift > 0:
            r = [lastSelected, self.sr.node.idx]
            r.sort()
            for node in self.sr.node.scroll.GetNodes():
                if node.idx > r[0] and node.idx <= r[1]:
                    node.checked = isChecked
                    if node.panel:
                        node.OnChange(node.panel.sr.checkbox)
                        node.panel.sr.checkbox.SetChecked(isChecked)

        self.sr.node.scroll.sr.lastSelected = idx

    def GetHeight(self, *args):
        node, width = args
        node.height = 28
        return node.height

    def GetMenu(self):
        m = []
        if self.sr.node.quantity > 1:
            m.append((MenuLabel('UI/Generic/SplitStack'), self.SplitStack))
        m.extend(GetMenuService().GetMenuFromItemIDTypeID(self.sr.node.itemID, self.sr.node.typeID))
        return m

    def SplitStack(self):
        maxQty = self.sr.node.quantity
        msg = localization.GetByLabel('UI/Common/HowManyItems')
        ret = uix.QtyPopup(int(maxQty), 1, 1, msg)
        if ret:
            sm.GetService('contracts').SplitStack(self.sr.node.stationID, self.sr.node.itemID, ret['qty'], self.sr.node.forCorp, self.sr.node.flag)


class ContractEntrySearch(ContractEntry):
    __guid__ = 'listentry.ContractEntrySearch'
    iconSize = 32
    iconMargin = 2
    lineHeight = 10
    labelMargin = 6
    reqItemEntryHeight = 16
    entryHeight = 10

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.sr.contractParent = Container(parent=self, name='contractParent', align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN, padTop=2)
        self.sr.contractIconParent = Container(parent=self.sr.contractParent, name='contractIconParent', align=uiconst.TOLEFT, width=self.iconSize + 5)
        self.sr.icon = ItemIcon(parent=self.sr.contractIconParent, pos=(2, 2, 32, 32), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        subPar = Container(parent=self.sr.contractParent, name='contractLabelClipper', state=uiconst.UI_DISABLED, align=uiconst.TOALL, clipChildren=True, padLeft=2)
        self.sr.contractLabel = eveLabel.EveLabelMedium(parent=subPar, left=self.labelMargin, align=uiconst.TOTOP, padRight=const.defaultPadding)

    def Load(self, node):
        self.sr.node = node
        c = node.contract
        numJumps = node.numJumps
        self.sr.node.contractID = c.contractID
        self.sr.node.solarSystemID = c.startSolarSystemID
        self.sr.node.name = GetContractTitle(c, node.contractItems)
        if prefs.GetValue('contractsSimpleView', 0):
            self.sr.icon.state = uiconst.UI_HIDDEN
            self.sr.contractIconParent.width = 6
        else:
            self.sr.icon.state = uiconst.UI_DISABLED
            self.sr.contractIconParent.width = self.iconSize + 5
        label = self.GetContractLabel()
        self.sr.contractLabel.SetText(label)
        if c.type in [const.conTypeAuction, const.conTypeItemExchange] and len(node.contractItems) == 1:
            typeID = node.contractItems[0].itemTypeID
            self.sr.icon.SetTypeID(typeID, isCopy=getattr(node.contractItems[0], 'copy', False))
        else:
            self.sr.icon.SetTexturePath(GetContractIcon(node.contract.type))
        numJumpsTxt = ''
        if numJumps == 0:
            if c.startStationID in {session.stationid, session.structureid}:
                numJumpsTxt = localization.GetByLabel('UI/Generic/CurrentStation')
            elif c.startSolarSystemID == session.solarsystemid2:
                numJumpsTxt = localization.GetByLabel('UI/Generic/CurrentSystem')
        elif numJumps == 1:
            numJumpsTxt = localization.GetByLabel('UI/Contracts/OneJumpAway')
        elif numJumps <= cc.NUMJUMPS_UNREACHABLE:
            numJumpsTxt = localization.GetByLabel('UI/Contracts/ContractEntry/NumJumpsAway', numJumps=numJumps)
        else:
            numJumpsTxt = '<color=0xffff6666>%s</color>' % localization.GetByLabel('UI/Generic/NoGateToGateRoute').upper()
        self.sr.jumpsLabel.SetText(numJumpsTxt)
        self.sr.timeLeftLabel.SetText(GetContractTimeLeftText(c))

    def GetContractLabel(self):
        node = self.sr.node
        contract = node.contract
        name = GetContractTitle(contract, node.contractItems)
        label = '<color=0xFFFFA600>%s</color>' % name
        if len(node.contractItems) == 1:
            item = node.contractItems[0]
            if evetypes.GetCategoryID(item.itemTypeID) == const.categoryBlueprint:
                if item.copy:
                    label += ' (%s)' % localization.GetByLabel('UI/Generic/Copy').lower()
                else:
                    label += ' (%s)' % localization.GetByLabel('UI/Generic/Original').lower()
        if contract.type == const.conTypeAuction:
            label += ' (%s)' % localization.GetByLabel('UI/Contracts/Auction').lower()
        return label

    def MakeTextLabel(self, name):
        subPar = Container(name='%sParent' % name, parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=False)
        label = eveLabel.EveLabelMedium(parent=subPar, name='%sLabel' % name, left=self.labelMargin, align=uiconst.TOLEFT, padTop=2)
        subPar.sr.label = label
        setattr(self.sr, '%sLabel' % name, label)

    def GetLocationText(self, solarSystemID, regionID, stationID = None):
        solarSystemName = cfg.evelocations.Get(solarSystemID).name
        dot = sm.GetService('contracts').GetSystemSecurityDot(solarSystemID)
        txt = '%s %s' % (dot, solarSystemName)
        if stationID and not idCheckers.IsStation(stationID):
            txt += '<color=0xffff6666> &lt;!&gt; </color>'
        if regionID and regionID != session.regionid:
            txt += '<br><color=0xffff6666>  %s</color>' % cfg.evelocations.Get(regionID).name
        return txt

    def GetMenu(self):
        m = ContractEntry.GetMenu(self)
        m += [(MenuLabel('UI/Contracts/ContractEntry/FindRelated'), ('isDynamic', sm.GetService('contracts').GetRelatedMenu, (self.sr.node.contract, self.sr.node.Get('typeID', None), False)))]
        return m

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        wrapWidth = 250
        node = self.sr.node
        c = node.contract
        privateTxt = '<font size=10 color=red> %s</font>' % localization.GetByLabel('UI/Contracts/ContractEntry/PrivateProperty')
        label = self.GetContractLabel()
        boldLabel = localization.GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=label)
        tooltipPanel.AddLabelMedium(text=boldLabel, wrapWidth=wrapWidth)
        hintLine = localization.GetByLabel('UI/Contracts/ContractEntry/ContractTypeWithType', contractType=GetContractTypeText(c.type))
        tooltipPanel.AddLabelMedium(text=hintLine, wrapWidth=wrapWidth)
        if node.numJumps <= cc.NUMJUMPS_UNREACHABLE:
            numJumpsInfo = node.numJumps
        else:
            numJumpsInfo = '<color=0xffff6666>%s</color>' % localization.GetByLabel('UI/Generic/NoGateToGateRoute').upper()
        hintLine = localization.GetByLabel('UI/Contracts/ContractEntry/ContractLocation', location=c.startSolarSystemID, numJumpsInfo=numJumpsInfo)
        if not idCheckers.IsStation(c.startStationID):
            hintLine += privateTxt
        if c.type == const.conTypeCourier and not idCheckers.IsStation(c.endStationID):
            hintLine += '<br>' + localization.GetByLabel('UI/Contracts/ContractEntry/DropOffStation') + privateTxt
        tooltipPanel.AddLabelMedium(text=hintLine, wrapWidth=wrapWidth)
        if c.forCorp:
            issuerID = c.issuerCorpID
        else:
            issuerID = c.issuerID
        issuer = cfg.eveowners.Get(issuerID)
        hintLine = localization.GetByLabel('UI/Contracts/ContractEntry/IssuerWithName', issuerName=issuer.name)
        tooltipPanel.AddLabelMedium(text=hintLine, wrapWidth=wrapWidth)
        if c.title != '':
            hintLine = localization.GetByLabel('UI/Contracts/ContractEntry/IssuerDescriptionWithDescription', description=c.title)
            tooltipPanel.AddLabelMedium(text=hintLine, wrapWidth=wrapWidth)
        contractItems = node.contractItems
        if contractItems < 1:
            return
        if c.type in [const.conTypeAuction, const.conTypeItemExchange]:
            itemList = []
            itemReqList = []
            numItems = 0
            numItemsReq = 0
            for e in contractItems:
                if e.inCrate:
                    itemInfo = cfg.FormatConvert(const.UE_TYPEIDANDQUANTITY, e.itemTypeID, max(1, e.quantity))
                    itemList.append(itemInfo)
                    numItems += 1
                else:
                    itemReqInfo = cfg.FormatConvert(const.UE_TYPEIDANDQUANTITY, e.itemTypeID, max(1, e.quantity))
                    itemReqList.append(itemReqInfo)
                    numItemsReq += 1

            if len(itemList) >= 2:
                itemList.append(localization.GetByLabel('UI/Common/MoreWithTrailing'))
            if len(itemReqList) >= 2:
                itemReqList.append(localization.GetByLabel('UI/Common/MoreWithTrailing'))
            if itemList:
                itemListText = localization.GetByLabel('UI/Contracts/ContractEntry/ItemsWithItemList', itemsString='')
                tooltipPanel.AddLabelMedium(text=itemListText, wrapWidth=wrapWidth)
                for eachItem in itemList:
                    tooltipPanel.AddLabelMedium(text=eachItem, wrapWidth=250, padLeft=10)

            else:
                itemListText = localization.GetByLabel('UI/Contracts/ContractEntry/ItemsWithItemList', itemsString=localization.GetByLabel('UI/Contracts/ContractEntry/NoneParen'))
                tooltipPanel.AddLabelMedium(text=itemListText, wrapWidth=wrapWidth)
            if len(itemReqList) > 0:
                itemsReq = localization.GetByLabel('UI/Contracts/ContractEntry/ItemsRequiredWithItemList', reqItemsString='')
                tooltipPanel.AddLabelMedium(text=itemsReq, wrapWidth=wrapWidth)
                for eachItem in itemReqList:
                    tooltipPanel.AddLabelMedium(text=eachItem, wrapWidth=wrapWidth, padLeft=10)

            if len(itemList) >= 2 or len(itemReqList) >= 2:
                tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/Contracts/ContractEntry/OpenForItems'), wrapWidth=wrapWidth)
            if len(contractItems) == 1:
                margin = list(tooltipPanel.margin)
                margin[3] = 12
                tooltipPanel.margin = tuple(margin)
                tooltipPanel.AddLabelMedium(text=self.hint)
                itemInContract = contractItems[0]
                try:
                    AddDynamicItemAttributes(tooltipPanel, itemInContract.itemID, itemInContract.itemTypeID, spacerHeight=8)
                except UserError as e:
                    if e.msg != 'ItemNotFound':
                        raise

                category = evetypes.GetCategoryID(itemInContract.itemTypeID)
                if category == const.categoryBlueprint or category == const.categoryAncientRelic:
                    AddBlueprintInfo(tooltipPanel, itemInContract.itemID, itemInContract.itemTypeID, spacerHeight=8)

    def OnColumnResize(self, newCols):
        for container, width in zip(self.children, newCols):
            if not isinstance(container, Container):
                continue
            container.width = width
            label = container.sr.label
            if label and label != self.sr.contractLabel:
                label.width = width - 14

    def GetDynamicHeight(_self, *args):
        text = localization.GetByLabel('UI/Contracts/ContractEntry/WantToBuy')
        textWidth, textHeight = eveLabel.EveLabelMedium.MeasureTextSize(text)
        if not prefs.GetValue('contractsSimpleView', 0):
            textHeight *= 2
        return textHeight + const.defaultPadding

    def OnMouseEnter(self, *args):
        ContractEntry.OnMouseEnter(self, *args)
        self.sr.icon.OnMouseEnter()

    def OnMouseExit(self, *args):
        ContractEntry.OnMouseExit(self, *args)
        self.sr.icon.OnMouseExit()


class ContractEntrySearchItemExchange(ContractEntrySearch):
    __guid__ = 'listentry.ContractEntrySearchItemExchange'

    def ApplyAttributes(self, attributes):
        ContractEntrySearch.ApplyAttributes(self, attributes)
        self.MakeTextLabel('location')
        self.MakeTextLabel('price')
        self.MakeTextLabel('jumps')
        self.MakeTextLabel('timeLeft')
        self.MakeTextLabel('issuer')
        self.MakeTextLabel('created')
        self.MakeTextLabel('info')

    def Load(self, node):
        ContractEntrySearch.Load(self, node)
        c = node.contract
        p = c.price
        self.sr.locationLabel.text = self.GetLocationText(c.startSolarSystemID, c.startRegionID, c.startStationID)
        if p == 0 and c.reward > 0:
            txt = '<color=0xff999999>-%s</color>' % FmtISKWithDescription(c.reward, True)
        else:
            txt = '<color=white>%s</color>' % FmtISKWithDescription(p, True)
        self.sr.priceLabel.SetText(txt)
        if localization.GetByLabel('UI/Contracts/ContractEntry/WantToBuy') not in self.sr.contractLabel.text:
            if len([ e for e in node.contractItems if not e.inCrate ]) >= 1:
                self.sr.priceLabel.text += '<br>[%s]' % localization.GetByLabel('UI/Generic/Items')
        if c.type == const.conTypeAuction:
            self.sr.priceLabel.text = '<color=white>%s</color>' % FmtISKWithDescription(GetCurrentBid(c, node.bids), True)
            if c.collateral:
                self.sr.priceLabel.text += '<br>(%s)' % FmtISKWithDescription(c.collateral, True)
            else:
                self.sr.priceLabel.text += '<br>(%s)' % localization.GetByLabel('UI/Contracts/ContractEntry/NoBuyoutPrice')
        self.sr.issuerLabel.text = node.issuer
        self.sr.createdLabel.text = '%s' % FmtDate(node.dateIssued, 'ss')
        self.sr.infoLabel.text = c.title


class ContractEntrySearchAuction(ContractEntrySearch):
    __guid__ = 'listentry.ContractEntrySearchAuction'

    def ApplyAttributes(self, attributes):
        ContractEntrySearch.ApplyAttributes(self, attributes)
        self.MakeTextLabel('location')
        self.MakeTextLabel('currentBid')
        self.MakeTextLabel('buyout')
        self.MakeTextLabel('bids')
        self.MakeTextLabel('jumps')
        self.MakeTextLabel('timeLeft')
        self.MakeTextLabel('issuer')
        self.MakeTextLabel('created')
        self.MakeTextLabel('info')

    def Load(self, node):
        ContractEntrySearch.Load(self, node)
        c = node.contract
        self.sr.locationLabel.text = self.GetLocationText(c.startSolarSystemID, c.startRegionID, c.startStationID)
        self.sr.currentBidLabel.text = '<color=white>%s</color>' % FmtISKWithDescription(GetCurrentBid(c, node.bids), True)
        self.sr.buyoutLabel.text = '%s' % ['<color=0xff999999>' + localization.GetByLabel('UI/Contracts/ContractEntry/NoneParen') + '</color>', '<color=white>' + FmtISKWithDescription(c.collateral, True) + '</color>'][c.collateral > 0]
        self.sr.bidsLabel.text = '%s' % node.searchresult.numBids
        self.sr.issuerLabel.text = node.issuer
        self.sr.createdLabel.text = '%s' % FmtDate(node.dateIssued, 'ss')
        self.sr.infoLabel.text = c.title


class ContractEntrySearchCourier(ContractEntrySearch):
    __guid__ = 'listentry.ContractEntrySearchCourier'

    def ApplyAttributes(self, attributes):
        ContractEntrySearch.ApplyAttributes(self, attributes)
        self.MakeTextLabel('to')
        self.MakeTextLabel('volume')
        self.MakeTextLabel('reward')
        self.MakeTextLabel('collateral')
        self.MakeTextLabel('route')
        self.MakeTextLabel('jumps')
        self.MakeTextLabel('timeLeft')
        self.MakeTextLabel('issuer')
        self.MakeTextLabel('created')
        self.MakeTextLabel('info')

    def Load(self, node):
        ContractEntrySearch.Load(self, node)
        c = node.contract
        self.sr.contractLabel.text = '<color=0xFFFFA600>%s</color>' % self.GetLocationText(c.startSolarSystemID, c.startRegionID, c.startStationID)
        self.sr.toLabel.text = '<color=0xFFFFA600>%s</color>' % self.GetLocationText(c.endSolarSystemID, None, c.endStationID)
        routeLength = node.routeLength
        volumeText = localization.GetByLabel('UI/Contracts/ContractsWindow/NumericVolume', volume=FmtAmt(c.volume, showFraction=0 if c.volume > 10 else 2))
        self.sr.volumeLabel.text = volumeText
        self.sr.rewardLabel.text = '<color=white>%s</color>' % [localization.GetByLabel('UI/Contracts/ContractEntry/NoneParen'), FmtISKWithDescription(c.reward, True)][c.reward > 0]
        self.sr.collateralLabel.text = '<color=white>%s</color>' % [localization.GetByLabel('UI/Contracts/ContractEntry/NoneParen'), FmtISKWithDescription(c.collateral, True)][c.collateral > 0]
        if int(routeLength) > cc.NUMJUMPS_UNREACHABLE:
            numJumpsTxt = '<color=0xffff6666>%s</color>' % localization.GetByLabel('UI/Generic/NoGateToGateRoute').upper()
        elif routeLength == 0:
            numJumpsTxt = localization.GetByLabel('UI/Contracts/ContractEntry/SameSystem')
        elif routeLength == 1:
            numJumpsTxt = localization.GetByLabel('UI/Contracts/ContractEntry/NextSystem')
        else:
            numJumpsTxt = localization.GetByLabel('UI/Contracts/ContractEntry/NumJumps', numJumps=routeLength)
        self.sr.routeLabel.text = '<color=white>%s</color>' % numJumpsTxt
        self.sr.issuerLabel.text = node.issuer
        self.sr.createdLabel.text = '%s' % FmtDate(node.dateIssued, 'ss')
        self.sr.infoLabel.text = c.title
