#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Graphs\Graph.py
import random
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample

def GetRandomData(minVal = 0, maxVal = 50, count = 25):
    return [ random.randrange(minVal, maxVal) for _ in xrange(count) ]


class Sample1(Sample):
    name = 'Basic'

    def construct_sample(self, parent):
        main = Container(name='container', parent=parent, width=400, height=400, align=uiconst.TOPLEFT)
        self.sample_code(main)

    def sample_code(self, parent):
        import carbonui.graphs.axis as axis
        from carbonui.graphs.graph import GraphArea
        from carbonui.graphs.linegraph import LineGraph
        verticalMinMax = (1.0, 0.0)
        horizontalMinMax = (0.0, 1.0)
        minValue = 0
        maxValue = 100
        numPoints = 10
        values = GetRandomData(minValue, maxValue, numPoints)
        verticalAxis = axis.AutoTicksAxis((minValue, maxValue))
        horizontalAxis = axis.CategoryAxis(values)
        graphArea = GraphArea(name='graph', parent=parent)
        graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, horizontalAxis, verticalMinMax[1], verticalMinMax[0])
        graphArea.AddAxis(axis.AxisOrientation.VERTICAL, verticalAxis, horizontalMinMax[1], horizontalMinMax[0])
        LineGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=values, color=eveColor.LIME_GREEN, lineWidth=2)


class Sample2(Sample):
    name = 'With Grid and labels '

    def construct_sample(self, parent):
        main = Container(name='container', parent=parent, width=400, height=400, align=uiconst.TOPLEFT)
        self.sample_code(main)

    def sample_code(self, parent):
        import carbonui.graphs.axis as axis
        import carbonui.graphs.axislabels as axislabels
        from carbonui.graphs.graph import GraphArea
        from carbonui.graphs.grid import Grid
        from carbonui.graphs.linegraph import LineGraph
        verticalMinMax = (1.0, 0.0)
        horizontalMinMax = (0.0, 1.0)
        verticalTicks = 5
        keys = ['North',
         'East',
         'South',
         'Banana',
         'West']
        values = [ random.randrange(0, 100) for _ in keys ]
        verticalAxis = axis.AutoTicksAxis((0, 100), tickCount=verticalTicks, margins=(0.1, 0.1))
        horizontalAxis = axis.CategoryAxis(keys, margins=(0.05, 0.0))
        axislabels.AxisLabels(parent=parent, align=uiconst.TOLEFT, width=30, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=verticalMinMax[0], maxFactor=verticalMinMax[1], padBottom=40)
        axislabels.AxisLabels(parent=parent, align=uiconst.TOBOTTOM, height=40, axis=horizontalAxis, orientation=axis.AxisOrientation.HORIZONTAL, minFactor=horizontalMinMax[0], maxFactor=horizontalMinMax[1], textAlignment=uiconst.CENTER)
        graphArea = GraphArea(name='graph', parent=parent, align=uiconst.TOALL)
        graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, horizontalAxis, verticalMinMax[1], verticalMinMax[0])
        graphArea.AddAxis(axis.AxisOrientation.VERTICAL, verticalAxis, horizontalMinMax[1], horizontalMinMax[0])
        LineGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=values, color=eveColor.LIME_GREEN, lineWidth=2)
        Grid(parent=graphArea, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=verticalMinMax[0], maxFactor=verticalMinMax[1])
        Grid(parent=graphArea, axis=horizontalAxis, orientation=axis.AxisOrientation.HORIZONTAL, minFactor=horizontalMinMax[0], maxFactor=horizontalMinMax[1])


