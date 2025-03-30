#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\drawingpolygon\drawingelement.py
from drawingpolygon.cursors import CURSOR_SELECTOR_POSITION
from carbonui import uiconst
from carbonui.primitives.sprite import TexturedBase
from signals.signal import Signal

class DrawingElement(TexturedBase):
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_idx = 0
    default_cursor = CURSOR_SELECTOR_POSITION
    default_draggingCursor = None

    def ApplyAttributes(self, attributes):
        super(DrawingElement, self).ApplyAttributes(attributes)
        self.polygon = attributes.get('polygon')
        self.dragging_cursor = attributes.get('draggingCursor', self.default_draggingCursor)
        self.base_cursor = self.cursor
        self.is_dragging = False
        self.is_hovering = False
        self.is_left_click_down = False
        self.on_left_clicked = Signal(signalName='on_left_clicked')
        self.on_right_clicked = Signal(signalName='on_right_clicked')
        self.on_drag_started = Signal(signalName='on_drag_started')
        self.on_drag_ended = Signal(signalName='on_drag_ended')
        self.on_hover_started = Signal(signalName='on_hover_started')
        self.on_hover_ended = Signal(signalName='on_hover_ended')

    def OnMouseDown(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self.is_left_click_down = True

    def OnMouseMove(self, *args):
        if self.is_left_click_down and not self.is_dragging:
            self.is_dragging = True
            if self.dragging_cursor:
                self.set_cursor(self.dragging_cursor)
            self.on_drag_started(self)

    def OnMouseUp(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self.is_left_click_down = False
            if self.is_dragging:
                self.is_dragging = False
                if self.dragging_cursor:
                    self.reset_cursor()
                self.on_drag_ended(self)
            else:
                self.on_left_clicked(self)
        elif button == uiconst.MOUSERIGHT:
            self.on_right_clicked(self)

    def OnMouseEnter(self, *args):
        if not self.is_hovering:
            self.is_hovering = True
            self.on_hover_started()

    def OnMouseExit(self, *args):
        if self.is_hovering:
            self.is_hovering = False
            self.on_hover_ended()

    def set_base_cursor(self, cursor):
        self.base_cursor = cursor

    def set_dragging_cursor(self, cursor):
        self.dragging_cursor = cursor

    def set_cursor(self, cursor):
        self.cursor = cursor

    def reset_cursor(self):
        self.cursor = self.base_cursor
