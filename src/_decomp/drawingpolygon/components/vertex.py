#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\drawingpolygon\components\vertex.py
from drawingpolygon.drawingelement import DrawingElement
from drawingpolygon.operations import are_points_within_distance
from carbonui.primitives.sprite import Sprite
VERTEX_SIZE = 16
VERTEX_OVERLAP_RANGE = 16

class PolygonVertex(DrawingElement, Sprite):
    default_width = VERTEX_SIZE
    default_height = VERTEX_SIZE
    default_draggingTexturePath = None

    def ApplyAttributes(self, attributes):
        super(PolygonVertex, self).ApplyAttributes(attributes)
        self.order = attributes.get('order')
        self.dragging_texture = attributes.get('draggingTexturePath', self.default_draggingTexturePath)
        self.base_texture = self.texturePath
        self.update_position(x=attributes.get('x'), y=attributes.get('y'))

    def update_position(self, x, y):
        self.x = x
        self.y = y
        self.left = x - VERTEX_SIZE / 2
        self.top = y - VERTEX_SIZE / 2

    def set_texture(self, texture_path):
        self.SetTexturePath(texture_path)

    def set_base_texture(self, texture_path):
        self.base_texture = texture_path
        self.reset_texture()

    def reset_texture(self):
        self.SetTexturePath(self.base_texture)

    def is_within_range(self, other_vertex):
        point_1 = [self.x, self.y]
        point_2 = [other_vertex.x, other_vertex.y]
        return are_points_within_distance(point_1, point_2, VERTEX_OVERLAP_RANGE)

    def OnMouseMove(self, *args):
        super(PolygonVertex, self).OnMouseMove(*args)
        if self.dragging_texture and self.is_dragging:
            self.set_texture(self.dragging_texture)

    def OnMouseUp(self, *args):
        super(PolygonVertex, self).OnMouseUp(*args)
        if self.dragging_texture and not self.is_dragging:
            self.reset_texture()
