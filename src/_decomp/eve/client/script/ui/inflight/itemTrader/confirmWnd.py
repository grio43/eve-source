#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\itemTrader\confirmWnd.py
import evetypes
from carbonui import const as uiconst
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.line import Line
from eve.client.script.ui.control.eveLabel import Label
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel

class ItemTraderDialogPopupWindow(Window):
    __guid__ = 'form.ItemTraderDialogPopup'
    default_windowID = 'itemTraderDialogPopup'
    default_caption = GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/ConfirmationTitle')
    default_isLightBackgroundConfigurable = False
    default_isMinimizable = False
    default_isStackable = False
    default_isCollapseable = False
    default_isLockable = False
    default_isOverlayable = False
    default_fixedWidth = 420
    default_fixedHeight = 260
    default_apply_content_padding = False
    default_iconNum = 'res:/UI/Texture/WindowIcons/question.png'

    def ApplyAttributes(self, attributes):
        self.item_trader = attributes.item_trader
        currentMultiplier = attributes.multiplier
        currentRecipe = attributes.recipe
        Window.ApplyAttributes(self, attributes)
        self.ConstructLayout()
        self.LoadItemAndPayoutContainers(currentMultiplier, currentRecipe)

    def ConstructLayout(self):
        self.main_container = Container(name='main_container', parent=self.content, width=self.default_fixedWidth, height=self.default_fixedHeight - 100, align=uiconst.TOTOP)
        self.grid_container = GridContainer(name='grid_container', parent=self.main_container, contentSpacing=(12, 12), columns=2, padding=(12, 12, 12, 12))
        self.items_parent_container = Container(name='items_parent_container', parent=self.grid_container)
        self.items_label = Label(parent=self.items_parent_container, text=GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/ConfirmationItems'), align=uiconst.TOTOP, padBottom=6)
        self.items_container = ScrollContainer(name='items_container', parent=self.items_parent_container, align=uiconst.TOALL)
        self.payouts_parent_container = Container(name='payouts_parent_container', parent=self.grid_container)
        self.payouts_label = Label(parent=self.payouts_parent_container, text=GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/ConfirmationPayout'), align=uiconst.TOTOP, padBottom=6)
        self.payouts_container = ScrollContainer(name='payouts_container', parent=self.payouts_parent_container, align=uiconst.TOALL)

    def LoadItemAndPayoutContainers(self, multiplier, recipe):
        self.items_container.Flush()
        self.payouts_container.Flush()
        self.currentMultiplier = multiplier
        self.currentRecipe = recipe
        for type_id, qty in recipe.inputItems.iteritems():
            newQty = multiplier * qty
            cont = ContainerAutoSize(parent=self.items_container, align=uiconst.TOTOP, clipChildren=True, padRight=10)
            Label(parent=cont, text=str(newQty) + ' ' + evetypes.GetName(type_id), align=uiconst.TOPLEFT, autoFadeSides=16, maxLines=1)

        if recipe.inputIsk:
            Label(parent=self.items_container, text=FmtISK(multiplier * recipe.inputIsk), align=uiconst.TOTOP, padTop=8)
        for type_id, qty in recipe.outputItems.iteritems():
            newQty = multiplier * qty
            cont = ContainerAutoSize(parent=self.payouts_container, align=uiconst.TOTOP, clipChildren=True)
            Label(parent=cont, text=str(newQty) + ' ' + evetypes.GetName(type_id), align=uiconst.TOPLEFT, autoFadeSides=16)

        self.action_container = Container(parent=self.sr.main)
        Line(parent=self.action_container, align=uiconst.TOTOP)
        self.button_group = ButtonGroup(parent=self.action_container, align=uiconst.CENTER)
        self.yes_button = Button(parent=self.button_group, name='yes_button', label=GetByLabel('UI/Common/Buttons/Yes'), func=self.OnClickConfirm, state=uiconst.UI_NORMAL)
        self.no_button = Button(parent=self.button_group, name='no_button', label=GetByLabel('UI/Common/Buttons/No'), func=self.OnClickCancel, state=uiconst.UI_NORMAL)

    def OnClickConfirm(self, *args):
        success, data = self.ProcessTrade()
        sm.ScatterEvent('OnItemTraderProcessed', self.item_trader.itemID, self.currentRecipe)
        if not success:
            eve.Message('CustomNotify', {'notify': GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/ItemTradeFailed')})
        self.Close()

    def ProcessTrade(self, *args):
        item_trader = self.item_trader
        return item_trader.ProcessTrade(self.currentRecipe.recipeID, self.currentMultiplier, 0)

    def OnClickCancel(self, *args):
        self.Close()
