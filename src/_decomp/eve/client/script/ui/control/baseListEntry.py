#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\baseListEntry.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.fill import Fill
from eve.client.script.ui.control.eveLabel import Label
import carbonui

class BaseListEntry(SE_BaseClassCore):
    default_name = 'BaseListEntry'
    default_align = uiconst.TOPLEFT
    default_height = 20
    isDragObject = True

    def Load(self, *args):
        pass

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.node = self.sr.node = attributes.node
        if self.node.selected:
            self.Select()

    @classmethod
    def GetCopyData(cls, node):
        return ''

    def GetHint(self):
        return self.node.hint

    @classmethod
    def GetDynamicHeight(cls, node, width = None):
        return node.height or cls.default_height

    def OnMouseHover(self, *args):
        if self.node.Get('OnMouseHover', None):
            self.node.OnMouseHover(self)

    def OnMouseEnter(self, *args):
        SE_BaseClassCore.OnMouseEnter(self, *args)
        if self.node.Get('OnMouseEnter', None):
            self.node.OnMouseEnter(self)

    def OnMouseExit(self, *args):
        SE_BaseClassCore.OnMouseExit(self, *args)
        if self.node.Get('OnMouseExit', None):
            self.node.OnMouseExit(self)

    def OnClick(self, *args):
        if self.sound_select:
            PlaySound(self.sound_select)
        if self.node.Get('selectable', 1):
            self.node.scroll.SelectNode(self.node)
        if self.node.Get('OnClick', None):
            self.node.OnClick(self)

    def OnDblClick(self, *args):
        self.node.scroll.SelectNode(self.node)
        if self.node.Get('OnDblClick', None):
            if isinstance(self.node.OnDblClick, tuple):
                func = self.node.OnDblClick[0]
                func(self, *self.node.OnDblClick[1:])
            else:
                self.node.OnDblClick(self)

    def OnMouseDown(self, *args):
        SE_BaseClassCore.OnMouseDown(self, *args)
        if self.node.Get('OnMouseDown', None):
            self.node.OnMouseDown(self)

    def OnMouseUp(self, *args):
        SE_BaseClassCore.OnMouseUp(self, *args)
        if self.node.Get('OnMouseUp', None):
            self.node.OnMouseUp(self)

    def GetMenu(self):
        if not self.node.Get('ignoreRightClick', 0):
            self.OnClick()
        if self.node.Get('GetMenu', None):
            return self.node.GetMenu(self)
        return []

    def OnDropData(self, dragObj, nodes):
        if self.node.OnDropData:
            self.node.OnDropData(dragObj, nodes)

    def DoSelectNode(self, toggle = 0):
        self.node.scroll.GetSelectedNodes(self.node, toggle=toggle)

    def GetRadialMenuIndicator(self, create = True, *args):
        indicator = getattr(self, 'radialMenuIndicator', None)
        if indicator and not indicator.destroyed:
            return indicator
        if not create:
            return
        self.radialMenuIndicator = Fill(bgParent=self, color=(1, 1, 1, 0.25), name='radialMenuIndicator')
        return self.radialMenuIndicator

    def ShowRadialMenuIndicator(self, slimItem, *args):
        indicator = self.GetRadialMenuIndicator(create=True)
        indicator.display = True

    def HideRadialMenuIndicator(self, slimItem, *args):
        indicator = self.GetRadialMenuIndicator(create=False)
        if indicator:
            indicator.display = False


class BaseListEntryCustomColumns(BaseListEntry):
    default_name = 'BaseListEntryCustomColumns'

    def ApplyAttributes(self, attributes):
        BaseListEntry.ApplyAttributes(self, attributes)
        self.columns = []

    def AddColumnContainer(self, padRight = 1, width = 0):
        column = Container(align=uiconst.TOLEFT, parent=self, clipChildren=True, padRight=padRight, width=width)
        self.columns.append(column)
        return column

    def AddColumnText(self, text = None):
        column = self.AddColumnContainer()
        return Label(parent=column, text=text, align=uiconst.CENTERLEFT, left=uiconst.LABELTABMARGIN)

    def AddColumnBodyText(self, text = None):
        column = self.AddColumnContainer()
        return carbonui.TextBody(parent=column, text=text, align=uiconst.CENTERLEFT, left=uiconst.LABELTABMARGIN)

    def OnColumnResize(self, newCols):
        for i, width in enumerate(newCols):
            self.columns[i].width = width - 1
