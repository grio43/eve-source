#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\baseScrollContEntry.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from signals import Signal

class LazyLoadVerticalMixin(object):
    is_loaded = False

    def check_lazy_load(self, clipper):
        if self.is_loaded or self.is_clipped_by(clipper):
            return False
        self.is_loaded = True
        self.lazy_load()
        return True

    def is_clipped_by(self, clipper):
        y_min = -self.parent.top
        y_max = y_min + clipper.displayHeight
        return self.displayY > y_max or self.displayY + self.displayHeight < y_min

    def lazy_load(self):
        pass


class BaseScrollContEntry(Container, LazyLoadVerticalMixin):
    default_name = 'BaseScrollContEntry'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOTOP
    default_fixedColor = None

    def ApplyAttributes(self, attributes):
        super(BaseScrollContEntry, self).ApplyAttributes(attributes)
        self.fixedColor = attributes.get('fixedColor', self.default_fixedColor)
        self.isSelected = False
        self.on_clicked = Signal(signalName='on_clicked')
        self.on_mouse_enter = Signal(signalName='on_mouse_enter')
        self.on_mouse_exit = Signal(signalName='on_mouse_exit')
        self.hoverBG = None

    def _check_construct_hover_bg(self):
        if self.hoverBG is None:
            self.hoverBG = ListEntryUnderlay(bgParent=self, color_override=self.fixedColor)

    def OnMouseEnter(self, *args):
        self._check_construct_hover_bg()
        self.hoverBG.hovered = True

    def OnMouseExit(self, *args):
        self._check_construct_hover_bg()
        self.hoverBG.hovered = False

    def OnClick(self, *args):
        self.on_clicked(self)

    def OnSelect(self):
        if not self.isSelected:
            self.isSelected = True
            self._check_construct_hover_bg()
            self.hoverBG.Select()

    def OnDeselect(self):
        if self.isSelected:
            self.isSelected = False
            self._check_construct_hover_bg()
            self.hoverBG.Deselect()
