#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\comboEntries.py
from carbonui import uiconst, fontconst, TextColor
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.line import Line
from carbonui.text.color import TextColor
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.text import Text
from eve.client.script.ui.control.eveIcon import Icon

class ComboEntry(Generic):
    sound_select = uiconst.SOUND_BUTTON_CLICK
    labelLeftDefault = 8

    def Load(self, node):
        super(ComboEntry, self).Load(node)
        iconLeft = 8
        if node.icon is not None:
            if not self.sr.icon:
                self.sr.icon = Icon(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, pos=(iconLeft,
                 0,
                 16,
                 16), ignoreSize=True)
            self.sr.icon.texturePath = node.icon
            self.sr.icon.rgba = node.iconColor
            self.sr.label.left = 16 + 16
        else:
            self.sr.icon = None
        if node.indentLevel:
            left = node.indentLevel * 10
            if self.sr.icon:
                self.sr.icon.left = iconLeft + left
            self.sr.label.left += left
            self.sr.label.SetRGBA(*Color.GRAY7)

    def GetHeight(self, *args):
        return 32

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.sr.node.loadTooltipFunc:
            self.sr.node.loadTooltipFunc(tooltipPanel, *args)


class ComboCaptionEntry(Text):

    def ApplyAttributes(self, attributes):
        super(ComboCaptionEntry, self).ApplyAttributes(attributes)
        if self.GetOrder() > 0:
            Line(parent=self, align=uiconst.TOTOP)

    def _ConstructLabel(self):
        return eveLabel.EveLabelSmall(parent=self, left=8, top=4, color=TextColor.SECONDARY, maxLines=1, align=uiconst.CENTERLEFT)

    def GetHeight(self, *args):
        return 32


class ComboSeparatorEntry(SE_BaseClassCore):
    default_showHilite = False

    def ApplyAttributes(self, attributes):
        super(ComboSeparatorEntry, self).ApplyAttributes(attributes)
        Line(parent=self, align=uiconst.TOTOP, top=4, height=1)

    def Load(self, data):
        pass

    def GetHeight(self, *args):
        return 9
