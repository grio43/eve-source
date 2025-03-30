#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\inventory\plexVault.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst, fontconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from eve.client.script.environment import invControllers
from eve.client.script.ui.control.eveLabel import Label, EveCaptionMedium, EveLabelMedium
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.plex.textures import PLEX_128_GRADIENT_YELLOW, PLEX_SLOT
from eve.client.script.ui.services.menuSvcExtras.marketMenu import SellItems
from eve.client.script.ui.shared.container import _InvContBase
from eve.client.script.ui.shared.market.sellMulti import SellItems as SellItemsWnd
from eve.client.script.ui.shared.tooltip.item import InventoryItemTooltip
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipDescriptionWrapper
from eve.client.script.ui.shared.vgs.currency import OFFER_CURRENCY_PLEX
from eve.client.script.ui.shared.vgs.priceTag import PriceTagSmall
from eve.client.script.ui.util.uix import QtyPopup
from eve.client.script.ui.view.aurumstore.shared.offerpricing import get_min_offer_price_in_currency
from eve.common.lib.vgsConst import CATEGORYTAG_GAMETIME
import evelink.client
import evetypes
from eveexceptions import UserError
from fastcheckout.const import FROM_PLEX_VAULT
from inventorycommon import const as invconst
from inventorycommon.typeHelpers import GetAveragePrice
from inventorycommon.util import GetTypeVolume
import localization
import logging
import math
import signals
import uthread
from vgs.common.listeners import PlexWithdrawalListener, PlexDepositListener
logger = logging.getLogger(__name__)

class PlexVaultController(object):

    def __init__(self):
        self.onBalance = signals.Signal(signalName='onBalance')
        account = sm.GetService('vgsService').GetStore().GetAccount()
        account.accountAurumBalanceChanged.connect(self.onBalance)

    @property
    def balance(self):
        try:
            account = sm.GetService('vgsService').GetStore().GetAccount()
            return account.GetAurumBalance()
        except Exception:
            logger.warning('Failed to retrieve the PLEX balance', exc_info=True)
            return None

    def DepositPlex(self, itemID, quantity):
        locationID = session.stationid or session.structureid
        reference = sm.GetService('invCache').GetInventoryMgr().DepositPlexToVault(locationID, itemID, quantity)
        PlexDepositListener(session.userid, quantity, reference)

    def WithdrawPlex(self, inventory):
        if not inventory.DoesAcceptItem(self._GetFakePlexItem()):
            return
        savedLocationID = session.locationid
        quantity = self._PromptUserForQuantity(inventory)
        if quantity is None or quantity <= 0:
            return
        if session.locationid != savedLocationID:
            return
        if not inventory.CheckCanAdd(invconst.typePlex, quantity):
            return
        reference = sm.GetService('invCache').GetInventoryMgr().WithdrawPlexFromVault(quantity, inventory.itemID, inventory.locationFlag)
        PlexWithdrawalListener(session.userid, quantity, reference)

    def _GetFakePlexItem(self):
        return Bunch(typeID=invconst.typePlex, groupID=evetypes.GetGroupID(invconst.typePlex), categoryID=evetypes.GetCategoryID(invconst.typePlex), quantity=self.balance, singleton=0, stacksize=self.balance, ownerID=session.charid, isInPlexVault=True)

    def _PromptUserForQuantity(self, inventory):
        if inventory.hasCapacity:
            capacity = inventory.GetCapacity()
            remainingCapacity = capacity.capacity - capacity.used
            itemVolume = GetTypeVolume(invconst.typePlex, 1)
            maxQuantity = min(self.balance, int(remainingCapacity / itemVolume))
            if maxQuantity <= 0:
                raise UserError('NotEnoughCargoSpaceFor1Unit', {'type': invconst.typePlex,
                 'free': remainingCapacity,
                 'required': itemVolume})
        else:
            maxQuantity = self.balance
        if maxQuantity <= 0:
            return 0
        if maxQuantity != self.balance:
            errmsg = localization.GetByLabel('UI/Common/NoRoomForMore')
        else:
            errmsg = None
        ret = QtyPopup(maxvalue=maxQuantity, minvalue=0, setvalue=maxQuantity, hint=errmsg)
        if ret:
            return ret['qty']

    def OnDropData(self, dragObj, nodes):
        items = self._GatherDroppedPlexItemIds(nodes)
        for item in items:
            if item.groupID != invconst.groupCurrency:
                continue
            self.DepositPlex(item.itemID, item.stacksize)

    def _GatherDroppedPlexItemIds(self, nodes):
        items = []
        for node in nodes:
            if not hasattr(node, 'item') or node.item is None:
                continue
            if node.item.typeID != invconst.typePlex:
                continue
            if node.item.itemID is None:
                continue
            items.append(node.item)

        return items

    def GetItemMenu(self):
        return sm.GetService('menu').InvItemMenu(self._GetFakePlexItem())

    def SellPlex(self):
        if not session.stationid and not session.structureid:
            raise UserError('CantSellPLEXFromSpace')
        item = self._GetFakePlexItem()
        item.locationID = session.stationid or session.structureid
        item.flagID = invconst.flagHangar
        SellItems([item])


