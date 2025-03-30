#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\messagebox.py
import carbonui
import localization
from carbonui import uiconst, Align, TextColor
from carbonui.control.checkbox import Checkbox
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.util import uix
ICON_BY_MSG_TYPE = {uiconst.INFO: 'res:/ui/Texture/WindowIcons/info.png',
 uiconst.WARNING: 'res:/ui/Texture/WindowIcons/warning.png',
 uiconst.QUESTION: 'res:/ui/Texture/WindowIcons/question.png',
 uiconst.ERROR: 'res:/ui/Texture/WindowIcons/stop.png',
 uiconst.FATAL: 'res:/UI/Texture/WindowICons/criminal.png'}

class MessageBox(Window):
    __guid__ = 'form.MessageBox'
    __nonpersistvars__ = ['suppress']
    default_windowID = 'message'
    default_width = 420
    default_height = 260
    default_alwaysLoadDefaults = True
    default_isStackable = False
    default_isLockable = False
    default_isOverlayable = False
    default_icon_size = 48
    edit = None
    _message_scroll = None
    _message_label = None

    def ApplyAttributes(self, attributes):
        super(MessageBox, self).ApplyAttributes(attributes)
        self.icon_size = attributes.get('icon_size', self.default_icon_size)
        self.suppress = 0
        self.name = 'modal'
        self.msgKey = attributes.get('msgKey', None)
        self.construct_layout()

    def construct_layout(self):
        self.construct_top_parent()
        self.construct_icon()

    def construct_top_parent(self):
        self.topParent = ContainerAutoSize(name='topParent', parent=self.content, align=Align.TOTOP, alignMode=Align.TOPLEFT, minHeight=48, clipChildren=True, padTop=16)

    def construct_icon(self):
        self.topIcon = Sprite(name='mainicon', parent=ContainerAutoSize(parent=self.topParent, align=Align.TOPLEFT, minHeight=48), align=Align.CENTER, state=uiconst.UI_DISABLED, width=self.icon_size, height=self.icon_size, texturePath=self.iconNum)

    def construct_caption(self, title):
        if title is None:
            title = localization.GetByLabel('UI/Common/Information')
        carbonui.TextHeadline(parent=self.topParent, padLeft=self.icon_size + 16, align=uiconst.VERTICALLY_CENTERED, text=title, color=TextColor.HIGHLIGHT)

    def construct_message_body(self, text):
        self._message_scroll = ScrollContainer(parent=self.content, align=uiconst.TOALL, padTop=16)
        self.edit = self._message_label = carbonui.TextBody(parent=self._message_scroll, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=text, tabs=list((16 * i for i in range(1, 9))))

    def Execute(self, text, title, buttons, icon, suppText, customicon = None, height = None, default = None, modal = True, okLabel = None, cancelLabel = None, isClosable = True):
        self._Execute(title, buttons, icon, suppText, customicon, height, default, modal, okLabel, cancelLabel, isClosable)
        if text:
            self.construct_message_body(text)

    def ExecuteCustomContent(self, customContentCls, title, buttons, icon, suppText, customicon = None, height = None, default = None, modal = True, okLabel = None, cancelLabel = None, messageData = None, isClosable = True):
        self._Execute(title, buttons, icon, suppText, customicon, height, default, modal, okLabel, cancelLabel, isClosable)
        customContent = customContentCls(parent=self.sr.main, padding=uiconst.defaultPadding, messageData=messageData, align=uiconst.TOTOP)
        height = customContent.GetContentHeight() + 80
        _, self.height = self.GetWindowSizeForContentSize(height=height)
        if getattr(customContent, 'forceMinHeight', False):
            minWidth = self.GetMinWidth()
            self.SetMinSize([minWidth, self.height])
        if getattr(customContent, 'setWidth', False):
            contentWidth = customContent.GetContentWidth()
            width, _ = self.GetWindowSizeForContentSize(width=contentWidth)
            self.width = max(self.width, width)

    def _Execute(self, title, buttons, icon, suppText, customicon, height, default, modal, okLabel, cancelLabel, isClosable):
        if height is None:
            height = self.default_height
        self.MakeUnMinimizable()
        self.HideHeader()
        self.SetMinSize((self.default_width, height))
        iconTexturePath = customicon or uix.GetDialogIconTexturePath(icon)
        self.icon = iconTexturePath
        self.SetTopIcon(iconTexturePath)
        self.construct_caption(title)
        self.DefineButtons(buttons, default=default, okLabel=okLabel, cancelLabel=cancelLabel)
        if suppText:
            self.ShowSupp(suppText)
        if modal:
            uicore.registry.SetFocus(self)
        if not isClosable:
            self.MakeUnKillable()

    def SetTopIcon(self, texturePath):
        if self.topIcon is not None:
            self.topIcon.texturePath = texturePath

    def ShowSupp(self, text):
        if self.sr.bottom is not None:
            index = self.sr.bottom.GetOrder() + 1
        else:
            index = 0
        bottom = ContainerAutoSize(name='suppressContainer', parent=self.content, align=uiconst.TOBOTTOM, padding=(0, 8, 0, 8), idx=index)
        Checkbox(parent=bottom, align=uiconst.TOTOP, pos=(0, 0, 0, 0), text=text, settingsKey='suppress', checked=0, callback=self.ChangeSupp)

    def ChangeSupp(self, sender):
        self.suppress = sender.checked

    def SetText(self, txt):
        self._message_label.text = txt
        self._message_scroll.ScrollToVertical(0.0)

    def CloseByUser(self, *etc):
        if self.isModal:
            self.SetModalResult(uiconst.ID_CLOSE)
        else:
            Window.CloseByUser(self)

    def ClickYes(self):
        if self.isModal:
            self.SetModalResult(uiconst.ID_YES)

    def ClickOk(self):
        if self.isModal:
            self.SetModalResult(uiconst.ID_OK)

    @classmethod
    def show_message_modal(cls, dialog_key, params = None, buttons = uiconst.OK, icon = None):
        wnd = cls(useDefaultPos=True, msgKey=dialog_key)
        wnd.state = uiconst.UI_HIDDEN
        wnd.isModal = True
        is_suppressed = settings.user.suppress.Get('suppress.' + dialog_key, None)
        if is_suppressed is not None:
            message_suppression = cfg.GetSuppressValueForMessage(dialog_key, params)
            if message_suppression is True or message_suppression is not False and is_suppressed == message_suppression:
                return is_suppressed
        msg = cfg.GetMessage(dialog_key, params, onNotFound='raise')
        icon = icon or msg.icon
        if icon is None:
            icon = ICON_BY_MSG_TYPE.get(msg.type, ICON_BY_MSG_TYPE.values()[0])
        title = msg.title
        if title is None:
            msgTitles = {'info': localization.GetByLabel('UI/Common/Information'),
             'infomodal': localization.GetByLabel('UI/Common/Information'),
             'warning': localization.GetByLabel('UI/Generic/Warning'),
             'question': localization.GetByLabel('UI/Common/Question'),
             'error': localization.GetByLabel('UI/Common/Error'),
             'fatal': localization.GetByLabel('UI/Common/Fatal')}
            title = msgTitles.get(msg.type, localization.GetByLabel('UI/Common/Information'))
        suppress_text = None
        if msg.suppress:
            if buttons in [None, uiconst.OK]:
                suppress_text = localization.GetByLabel('/Carbon/UI/Common/DoNotShowAgain')
            else:
                suppress_text = localization.GetByLabel('/Carbon/UI/Common/DoNotAskAgain')
        wnd.Execute(text=msg.text, title=title, buttons=buttons, icon=icon, suppText=suppress_text, modal=True, isClosable=msg.closable)
        ret = wnd.ShowModal()
        if wnd.suppress and ret not in (uiconst.ID_CLOSE, uiconst.ID_CANCEL):
            suppress = cfg.GetSuppressValueForMessage(dialog_key, params)
            if ret == suppress or suppress is True:
                settings.user.suppress.Set('suppress.' + dialog_key, ret)
                sm.GetService('settings').SaveSettings()
        return ret
