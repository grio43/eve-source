#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\vgsDetailProduct.py
from carbonui import const as uiconst
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.fontconst import STYLE_HEADER
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.util.uiComponents import Component, ButtonEffect
from eve.client.script.ui.view.aurumstore.shared.const import QUANTITY_MIN, QUANTITY_MAX
from eve.client.script.ui.view.aurumstore.vgsOffer import GetPreviewType
from eve.common.script.sys.eveCfg import IsPreviewable
from localization import GetByLabel
import trinity
PRICE_LABEL_COLOR = (1.0, 1.0, 1.0, 1.2)

@Component(ButtonEffect(bgElementFunc=lambda self, _: self.highlight, opacityHover=0.1, opacityMouseDown=0.4, audioOnEntry=uiconst.SOUND_ENTRY_HOVER, audioOnClick=uiconst.SOUND_ENTRY_SELECT))

class VgsDetailProduct(Container):
    default_height = 36

    def ApplyAttributes(self, attributes):
        super(VgsDetailProduct, self).ApplyAttributes(attributes)
        self.name = attributes.name
        self.quantity = attributes.quantity
        self.price = attributes.price
        self.typeID = attributes.typeID
        self.onClick = attributes.onClick
        self.isSinglePurchase = attributes.isSinglePurchase
        self.showQuantity = attributes.get('showQuantity', True)
        self.showPrice = attributes.get('showPrice', True)
        self.onQuantityChangeCallback = attributes.get('onQuantityChangeCallback')
        self.text = GetByLabel('UI/VirtualGoodsStore/ItemNameAndQuantity', itemName=self.name, quantity=self.quantity)
        self.BuildHoverHighlight()
        self.BuildPrice()
        self.BuildQuantityEditor()
        self.BuildProductName()
        self.BuildCursor()

    def BuildHoverHighlight(self):
        self.highlight = Sprite(name='hoverGradient', bgParent=self, texturePath='res:/UI/Texture/Vgs/store-button-gradient2.png', color=(0.2, 0.7, 1.0))

    def BuildPrice(self):
        if self.showPrice:
            priceContainer = Container(name='priceContainer', parent=self, align=uiconst.TORIGHT, width=120, state=uiconst.UI_DISABLED)
            Label(name='price', parent=priceContainer, align=uiconst.CENTERRIGHT, text=GetByLabel('UI/PlexVault/PlexBalance', amount=self.price), fontsize=16)

    def BuildQuantityEditor(self):
        if self.showQuantity:
            quantityEditorContainer = Container(name='quantityEditorContainer', parent=self, align=uiconst.TORIGHT, width=64)
            self.quantityEdit = SingleLineEditInteger(parent=quantityEditorContainer, minValue=QUANTITY_MIN, maxValue=QUANTITY_MAX, fontsize=16, fontStyle=STYLE_HEADER, bold=True, width=56, height=24, top=0, padLeft=8, align=uiconst.CENTERLEFT, bgColor=Color.GRAY7, arrowIconColor=(0.0, 0.0, 0.0, 1.0), arrowIconGlowColor=(0.2, 0.2, 0.2, 1.0), arrowIconClass=Sprite, arrowIconBlendMode=trinity.TR2_SBM_BLEND, arrowUseThemeColor=False, caretColor=(0.0, 0.0, 0.0, 0.75), selectColor=(0.0, 0.0, 0.0, 0.25), fontcolor=(0.0, 0.0, 0.0, 1.0), OnChange=self.onQuantityChangeCallback, maxLength=2, hint=GetByLabel('UI/Common/Quantity'), state=uiconst.UI_NORMAL)
            if self.isSinglePurchase:
                self.quantityEdit.Disable()
            self.quantityEdit.underlay.Hide()

    def BuildProductName(self):
        productNameContainer = Container(name='productNameContainer', parent=self, align=uiconst.TOALL)
        Label(name='productName', parent=productNameContainer, align=uiconst.CENTERLEFT, text=self.text, autoFadeSides=True, fontsize=14)

    def BuildCursor(self):
        if IsPreviewable(GetPreviewType(self.typeID)):
            self.cursor = uiconst.UICURSOR_MAGNIFIER
        else:
            self.disabled = True

    def OnClick(self):
        self.onClick(self.typeID)

    def GetQuantityEditValue(self):
        if self.showQuantity:
            return self.quantityEdit.GetValue()

    def SetQuantityEditValue(self, quantity):
        if self.showQuantity:
            return self.quantityEdit.SetValue(quantity, docallback=False)

    def DisableQuantityEdit(self):
        if self.showQuantity:
            self.quantityEdit.Disable()
