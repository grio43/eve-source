#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerFiles\directionalScanResultEntry.py
import evetypes
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
import carbonui.const as uiconst
from localization import GetByLabel
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService

class DirectionalScanResultEntry(BaseListEntryCustomColumns):

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.AddIconColumn()
        self.nameColumn = self.AddColumnText()
        self.typeColumn = self.AddColumnText()
        self.distanceColumn = self.AddColumnText()

    def AddIconColumn(self):
        column = Container(align=uiconst.TOLEFT, width=16, state=uiconst.UI_DISABLED, parent=self)
        self.columns.append(column)
        self.icon = Sprite(parent=column, align=uiconst.CENTERLEFT, pos=(0, -1, 16, 16))
        return column

    def Load(self, node):
        if node.selected:
            self.Select()
        else:
            self.Deselect()
        self.icon.SetTexturePath(sm.GetService('bracket').GetBracketIcon(node.typeID))
        self.nameColumn.text = node.entryName
        self.typeColumn.text = node.typeName
        self.distanceColumn.text = node.diststr

    def GetHeight(self, *args):
        return 20

    def OnDblClick(self, *args):
        BaseListEntryCustomColumns.OnDblClick(self, *args)
        sm.GetService('info').ShowInfo(self.node.typeID, self.node.itemID)

    def GetMenu(self, *args):
        data = self.node
        if data.itemID:
            return GetMenuService().CelestialMenu(data.itemID, typeID=data.typeID)
        return []

    def GetDragData(self, *args):
        return self.node.scroll.GetSelectedNodes(self.sr.node)

    def OnClick(self, *args):
        BaseListEntryCustomColumns.OnClick(self, *args)
        uicore.cmd.ExecuteCombatCommand(self.node.itemID, uiconst.UI_CLICK)

    def OnMouseEnter(self, *args):
        BaseListEntryCustomColumns.OnMouseEnter(self, *args)
        sm.ScatterEvent('OnDscanEntryMouseEnter', self.node.typeID)

    def OnMouseExit(self, *args):
        BaseListEntryCustomColumns.OnMouseExit(self, *args)
        sm.ScatterEvent('OnDscanEntryMouseExit')

    @classmethod
    def GetCopyData(cls, node):
        return '<t>'.join([str(node.typeID),
         node.entryName,
         node.typeName,
         node.diststr])

    @staticmethod
    def GetDefaultColumnAndDirection():
        return (GetByLabel('UI/Common/ID'), True)

    @staticmethod
    def GetFixedColumns():
        return {'': 20}

    @staticmethod
    def GetColumns():
        return ['',
         GetByLabel('UI/Common/Name'),
         GetByLabel('UI/Common/Type'),
         GetByLabel('UI/Common/Distance')]

    @staticmethod
    def GetColumnsMinSize():
        return {GetByLabel('UI/Common/Name'): 90,
         GetByLabel('UI/Common/Type'): 90,
         GetByLabel('UI/Common/Distance'): 60}

    @staticmethod
    def GetColumnsDefaultSize():
        return {'': 16,
         GetByLabel('UI/Common/Name'): 160,
         GetByLabel('UI/Common/Type'): 130,
         GetByLabel('UI/Common/Distance'): 100}
