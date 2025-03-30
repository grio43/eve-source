#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Patterns\Icons.py
import random
import eveformat
import eveicon
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.devtools.script.uiControlCatalog.sample import Sample
from eveicon.client.browser import IconBrowserWindow

class Sample1(Sample):
    name = 'Icons'
    description = "There's an extensive icon library available through the <b>eveicon</b> package. You can pass icons from the package directly to sprites and other basic components."

    def construct_sample(self, parent):
        gap = 8
        columns = 12
        icon_size = 16
        main = ContainerAutoSize(parent=parent, align=uiconst.CENTER, width=columns * icon_size + (columns - 1) * gap)
        flow = FlowContainer(parent=main, align=uiconst.TOTOP, contentSpacing=(gap, gap))
        icons = list((icon for icon in eveicon.iter_icons() if icon_size in icon.sizes))
        random.shuffle(icons)
        for icon in icons[:60]:
            Sprite(parent=flow, align=uiconst.NOALIGN, width=icon_size, height=icon_size, texturePath=icon)

        Button(parent=ContainerAutoSize(parent=main, align=uiconst.TOTOP, top=16), align=uiconst.CENTER, label='Open Icon Browser', func=lambda button: IconBrowserWindow.Open())

    def sample_code(self, parent):
        import eveicon
        Sprite(parent=parent, width=16, height=16, texturePath=eveicon.star)


class Sample2(Sample):
    name = 'Auto-size'
    description = 'Sprites, buttons and other components will automatically resolve the icon to a texture of a size that best fits the size of the component.'

    def construct_sample(self, parent):
        grid = LayoutGrid(parent=parent, align=uiconst.CENTER, columns=3, cellSpacing=(16, 16))
        self.sample_code(grid)

    def sample_code(self, parent):
        import eveicon
        Sprite(parent=parent, width=16, height=16, texturePath=eveicon.target)
        Sprite(parent=parent, width=32, height=32, texturePath=eveicon.target)
        Button(parent=parent, label='Target', texturePath=eveicon.target)


class Sample3(Sample):
    name = 'Manual resolution'
    description = "If you really need a raw texture reference for an icon you can use the relevant icon's <b>resolve</b> method.<br><br>{}".format(eveformat.color("NOTE: The icon's texture path is not stable, so don't save it as a constant since it may stop working in the future.", eveColor.WARNING_ORANGE))

    def construct_sample(self, parent):
        grid = LayoutGrid(parent=parent, align=uiconst.CENTER, columns=1, cellSpacing=(16, 16))
        Sprite(parent=grid, align=uiconst.CENTER, width=16, height=16, texturePath=eveicon.star)
        EveLabelMedium(parent=grid, text=eveicon.star.resolve(16))

    def sample_code(self, parent):
        import eveicon
        eveicon.star.resolve(16)
