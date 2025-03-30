#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\checkbox.py
import carbonui.control.checkbox
import carbonui.control.radioButton
import uthread
from carbonui import uiconst
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.util import uix

class CheckboxEntry(Generic):
    __guid__ = 'listentry.Checkbox'
    __params__ = ['cfgname', 'retval']

    def Startup(self, *args):
        Generic.Startup(self, args)
        self.sr.label.top = 0
        self.sr.label.SetAlign(uiconst.CENTERLEFT)

    def Load(self, args):
        Generic.Load(self, args)
        data = self.sr.node
        group = data.Get('group', None)
        if group:
            self.sr.checkbox = carbonui.control.radioButton.RadioButton(align=uiconst.CENTERLEFT, pos=(0, 0, 16, 16), state=uiconst.UI_DISABLED, callback=self.CheckBoxChange, parent=self, idx=0, groupname=group, retval=data.retval, checked=data.checked, settingsKey=data.cfgname)
        else:
            self.sr.checkbox = carbonui.control.checkbox.Checkbox(align=uiconst.CENTERLEFT, pos=(0, 0, 16, 16), state=uiconst.UI_DISABLED, callback=self.CheckBoxChange, parent=self, idx=0, checked=data.checked, settingsKey=data.cfgname)
        self.sr.label.text = data.label
        self.sr.label.tabs = data.get('tabs', [])
        self.sr.checkbox.left = 4 + 16 * data.Get('sublevel', 0)
        self.sr.label.left = 24 + 16 * data.Get('sublevel', 0)
        self.sr.label.Update()

    def CheckBoxChange(self, cb):
        self.sr.node.checked = self.sr.checkbox.checked
        self.sr.node.OnChange(cb, self.sr.node)

    def GetHeight(self, *args):
        node, width = args
        height = CheckboxEntry.GetDynamicHeight(node, width)
        node.height = height
        return height

    def OnCharSpace(self, enteredChar, *args):
        uthread.pool('checkbox::OnChar', self.OnClick, self)
        return 1

    @staticmethod
    def GetDynamicHeight(node, width):
        height = max(19, uix.GetTextHeight(node.label, maxLines=1) + 4)
        return height

    def OnClick(self, *args):
        self.sr.checkbox.OnClick(*args)

    def OnMouseEnter(self, *args):
        super(CheckboxEntry, self).OnMouseEnter(*args)
        self.sr.checkbox.OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        super(CheckboxEntry, self).OnMouseExit(*args)
        self.sr.checkbox.OnMouseExit(*args)

    def OnMouseDown(self, *args):
        super(CheckboxEntry, self).OnMouseDown(*args)
        self.sr.checkbox.OnMouseDown(*args)

    def OnMouseUp(self, *args):
        super(CheckboxEntry, self).OnMouseUp(*args)
        self.sr.checkbox.OnMouseUp(*args)
