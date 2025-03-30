#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\HistoryBar.py
import string
from carbonui.control.button import Button
from eve.client.script.ui.control import eveLabel
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from eve.devtools.script.uiControlCatalog.sample import Sample
VALUES = ['A', 'B', 'C']
ALLOWED_VALUES = list(string.ascii_uppercase)[3:]

def get_label_text(value):
    return 'Selected value = %s' % (value if value else 'NA')


def get_value_to_add():
    if ALLOWED_VALUES:
        newValue = ALLOWED_VALUES.pop(0)
    return newValue


class Sample1(Sample):
    name = 'Basic'

    def construct_sample(self, parent):
        mainCont = Container(name='mainCont', parent=parent, align=uiconst.TOPLEFT, width=400, height=100)
        self.sample_code(mainCont)

    def sample_code(self, parent):
        from eve.client.script.ui.control.historyBar import HistoryController
        from eve.client.script.ui.control.historyBar import HistoryBar
        historyValueLabel = eveLabel.EveLabelMedium(parent=parent, align=uiconst.TOTOP, text='')
        historyController = HistoryController(history=VALUES, overwriteHistory=False)

        def AddToHistory(*args):
            historyController.AddToHistory(get_value_to_add())

        Button(name='AddToHistory', align=uiconst.TOPRIGHT, parent=parent, label='Add to History', func=AddToHistory)

        def OnValueAdded(value, *args):
            historyValueLabel.text = get_label_text(value)

        HistoryBar(parent=parent, align=uiconst.CENTERBOTTOM, callback=OnValueAdded, historyController=historyController, width=100)
        historyValueLabel.text = get_label_text(historyController.GetHistoryFromLastLit())


class Sample2(Sample):
    name = 'Overwrite History'
    description = "If 'overwriteHistory=True', we branch off from the currently selected value"

    def construct_sample(self, parent):
        mainCont = Container(name='mainCont', parent=parent, align=uiconst.TOPLEFT, width=400, height=100)
        self.sample_code(mainCont)

    def sample_code(self, parent):
        from eve.client.script.ui.control.historyBar import HistoryController
        from eve.client.script.ui.control.historyBar import HistoryBar
        historyValueLabel = eveLabel.EveLabelMedium(parent=parent, align=uiconst.TOTOP, text='')
        historyController = HistoryController(history=VALUES, overwriteHistory=True)

        def AddToHistory(*args):
            historyController.AddToHistory(get_value_to_add())

        Button(name='AddToHistory', align=uiconst.TOPRIGHT, parent=parent, label='Add to History (overwrite)', func=AddToHistory)

        def OnValueAdded(value, *args):
            historyValueLabel.text = get_label_text(value)

        HistoryBar(parent=parent, align=uiconst.CENTERBOTTOM, callback=OnValueAdded, historyController=historyController, width=100)
        historyValueLabel.text = get_label_text(historyController.GetHistoryFromLastLit())
