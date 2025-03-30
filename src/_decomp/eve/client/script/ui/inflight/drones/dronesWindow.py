#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\drones\dronesWindow.py
import appConst
import log
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import eveicon
import evetypes
import localization
import uthread
import uthread2
from carbon.client.script.util.misc import Uthreaded
from carbonui import TextColor, uiconst
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import SortListOfTuples
from carbonui.window.header.small import SmallWindowHeader
from carbonui.window.widget import WidgetWindow
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.inflight import actionPanelDefaults
from eve.client.script.ui.inflight.drones import droneSignals, dronesDragData
from eve.client.script.ui.inflight.drones.droneEntry import DroneInSpaceEntry, DroneInBayEntry, NoDroneInBayEntry, NoDroneInSpaceEntry
from eve.client.script.ui.inflight.drones.droneGroup import DroneSubGroup, DroneSubGroupInSpace, DroneSubGroupInBay
from eve.client.script.ui.inflight.drones.droneGroupHeader import DroneGroupHeaderInBay, DroneGroupHeaderInSpace
from eve.client.script.ui.inflight.drones.droneGroupsController import GetDroneGroupsController
from eve.client.script.ui.inflight.drones.droneSettings import drones_aggressive_setting, drones_focus_fire_setting, VIEW_MODE_ICONS, drones_view_mode_setting, VIEW_MODE_LIST, drones_view_mode_compact_setting
from eve.client.script.ui.inflight.drones.dronesConst import DRONESTATE_INBAY, DRONESTATE_INSPACE
from eve.client.script.ui.inflight.drones.dronesDragData import HasInSpaceDroneIDs
from eve.client.script.ui.inflight.drones.dronesUtil import GetDronesInLocalSpace, GetDronesInBay, GetDroneIDsInBay, GetDroneIDsInSpace, ExpandRadialMenuForInBayGroup, ExpandRadialMenuForInSpaceGroup
from eve.client.script.ui.inflight.drones.dronesWarpWarning import warp_warning_enabled_setting, WarpWarning
from eve.client.script.ui.services.menuSvcExtras import droneFunctions
from eve.common.lib import appConst as const
from eveDrones.droneConst import DAMAGESTATE_NOT_READY
from eveservices.menu import GetMenuService
from localization import GetByLabel
from menu import MenuLabel, MenuList
from utillib import KeyVal
NODRONES_CLOSE_TIME = 5

