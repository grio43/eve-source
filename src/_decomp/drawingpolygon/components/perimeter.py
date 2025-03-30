#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\drawingpolygon\components\perimeter.py
from drawingpolygon.drawingelement import DrawingElement
from carbonui.primitives.vectorlinetrace import VectorLineTrace, CORNERTYPE_NONE
from signals import Signal
import trinity

class PolygonSegment(VectorLineTrace):
    default_cornerType = CORNERTYPE_NONE
    default_spriteEffect = trinity.TR2_SFX_FILL_AA

    def ApplyAttributes(self, attributes):
        super(PolygonSegment, self).ApplyAttributes(attributes)
        self.on_removed = Signal(signalName='on_removed')

    def Close(self):
        self.on_removed()
        super(PolygonSegment, self).Close()

    def is_available(self):
        return self.renderObject is not None

    def execute_only_if_available(function):

        def wrapper(self, *args, **kwargs):
            if self.is_available():
                return function(self, *args, **kwargs)

        return wrapper

    @execute_only_if_available
    def add_vertex(self, x, y):
        self.AddPoint(pos=(x, y), color=self.color.GetRGBA())

    @execute_only_if_available
    def remove_vertex(self, index):
        self.RemovePoint(index)

    @execute_only_if_available
    def update_vertex(self, index, x, y):
        self.UpdatePoint(index, x, y)


class PolygonPerimeter(DrawingElement, PolygonSegment):
    pass