def IsPartiallyClipped(child):
    parent = child.parent
    cdx = child.displayX
    cdw = child.displayWidth
    sdw = parent.displayWidth
    if cdw > sdw or cdx + cdw > sdw:
        return True
    cdy = child.displayY
    cdh = child.displayHeight
    sdh = parent.displayHeight
    if cdh > sdh or cdy + cdh > sdh:
        return True
    return False


class PlexVault(_InvContBase):
    __invControllerClass__ = invControllers.PlexVault
    default_name = invconst.INVENTORY_ID_PLEX_VAULT
    default_availableViewModes = []

    def ApplyAttributes(self, attributes):
        self.controller = PlexVaultController()
        self._isResponsive = False
        super(PlexVault, self).ApplyAttributes(attributes)

    def ConstructUI(self):
        self.viewMode = 'icons'
        self.vault = Vault(parent=self, align=uiconst.TOTOP, padBottom=16, controller=self.controller)
        self.mainCont = Container(parent=self, align=uiconst.TOALL, clipChildren=True)
        self.vaultActionsScrollContainer = ScrollContainer(name='vaultActionsScrollContainer', parent=self.mainCont, align=uiconst.TOALL)
        self.actions = PlexVaultActions(parent=self.vaultActionsScrollContainer, align=uiconst.TOTOP, controller=self.controller, logContext=FROM_PLEX_VAULT)

    def IsQuickFilterEnabled(self):
        return False

    def IsCapacityEnabled(self):
        return False

    def IsEstimatedValueEnabled(self):
        return False

    def OnDropData(self, dragObj, nodes):
        self.controller.OnDropData(dragObj, nodes)

    def OnPostCfgDataChanged(self, what, data):
        pass

    def UpdateHint(self):
        pass

    def _ChangeViewMode(self):
        pass


