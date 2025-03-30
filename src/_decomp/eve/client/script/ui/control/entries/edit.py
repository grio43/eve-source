#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\edit.py
import logging
from carbonui import Density, uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.util import uix
log = logging.getLogger(__name__)

class EditEntry(SE_BaseClassCore):
    __guid__ = 'listentry.Edit'
    __params__ = ['label']
    default_showHilite = False

    def Startup(self, args):
        Container(name='push', parent=self, height=3, align=uiconst.TOTOP)
        Container(name='push', parent=self, width=128, align=uiconst.TOLEFT)
        Container(name='push', parent=self, width=3, align=uiconst.TORIGHT)
        self.sr.label = EveLabelSmall(text='', parent=self, left=8, top=5, width=112, state=uiconst.UI_DISABLED)
        self.sr.edit = SingleLineEditText(name='textEdit', parent=self, align=uiconst.TOTOP, density=Density.COMPACT)

    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = self.sr.node.label
        if self.sr.node.Get('lines', 1) != 1:
            log.error('listentry.Edit is not multi line')
        if self.sr.node.Get('intmode', 0):
            minInt, maxInt = self.sr.node.intmode
            self.sr.edit.Close()
            self.sr.edit = SingleLineEditInteger(name='intEdit', parent=self, align=uiconst.TOTOP, minValue=minInt, maxValue=maxInt)
        elif self.sr.node.Get('floatmode', 0):
            minFloat, maxFloat = self.sr.node.floatmode
            self.sr.edit.Close()
            self.sr.edit = SingleLineEditFloat(name='floatEdit', parent=self, align=uiconst.TOTOP, minValue=minFloat, maxValue=maxFloat)
        if self.sr.node.Get('setValue', None) is None:
            self.sr.node.setValue = ''
        if self.sr.node.Get('hintText', None):
            self.sr.edit.SetHintText(self.sr.node.hintText)
        self.sr.edit.SetValue(self.sr.node.setValue)
        if self.sr.node.Get('maxLength', None):
            self.sr.edit.SetMaxLength(self.sr.node.maxLength)
        if self.sr.node.Get('name', ''):
            self.sr.edit.name = self.sr.node.name
        self.sr.edit.OnChange = self.OnChange
        self.sr.node.GetValue = self.sr.edit.GetValue

    def OnChange(self, *args):
        if self is not None and not self.destroyed and self.sr.node is not None:
            self.sr.node.setValue = self.sr.edit.GetValue()

    def GetHeight(self, *args):
        node, width = args
        node.height = max(22, uix.GetTextHeight(node.label, width=112)) + 6
        return node.height
