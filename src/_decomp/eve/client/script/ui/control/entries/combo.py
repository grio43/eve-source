#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\combo.py
from carbonui import Density, uiconst
from carbonui.control.combo import Combo
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.util import uix

class ComboEntry(SE_BaseClassCore):
    __guid__ = 'listentry.Combo'
    __params__ = ['OnChange', 'label', 'options']
    default_showHilite = False

    def Startup(self, args):
        Container(name='push', parent=self, height=5, align=uiconst.TOTOP, idx=0)
        self.sr.combo = Combo(parent=self, label='', options=[], name='', callback=self.OnComboChange, align=uiconst.TOTOP, density=Density.COMPACT)
        self.sr.push = Container(name='push', parent=self, width=128, align=uiconst.TOLEFT, idx=0)
        self.sr.label = EveLabelSmall(text='', parent=self, left=8, top=5, width=112, state=uiconst.UI_DISABLED)
        Container(name='push', parent=self, width=3, align=uiconst.TORIGHT, idx=0)

    def Load(self, node):
        self.sr.node = node
        self.sr.combo.LoadOptions(self.sr.node.options, self.sr.node.Get('setValue', None))
        self.sr.label.text = self.sr.node.label
        self.sr.push.width = max(128, self.sr.label.textwidth + 10)
        if self.sr.node.Get('name', ''):
            self.sr.combo.name = self.sr.node.name

    def OnComboChange(self, combo, header, value, *args):
        if self.sr.node.Get('settingsUser', 0):
            settings.user.ui.Set(self.sr.node.cfgName, value)
        self.sr.node.setValue = value
        self.sr.node.OnChange(combo, header, value)

    def GetHeight(self, *args):
        node, width = args
        node.height = max(22, uix.GetTextHeight(node.label, width=112)) + 6
        return node.height
