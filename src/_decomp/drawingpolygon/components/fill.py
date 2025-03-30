#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\drawingpolygon\components\fill.py
from drawingpolygon.drawingelement import DrawingElement
from carbonui.primitives.base import ScaleDpi
from carbonui.primitives.polygon import Polygon as UiPolygon

class PolygonFill(DrawingElement, UiPolygon):

    def ApplyAttributes(self, attributes):
        super(PolygonFill, self).ApplyAttributes(attributes)
        self.is_complete = False

    def is_available(self):
        return self.renderObject is not None

    def execute_only_if_available(function):

        def wrapper(self, *args, **kwargs):
            if self.is_available():
                return function(self, *args, **kwargs)

        return wrapper

    @execute_only_if_available
    def add_vertex(self, x, y):
        self.AddPoint(ScaleDpi(x), ScaleDpi(y), self.color.GetRGBA())

    @execute_only_if_available
    def remove_vertex(self, index):
        self.RemovePoint(index)
        if self.is_complete:
            self.Triangulate()

    @execute_only_if_available
    def update_vertex(self, index, x, y):
        self.UpdatePoint(index, ScaleDpi(x), ScaleDpi(y))
        if self.is_complete:
            self.Triangulate()

    @execute_only_if_available
    def complete(self):
        self.is_complete = True
        self.Triangulate()
