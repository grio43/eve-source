#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawingtool.py
from projectdiscovery.client.projects.covid.ui.drawingtooldecorations import DrawingToolDecorations
from carbonui import uiconst
from drawingpolygon import DrawingArea, do_any_segments_intersect, do_polygons_intersect, is_point_inside_polygon

class DrawingTool(DrawingArea):

    def ApplyAttributes(self, attributes):
        super(DrawingTool, self).ApplyAttributes(attributes)
        self.line_markers_decoration = DrawingToolDecorations(name='line_markers_decoration', parent=self, align=uiconst.CENTER, idx=0)
        self.is_enabled = True
        self.on_polygons_changed.connect(self.line_markers_decoration.update_clusters_marked)

    def SetSize(self, width, height):
        super(DrawingTool, self).SetSize(width, height)
        self.line_markers_decoration.SetSize(self.width, self.height)

    def Enable(self, *args):
        super(DrawingArea, self).Enable(*args)
        self.is_enabled = True
        self.enable_markers()

    def Disable(self, *args):
        super(DrawingArea, self).Disable(*args)
        self.is_enabled = False
        self.disable_markers()

    def enable_markers(self):
        self.line_markers_decoration.Enable()

    def disable_markers(self):
        self.line_markers_decoration.Disable()

    def invalidate(self, invalid_polygons):
        self.content.invalidate_polygons(invalid_polygons)

    def _get_completed_polygons(self):
        return [ polygon for polygon in self.content.polygons if polygon.is_complete ]

    def _has_no_polygons(self):
        return not self._get_completed_polygons()

    def _has_crossings(self, invalid_polygons):
        has_crossings = False
        for polygon in self._get_completed_polygons():
            points = [ (vertex.x, -vertex.y) for vertex in polygon.vertices ]
            if do_any_segments_intersect(points):
                has_crossings = True
                invalid_polygons.add(polygon.order)

        return has_crossings

    def _has_polygons_inside_others(self, invalid_polygons):
        has_intersections = False
        for polygon_1 in self._get_completed_polygons():
            for polygon_2 in self._get_completed_polygons():
                if polygon_1.order != polygon_2.order:
                    points_1 = [ (vertex.x, -vertex.y) for vertex in polygon_1.vertices ]
                    points_2 = [ (vertex.x, -vertex.y) for vertex in polygon_2.vertices ]
                    for x, y in points_1:
                        if is_point_inside_polygon(x, y, points_2):
                            has_intersections = True
                            invalid_polygons.add(polygon_1.order)
                            invalid_polygons.add(polygon_2.order)
                            break

        return has_intersections

    def _has_segment_intersections(self, invalid_polygons):
        has_intersections = False
        for polygon_1 in self._get_completed_polygons():
            for polygon_2 in self._get_completed_polygons():
                if polygon_1.order != polygon_2.order:
                    points_1 = [ (vertex.x, -vertex.y) for vertex in polygon_1.vertices ]
                    points_2 = [ (vertex.x, -vertex.y) for vertex in polygon_2.vertices ]
                    if do_polygons_intersect(points_1, points_2):
                        has_intersections = True
                        invalid_polygons.add(polygon_1.order)
                        invalid_polygons.add(polygon_2.order)

        return has_intersections

    def _has_intersections(self, invalid_polygons):
        has_segment_intersections = self._has_segment_intersections(invalid_polygons)
        has_polygons_inside_others = self._has_polygons_inside_others(invalid_polygons)
        return has_segment_intersections or has_polygons_inside_others

    def validate(self):
        invalid_polygons = set()
        has_no_polygons = self._has_no_polygons()
        has_crossings = self._has_crossings(invalid_polygons)
        has_intersections = self._has_intersections(invalid_polygons)
        is_valid = not has_no_polygons and not has_crossings and not has_intersections
        return (is_valid,
         has_no_polygons,
         has_crossings,
         has_intersections,
         invalid_polygons)
