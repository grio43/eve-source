#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\closeWindowStackPrompt.py
import localization
from carbonui import AxisAlignment, uiconst
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from eve.client.script.ui.control.eveLabel import EveLabelMedium
MESSAGE_KEY = 'CloseWindowStackPrompt'

def ask():
    if is_suppressed():
        return Response.close_all
    window = CloseWindowStackPrompt.Open()
    response = window.ShowModal()
    if response in (uiconst.ID_CLOSE, uiconst.ID_CANCEL):
        response = Response.cancel
    if window.suppress_checkbox.checked and response == Response.close_all:
        set_suppressed()
    return response


class Response(object):
    cancel = 'cancel'
    close_all = 'close_all'
    close_current = 'close_current'


class CloseWindowStackPrompt(Window):
    default_fixedWidth = 400
    default_isMinimizable = False
    default_isStackable = False
    default_isCollapseable = False
    default_isLockable = False
    default_isOverlayable = False
    default_isLightBackgroundConfigurable = False
    default_iconNum = 'res:/ui/Texture/WindowIcons/question.png'

    def __init__(self, **kwargs):
        self.main_cont = None
        self.suppress_checkbox = None
        super(CloseWindowStackPrompt, self).__init__(**kwargs)
        self.caption = localization.GetByLabel('UI/CloseWindowStackPrompt/WindowCaption')
        self.layout()

    def layout(self):
        self.main_cont = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, callback=self._update_height)
        self.main_cont.DisableAutoSize()
        EveLabelMedium(parent=self.main_cont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CloseWindowStackPrompt/BodyText'))
        self.suppress_checkbox = Checkbox(parent=ContainerAutoSize(parent=self.main_cont, align=uiconst.TOTOP, top=16), align=uiconst.TOPLEFT, text=localization.GetByLabel('UI/CloseWindowStackPrompt/SuppressLabel'), checked=False)
        button_cont = FlowContainer(parent=self.main_cont, align=uiconst.TOTOP, top=8, contentAlignment=AxisAlignment.END, contentSpacing=(8, 8))
        Button(parent=button_cont, align=uiconst.NOALIGN, label=localization.GetByLabel('UI/CloseWindowStackPrompt/CloseAllLabel'), func=self.SetModalResult, args=(Response.close_all,))
        Button(parent=button_cont, align=uiconst.NOALIGN, label=localization.GetByLabel('UI/CloseWindowStackPrompt/CloseCurrentLabel'), func=self.SetModalResult, args=(Response.close_current,))
        Button(parent=button_cont, align=uiconst.NOALIGN, label=localization.GetByLabel('UI/Common/Cancel'), func=self.SetModalResult, args=(Response.cancel,))
        self.main_cont.EnableAutoSize()

    def Prepare_Background_(self):
        super(CloseWindowStackPrompt, self).Prepare_Background_()

    def _update_height(self):
        _, height = self.GetWindowSizeForContentSize(height=self.main_cont.height)
        self.SetFixedHeight(height)


def is_suppressed():
    return settings.user.suppress.Get('suppress.{}'.format(MESSAGE_KEY), False)


def set_suppressed():
    settings.user.suppress.Set('suppress.{}'.format(MESSAGE_KEY), True)
