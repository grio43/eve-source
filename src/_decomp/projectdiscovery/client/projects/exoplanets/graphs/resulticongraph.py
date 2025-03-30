#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphs\resulticongraph.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from carbonui.graphs.axis import AxisOrientation
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
import random

class ResultIconGraph(Container):

    def ApplyAttributes(self, attributes):
        super(ResultIconGraph, self).ApplyAttributes(attributes)
        self._category_axis = attributes.get('categoryAxis')
        self._color = attributes.get('color', (1, 1, 1, 1))
        self._icon_path = attributes.get('iconPath', None)
        self._orientation = attributes.get('orientation', AxisOrientation.VERTICAL)
        self._tooltip_message = attributes.get('tooltipMessage', '')
        self._transit_intervals = attributes.get('transitIntervals')
        self._on_click = attributes.get('onClick')
        self._interval_mapping = attributes.get('intervalMapping')
        self._icons = []
        self._locked = False
        self._dirty = False
        self._is_animating = False
        self._category_axis.onChange.connect(self._axis_changed)
        self._build()

    def LockGraphUpdates(self):
        self._locked = True

    def UnlockGraphUpdates(self):
        if self._locked:
            self._locked = False
            if self._dirty:
                self._rescale()

    def Close(self):
        self._category_axis.onChange.disconnect(self._axis_changed)
        self._icons = []
        super(ResultIconGraph, self).Close()

    def _axis_changed(self, _):
        if self._locked:
            self._dirty = True
        else:
            self._rescale()

    def _build(self):
        vertices = self._get_vertex_positions()
        icon_width = 10
        icon_height = 10
        half_icon_width = 5
        for (x, y), interval in zip(vertices, self._transit_intervals):
            marker = self._interval_mapping.get(interval, None)
            icon = ButtonIcon(name='ResultIcon', parent=self, align=uiconst.BOTTOMLEFT, left=x - half_icon_width, width=icon_width, height=icon_height, iconSize=icon_width, texturePath=self._icon_path, iconColor=self._color, opacity=0, state=uiconst.UI_NORMAL, args=interval, func=self._on_click)
            if len(set(self._interval_mapping.values())) > 1 and marker is not None:
                Label(name='TransitNumber', parent=icon, top=-icon_height, text=marker.number, align=uiconst.CENTER)
            SetTooltipHeaderAndDescription(targetObject=icon, headerText='', descriptionText=self._tooltip_message)
            self._icons.append(icon)

        icons = [ icon for icon in self._icons ]
        random.shuffle(icons)
        offset = 0
        offset_delta = 1.0 / float(len(self._icons)) if len(self._icons) else 0
        for icon in icons:
            animations.BlinkIn(icon, timeOffset=offset)
            offset += offset_delta

    def _rescale(self):
        vertices = self._get_vertex_positions()
        for (x, y), icon in zip(vertices, self._icons):
            icon.left = x - 5

    def _get_vertex_positions(self):
        count = len(self._category_axis.get_actual_data_points())
        if self._orientation == AxisOrientation.VERTICAL:
            vertices = zip(self._category_axis.MapDataPointsToViewport(), [ self.displayHeight for i in xrange(count) ])
        else:
            vertices = zip([ 0 for i in xrange(count) ], self._category_axis.MapDataPointsToViewport())
        return vertices