class DronesWindow(WidgetWindow):
    __notifyevents__ = ['OnAttribute',
     'OnAttributes',
     'OnDroneControlLost',
     'OnItemChange',
     'OnClientEvent_WarpStarted',
     'OnClientEvent_WarpFinished',
     'OnWarpStarted2',
     'ProcessSessionChange']
    default_windowID = 'droneview'
    uniqueUiName = pConst.UNIQUE_NAME_DRONE_WND
    default_minSize = (240, 120)
    default_scope = uiconst.SCOPE_INFLIGHT
    default_isKillable = False

    def get_wnd_menu_unique_name(self):
        return pConst.UNIQUE_NAME_DRONE_SETTINGS

    @staticmethod
    def default_left(*args):
        return actionPanelDefaults.GetDroneViewLeft()

    @staticmethod
    def default_top(*args):
        return actionPanelDefaults.GetDroneViewTop()

    @staticmethod
    def default_width():
        return actionPanelDefaults.GetDroneViewWidth()

    @staticmethod
    def default_height():
        return actionPanelDefaults.GetDroneViewHeight()

    def ApplyAttributes(self, attributes):
        self.inBayHeader = None
        super(DronesWindow, self).ApplyAttributes(attributes)
        self.panelname = attributes.panelName
        self.lastActionSerial = None
        self.actionsTimer = None
        self.reloadThread = None
        self.lastUpdateIDs = None
        self.reloadPending = False
        self.inSpace = None
        self.droneGroupsController = GetDroneGroupsController()
        self.droneGroupsController.on_groups_changed.connect(self.OnDroneGroupsChanged)
        if self.panelname:
            self.SetCaption(self.panelname)
        self.content.clipChildren = True
        self.warpWarning = WarpWarning(parent=self.content, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, padBottom=2)
        self.ConstructBottomScroll()
        self.ConstructTopScroll()
        openState = uicore.registry.GetListGroupOpenState(('dronegroups', DRONESTATE_INBAY), default=False)
        uicore.registry.GetLockedGroup('dronegroups', DRONESTATE_INBAY, localization.GetByLabel('UI/Inflight/Drone/DronesInBay'), openState=openState)
        openState = uicore.registry.GetListGroupOpenState(('dronegroups', DRONESTATE_INSPACE), default=False)
        uicore.registry.GetLockedGroup('dronegroups', DRONESTATE_INSPACE, localization.GetByLabel('UI/Inflight/Drone/DronesInLocalSpace'), openState=openState)
        droneSettingChanges = {appConst.attributeDroneIsAggressive: drones_aggressive_setting.is_enabled(),
         appConst.attributeDroneFocusFire: drones_focus_fire_setting.is_enabled()}
        sm.GetService('godma').GetStateManager().ChangeDroneSettings(droneSettingChanges)
        if self and not self.destroyed:
            self.CheckReloadDronesScroll()
        self.UpdateAll()
        self.on_compact_mode_changed.connect(self.OnWindowStateChanged)
        self.on_stacked_changed.connect(self.OnWindowStateChanged)
        self.on_collapsed_changed.connect(self.OnWindowStateChanged)
        drones_view_mode_setting.on_change.connect(self.OnDronesViewModeChanged)
        drones_view_mode_compact_setting.on_change.connect(self.OnDronesViewModeChanged)
        self.UpdateHeaderPadding()
        uthread2.StartTasklet(self.CheckCloseThread)

    def OnDroneGroupsChanged(self):
        self.CheckReloadDronesScroll(force=True)

    def ConstructTopScroll(self):
        self.inBayHeader = DroneGroupHeaderInBay(parent=self.content, align=uiconst.TOTOP, idx=0)
        self.inBayHeader.on_open_changed.connect(self.OnInBayHeaderExpandedChanged)
        self.inBayHeader.OnMouseMoveDrag = self.OnInBayHeaderMouseMoveDrag
        self.inBayHeader.OnMouseDownDrag = self.OnInBayHeaderMouseDownDrag
        self.inBayHeader.OnMouseUp = self.OnInBayHeaderMousUp
        self.topScroll = Scroll(name='dronesInBayScroll', parent=self.content, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.topScroll.sr.content.OnDropData = self.OnDropData
        self.topScroll.sr.content.OnDragEnter = self.OnDragEnter
        self.topScroll.multiSelect = 1
        self.topScroll.OnChar = self.OnDronesScrollChar

    def OnInBayHeaderMousUp(self, *args):
        self.OnMouseUp(*args)

    def OnInBayHeaderMouseDownDrag(self, *args):
        self.dragMousePosition = (uicore.uilib.x, uicore.uilib.y)
        self.OnMouseDownDrag(*args)

    def OnInBayHeaderMouseMoveDrag(self, *args):
        self.OnMouseMoveDrag(*args)

    def OnDropData(self, dragSource, dragData):
        droneIDs = dronesDragData.GetInSpaceDroneIDs(dragData)
        if droneIDs:
            droneFunctions.ReturnToDroneBay(droneIDs)
            droneSignals.on_drones_dropped_to_bay()

    def OnDragEnter(self, dragSource, dragData):
        if HasInSpaceDroneIDs(dragData):
            droneSignals.on_in_bay_entry_drag_enter()

    def OnInBayHeaderExpandedChanged(self, isExpanded):
        self.topScroll.display = isExpanded
        self.bottomCont.align = uiconst.TOBOTTOM if isExpanded else uiconst.TOTOP
        if not isExpanded and not self.inSpaceHeader.isExpanded:
            self.inSpaceHeader.SetAsExpanded()

    def ConstructBottomScroll(self):
        self.bottomCont = ContainerAutoSize(name='bottomCont', parent=self.content, align=uiconst.TOBOTTOM)
        self.inSpaceHeader = DroneGroupHeaderInSpace(parent=self.bottomCont, align=uiconst.TOTOP, padTop=4)
        self.inSpaceHeader.on_open_changed.connect(self.OnInSpaceHeaderExpanedChanged)
        self.bottomScroll = Scroll(name='dronesInSpaceScroll', align=uiconst.TOTOP, parent=self.bottomCont, state=uiconst.UI_PICKCHILDREN, padTop=2)
        self.bottomScroll.multiSelect = 1
        self.bottomScroll.OnChar = self.OnDronesScrollChar
        self.bottomScroll.sr.content.state = uiconst.UI_PICKCHILDREN
        self.bottomScroll.on_content_resize.connect(self.OnBottomScrollContentResize)

    def OnInSpaceHeaderExpanedChanged(self, isExpanded):
        self.bottomScroll.display = isExpanded
        if not isExpanded and not self.inBayHeader.isExpanded:
            self.inBayHeader.SetAsExpanded()

    def OnBottomScrollContentResize(self, height):
        self.UpdateBottomScrollHeight()

    def UpdateBottomScrollHeight(self):
        window_height = self.height if not self.stacked else self.GetCurrentAbsoluteSize()[1]
        maxHeight = max(window_height - (86 if self.compact else 128), 0)
        self.bottomScroll.height = min(self.bottomScroll.GetEntriesTotalHeight(), maxHeight)

    def _OnResize(self, *args, **kw):
        super(DronesWindow, self)._OnResize(*args, **kw)
        self.UpdateBottomScrollHeight()

    def OnDronesViewModeChanged(self, *args):
        self.CheckReloadDronesScroll(force=True)

    def UpdateHeaderPadding(self):
        self.extend_content_into_header = self.compact
        if self.compact:
            _, _, content_pad_right, _ = self.content_padding
            _, inset_right = self.header_inset
            reserved_spaced_right = max(inset_right - content_pad_right, 0)
        else:
            reserved_spaced_right = 0
        self.inBayHeader.reserved_space_right = reserved_spaced_right

    def OnWindowStateChanged(self, *args):
        self.UpdateHeaderPadding()
        self._update_header()
        self.CheckReloadDronesScroll(force=True)

    def Prepare_Header_(self):
        self._SetHeader(SmallWindowHeader(show_caption=not self.compact, fixed_height=self._get_header_fixed_height()))

    def _update_header(self):
        self.header.show_caption = not self.compact
        self.header.fixed_height = self._get_header_fixed_height()

    def _get_header_fixed_height(self):
        if self.compact:
            return 40

    def ProcessSessionChange(self, *etc):
        self.CheckReloadDronesScroll(True)

    ProcessSessionChange = Uthreaded(ProcessSessionChange)

    def OnDroneControlLost(self, droneID):
        self.CheckReloadDronesScroll(True)

    def OnAttributes(self, l):
        for attributeName, item, newValue in l:
            self.OnAttribute(attributeName, item, newValue)

    def OnAttribute(self, attributeName, item, newValue):
        if not self or self.destroyed:
            return
        if item.itemID == session.charid and attributeName == 'maxActiveDrones':
            t = self.lastUpdateIDs
            if t is None:
                self.CheckReloadDronesScroll()

    def OnItemChange(self, item, change, location):
        if item.locationID == session.shipid:
            if item.flagID == const.flagDroneBay or change.get(const.ixFlag, None) == const.flagDroneBay:
                self.CheckReloadDronesScroll()
        elif change.get(const.ixLocationID, None) == session.shipid and change.get(const.ixFlag, None) == const.flagDroneBay:
            self.CheckReloadDronesScroll()

    def OnDronesScrollChar(self, *args):
        return False

    def GetSelected(self, fromNode):
        nodes = []
        sel = fromNode.scroll.GetSelectedNodes(fromNode)
        for node in sel:
            if node.Get('typeID', None) is None:
                continue
            if evetypes.GetGroupID(node.typeID) == evetypes.GetGroupID(fromNode.typeID):
                if node.droneState == fromNode.droneState:
                    nodes.append(node)

        return nodes

    def UpdateAll(self):
        if self.content.state != uiconst.UI_PICKCHILDREN:
            self.actionsTimer = None
            return
        self.CheckReloadDronesScroll()

    def GetSubGroups(self, what):
        return []

    def CheckReloadDronesScroll(self, force = False, *args):
        if force:
            self.lastUpdateIDs = None
        if self.reloadThread:
            self.reloadPending = True
        else:
            self.reloadThread = uthread.new(self._CheckReloadDronesScroll)

    def _CheckReloadDronesScroll(self):
        if session.stationid:
            return
        inBayIDs = GetDroneIDsInBay()
        inLocalSpaceIDs = GetDroneIDsInSpace()
        uthread.new(sm.GetService('tactical').GetInBayDroneDamageTracker().FetchInBayDroneDamageToServer, inBayIDs)
        allDroneIDs = (inBayIDs, inLocalSpaceIDs)
        if self.lastUpdateIDs != allDroneIDs:
            self.lastUpdateIDs = allDroneIDs
            self._ReloadScroll(inBayIDs, inLocalSpaceIDs)
        self.CheckHint()
        self.UpdateWarpWarning()
        self.inBayHeader.UpdateLabelText()
        self.inSpaceHeader.UpdateLabelText()
        uthread2.Sleep(0.1)
        if self.reloadPending:
            self.reloadPending = False
            self.CheckReloadDronesScroll()
        self.reloadThread = None

    def _ReloadScroll(self, inBayIDs, inLocalSpaceIDs):
        self._ReloadTopScroll(inBayIDs)
        self._ReloadBottomScroll(inLocalSpaceIDs)

    def _ReloadTopScroll(self, inBayIDs):
        scrolllist = self.GetMainGroupEntriesInBay(DRONESTATE_INBAY, inBayIDs)
        self.topScroll.Load(contentList=scrolllist)

    def _ReloadBottomScroll(self, inLocalSpaceIDs):
        scrolllist = self.GetMainGroupEntriesInSpace(DRONESTATE_INSPACE, inLocalSpaceIDs)
        self.bottomScroll.Load(contentList=scrolllist)

    def CheckCloseThread(self):
        noDronesCounter = 0
        while not self.destroyed:
            uthread2.Sleep(1.0)
            if not self.HasDronesInBayOrSpace():
                noDronesCounter += 1
            else:
                noDronesCounter = 0
            if noDronesCounter >= NODRONES_CLOSE_TIME:
                self.Close()

    def HasDronesInBayOrSpace(self):
        return GetDronesInBay() or sm.GetService('michelle').GetDrones()

    def GetSubFolderMenu(self, node):
        m = MenuList([None])
        data = self.droneGroupsController.GetDroneDataForSubGroup(node.droneState, node.groupName)
        if not data:
            return m
        if node.droneState == DRONESTATE_INSPACE:
            m += GetMenuService().DroneMenu(data)
        elif node.droneState == DRONESTATE_INBAY:
            m += GetMenuService().InvItemMenu(data).filter([MenuLabel('UI/Inventory/ItemActions/BuyThisType'),
             MenuLabel('UI/Inventory/ItemActions/AddTypeToMarketQuickbar'),
             MenuLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'),
             MenuLabel('UI/Inventory/ItemActions/FindInContracts')])
        favoriteGroup = self.droneGroupsController.GetFavoriteGroupID()
        groupIdentifier = node.id[-1]
        if favoriteGroup == groupIdentifier:
            m.append(MenuEntryData(text=MenuLabel('UI/Drones/UnmarkAsFavorite'), func=lambda : self.RemoveAsFavorite(groupIdentifier), texturePath=eveicon.star_slash))
        else:
            m.append(MenuEntryData(text=MenuLabel('UI/Drones/MarkAsFavorite'), func=lambda : self.AddAsFavorite(groupIdentifier), texturePath=eveicon.star))
        return m

    def AddAsFavorite(self, groupIdentifier):
        self.droneGroupsController.SetFavoriteGroupID(groupIdentifier)
        self.CheckReloadDronesScroll(force=True)

    def RemoveAsFavorite(self, groupIdentifier):
        favoriteGroupID = self.droneGroupsController.GetFavoriteGroupID()
        if groupIdentifier == favoriteGroupID:
            self.droneGroupsController.SetFavoriteGroupID(None)
            self.CheckReloadDronesScroll(force=True)

    def GroupMenu(self, droneNode):
        selected = self.GetSelected(droneNode)
        itemIDs = [ n.itemID for n in selected ]
        m = MenuList()
        move = [(MenuLabel('UI/Commands/NewGroup'), self.droneGroupsController.CreateSubGroup, (evetypes.GetGroupID(droneNode.typeID), itemIDs))]
        inGroup = []
        for node in selected:
            group = self.droneGroupsController.GetDroneGroup(node.itemID)
            if group:
                inGroup.append(node)

        if inGroup:
            itemIDs = [ entry.itemID for entry in inGroup ]
            move += [(MenuLabel('UI/Commands/OutOfThisGroup'), self.droneGroupsController.RemoveFromGroup, (itemIDs,))]
        groupNames = self.droneGroupsController.GetGroupNames()
        groupNames.sort(key=lambda x: x.lower())
        move += [ (groupName, self.droneGroupsController.MoveToGroup, (evetypes.GetGroupID(droneNode.typeID), groupName, [ d.itemID for d in selected ])) for groupName in groupNames ]
        m += [(MenuLabel('UI/Commands/MoveDrone'), move)]
        return m

    def OnMouseDownOnDroneMainGroup(self, group, *args):
        self.OnMouseDownOnDroneMainGroup_thread(group)

    def OnMouseDownOnDroneMainGroup_thread(self, group):
        groupNode = group.sr.node
        droneData = self.droneGroupsController.GetDroneDataForMainGroup(groupNode.droneState)
        if droneData:
            return self.GetRadialMenuOnGroup(group, droneData)

    def OnMouseDownOnDroneSubGroup(self, group, *args):
        uthread.new(self.OnMouseDownOnDroneSubGroup_thread, group)

    def OnMouseDownOnDroneSubGroup_thread(self, group):
        groupNode = group.sr.node
        droneData = self.droneGroupsController.GetDroneDataForSubGroup(groupNode.droneState, groupNode.groupName)
        if droneData:
            return self.GetRadialMenuOnGroup(group, droneData)

    def GetRadialMenuOnGroup(self, group, droneData):
        groupNode = group.sr.node
        if groupNode.droneState == DRONESTATE_INBAY:
            ExpandRadialMenuForInBayGroup(group, groupNode.cleanLabel, droneData)
        elif groupNode.droneState == DRONESTATE_INSPACE:
            ExpandRadialMenuForInSpaceGroup(group, groupNode.cleanLabel, droneData)

    def GetSpaceDrone(self, droneID):
        return sm.GetService('michelle').GetDroneState(droneID)

    def _GetSubGroupEntryClass(self, droneState):
        if droneState == DRONESTATE_INSPACE:
            groupCls = DroneSubGroupInSpace
        else:
            if droneState == DRONESTATE_INBAY:
                return DroneSubGroupInBay
            groupCls = DroneSubGroup
        return groupCls

    def GetSubGroupListEntry(self, group, state, items):
        numDrones = self.GetNumberOfDronesInGroup(state, items)
        icon = None
        groupIdentifier = group['id']
        favoriteGroup = self.droneGroupsController.GetFavoriteGroupID()
        if favoriteGroup and favoriteGroup == groupIdentifier:
            icon = eveicon.star
        cls = self._GetSubGroupEntryClass(state)
        return GetFromClass(cls, {'GetSubContent': self.GetSubGroupContent,
         'MenuFunction': self.GetSubFolderMenu,
         'label': localization.GetByLabel('UI/Inflight/Drone/DroneGroupWithCount', groupLabel=group['label'], count=numDrones),
         'id': (state, group['id']),
         'droneGroupID': group['droneGroupID'],
         'groupItems': None,
         'iconMargin': 18,
         'state': 'locked',
         'sublevel': 0,
         'droneState': state,
         'BlockOpenWindow': 1,
         'showlen': 0,
         'groupName': group['label'],
         'OnMouseDown': self.OnMouseDownOnDroneSubGroup,
         'showicon': icon,
         'isFavorite': bool(icon)})

    def GetNumberOfDronesInGroup(self, droneState, items):
        t = 0
        if droneState == DRONESTATE_INBAY:
            dronebay = {}
            for drone in GetDronesInBay():
                dronebay[drone.itemID] = drone

            for droneID in items:
                if droneID not in dronebay:
                    log.LogWarn("Drone we thought was in the dronebay wasn't actually there, droneID = ", droneID)
                    continue
                t += dronebay[droneID].stacksize

        else:
            t = len(items)
        return t

    def GetMainGroupEntriesInBay(self, droneState, droneIDs, subLevel = 0):
        scrollList = []
        dronebay = {}
        for drone in GetDronesInBay():
            dronebay[drone.itemID] = drone

        subGroups = {}
        for droneID in droneIDs:
            group = self.droneGroupsController.GetDroneGroup(droneID)
            if group:
                subGroups.setdefault(group['label'], []).append(droneID)
                continue
            if dronebay.has_key(droneID):
                entry = self.GetBayDroneEntry(dronebay[droneID], subLevel, droneState)
                scrollList.append(((0, entry.label.lower()), entry))

        self.AppendSubGroups(scrollList, droneState, subGroups)
        return SortListOfTuples(scrollList)

    def GetMainGroupEntriesInSpace(self, droneState, droneIDs, subLevel = 0):
        scrollList = []
        subGroups = {}
        for droneID in droneIDs:
            group = self.droneGroupsController.GetDroneGroup(droneID)
            if group:
                subGroups.setdefault(group['label'], []).append(droneID)
                continue
            entry = self.GetSpaceDroneEntry(self.GetSpaceDrone(droneID), subLevel, droneState)
            scrollList.append(((0, entry.label.lower()), entry))

        self.AppendSubGroups(scrollList, droneState, subGroups)
        return SortListOfTuples(scrollList)

    def AppendSubGroups(self, scrollList, droneState, subGroups):
        for groupName, droneIDs in subGroups.iteritems():
            group = self.droneGroupsController.GetSubGroup(groupName)
            if group:
                entry = self.GetSubGroupListEntry(group, droneState, droneIDs)
                scrollList.append(((1, entry.label.lower()), entry))

        if not scrollList:
            noItemEntry = self.GetNoDroneInBayEntry() if droneState == DRONESTATE_INBAY else self.GetNoDroneInSpaceEntry()
            scrollList.append((0, noItemEntry))

    def GetSubGroupContent(self, nodedata, newitems = 0):
        scrollList = []
        subGroupInfo = self.droneGroupsController.GetSubGroup(nodedata.groupName)
        if nodedata.droneState == DRONESTATE_INBAY:
            drones = GetDronesInBay()
            for drone in drones:
                if drone.itemID in subGroupInfo['droneIDs']:
                    entry = self.GetBayDroneEntry(drone, 1, nodedata.droneState)
                    scrollList.append(((entry.subLevel, entry.label), entry))

        elif nodedata.droneState == DRONESTATE_INSPACE:
            drones = GetDronesInLocalSpace()
            for drone in drones:
                if drone.droneID in subGroupInfo['droneIDs']:
                    entry = self.GetSpaceDroneEntry(drone, 1, nodedata.droneState)
                    scrollList.append(((entry.subLevel, entry.label), entry))

        return SortListOfTuples(scrollList)

    def GetNoDroneInBayEntry(self):
        return GetFromClass(NoDroneInBayEntry, self._GetNoItemEntryData())

    def GetNoDroneInSpaceEntry(self):
        return GetFromClass(NoDroneInSpaceEntry, self._GetNoItemEntryData())

    def _GetNoItemEntryData(self):
        data = KeyVal()
        data.label = localization.GetByLabel('/Carbon/UI/Controls/Common/NoItem')
        data.sublevel = 0
        data.itemID = None
        data.height = 24
        data.fontColor = TextColor.SECONDARY
        data.selectable = False
        return data

    def GetDroneDamageState(self, droneID):
        damageTracker = sm.GetService('tactical').GetInBayDroneDamageTracker()
        if damageTracker.IsDroneDamageReady(droneID):
            damageState = damageTracker.GetDamageStateForDrone(droneID)
        else:
            damageState = DAMAGESTATE_NOT_READY
        return damageState

    def GetBayDroneEntry(self, drone, level, droneState):
        data = KeyVal()
        data.itemID = drone.itemID
        data.itemIDs = [drone.itemID]
        data.typeID = drone.typeID
        data.invItem = drone
        data.damageState = self.GetDroneDamageState(drone.itemID)
        data.displayName = evetypes.GetName(drone.typeID)
        if drone.stacksize > 1:
            data.label = localization.GetByLabel('UI/Inflight/Drone/DroneBayEntryWithStacksize', drone=drone.typeID, stacksize=drone.stacksize)
        else:
            data.label = evetypes.GetName(drone.typeID)
        data.sublevel = level
        data.customMenu = self.GroupMenu
        data.droneState = droneState
        return GetFromClass(DroneInBayEntry, data)

    def GetSpaceDroneEntry(self, drone, level, droneState):
        data = KeyVal()
        data.itemID = drone.droneID
        data.itemIDs = [drone.droneID]
        data.typeID = drone.typeID
        data.ownerID = drone.ownerID
        data.controllerID = drone.controllerID
        data.controllerOwnerID = drone.controllerOwnerID
        data.displayName = data.label = evetypes.GetName(drone.typeID)
        data.sublevel = level
        data.customMenu = self.GroupMenu
        data.droneState = droneState
        return GetFromClass(DroneInSpaceEntry, data)

    def CheckHint(self):
        if not self.topScroll.GetNodes():
            self.topScroll.ShowHint(localization.GetByLabel('UI/Inflight/Drone/NoDrones'))
        else:
            self.topScroll.ShowHint()

    def GetMenuMoreOptions(self):
        menuData = super(DronesWindow, self).GetMenuMoreOptions()
        menuData.AddCheckbox(text=localization.GetByLabel('UI/Drones/WarpWarningOption'), setting=warp_warning_enabled_setting)
        menuData.AddSeparator()
        menuData.AddCaption(text=GetByLabel('UI/Inventory/ViewMode'))
        setting = drones_view_mode_compact_setting if self.compact else drones_view_mode_setting
        menuData.AddRadioButton(text=GetByLabel('UI/Inventory/Icons'), value=VIEW_MODE_ICONS, setting=setting)
        menuData.AddRadioButton(text=GetByLabel('UI/Inventory/List'), value=VIEW_MODE_LIST, setting=setting)
        return menuData

    def OnClientEvent_WarpStarted(self, *args):
        self.UpdateWarpWarning()

    def OnWarpStarted2(self, *args):
        self.UpdateWarpWarning()

    def OnClientEvent_WarpFinished(self, *args):
        self.UpdateWarpWarning()

    def UpdateWarpWarning(self):
        if not warp_warning_enabled_setting.is_enabled():
            self.warpWarning.Hide()
            return
        michelle = sm.GetService('michelle')
        if michelle.IsPreparingWarp() and michelle.AreDronesOut():
            self.warpWarning.FadeIn()
        else:
            self.warpWarning.FadeOut()
