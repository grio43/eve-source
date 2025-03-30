#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\header\caption.py
from carbonui import uiconst
from carbonui.primitives.base import ReverseScaleDpi
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveLabel

class WindowCaption(Container):

    def __init__(self, parent, text, font_size, color, state = uiconst.UI_DISABLED, padding = None):
        self._label = None
        super(WindowCaption, self).__init__(parent=parent, align=uiconst.TOLEFT, state=state, padding=padding)
        self._label = eveLabel.Label(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, text=text, fontsize=font_size, maxLines=1, autoFadeSides=24, color=color)

    @property
    def text(self):
        if self._label is not None:
            return self._label.text

    @text.setter
    def text(self, value):
        if self._label is not None:
            self._label.text = value

    @property
    def color(self):
        if self._label is not None:
            if hasattr(self._label.color, 'GetRGBA'):
                return self._label.color.GetRGBA()
            else:
                return self._label.color

    @color.setter
    def color(self, value):
        if self._label is not None:
            self._label.color = value

    @property
    def font_size(self):
        if self._label is not None:
            return self._label.fontsize

    @font_size.setter
    def font_size(self, value):
        if self._label is not None:
            self._label.fontsize = value

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        result = super(WindowCaption, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
        if not updateChildrenOnly:
            self.width = min(self._label.width, max(ReverseScaleDpi(budgetWidth) - self.padLeft - self.padRight, 0))
            if self._alignmentDirty:
                result = super(WindowCaption, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
        return result
