#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\radioButtonMessageBox.py
import uthread
import localization
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import CaptionLabel
from eve.client.script.ui.shared.messagebox import MessageBox
from eve.client.script.ui.util import uix

class RadioButtonMessageBox(MessageBox):
    __guid__ = 'form.RadioButtonMessageBox'
    __nonpersistvars__ = ['suppress']

    def Execute(self, text, title, buttons, icon, suppText, customicon = None, height = None, default = None, modal = True, cancelLabel = None, isClosable = True, width = None, radioOptions = None):
        height = height or 280
        width = width or 340
        self.HideHeader()
        self.SetMinSize([width, height])
        self.width = width
        self.height = height
        self.GetMainArea().padding = 16
        iconTexturePath = customicon or uix.GetDialogIconTexturePath(icon)
        self.icon = iconTexturePath
        self.SetTopIcon(iconTexturePath)
        if title is None:
            title = localization.GetByLabel('UI/Common/Information')
        eveLabel.EveCaptionLarge(parent=ContainerAutoSize(parent=self.topParent, align=uiconst.TOLEFT, left=8), align=uiconst.CENTERLEFT, text=title, width=300)
        self.radioButtonContainer = ContainerAutoSize(name='radioContainer', parent=self.sr.main, align=uiconst.TOBOTTOM, padding=(0, 8, 0, 8))
        if text:
            self._message_scroll = ScrollContainer(parent=self.content, align=uiconst.TOALL, padBottom=8)
            self.edit = self._message_label = eveLabel.EveLabelMedium(parent=self._message_scroll, align=uiconst.TOTOP, text=text, tabs=list((16 * i for i in range(1, 9))))
        if radioOptions:
            self.radioboxID = 'radioButtonMessageBox_%s' % repr(title)
            radioSelection = settings.user.ui.Get(self.radioboxID, 'radioboxOption1Selected')
            for index, label in enumerate(radioOptions):
                RadioButton(parent=self.radioButtonContainer, text=label, settingsKey=self.radioboxID, retval='radioboxOption%dSelected' % (index + 1), checked='radioboxOption%dSelected' % (index + 1) == radioSelection, groupname=self.radioboxID, callback=self.OnCheckboxChange)

        if suppText:
            self.ShowSupp(suppText)
        self.DefineButtons(buttons, default=default)
        if modal:
            uicore.registry.SetFocus(self)
        scroll_size_fraction = self._message_scroll._scrollbar_vertical.handle_size_fraction
        self.height = min(int(round(0.8 * uicore.desktop.height)), max(self.GetMinHeight(), self.height + self._message_label.height * (1.0 - scroll_size_fraction)))

    def OnCheckboxChange(self, radioButton, *args):
        settings.user.ui.Set(radioButton.GetSettingsKey(), radioButton.GetReturnValue())

    def GetRadioSelection(self):
        return settings.user.ui.Get(self.radioboxID, 'radioboxOption1Selected')
