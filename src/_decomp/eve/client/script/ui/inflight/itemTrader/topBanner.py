#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\itemTrader\topBanner.py
import carbonui
import eveicon
import evetypes
from carbon.common.script.util.format import FmtAmt
from carbonui import const as uiconst, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.inflight.itemTrader.recipeUtil import LoadRecipeTooltipPanel
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel

class TopBanner(Container):
    default_align = uiconst.TOTOP
    default_height = 60
    default_clipChildren = True
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(TopBanner, self).ApplyAttributes(attributes)
        self.recipe = None
        text = GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/TradeRatio')
        carbonui.TextDetail(parent=self, align=uiconst.TOTOP, color=TextColor.SECONDARY, text=text, top=6)
        self.recipeCont = Container(name='recipeCont', parent=self, align=uiconst.TOALL, padBottom=8)

    def LoadRecipe(self, recipe):
        self.recipeCont.Flush()
        self.recipe = recipe
        lastPlusLabelCont = None
        if self.recipe.inputIsk:
            TopBannerIsk(parent=self.recipeCont, amount=self.recipe.inputIsk)
            lastPlusLabelCont = PlusLabelCont(parent=self.recipeCont)
        for typeID, qty in recipe.inputItems.iteritems():
            TopBannerItem(parent=self.recipeCont, typeID=typeID, qty=qty)
            lastPlusLabelCont = PlusLabelCont(parent=self.recipeCont)

        if lastPlusLabelCont:
            lastPlusLabelCont.Close()
            lastPlusLabelCont = None
        tradeIcon = Sprite(parent=ContainerAutoSize(parent=self.recipeCont, align=uiconst.TOLEFT, padding=(8, 0, 8, 0)), align=uiconst.CENTERLEFT, pos=(0, 0, 16, 16), texturePath=eveicon.trade, color=TextColor.SECONDARY)
        for typeID, qty in recipe.outputItems.iteritems():
            TopBannerItem(parent=self.recipeCont, typeID=typeID, qty=qty)
            lastPlusLabelCont = PlusLabelCont(parent=self.recipeCont)

        if lastPlusLabelCont:
            lastPlusLabelCont.Close()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        LoadRecipeTooltipPanel(tooltipPanel, self.recipe)


class TopBannerIsk(ContainerAutoSize):
    default_align = uiconst.TOLEFT

    def ApplyAttributes(self, attributes):
        super(TopBannerIsk, self).ApplyAttributes(attributes)
        amount = attributes.amount
        innnerCont = ContainerAutoSize(parent=self, align=uiconst.CENTERLEFT)
        sprite = Sprite(parent=innnerCont, align=uiconst.CENTERLEFT, pos=(8, 0, 16, 16), texturePath=eveicon.isk, color=TextColor.SECONDARY, state=uiconst.UI_DISABLED)
        left = sprite.left + sprite.width
        carbonui.TextDetail(parent=self, text=FmtISK(amount), align=uiconst.CENTERLEFT, left=left + 8, color=TextColor.SECONDARY)


class TopBannerItem(ContainerAutoSize):
    default_align = uiconst.TOLEFT

    def ApplyAttributes(self, attributes):
        super(TopBannerItem, self).ApplyAttributes(attributes)
        typeID = attributes.typeID
        qty = attributes.qty
        innnerCont = ContainerAutoSize(parent=self, align=uiconst.CENTERLEFT)
        qtyLabel = carbonui.TextDetail(parent=self, text=FmtAmt(qty), align=uiconst.CENTERLEFT, color=TextColor.SECONDARY)
        left = qtyLabel.left + qtyLabel.width
        typeIcon = Sprite(parent=innnerCont, align=uiconst.CENTERLEFT, pos=(left + 8,
         0,
         16,
         16), state=uiconst.UI_DISABLED)
        sm.GetService('photo').GetIconByType(typeIcon, typeID)
        left = typeIcon.left + typeIcon.width
        carbonui.TextDetail(parent=self, text=evetypes.GetName(typeID), align=uiconst.CENTERLEFT, left=left + 8, color=TextColor.SECONDARY)


class PlusLabelCont(ContainerAutoSize):
    default_align = uiconst.TOLEFT
    default_padding = (8, 0, 8, 0)

    def ApplyAttributes(self, attributes):
        super(PlusLabelCont, self).ApplyAttributes(attributes)
        carbonui.TextDetail(parent=self, text='+', align=uiconst.CENTERLEFT, color=TextColor.SECONDARY)
