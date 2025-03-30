#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\Text\SingleLineEdit.py
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.button import Button
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Text'

    def sample_code(self, parent):
        from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
        SingleLineEditText(name='myTextEdit', parent=parent, align=uiconst.TOPLEFT, width=250, hintText='My Text field', label='My Text')


class Sample2(Sample):
    name = 'Integer'

    def sample_code(self, parent):
        from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
        SingleLineEditInteger(name='myIntInput', parent=parent, align=uiconst.TOPLEFT, width=250, label='My Integer field', hintText='Pick a number', maxValue=100)


class Sample3(Sample):
    name = 'Float'

    def sample_code(self, parent):
        from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
        SingleLineEditFloat(name='myFloatInput', parent=parent, align=uiconst.TOPLEFT, width=250, label='My Float field', hintText='Pick a number', maxValue=100000.5)


class Sample4(Sample):
    name = 'Password'

    def construct_sample(self, parent):
        cont = ContainerAutoSize(name='cont', parent=parent, align=uiconst.TOPLEFT, width=250)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.control.singlelineedits.singleLineEditPassword import SingleLineEditPassword

        def OnSubmitButton(text):
            ShowQuickMessage('Password: %s' % passwordEdit.GetValue())

        passwordEdit = SingleLineEditPassword(name='myPasswordEdit', parent=parent, align=uiconst.TOTOP, passwordCharacter=u'\u2022')
        Button(name='submitButton', parent=parent, align=uiconst.TOTOP, padTop=4, label='Submit', func=lambda x: OnSubmitButton(passwordEdit.GetValue()))


class Sample5(Sample):
    name = 'Market Price'
    description = 'Float input field representing ISK amounts, will round to market ticks'

    def sample_code(self, parent):
        from eve.client.script.ui.shared.market.singleLineEditMarketPrice import SingleLineEditMarketPrice
        SingleLineEditMarketPrice(name='myMarketPriceInputNew', parent=parent, align=uiconst.TOTOP, width=250, hintText='Put in a number and a decimal', setvalue=123456.78)
