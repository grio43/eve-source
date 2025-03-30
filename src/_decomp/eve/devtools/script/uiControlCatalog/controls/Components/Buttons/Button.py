#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\Buttons\Button.py
from carbonui.control.button import Button
import eveicon
import threadutils
import uthread2
from carbonui import ButtonFrameType, ButtonStyle, ButtonVariant, Density, uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.message import ShowQuickMessage
from carbonui.control.tabGroup import TabGroup
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from carbonui.control.button import Button

        def OnButton(*args):
            ShowQuickMessage('Thanks!')

        Button(name='myButton', parent=parent, label='Press me plz', func=OnButton)


class Sample2(Sample):
    name = 'Playground'
    cls = Button

    def construct_sample(self, parent):

        def on_clicked(button):
            ShowQuickMessage('{} pushed!'.format(button.label))

        create_button_tweaker_harness(Button(parent=parent, align=uiconst.CENTER, label='Button', func=on_clicked))


def create_button_tweaker_harness(button):
    main_cont = LayoutGrid(parent=button.parent, align=uiconst.CENTER, columns=3, cellSpacing=(32, 32))
    button_cont = ContainerAutoSize(parent=main_cont, align=uiconst.CENTER, padding=32)
    button.SetParent(button_cont)
    control_cont = ContainerAutoSize(parent=main_cont, align=uiconst.TOPLEFT, width=160)
    control_cont_right = ContainerAutoSize(parent=main_cont, align=uiconst.TOPLEFT, width=160)

    def on_variant_changed(combo, key, value):
        button.variant = value

    eveLabel.EveLabelMedium(parent=control_cont, align=uiconst.TOTOP, padding=(0, 0, 0, 4), text='Variant')
    Combo(parent=control_cont, align=uiconst.TOTOP, options=[('Primary', ButtonVariant.PRIMARY), ('Normal', ButtonVariant.NORMAL), ('Ghost', ButtonVariant.GHOST)], select=button.variant, callback=on_variant_changed)

    def on_density_changed(combo, key, value):
        button.density = value

    eveLabel.EveLabelMedium(parent=control_cont, align=uiconst.TOTOP, padding=(0, 16, 0, 4), text='Density')
    Combo(parent=control_cont, align=uiconst.TOTOP, options=[('Compact', Density.COMPACT), ('Normal', Density.NORMAL), ('Extended', Density.EXPANDED)], select=button.density, callback=on_density_changed)

    def on_text_changed(checkbox):
        text = 'Button' if checkbox.checked else None
        button.label = text

    Checkbox(parent=control_cont, align=uiconst.TOTOP, text='With text', checked=bool(button.label), callback=on_text_changed, padding=(0, 16, 0, 8))

    def on_icon_changed(checkbox):
        button.icon = eveicon.eye if checkbox.checked else None

    Checkbox(parent=control_cont, align=uiconst.TOTOP, text='With icon', checked=bool(button.icon), callback=on_icon_changed, padBottom=8)

    def on_style_changed(combo, key, value):
        button.style = value

    eveLabel.EveLabelMedium(parent=control_cont_right, align=uiconst.TOTOP, padding=(0, 0, 0, 4), text='Style')
    Combo(parent=control_cont_right, align=uiconst.TOTOP, options=[('Normal', ButtonStyle.NORMAL),
     ('Success', ButtonStyle.SUCCESS),
     ('Warning', ButtonStyle.WARNING),
     ('Danger', ButtonStyle.DANGER),
     ('Monetization', ButtonStyle.MONETIZATION)], select=button.style, callback=on_style_changed)

    def on_frame_type_changed(combo, key, value):
        button.frame_type = value

    eveLabel.EveLabelMedium(parent=control_cont_right, align=uiconst.TOTOP, padding=(0, 16, 0, 4), text='Frame type')
    Combo(parent=control_cont_right, align=uiconst.TOTOP, options=[('Rectangle', ButtonFrameType.RECTANGLE),
     ('Cut corner - bottom left', ButtonFrameType.CUT_BOTTOM_LEFT),
     ('Cut corner - bottom right', ButtonFrameType.CUT_BOTTOM_RIGHT),
     ('Cut corner - bottom left and right', ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT)], select=button.frame_type, callback=on_frame_type_changed)

    def on_enabled_changed(checkbox):
        button.enabled = checkbox.checked

    Checkbox(parent=control_cont_right, align=uiconst.TOTOP, text='Enabled', checked=button.enabled, callback=on_enabled_changed, padding=(0, 16, 0, 8))

    def on_busy_changed(checkbox):
        button.busy = checkbox.checked

    Checkbox(parent=control_cont_right, align=uiconst.TOTOP, text='Busy', checked=button.busy, callback=on_busy_changed, padBottom=8)


