#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Colors\eveThemeColor.py
import blue
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.util.color import Color
from eve.client.script.ui import eveThemeColor, eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.devtools.script.uiControlCatalog.sample import Sample

class ColorEntry(Container):
    default_height = 40
    default_padding = (0, 1, 0, 0)
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(ColorEntry, self).ApplyAttributes(attributes)
        self.colorHex = attributes.colorHex
        name = attributes.name
        self.colorName = 'eveColor.%s' % name
        brightness = Color(self.colorHex).GetBrightness()
        if brightness > 0.5:
            color = eveColor.BLACK
        else:
            color = eveColor.WHITE
        EveLabelLarge(parent=self, align=uiconst.CENTER, text=self.colorName, color=color, shadowOffset=(0, 0))
        Fill(bgParent=self, color=Color.HextoRGBA(self.colorHex))

    def GetMenu(self):
        rgb = Color.HextoRGBA(self.colorHex)
        rgbText = ', '.join([ str(x) for x in rgb ])
        rgbText = '(%s)' % rgbText
        m = [(self.colorName, blue.pyos.SetClipboardData, (self.colorName,)), (self.colorHex, blue.pyos.SetClipboardData, (self.colorHex,)), (rgbText, blue.pyos.SetClipboardData, (rgbText,))]
        return m

    def GetTooltipPointer(self):
        return uiconst.POINT_RIGHT_2


class ColorsPanel(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(ColorsPanel, self).ApplyAttributes(attributes)
        self.Reconstruct()

    def Reconstruct(self):
        self.Flush()
        for colorName, colorHex, hint in self.GetColors():
            ColorEntry(parent=self, align=uiconst.TOTOP, name=colorName, colorHex=colorHex, hint=hint)

    def GetColors(self):
        return [('THEME_TINT', eveThemeColor.THEME_TINT.hex, 'Window background color'),
         ('THEME_FOCUS', eveThemeColor.THEME_FOCUS.hex, 'Interactable Component primary color'),
         ('THEME_FOCUSDARK', eveThemeColor.THEME_FOCUSDARK.hex, 'Interactable Component secondary color'),
         ('THEME_ACCENT', eveThemeColor.THEME_ACCENT.hex, 'Hightlight and selected state color'),
         ('THEME_ALERT', eveThemeColor.THEME_ALERT.hex, 'Alert color, used to indicate something new or of interest')]

    def _GetColorSortKey(self, nameAndColor):
        name, colorHex = nameAndColor
        c = Color(colorHex)
        return (c.GetHSB(), name)

    def OnColorThemeChanged(self):
        super(ColorsPanel, self).OnColorThemeChanged()
        self.Reconstruct()


class Sample1(Sample):
    name = 'Theme colors'
    description = 'The EVE theme colors are defined under <b>eve.client.script.ui.eveThemeColor</b>\n    These colors adjust to the color theme selected under System Menu > General > Color Theme'

    def construct_sample(self, parent):
        ColorsPanel(parent=parent, align=uiconst.TOPLEFT, width=500)
