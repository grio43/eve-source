#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\Text\EditPlainText.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from eve.client.script.ui.control.eveEditPlainText import EditPlainText
        EditPlainText(name='myTextEdit', parent=parent, align=uiconst.TOPLEFT, width=250, height=200, setvalue='Edit this text')


class Sample2(Sample):
    name = 'Submitting text'

    def construct_sample(self, parent):
        cont = ContainerAutoSize(parent=parent, align=uiconst.TOPLEFT, width=250)
        self.sample_code(cont)

    def sample_code(self, parent):
        from eve.client.script.ui.control.eveEditPlainText import EditPlainText

        def submit(text):
            ShowQuickMessage(text)

        edit = EditPlainText(name='myTextEdit', parent=parent, align=uiconst.TOTOP, height=200, setvalue='Edit this text')
        Button(name='submitBtn', parent=parent, align=uiconst.TOTOP, padTop=4, label='Submit', func=lambda x: submit(edit.GetValue()))


class Sample3(Sample):
    name = 'Formatting controls'

    def sample_code(self, parent):
        from eve.client.script.ui.control.eveEditPlainText import EditPlainText
        EditPlainText(name='myTextEdit', parent=parent, align=uiconst.TOPLEFT, width=250, height=200, setvalue='Edit this text', showattributepanel=True)
