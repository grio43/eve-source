#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\buttonbazaar\window.py
import logging
import textwrap
from carbonui import Color, uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from eve.client.script.ui.control import eveLabel
from carbonui.control.window import Window
from eve.devtools.script.buttonbazaar.buttons import Group, iter_buttons
log = logging.getLogger(__name__)

class ButtonBazaarWindow(Window):
    default_windowID = 'ButtonBazaarWindow'
    default_minSize = (800, 600)

    def __init__(self, **kwargs):
        super(ButtonBazaarWindow, self).__init__(**kwargs)
        self.main_cont = None
        self.errors = None
        self.view_mode = ViewMode.all
        self.layout()

    def layout(self):
        scroll = ScrollContainer(parent=self.GetMainArea(), align=uiconst.TOALL)
        top_cont = ContainerAutoSize(parent=scroll, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(0, 0, 0, 16))
        right_cont = ContainerAutoSize(parent=top_cont, align=uiconst.TORIGHT, alignMode=uiconst.CENTER, padLeft=32)
        self.caption = 'Welcome to the Button Bazaar!'
        eveLabel.EveLabelLarge(parent=top_cont, align=uiconst.TOTOP, text='The EVE codebase has a staggering number of different types of buttons. This bazaar is meant to highlight this fact by showing them all in one place.')
        Checkbox(parent=right_cont, align=uiconst.CENTER, text='Group by base class', checked=self.view_mode == ViewMode.grouped, callback=lambda checkbox: self.toggle_view_mode())
        self.errors = ErrorsWidget(parent=right_cont, align=uiconst.TOPRIGHT, top=32)
        self.main_cont = ContainerAutoSize(parent=scroll, align=uiconst.TOTOP, padding=(0, 16, 0, 0))
        self.reload()

    def toggle_view_mode(self):
        if self.view_mode == ViewMode.all:
            self.view_mode = ViewMode.grouped
        else:
            self.view_mode = ViewMode.all
        self.reload()

    def clear_errors(self):
        self.errors.clear()

    def reload(self):
        self.clear_errors()
        self.main_cont.Flush()
        if self.view_mode == ViewMode.all:
            self.load_all()
        else:
            self.load_grouped_by_base()

    def load_all(self):
        cont = FlowContainer(parent=self.main_cont, align=uiconst.TOTOP, contentSpacing=(16, 16))
        for data in iter_buttons():
            if data.group == Group.primitive:
                continue
            try:
                button = data.create()
                ButtonWrapper(parent=cont, align=uiconst.NOALIGN, button=button)
            except Exception as error:
                log.exception('Failed to create button')
                self.errors.add_error(error)

    def load_grouped_by_base(self):
        cont_by_core_class = {}
        for data in iter_buttons(Group.core):
            button = data.create()
            cont = ButtonContainer(parent=self.main_cont, align=uiconst.TOTOP, padBottom=32, core_button=button, color=(0.2, 0.6, 0.8))
            cont_by_core_class[button.__class__] = cont

        for data in iter_buttons(Group.primitive):
            primitive = data.create()
            cont = ButtonContainer(parent=self.main_cont, align=uiconst.TOTOP, padBottom=32, core_button=primitive, color=(0.8, 0.6, 0.2))
            cont_by_core_class[primitive.__class__] = cont

        for data in iter_buttons(Group.derived):
            try:
                button = data.create()
            except Exception as error:
                log.exception('Failed to create button')
                self.errors.add_error(error)
                continue

            core_cls = find_core_base(button.__class__, cont_by_core_class.keys())
            if core_cls is None:
                core_cls = Container
            cont = cont_by_core_class[core_cls]
            cont.add(button)


def find_core_base(cls, core_classes):
    candidates = []
    candidates.extend(cls.__bases__)
    while candidates:
        candidate = candidates.pop(0)
        if candidate in core_classes:
            return candidate
        candidates.extend(candidate.__bases__)


class ViewMode(object):
    all = 1
    grouped = 2


