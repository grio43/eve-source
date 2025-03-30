#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Patterns\CopyPaste.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def construct_sample(self, parent):
        cont = ContainerAutoSize(name='cont', parent=parent, align=uiconst.TOPLEFT, width=200)
        self.sample_code(cont)

    def sample_code(self, parent):
        import blue
        edit = SingleLineEditText(parent=parent, align=uiconst.TOTOP, hintText='Type here...')

        def copy_text(*args):
            blue.pyos.SetClipboardData(edit.GetText())
            ShowQuickMessage('Text copied to clipboard')

        Button(parent=parent, align=uiconst.TOTOP, padTop=8, label='Copy text to clipboard', func=copy_text)