class Sample3(Sample):
    name = 'Auto Y-axis'

    def construct_sample(self, parent):
        main = Container(name='container', parent=parent, width=400, height=400, align=uiconst.TOPLEFT)
        self.sample_code(main)

    def sample_code(self, parent):
        import carbonui.graphs.animations as animations
        import carbonui.graphs.axis as axis
        import carbonui.graphs.axislabels as axislabels
        from carbonui.graphs.graph import GraphArea
        from carbonui.graphs.grid import Grid
        from carbonui.graphs.linegraph import LineGraph
        data = GetRandomData(0, 1000, 10)
        verticalAxis = axis.AutoTicksAxis(axis.GetRangeFromSequences(data), tickCount=10, behavior=axis.AXIS_FROM_ZERO, margins=(0.1, 0.1))
        horizontalAxis = axis.AutoTicksCategoryAxis(range(0, len(data)))
        axislabels.AxisLabels(parent=parent, align=uiconst.TOLEFT, width=50, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0)
        graphArea = GraphArea(name='graph', parent=parent, align=uiconst.TOALL)
        graphArea.AddAxis(axis.AxisOrientation.VERTICAL, verticalAxis, 1.0, 0.0)
        graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, horizontalAxis)
        lineGraph = LineGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=data, color=(0.5, 0.5, 1.0, 0.8), lineWidth=1)
        Grid(parent=graphArea, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0)
        lineGraph.Animate(animations.AnimationType.FADE, animations.AnimationDynamics.SIMULTANEOUS, 0.3)


class Sample4(Sample):
    name = 'With Pan and Zoom'

    def construct_sample(self, parent):
        main = Container(name='container', parent=parent, width=400, height=400, align=uiconst.TOPLEFT)
        self.sample_code(main)

    def sample_code(self, parent):
        import carbonui.graphs.axis as axis
        import carbonui.graphs.axislabels as axislabels
        from carbonui.graphs.graph import GraphArea
        from carbonui.graphs.grid import Grid
        from carbonui.graphs.linegraph import LineGraph
        verticalMinMax = (1.0, 0.0)
        horizontalMinMax = (0.0, 1.0)
        minVal = 0
        maxVal = 40
        numVals = 100
        values = GetRandomData(minVal, maxVal, numVals)
        verticalAxis = axis.AutoTicksAxis((minVal, maxVal), tickCount=10, margins=(0.1, 0.1), interactionLimit=axis.InteractionLimit.DATA_RANGE)
        horizontalAxis = axis.CategoryAxis(range(numVals), margins=(0.1, 0.1), interactionLimit=axis.InteractionLimit.DATA_RANGE, behavior=axis.AXIS_TIGHT)
        axislabels.AxisLabels(parent=parent, width=30, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=verticalMinMax[0], maxFactor=verticalMinMax[1], padBottom=40, align=uiconst.TOLEFT)
        axislabels.AxisLabels(parent=parent, align=uiconst.TOBOTTOM, height=40, axis=horizontalAxis, orientation=axis.AxisOrientation.HORIZONTAL, minFactor=horizontalMinMax[0], maxFactor=horizontalMinMax[1], textAlignment=uiconst.CENTER)
        graphArea = GraphArea(name='graph', parent=parent)
        graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, horizontalAxis, verticalMinMax[1], verticalMinMax[0])
        graphArea.AddAxis(axis.AxisOrientation.VERTICAL, verticalAxis, horizontalMinMax[1], horizontalMinMax[0])
        graphArea.AddZoomAxis(horizontalAxis)
        graphArea.AddPanAxis(verticalAxis)
        graphArea.AddPanAxis(horizontalAxis)
        horizontalAxis.SetVisibleRange((0.0, 10.0))
        verticalAxis.SetVisibleRange((minVal - 1, maxVal))
        LineGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=values, color=(0.5, 0.5, 1.0, 0.8), lineWidth=1)
        Grid(parent=graphArea, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=verticalMinMax[0], maxFactor=verticalMinMax[1], zeroColor=(1, 1, 1, 0.2))
        Grid(parent=graphArea, axis=horizontalAxis, orientation=axis.AxisOrientation.HORIZONTAL, minFactor=horizontalMinMax[0], maxFactor=horizontalMinMax[1])


