#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\divider.py
import mathext
from carbonui import Axis, AxisAlignment, uiconst
from carbonui.decorative.resize_handle import ResizeHandle
from carbonui.primitives.container import Container
from carbonui.uicore import uicore

def axis_from_legacy_xory(xory):
    if xory == 'x':
        return Axis.HORIZONTAL
    if xory == 'y':
        return Axis.VERTICAL


class Divider(Container):
    _axis = None
    _drag_start_x = None
    _drag_start_y = None
    _dragging = False
    _property_name = None
    _property_value_initial = None
    _property_value_max = None
    _property_value_min = None
    _target = None
    _line = None

    def __init__(self, show_line = False, cross_axis_alignment = AxisAlignment.CENTER, **kwargs):
        super(Divider, self).__init__(**kwargs)
        self._handle = ResizeHandle(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, orientation=Axis.HORIZONTAL, show_line=show_line, cross_axis_alignment=cross_axis_alignment)

    @property
    def cross_axis_alignment(self):
        return self._handle.cross_axis_alignment

    @cross_axis_alignment.setter
    def cross_axis_alignment(self, value):
        self._handle.cross_axis_alignment = value

    @property
    def min(self):
        return self._property_value_min

    @min.setter
    def min(self, value):
        self._property_value_min = value

    @property
    def max(self):
        return self._property_value_max

    @max.setter
    def max(self, value):
        self._property_value_max = value

    @property
    def show_line(self):
        return self._handle.show_line

    @show_line.setter
    def show_line(self, value):
        self._handle.show_line = value

    def Close(self):
        self.OnSizeChanged = None
        self.OnSizeChanging = None
        self.OnSizeChangeStarting = None
        super(Divider, self).Close()

    def Startup(self, victim, attribute, xory, minValue = 1, maxValue = 1600):
        self._target = victim
        self._property_name = attribute
        self._axis = axis_from_legacy_xory(xory)
        self._handle.orientation = self._get_handle_orientation()
        self.SetMinMax(minValue, maxValue)
        if self._axis == Axis.HORIZONTAL:
            self.cursor = uiconst.UICORSOR_HORIZONTAL_RESIZE
        else:
            self.cursor = uiconst.UICORSOR_VERTICAL_RESIZE

    def _get_handle_orientation(self):
        if self._axis == Axis.HORIZONTAL:
            return Axis.VERTICAL
        if self._axis == Axis.VERTICAL:
            return Axis.HORIZONTAL

    def OnMouseDown(self, *args):
        self._dragging = True
        self.OnSizeChangeStarting(self)
        self._drag_start_x = uicore.uilib.x
        self._drag_start_y = uicore.uilib.y
        self._property_value_initial = getattr(self._target, self._property_name, 0)

    def OnMouseUp(self, *args):
        self._dragging = False
        self.OnSizeChanged()

    def SetMinMax(self, minValue = None, maxValue = None):
        if minValue is not None:
            self.min = minValue
        if maxValue is not None:
            self.max = maxValue

    def OnMouseMove(self, *args):
        self._handle.OnMouseMove(*args)
        if self._dragging:
            delta = 0
            if self._axis == Axis.HORIZONTAL:
                delta = uicore.uilib.x - self._drag_start_x
            elif self._axis == Axis.VERTICAL:
                delta = uicore.uilib.y - self._drag_start_y
            if self._target.align in (uiconst.TOBOTTOM, uiconst.TORIGHT):
                delta = -delta
            new_property_value = mathext.clamp(value=self._property_value_initial + delta, low=self.min, high=self.max)
            setattr(self._target, self._property_name, new_property_value)
            self.OnSizeChanging()

    def OnMouseEnter(self, *args):
        self._handle.OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        self._handle.OnMouseExit(*args)

    def OnSizeChangeStarting(self, *args):
        pass

    def OnSizeChanged(self, *args):
        pass

    def OnSizeChanging(self, *args):
        pass
