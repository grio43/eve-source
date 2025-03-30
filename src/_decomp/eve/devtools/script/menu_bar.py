#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\menu_bar.py
from carbonui import TextColor, uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control import eveLabel

class MenuBar(ContainerAutoSize):

    def __init__(self, parent = None, align = uiconst.TOTOP, on_size_changed = None):
        super(MenuBar, self).__init__(parent=parent, align=align, height=24, callback=on_size_changed)

    def AddMenu(self, text, entries):
        if not callable(entries):
            entries = lambda _entries = entries: _entries
        MenuBarItem(parent=self, align=uiconst.TOLEFT, text=text, callback=entries)


class MenuBarItem(ContainerAutoSize):
    expandOnLeft = True
    ignore_command_blocker = True

    def __init__(self, text, callback, parent = None, align = uiconst.TOPLEFT):
        self._text = text
        self._callback = callback
        super(MenuBarItem, self).__init__(parent=parent, align=align, alignMode=uiconst.TOLEFT, state=uiconst.UI_NORMAL, minHeight=24, cursor=uiconst.UICURSOR_POINTER_MENU)
        self._label = eveLabel.EveLabelMedium(parent=ContainerAutoSize(parent=self, align=uiconst.TOLEFT, padding=(8, 0, 8, 0)), align=uiconst.CENTERLEFT, text=self._text, color=TextColor.SECONDARY)
        self._hover = Fill(bgParent=self, align=uiconst.TOALL, color=eveColor.WHITE, opacity=0.0)

    def OnMouseEnter(self, *args):
        if self._hover is not None:
            animations.FadeIn(self._hover, endVal=0.1, duration=0.1)
        if self._label is not None:
            self._label.color = eveThemeColor.THEME_FOCUS.rgba

    def OnMouseExit(self, *args):
        if self._hover is not None:
            animations.FadeOut(self._hover, duration=0.3)
        if self._label is not None:
            self._label.color = TextColor.SECONDARY

    def GetMenu(self):
        return self._callback()

    def GetMenuPosition(self, element):
        return (self.absoluteLeft, self.absoluteBottom)