class ErrorsWidget(ContainerAutoSize):

    def __init__(self, **kwargs):
        super(ErrorsWidget, self).__init__(state=uiconst.UI_NORMAL, **kwargs)
        self._errors = []
        self._label = None
        self.layout()

    def layout(self):
        self._label = eveLabel.EveLabelLarge(parent=self, color=(0.8, 0.2, 0.0))

    def add_error(self, error):
        self._errors.append('{}: {}'.format(error.__class__.__name__, str(error)))
        self._update_error_count()

    def clear(self):
        self._errors = []
        self._update_error_count()

    def _update_error_count(self):
        if len(self._errors) == 1:
            self._label.SetText('1 error!')
        elif len(self._errors) > 1:
            self._label.SetText('{} errors!'.format(len(self._errors)))
        else:
            self._label.SetText('')

    def LoadTooltipPanel(self, panel, owner):
        panel.margin = 16
        panel.cellSpacing = (0, 4)
        for i, error in enumerate(self._errors):
            if i > 10:
                break
            panel.AddLabelMedium(text=error)

        if len(self._errors) > 10:
            panel.AddLabelMedium(text='and {} more ...'.format(len(self._errors) - 10), opacity=0.25)


class ButtonContainer(ContainerAutoSize):
    default_alignMode = uiconst.TOTOP

    def __init__(self, core_button, color, **kwargs):
        super(ButtonContainer, self).__init__(**kwargs)
        Container(parent=self, align=uiconst.TOLEFT, width=2, bgColor=color)
        top_cont_wrap = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, bgColor=Color.from_any(color).with_alpha(0.05))
        top_cont = ContainerAutoSize(parent=top_cont_wrap, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(16, 8, 16, 8))
        core_button.align = uiconst.CENTERRIGHT
        core_button.SetParent(top_cont)
        eveLabel.Label(parent=top_cont, align=uiconst.TOTOP, text=core_button.__class__.__name__, fontsize=32, fontStyle=eveLabel.fontconst.STYLE_HEADER)
        eveLabel.EveLabelMedium(parent=top_cont, align=uiconst.TOTOP, top=-4, text=core_button.__class__.__module__, opacity=0.25)
        if core_button.__class__.__doc__:
            docstring = textwrap.dedent(core_button.__class__.__doc__.strip()).split('\n')
            if len(docstring) == 1:
                docstring = docstring[0]
            else:
                docstring = u'{} [...]'.format(docstring[0])
            eveLabel.EveLabelMedium(parent=top_cont, align=uiconst.TOTOP, top=8, text=docstring)
        self.flow = FlowContainer(parent=self, align=uiconst.TOTOP, contentSpacing=(16, 16), padding=(16, 16, 0, 0))

    def add(self, button):
        ButtonWrapper(parent=self.flow, align=uiconst.NOALIGN, button=button)


class ButtonWrapper(ContainerAutoSize):
    default_alignMode = uiconst.TOPLEFT

    def __init__(self, button, **kwargs):
        super(ButtonWrapper, self).__init__(**kwargs)
        label = Label(parent=self, align=uiconst.TOPLEFT, button=button, opacity=0.25)
        button.SetAlign(uiconst.TOPLEFT)
        button.top = 18
        button.SetParent(self)


class Label(eveLabel.EveLabelSmall):
    default_state = uiconst.UI_NORMAL

    def __init__(self, button, **kwargs):
        self._button = button
        super(Label, self).__init__(text=self._button.__class__.__name__, **kwargs)

    def LoadTooltipPanel(self, panel, *args):
        panel.margin = 16
        panel.AddLabelLarge(text='<b>{}</b>'.format(self._button.__class__.__name__))
        panel.AddLabelMedium(text='in {}'.format(self._button.__class__.__module__))
        panel.AddSpacer(height=16)
        panel.AddLabelMedium(text='Derived from', opacity=0.25)
        panel.AddLabelMedium(text='<br>'.join(('{} ({})'.format(base.__name__, base.__module__) for base in self._button.__class__.__bases__)))


def __reload_update__(namespace):
    window = ButtonBazaarWindow.GetIfOpen()
    if window:
        window.Close()
    ButtonBazaarWindow.Open()
