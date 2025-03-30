#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\vgs\label.py
import carbonui.fontconst
from carbon.common.script.util.format import FmtAmt
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.plex.textures import PLEX_32_GRADIENT_YELLOW
from eve.common.script.util.eveFormat import RoundISK
from inventorycommon.const import typePlex
import localization
import inventorycommon.typeHelpers
FONTSIZE_LARGE = 28
FONTSIZE_MEDIUM = 18
FONTSIZE_SMALL = 12
FONT_COLOR_WHITE = (1.0, 1.0, 1.0, 0.75)
FONT_COLOR_DISCOUNT = (0.627, 0.145, 0.094, 1.0)

class VgsLabel(Label):
    default_center = False

    def ApplyAttributes(self, attributes):
        self.center = attributes.get('center', self.default_center)
        super(VgsLabel, self).ApplyAttributes(attributes)

    def GetText(self):
        return super(VgsLabel, self).GetText()

    def SetText(self, text):
        if self.center:
            text = '<center>%s</center>' % text
        super(VgsLabel, self).SetText(text)

    text = property(GetText, SetText)


class VgsLabelLarge(VgsLabel):
    default_name = 'VgsLabelLarge'
    default_fontsize = FONTSIZE_LARGE
    BASELINE = 0


class VgsLabelMedium(VgsLabel):
    default_name = 'VgsLabelMedium'
    default_fontsize = FONTSIZE_MEDIUM
    BASELINE = 0


class VgsLabelSmall(VgsLabel):
    default_name = 'VgsLabelSmall'
    default_fontsize = FONTSIZE_SMALL
    BASELINE = 4


class VgsHeaderLarge(VgsLabel):
    default_name = 'VgsHeaderLarge'
    default_fontsize = FONTSIZE_LARGE
    default_fontStyle = carbonui.fontconst.STYLE_HEADER
    BASELINE = 8


class VgsHeaderMedium(VgsLabel):
    default_name = 'VgsHeaderMedium'
    default_fontsize = FONTSIZE_MEDIUM
    default_fontStyle = carbonui.fontconst.STYLE_HEADER
    BASELINE = 5


class VgsHeaderSmall(VgsLabel):
    default_name = 'VgsHeaderSmall'
    default_fontsize = FONTSIZE_SMALL
    default_fontStyle = carbonui.fontconst.STYLE_HEADER
    BASELINE = 4


class VgsButtonLabelMedium(VgsLabel):
    default_name = 'VgsButtonLabelMedium'
    default_fontsize = FONTSIZE_MEDIUM
    default_fontStyle = carbonui.fontconst.STYLE_HEADER
    default_uppercase = True
    BASELINE = 5


class PlexPriceTag(ContainerAutoSize):
    default_alignMode = uiconst.TOLEFT
    PLEX_FONT_CLASS = VgsHeaderMedium
    ISK_FONT_CLASS = VgsLabelSmall
    ISK_FONT_COLOR = (0.5, 0.5, 0.5, 1.0)
    WORD_PADDING = 8

    def ApplyAttributes(self, attributes):
        super(PlexPriceTag, self).ApplyAttributes(attributes)
        self.height = self.PLEX_FONT_CLASS.default_fontsize
        amount = attributes.amount
        baseAmount = attributes.get('baseAmount', None)
        cont = Container(parent=self, align=uiconst.TOLEFT, padRight=4, width=32)
        Sprite(parent=cont, align=uiconst.BOTTOMLEFT, state=uiconst.UI_DISABLED, texturePath=PLEX_32_GRADIENT_YELLOW, height=32, width=32, top=-7)
        self.AddPlexAmount(amount)
        if baseAmount is not None and baseAmount > amount:
            self.AddPlexAmount(baseAmount, color=FONT_COLOR_DISCOUNT, strikeThrough=True)
        iskWorth = self._CalculateEstimatedIskWorth(amount)
        if iskWorth is not None:
            self.AddEstimatedIskPrice(iskWorth)

    def AddPlexAmount(self, amount, color = None, strikeThrough = False):
        self.AddLabel(FmtAmt(amount), font=self.PLEX_FONT_CLASS, color=color, strikeThrough=strikeThrough)

    def AddEstimatedIskPrice(self, amount):
        label = localization.GetByLabel('UI/VirtualGoodsStore/EstimatedIskPrice', amount=amount)
        self.AddLabel(label, font=self.ISK_FONT_CLASS, color=self.ISK_FONT_COLOR)

    def AddLabel(self, text, font, color = None, strikeThrough = False):
        color = color or FONT_COLOR_WHITE
        cont = Container(parent=self, align=uiconst.TOLEFT, padRight=self.WORD_PADDING)
        if strikeThrough:
            Sprite(parent=cont, align=uiconst.TOALL, texturePath='res:/UI/Texture/Vgs/strikethrough.png', color=color, state=uiconst.UI_DISABLED)
        label = font(parent=cont, align=uiconst.BOTTOMLEFT, top=-font.BASELINE, text=text, color=color)
        cont.width = label.textwidth

    def _CalculateEstimatedIskWorth(self, plexPrice):
        try:
            plexValue = inventorycommon.typeHelpers.GetAveragePrice(typePlex)
        except KeyError:
            return None

        if not plexValue:
            return None
        return RoundISK(plexPrice * plexValue)


class PlexPriceTagLarge(PlexPriceTag):
    PLEX_FONT_CLASS = VgsHeaderLarge
    ISK_FONT_CLASS = VgsLabelSmall
