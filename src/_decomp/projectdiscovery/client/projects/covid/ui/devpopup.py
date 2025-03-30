#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\devpopup.py
import carbonui.const as uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui.control.window import Window

class FixTaskIdDevPopup(Window):
    __guid__ = 'form.FixTaskIdDevPopup'
    default_width = 240
    default_height = 90
    default_minSize = (default_width, default_height)
    default_windowID = 'FixTaskIdDevPopup'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Confirm, cancelFunc=self.Cancel)
        self.input = None
        self.caption = 'Fix taskID'
        self.text = 'Enter a task ID to fix, or 0 to reset'
        self.SetCaption(self.caption)
        self.MakeUnResizeable()
        self.ConstructLayout()

    def ConstructLayout(self):
        edit_container = Container(parent=self.sr.main, align=uiconst.TOALL, padding=(4, 16, 4, 4))
        self.edit = SingleLineEditText(name='edit', parent=edit_container, label=self.text, align=uiconst.TOTOP)
        uicore.registry.SetFocus(self.edit)

    def Confirm(self, *args):
        try:
            input = int(self.edit.GetValue())
            sm = ServiceManager.Instance()
            sm.RemoteSvc('ProjectDiscovery').fix_task_id(input)
        except TypeError:
            eve.Message('CustomInfo', {'info': 'TaskID needs to be an integer'})

        self.Close()

    def Cancel(self, *args):
        self.Close()
