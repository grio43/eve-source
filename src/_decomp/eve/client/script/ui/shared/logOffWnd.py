#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\logOffWnd.py
import carbonui.const as uiconst
from carbonui import ButtonVariant
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.window import Window
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold
from eve.client.script.ui.shared.loginRewards.reminderCont import ReminderCont
from localization import GetByLabel
import log

class LogOffWnd(Window):
    __guid__ = 'LogOffWnd'
    default_windowID = 'message'
    default_height = 188
    default_alwaysLoadDefaults = True
    default_scope = uiconst.SCOPE_ALL
    default_isMinimizable = False
    default_isCollapseable = False
    default_isLockable = False
    default_isOverlayable = False
    default_isStackable = False
    default_isLightBackgroundConfigurable = False
    default_fixedWidth = 380
    default_width = default_fixedWidth
    default_minSize = [default_fixedWidth, default_height]
    default_iconNum = 'res:/UI/Texture/WindowIcons/quitGame.png'

    def ApplyAttributes(self, attributes):
        super(LogOffWnd, self).ApplyAttributes(attributes)
        self.suppress = 0
        self.name = 'modal'
        self.edit = None
        self.yesBtn = None
        self.msgKey = attributes.get('msgKey', None)
        self.MakeUnResizeable()
        self.mainCont = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, callback=self.OnRewardSectionUpdated)
        self.rewardSection = ContainerAutoSize(name='rewardSection', parent=self.mainCont, align=uiconst.TOTOP)
        self.msgLabel = EveLabelMediumBold(parent=self.mainCont, align=uiconst.TOTOP, top=16)
        self.bottomCont = ContainerAutoSize(name='bottomCont', parent=self.mainCont, align=uiconst.TOTOP, top=16)
        self.buttonCont = ContainerAutoSize(name='buttonCont', parent=self.bottomCont, align=uiconst.TOTOP)
        self.suppressCont = ContainerAutoSize(name='suppressContainer', parent=self.bottomCont, align=uiconst.TOTOP, padding=(0, 0, 0, 8), idx=0)

    def Prepare_Background_(self):
        super(LogOffWnd, self).Prepare_Background_()

    def Execute(self, text, title, buttons, icon, suppText, customicon = None, height = None, default = None, modal = True, okLabel = None, cancelLabel = None, isClosable = True):
        if title is None:
            title = GetByLabel('UI/Common/Information')
        self.SetCaption(title)
        self.msgLabel.text = '<center>%s</center>' % text
        self.DefineButtons(buttons, default=default, okLabel=okLabel, cancelLabel=cancelLabel)
        if suppText:
            self.ShowSupp(suppText)
        self.suppressCont.display = bool(suppText)
        if modal:
            if self.yesBtn:
                uicore.registry.SetFocus(self.yesBtn)
            else:
                uicore.registry.SetFocus(self)
        if session.charid:
            self.rewardSection.display = True
            self.LoadClaimCont()
        else:
            self.rewardSection.display = False

    def DefineButtons(self, *args, **kwargs):
        btnGroup = ButtonGroup(parent=self.buttonCont, align=uiconst.TOTOP, button_size_mode=ButtonSizeMode.STRETCH)
        self.yesBtn = Button(parent=btnGroup, label=GetByLabel('UI/Common/Buttons/Yes'), func=self.ClickYes, variant=ButtonVariant.PRIMARY)
        Button(parent=btnGroup, label=GetByLabel('UI/Common/Buttons/No'), func=self.ClickNo)

    def ShowSupp(self, text):
        self.sr.suppCheckbox = Checkbox(text=text, parent=self.suppressCont, configName='suppress', retval=0, checked=0, groupname=None, callback=self.ChangeSupp, align=uiconst.CENTERLEFT)
        self.suppressCont.height = max(20, self.sr.suppCheckbox.height)

    def ChangeSupp(self, sender):
        self.suppress = sender.checked

    def OnSuppLabelClicked(self, *args):
        self.sr.suppCheckbox.ToggleState()

    def CloseByUser(self, *etc):
        if self.isModal:
            self.SetModalResult(uiconst.ID_CLOSE)
        else:
            super(LogOffWnd, self).CloseByUser(*etc)

    def ClickYes(self, *args, **kwargs):
        if self.isModal:
            self.SetModalResult(uiconst.ID_YES)

    def ClickNo(self, *args, **kwargs):
        if self.isModal:
            self.SetModalResult(uiconst.ID_NO)

    def LoadClaimCont(self):
        try:
            self.rewardSection.Flush()
            self.rewardSection.display = True
            padLeft, _, padRight, _ = self.GetContentToWindowEdgePadding()
            ReminderCont(parent=self.rewardSection, parentWidth=self.width - padLeft - padRight, align=uiconst.TOTOP)
        except StandardError:
            log.LogException()
            self.rewardSection.display = False

    def OnRewardSectionUpdated(self):
        heightBefore = self.height
        _, newHeight = self.GetWindowSizeForContentSize(height=self.mainCont.height)
        self.SetMinSize(size=(self.GetMinWidth(), newHeight), refresh=True)
        heightChange = self.height - heightBefore
        self.top = max(0, self.top - heightChange / 2)