class Sample3(Sample):
    name = 'Variant'
    description = 'Not all actions in the game are equally important to the player. We use different button variants to communicate the relative importance of actions. There are three different variants available:'

    def construct_sample(self, parent):
        main_cont = ContainerAutoSize(parent=parent, align=uiconst.CENTER, width=460)
        tabs = TabGroup(parent=main_cont, align=uiconst.TOTOP, top=16, padBottom=16)
        variants = [('Normal', ButtonVariant.NORMAL, "The normal variant is the default. It's used for most actions."), ('Primary', ButtonVariant.PRIMARY, "The primary variant should be used for the most pertinent actions. Primary actions usually move the user forward in the flow of the UI. It's the next logical action that the user should take. F.ex. 'Submit', 'Next', 'Buy', etc.\n\nThere should only be a single button of the primary variant visible in any given UI."), ('Ghost', ButtonVariant.GHOST, 'The ghost variant has the lowest emphasis of the three. It should be used for supplamentary actions or less important actions that are associated with deeply nested content.\n\nThis variant blends in with the other content and users are more likely to miss it than the other variants, so avoid using it for actions that players need to see clearly.')]
        for name, variant, description in variants:
            tab_cont = ContainerAutoSize(parent=main_cont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=Button.default_height)
            Button(parent=ContainerAutoSize(parent=tab_cont, align=uiconst.TOLEFT, padRight=16), align=uiconst.CENTERTOP, label=name, variant=variant)
            eveLabel.EveLabelMedium(parent=tab_cont, align=uiconst.TOTOP, text=description)
            tabs.AddTab(label=name, panel=tab_cont)

        tabs.AutoSelect()


class Sample4(Sample):
    name = 'Style'
    description = "The button's style is used to communicate information about the action that the button represents."

    def construct_sample(self, parent):
        main_cont = ContainerAutoSize(parent=parent, align=uiconst.CENTERTOP, width=460)
        tabs = TabGroup(parent=main_cont, align=uiconst.TOTOP, top=16, padBottom=16)
        styles = [('Normal', ButtonStyle.NORMAL, "This is the default style. You'll use this most of the time."),
         ('Success', ButtonStyle.SUCCESS, 'This style can be used for actions to continue some flow that has been completed. F.ex. complete mission, claim reward, etc.'),
         ('Warning', ButtonStyle.WARNING, 'This style should be used when the action has some potential major consequences. For example: undocking into a dangerous system, buying an item at above the regional average price, etc.'),
         ('Danger', ButtonStyle.DANGER, "This style should be used when the action is severe and can't be undone. For example: trashing an item, self-destructing your ship, etc."),
         ('Monetization', ButtonStyle.MONETIZATION, 'This style should be used whenever the action deals with PLEX, Omega orother monetization concepts.')]
        for name, style, description in styles:
            tab_cont = ContainerAutoSize(parent=main_cont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=Button.default_height)
            Button(parent=ContainerAutoSize(parent=tab_cont, align=uiconst.TOLEFT, padRight=16), align=uiconst.CENTERTOP, label=name, style=style)
            eveLabel.EveLabelMedium(parent=tab_cont, align=uiconst.TOTOP, text=description)
            tabs.AddTab(label=name, panel=tab_cont)

        tabs.AutoSelect()


class Sample5(Sample):
    name = 'Busy flag'
    description = "The 'busy' flag can be used to indicate progress on a button"

    def sample_code(self, parent):

        @threadutils.threaded
        def long_running_process(button):
            if button.busy:
                return
            button.busy = True
            label_before = button.label
            button.label = 'Processing ...'
            uthread2.sleep(3.0)
            button.busy = False
            button.label = label_before

        Button(parent=parent, align=uiconst.TOPLEFT, label='Start', func=long_running_process)


class Sample6(Sample):
    name = 'Density'

    def construct_sample(self, parent):
        grid = LayoutGrid(parent=parent, columns=1, cellSpacing=(24, 24))
        self.sample_code(grid)

    def sample_code(self, parent):
        Button(align=uiconst.CENTERTOP, parent=parent, label='Extended', density=Density.EXPANDED, func=lambda button: ShowQuickMessage('Pressed extended button'))
        Button(align=uiconst.CENTERTOP, parent=parent, label='Normal', func=lambda button: ShowQuickMessage('Pressed normal button'))
        Button(align=uiconst.CENTERTOP, parent=parent, label='Compact', density=Density.COMPACT, func=lambda button: ShowQuickMessage('Pressed compact button'))
