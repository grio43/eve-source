#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\tabVertical.py
from carbonui import fontconst, uiconst
from carbonui.control.tab import Tab

class TabVertical(Tab):
    default_fontsize = fontconst.EVE_MEDIUM_FONTSIZE

    def _ConstructLabel(self):
        super(TabVertical, self)._ConstructLabel()
        self.label.align = uiconst.CENTER
        width, _ = self.GetAbsoluteSize()
        self.label.maxWidth = width - 2 * self.labelPadding

    def SetLabel(self, label, hint = None):
        super(TabVertical, self).SetLabel(label, hint)
