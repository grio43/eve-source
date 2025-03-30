#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\renderer\elements\vertex.py
from carbonui import uiconst
from carbonui.primitives import fill
from carbonui.primitives import container
from projectdiscovery.client.projects.covid.ui.drawing.renderer.elements import colors
import logging
log = logging.getLogger('projectdiscovery.covid.renderer.vertex')
VERTEX_SIZE = 7
VERTEX_SIZE_INNER = 5
VERTEX_SHIFT_SIZE = (VERTEX_SIZE - 1) / 2
VERTEX_STYLE_DEFAULT = 1
VERTEX_STYLE_OPEN = 2
VERTEX_STYLE_ACTIVE = 3
VERTEX_STYLE_INVALID = 4

class Vertex(container.Container):
    default_name = 'vertex'
    default_state = uiconst.UI_NORMAL
    default_idx = 0
    default_align = uiconst.BOTTOMLEFT
    default_cursor = 'res:/UI/Cursor/DrawingTool/selector_target.png'
    default_height = VERTEX_SIZE
    default_width = VERTEX_SIZE
    default_padding = (-VERTEX_SHIFT_SIZE,
     VERTEX_SHIFT_SIZE,
     VERTEX_SHIFT_SIZE,
     -VERTEX_SHIFT_SIZE)
    default_vertex_style = VERTEX_STYLE_DEFAULT

    def __init__(self, polygon_uuid = None, vertex_index = None, mouse_enter_callback = None, vertex_style = None, **attributes):
        self.vertex_style = vertex_style or Vertex.default_vertex_style
        self.outer = None
        self.inner = None
        self.polygon_uuid = polygon_uuid
        self.vertex_index = vertex_index
        self.mouse_enter_callback = mouse_enter_callback
        super(Vertex, self).__init__(vertex_style=self.vertex_style, **attributes)

    def ApplyAttributes(self, attributes):
        super(Vertex, self).ApplyAttributes(attributes)
        self.outer = fill.Fill(name='vertex_outer', parent=self, color=colors.PDC19_WHITE.as_tuple, align=uiconst.CENTER, width=VERTEX_SIZE, heigt=VERTEX_SIZE)
        vs = self.vertex_style
        self.vertex_style = -1
        self.update_style(vs)

    def update_style(self, new_style):
        if self.vertex_style != new_style:
            self.vertex_style = new_style
            if self.vertex_style == VERTEX_STYLE_OPEN:
                self._ensure_inner()
                self.outer.color = colors.PDC19_WHITE.as_tuple
                self.inner.color = colors.BLACK.as_tuple
            elif self.vertex_style == VERTEX_STYLE_ACTIVE:
                self._ensure_inner()
                self.outer.color = colors.CLEAR.as_tuple
                self.inner.color = colors.PDC19_WHITE.as_tuple
            elif self.vertex_style == VERTEX_STYLE_INVALID:
                self._ensure_inner()
                self.outer.color = colors.CLEAR.as_tuple
                self.inner.color = colors.PDC19_RED.as_tuple
            else:
                self.outer.color = colors.PDC19_WHITE.as_tuple
                if self.inner:
                    self.inner.color = colors.PDC19_WHITE.as_tuple

    def set_style_default(self):
        self.update_style(VERTEX_STYLE_DEFAULT)

    def set_style_active(self):
        self.update_style(VERTEX_STYLE_ACTIVE)

    def set_style_invalid(self):
        self.update_style(VERTEX_STYLE_INVALID)

    def set_style_open(self):
        self.update_style(VERTEX_STYLE_OPEN)

    def _ensure_inner(self):
        if not self.inner:
            self.inner = fill.Fill(name='vertex_inner', parent=self, align=uiconst.CENTER, idx=0, width=VERTEX_SIZE_INNER, height=VERTEX_SIZE_INNER, color=colors.CLEAR.as_tuple)

    def OnDragCanceled(self, dragSource, dragData):
        log.warning('%s:OnDragCanceled:self=%r, args=%r', self.__class__.__name__, self, dragSource, dragData)

    def OnDragEnter(self, dragSource, dragData):
        log.warning('%s:OnDragEnter:self=%r, args=%r', self.__class__.__name__, self, dragSource, dragData)

    def OnDragMove(self, dragSource, dragData):
        log.warning('%s:OnDragMove:self=%r, args=%r', self.__class__.__name__, self, dragSource, dragData)

    def OnDropData(self, dragSource, dragData):
        log.warning('%s:OnDropData:self=%r, args=%r', self.__class__.__name__, self, (dragSource, dragData))

    def OnEndDrag(self, dragSource, dropLocation, dragData):
        log.warning('%s:OnEndDrag:self=%r, args=%r', self.__class__.__name__, self, (dragSource, dropLocation, dragData))

    def OnDragExit(self, dragSource, dragData):
        log.warning('%s:OnDragExit:self=%r, args=%r', self.__class__.__name__, self, (dragSource, dragData))

    def OnExternalDragEnded(self, dragSource, dropLocation, dragData):
        log.warning('%s:OnExternalDragEnded:self=%r, args=%r', self.__class__.__name__, self, (dragSource, dropLocation, dragData))

    def OnExternalDragInitiated(self, dragSource, dragData):
        log.warning('%s:OnExternalDragInitiated:self=%r, dragSource=%r, dragData=%r', self.__class__.__name__, self, dragSource, dragData)

    def OnMouseUp(self, *args):
        log.warning('%s:OnMouseUp:self=%r, args=%r', self.__class__.__name__, self, args)

    def OnMouseDown(self, *args):
        log.warning('%s:OnMouseDown:self=%r, args=%r', self.__class__.__name__, self, args)

    def OnMouseEnter(self, *args):
        log.warning('%s:OnMouseEnter:self=%r, args=%r', self.__class__.__name__, self, args)
        if self.mouse_enter_callback:
            self.mouse_enter_callback(polygon_uuid=self.polygon_uuid, vertex_index=self.vertex_index)

    def OnMouseExit(self, *args):
        log.warning('%s:OnMouseExit:self=%r, args=%r', self.__class__.__name__, self, args)
        if self.mouse_enter_callback:
            self.mouse_enter_callback(polygon_uuid=self.polygon_uuid, vertex_index=self.vertex_index, is_exit=True)
