#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Overlays\UiBlinker.py
from eve.devtools.script.uiControlCatalog.sample import Sample
import eveui
import uthread2
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        import uiblinker
        sprite = Sprite(name='my_unique_sprite', parent=parent, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, width=64, height=64, texturePath='res:/UI/Texture/Icons/icons111_07.png')
        blinker = uiblinker.start_ring('my_unique_sprite')
        sprite._blinker = blinker
        Button(parent=parent, align=uiconst.CENTERTOP, top=80, label='Stop Blinker', func=lambda : blinker.dispose(), args=())


class Sample2(Sample):
    name = 'Shapes'

    def construct_sample(self, parent):
        grid = LayoutGrid(parent=parent, align=uiconst.CENTER, columns=2, cellSpacing=(32, 32))
        self.sample_code(grid)

    def sample_code(self, parent):
        import uiblinker
        button = Button(name='my_unique_button', parent=parent, align=uiconst.CENTER, label='Just a button')
        button._blinker = uiblinker.start_box('my_unique_button')
        eveLabel.EveLabelMedium(parent=parent, align=uiconst.TOPLEFT, width=240, text='Use a box blinker for elements with a square visual representation, such as buttons and other elements with a rectangular frame.')
        sprite = Sprite(name='my_unique_sprite', parent=parent, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=64, height=64, texturePath='res:/UI/Texture/Icons/78_64_11.png')
        sprite._blinker = uiblinker.start_ring('my_unique_sprite')
        eveLabel.EveLabelMedium(parent=parent, align=uiconst.TOPLEFT, width=240, text='Use a ring blinker for elements that have an irregular shape, such as icons and other buttons without a rectangular frame.')


class Sample3(Sample):
    name = 'Occlusion'
    description = 'Blinkers turn into a flare when occluded by other pickable elements.'

    def construct_sample(self, parent):
        container = Container(parent=parent, align=uiconst.CENTER, width=300, height=100)
        self.sample_code(container)

    def sample_code(self, parent):
        import uiblinker
        occluder = Fill(parent=parent, align=uiconst.CENTER, state=uiconst.UI_NORMAL, left=100, width=100, height=100, color=(0.1, 0.1, 0.1), opacity=0.95)
        sprite = Sprite(name='my_unique_sprite', parent=parent, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=64, height=64, texturePath='res:/UI/Texture/Icons/53_64_13.png')
        sprite._blinker = uiblinker.start_ring('my_unique_sprite')

        def animate_occluder():
            while not occluder.destroyed:
                eveui.animate(occluder, 'left', end_value=0, duration=4.0, sleep=True)
                uthread2.sleep(2.0)
                eveui.animate(occluder, 'left', end_value=100, duration=4.0, sleep=True)
                uthread2.sleep(2.0)

        uthread2.start_tasklet(animate_occluder)


class Sample4(Sample):
    name = 'Customization'
    description = 'You can easily create your own custom UI references. This sample UI reference implementation walks the entire UI element tree and finds all sprites with the given texture path.'

    def sample_code(self, parent):
        import uiblinker

        class SampleUiReference(uiblinker.UiReference):

            def __init__(self, texture_path):
                self.texture_path = texture_path

            def resolve(self, root):
                elements = []
                for element in uiblinker.iter_element_tree(root):
                    if isinstance(element, Sprite) and element.texturePath == self.texture_path:
                        elements.append(element)

                return elements

        TEXTURE_PATH = 'res:/UI/Texture/Icons/53_64_12.png'
        sprite = Sprite(parent=parent, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=64, height=64, texturePath=TEXTURE_PATH)
        sprite._blinker = uiblinker.start_ring(SampleUiReference(TEXTURE_PATH))
