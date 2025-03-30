#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Graphs\CircularGraph.py
from eve.client.script.ui import eveColor
from carbonui import uiconst
from eve.client.script.ui.graphs import GraphSegmentParams
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from eve.client.script.ui.graphs.circulargraph import CircularGraph
        circularGraph = CircularGraph(parent=parent, align=uiconst.TOPLEFT, radius=90, lineWidth=4, bgLineWidth=8, colorBg=eveColor.MATTE_BLACK)
        graphData = [GraphSegmentParams(0.3, eveColor.DANGER_RED), GraphSegmentParams(0.3, eveColor.PRIMARY_BLUE), GraphSegmentParams(0.1, eveColor.LIME_GREEN)]
        circularGraph.LoadGraphData(graphData, animateIn=True)


class Sample2(Sample):
    name = 'With markers and tooltips'

    def sample_code(self, parent):
        from eve.client.script.ui.graphs.circulargraph import CircularGraph
        circularGraph = CircularGraph(parent=parent, align=uiconst.TOPLEFT, radius=90, lineWidth=16, bgLineWidth=10, colorBg=(1, 1, 1, 0.1))
        graphData = [GraphSegmentParams(0.3, eveColor.DANGER_RED, showMarker=True, tooltip='RED'), GraphSegmentParams(0.5, eveColor.PRIMARY_BLUE, showMarker=True, tooltip='BLUE'), GraphSegmentParams(0.2, eveColor.LIME_GREEN, showMarker=True, tooltip='GREEN')]
        circularGraph.LoadGraphData(graphData, animateIn=True)
