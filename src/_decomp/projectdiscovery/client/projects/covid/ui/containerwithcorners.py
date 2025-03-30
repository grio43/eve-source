#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\containerwithcorners.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from math import pi
CORNER_ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/covid/corner_decoration.png'
CORNER_ICON_SIZE = 4

class ContainerWithCorners(Container):
    default_shouldShowLeftCorners = True
    default_shouldShowRightCorners = True
    default_shouldShowTopCorners = True
    default_shouldShowBottomCorners = True

    def ApplyAttributes(self, attributes):
        super(ContainerWithCorners, self).ApplyAttributes(attributes)
        self.should_show_left_corners = attributes.get('shouldShowLeftCorners', self.default_shouldShowLeftCorners)
        self.should_show_right_corners = attributes.get('shouldShowRightCorners', self.default_shouldShowRightCorners)
        self.should_show_top_corners = attributes.get('shouldShowTopCorners', self.default_shouldShowTopCorners)
        self.should_show_bottom_corners = attributes.get('shouldShowBottomCorners', self.default_shouldShowBottomCorners)
        if self.should_show_left_corners:
            if self.should_show_top_corners:
                self.add_corner('top_left', uiconst.TOPLEFT, -pi / 2)
            if self.should_show_bottom_corners:
                self.add_corner('bottom_left', uiconst.BOTTOMLEFT, 0)
        if self.should_show_right_corners:
            if self.should_show_top_corners:
                self.add_corner('top_right', uiconst.TOPRIGHT, pi)
            if self.should_show_bottom_corners:
                self.add_corner('bottom_right', uiconst.BOTTOMRIGHT, pi / 2)

    def add_corner(self, name, align, rotation):
        Sprite(name='corner_%s' % name, parent=self, align=align, width=CORNER_ICON_SIZE, height=CORNER_ICON_SIZE, texturePath=CORNER_ICON_TEXTURE_PATH, rotation=rotation)
