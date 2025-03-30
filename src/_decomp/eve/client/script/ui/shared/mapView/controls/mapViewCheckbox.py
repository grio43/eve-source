#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\controls\mapViewCheckbox.py
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import const as uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.control.checkbox import Checkbox
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.eveLabel import EveLabelSmall

class MapViewCheckbox(SE_BaseClassCore):
    TEXTLEFT = 26
    TEXTRIGHT = 12
    TEXTTOPBOTTOM = 4

    def Startup(self, *args):
        self.label = EveLabelSmall(parent=self, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, left=self.TEXTLEFT)

    def Load(self, data):
        group = data.Get('group', None)
        if group:
            self.checkbox = RadioButton(align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, parent=self, pos=(4, 0, 16, 16), idx=0, callback=self.CheckBoxChange, groupname=group, retval=data.retval, checked=data.checked, settingsKey=data.cfgname)
        else:
            self.checkbox = Checkbox(align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, parent=self, pos=(4, 0, 16, 16), idx=0, callback=self.CheckBoxChange, checked=data.checked, settingsKey=data.cfgname)
        self.label.width = data.entryWidth - self.TEXTLEFT - self.TEXTRIGHT
        self.label.text = data.label
        self.hint = data.Get('hint', None)

    def CheckBoxChange(self, *args):
        self.sr.node.checked = self.checkbox.checked
        self.sr.node.OnChange(*args)

    def OnClick(self, *args):
        if not self or self.destroyed:
            return
        self.checkbox.OnClick(*args)

    def GetHeight(self, node, width):
        textWidth, textHeight = EveLabelSmall.MeasureTextSize(node.label, width=node.entryWidth - MapViewCheckbox.TEXTLEFT - MapViewCheckbox.TEXTRIGHT)
        return max(20, textHeight + MapViewCheckbox.TEXTTOPBOTTOM * 2)

    def OnCharSpace(self, enteredChar, *args):
        uthread.pool('checkbox::OnChar', self.OnClick, self)
        return 1

    def OnMouseEnter(self, *args):
        SE_BaseClassCore.OnMouseEnter(self, *args)
        self.checkbox.OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        SE_BaseClassCore.OnMouseExit(self, *args)
        self.checkbox.OnMouseExit(*args)

    def OnMouseDown(self, *args):
        self.checkbox.OnMouseDown(*args)

    def OnMouseUp(self, *args):
        self.checkbox.OnMouseUp(*args)