class Vault(Container):
    default_height = 120
    default_state = uiconst.UI_NORMAL
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(Vault, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self._currentBalance = None
        self.Layout()
        uthread.new(self.UpdateBalance, animate=False)
        self.controller.onBalance.connect(self.OnBalanceUpdated)

    def Layout(self):
        centerCont = Container(parent=self, align=uiconst.CENTER, width=130, height=90)
        Sprite(bgParent=centerCont, texturePath=PLEX_SLOT, width=118, height=90, opacity=0.5)
        leftCont = Container(parent=self, align=uiconst.TOLEFT_PROP, width=0.5)
        balanceLabelCont = ContainerAutoSize(parent=leftCont, align=uiconst.CENTERRIGHT, left=60)
        self.balanceLabel = EveCaptionMedium(parent=balanceLabelCont, align=uiconst.TOPRIGHT)
        self.iskValueLabel = EveLabelMedium(parent=balanceLabelCont, align=uiconst.TOPRIGHT, top=26, opacity=0.6)
        self.item = PlexItem(parent=centerCont, align=uiconst.CENTER, controller=self.controller)
        MoreInfoIcon(parent=centerCont, align=uiconst.TOPRIGHT, hint=localization.GetByLabel('UI/PlexVault/HelpText'), opacity=0.5)

    def OnDragEnter(self, dragObj, nodes):
        pass

    def OnDragExit(self, dragObj, nodes):
        pass

    def OnDropData(self, dragObj, nodes):
        self.controller.OnDropData(dragObj, nodes)

    def UpdateBalance(self, animate = True):
        balance = self.controller.balance
        if balance is not None:
            if balance > 0:
                self.item.Show()
            else:
                self.item.Hide()
            if animate:
                animations.MorphScalar(self, 'balance', startVal=self.balance or 0, endVal=balance, curveType=uiconst.ANIM_SMOOTH, duration=1.2, callback=lambda : setattr(self, 'balance', balance))
            else:
                self.balance = balance
        else:
            self.item.Hide()
            self.balanceLabel.SetText(localization.GetByLabel('UI/PlexVault/PlexBalanceUnknown'))
            self.iskValueLabel.SetText(localization.GetByLabel('UI/PlexVault/PlexVaultConnectionLost'))

    @property
    def balance(self):
        return self._currentBalance

    @balance.setter
    def balance(self, balance):
        self._currentBalance = balance
        text = localization.GetByLabel('UI/PlexVault/PlexBalance', amount=balance)
        self.balanceLabel.SetText(text)
        price = GetAveragePrice(invconst.typePlex)
        if price:
            value = balance * price
            text = localization.GetByLabel('UI/PlexVault/EstimatedIskValue', value=value)
            self.iskValueLabel.SetText(text)

    def OnBalanceUpdated(self, *args, **kwargs):
        self.UpdateBalance()


class PlexItem(Container):
    default_width = 64
    default_height = 64
    default_state = uiconst.UI_NORMAL
    isDragObject = True

    def ApplyAttributes(self, attributes):
        super(PlexItem, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.ConstructLayout()
        uthread.new(self.UpdateBalance)
        self.controller.onBalance.connect(self.OnBalanceUpdated)

    def ConstructLayout(self):
        self.hilite = ListEntryUnderlay(bgParent=self, padding=(-6, -6, -5, -5))
        Sprite(bgParent=self, name='background', texturePath='res:/UI/Texture/classes/InvItem/bgNormal.png')
        Sprite(parent=self, name='icon', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=PLEX_128_GRADIENT_YELLOW)
        qtypar = ContainerAutoSize(parent=self, idx=0, name='qtypar', pos=(2, 48, 0, 0), align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, bgColor=(0, 0, 0, 0.9))
        self.quantityLabel = Label(parent=qtypar, maxLines=1, bold=True, fontsize=fontconst.EVE_SMALL_FONTSIZE, opacity=1.0, padding=(4, 1, 4, 0))

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_SELECT)
        super(PlexItem, self).OnClick(*args)

    def OnMouseEnter(self, *args):
        self.hilite.hovered = True
        PlaySound(uiconst.SOUND_ENTRY_HOVER)

    def OnMouseExit(self, *args):
        self.hilite.hovered = False

    def OnDropData(self, dragObj, nodes):
        self.controller.OnDropData(dragObj, nodes)

    def GetDragData(self):
        return [PlexDragData(self.controller)]

    def OnEndDrag(self, dragSource, dropLocation, dragData):
        if self is dragSource:
            wnd = SellItemsWnd.GetIfOpen()
            if dropLocation.IsUnder(wnd) or dropLocation is wnd:
                wnd.DropItems(None, dragData)

    def GetMenu(self):
        return self.controller.GetItemMenu()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if uicore.IsDragging():
            return
        InventoryItemTooltip(tooltipPanel=tooltipPanel, item=self.controller._GetFakePlexItem())

    def UpdateBalance(self):
        if self.controller.balance:
            self.quantityLabel.SetText(FmtAmt(self.controller.balance, fmt='ss'))

    def OnBalanceUpdated(self, *args, **kwargs):
        self.UpdateBalance()


class PlexDragData(object):
    __guid__ = None

    def __init__(self, controller):
        self.typeID = invconst.typePlex
        self.controller = controller

    @property
    def item(self):
        return self.controller._GetFakePlexItem()

    def get_link(self):
        return evelink.type_link(self.typeID)

    def LoadIcon(self, icon, parent, size):
        icon.LoadIconByTypeID(self.typeID, size=size)

    def WithdrawPlex(self, invController):
        self.controller.WithdrawPlex(invController)


def GetPriceForTypeIdFunctor(typeID):

    def f():
        store = sm.GetService('vgsService').GetStore()
        offers = store.SearchOffersByTypeIDs([typeID])
        if offers:
            return get_min_offer_price_in_currency(offers, OFFER_CURRENCY_PLEX)

    return f


def GetPriceForStoreCategoryIdFunctor(categoryID):

    def f():
        store = sm.GetService('vgsService').GetStore()
        categoryID = store.GetCategoryIdByCategoryTag(CATEGORYTAG_GAMETIME)
        offers = store.SearchOffersByCategoryIDs([categoryID])
        if offers:
            return get_min_offer_price_in_currency(offers, OFFER_CURRENCY_PLEX)

    return f


class PlexVaultActions(FlowContainer):
    default_name = 'PlexVaultActions'

    def __init__(self, controller, logContext, **kwargs):
        self.controller = controller
        self.logContext = logContext
        self.sellPlexForIskAction = None
        self.sellPlexForIskDisabledTooltip = None
        super(PlexVaultActions, self).__init__(centerContent=True, contentSpacing=(16, 16), **kwargs)
        self.controller.onBalance.connect(self.OnBalanceUpdated)
        self.Load()

    def Reload(self):
        self.Flush()
        self.Load()

    def Load(self):
        self.sellPlexForIskAction = PlexAction(parent=self, align=uiconst.NOALIGN, text=localization.GetByLabel('UI/PlexVault/SellPlexForIsk'), texturePath='res:/UI/Texture/classes/PlexVault/BuyISKforPLEX.png', onClick=self.SellPlex, onUpdate=self.UpdatePlexActionHeights)
        self.sellPlexForIskDisabledTooltip = TooltipDescriptionWrapper(description=localization.GetByLabel('UI/PlexVault/SellPlexForIskDisabledTooltipDescription'))
        PlexAction(parent=self, align=uiconst.NOALIGN, text=localization.GetByLabel('UI/PlexVault/AddOmegaTime'), texturePath='res:/UI/Texture/classes/PlexVault/UpgradeOmega.png', price=GetPriceForStoreCategoryIdFunctor(CATEGORYTAG_GAMETIME), onClick=self.BuyOmegaTime, onUpdate=self.UpdatePlexActionHeights)
        PlexAction(parent=self, align=uiconst.NOALIGN, text=localization.GetByLabel('UI/PlexVault/BuyMultipleTraining'), texturePath='res:/UI/Texture/Icons/multiple_training.png', price=GetPriceForTypeIdFunctor(invconst.typeMultiTrainingToken), onClick=self.BuyMultipleTraining, onUpdate=self.UpdatePlexActionHeights)
        PlexAction(parent=self, align=uiconst.NOALIGN, text=localization.GetByLabel('UI/PlexVault/OpenNewEdenStore'), texturePath='res:/UI/Texture/WindowIcons/NES.png', onClick=self.OpenNewEdenStore, onUpdate=self.UpdatePlexActionHeights)
        self.buyPlexAction = PlexAction(parent=self, align=uiconst.NOALIGN, text=localization.GetByLabel('UI/PlexVault/BuyPlexForMoney'), texturePath=PLEX_128_GRADIENT_YELLOW, onClick=self.BuyPlex, onUpdate=self.UpdatePlexActionHeights, isHighlighted=True)
        for action in self.children:
            action.ResetSize()

        self.OnBalanceUpdated(self.controller.balance)
        self.UnifyContentSize()

    def OnBalanceUpdated(self, balance, *args, **kwargs):
        if balance > 0:
            self.sellPlexForIskAction.Enable()
            self.sellPlexForIskAction.tooltipPanelClassInfo = None
        else:
            self.sellPlexForIskAction.tooltipPanelClassInfo = self.sellPlexForIskDisabledTooltip
            self.sellPlexForIskAction.Disable()

    def UpdatePlexActionHeights(self):
        for action in self.children:
            action.ResetSize()

        self.UnifyContentSize()

    def ShowBuyPlex(self):
        if self.buyPlexAction.IsVisible():
            return
        self.buyPlexAction.Show()
        self.buyPlexAction.opacity = 0.0
        animations.MorphScalar(self.buyPlexAction, 'width', startVal=0, endVal=self.buyPlexAction.default_width, duration=0.1)
        animations.FadeIn(self.buyPlexAction, duration=0.2, timeOffset=0.1)

    def HideBuyPlex(self, animate = True):
        if animate:
            animations.FadeOut(self.buyPlexAction, duration=0.2)
            animations.MorphScalar(self.buyPlexAction, 'width', startVal=self.buyPlexAction.default_width, endVal=0, duration=0.1, timeOffset=0.2, callback=self.buyPlexAction.Hide)
        else:
            self.buyPlexAction.Hide()

    def OpenNewEdenStore(self):
        uicore.cmd.ToggleAurumStore()

    def BuyOmegaTime(self):
        sm.GetService('vgsService').OpenStore(categoryTag=CATEGORYTAG_GAMETIME)

    def BuyMultipleTraining(self):
        sm.GetService('vgsService').OpenStore(typeIds=[invconst.typeSoulboundMultiTrainingToken])

    def BuyPlex(self):
        uicore.cmd.CmdBuyPlex(self.logContext)

    def ViewPlexMarketDetails(self):
        sm.StartService('marketutils').ShowMarketDetails(invconst.typePlex, None)

    def SellPlex(self):
        self.controller.SellPlex()


def center(text):
    return u'<center>{}</center>'.format(text)


class PlexAction(Container):
    default_name = 'PlexAction'
    default_state = uiconst.UI_NORMAL
    default_width = 80
    disabled_color = (1.0, 1.0, 1.0, 0.5)
    enabled_color = (1.0, 1.0, 1.0, 1.0)
    default_isHighlighted = False
    frameColor_enabled = (1.0, 0.65, 0.0, 1.0)
    frameColor_disabled = (1.0, 1.0, 1.0, 0.5)
    underlayColor = (1.0, 1.0, 1.0, 0.1)
    underlayColorHighlighted = (0.87, 0.61, 0.0, 0.2)

    def ApplyAttributes(self, attributes):
        super(PlexAction, self).ApplyAttributes(attributes)
        self.action = attributes.onClick
        self.price = attributes.price
        self.texturePath = attributes.texturePath
        self.text = attributes.text
        self.onUpdate = attributes.onUpdate
        self.isHighlighted = attributes.get('isHighlighted', self.default_isHighlighted)
        self.priceTag = None
        self.actionIcon = None
        self.actionLabelText = None
        self.frame = None
        self.underlay = None
        self.enabled = True
        self.Layout()

    def Layout(self):
        self.CreateFrame()
        self.CreateUnderlay()
        self.CreateTopContainer()
        self.CreateBottomContainer()

    def CreateFrame(self):
        if self.isHighlighted:
            self.frame = Frame(name='border_frame', bgParent=self, color=self.frameColor_enabled)

    def CreateUnderlay(self):
        self.underlay = Fill(bgParent=self, color=self.underlayColorHighlighted if self.isHighlighted else self.underlayColor)

    def CreateTopContainer(self):
        self.topContainer = ContainerAutoSize(name='topContainer', parent=self, align=uiconst.TOTOP)
        self.CreateIcon()
        self.CreateText()

    def CreateIcon(self):
        iconContainer = Container(parent=self.topContainer, align=uiconst.TOTOP, height=56)
        self.actionIcon = Sprite(parent=iconContainer, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self.texturePath, height=56, width=56)

    def CreateText(self):
        self.actionLabelText = EveLabelMedium(parent=self.topContainer, align=uiconst.TOTOP, text=center(self.text), padding=(8, 0, 8, 0))

    def CreateBottomContainer(self):
        self.bottomContainer = ContainerAutoSize(name='bottomContainer', parent=self, align=uiconst.TOBOTTOM)
        uthread.new(self.UpdatePrice)

    def UpdatePrice(self):
        if callable(self.price):
            price = self.price()
        else:
            price = self.price
        if price:
            if self.priceTag is None:
                self._ConstructPriceTag(price)
            else:
                self.priceTag.UpdatePrice(price)
        else:
            self._RemovePriceTag()
        if callable(self.onUpdate):
            self.onUpdate()

    def _ConstructPriceTag(self, price):
        priceCont = Container(parent=self.bottomContainer, align=uiconst.TOTOP, height=30, padding=(0, 0, 0, 2))
        self.priceTag = PriceTagSmall(parent=priceCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, price=price, currency=OFFER_CURRENCY_PLEX)

    def _RemovePriceTag(self):
        if self.priceTag:
            self.priceTag.Close()
            self.priceTag = None

    def OnClick(self, *args):
        if self.enabled:
            PlaySound(uiconst.SOUND_BUTTON_CLICK)
            self.action()

    def OnMouseEnter(self, *args):
        if self.enabled:
            PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def UpdateFrameColor(self):
        if self.frame:
            color = self.frameColor_enabled if self.enabled else self.frameColor_disabled
            self.frame.SetRGBA(*color)

    def Disable(self):
        if self.enabled:
            self.UpdateFrameColor()
            self.actionIcon.color = self.disabled_color
            self.actionLabelText.color = self.disabled_color
            self.enabled = False

    def Enable(self):
        if not self.enabled:
            self.UpdateFrameColor()
            self.actionIcon.color = self.enabled_color
            self.actionLabelText.color = self.enabled_color
            self.enabled = True

    def ResetSize(self):
        self.topContainer.EnableAutoSize()
        self.topContainer.DisableAutoSize()
        self.bottomContainer.EnableAutoSize()
        self.bottomContainer.DisableAutoSize()
        self.height = self.topContainer.height + self.bottomContainer.height
