#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\autopilotSettings.py
import blue
import carbonui.const as uiconst
import evetypes
import localization
from carbonui.control.checkbox import Checkbox
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.util.various_unsorted import GetAttrs
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.universe import LocationTextEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from carbonui.control.tabGroup import TabGroup

class AutopilotSettings(Window):
    __guid__ = 'form.AutopilotSettings'
    default_windowID = 'AutopilotSettings'
    default_width = 600
    default_height = 450
    default_minSize = (100, 140)
    default_captionLabelPath = 'UI/Map/MapPallet/ManageAutopilotRoute'
    __notifyevents__ = ['OnDestinationSet', 'OnAutopilotUpdated']

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.isChangingOrder = False
        self.loadedTab = None
        self.waypointBtns = ButtonGroup(parent=self.sr.main, btns=[[localization.GetByLabel('UI/Map/MapPallet/btnOptimizeRoute'),
          sm.GetService('autoPilot').OptimizeRoute,
          (),
          66]])
        waypointOptionCont = ContainerAutoSize(name='waypointopt', parent=self.sr.main, align=uiconst.TOBOTTOM, clipChildren=True, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         0))
        self.sr.scroll2 = eveScroll.Scroll(parent=self.sr.main, padding=const.defaultPadding)
        self.sr.scroll2.sr.id = 'autopilotSettings'
        self.sr.scroll2.sr.content.OnDropData = self.MoveWaypoints
        eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Map/MapPallet/lblChangeWaypointPriority'), parent=waypointOptionCont, padTop=4, align=uiconst.TOTOP)
        checkbox = Checkbox(text=localization.GetByLabel('UI/Map/MapPallet/cbExpandWaypoints'), parent=waypointOptionCont, settingsKey='expandwaypoints', checked=settings.user.ui.Get('expandwaypoints', 1), callback=self.OnCheckboxWaypoints, align=uiconst.TOTOP, padTop=8)
        autopilottabs = TabGroup(name='tabparent', parent=self.sr.main, idx=0)
        autopilottabs.Startup([[localization.GetByLabel('UI/Map/MapPallet/tabWaypoints'),
          self.sr.scroll2,
          self,
          'waypointconf',
          waypointOptionCont], [localization.GetByLabel('UI/Map/MapPallet/tabMapAdvoidance'),
          self.sr.scroll2,
          self,
          'avoidconf',
          None]], 'autopilottabs', autoselecttab=1)
        self.sr.autopilottabs = autopilottabs

    def Load(self, key):
        self.SetHint()
        self.waypointBtns.display = False
        if key == 'waypointconf':
            self.waypointBtns.display = True
            self.LoadWaypoints()
        elif key == 'avoidconf':
            self.LoadAvoidance()
        if self.destroyed:
            return
        self.loadedTab = key

    def MoveWaypoints(self, dragObj, entries, orderID = -1, *args):
        self.ChangeWaypointSorting(orderID=orderID)

    def ChangeWaypointSorting(self, orderID = -1, *args):
        if self.isChangingOrder:
            return
        try:
            self.isChangingOrder = True
            sel = self.sr.scroll2.GetSelected()
            starmapSvc = sm.GetService('starmap')
            if not len(sel):
                return
            waypoints = starmapSvc.GetWaypoints()
            waypointIndex = sel[0].orderID
            if waypointIndex < 0:
                return
            if waypointIndex > len(waypoints):
                return
            waypoint = waypoints[waypointIndex]
            del waypoints[waypointIndex]
            if waypointIndex < orderID:
                orderID -= 1
            if orderID == -1:
                orderID = len(waypoints)
            waypoints.insert(orderID, waypoint)
            starmapSvc.SetWaypoints(waypoints)
        finally:
            self.isChangingOrder = False

    def OnCheckboxWaypoints(self, checkbox):
        settings.user.ui.Set('expandwaypoints', checkbox.checked)
        self.LoadWaypoints()

    def LoadWaypoints(self, *args):
        mapSvc = sm.GetService('map')
        starmapSvc = sm.GetService('starmap')
        structureDirectory = sm.GetService('structureDirectory')
        waypoints = starmapSvc.GetWaypoints()
        tmplst = []
        fromID = eve.session.solarsystemid2
        scrolllist = []
        actualID = 0
        selectedItem = None
        if waypoints and len(waypoints):
            self.SetHint()
            counter = 0
            currentPlace = mapSvc.GetItem(eve.session.solarsystemid2)
            scrolllist.append(GetFromClass(Item, {'itemID': currentPlace.itemID,
             'typeID': currentPlace.typeID,
             'label': localization.GetByLabel('UI/Map/MapPallet/lblCurrentLocation', locationName=currentPlace.itemName),
             'orderID': -1,
             'actualID': 0}))
            for waypointID in waypoints:
                blue.pyos.BeNice()
                actualID = actualID + 1
                wasID, waypointName, waypointTypeID = self._GetWaypointInfo(waypointID, mapSvc, structureDirectory)
                if wasID is None:
                    continue
                description = localization.GetByLabel('UI/Map/MapPallet/lblActiveColorCategory', activeLabel=evetypes.GetName(waypointTypeID))
                while wasID:
                    wasID = mapSvc.GetParent(wasID)
                    if wasID:
                        item = mapSvc.GetItem(wasID)
                        if item is not None:
                            description = description + ' / ' + item.itemName

                if settings.user.ui.Get('expandwaypoints', 1) == 1:
                    solarsystems = starmapSvc.GetRouteBetween(fromID, waypointID)
                    if len(solarsystems):
                        for solarsystemID in solarsystems[1:-1]:
                            actualID = actualID + 1
                            sunItem = mapSvc.GetItem(solarsystemID)
                            scrolllist.append(GetFromClass(AutoPilotItem, {'itemID': solarsystemID,
                             'typeID': sunItem.typeID,
                             'label': localization.GetByLabel('UI/Map/MapPallet/lblWaypointListEntryNoCount', itemName=sunItem.itemName),
                             'orderID': -1,
                             'actualID': actualID}))

                lblTxt = localization.GetByLabel('UI/Map/MapPallet/lblWaypointListEntry', counter=counter + 1, itemName=waypointName, description=description)
                scrolllist.append(GetFromClass(AutoPilotItem, {'itemID': waypointID,
                 'typeID': waypointTypeID,
                 'label': lblTxt,
                 'orderID': counter,
                 'actualID': actualID,
                 'canDrag': 1}))
                if self.sr.Get('selectedWaypoint', None) is not None and self.sr.selectedWaypoint < len(waypoints) and waypointID == waypoints[self.sr.selectedWaypoint]:
                    selectedItem = actualID
                counter = counter + 1
                fromID = waypointID

        if self == None:
            return
        destinationPath = starmapSvc.GetDestinationPath()
        self.sr.scroll2.Load(contentList=scrolllist)
        if not len(scrolllist):
            self.SetHint(localization.GetByLabel('UI/Map/MapPallet/hintNoWaypoints'))
        if selectedItem is not None:
            self.sr.scroll2.SetSelected(selectedItem)

    def _GetWaypointInfo(self, waypointID, mapSvc, structureDirectory):
        each = mapSvc.GetItem(waypointID)
        if each:
            return (each.itemID, each.itemName, each.typeID)
        structureInfo = structureDirectory.GetStructureInfo(waypointID)
        if structureInfo:
            return (structureInfo.solarSystemID, cfg.evelocations.Get(waypointID).name, structureInfo.typeID)
        return (None, None, None)

    def LoadAvoidance(self, *args):
        mapSvc = sm.StartService('map')
        items = sm.GetService('clientPathfinderService').GetAvoidanceItems()
        scrolllist = []
        if items and len(items):
            self.SetHint()
            counter = 0
            for itemsID in items:
                blue.pyos.BeNice()
                each = mapSvc.GetItem(itemsID)
                description = localization.GetByLabel('UI/Map/MapPallet/lblActiveColorCategory', activeLabel=evetypes.GetGroupNameByGroup(each.typeID))
                wasID = each.itemID
                while wasID:
                    wasID = mapSvc.GetParent(wasID)
                    if wasID:
                        item = mapSvc.GetItem(wasID)
                        if item is not None:
                            description = description + ' / ' + item.itemName

                itemName = each.itemName
                text = localization.GetByLabel('UI/Map/MapPallet/lblAdvoidanceListEntry', itemName=itemName, description=description)
                entry = GetFromClass(LocationTextEntry, {'itemID': itemsID,
                 'typeID': each.typeID,
                 'text': text,
                 'locationID': itemsID,
                 'genericDisplayLabel': itemName})
                scrolllist.append(entry)

        self.sr.scroll2.Load(contentList=scrolllist)
        if not len(scrolllist):
            self.SetHint(localization.GetByLabel('UI/Map/MapPallet/hintNoAdvoidanceItems'))

    def SetHint(self, hintstr = None):
        if self.sr.scroll2:
            self.sr.scroll2.ShowHint(hintstr)

    def OnDestinationSet(self, *args):
        if self.sr.autopilottabs.GetSelectedArgs() == 'waypointconf':
            self.LoadWaypoints()

    def OnAutopilotUpdated(self):
        if self.sr.autopilottabs.GetSelectedArgs() == 'avoidconf':
            self.LoadAvoidance()


