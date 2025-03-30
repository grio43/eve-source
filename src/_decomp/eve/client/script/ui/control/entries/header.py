#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\header.py
from carbonui import uiconst
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.fill import Fill
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.util import uix

class Header(SE_BaseClassCore):
    __guid__ = 'listentry.Header'
    __params__ = ['label']
    default_showHilite = False

    def Startup(self, args):
        self.sr.label = EveLabelMedium(text='', parent=self, left=8, top=0, state=uiconst.UI_DISABLED, maxLines=1, align=uiconst.CENTERLEFT)
        self.sr.mainFill = Fill(parent=self, opacity=0.05, padBottom=1)

    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = self.sr.node.label

    def GetHeight(self, *args):
        node, width = args
        node.height = max(uicore.font.GetTextHeight(node.label, maxLines=1), HEIGHT_NORMAL)
        return node.height

    @classmethod
    def GetCopyData(cls, node):
        return node.label


class Subheader(SE_BaseClassCore):
    __guid__ = 'listentry.Subheader'
    __params__ = ['label']
    default_showHilite = False

    def Startup(self, args):
        self.sr.label = EveLabelMedium(text='', parent=self, left=8, top=0, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, bold=True)
        self.sr.fill = FillThemeColored(parent=self, padding=(1, 1, 1, 1), colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.125)

    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = self.sr.node.label
        sublevel = node.sublevel or 0
        offset = sublevel * 16
        self.sr.label.left = 8 + offset

    def GetHeight(self, *args):
        node, width = args
        node.height = uix.GetTextHeight(node.label, maxLines=1) + 6
        return node.height
