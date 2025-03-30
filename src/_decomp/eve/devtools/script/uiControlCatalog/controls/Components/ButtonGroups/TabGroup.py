#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\ButtonGroups\TabGroup.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def construct_sample(self, parent):
        cont = Container(parent=parent, align=uiconst.TOPLEFT, width=300, height=300)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.control.tabGroup import TabGroup
        TAB_ID_1 = 1
        TAB_ID_2 = 2
        TAB_ID_3 = 3
        tabGroup = TabGroup(name='myTabGroup', parent=parent, groupID='MyTabGroupID', align=uiconst.TOTOP)
        panel1 = Container(name='panel1', parent=parent, bgColor=eveColor.MATTE_BLACK)
        panel2 = Container(name='panel2', parent=parent, bgColor=eveColor.SMOKE_BLUE)
        panel3 = Container(name='panel3', parent=parent, bgColor=eveColor.COPPER_OXIDE_GREEN)
        tabGroup.AddTab('Panel 1', panel1, tabID=TAB_ID_1)
        tabGroup.AddTab('Panel 2', panel2, tabID=TAB_ID_2)
        tabGroup.AddTab('Panel 3', panel3, tabID=TAB_ID_3)
        tabGroup.AutoSelect()


class Sample2(Sample):
    name = 'Lazy loading'
    description = "Often times it's smart to lazy load panel content when we have multiple content heavy, or server snooping panels"

    def construct_sample(self, parent):
        cont = Container(parent=parent, align=uiconst.TOPLEFT, width=300, height=300)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.control.tabGroup import TabGroup
        TAB_ID_1 = 1
        TAB_ID_2 = 2

        class MyPanel(Container):
            isLoaded = False

            def LoadPanel(self):
                if not self.isLoaded:
                    ShowQuickMessage('Loading {panelName}'.format(panelName=self.name))
                    self.isLoaded = True

        tabGroup = TabGroup(name='myTabGroup', parent=parent, groupID='MyTabGroupID2', align=uiconst.TOTOP)
        panel1 = MyPanel(name='panel1', parent=parent, bgColor=eveColor.MATTE_BLACK)
        panel2 = MyPanel(name='panel2', parent=parent, bgColor=eveColor.SMOKE_BLUE)
        tabGroup.AddTab('Panel 1', panel1, tabID=TAB_ID_1)
        tabGroup.AddTab('Panel 2', panel2, tabID=TAB_ID_2)
        tabGroup.AutoSelect()
