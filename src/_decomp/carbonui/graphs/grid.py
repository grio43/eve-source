#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\graphs\grid.py
import trinity
from carbonui import uiconst
from carbonui.graphs.axis import AxisOrientation
from carbonui.primitives.vectorlinetrace import VectorLineTrace, CORNERTYPE_NONE
from carbonui.text.color import TextColor
from carbonui.uicore import uicore

class Grid(VectorLineTrace):
    default_name = 'grid'
    default_align = uiconst.TOALL
    default_state = uiconst.UI_DISABLED
    default_lineWidth = 1
    default_spriteEffect = trinity.TR2_SFX_FILL
    default_cornerType = CORNERTYPE_NONE
    default_gridColor = TextColor.SECONDARY.rgba
    default_zeroColor = TextColor.NORMAL.rgba

    def ApplyAttributes(self, attributes):
        VectorLineTrace.ApplyAttributes(self, attributes)
        self._orientation = attributes['orientation']
        self._axis = attributes['axis']
        self._minFactor = attributes.get('minFactor', 0.0)
        self._maxFactor = attributes.get('maxFactor', 1.0)
        self.gridColor = attributes.get('gridColor', self.default_gridColor)
        self.zeroColor = attributes.get('zeroColor', self.default_zeroColor)
        self._axis.onChange.connect(self._Build)
        self._Build()

    def _GetTicks(self):
        width, height = self.GetAbsoluteSize()
        width *= uicore.dpiScaling
        height *= uicore.dpiScaling
        size = width if self._orientation == AxisOrientation.HORIZONTAL else height
        ticks = []
        offsets = []
        for tick in self._axis.GetTicks():
            v = self._minFactor + self._axis.MapToView(tick) * (self._maxFactor - self._minFactor)
            offset = v * size
            if offset < 0 or offset >= size:
                continue
            ticks.append(tick)
            offsets.append(offset)

        return (ticks, offsets)

    def _Build(self, *_):
        width, height = self.GetAbsoluteSize()
        width *= uicore.dpiScaling
        height *= uicore.dpiScaling
        self.Flush()
        positions = []
        colors = []
        ticks, offsets = self._GetTicks()
        clearColor = self.gridColor[0:3] + (0,)
        for tick, offset in zip(ticks, offsets):
            if self._orientation == AxisOrientation.HORIZONTAL:
                positions.append((offset, 0))
                positions.append((offset, 0))
                positions.append((offset, height))
                positions.append((offset, height))
            else:
                positions.append((0, offset))
                positions.append((0, offset))
                positions.append((width, offset))
                positions.append((width, offset))
            if tick == 0:
                colors.append(self.zeroColor[0:3] + (0,))
                colors.append(self.zeroColor)
                colors.append(self.zeroColor)
                colors.append(self.zeroColor[0:3] + (0,))
            else:
                colors.append(clearColor)
                colors.append(self.gridColor)
                colors.append(self.gridColor)
                colors.append(clearColor)

        self.AppendVertices(positions, None, colors)

    def _OnResize(self, *args):
        self._Build()
