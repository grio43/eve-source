#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\pvptrade\pvptradewnd.py
import carbonui.const as uiconst
import eveformat
import eveicon
import evetypes
import localization
import uthread
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui import TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.environment import invControllers as invCtrl
from eve.client.script.ui.control import primaryButton
from carbonui.control.button import Button
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium
from carbonui.control.window import Window
from eve.client.script.ui.shared.container import _InvContBase, InvContViewBtns
from eve.client.script.ui.shared.tooltip.item import InventoryItemTooltip
from eve.client.script.ui.util import uix
from eve.common.lib import appConst
from eveexceptions import UserError
from inventorycommon.const import VIEWMODE_DETAILS, VIEWMODE_LIST, VIEWMODE_ICONS
from localization import GetByLabel
from menucheckers import ItemChecker
from utillib import KeyVal

class PVPTrade(Window):
    __guid__ = 'form.PVPTrade'
    default_minSize = (300, 410)
    default_width = 460
    default_height = 500
    default_scope = uiconst.SCOPE_DOCKED

    def ApplyAttributes(self, attributes):
        super(PVPTrade, self).ApplyAttributes(attributes)
        self.tradeSession = attributes.tradeSession
        tradeItems = attributes.tradeItems
        buttonParent = ButtonGroup(name='buttonParent', parent=self.content, align=uiconst.TOBOTTOM, padTop=16, button_size_mode=ButtonSizeMode.STRETCH)
        acceptBtn = primaryButton.PrimaryButton(parent=buttonParent, label=localization.GetByLabel('UI/PVPTrade/Accept'), func=self.OnClickAccept)
        self.acceptBtnController = acceptBtn.controller
        Button(parent=buttonParent, label=localization.GetByLabel('UI/Common/Buttons/Cancel'), func=self.Cancel)
        sessionData = self.tradeSession.List()
        herID = sessionData.traders[not sessionData.traders.index(session.charid)]
        self.sr.herinfo = cfg.eveowners.Get(herID)
        mainCont = Container(name='mainCont', parent=self.sr.main)
        myCont = DragResizeCont(parent=mainCont, align=uiconst.TOTOP_PROP, defaultSize=0.5, minSize=0.35, maxSize=0.65, settingsID='PVPtradeResizeCont', show_line=True)
        herCont = Container(parent=mainCont, align=uiconst.TOALL)
        self.sr.my = my = PlayerTrade(name='InventoryContainer_myTrade', parent=myCont, align=uiconst.TOALL, itemID=sessionData.tradeContainerID, ownerID=session.charid, tradeSession=self.tradeSession, state=uiconst.UI_PICKCHILDREN, tradeItems=tradeItems, tradeWindow=self)
        self.sr.myAccept = my.acceptIcon
        self.sr.myMoney = my.moneyLabel
        self.sr.myMoney.amount = 0
        self.sr.her = her = PlayerTrade(name='InventoryContainer_herTrade', parent=herCont, align=uiconst.TOALL, itemID=sessionData.tradeContainerID, ownerID=herID, tradeSession=self.tradeSession, state=uiconst.UI_PICKCHILDREN, tradeWindow=self)
        self.sr.herAccept = her.acceptIcon
        self.sr.herMoney = her.moneyLabel
        self.sr.herMoney.amount = 0
        self.sr.her.invController.OnDropData = self.sr.my.invController.OnDropData
        Button(name='OfferMoneyButton', parent=my.topCont, label=localization.GetByLabel('UI/PVPTrade/OfferMoney'), func=self.OnClickOfferMoney, args=None, idx=0, align=uiconst.TOPRIGHT)
        self.sr.myIx = sessionData.traders.index(session.charid)
        self.sr.herIx = sessionData.traders.index(herID)
        self.OnMoneyOffer([0, 0])
        self.SetCaption(self.GetWindowCaptionText())

    def _OnClose(self, *args):
        if self and getattr(self, 'sr', None):
            if self.sr.my:
                self.sr.my.Close()
            if self.sr.her:
                self.sr.her.Close()
        try:
            self.tradeSession.Abort()
        except AttributeError:
            pass

    def Cancel(self, *etc):
        if self.tradeSession and eve.Message('ConfirmCancelTrade', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
            if self and not self.destroyed and hasattr(self, 'sr'):
                tmp = self.tradeSession
                self.tradeSession = None
                tmp.Abort()
            else:
                eve.Message('TradeNotCanceled')

    CloseByUser = Cancel

    def OnClickAccept(self, *etc):
        myItems = filter(None, self.sr.my.items)
        herItems = filter(None, self.sr.her.items)
        self.acceptBtnController.is_enabled = False
        moneys = [self.sr.myMoney.amount]
        moneys.insert(self.sr.herIx, self.sr.herMoney.amount)
        manifest = KeyVal(tradeContainerID=self.sr.my.itemID, money=moneys, tradeItems=set(myItems) | set(herItems))
        shipsAreCool = False
        for i in manifest.tradeItems:
            if evetypes.GetCategoryIDByGroup(i.groupID) == appConst.categoryShip:
                if i.ownerID != session.charid and not shipsAreCool:
                    if eve.Message('TradeShipWarning', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                        return self.OnTradeOfferReset()
                    shipsAreCool = True

        try:
            self.tradeSession.MakeOffer(manifest)
        except UserError:
            self.OnTradeOfferReset()
            raise
        except AttributeError:
            self.OnCancel()

    def GetWindowCaptionText(self):
        return localization.GetByLabel('UI/PVPTrade/TradeWith', otherParty=self.sr.herinfo.id)

    def OnTradeOfferReset(self):
        self.sr.myAccept.display = False
        self.sr.herAccept.display = False
        self.acceptBtnController.is_enabled = True

    def OnStateToggle(self, states):
        myDisplayState = bool(states[self.sr.myIx])
        self.sr.myAccept.display = myDisplayState
        herDisplayState = bool(states[self.sr.herIx])
        self.sr.herAccept.display = herDisplayState
        if myDisplayState:
            self.acceptBtnController.is_enabled = False
        else:
            self.acceptBtnController.is_enabled = True
        if states[0] and states[1]:
            self.sr.my.invReady = 0
            self.sr.her.invReady = 0
            self.Close()

    def OnMoneyOffer(self, money):
        self.acceptBtnController.is_enabled = True
        myMoney = eveformat.isk(money[self.sr.myIx])
        if money[self.sr.myIx] > 0:
            myMoney = eveformat.color(myMoney, color=TextColor.DANGER)
        else:
            myMoney = eveformat.color(myMoney, color=TextColor.SECONDARY)
        herMoney = eveformat.isk(money[self.sr.herIx])
        if money[self.sr.herIx] > 0:
            herMoney = eveformat.color(herMoney, color=TextColor.SUCCESS)
        else:
            herMoney = eveformat.color(herMoney, color=TextColor.SECONDARY)
        self.sr.myMoney.text = localization.GetByLabel('UI/PVPTrade/MyCharacterOffers', formattedAmount=myMoney)
        self.sr.myMoney.amount = money[self.sr.myIx]
        self.sr.herMoney.text = localization.GetByLabel('UI/PVPTrade/OtherCharacterOffers', formattedAmount=herMoney)
        self.sr.herMoney.amount = money[self.sr.herIx]
        self.OnStateToggle([0, 0])

    def OnClickOfferMoney(self, *etc):
        ret = uix.QtyPopup(sm.GetService('wallet').GetWealth(), self.sr.myMoney.amount, 100, digits=2)
        if ret is not None and self is not None and not self.destroyed:
            self.tradeSession.OfferMoney(ret['qty'])

    def OnTradeComplete(self, items):
        eve.Message('TradeComplete', {'name': self.sr.herinfo.name})
        self.sr.my.invReady = 0
        self.sr.her.invReady = 0
        self.Close()

    def OnCancel(self):
        eve.Message('TradeCancel', {'name': self.sr.herinfo.name})
        self.sr.my.invReady = 0
        self.sr.her.invReady = 0
        self.tradeSession = None
        self.Close()


class PlayerTrade(_InvContBase):
    __guid__ = 'invCont.PlayerTrade'
    __invControllerClass__ = invCtrl.PlayerTrade
    default_containerViewMode = VIEWMODE_DETAILS

    def ApplyAttributes(self, attributes):
        _InvContBase.ApplyAttributes(self, attributes)
        tradeItems = attributes.tradeItems
        ownerID = attributes.ownerID
        ownerName = cfg.eveowners.Get(ownerID).name
        self.tradeWindow = attributes.tradeWindow
        self.topCont = Container(parent=self, align=uiconst.TOTOP, height=64, idx=0, padBottom=8)
        myImgCont = Sprite(parent=self.topCont, align=uiconst.TOLEFT, width=64, idx=0, texturePath='res:/UI/Texture/silhouette_64.png')
        sm.GetService('photo').GetPortrait(ownerID, 64, myImgCont)
        myImgCont.OnClick = (self.ShowCharInfo, ownerID)
        myImgCont.hint = ownerName
        ownerLink = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=ownerName, info=('showinfo', appConst.typeCharacter, ownerID))
        EveLabelLarge(text=ownerLink, parent=self.topCont, left=72, state=uiconst.UI_NORMAL)
        self.acceptIcon = Sprite(parent=self.topCont, align=uiconst.TOPLEFT, left=72, top=24, width=16, height=16, state=uiconst.UI_NORMAL, texturePath=eveicon.checkmark, hint=GetByLabel('UI/PVPTrade/AcceptedHint', name=ownerName), color=eveColor.SUCCESS_GREEN)
        InvContViewBtns(parent=self.topCont, align=uiconst.BOTTOMRIGHT, controller=self)
        self.moneyLabel = EveLabelMedium(parent=self.topCont, left=72, align=uiconst.BOTTOMLEFT)
        hiddenHeaders = uix.GetInvItemDefaultHiddenHeaders()
        hiddenHeaders += [localization.GetByLabel('UI/Inventory/ItemSize'),
         localization.GetByLabel('UI/Inventory/ItemSlot'),
         localization.GetByLabel('UI/Inventory/ItemVolume'),
         localization.GetByLabel('UI/Contracts/ContractsWindow/EstPrice')]
        self.scroll.SetColumnsHiddenByDefault(hiddenHeaders)
        if tradeItems:
            uthread.new(self.AddStartingItems, tradeItems)

    def AddStartingItems(self, tradeItems):
        self.invController.OnDropData(tradeItems)

    def AddItem(self, rec, index = None, fromWhere = None):
        if self.IsItemPresent(rec.itemID):
            return
        self.tradeWindow.OnTradeOfferReset()
        super(PlayerTrade, self).AddItem(rec, index, fromWhere)

    def _GetInvController(self, attributes):
        return self.__invControllerClass__(itemID=attributes.itemID, ownerID=attributes.ownerID, tradeSession=attributes.tradeSession)

    def ShowCharInfo(self, ownerID, *args):
        sm.GetService('info').ShowInfo(appConst.typeCharacter, ownerID)

    def GetItemData(self, rec, scrollID = None):
        node = _InvContBase.GetItemData(self, rec, scrollID)
        node.labelFunc = GetItemLabel
        node.LoadTooltipPanel = LoadTooltipPanelForTrade
        return node


def LoadTooltipPanelForTrade(tooltipPanel, owner, *args):
    if uicore.IsDragging():
        return
    node = owner.sr.node
    rec = node.rec
    itemChecker = ItemChecker(rec)
    if itemChecker.IsAlphaSkillInjector() or itemChecker.IsSkillInjector() or itemChecker.IsNonDiminishingInjectionBooster():
        return owner.LoadTooltipPanel(tooltipPanel)
    InventoryItemTradeTooltip(tooltipPanel=tooltipPanel, item=rec)


def GetItemLabel(rec, data, new = 0):
    if getattr(data, 'label', None) and data.viewMode == VIEWMODE_ICONS and not new:
        return data.label
    name = evetypes.GetName(rec.typeID)
    itemName = uix.GetItemName(rec, data)
    if name != itemName:
        name = GetByLabel('UI/PVPTrade/TypeNameAndItemName', typeName=name, itemName=itemName)
    if data.viewMode in (VIEWMODE_LIST, VIEWMODE_DETAILS):
        label = uix.GetItemLabelForListOrDetails(rec, data, name)
        data.label = label
    else:
        data.label = '<center>%s' % name
    return data.label


class InventoryItemTradeTooltip(InventoryItemTooltip):

    def AddName(self):
        typeName = evetypes.GetName(self.item.typeID)
        itemName = uix.GetItemName(self.item)
        text = GetByLabel('UI/PVPTrade/TypeNameWithName', typeName=typeName)
        self.panel.AddLabelMedium(text=text, colSpan=2)
        text = GetByLabel('UI/PVPTrade/ItemNameWithName', itemName=itemName)
        self.panel.AddLabelMedium(text=text, colSpan=2)
        qtyText = GetByLabel('UI/PVPTrade/QuantityWithQty', qty=self.item.stacksize)
        self.panel.AddLabelMedium(text=qtyText, colSpan=2)
