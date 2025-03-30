#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\button.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import Density, fontconst, uiconst
from carbonui.button import styling
from carbonui.control.button import Button
from carbonui.control.scrollentries import SE_BaseClassCore
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.util import uix

class ButtonEntry(SE_BaseClassCore):
    __guid__ = 'listentry.Button'
    __params__ = ['label', 'caption', 'OnClick']
    default_showHilite = False

    def Startup(self, args):
        self.sr.label = EveLabelMedium(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=8, maxLines=1)
        self.sr.button = Button(parent=self, align=uiconst.CENTERRIGHT, label='', idx=0, density=Density.COMPACT)

    def Load(self, node):
        self.sr.node = node
        self._showHilite = node.get('showHilite', self.default_showHilite)
        maxLines = node.Get('maxLines', 1)
        self.sr.label.maxLines = maxLines
        btnWidth = 0
        if self.sr.node.Get('OnClick', None):
            self.sr.button.OnClick = (self.OnButtonClicked,)
            self.sr.button.SetLabel(self.sr.node.caption)
            self.sr.button.state = uiconst.UI_NORMAL
            btnWidth = self.sr.button.width
        else:
            self.sr.button.state = uiconst.UI_HIDDEN
        if maxLines != 1:
            l, t, w, h = self.GetAbsolute()
            self.sr.label.width = w - btnWidth - self.sr.label.left * 2
        self.sr.label.text = self.sr.node.label

    def OnButtonClicked(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        args = self.sr.node.Get('args', (None,))
        return self.sr.node.OnClick(*(args + (self.sr.button,)))

    def GetHeight(self, *args):
        node, width = args
        if node.Get('OnClick', None):
            btnLabelWidth = uix.GetTextWidth(node.caption, fontsize=fontconst.EVE_MEDIUM_FONTSIZE)
            btnWidth = min(256, max(48, btnLabelWidth + 24))
            btnHeight = styling.get_height(Density.COMPACT)
        else:
            btnWidth = 0
            btnHeight = 0
        maxLines = node.Get('maxLines', 1)
        if maxLines == 1:
            mainLabelHeight = uix.GetTextHeight(node.label, fontsize=fontconst.EVE_MEDIUM_FONTSIZE, maxLines=1)
            node.height = max(16, mainLabelHeight + 4, btnHeight + 4)
        else:
            width = node.Get('entryWidth', 100) - btnWidth
            mainLabelHeight = uix.GetTextHeight(node.label, width=width, fontsize=fontconst.EVE_MEDIUM_FONTSIZE)
            node.height = max(16, mainLabelHeight + 4, btnHeight + 4)
        return node.height
