#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\graphstest.py
from carbonui.control.window import Window
from eve.client.script.ui.shared.market.marketGraph import MarketGraph
from carbonui.graphs.datafortesting import GetTestData

class TestGraph(Window):
    __guid__ = 'form.TestGraph'
    default_caption = 'Graphs Test'
    default_minSize = (600, 300)
    default_windowID = 'GraphsTest'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.data = GetTestData()
        self.graph = MarketGraph(parent=self.GetMainArea(), data=self.data)

    def _OnSizeChange_NoBlock(self, width, height):
        self.graph.RebuildAll()