class Sample5(Sample):
    name = 'Minimap'

    def sample_code(self, parent):
        import carbonui.graphs.axis as axis
        import carbonui.graphs.axislabels as axislabels
        from carbonui.graphs.areagraph import AreaGraph
        from carbonui.graphs.graph import GraphArea
        from carbonui.graphs.grid import Grid
        from carbonui.graphs.linegraph import LineGraph
        from carbonui.graphs.minimap import MiniMap
        data = GetRandomData(0, 100, 100)
        main = Container(name='container', parent=parent, width=400, height=400, align=uiconst.TOPLEFT)
        miniMapContainer = Container(name='minimapContainer', parent=main, align=uiconst.TOBOTTOM, height=40)
        verticalAxis = axis.AutoTicksAxis((0, 100), tickCount=10, margins=(0.1, 0.1))
        horizontalAxis = axis.AutoTicksCategoryAxis(range(0, len(data)), interactionLimit=axis.InteractionLimit.DATA_RANGE)
        axislabels.AxisLabels(parent=main, align=uiconst.TOLEFT, width=50, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0)
        graphArea = GraphArea(name='graph', parent=main, align=uiconst.TOALL)
        graphArea.AddAxis(axis.AxisOrientation.VERTICAL, verticalAxis, 1.0, 0.0)
        graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, horizontalAxis)
        graphArea.AddPanAxis(horizontalAxis)
        horizontalAxis.SetVisibleRange((0.0, 20))
        Grid(parent=graphArea, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0)
        LineGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=data, color=eveColor.LIME_GREEN, lineWidth=2)
        minimap = MiniMap(name='MiniMap', parent=miniMapContainer, align=uiconst.TOALL, controlAxis=horizontalAxis, padTop=0, values=data)
        valueAxis = axis.AutoTicksAxis((0, max(data)), behavior=axis.AXIS_FROM_ZERO)
        categoryAxis = axis.CategoryAxis(data)
        AreaGraph(parent=minimap, categoryAxis=categoryAxis, valueAxis=valueAxis, values=data, graphColor=(1.0, 1.0, 1.0, 0.1), state=uiconst.UI_DISABLED)
        minimap.AddAxis(axis.AxisOrientation.HORIZONTAL, categoryAxis)
        minimap.AddAxis(axis.AxisOrientation.VERTICAL, valueAxis, 1.0, 0.0)


class Sample6(Sample):
    name = 'Point Graph'

    def construct_sample(self, parent):
        main = Container(name='container', parent=parent, width=400, height=400, align=uiconst.TOPLEFT)
        self.sample_code(main)

    def sample_code(self, parent):
        import carbonui.graphs.animations as animations
        import carbonui.graphs.axis as axis
        import carbonui.graphs.axislabels as axislabels
        from carbonui.graphs.graph import GraphArea
        from carbonui.graphs.grid import Grid
        from carbonui.graphs.pointgraph import PointGraph
        data = GetRandomData()
        verticalAxis = axis.AutoTicksAxis(axis.GetRangeFromSequences(data), tickCount=10, margins=(0.1, 0.1))
        horizontalAxis = axis.AutoTicksCategoryAxis(range(0, len(data)), tickCount=5)
        axislabels.AxisLabels(parent=parent, align=uiconst.TOLEFT, width=50, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0)
        graphArea = GraphArea(name='graph', parent=parent, align=uiconst.TOALL)
        graphArea.AddAxis(axis.AxisOrientation.VERTICAL, verticalAxis, 1.0, 0.0)
        graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, horizontalAxis)
        Grid(parent=graphArea, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0)
        pointGraph = PointGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=data, pointColor=eveColor.LIME_GREEN, pointSize=8)
        pointGraph.Animate(animations.AnimationType.GROW, animations.AnimationDynamics.RANDOM, 0.3)


class Sample7(Sample):
    name = 'BarGraph'

    def construct_sample(self, parent):
        main = Container(name='container', parent=parent, width=400, height=400, align=uiconst.TOPLEFT)
        self.sample_code(main)

    def sample_code(self, parent):
        import carbonui.graphs.animations as animations
        import carbonui.graphs.axis as axis
        import carbonui.graphs.axislabels as axislabels
        from carbonui.graphs.bargraph import BarGraph
        from carbonui.graphs.graph import GraphArea
        from carbonui.graphs.grid import Grid
        data = GetRandomData(minVal=0, maxVal=100, count=10)
        verticalAxis = axis.AutoTicksAxis((0, 100), tickCount=10, margins=(0.1, 0.1))
        horizontalAxis = axis.AutoTicksCategoryAxis(range(0, len(data)), tickCount=5)
        axislabels.AxisLabels(parent=parent, align=uiconst.TOLEFT, width=50, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0)
        graphArea = GraphArea(name='graph', parent=parent, align=uiconst.TOALL)
        graphArea.AddAxis(axis.AxisOrientation.VERTICAL, verticalAxis, 1.0, 0.0)
        graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, horizontalAxis)
        barColors = [ Color(*eveColor.CHERRY_RED).SetBrightness(0.3 + 0.7 * v / 100.0).GetRGBA() for v in data ]
        barGraph = BarGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=data, barColors=barColors, barSize=16)
        Grid(parent=graphArea, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0)
        barGraph.Animate(animations.AnimationType.FADE, animations.AnimationDynamics.ALONG_AXIS, 0.6)


