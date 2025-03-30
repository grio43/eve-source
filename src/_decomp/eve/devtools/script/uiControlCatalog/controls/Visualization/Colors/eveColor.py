#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Colors\eveColor.py
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui import uiconst, fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge
import blue
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


class ColorsPanel(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(ColorsPanel, self).ApplyAttributes(attributes)
        for colorName, colorHex in self.GetColors():
            ColorEntry(parent=self, align=uiconst.TOTOP, name=colorName, colorHex=colorHex)

    def GetColors(self):
        ret = []
        for key, value in eveColor.__dict__.iteritems():
            if key.endswith('_HEX'):
                key = key.replace('_HEX', '')
                ret.append((key, value))

        return sorted(ret, key=self._GetColorSortKey)

    def _GetColorSortKey(self, nameAndColor):
        name, colorHex = nameAndColor
        c = Color(colorHex)
        return (c.GetHSB(), name)


class Sample1(Sample):
    name = 'Colors'
    description = 'The EVE color library is defined under <b>eve.client.script.ui.eveColor</b>\n    Please use existing colors from the palette instead of inventing new ones'

    def construct_sample(self, parent):
        ColorsPanel(parent=parent, align=uiconst.TOPLEFT, width=500)
