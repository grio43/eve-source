#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\singlelineedits\singleLineEditHistory.py
from carbonui.primitives.container import Container
from carbonui import uiconst
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from eve.client.script.ui.control.eveLabel import Label

class SingleLineEditHistory(Container):
    default_name = 'historyMenuParent'
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.dynamicHistoryWidth = attributes.dynamicHistoryWidth
        self.historyMenuSub = self.sr.entries = Container(name='historyMenuSub', parent=self)
        self.mouseDownFunc = attributes.mouseDownFunc
        self.mouseUpFunc = attributes.mouseUpFunc
        self.currentText = attributes.currentText
        Frame(parent=self, frameConst=uiconst.FRAME_BORDER1_CORNER0, color=(1.0, 1.0, 1.0, 0.2))
        Frame(parent=self, frameConst=uiconst.FRAME_FILLED_CORNER0, color=(0.0, 0.0, 0.0, 0.75))

    def PopulateHistoryMenu(self, history):
        for entry in history:
            historyEntry = EditHistoryEntry(parent=self.historyMenuSub, displayText=entry.displayText, editText=entry.editText, info=entry.info, mouseDownFunc=self.mouseDownFunc, mouseUpFunc=self.mouseUpFunc, historyEntry=entry.historyEntry)
            historyEntry.sr.menu = self
            self.height += historyEntry.height
            if self.historyMenuSub:
                self.width = max(self.width, historyEntry.textWidth)

    def GetSelectedEntry(self):
        for _entry in self.sr.entries.children:
            _entry.sr.hilite.display = False
            if _entry.selected:
                return _entry

    def GetTextEntered(self):
        return self.currentText


class EditHistoryEntry(Container):
    default_name = 'entryParent'
    default_clipChildren = True
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_height = 16

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        displayText = attributes.displayText
        editText = attributes.editText
        info = attributes.info
        historyEntry = attributes.historyEntry
        self.mouseDownFunc = attributes.mouseDownFunc
        self.mouseUpFunc = attributes.mouseUpFunc
        t = Label(text=displayText, parent=self, left=6, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
        self.height = t.textheight + 4
        self.textWidth = t.width + 12
        self.sr.hilite = Fill(parent=self, color=(1.0, 1.0, 1.0, 0.25), pos=(1, 1, 1, 1), state=uiconst.UI_DISABLED)
        self.sr.hilite.display = False
        Line(parent=self, align=uiconst.TOBOTTOM)
        self.selected = 0
        self.string = editText
        self.info = info
        self.historyEntry = historyEntry

    def OnMouseDown(self, mouseButton, *args):
        self.mouseDownFunc(self, mouseButton)

    def OnMouseUp(self, mouseButton, *args):
        self.mouseUpFunc(self, mouseButton)

    def OnMouseEnter(self, *args):
        hm = self.sr.menu
        if not hm or hm.destroyed:
            return
        for _entry in hm.sr.entries.children:
            _entry.sr.hilite.display = False
            _entry.selected = 0

        self.sr.hilite.display = True
        self.selected = 1
