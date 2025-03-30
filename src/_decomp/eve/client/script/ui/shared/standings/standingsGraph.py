#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\standings\standingsGraph.py
from carbonui.graphs.areagraph import AreaGraph
from carbonui.graphs.axis import InteractionLimit
from carbonui.graphs.bargraph import DynamicHint
from carbonui.graphs.graph import GraphArea
from carbonui.graphs.linegraph import LineGraph
from carbonui.graphs.pointgraph import PointGraph
from carbonui.primitives.container import Container
import carbonui.graphs.animations as animations
import carbonui.graphs.axis as axis
import carbonui.const as uiconst
from carbonui.primitives.line import Line
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.shared.standings import standingUIConst
from eve.client.script.ui.shared.standings.standingsUtil import GetStandingChangeFormatted
from eve.common.script.util.eveFormat import FmtStandingTransaction
from eve.common.script.util.standingUtil import RoundStandingChange
from localization.formatters.dateTimeFormatters import FormatDateTime
MAX_POINTS = 25.0
MARGINS_VERTICAL = (0.05, 0.05)
MARGINS_HORIZONTAL = (0.005, 0.005)

class StandingsGraph(Container):
    default_name = 'StandingsGraph'
    __notifyevents__ = ['OnStandingHistoryEntryMouseEnter', 'OnStandingHistoryEntryMouseExit']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.graphData = []
        self.transactions = []

    def Update(self, fromID, toID, transactions):
        self.transactions = transactions
        standingSvc = sm.GetService('standing')
        self.transactions.reverse()
        baseStanding = standingSvc.GetStanding(fromID, toID)
        modifications = [ transaction.modification for transaction in self.transactions ]
        self.graphData = self.GetGraphData(modifications[:], baseStanding)
        self.Flush()
        Line(parent=self, align=uiconst.TOTOP, opacity=0.05)
        Line(parent=self, align=uiconst.TOBOTTOM, opacity=0.05)
        self.graphArea = GraphArea(name='graph', parent=self, align=uiconst.TOALL)
        self.ConstructStandingGraph(self.graphData)

    def ConstructStandingGraph(self, data):
        dataRange = (min(data), max(data))
        verticalAxis = axis.AutoTicksAxis(dataRange, tickCount=1, tickBase=5.0, margins=MARGINS_VERTICAL)
        self.graphArea.AddAxis(axis.AxisOrientation.VERTICAL, verticalAxis, 1.0, 0.0)
        verticalAxis.ZoomOn(dataRange)
        xRange = range(0, len(data))
        horizontalAxis = axis.CategoryAxis(xRange, visibleRange=(0, MAX_POINTS), margins=MARGINS_HORIZONTAL, interactionLimit=InteractionLimit.DATA_RANGE)
        self.graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, horizontalAxis)
        numPoints = len(data)
        if numPoints > MAX_POINTS:
            horizontalAxis.ZoomOn((numPoints - MAX_POINTS - 1, numPoints - 1))
            self.graphArea.AddPanAxis(horizontalAxis)
        else:
            horizontalAxis.ZoomOn((0.0, numPoints - 1))
        areaGraph = AreaGraph(parent=self.graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=data, color=(0.3, 0.3, 0.3, 1.0), lineWidth=1, state=uiconst.UI_DISABLED)
        self.pointGraph = StandingsPointGraph(parent=self.graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=data, pointColor=Color.GRAY2, lineWidth=1, hint=DynamicHint(self.GetPointHint))
        lineGraph = LineGraph(parent=self.graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=data, lineColor=Color.GRAY2, opacity=1.0, lineWidth=1.0)
        lineGraph.Animate(animations.AnimationType.GROW, animations.AnimationDynamics.OPPOSITE_AXIS, 0.25)
        self.pointGraph.Animate(animations.AnimationType.FADE, animations.AnimationDynamics.ALONG_AXIS, 0.6)
        uicore.animations.FadeTo(areaGraph, 0.0, 1.0, duration=0.4, timeOffset=0.35)

    def GetPointHint(self, index):
        valueText = '%.2f' % round(self.graphData[index], 2)
        if index == 0:
            return valueText
        transaction = self.transactions[index - 1]
        body, subject = FmtStandingTransaction(transaction)
        date = FormatDateTime(transaction.eventDateTime)
        standingDiff = RoundStandingChange(transaction.modification)
        diffText = GetStandingChangeFormatted(standingDiff)
        dateColor = Color.RGBtoHex(*Color.GRAY5)
        return '%s\n%s\n<color=%s>%s</color>\n<b>%s</b>\n%s' % (valueText,
         diffText,
         dateColor,
         date,
         body,
         subject)

    def GetGraphData(self, modifications, standing):
        ret = [standing]
        modifications.reverse()
        for modification in modifications:
            standing -= modification
            if round(abs(standing), 1) == 0.0:
                standing = 0.0
            ret.append(standing)

        ret.reverse()
        return ret

    def OnStandingHistoryEntryMouseEnter(self, transaction):
        try:
            index = self.transactions.index(transaction) + 1
        except ValueError:
            index = None

        self.pointGraph.HilitePoint(index)

    def OnStandingHistoryEntryMouseExit(self, transaction):
        self.pointGraph.HilitePoint(None)


class StandingsPointGraph(PointGraph):

    def GetPointColors(self):
        colors = []
        for i in xrange(len(self._values)):
            color = self._GetPointColor(i)
            for i in xrange(4):
                colors.append(color)

        return colors

    def _GetPointColor(self, index):
        if index == 0 or index >= len(self._values):
            return standingUIConst.COLOR_NEUTRAL
        else:
            diff = self._values[index] - self._values[index - 1]
            if diff > 0:
                return standingUIConst.COLOR_GOOD
            return standingUIConst.COLOR_BAD

    def OnMouseEnter(self, *args):
        PointGraph.OnMouseEnter(self, *args)
        self.OnHoverStateChange()

    def OnMouseExit(self, *args):
        PointGraph.OnMouseExit(self, *args)
        self.OnHoverStateChange()

    def OnHoverStateChange(self):
        sm.ScatterEvent('OnStandingsGraphHoverStateChange', self._hoverIndex)
