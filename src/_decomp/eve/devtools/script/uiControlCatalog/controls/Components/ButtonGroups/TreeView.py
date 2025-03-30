#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\ButtonGroups\TreeView.py
import carbonui
from carbonui import Align, IdealSize
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from eve.client.script.ui import eveThemeColor, eveColor
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

def on_click_message(node):
    if not node.IsSelected():
        node.GetRootNode().DeselectAll()
        node.SetSelected()
    ShowQuickMessage('on_click: {}'.format(node.GetLabel()))


class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from eve.client.script.ui.control.treeViewEntry import TreeViewEntry
        from eve.client.script.ui.control.treeData import TreeData
        scrollCont = ScrollContainer(parent=parent, align=Align.TOPLEFT, width=200, height=200)
        rootNode = TreeData()
        rootNode.on_click.connect(on_click_message)
        node1 = rootNode.AddNode(label='Node 1')
        node2 = rootNode.AddNode(label='Node 2')
        node3 = rootNode.AddNode(label='Node 3')
        node1.AddNode('Node A')
        node1.AddNode('Node B')
        node1.AddNode('Node C')
        node2.AddNode('Node X')
        node2.AddNode('Node Y')
        node2.AddNode('Node Z')
        node3.AddNode('Node Alpha')
        node3.AddNode('Node Beta')
        node3.AddNode('Node Gamma')
        for node in rootNode.children:
            TreeViewEntry(parent=scrollCont, data=node)


class Sample2(Sample):
    name = 'Top level Headers'

    def sample_code(self, parent):
        from eve.client.script.ui.control.treeViewEntry import TreeViewEntryHeader
        from eve.client.script.ui.control.treeData import TreeData
        scrollCont = ScrollContainer(parent=parent, align=Align.TOPLEFT, width=200, height=200)
        rootNode = TreeData()
        rootNode.on_click.connect(on_click_message)
        node1 = rootNode.AddNode(label='Node 1')
        node2 = rootNode.AddNode(label='Node 2')
        node3 = rootNode.AddNode(label='Node 3')
        node1.AddNode('Node A')
        node1.AddNode('Node B')
        node1.AddNode('Node C')
        node2.AddNode('Node X')
        node2.AddNode('Node Y')
        node2.AddNode('Node Z')
        node3.AddNode('Node Alpha')
        node3.AddNode('Node Beta')
        node3.AddNode('Node Gamma')
        for node in rootNode.children:
            TreeViewEntryHeader(parent=scrollCont, data=node)


def on_click(node):
    if not node.IsSelected():
        node.GetRootNode().DeselectAll()
        node.SetSelected()


class Sample3(Sample):
    name = 'As navigation menu'

    def construct_sample(self, parent):
        parent = Container(parent=parent, align=Align.TOPLEFT, width=IdealSize.SIZE_480, height=IdealSize.SIZE_240)
        self.sample_code(parent)

    def sample_code(self, parent):
        from eve.client.script.ui.control.treeViewEntry import TreeViewEntry
        from eve.client.script.ui.control.treeData import TreeData
        ID_1 = 1
        ID_2 = 2
        ID_3 = 3
        ID_4 = 4
        ID_5 = 5

        class MyPanelContainer(Container):
            default_bgColor = eveColor.MATTE_BLACK

            def ApplyAttributes(self, attributes):
                super(MyPanelContainer, self).ApplyAttributes(attributes)
                self.label = carbonui.TextHeader(parent=self, align=Align.CENTER)

            def OnNodeSelected(self, node, animate = True):
                self.label.text = '{} Selected (ID={})'.format(node.GetLabel(), node.GetID())

        scrollCont = ScrollContainer(parent=parent, align=Align.TOLEFT, width=100)
        panelCont = MyPanelContainer(parent=parent, padLeft=16)
        rootNode = TreeData()
        rootNode.on_click.connect(on_click)
        rootNode.on_selected.connect(panelCont.OnNodeSelected)
        node1 = rootNode.AddNode(label='Node 1', nodeID=ID_1)
        node1.AddNode(label='Node 2', nodeID=ID_2)
        node1.AddNode(label='Node 3', nodeID=ID_3)
        node4 = rootNode.AddNode(label='Node 4', nodeID=ID_4)
        node4.AddNode(label='Node 5', nodeID=ID_5)
        for node in rootNode.children:
            TreeViewEntry(parent=scrollCont, data=node)


def on_click_toggle_or_select(node):
    if node.IsLeaf():
        node.GetRootNode().DeselectAll()
        node.SetSelected()
    else:
        node.ToggleExpanded()


class Sample4(Sample):
    name = 'Groups not selectable'

    def sample_code(self, parent):
        from eve.client.script.ui.control.treeViewEntry import TreeViewEntryHeader
        from eve.client.script.ui.control.treeData import TreeData
        scrollCont = ScrollContainer(parent=parent, align=Align.TOPLEFT, width=200, height=200)
        rootNode = TreeData()
        rootNode.on_click.connect(on_click_toggle_or_select)
        node1 = rootNode.AddNode(label='Group 1')
        node2 = rootNode.AddNode(label='Group 2')
        node3 = rootNode.AddNode(label='Group 3')
        node1.AddNode('Node A')
        node1.AddNode('Node B')
        node1.AddNode('Node C')
        node2.AddNode('Node X')
        node2.AddNode('Node Y')
        node2.AddNode('Node Z')
        node3.AddNode('Node Alpha')
        node3.AddNode('Node Beta')
        node3.AddNode('Node Gamma')
        for node in rootNode.children:
            TreeViewEntryHeader(parent=scrollCont, data=node)
