#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\slimItemInspector.py
import eveformat
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.scroll import Scroll
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.primitives.container import Container
import carbonui
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
import blue

class SlimItemInspector(Window):
    __guid__ = 'slimItemInspector'
    default_windowID = 'SlimItemInspector'

    def ApplyAttributes(self, attributes):
        super(SlimItemInspector, self).ApplyAttributes(attributes)
        self.itemID = attributes.itemID
        self._updateThread = None
        self.SetCaption('Slim Item Inspector')
        self.lastSlimValues = {}
        Checkbox(parent=self.content, align=carbonui.Align.TOBOTTOM, text='Live update', checked=False, callback=self.ChangeLiveUpdates, hint='check if you want to see the values update')
        top = Container(name='top', parent=self.content, height=20, align=carbonui.Align.TOTOP)
        Button(parent=top, label='Refresh', align=carbonui.Align.TORIGHT, func=self.Refresh)
        self.input = SingleLineEditText(name='itemID', parent=top, width=-1, height=-1, align=carbonui.Align.TOALL)
        self.input.OnReturn = self.Refresh
        if self.itemID:
            self.input.SetValue(str(self.itemID))
        Container(name='div', parent=self.content, height=5, align=carbonui.Align.TOTOP)
        self.scroll = Scroll(parent=self.content)
        self.Refresh()

    def Refresh(self, *args):
        if self.destroyed:
            return
        inputValue = self.input.GetValue()
        bp = sm.StartService('michelle').GetBallpark()
        if not inputValue or not bp:
            self.scroll.Load(contentList=[], noContentHint='Nothing to show')
            return
        itemID = int(inputValue)
        slimItem = bp.GetInvItem(itemID)
        slimItemAttributes = []
        for k, v in slimItem.__dict__.items():
            if k.startswith('__'):
                continue
            slimItemAttributes.append((k, v))

        slimItemAttributes.sort()
        scrollList = []
        for fieldName, fieldValue in slimItem.__dict__.items():
            if k.startswith('__'):
                continue
            text = '%s<t>%s' % (fieldName, fieldValue)
            if fieldName not in self.lastSlimValues:
                text = eveformat.color(text, eveColor.SAND_YELLOW_HEX)
            elif fieldValue != self.lastSlimValues[fieldName]:
                text = '%s<t>%s' % (fieldName, eveformat.color(fieldValue, eveColor.SAND_YELLOW_HEX))
            data = {'label': text,
             'GetMenu': self.GetEntryMenu,
             'fieldName': fieldName,
             'fieldValue': fieldValue,
             'sort_fieldName': fieldName}
            entry = GetFromClass(Generic, data)
            scrollList.append((fieldName, entry))

        scrollList = SortListOfTuples(scrollList)
        self.lastSlimValues = {k:v for k, v in slimItem.__dict__.items() if not k.startswith('__')}
        self.scroll.Load(contentList=scrollList, headers=['fieldName', 'fieldValue'], fixedEntryHeight=18)

    def GetEntryMenu(self, entry):
        node = entry.sr.node
        m = MenuData()
        m.AddEntry('Copy Field name', func=lambda : blue.pyos.SetClipboardData(node.fieldName))
        m.AddEntry('Copy value', func=lambda : blue.pyos.SetClipboardData(unicode(node.fieldValue)))
        return m

    def ChangeLiveUpdates(self, cb):
        isChecked = cb.GetValue()
        if isChecked:
            self._updateThread = AutoTimer(500, self.Refresh)
        else:
            self._updateThread = None
