#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\ButtonGroups\ButtonGroup.py
import random
import eveicon
from carbonui import Axis, AxisAlignment, ButtonVariant, Density, TextColor, uiconst
from carbonui.control.button import Button
from carbonui.button.group import ButtonGroup
from carbonui.control.combo import Combo
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control import eveLabel
from carbonui.button.group import ButtonSizeMode
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from carbonui.button.group import ButtonGroup

        def on_button_clicked(button):
            ShowQuickMessage('You picked {}'.format(button.label))

        button_group = ButtonGroup(parent=parent, align=uiconst.TOPLEFT)
        Button(parent=button_group, label='Yes', func=on_button_clicked)
        Button(parent=button_group, label='No', func=on_button_clicked)
        Button(parent=button_group, label='Maybe', func=on_button_clicked, variant=ButtonVariant.GHOST)


class Sample2(Sample):
    name = 'Playground'
    playground = None

    def construct_sample(self, parent):
        Playground(parent=parent, align=uiconst.CENTER, button_group=ButtonGroup(align=uiconst.CENTER, buttons=[ Button(label=random.choice(FRUIT), texturePath=get_random_icon()) for _ in range(3) ]))


class Playground(ContainerAutoSize):
    _button_alignment_label = None
    _button_alignment_combo = None
    _width_slider = None
    _width_slider_label = None

    def __init__(self, button_group, **kwargs):
        self.button_group = button_group
        super(Playground, self).__init__(**kwargs)
        self._layout()

    def _layout(self):
        main = LayoutGrid(parent=self, align=uiconst.TOPLEFT, columns=2)
        button_group_section = Container(parent=main, align=uiconst.TOPLEFT, width=500, height=368, clipChildren=True)
        Frame(bgParent=button_group_section, align=uiconst.TOALL, opacity=0.05)
        self.button_group.SetParent(button_group_section)
        option_wrap = Container(parent=main, align=uiconst.TOPLEFT, width=200, height=368, bgColor=(1.0, 1.0, 1.0, 0.05))
        options = Container(parent=option_wrap, align=uiconst.TOALL, padding=16)
        eveLabel.EveLabelMedium(parent=options, align=uiconst.TOTOP, padding=(0, 0, 0, 4), text='Alignment')
        Combo(parent=options, align=uiconst.TOTOP, options=[('CENTER', uiconst.CENTER),
         ('TOPLEFT', uiconst.TOPLEFT),
         ('TOLEFT', uiconst.TOLEFT),
         ('TOTOP', uiconst.TOTOP),
         ('TORIGHT', uiconst.TORIGHT),
         ('TOBOTTOM', uiconst.TOBOTTOM)], select=self.button_group.align, callback=self._on_alignment_changed, density=Density.COMPACT)
        self._button_alignment_label = eveLabel.EveLabelMedium(parent=options, align=uiconst.TOTOP, padding=(0, 8, 0, 4), text='Button alignment')
        self._button_alignment_combo = Combo(parent=options, align=uiconst.TOTOP, options=[('START', AxisAlignment.START), ('CENTER', AxisAlignment.CENTER), ('END', AxisAlignment.END)], select=self.button_group.button_alignment, callback=self._on_button_alignment_changed, density=Density.COMPACT)
        self._update_button_alignment_enabled()
        eveLabel.EveLabelMedium(parent=options, align=uiconst.TOTOP, padding=(0, 8, 0, 4), text='Button size mode')
        Combo(parent=options, align=uiconst.TOTOP, options=[('Equal', ButtonSizeMode.EQUAL), ('Dynamic', ButtonSizeMode.DYNAMIC), ('Stretch', ButtonSizeMode.STRETCH)], select=self.button_group.button_size_mode, callback=self._on_button_size_mode_changed, density=Density.COMPACT)
        eveLabel.EveLabelMedium(parent=options, align=uiconst.TOTOP, padding=(0, 8, 0, 4), text='Orientation')
        Combo(parent=options, align=uiconst.TOTOP, options=[('Horizontal', Axis.HORIZONTAL), ('Vertical', Axis.VERTICAL)], select=self.button_group.orientation, callback=self._on_orientation_changed, density=Density.COMPACT)
        eveLabel.EveLabelMedium(parent=options, align=uiconst.TOTOP, padding=(0, 8, 0, 4), text='Density')
        Combo(parent=options, align=uiconst.TOTOP, options=[('Compact', Density.COMPACT), ('Normal', Density.NORMAL), ('Extended', Density.EXPANDED)], select=self.button_group.density, callback=self._on_density_changed, density=Density.COMPACT)
        self._width_slider_label = eveLabel.EveLabelMedium(parent=options, align=uiconst.TOTOP, top=8, text='Width')
        self._width_slider = Slider(parent=options, align=uiconst.TOTOP, value=self.button_group.width, minValue=0, maxValue=500, callback=self._set_button_group_width, on_dragging=self._set_button_group_width, getHintFunc=lambda s: '{} px'.format(int(s.value)))
        self._update_width_slider_enabled()
        ButtonGroup(parent=options, align=uiconst.TOTOP, top=8, density=Density.COMPACT, button_size_mode=ButtonSizeMode.STRETCH, buttons=[Button(label='Add', func=self._add_button, args=()), Button(label='Remove', func=self._remove_button, args=())])

    def _add_button(self):
        Button(parent=self.button_group, label=random.choice(FRUIT), texturePath=get_random_icon())

    def _remove_button(self):
        if len(self.button_group.buttons) > 0:
            self.button_group.buttons[-1].Close()

    def _on_alignment_changed(self, combo, key, value):
        self.button_group.align = value
        self._update_button_group_width()
        self._update_width_slider_enabled()

    def _on_button_alignment_changed(self, combo, key, value):
        self.button_group.button_alignment = value

    def _on_button_size_mode_changed(self, combo, key, value):
        self.button_group.button_size_mode = value
        self._update_width_slider_enabled()
        self._update_button_alignment_enabled()

    def _on_orientation_changed(self, combo, key, value):
        self.button_group.orientation = value

    def _on_density_changed(self, combo, key, value):
        self.button_group.density = value

    def _set_button_group_width(self, slider):
        self._update_button_group_width()

    def _update_button_group_width(self):
        if self._get_width_slider_enabled():
            self.button_group.width = int(self._width_slider.value)

    def _get_button_alignment_enabled(self):
        return self.button_group.button_size_mode != ButtonSizeMode.STRETCH

    def _update_button_alignment_enabled(self):
        if self._get_button_alignment_enabled():
            self._button_alignment_combo.Enable()
            self._button_alignment_combo.hint = None
            self._button_alignment_label.color = TextColor.NORMAL
        else:
            self._button_alignment_combo.Disable()
            self._button_alignment_combo.hint = "When the button size mode is set to 'Stretch' the button alignment is irrelevant since the buttons will stretch out to fill the entire button group anyway."
            self._button_alignment_label.color = TextColor.DISABLED

    def _get_width_slider_enabled(self):
        return self.button_group.align in uiconst.ALIGNMENTS_WITH_RELEVANT_WIDTH and self.button_group.button_size_mode == ButtonSizeMode.STRETCH

    def _update_width_slider_enabled(self):
        if self._get_width_slider_enabled():
            self._width_slider.Enable()
            self._width_slider_label.color = TextColor.NORMAL
            self.button_group.width = self._width_slider.GetValue()
        else:
            self._width_slider.Disable()
            self._width_slider_label.color = TextColor.DISABLED


def get_random_icon():
    return random.choice(list((icon for icon in eveicon.iter_icons() if 16 in icon.sizes)))


FRUIT = ['Apple',
 'Apricot',
 'Avocado',
 'Banana',
 'Blackberry',
 'Blueberry',
 'Cherry',
 'Coconut',
 'Cucumber',
 'Durian',
 'Dragonfruit',
 'Fig',
 'Gooseberry',
 'Grape',
 'Guava',
 'Jackfruit',
 'Plum',
 'Kiwifruit',
 'Kumquat',
 'Lemon',
 'Lime',
 'Mango',
 'Watermelon',
 'Mulberry',
 'Orange',
 'Papaya',
 'Passionfruit',
 'Peach',
 'Pear',
 'Persimmon',
 'Pineapple',
 'Pineberry',
 'Quince',
 'Raspberry',
 'Soursop',
 'Star fruit',
 'Strawberry',
 'Tamarind',
 'Yuzu']