class AutoPilotItem(Item):
    __guid__ = 'listentry.AutoPilotItem'
    isDragObject = True

    def Startup(self, *args):
        super(AutoPilotItem, self).Startup(*args)
        self.sr.posIndicatorCont = Container(name='posIndicator', parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=2)
        self.sr.posIndicatorNo = Fill(parent=self.sr.posIndicatorCont, color=(0.61, 0.05, 0.005, 1.0))
        self.sr.posIndicatorNo.state = uiconst.UI_HIDDEN
        self.sr.posIndicatorYes = Fill(parent=self.sr.posIndicatorCont, color=(1.0, 1.0, 1.0, 0.5))
        self.sr.posIndicatorYes.state = uiconst.UI_HIDDEN

    def GetDragData(self, *args):
        if not self.sr.node.canDrag:
            return
        self.sr.node.scroll.SelectNode(self.sr.node)
        return [self.sr.node]

    def OnDropData(self, dragObj, nodes, *args):
        self.sr.posIndicatorNo.state = uiconst.UI_HIDDEN
        self.sr.posIndicatorYes.state = uiconst.UI_HIDDEN
        if GetAttrs(self, 'parent', 'OnDropData'):
            node = nodes[0]
            if self.sr.node.canDrag:
                if GetAttrs(node, 'panel'):
                    self.parent.OnDropData(dragObj, nodes, orderID=self.sr.node.orderID)

    def OnDragEnter(self, dragObj, nodes, *args):
        node = nodes[0]
        if self.sr.node.canDrag:
            self.sr.posIndicatorYes.state = uiconst.UI_DISABLED
        else:
            self.sr.posIndicatorNo.state = uiconst.UI_DISABLED

    def OnDragExit(self, *args):
        self.sr.posIndicatorNo.state = uiconst.UI_HIDDEN
        self.sr.posIndicatorYes.state = uiconst.UI_HIDDEN
