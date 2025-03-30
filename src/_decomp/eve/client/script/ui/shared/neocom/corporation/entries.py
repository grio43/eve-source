#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\entries.py
from carbonui import ButtonVariant, uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button

class TwoButtons(SE_BaseClassCore):
    __guid__ = 'listentry.TwoButtons'
    __params__ = ['label',
     'caption1',
     'caption2',
     'OnClick1',
     'OnClick2']
    default_showHilite = False
    ENTRYHEIGHT = 36

    def Startup(self, args):
        self.sr.button1 = Button(parent=self, label='', align=uiconst.CENTERRIGHT, left=2, variant=ButtonVariant.GHOST)
        self.sr.button2 = Button(parent=self, label='', align=uiconst.CENTERRIGHT, variant=ButtonVariant.GHOST)
        self.sr.label = eveLabel.EveLabelMedium(name='label', text='', parent=self, align=uiconst.CENTERLEFT, left=8, state=uiconst.UI_DISABLED)

    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = self.sr.node.label
        self.sr.button1.OnClick = lambda *args: self.sr.node.OnClick1(*(self.sr.node.Get('args1', (None,)), (self.sr.button1,)))
        self.sr.button1.SetLabel(self.sr.node.caption1)
        self.sr.button2.OnClick = lambda *args: self.sr.node.OnClick2(*(self.sr.node.Get('args2', (None,)), (self.sr.button2,)))
        self.sr.button2.SetLabel(self.sr.node.caption2)
        self.sr.button2.left = self.sr.button1.left + self.sr.button1.width + 2
