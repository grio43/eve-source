#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\vgs\priceTag.py
from decimal import Decimal, ROUND_FLOOR
import logging
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.plex.textures import PLEX_32_SOLID_YELLOW, PLEX_24_SOLID_YELLOW
from eve.client.script.ui.shared.vgs.label import VgsLabelLarge, VgsHeaderMedium, VgsLabel
from eve.client.script.ui.shared.vgs.currency import OFFER_CURRENCY_PLEX, OFFER_CURRENCY_GEM, get_price_amount, get_price_text
ICON_SIZE_MEDIUM = 28
ICON_SIZE_LARGE = 32
FONT_COLOR_DISCOUNT_PERCENT = Color.HextoRGBA('#FF6DA149')
FONT_COLOR_DISCOUNT_STRIKETHROUGH = Color.HextoRGBA('#FF606060')
logger = logging.getLogger(__name__)

class PriceTagCore(ContainerAutoSize):
    default_height = 24
    default_fontsize = 18
    default_fontClass = VgsHeaderMedium
    default_showBasePrice = True
    default_iconSize = ICON_SIZE_MEDIUM
    FONT_BASELINE_OFFSET = 0
    WORD_PADDING = 6

    def ApplyAttributes(self, attributes):
        super(PriceTagCore, self).ApplyAttributes(attributes)
        self.fontsize = attributes.get('fontsize', self.default_fontsize)
        self.fontClass = attributes.get('fontClass', self.default_fontClass)
        self.price = attributes.price
        self.basePrice = attributes.basePrice
        self.currency = attributes.currency
        self.showBasePrice = attributes.get('showBasePrice', self.default_showBasePrice)
        self.iconSize = attributes.get('iconSize', self.default_iconSize)
        self.priceLabel = None
        self.basePriceLabel = None
        self.Layout()

    @property
    def priceText(self):
        return get_price_text(self.price, self.currency, useSpace=False)

    @property
    def basePriceText(self):
        return get_price_amount(self.basePrice, self.currency)

    def Layout(self):
        if self.currency is None:
            return
        if self.currency == OFFER_CURRENCY_PLEX or self.currency == OFFER_CURRENCY_GEM:
            self.PrepareCurrencyIcon()
        self.PreparePriceLabel()
        if self.showBasePrice and self.price < self.basePrice:
            self.PrepareBasePriceLabel()

    def PrepareCurrencyIcon(self):
        iconCont = Container(parent=self, align=uiconst.TOLEFT, width=self.iconSize, padLeft=-7)
        Sprite(parent=iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self.GetIconTexture(), width=self.iconSize, height=self.iconSize, padTop=-2)

    def PreparePriceLabel(self):
        self.priceLabel = self.fontClass(parent=self, align=uiconst.TOLEFT, text=self.priceText, padTop=self.FONT_BASELINE_OFFSET, fontsize=self.fontsize, padLeft=-2, color=Color.WHITE)

    def PrepareBasePriceLabel(self):
        labelCont = Container(parent=self, align=uiconst.TOLEFT, padLeft=self.WORD_PADDING, padTop=self.FONT_BASELINE_OFFSET)
        strikethrough = Sprite(name='strikethrough', parent=labelCont, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Vgs/strikethrough.png', color=FONT_COLOR_DISCOUNT_STRIKETHROUGH)
        self.basePriceLabel = self.fontClass(parent=labelCont, align=uiconst.TOPLEFT, text=self.basePriceText, color=FONT_COLOR_DISCOUNT_STRIKETHROUGH, fontsize=self.fontsize)
        labelCont.width = self.basePriceLabel.textwidth
        strikethrough.height = max(0, self.basePriceLabel.height - self.basePriceLabel.height % 2)
        rawPercent = (Decimal(1.0) - Decimal(self.price) / Decimal(self.basePrice)) * Decimal(100.0)
        roundPercent = rawPercent.quantize(Decimal('1'), rounding=ROUND_FLOOR)
        self.basePricePercentLabel = self.fontClass(parent=self, align=uiconst.TOLEFT, padLeft=self.WORD_PADDING, text='(-%s%%)' % roundPercent, color=FONT_COLOR_DISCOUNT_PERCENT, fontsize=self.fontsize)

    def UpdatePrice(self, price, basePrice, currency = None):
        self.price = price
        self.basePrice = basePrice
        if currency:
            self.currency = currency
        self.Refresh()

    def Refresh(self):
        self.Flush()
        self.Layout()
        self.SetSizeAutomatically()

    def GetIconTexture(self):
        if self.currency == OFFER_CURRENCY_PLEX:
            if self.iconSize == ICON_SIZE_LARGE:
                return PLEX_32_SOLID_YELLOW
            else:
                return PLEX_24_SOLID_YELLOW
        if self.currency == OFFER_CURRENCY_GEM:
            return 'res:/UI/Texture/Vgs/quantum_pricetag%d.png' % self.iconSize
        logger.error('Unhandled currency type: %s' % self.currency)
        return ''


class PriceTagSmall(PriceTagCore):
    default_fontClass = VgsLabel
    default_fontsize = 14
    FONT_BASELINE_OFFSET = 3


class PriceTagMedium(PriceTagCore):
    pass


class PriceTagLarge(PriceTagCore):
    default_height = 38
    default_name = 'PriceTagLarge'
    default_fontsize = 28
    default_fontClass = VgsLabelLarge
    default_iconSize = ICON_SIZE_LARGE
    WORD_PADDING = 8
