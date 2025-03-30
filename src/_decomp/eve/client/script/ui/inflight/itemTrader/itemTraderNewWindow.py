#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\itemTrader\itemTraderNewWindow.py
import carbonui.const as uiconst
import eveformat
import evetypes
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbon.common.script.util.format import FmtAmt
from carbonui import TextColor
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.window import Window
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.gradientSprite import GradientSprite, GradientConst
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.sprite import Sprite
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.line import Line
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.collapseLine import ANIM_DURATION, CollapseLine
from eve.client.script.ui.inflight.itemTrader.confirmWnd import ItemTraderDialogPopupWindow
from eve.client.script.ui.inflight.itemTrader.itemTraderController import ItemTraderController
from eve.client.script.ui.inflight.itemTrader.offerBrowser import OfferBrowser
from eve.client.script.ui.inflight.itemTrader.outputCont import ItemTraderOutputCont
from eve.client.script.ui.inflight.itemTrader.topBanner import TopBanner
from eveexceptions import ExceptionEater
from eveservices.menu import GetMenuService
from localization import GetByLabel
from signals.signalUtil import ChangeSignalConnect
import carbonui

class ItemTraderWindow(Window):
    __guid__ = 'form.ItemTraderWindow'
    __notifyevents__ = ['OnItemTraderProcessed']
    default_minSize = [620, 375]
    default_windowID = 'itemTrader'
    default_captionLabelPath = 'UI/Inflight/SpaceComponents/ItemTrader/ItemTrader'
    default_isStackable = False
    default_isCollapseable = False
    input_isk = 0
    multiplier = 0
    input_container = None
    output_container = None
    trade_items_action_button = None
    quantity_numeric_input = None

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.item_trader = attributes.item_trader
        self.itemTraderController = ItemTraderController(self.item_trader)
        self.ConstructContainers()
        self.UpdateMinSize()
        self.LoadRecipe()
        self.ChangeSignalConnection()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.itemTraderController.on_recipe_clicked, self.OnRecipeClicked),
         (self.itemTraderController.affordableSetting.on_change, self.OnFilterChanged),
         (self.collapseLine.on_section_expand, self.OnCollapseLineExpand),
         (self.collapseLine.on_section_collapse, self.OnCollapseLineCollapse)]
        ChangeSignalConnect(signalAndCallback, connect)

    def OnItemTraderProcessed(self, itemID, recipe):
        if itemID != self.item_trader.itemID:
            return
        self.LoadRecipe(recipe)

    def ConstructContainers(self):
        action_container = Container(name='actionContainer', parent=self.content, height=51, align=uiconst.TOBOTTOM)
        self.resizeCont = DragResizeCont(name='resizeCont', parent=self.content, align=uiconst.TOLEFT, minSize=0, maxSize=300, defaultSize=200, onDragCallback=self.OnDividerMove, onResizeCallback=self.OnResizeDivider, settingsID='itemTraderBrowserWidth')
        self.leftPanel = PanelUnderlay(name='leftPanelUnderLay', parent=self.resizeCont, align=uiconst.TOALL)
        self.offerBrowser = OfferBrowser(parent=self.leftPanel, item_trader=self.item_trader, itemTraderController=self.itemTraderController)
        singleOffer = len(self.itemTraderController.GetRecipes()) < 2
        self.collapseLine = CollapseLine(parent=self.content, align=uiconst.TOLEFT, collapsingSection=self.resizeCont, collapsingSectionWidth=self.resizeCont.width, isCollapsed=singleOffer or None, padRight=8, settingKey='item_trader_collapse')
        if singleOffer:
            self.collapseLine.display = False
            self.leftPanel.display = False
        self.topBanner = TopBanner(parent=self.content, itemTraderController=self.itemTraderController)
        self.mainContent = Container(name='mainContent', parent=self.content, align=uiconst.TOALL, clipChildren=True)
        body_container = Container(name='bodyContainer', parent=self.mainContent, height=208, align=uiconst.VERTICALLY_CENTERED)
        OUTPUT_WIDTH = 280
        self.input_container = ScrollContainer(name='input_container', parent=body_container, padRight=OUTPUT_WIDTH)
        self.output_containerParent = ItemTraderOutputCont(name='output_containerParent', parent=body_container, padding=(0, 0, 0, 0), align=uiconst.TORIGHT_NOPUSH, pos=(-30,
         0,
         OUTPUT_WIDTH,
         10), itemTraderController=self.itemTraderController)
        Line(parent=action_container, align=uiconst.TOTOP)
        action_inner_container = Container(name='tradeActionInnerContainer', parent=action_container, padding=8)
        quantity_numeric_input_container = Container(parent=action_inner_container, align=uiconst.TORIGHT, width=80)
        self.quantity_numeric_input = SingleLineEditInteger(parent=quantity_numeric_input_container, name='', width=60, align=uiconst.CENTERRIGHT, OnChange=self.OnNumericInputChange, dataType=int)
        numTradesCont = Container(parent=action_inner_container, align=uiconst.TORIGHT, width=100)
        input_label = carbonui.TextBody(parent=numTradesCont, text=GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/NumTrades'), align=uiconst.CENTERRIGHT, color=TextColor.SECONDARY)
        self.trade_items_action_button = Button(name='tradeItemsActionButton', parent=action_inner_container, label=GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/TradeItems'), align=uiconst.CENTERRIGHT, func=self.OnButtonTradeItemsClicked)
        quantity_numeric_input_container.left = self.trade_items_action_button.width + 16

    def OnFilterChanged(self, *args):
        self.offerBrowser.LoadRecipes()

    def OnRecipeClicked(self, recipe):
        self.LoadRecipe(recipe)

    def LoadRecipe(self, recipe = None):
        if recipe is None:
            recipe = self.itemTraderController.selectedRecipe
        self.itemTraderController.UpdateCargoQty()
        self.multiplier = 1
        self.AddInputItems(recipe)
        self.AddOutputItems(recipe)
        self.topBanner.LoadRecipe(recipe)
        self.quantity_numeric_input.SetValue(self.multiplier)
        maxValue = self.itemTraderController.GetInputMaxMultiplier() or 1
        self.quantity_numeric_input.SetMaxValue(maxValue)
        self.UpdateBtnState()

    def AddInputItems(self, recipe):
        item_height = 60
        items = recipe.inputItems
        self.input_container.Flush()
        self.input_entries = {}
        input_label_padding_top = 12
        if len(items) == 1:
            input_label_padding_top = 46
        input_label = carbonui.TextBody(parent=self.input_container, text=GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/RequiredItems'), padding=(20,
         input_label_padding_top,
         20,
         6), align=uiconst.TOTOP, color=TextColor.SECONDARY)
        for type_id, quantity in items.iteritems():
            item_quantity = self.multiplier * quantity
            item_container = InputEntry(parent=self.input_container, itemTraderController=self.itemTraderController, type_id=type_id, qty=item_quantity, height=item_height)
            self.input_entries[type_id] = item_container

    def AddOutputItems(self, recipe):
        outputs = recipe.outputItems
        outputItemsAndQty = []
        for type_id, qty in outputs.iteritems():
            outputItemsAndQty.append((type_id, self.multiplier * qty))

        self.output_containerParent.AddOutputItems(outputItemsAndQty)

    def UpdateBtnState(self):
        maxMultiplier = self.itemTraderController.GetInputMaxMultiplier()
        if maxMultiplier <= 0:
            self.trade_items_action_button.disabled = True
            self.trade_items_action_button.hint = GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/MissingRequiredItems')
        elif self.multiplier == 0:
            self.trade_items_action_button.disabled = True
        else:
            self.trade_items_action_button.disabled = False
            self.trade_items_action_button.hint = ''

    def OnNumericInputChange(self, *args):
        self.multiplier = self.quantity_numeric_input.GetValue()
        current_recipe = self.itemTraderController.selectedRecipe
        for type_id, qty in current_recipe.inputItems.iteritems():
            inputEntry = self.input_entries.get(type_id)
            if inputEntry:
                inputEntry.UpdateQty(self.multiplier * qty)

        for type_id, qty in current_recipe.outputItems.iteritems():
            self.output_containerParent.UpdateQty(type_id, self.multiplier * qty)

        self.UpdateBtnState()

    def OnButtonTradeItemsClicked(self, *args):
        wnd = ItemTraderDialogPopupWindow.GetIfOpen(windowInstanceID=self.item_trader.itemID)
        if wnd and not wnd.destroyed:
            wnd.LoadItemAndPayoutContainers(self.multiplier, self.itemTraderController.selectedRecipe)
            wnd.Maximize()
            return
        ItemTraderDialogPopupWindow.Open(windowInstanceID=self.item_trader.itemID, item_trader=self.item_trader, multiplier=self.multiplier, recipe=self.itemTraderController.selectedRecipe)

    def Close(self, setClosed = False, *args, **kwds):
        with ExceptionEater('Closing Item trader window'):
            wnd = ItemTraderDialogPopupWindow.GetIfOpen(windowInstanceID=self.item_trader.itemID)
            if wnd:
                wnd.Close()
            self.ChangeSignalConnection(False)
            self.itemTraderController = None
        super(ItemTraderWindow, self).Close(setClosed, *args, **kwds)

    def OnCollapseLineExpand(self, animate):
        newWidth = self.width + self.collapseLine.collapsingSectionSize
        animations.MorphScalar(self, 'width', self.width, newWidth, duration=ANIM_DURATION)
        self.UpdateMinSize()

    def UpdateMinSize(self):
        if not self.collapseLine.display:
            return
        if self.collapseLine.isCollapsed:
            newMinWidth = self.default_minSize[0]
        else:
            newMinWidth = self.default_minSize[0] + self.collapseLine.collapsingSectionSize
        self.SetMinSize([newMinWidth, self.default_minSize[1]])

    def OnCollapseLineCollapse(self, animate):
        newWidth = self.width - self.collapseLine.collapsingSectionSize
        animations.MorphScalar(self, 'width', self.width, newWidth, duration=ANIM_DURATION)
        self.UpdateMinSize()

    def OnDividerMove(self, *args):
        if self.itemTraderController.tempWndWidth is None:
            self.resizeCont.minSize = 100
            self.itemTraderController.tempWndWidth = self.width - self.resizeCont.width
        self.width = self.itemTraderController.tempWndWidth + self.resizeCont.width
        self.collapseLine.SetCollapsingSectionSize(self.resizeCont.width)

    def OnResizeDivider(self, *args):
        self.itemTraderController.tempWndWidth = None
        self.resizeCont.minSize = 0
        self.UpdateMinSize()

    def GetMenuMoreOptions(self):
        menu_data = super(ItemTraderWindow, self).GetMenuMoreOptions()
        if session.role & ROLE_PROGRAMMER:
            menu_data.AddEntry('QA Reload', lambda : self.Reload(self))
        return menu_data


class InputEntry(Container):
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(InputEntry, self).ApplyAttributes(attributes)
        self.type_id = attributes.type_id
        self.itemTraderController = attributes.itemTraderController
        item_quantity = attributes.item_quantity
        self.ConstructUI(item_quantity)

    def ConstructUI(self, item_quantity):
        typeName = evetypes.GetName(self.type_id)
        GradientSprite(bgParent=self, rgbData=[(1.0, (1, 1, 1))], alphaData=[(0, 0.05), (0.9, 0.05), (1.0, 0)], alphaInterp=GradientConst.INTERP_LINEAR, colorInterp=GradientConst.INTERP_LINEAR, padTop=2, padBottom=2)
        item_icon_container = Container(parent=self, align=uiconst.TOLEFT, padLeft=12, width=60)
        item_icon = Sprite(name='Item logo', parent=item_icon_container, align=uiconst.CENTER, height=40, width=40)
        sm.GetService('photo').GetIconByType(item_icon, self.type_id)
        item_numeric_input_container = Container(name='item_numeric_input_container', parent=self, align=uiconst.TORIGHT, padRight=40, width=50)
        self.item_quantity_label = carbonui.TextBody(parent=item_numeric_input_container, text=FmtAmt(item_quantity), align=uiconst.CENTERRIGHT)
        item_label_container = Container(parent=self, align=uiconst.TOALL)
        item_label = carbonui.TextBody(name='item_label', parent=item_label_container, text=typeName, align=uiconst.CENTERLEFT, autoFadeSides=16)

    def UpdateQty(self, qty):
        qtyInCargo = self.itemTraderController.GetCargoQtyForTypeID(self.type_id)
        qtyText = FmtAmt(qty)
        if qtyInCargo < qty:
            newColor = eveColor.DANGER_RED
            qtyText = eveformat.color(qtyText, newColor)
        self.item_quantity_label.SetText(qtyText)

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(None, self.type_id, includeMarketDetails=True)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.columns = 2
        typeIcon = Sprite(parent=tooltipPanel, align=uiconst.CENTERLEFT, pos=(0, 0, 20, 20))
        sm.GetService('photo').GetIconByType(typeIcon, self.type_id)
        tooltipPanel.AddTextBodyLabel(text=evetypes.GetName(self.type_id))
        tooltipPanel.FillRow()
        amountInCargo = self.itemTraderController.GetCargoQtyForTypeID(self.type_id)
        text = GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/UnitsInCargo', numUnits=FmtAmt(amountInCargo))
        tooltipPanel.AddTextBodyLabel(text=text, colSpan=tooltipPanel.columns)
        tooltipPanel.FillRow()
