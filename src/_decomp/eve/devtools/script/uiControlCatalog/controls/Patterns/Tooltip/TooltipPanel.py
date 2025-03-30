#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Patterns\Tooltip\TooltipPanel.py
import carbonui.const as uiconst
import uthread2
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.shipTree.infoBubble import SkillEntry
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = '1 Column'
    description = 'Tooltip with 1 column text layout, tooltip always above'

    def sample_code(self, parent):

        class MyContainer2(Container):

            def LoadTooltipPanel(self, tooltipPanel, *args):
                tooltipPanel.LoadStandardSpacing()
                tooltipPanel.columns = 1
                tooltipPanel.AddMediumHeader(text='A Header')
                tooltipPanel.AddLabelMedium(text='And some very, very redundant description')

        MyContainer2(name='myCont', parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, width=100, height=100, bgColor=eveColor.MATTE_BLACK)


class Sample2(Sample):
    name = '2 Columns'
    description = 'Tooltip with 2 column text layout, tooltip always below'

    def sample_code(self, parent):

        class MyContainer3(Container):

            def LoadTooltipPanel(self, tooltipPanel, *args):
                tooltipPanel.LoadStandardSpacing()
                tooltipPanel.columns = 2
                tooltipPanel.AddMediumHeader(text='A header that spans 2 columns', labelColSpan=2)
                tooltipPanel.AddLabelMedium(text='And some very, very redundant description on the left', wrapWidth=150)
                tooltipPanel.AddLabelMedium(text='And some very, very redundant description on the right', wrapWidth=150)

            def GetTooltipPointer(self):
                return uiconst.POINT_TOP_2

        MyContainer3(name='myCont', parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, width=100, height=100, bgColor=eveColor.MATTE_BLACK)


class Sample3(Sample):
    name = 'Shortcut hint'

    def sample_code(self, parent):

        class MyContainer1(Container):

            def LoadTooltipPanel(self, tooltipPanel, *args):
                tooltipPanel.LoadStandardSpacingOld()
                tooltipPanel.columns = 2
                tooltipPanel.AddCommandTooltip(uicore.cmd.commandMap.GetCommandByName('CmdSetCameraOrbit'))

        MyContainer1(name='myCont', parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, width=100, height=100, bgColor=eveColor.MATTE_BLACK)


class Sample4(Sample):
    name = 'Interactable'
    description = 'Interactable tooltip with skill requirements'

    def sample_code(self, parent):

        class MyContainer4(Container):

            def LoadTooltipPanel(self, tooltipPanel, *args):
                tooltipPanel.state = uiconst.UI_NORMAL
                tooltipPanel.LoadStandardSpacing()
                tooltipPanel.columns = 2
                tooltipPanel.AddRow(rowClass=SkillEntry, typeID=4411, level=3, showLevel=True)
                tooltipPanel.AddRow(rowClass=SkillEntry, typeID=12183, level=5, showLevel=True)

        MyContainer4(name='myCont', parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, width=100, height=100, bgColor=eveColor.MATTE_BLACK)


class Sample5(Sample):
    name = 'Using Subclassing'
    description = 'Tooltip panel implemented via custom TooltipPanel subclass'

    def sample_code(self, parent):
        from eve.client.script.ui.control.tooltips import TooltipPanel

        class MyTooltipPanelClass(TooltipPanel):

            def ApplyAttributes(self, attributes):
                super(MyTooltipPanelClass, self).ApplyAttributes(attributes)
                self.myValue = attributes.myValue
                self.LoadGeneric1ColumnTemplate()
                self.label = self.AddLabelMedium()
                self.UpdateLabelText()
                uthread2.StartTasklet(self.UpdateValues)

            def UpdateLabelText(self):
                self.label.text = 'My value is %s and increasing!' % self.myValue

            def UpdateValues(self):
                while not self.destroyed:
                    uthread2.Sleep(1.0)
                    self.myValue += 1
                    self.UpdateLabelText()

        class MyContainer(Container):

            def ConstructTooltipPanel(self):
                return MyTooltipPanelClass(myValue=10)

        MyContainer(name='myCont', parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, width=100, height=100, bgColor=eveColor.MATTE_BLACK)


class Sample6(Sample):
    name = 'Callbacks'
    description = 'Callbacks for when the tooltip is opened and closed'

    def sample_code(self, parent):

        class MyContainerWithCallbacks(Container):

            def LoadTooltipPanel(self, tooltipPanel, *args):
                tooltipPanel.LoadStandardSpacing()
                tooltipPanel.columns = 1
                tooltipPanel.AddLabelMedium(text='Now that I am open the box is red')

            def OnTooltipPanelOpened(self):
                self.bgFill.color = (1, 0, 0, 1)

            def OnTooltipPanelClosed(self):
                self.bgFill.color = eveColor.MATTE_BLACK

            def GetTooltipPointer(self):
                return uiconst.POINT_BOTTOM_2

        MyContainerWithCallbacks(name='myCont', parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, width=100, height=100, bgColor=eveColor.MATTE_BLACK)
