#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmppchatclient\xmppchatpassword.py
import localization
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.singlelineedits.singleLineEditPassword import SingleLineEditPassword
from carbonui.control.window import Window
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.eveLabel import EveLabelMedium
CONTENT_WIDTH_MAX = 300

class ChannelPasswordWindow(Window):
    default_captionLabelPath = 'UI/Menusvc/PasswordRequired'
    default_isMinimizable = False
    default_isCollapseable = False

    def _on_main_cont_size_changed(self):
        width, height = self.GetWindowSizeForContentSize(width=CONTENT_WIDTH_MAX, height=self._main_cont.height)
        self.SetFixedWidth(width)
        self.SetFixedHeight(height)

    def ApplyAttributes(self, attributes):
        super(ChannelPasswordWindow, self).ApplyAttributes(attributes)
        self.title = attributes.title
        self.channel = attributes.channel
        self.displayName = attributes.displayName
        self.password = None
        settings.user.ui.Set('%sPassword' % self.channel, '')
        self._main_cont = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, callback=self._on_main_cont_size_changed, only_use_callback_when_size_changes=True)
        EveLabelMedium(parent=self._main_cont, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, text=attributes.title)
        if attributes.retry:
            passwordLabel = localization.GetByLabel('UI/Menusvc/PleaseTryEnteringPasswordAgain')
        else:
            passwordLabel = localization.GetByLabel('UI/Menusvc/PleaseEnterPassword')
        EveLabelMedium(parent=ContainerAutoSize(parent=self._main_cont, align=uiconst.TOTOP), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, top=16, text=passwordLabel)
        self.passwordEdit = SingleLineEditPassword(name='passwordEdit', parent=self._main_cont, align=uiconst.TOTOP, passwordCharacter=u'\u2022')
        self.rememberPwdCb = Checkbox(parent=self._main_cont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Chat/SavePassword'), settingsKey='rememberPwdCb', checked=0)
        self.btnGroup = ButtonGroup(parent=self._main_cont, align=uiconst.TOTOP, top=16)
        self.btnGroup.AddButton(localization.GetByLabel('UI/Chat/ChannelWindow/JoinChannel'), self.OnOK, ())
        self.btnGroup.AddButton(localization.GetByLabel('UI/Common/Cancel'), self.OnCancel, ())

    def OnOK(self, *args):
        password = self.passwordEdit.GetValue(raw=1)
        password = password.strip()
        if len(password) < 1:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Common/PleaseTypeSomething')})
            return
        self.password = password
        if self.rememberPwdCb.GetValue():
            settings.user.ui.Set('%sPassword' % self.channel, self.password)
        self.CloseByUser()

    def OnCancel(self, *args):
        self.password = None
        self.rememberPassword = False
        self.CloseByUser()
