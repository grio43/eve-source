#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\SpecialContainers\LayoutGrid.py
from carbonui.primitives.layoutGrid import LayoutGrid, LayoutGridRow
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.fill import Fill
from carbonui.control.label import LabelCore
import carbonui.const as uiconst
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample

class CustomGridRow(LayoutGridRow):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        LayoutGridRow.ApplyAttributes(self, attributes)
        LabelCore(parent=self, text='Custom row Cell 1')
        LabelCore(parent=self, text='Custom row Cell 2 and some more text')
        LabelCore(parent=self, text='Custom row Cell 3')
        self.hilite = Fill(bgParent=self, idx=0, state=uiconst.UI_HIDDEN)

    def OnMouseEnter(self, *args):
        self.hilite.display = True

    def OnMouseExit(self, *args):
        self.hilite.display = False


class Sample1(Sample):
    name = 'Basic'
    description = "A LayoutGrid will fit it's cells and rows as snug as it can and it's primary use is as a base class for TooltipPanel. Total width is dictated by the longest row, which is then divided evenly between columns, taking any colSpan values into account. Total height is simply the sum of all row heights."

    def sample_code(self, parent):
        from carbonui.primitives.layoutGrid import LayoutGrid

        def RowEnter(row):
            row.hilite.display = True

        def RowExit(row):
            row.hilite.display = False

        mainGrid = LayoutGrid(columns=3, parent=parent, cellPadding=5, cellSpacing=10, margin=10, bgColor=eveColor.MATTE_BLACK)
        mainGrid.DebugCells()
        row = mainGrid.AddRow(bgColor=eveColor.CHERRY_RED)
        row.DebugCells()
        LabelCore(parent=row, text='Row Cell 1')
        LabelCore(parent=row, text='Row Cell 2')
        LabelCore(parent=row, text='Row Cell 3', align=uiconst.CENTERRIGHT)
        row.state = uiconst.UI_NORMAL
        row.OnMouseEnter = (RowEnter, row)
        row.OnMouseExit = (RowExit, row)
        row.hilite = Fill(bgParent=row, idx=0, state=uiconst.UI_HIDDEN)
        row = mainGrid.AddRow(bgColor=eveColor.COPPER_OXIDE_GREEN)
        row.DebugCells()
        row.AddCell(cellObject=LabelCore(text='Row Cell 1'))
        row.AddCell(cellObject=LabelCore(text='Row Cell 2', align=uiconst.CENTERRIGHT), colSpan=2)
        row.state = uiconst.UI_NORMAL
        row.OnMouseEnter = (RowEnter, row)
        row.OnMouseExit = (RowExit, row)
        row.hilite = Fill(bgParent=row, idx=0, state=uiconst.UI_HIDDEN)
        mainGrid.AddRow(bgColor=eveColor.SMOKE_BLUE, rowClass=CustomGridRow)
        for i in xrange(mainGrid.columns * 2):
            LabelCore(parent=mainGrid, text='Text %s' % i, align=uiconst.CENTER)

        mainGrid.AddCell(cellObject=LabelCore(text='colSpan=2', align=uiconst.CENTERLEFT), colSpan=2)
        mainGrid.FillRow()
        mainGrid.AddCell(cellObject=LabelCore(text='colSpan=3', align=uiconst.CENTERLEFT), colSpan=3)
        mainGrid.AddCell(cellObject=LabelCore(text='FIRST COL LONG TEXT', align=uiconst.CENTERLEFT), colSpan=1)
        mainGrid.AddCell(cellObject=LabelCore(text='SECOND COL, colSpan=2 MORE TEXT ', align=uiconst.CENTERLEFT), colSpan=2)


class ResizableContainer(Container):
    default_cursor = uiconst.UICURSOR_DRAGGABLE

    def OnMouseMove(self, *args):
        if uicore.uilib.leftbtn:
            self.width += uicore.uilib.dx
            self.height += uicore.uilib.dy


def SetMargin(layoutGrid, value):
    layoutGrid.margin = int(value)


def SetCellSpacing(layoutGrid, value):
    layoutGrid.cellSpacing = int(value)


def SetCellPadding(layoutGrid, value):
    layoutGrid.cellPadding = int(value)


class Sample2(Sample):
    name = 'Playground'
    description = 'Drag each of the containers around to see how it affects the layout (Red debug frame indicates cell sizes)'

    def construct_sample(self, parent):
        from carbonui.primitives.layoutGrid import LayoutGrid
        comboCont = ContainerAutoSize(parent=parent, align=uiconst.CENTERTOP, height=20)
        layoutGrid = LayoutGrid(parent=parent, columns=3, align=uiconst.CENTERTOP, top=40)
        Frame(bgParent=layoutGrid)
        layoutGrid.debug_showCells = True
        SingleLineEditInteger(parent=comboCont, align=uiconst.TOLEFT, width=50, label='Margin', minValue=-100, setvalue=0, OnChange=lambda x: SetMargin(layoutGrid, x))
        SingleLineEditInteger(parent=comboCont, align=uiconst.TOLEFT, width=50, padLeft=20, label='CellSpacing', minValue=-100, setvalue=0, OnChange=lambda x: SetCellSpacing(layoutGrid, x))
        SingleLineEditInteger(parent=comboCont, align=uiconst.TOLEFT, width=50, padLeft=20, label='CellPadding', minValue=-100, setvalue=0, OnChange=lambda x: SetCellPadding(layoutGrid, x))
        align = uiconst.CENTER
        cont = ResizableContainer(align=align, pos=(0, 0, 200, 100), bgColor=eveColor.SMOKE_BLUE, state=uiconst.UI_NORMAL)
        layoutGrid.AddCell(cont, colSpan=3)
        cont = ResizableContainer(align=align, pos=(0, 0, 30, 22), bgColor=eveColor.CRYO_BLUE, state=uiconst.UI_NORMAL)
        layoutGrid.AddCell(cont)
        cont = ResizableContainer(align=align, pos=(0, 0, 60, 44), bgColor=eveColor.BURNISHED_GOLD, state=uiconst.UI_NORMAL)
        layoutGrid.AddCell(cont)
        cont = ResizableContainer(align=align, pos=(0, 0, 80, 66), bgColor=eveColor.LEAFY_GREEN, state=uiconst.UI_NORMAL)
        layoutGrid.AddCell(cont)
        cont = ResizableContainer(align=align, pos=(0, 0, 160, 66), bgColor=eveColor.SMOKE_BLUE, state=uiconst.UI_NORMAL)
        layoutGrid.AddCell(cont, colSpan=2)
        cont = ResizableContainer(align=align, pos=(0, 0, 180, 88), bgColor=eveColor.SAND_YELLOW, state=uiconst.UI_NORMAL)
        layoutGrid.AddCell(cont)
