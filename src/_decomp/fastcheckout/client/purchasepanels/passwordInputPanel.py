#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fastcheckout\client\purchasepanels\passwordInputPanel.py
from carbonui import const as uiconst
from carbonui.control.singlelineedits.singleLineEditPassword import SingleLineEditPassword
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.linkLabel import LinkLabel
from fastcheckout.client.purchasepanels.purchaseButton import PurchaseButton
from localization import GetByLabel
LABEL_LEFT_INDENT = 6
PADDING_TOP = 15
PADDING_INSTRUCTIONS_TO_PASSWORD_INPUT = 15
PADDING_PASSWORD_INPUT_TO_FORGOT_LINK = 6
PADDING_BOTTOM_TO_PURCHASE_BUTTON = 30
HEIGHT_PASSWORD_INPUT = 35
PURCHASE_BUTTON_WIDTH = 200
PURCHASE_BUTTON_HEIGHT = 35
FONTSIZE_INSTRUCTIONS = 14
FONTSIZE_FORGOT_PASSWORD = 13
LABEL_PATH_INSTRUCTIONS = 'UI/FastCheckout/PasswordLabel'
LABEL_PATH_PASSWORD_HINT = 'UI/FastCheckout/PasswordHint'
LABEL_PATH_FORGOT_PASSWORD = 'UI/FastCheckout/ForgotPasswordLabel'
LABEL_PATH_PURCHASE_BUTTON = 'UI/FastCheckout/Purchase'
LABEL_PATH_WRONG_PASSWORD = 'UI/FastCheckout/WrongPasswordLabel'

class PasswordInputPanel(Container):
    default_name = 'PasswordInputPanel'
    default_opacity = 0
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(PasswordInputPanel, self).ApplyAttributes(attributes)
        self.enter_password_func = attributes.get('enter_password_func', None)
        self.forgot_password_func = attributes.get('forgot_password_func', None)
        self.close_func = attributes.get('close_func', None)
        self._add_instructions()
        self._add_password_input()
        self._add_forgot_password_link()
        self._add_purchase_button()
        self._connect_actions()
        self.is_ready = False

    def _add_instructions(self):
        self.instructions_label = Label(name='instructions_label', parent=self, align=uiconst.TOTOP, text=GetByLabel(LABEL_PATH_INSTRUCTIONS), fontsize=FONTSIZE_INSTRUCTIONS, padTop=PADDING_TOP, padLeft=LABEL_LEFT_INDENT)

    def _add_password_input(self):
        input_container = Container(name='password_input_container', parent=self, state=uiconst.UI_NORMAL, align=uiconst.TOTOP, height=HEIGHT_PASSWORD_INPUT, padTop=PADDING_INSTRUCTIONS_TO_PASSWORD_INPUT)
        self.password_input = SingleLineEditPassword(name='password_input', parent=input_container, align=uiconst.TOALL, bgColor=Color.WHITE, fontcolor=Color.BLACK, width=0, top=0, autoselect=True, maxLength=128, caretColor=Color.ORANGE, selectColor=(0.5, 0.5, 0.5, 0.5), hintText=GetByLabel(LABEL_PATH_PASSWORD_HINT))

    def _add_forgot_password_link(self):
        forgot_password_container = ContainerAutoSize(name='forgot_password_container', parent=self, align=uiconst.TOTOP, padTop=PADDING_PASSWORD_INPUT_TO_FORGOT_LINK)
        LinkLabel(name='forgot_password_label', parent=forgot_password_container, align=uiconst.TOPLEFT, text=GetByLabel(LABEL_PATH_FORGOT_PASSWORD), fontsize=FONTSIZE_FORGOT_PASSWORD, state=uiconst.UI_NORMAL, padLeft=LABEL_LEFT_INDENT, function=lambda *args: (self.forgot_password_func() if callable(self.forgot_password_func) else None))

    def _add_purchase_button(self):
        purchase_button_container = ContainerAutoSize(name='purchase_button_container', parent=self, align=uiconst.TOBOTTOM, padBottom=PADDING_BOTTOM_TO_PURCHASE_BUTTON)
        self.purchase_button = PurchaseButton(name='purchase_button', parent=purchase_button_container, align=uiconst.TOPRIGHT, width=PURCHASE_BUTTON_WIDTH, height=PURCHASE_BUTTON_HEIGHT, text=GetByLabel(LABEL_PATH_PURCHASE_BUTTON))

    def _connect_actions(self):
        self.purchase_button.Disable()
        self.password_input.OnChange = lambda *args: self._update_purchase_button_state()
        if callable(self.enter_password_func):
            confirm_password_function = lambda *args: self.enter_password_func(self.password_input.GetValue())
            self.password_input.OnReturn = confirm_password_function
            self.purchase_button.func = confirm_password_function

    def _update_purchase_button_state(self):
        if self.password_input.GetValue():
            self.purchase_button.Enable()
        else:
            self.purchase_button.Disable()

    def notify_of_wrong_password(self):
        self.instructions_label.SetText(GetByLabel(LABEL_PATH_WRONG_PASSWORD))
        self.instructions_label.SetTextColor(Color.RED)

    def set_password(self, password):
        self.password_input.SetValue(password)

    def get_password(self):
        return self.password_input.GetValue()

    def AnimEntry(self):
        animations.FadeIn(self, duration=0.5, callback=self.SetReady)

    def AnimExit(self):
        animations.FadeOut(self, callback=super(PasswordInputPanel, self).Close, duration=0.5)

    def IsReady(self):
        return self.is_ready

    def SetReady(self):
        self.is_ready = True

    def Close(self):
        if callable(self.close_func):
            self.close_func()
        super(PasswordInputPanel, self).Close()
