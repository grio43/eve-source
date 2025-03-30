#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\item.py
import itertools
import evetypes
import metaGroups
import utillib
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from eve.client.script.ui.control.entries.divider import DividerEntry
from eve.client.script.ui.control.entries.generic import events, Generic
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.shared.tooltip.dynamicItem import AddDynamicItemAttributes
from eve.client.script.ui.shared.traits import HasTraits, TraitsContainer
from eveservices.menu import GetMenuService

class Item(Generic):
    __guid__ = 'listentry.Item'
    __params__ = ['itemID', 'typeID', 'label']
    isDragObject = True

    def Startup(self, *args):
        Generic.Startup(self, args)
        self.labelCont = Container(name='labelCont', parent=self, padRight=16)
        self.sr.label.SetParent(self.labelCont)
        self.sr.label.left = 8
        self.sr.label.autoFadeSides = 16
        self.sr.infoicon = InfoIcon(left=2, parent=self, idx=0, align=uiconst.CENTERRIGHT)
        self.sr.infoicon.OnClick = self.ShowInfo
        self.sr.icon = ItemIcon(parent=self, pos=(1, 2, 24, 24), align=uiconst.TOPLEFT, idx=0)
        for eventName in events:
            setattr(self.sr, eventName, None)

    def Load(self, node):
        self.sr.node = node
        self.itemID = node.itemID
        self.typeID = node.typeID
        self.isStation = node.Get('isStation', 0)
        self.confirmOnDblClick = node.Get('confirmOnDblClick', 0)
        self.showTooltip = node.Get('showTooltip', True)
        self.disableIcon = node.Get('disableIcon', False)
        showinfo = node.Get('showinfo', True)
        if node.getIcon and self.typeID:
            self.sr.icon.state = uiconst.UI_DISABLED if self.disableIcon else uiconst.UI_NORMAL
            self.sr.icon.SetTypeIDandItemID(self.typeID, self.itemID, isCopy=getattr(node, 'isCopy', False))
            self.sr.label.left = self.height + 4 + node.get('sublevel', 0) * 16
            self.sr.icon.left = node.get('sublevel', 0) * 16
        else:
            self.sr.icon.state = uiconst.UI_HIDDEN
            self.sr.label.left = 8 + node.get('sublevel', 0) * 16
        self.sr.label.text = node.label
        self.hint = node.Get('hint', '')
        if showinfo and (self.typeID or self.isStation):
            self.sr.infoicon.state = uiconst.UI_NORMAL
        else:
            self.sr.infoicon.state = uiconst.UI_HIDDEN
        for eventName in events:
            if node.Get(eventName, None):
                setattr(self.sr, eventName, node.Get(eventName, None))

        if node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        self.labelCont.padRight = 0 if self.sr.infoicon.state == uiconst.UI_HIDDEN else 16
        self.sr.label.Update()

    def GetHeight(self, *args):
        node, width = args
        node.height = 29
        return node.height

    def GetMenu(self):
        if not self.sr.node.Get('ignoreRightClick', 0):
            self.OnClick()
        if self.sr.node.Get('GetMenu', None):
            return self.sr.node.GetMenu(self)
        if self.itemID:
            return GetMenuService().GetMenuFromItemIDTypeID(self.itemID, self.typeID, includeMarketDetails=True)
        if self.typeID:
            if getattr(self.sr.node, 'isCopy', False):
                bpData = sm.GetService('blueprintSvc').GetBlueprintTypeCopy(self.typeID, original=False)
                abstractInfo = utillib.KeyVal(bpData=bpData)
            else:
                abstractInfo = None
            return GetMenuService().GetMenuFromItemIDTypeID(None, self.typeID, includeMarketDetails=True, abstractInfo=abstractInfo)
        return []

    def GetDragData(self, *args):
        return self.sr.node.scroll.GetSelectedNodes(self.sr.node)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.IsUnder(uicore.layer.menu):
            return
        if not self.showTooltip:
            return
        if HasTraits(self.typeID):
            tooltipPanel.LoadGeneric1ColumnTemplate()
            tooltipPanel.AddSpacer(width=300, height=1)
            TraitsContainer(parent=tooltipPanel, typeID=self.typeID, padding=7)
        if self.itemID:
            tooltipPanel.LoadGeneric1ColumnTemplate()
            AddDynamicItemAttributes(tooltipPanel, self.itemID, self.typeID)
        loadTooltipPanelFunc = self.sr.node.Get('LoadTooltipPanelFunc', None)
        if loadTooltipPanelFunc:
            loadTooltipPanelFunc(tooltipPanel, self.itemID, self.typeID)

    def OnMouseEnter(self, *args):
        Generic.OnMouseEnter(self, *args)
        self.sr.icon.OnMouseEnter()

    def OnMouseExit(self, *args):
        Generic.OnMouseExit(self, *args)
        self.sr.icon.OnMouseExit()


def GetItemEntriesByMetaGroup(typeIDs):
    sortKeys = []
    for typeID in typeIDs:
        metaGroupID = evetypes.GetMetaGroupID(typeID) or 1
        metaLevel = evetypes.GetMetaLevel(typeID)
        name = evetypes.GetName(typeID)
        sortKeys.append((metaGroupID,
         metaLevel,
         name,
         typeID))

    entries = []
    it = itertools.groupby(sorted(sortKeys), key=lambda x: x[0])
    for metaGroupID, variants in it:
        headerData = {'line': metaGroupID,
         'label': metaGroups.get_name(metaGroupID),
         'text': None}
        entries.append(GetFromClass(Header, headerData))
        for _, _, name, typeID in variants:
            itemData = {'typeID': typeID,
             'label': name,
             'getIcon': 1}
            entries.append(GetFromClass(Item, itemData))

        entries.append(GetFromClass(DividerEntry))

    return entries
