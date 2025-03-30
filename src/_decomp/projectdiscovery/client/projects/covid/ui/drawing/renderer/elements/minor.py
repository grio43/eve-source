#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\renderer\elements\minor.py
from carbonui import uiconst
from carbonui.primitives import line
from carbonui.primitives import container
from projectdiscovery.client.projects.covid.ui.drawing.renderer.elements import colors
import logging
log = logging.getLogger('projectdiscovery.covid.renderer.minor')

class BottomLine(line.Line):
    default_name = 'bottom_line'
    default_weight = 1
    default_color = colors.WHITE.as_tuple
    default_state = uiconst.UI_DISABLED


class Corner(container.Container):
    ORIENTATION_SW = 1
    ORIENTATION_NW = 2
    ORIENTATION_NE = 3
    ORIENTATION_SE = 4
    default_name = 'corner'
    default_width = 20
    default_height = 20
    default_orientation = ORIENTATION_NE
    default_line_thickness = 1
    default_line_color = colors.WHITE.as_tuple
    default_state = uiconst.UI_DISABLED

    def __init__(self, width = 20, height = 20, line_thickness = 1, line_color = None, orientation = None, **attributes):
        log.warning('orientation2=%r', orientation)
        self.vertical_line = None
        self.horizontal_line = None
        super(Corner, self).__init__(width=width, height=height, line_thickness=line_thickness, line_color=line_color, orientation=orientation, **attributes)

    def ApplyAttributes(self, attributes):
        log.warning('attributes=%r', attributes)
        super(Corner, self).ApplyAttributes(attributes)
        log.warning('attributes2=%r', attributes)
        thickness = attributes.get('line_thickness', self.default_line_thickness)
        line_color = attributes.get('line_color', self.default_line_color)
        line_height = attributes.get('height', self.default_height) / 2.0
        line_width = attributes.get('width', self.default_width) / 2.0
        orientation = attributes.get('orientation', self.default_orientation)
        log.warning('orientation=%r', orientation)
        if orientation == self.ORIENTATION_SW:
            align = uiconst.BOTTOMLEFT
        elif orientation == self.ORIENTATION_NW:
            align = uiconst.TOPLEFT
        elif orientation == self.ORIENTATION_SE:
            align = uiconst.BOTTOMRIGHT
        else:
            align = uiconst.TOPRIGHT
        self.horizontal_line = line.Line(parent=self, color=line_color, align=align, width=line_width, height=thickness)
        self.vertical_line = line.Line(parent=self, color=line_color, align=align, width=thickness, height=line_height)
