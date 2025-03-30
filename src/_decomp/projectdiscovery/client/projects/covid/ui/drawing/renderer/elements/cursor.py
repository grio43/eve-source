#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\renderer\elements\cursor.py
from carbonui.primitives import container
from projectdiscovery.client.projects.covid.ui.drawing.renderer.elements import colors
from carbonui import const
from carbonui.primitives import sprite
RADIUS_GRID = 'res:/UI/Cursor/DrawingTool/scifi_radius_grid.png'
RADIUS_GRID_SIZE = 53

class SciFiCursorRadius(container.Container):
    default_height = 27
    default_width = 27
    default_align = const.BOTTOMLEFT
    default_state = const.UI_DISABLED
    default_color = colors.PDC19_BLUE.as_tuple

    def __init__(self, **attributes):
        self.cursor_radius = None
        super(SciFiCursorRadius, self).__init__(**attributes)

    def ApplyAttributes(self, attributes):
        super(SciFiCursorRadius, self).ApplyAttributes(attributes)
        self.cursor_radius = sprite.Sprite(parent=self, align=const.BOTTOMLEFT, width=RADIUS_GRID_SIZE, height=RADIUS_GRID_SIZE, left=-26, top=-26, texturePath=RADIUS_GRID, color=colors.PDC19_WHITE.opaque(0.6).as_tuple)

    def update(self, coord):
        self.SetPosition(*coord.as_tuple)

    def set_style_invalid(self):
        self.cursor_radius.color = colors.PDC19_RED.opaque(0.6).as_tuple

    def set_style_snapping(self):
        self.cursor_radius.color = colors.PDC19_WHITE.opaque(0.8).as_tuple

    def set_style_default(self):
        self.cursor_radius.color = colors.PDC19_BLUE.opaque(0.6).as_tuple