class Sample8(Sample):
    name = 'Area Graph'

    def construct_sample(self, parent):
        main = Container(name='container', parent=parent, width=400, height=400, align=uiconst.TOPLEFT)
        self.sample_code(main)

    def sample_code(self, parent):
        import carbonui.graphs.animations as animations
        import carbonui.graphs.axis as axis
        import carbonui.graphs.axislabels as axislabels
        from carbonui.graphs.areagraph import AreaGraph
        from carbonui.graphs.graph import GraphArea
        from carbonui.graphs.grid import Grid
        data = GetRandomData(15, 30, count=16)
        verticalAxis = axis.AutoTicksAxis((0, 40), tickCount=10, margins=(0.1, 0.1))
        horizontalAxis = axis.AutoTicksCategoryAxis(range(0, len(data)), tickCount=5)
        axislabels.AxisLabels(parent=parent, align=uiconst.TOLEFT, width=50, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0)
        graphArea = GraphArea(name='graph', parent=parent, align=uiconst.TOALL)
        graphArea.AddAxis(axis.AxisOrientation.VERTICAL, verticalAxis, 1.0, 0.0)
        graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, horizontalAxis)
        graph = AreaGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=data, color=eveColor.SAND_YELLOW, hoverColor=eveColor.TUNGSTEN_GREY)
        Grid(parent=graphArea, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0)
        graph.Animate(animations.AnimationType.FADE, animations.AnimationDynamics.ALONG_AXIS, 0.6)


class Sample9(Sample):
    name = 'Legend'

    def construct_sample(self, parent):
        main = Container(name='container', parent=parent, width=400, height=400, align=uiconst.TOPLEFT)
        self.sample_code(main)

    def sample_code(self, parent):
        import carbonui.graphs.axis as axis
        import carbonui.graphs.axislabels as axislabels
        from carbonui.graphs.bargraph import BarGraph
        from carbonui.graphs.graph import GraphArea
        from carbonui.graphs.legend import Legend
        from carbonui.graphs.linegraph import LineGraph
        from carbonui.graphs.pointgraph import PointGraph
        data = GetRandomData(2, 10, 12)
        legend = Legend(parent=parent, align=uiconst.TOTOP, autoHeight=True, centerContent=True, contentSpacing=(6, 6))
        verticalAxis = axis.AutoTicksAxis(axis.GetRangeFromSequences(data), tickCount=10, margins=(0.1, 0.1), behavior=axis.AXIS_FROM_ZERO)
        horizontalAxis = axis.AutoTicksCategoryAxis(range(0, len(data)))
        axislabels.AxisLabels(parent=parent, align=uiconst.TOLEFT, width=50, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0)
        graphArea = GraphArea(name='graph', parent=parent, align=uiconst.TOALL)
        graphArea.AddAxis(axis.AxisOrientation.VERTICAL, verticalAxis, 1.0, 0.0)
        graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, horizontalAxis)
        pointGraph = PointGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=data, pointColor=eveColor.CRYO_BLUE, hoverColor=eveColor.PLATINUM_GREY, pointSize=16)
        legend.AddItem(pointGraph.GetLegendItem(), 'Scatter Graph')
        lineGraph = LineGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=data, lineColor=eveColor.SMOKE_BLUE, lineWidth=1)
        legend.AddItem(lineGraph.GetLegendItem(), 'Line Graph')
        barData = [ x * 0.6 + 1 for x in data ]
        barGraph = BarGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=barData, color=eveColor.CHERRY_RED, barSize=8)
        legend.AddItem(barGraph.GetLegendItem(), 'Bar Graph')
