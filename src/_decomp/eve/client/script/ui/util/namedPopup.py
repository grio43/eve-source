#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\util\namedPopup.py
import localization
import carbonui.const as uiconst
from carbonui.control.singlelineedits.singleLineEditPassword import SingleLineEditPassword
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveLabel
from carbonui.button.group import ButtonGroup
from carbonui.control.window import Window
from carbonui.control.singlelineedits.prefixed import PrefixedSingleLineEdit
from eve.common.lib import appConst as const

class NamePopupWnd(Window):
    __guid__ = 'form.NamePopupWnd'
    default_width = 360
    default_height = 160
    default_minSize = (default_width, default_height)
    default_windowID = 'setNewName'
    default_maxLength = None
    default_body = None

    def ApplyAttributes(self, attributes):
        self._mainCont = None
        Window.ApplyAttributes(self, attributes)
        caption = attributes.get('caption', None)
        if caption is None:
            caption = localization.GetByLabel('UI/Common/Name/TypeInName')
        self.SetCaption(caption)
        self.MakeUnResizeable()
        self.label = attributes.get('label', None)
        if self.label is None:
            self.label = localization.GetByLabel('UI/Common/Name/TypeInName')
        self.body = attributes.get('body', self.default_body)
        self.setvalue = attributes.get('setvalue', '')
        self.maxLength = attributes.get('maxLength', self.default_maxLength)
        self.passwordChar = attributes.get('passwordChar', None)
        self.prefix = attributes.get('prefix', None)
        self.funcValidator = attributes.get('validator', None) or self.CheckName
        self.ConstructLayout()

    def ConstructLayout(self):
        self.AddMainContainer()
        self.AddBody(parent=self._mainCont)
        self.AddLabel()
        self.AddLineEdit(parent=self._mainCont, padding=0)
        self.AddExtra(parent=self._mainCont)
        self.AddButtons()
        uicore.registry.SetFocus(self.newName)

    def AddMainContainerOld(self):
        return Container(parent=self.sr.main, align=uiconst.TOALL, pos=(const.defaultPadding,
         16,
         const.defaultPadding,
         const.defaultPadding))

    def AddMainContainer(self):
        self._mainCont = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, callback=self._OnContentSizeChanged)

    def AddBody(self, parent):
        if not self.body:
            return
        leftPad, _, rightPad, _ = self.content_padding
        eveLabel.EveLabelMedium(parent=ContainerAutoSize(parent=parent, align=uiconst.TOTOP, padTop=8, padBottom=16), align=uiconst.TOPLEFT, text=self.body, width=self.width - leftPad - rightPad)

    def AddLabel(self):
        eveLabel.EveLabelMedium(parent=ContainerAutoSize(parent=self._mainCont, align=uiconst.TOTOP, padBottom=8), align=uiconst.TOPLEFT, text=self.label)

    def AddLineEdit(self, parent, padding):
        if self.prefix:
            editClass = PrefixedSingleLineEdit
        elif self.passwordChar:
            editClass = SingleLineEditPassword
        else:
            editClass = SingleLineEditText
        self.newName = editClass(name='namePopup', parent=parent, align=uiconst.TOTOP, setvalue=self.setvalue, maxLength=self.maxLength, passwordCharacter=self.passwordChar, autoselect=True, prefix=self.prefix, OnReturn=self.Confirm, padding=padding, showLetterCounter=bool(self.maxLength))

    def AddExtra(self, parent):
        pass

    def AddButtons(self):
        buttons = ButtonGroup(parent=ContainerAutoSize(parent=self._mainCont, align=uiconst.TOTOP, padTop=8), align=uiconst.CENTER)
        buttons.AddButton(label=localization.GetByLabel('UI/Common/Buttons/OK'), func=self.Confirm)
        buttons.AddButton(label=localization.GetByLabel('UI/Common/Buttons/Cancel'), func=self.Cancel)

    def _OnContentSizeChanged(self):
        _, self.height = self.GetWindowSizeForContentSize(height=self._mainCont.height)

    def CheckName(self, name, *args):
        name = self.newName.GetValue()
        if not len(name) or len(name) and len(name.strip()) < 1:
            return localization.GetByLabel('UI/Common/PleaseTypeSomething')

    def Confirm(self, *args):
        if not hasattr(self, 'newName'):
            return
        newName = self.newName.GetValue()
        error = self.funcValidator(newName)
        if error:
            eve.Message('CustomInfo', {'info': error})
        else:
            self.result = newName
            self.SetModalResult(1)

    def Cancel(self, *args):
        self.result = None
        self.SetModalResult(0)
