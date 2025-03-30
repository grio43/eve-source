#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawingtooldecorations.py
import carbonui.const as uiconst
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import Label
from localization import GetByLabel
from math import pi
from projectdiscovery.client.projects.covid.ui.linemarkers import LineMarkersDecoration
CORNER_WIDTH = 8
CORNER_HEIGHT = 8
CORNER_LEFT = 15
CORNER_TEXTURE_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/covid/corner_decoration.png'
GRID_WIDTH = 28
GRID_HEIGHT = 28
GRID_LEFT = 44
GRID_TOP = 44
GRID_TEXTURE_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/covid/grid_decoration.png'
CLUSTERS_MARKED_FONTSIZE = 12
CLUSTERS_MARKED_COLOR = (0.96, 0.96, 0.96, 1.0)
CLUSTERS_MARKED_RIGHT = 15
CLUSTERS_MARKED_BOTTOM = 15
CLUSTERS_MARKED_LABEL_PATH = 'UI/ProjectDiscovery/Covid/ClustersMarked'
LINE_COLOR = (1.0, 1.0, 1.0, 1.0)
LINE_HEIGHT = 5

class DrawingToolDecorations(LineMarkersDecoration):

    def ApplyAttributes(self, attributes):
        super(DrawingToolDecorations, self).ApplyAttributes(attributes)
        self._add_corners()
        self._add_grids()
        self._add_clusters_marked()
        self._add_bottom_line()

    def _add_corners(self):
        topright_corner = Sprite(name='topright_corner', parent=self, align=uiconst.TOPRIGHT, width=CORNER_WIDTH, height=CORNER_HEIGHT, left=CORNER_LEFT, top=CORNER_LEFT, texturePath=CORNER_TEXTURE_PATH, state=uiconst.UI_DISABLED)
        bottomleft_corner = Sprite(name='bottomleft_corner', parent=self, align=uiconst.BOTTOMLEFT, width=CORNER_WIDTH, height=CORNER_HEIGHT, left=CORNER_LEFT, top=CORNER_LEFT, texturePath=CORNER_TEXTURE_PATH, rotation=pi, state=uiconst.UI_DISABLED)
        self.corners = [topright_corner, bottomleft_corner]

    def _add_grids(self):
        topleft_grid = Sprite(name='topleft_grid', parent=self, align=uiconst.TOPRIGHT, width=GRID_WIDTH, height=GRID_HEIGHT, left=GRID_LEFT, top=GRID_TOP, texturePath=GRID_TEXTURE_PATH, state=uiconst.UI_DISABLED)
        topright_grid = Sprite(name='topright_grid', parent=self, align=uiconst.TOPLEFT, width=GRID_WIDTH, height=GRID_HEIGHT, left=GRID_LEFT, top=GRID_TOP, texturePath=GRID_TEXTURE_PATH, state=uiconst.UI_DISABLED)
        bottomleft_grid = Sprite(name='bottomleft_grid', parent=self, align=uiconst.BOTTOMLEFT, width=GRID_WIDTH, height=GRID_HEIGHT, left=GRID_LEFT, top=GRID_TOP, texturePath=GRID_TEXTURE_PATH, rotation=pi, state=uiconst.UI_DISABLED)
        bottomright_grid = Sprite(name='bottomright_grid', parent=self, align=uiconst.BOTTOMRIGHT, width=GRID_WIDTH, height=GRID_HEIGHT, left=GRID_LEFT, top=GRID_TOP, texturePath=GRID_TEXTURE_PATH, rotation=pi, state=uiconst.UI_DISABLED)
        self.grids = [topleft_grid,
         topright_grid,
         bottomleft_grid,
         bottomright_grid]

    def _add_clusters_marked(self):
        self.clusters_marked = Label(name='clusters_marked', parent=self, align=uiconst.BOTTOMRIGHT, fontsize=CLUSTERS_MARKED_FONTSIZE, color=CLUSTERS_MARKED_COLOR, left=CLUSTERS_MARKED_RIGHT, top=CLUSTERS_MARKED_BOTTOM, state=uiconst.UI_DISABLED)
        self.update_clusters_marked(0)

    def _add_bottom_line(self):
        self.bottom_line = Line(name='bottom_line', parent=self, align=uiconst.TOBOTTOM, height=LINE_HEIGHT, color=LINE_COLOR, state=uiconst.UI_DISABLED)

    def update_clusters_marked(self, number_of_clusters):
        if self.is_enabled:
            self.clusters_marked.SetText(GetByLabel(CLUSTERS_MARKED_LABEL_PATH, numberOfClusters=number_of_clusters))
