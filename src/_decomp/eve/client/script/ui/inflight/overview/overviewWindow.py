#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overview\overviewWindow.py
import _weakref
import bisect
import logging
import sys
from collections import defaultdict
import blue
import stackless
import telemetry
import eveicon
import evetypes
import gametime
import homestation.client
import localization
import locks
import overviewPresets.overviewSettingsConst as osConst
import trinity
import uthread
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbon.common.script.util.format import FmtDist
from carbonui.control.basicDynamicScroll import BasicDynamicScroll
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.contextMenu.menuEntryData import MenuEntryData, MenuEntryDataCheckbox, MenuEntryDataCaption
from carbonui.decorative.divider_line import DividerLine
from carbonui.uicore import uicore
from carbonui.util.color import Color
from carbonui.util.various_unsorted import IsUnder
from carbonui.util import colorblind
from carbonui.window.header.small import SmallWindowHeader
from carbonui.window.widget import WidgetWindow
from eve.client.script.parklife import states as state
from eve.client.script.parklife.overview import overviewSignals
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.window.control.action import WindowMenuAction
from eve.client.script.ui.inflight import actionPanelDefaults
from eve.client.script.ui.inflight.actions import ActionPanel
from eve.client.script.ui.inflight.bracketsAndTargets.bracketVarious import GetIconColor
from eve.client.script.ui.inflight.overViewLabel import OverviewLabel, SortHeaders
from eve.client.script.ui.inflight.overview import overviewConst, overviewColumns, overviewSettings, overviewPulse
from eve.client.script.ui.inflight.overview.addTabPopup import AddTabPopup
from eve.client.script.ui.inflight.overview.overviewConst import *
from eve.client.script.ui.inflight.overview.overviewMenuUtil import GetBracketVisibilitySubMenu, GetColumnVisibilitySubMenu
from eve.client.script.ui.inflight.overview.overviewNodeUtil import PrimeDisplayName, UpdateIconAndBackgroundFlagsOnNode, PrimeCorpAndAllianceName, UpdateVelocityData
from eve.client.script.ui.inflight.overview.overviewScrollEntry import OverviewScrollEntry
from eve.client.script.ui.inflight.overview.overviewTabGroup import OverviewTabGroup
from eve.client.script.ui.inflight.overview.overviewUtil import GetSortValueWhenBroadcastGoToTop, GetAllianceTickerName, GetCorpTickerName, PrepareLocalizationTooltip, GetSlimItemForCharID, GetEntryFontSize, GetEntryHeight, GetColumnValuesToCalculate, GetColumnSettingsAndSortKeys
from eve.client.script.ui.inflight.overview.slimItemDisplayChecker import SlimItemDisplayChecker
from eve.client.script.ui.shared.pointerTool import pointerToolConst as pConst
from eve.client.script.ui.shared.stateFlag import GetIconFlagAndBackgroundFlag, FindDockingRightsToDisplay, GetGateLockValue, GetLockedToGateID, GetGateLockValueForSlimItem
from eve.common.lib import appConst as const
from eve.common.script.sys.idCheckers import IsSolarSystem
from eveexceptions import ExceptionEater
from globalConfig.getFunctions import GetOverviewMousemovementTimeout
from inventorycommon.util import IsNPC
from menu import MenuLabel
from npcs.npccorporations import get_corporation_faction_id
from overviewPresets.overviewSettingsConst import SETTING_TAB_NAME, SETTING_TAB_COLOR, MAX_TAB_NUM
from stargate.client.gate_signals import on_lock_removed
from structures import STATE_UNANCHORED, DOCKING_ACCESS_UNKNOWN
from structures.types import IsFlexStructure
from uihider import UiHiderMixin
ScrollListLock = locks.RLock()
log = logging.getLogger(__name__)

class OverviewWindow(UiHiderMixin, WidgetWindow):
    __notifyevents__ = ['OnDestinationSet',
     'OnOverviewPresetsChanged',
     'OnReloadingOverviewProfile',
     'OnEwarStart',
     'OnEwarEnd',
     'OnStateSetupChange',
     'OnSessionChanged',
     'OnFleetJoin_Local',
     'OnFleetLeave_Local',
     'OnPostCfgDataChanged',
     'OnOverviewPresetLoaded',
     'OnFleetStateChange',
     'OnStateChange',
     'DoBallsAdded',
     'DoBallRemove',
     'OnSlimItemChange',
     'OnContactChange',
     'OnItemHighlighted',
     'ProcessBountyInfoUpdated',
     'DoBallsRemove',
     'OnStructuresVisibilityUpdated',
     'OnEnterSpace',
     'OnRefreshWhenDockingRequestDenied',
     'OnStructureAccessUpdated',
     'OnOverviewOverrideChangedOnDoBallAddEgoChange',
     'OnShipLabelsUpdated',
     'OnFullOverviewReload',
     'OnFreezeOverviewWindows',
     'OnUnfreezeOverviewWindows',
     'OnFlagsInvalidated',
     'OnOverviewTabsChanged',
     'OnBracketIconUpdated',
     'OnEmanationLockUpdated']
    default_windowID = overviewConst.WINDOW_ID
    default_open = True
    default_cursor = uiconst.UICURSOR_HASMENU
    default_isKillable = False
    default_scope = uiconst.SCOPE_INFLIGHT
    default_minSize = (128, 128)
    default_iconNum = 'res:/ui/Texture/WindowIcons/overview.png'
    sortingFrozen = False
    uniqueUiName = pConst.UNIQUE_NAME_OVERVIEW_WND
    _tab_line = None

    @staticmethod
    def default_left(*args):
        return actionPanelDefaults.GetOverviewLeft()

    @staticmethod
    def default_top(*args):
        return actionPanelDefaults.GetOverviewTop()

    @staticmethod
    def default_width():
        return actionPanelDefaults.GetOverviewWidth()

    @staticmethod
    def default_height():
        return actionPanelDefaults.GetOverviewHeight()

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        self.stateSvc = sm.GetService('stateSvc')
        self.fleetSvc = sm.GetService('fleet')
        self.machoNet = sm.GetService('machoNet')
        self.presetSvc = sm.GetService('overviewPresetSvc')
        self.michelle = sm.GetService('michelle')
        super(OverviewWindow, self).ApplyAttributes(attributes)
        self.updateEntryOrderThread = None
        self._freezeOverview = False
        self._ballparkDirty = True
        self._scrollEntriesDirty = True
        self._scrollNodesByItemID = {}
        self.displayChecker = SlimItemDisplayChecker()
        self.tabGroup = None
        self._update_extend_content_into_header()
        self.jammers = {}
        self.ewarTypes = self.stateSvc.GetEwarTypes()
        self.ewarHintsByGraphicID = {}
        for jamType, (flag, graphicID) in self.ewarTypes:
            self.ewarHintsByGraphicID[graphicID] = self.stateSvc.GetEwarHint(jamType)

        self.prevMouseCoords = trinity.mainWindow.GetCursorPos()
        self.lastMovementTime = blue.os.GetWallclockTime()
        self.mouseMovementTimeout = GetOverviewMousemovementTimeout(self.machoNet)
        homeStationService = homestation.Service.instance()
        if not homeStationService.is_home_station_data_loaded:
            uthread.new(homeStationService.get_home_station)
        self._ConnectSignals()
        self.tabGroup = OverviewTabGroup(align=uiconst.TOTOP, parent=self.content, padding=self._get_tab_group_padding(), groupID='overviewTabs', UIIDPrefix='OverviewTab_', callback=self.OnTabSelected, show_line=False)
        self._tab_line = DividerLine(parent=self.content, align=uiconst.TOTOP_NOPUSH, top=self._get_tab_line_top(), padding=self._get_tab_line_padding())
        self.ConstructScroll()
        self.ReconstructTabs()

    def ConstructScroll(self):
        self.scroll = BasicDynamicScroll(name='overviewscroll2', align=uiconst.TOALL, parent=self.content, multiSelect=False, autoPurgeHiddenEntries=False)
        self.scroll.OnSelectionChange = self.OnScrollSelectionChange
        self.scroll.OnChar = self.OnChar
        self.scroll.OnKeyUp = self.OnKeyUp
        self.sortHeaders = SortHeaders(parent=self.scroll.sr.maincontainer, settingsID='overviewScroll2', idx=0, get_menu_func=self.GetMenuForsortHeaders)
        self.sortHeaders.SetDefaultColumn(COLUMN_DISTANCE, True)
        self.sortHeaders.OnColumnSizeChange = self.OnColumnSizeChanged
        self.sortHeaders.OnSortingChange = self.OnSortingChange
        self.sortHeaders.OnColumnSizeReset = self.OnColumnSizeReset

    def GetMenuForsortHeaders(self):
        return GetColumnVisibilitySubMenu(self.GetSelectedTabID())

    def GetScrollContent(self):
        return self.scroll.sr.content

    def _ConnectSignals(self):
        homeStationService = homestation.Service.instance()
        homeStationService.on_home_station_changed.connect(self._OnHomeStationChanged)
        homeStationService.on_home_station_data_loaded.connect(self._UpdateHomeStation)
        self.on_compact_mode_changed.connect(self._on_compact_mode_changed)
        self.on_header_inset_changed.connect(self._on_header_inset_changed)
        self.on_content_padding_changed.connect(self._on_content_padding_changed)
        overviewSignals.on_preset_saved.connect(self.OnOverviewPresetsChanged)
        overviewSignals.on_preset_saved_as.connect(self.OnPresetSavedAs)
        overviewSignals.on_preset_restored.connect(self.OnOverviewPresetsChanged)
        overviewSignals.on_tab_columns_changed.connect(self.OnTabColumnsChanged)
        overviewPulse.connect_to_visible_entry_update_pulse(self.OnVisibleEntryUpdatePulse)
        colorblind.on_colorblind_mode_changed.connect(self.OnColorblindModeChanged)
        on_lock_removed.connect(self.OnEmanationGateLockRemoved)

    def OnVisibleEntryUpdatePulse(self):
        if self.destroyed:
            return
        self.LoadVisibleEntries()

    def OnTabColumnsChanged(self, tabID):
        if tabID == self.GetSelectedTabID():
            self.ReconstructTabs()
            self.FullReload()

    def OnPresetSavedAs(self, oldPresetName, presetName):
        tabID = self.GetSelectedTabID()
        currTabPresetName = self.presetSvc.GetTabPreset(tabID)
        (oldPresetName,
         presetName,
         currTabPresetName,
         tabID,
         self.destroyed)
        if oldPresetName != presetName and currTabPresetName == oldPresetName:
            self.presetSvc.SetTabPreset(tabID, presetName)
        self.OnOverviewPresetsChanged()

    def _on_compact_mode_changed(self, window):
        self.header.show_caption = not self.compact
        self._update_extend_content_into_header()
        self._update_tab_line_top()
        self.ReconstructTabs()
        self.FullReload()

    def _on_content_padding_changed(self, window):
        self._update_tab_line_padding()
        self._update_tabs_padding()

    def _on_header_inset_changed(self, window):
        self._update_tabs_padding()

    def _update_extend_content_into_header(self):
        self.extend_content_into_header = self.compact

    def _get_tab_line_padding(self):
        pad_left, _, pad_right, _ = self.content_padding
        return (-pad_left,
         0,
         -pad_right,
         0)

    def _update_tab_line_padding(self):
        if self._tab_line:
            self._tab_line.padding = self._get_tab_line_padding()

    def _get_tab_line_top(self):
        _, _, _, tabs_pad_bottom = self._get_tab_group_padding()
        return -1 - tabs_pad_bottom

    def _update_tab_line_top(self):
        if self._tab_line:
            self._tab_line.top = self._get_tab_line_top()

    def _get_tab_group_padding(self):
        _, inset_right = self.header_inset
        _, pad_top, pad_right, _ = self.content_padding
        return (0,
         -8,
         inset_right - pad_right if self.compact else -4,
         4 if self.compact else 8)

    def _update_tabs_padding(self):
        self.tabGroup.padding = self._get_tab_group_padding()

    def Prepare_Header_(self):
        self._SetHeader(SmallWindowHeader(show_caption=not self.compact))

    def get_wnd_menu_unique_name(self):
        return pConst.UNIQUE_NAME_OVERVIEW_SETTINGS

    def Close(self, setClosed = False, *args, **kwds):
        ActionPanel.Close(self)
        with ExceptionEater('closing OverviewWindow'):
            homeStationService = homestation.Service.instance()
            homeStationService.on_home_station_changed.disconnect(self._OnHomeStationChanged)
            homeStationService.on_home_station_data_loaded.disconnect(self._UpdateHomeStation)
            on_lock_removed.disconnect(self.OnEmanationGateLockRemoved)

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return
        itemID = slimItem.itemID
        node = self._scrollNodesByItemID.get(itemID, None)
        if node:
            node.leavingOverview = True
            if node.panel:
                node.panel.opacity = 0.25
                node.panel.state = uiconst.UI_DISABLED
            if node.itemID in self._scrollNodesByItemID:
                del self._scrollNodesByItemID[node.itemID]

    def DoBallsAdded(self, lst, *args, **kw):
        uthread.new(self._DoBallsAdded, lst, *args, **kw)

    @telemetry.ZONE_METHOD
    def _DoBallsAdded(self, lst, *args, **kw):
        columns = overviewColumns.GetColumns(self.GetSelectedTabID())
        if self.sortHeaders.GetCurrentColumns() != columns:
            self.sortHeaders.CreateColumns(columns, fixedColumns=FIXEDCOLUMNS)
        with ScrollListLock:
            newEntries = []
            for ball, slimItem in lst:
                if slimItem.itemID in self._scrollNodesByItemID:
                    continue
                if not self.displayChecker.ShouldDisplayItem(slimItem):
                    continue
                updateItem = self.stateSvc.CheckIfUpdateItem(slimItem)
                newNode = GetFromClass(OverviewScrollEntry, {'itemID': slimItem.itemID,
                 'updateItem': updateItem})
                newNode.ball = _weakref.ref(ball)
                newNode.slimItem = _weakref.ref(slimItem)
                if updateItem:
                    newNode.ewarGraphicIDs = self.GetEwarDataForNode(newNode)
                newNode.ewarHints = self.ewarHintsByGraphicID
                newEntries.append(newNode)

            if newEntries:
                self._UpdateStaticDataForNodes(newEntries)
                self._UpdateDynamicDataForNodes(newEntries)
                currentActive, currentDirection = self.sortHeaders.GetCurrentActive()
                broadcastsToTop = self.presetSvc.GetSettingValueBroadcastToTop()
                fleetBroadcasts = self.fleetSvc.GetCurrentFleetBroadcasts()

                def GetSortValue(_node):
                    if broadcastsToTop:
                        return GetSortValueWhenBroadcastGoToTop(_node, fleetBroadcasts, currentDirection)
                    return _node.sortValue

                self.scroll.ShowHint()
                if self.sortingFrozen:
                    newEntries.sort(key=lambda x: GetSortValue(x), reverse=not currentDirection)
                    self.scroll.AddNodes(-1, newEntries)
                else:
                    sortValues = [ GetSortValue(x) for x in self.scroll.sr.nodes ]
                    entriesAtIdx = defaultdict(list)
                    for entry in newEntries:
                        insertionIndex = bisect.bisect(sortValues, GetSortValue(entry))
                        entriesAtIdx[insertionIndex].append(entry)

                    insertionPoints = sorted(entriesAtIdx.keys(), reverse=True)
                    for insertionIdx in insertionPoints:
                        sortedGroup = sorted(entriesAtIdx[insertionIdx], key=GetSortValue, reverse=not currentDirection)
                        self.scroll.AddNodes(insertionIdx, sortedGroup)

    def UpdateUIScaling(self, value, oldValue):
        super(OverviewWindow, self).UpdateUIScaling(value, oldValue)
        self.FullReload()

    def OnStateChange(self, itemID, flag, newState, *args):
        node = self._scrollNodesByItemID.get(itemID, None)
        if node and node.panel:
            node.panel.OnStateChange(itemID, flag, newState, *args)
        if flag in (state.flagWreckEmpty, state.flagWreckAlreadyOpened):
            self.FlagBallparkDirty()

    def OnFleetStateChange(self, fleetState):
        if not fleetState:
            return
        for itemID, tag in fleetState.targetTags.iteritems():
            node = self._scrollNodesByItemID.get(itemID, None)
            if node is None:
                continue
            node.display_TAG = tag
            if node.sortTagIndex is not None:
                if tag:
                    node.sortValue[node.sortTagIndex] = tag.lower()
                else:
                    node.sortValue[node.sortTagIndex] = 0

    def OnSlimItemChange(self, oldSlim, newSlim):
        node = self._scrollNodesByItemID.get(oldSlim.itemID, None)
        if node:
            node.slimItem = _weakref.ref(newSlim)
            node.iconColor = None
            PrimeDisplayName(node)
            currentActive, _ = self.sortHeaders.GetCurrentActive()
            columnSettings, _ = GetColumnSettingsAndSortKeys(currentActive, self.GetSelectedTabID())
            PrimeCorpAndAllianceName(node, columnSettings)
            UpdateIconAndBackgroundFlagsOnNode(node)
            if node.panel:
                node.panel.UpdateIcon()

    def ProcessBountyInfoUpdated(self, itemIDs):
        for itemID in itemIDs:
            node = self._scrollNodesByItemID.get(itemID, None)
            if node is not None:
                UpdateIconAndBackgroundFlagsOnNode(node)

    def FlushEwarStates(self):
        if self.jammers:
            currentSourceIDs = self.jammers.keys()
            self.jammers = {}
            for sourceBallID in currentSourceIDs:
                self.UpdateEwarStateOnItemID(sourceBallID)

    def OnEwarStart(self, sourceBallID, moduleID, targetBallID, jammingType):
        if targetBallID != session.shipid:
            return
        if not jammingType:
            return
        if not hasattr(self, 'jammers'):
            self.jammers = {}
        jammingID = sm.StartService('stateSvc').GetEwarGraphicID(jammingType)
        if sourceBallID not in self.jammers:
            self.jammers[sourceBallID] = {}
        if jammingID not in self.jammers[sourceBallID]:
            self.jammers[sourceBallID][jammingID] = {}
        self.jammers[sourceBallID][jammingID][moduleID] = True
        self.UpdateEwarStateOnItemID(sourceBallID)

    def OnEwarEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        if targetBallID != session.shipid:
            return
        if not jammingType:
            return
        if not hasattr(self, 'jammers'):
            return
        jammingID = sm.StartService('stateSvc').GetEwarGraphicID(jammingType)
        if not self.jammers.has_key(sourceBallID) or not self.jammers[sourceBallID].has_key(jammingID) or not self.jammers[sourceBallID][jammingID].has_key(moduleID):
            return
        del self.jammers[sourceBallID][jammingID][moduleID]
        if self.jammers[sourceBallID][jammingID] == {}:
            del self.jammers[sourceBallID][jammingID]
        self.UpdateEwarStateOnItemID(sourceBallID)

    def UpdateEwarStateOnItemID(self, itemID):
        node = self._scrollNodesByItemID.get(itemID, None)
        if node is None:
            return
        node.ewarGraphicIDs = self.GetEwarDataForNode(node)
        if node.panel:
            node.panel.UpdateEwar()

    def GetEwarDataForNode(self, node):
        if node.itemID not in self.jammers:
            return
        jammersOnItem = self.jammers.get(node.itemID, None)
        if not jammersOnItem:
            return
        ret = []
        for jamType, (flag, graphicID) in self.ewarTypes:
            if graphicID in jammersOnItem:
                ret.append(graphicID)

        return ret

    def OnOverviewPresetLoaded(self, presetName, preset):
        self.FlagScrollEntriesAndBallparkDirty_InstantUpdate('OnOverviewPresetLoaded')

    def UpdateWindowCaption(self, presetName):
        presetDisplayName = self.presetSvc.GetPresetDisplayName(presetName)
        text = localization.GetByLabel('UI/Tactical/OverviewCaption', preset=presetDisplayName)
        if overviewSettings.show_debug_info.is_enabled():
            text += ' windowInstanceID=%s' % self.windowInstanceID
        self.SetCaption(text)

    def OnPostCfgDataChanged(self, what, data):
        if what == 'evelocations':
            itemID = data[0]
            if itemID in self._scrollNodesByItemID:
                node = self._scrollNodesByItemID[itemID]
                PrimeDisplayName(node)

    def OnDestinationSet(self, *etc):
        for node in self.scroll.sr.nodes:
            slimItem = node.slimItem()
            if not slimItem:
                continue
            if slimItem.groupID not in (const.groupStargate, const.groupStation) and slimItem.categoryID != const.categoryStructure:
                continue
            node.iconColor = None

    def OnContactChange(self, contactIDs, contactType = None):
        self.FlagBallparkDirty()

    def OnFleetJoin_Local(self, member, *args):
        self.UpdateFleetMemberOrFlagDirty(member)
        self.FlagBallparkDirty()

    def OnFleetLeave_Local(self, member, *args):
        self.UpdateFleetMemberOrFlagDirty(member)
        self.FlagBallparkDirty()

    def OnDoBallAddEgoChange(self):
        self.TriggerInstantUpdate('OnDoBallAddEgoChange')

    def OnShipLabelsUpdated(self):
        self.FullReload()

    def OnFullOverviewReload(self):
        self.FullReload()

    def UpdateFleetMemberOrFlagDirty(self, member):
        if member.charID == session.charid:
            self.FlagScrollEntriesDirty('UpdateFleetMemberOrFlagDirty')
        else:
            slimItem = GetSlimItemForCharID(member.charID)
            if slimItem and slimItem.itemID in self._scrollNodesByItemID:
                node = self._scrollNodesByItemID[slimItem.itemID]
                UpdateIconAndBackgroundFlagsOnNode(node)

    def _OnHomeStationChanged(self):
        homeStationService = homestation.Service.instance()
        if not homeStationService.is_home_station_data_loaded:
            uthread.new(homeStationService.get_home_station)

    def _UpdateHomeStation(self):
        homeStation = homestation.Service.instance().get_home_station()
        for node in self.scroll.sr.nodes:
            isHomeStation = node.itemID == homeStation.id
            if isHomeStation != node.isHomeStation:
                node.isHomeStation = isHomeStation
                if node.panel and node.panel.state != uiconst.UI_HIDDEN:
                    node.panel.Load(node)
                    UpdateIconAndBackgroundFlagsOnNode(node)

    def OnRefreshWhenDockingRequestDenied(self, structureID):
        self._RefreshStructureDockingAccess(structureID)

    def OnStructureAccessUpdated(self):
        structuresInOverview = {node.itemID for node in self.scroll.sr.nodes if node.slimItem and node.slimItem().categoryID == const.categoryStructure}
        for eachStructureID in structuresInOverview:
            self._RefreshStructureDockingAccess(eachStructureID)

    def _RefreshStructureDockingAccess(self, structureID):
        ballpark = self.michelle.GetBallpark()
        if not ballpark:
            return
        slimItem = ballpark.GetInvItem(structureID)
        if not slimItem:
            return
        if IsFlexStructure(slimItem.typeID):
            return
        node = self._scrollNodesByItemID.get(slimItem.itemID, None)
        if node:
            hasDockingRights = FindDockingRightsToDisplay(sm.GetService('structureProximityTracker'), slimItem)
            node.hasDockingRights = hasDockingRights
            if node.panel and node.panel.state != uiconst.UI_HIDDEN:
                node.panel.Load(node)
                node.panel.UpdateIcon()

    def OnFlagsInvalidated(self, itemIDs = None):
        if itemIDs:
            self.UpdateAllIconAndBackgroundFlagsForItemIDs(itemIDs)
        else:
            self.UpdateAllIconAndBackgroundFlagsForAllNodes()

    @telemetry.ZONE_METHOD
    def UpdateAllIconAndBackgroundFlagsForAllNodes(self):
        for node in self.scroll.sr.nodes:
            self.UpdateAllIconAndBackgroundFlagsForNode(node)

    @telemetry.ZONE_METHOD
    def UpdateAllIconAndBackgroundFlagsForItemIDs(self, itemIDs):
        for eachItemID in itemIDs:
            node = self._scrollNodesByItemID.get(eachItemID, None)
            if node:
                self.UpdateAllIconAndBackgroundFlagsForNode(node)

    def UpdateAllIconAndBackgroundFlagsForNode(self, node):
        if node.updateItem:
            UpdateIconAndBackgroundFlagsOnNode(node)
        else:
            slimItem = node.slimItem()
            if slimItem is not None and slimItem.groupID in const.containerGroupIDs:
                node.iconColor = None
                if node.panel is not None:
                    node.panel.UpdateIconColor()

    def OnReloadingOverviewProfile(self):
        self.FullReload()

    def OnOverviewPresetsChanged(self, *args):
        self.ReconstructTabs()

    def OnOverviewTabsChanged(self):
        self.ReconstructTabs()

    def OnColorblindModeChanged(self):
        self.ReconstructTabs()

    def OnBracketIconUpdated(self, itemID):
        node = self._scrollNodesByItemID.get(itemID, None)
        if node and node.panel:
            node.panel.UpdateIcon()

    def ReconstructTabs(self):
        if self.destroyed:
            return
        selectedID = self.tabGroup.GetSelectedID()
        tabIDs = self.presetSvc.GetTabIDs(self.windowInstanceID)
        if tabIDs is None:
            self.Close()
            return
        self.tabGroup.Flush()
        self._ConstructTabs(tabIDs)
        self._update_tabs_padding()
        self._update_window_controls()
        numTabs = len(self.presetSvc.GetSettingsByTabID())
        if not self.presetSvc.IsReadOnly():
            if numTabs < MAX_TAB_NUM and not self.compact:
                self.tabGroup.AddButton(icon=eveicon.add, func=self.AddTab, hint=localization.GetByLabel('UI/Overview/AddTab'))
        if selectedID is not None and selectedID in tabIDs:
            self.tabGroup.SelectByID(selectedID)
        else:
            self.tabGroup.AutoSelect()
        sm.ScatterEvent('OnOverviewTabsReconstructed')

    def _ShouldShowBracketDictatingIconButton(self):
        return self.presetSvc.IsBracketFilterDictatingWindow(self.windowInstanceID) and len(self.presetSvc.GetWindowInstanceIDs()) > 1

    def _ConstructTabs(self, tabIDs):
        for tabID in tabIDs:
            tabSettings = self.presetSvc.GetTabSettings(tabID)
            if not tabSettings:
                log.warning('No settings found for tabID=%s' % tabID)
                continue
            tabName = tabSettings.get(SETTING_TAB_NAME, None).strip()
            tabColor = tabSettings.get(SETTING_TAB_COLOR, None)
            if tabColor:
                hexColor = Color.RGBtoHex(*tabColor)
                tabName = '<color=%s>%s</color>' % (hexColor, tabName)
            self.tabGroup.AddTab(tabName, tabID=tabID)

    def GetCustomHeaderButtons(self):
        actions = super(OverviewWindow, self).GetCustomHeaderButtons()
        if not self.presetSvc.IsReadOnly() and self._ShouldShowBracketDictatingIconButton():
            actions.append(WindowMenuAction(window=self, label=localization.GetByLabel('UI/Overview/DictateBracketFilterHint'), icon=eveicon.brackets, callback=self.BracketButtonMenuCallback))
        return actions

    def BracketButtonMenuCallback(self, window):
        return [MenuEntryDataCaption(MenuLabel('UI/Overview/BracketVisibility'))] + GetBracketVisibilitySubMenu()

    def OnStateSetupChange(self, reason = None):
        self.FlagScrollEntriesDirty('OnStateSetupChange')

    def AddTab(self):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        addTabPopup = AddTabPopup.Open()
        if addTabPopup.ShowModal() != 1:
            return
        name, overviewPreset, bracketPreset, inNewWindow = addTabPopup.result
        wndInstanceID = None if inNewWindow else self.windowInstanceID
        self.presetSvc.AddTab(name, overviewPreset, bracketPreset, wndInstanceID)

    def _SetOpacity(self, value):
        if self.sr.underlay:
            display = True if value else False
            self.sr.underlay.display = display
        super(OverviewWindow, self)._SetOpacity(value)

    def OnSetActive_(self, *args):
        if self.scroll is not None:
            selected = self.scroll.GetSelected()
            if selected is None:
                self.scroll.SetSelected(0)

    def OnKeyUp(self, *args):
        selected = self.scroll.GetSelected()
        if not selected:
            return
        uicore.cmd.ExecuteCombatCommand(selected[0].itemID, uiconst.UI_KEYUP)

    def OnChar(self, *args):
        return False

    def OnTabSelected(self, tabID, oldTabID):
        self.presetSvc.LoadTab(tabID)
        self.displayChecker.UpdateState(tabID)
        self.sortHeaders.SetSubSettingID(tabID)
        presetName = self.presetSvc.GetTabPreset(tabID)
        self.UpdateWindowCaption(presetName)

    def OnColumnSizeReset(self, columnID):
        useSmallText = self.presetSvc.GetSettingValueOrDefaultFromName(osConst.SETTING_NAME_SMALL_TEXT, False)
        fontSize = GetEntryFontSize(useSmallText)
        labelClass = OverviewLabel
        widths = [COLUMNMINSIZE - COLUMNMARGIN * 2]
        for node in self.scroll.sr.nodes:
            displayValue = OverviewScrollEntry.GetColumnDisplayValue(node, columnID)
            if displayValue:
                textWidth, textHeight = labelClass.MeasureTextSize(displayValue, fontSize=fontSize)
                widths.append(textWidth)

        self.sortHeaders.SetColumnSize(columnID, max(widths) + COLUMNMARGIN * 2)
        self.TriggerInstantUpdate('OnColumnSizeReset')

    def OnColumnSizeChanged(self, columnID, headerWidth, currentSizes, *args):
        self.TriggerInstantUpdate('OnColumnSizeChanged')

    def OnSortingChange(self, oldColumnID, columnID, oldSortDirection, sortDirection):
        if oldColumnID == columnID and oldSortDirection != sortDirection:
            self.TriggerInstantUpdate('OnSortingChange')
        else:
            self.FlagScrollEntriesDirty_InstantUpdate('OnSortingChange')

    def OnScrollSelectionChange(self, nodes, *args):
        if not nodes:
            return
        node = nodes[0]
        if node and node.itemID:
            self.stateSvc.SetState(node.itemID, state.selected, 1)
            if sm.GetService('target').IsTarget(node.itemID):
                self.stateSvc.SetState(node.itemID, state.activeTarget, 1)

    def GetMenuMoreOptions(self):
        m = []
        if session.role & ROLE_GML:
            m.append(MenuEntryData('GM / WM Extras', subMenuData=self.GetDevMenu))
        if self.presetSvc.IsReadOnly():
            return m
        m.append(MenuEntryData(MenuLabel('UI/Overview/AddTab'), self.AddTab, texturePath=eveicon.add.resolve(16)))
        m.append(MenuEntryData(MenuLabel('UI/Commands/OpenOverviewSettings'), sm.GetService('tactical').OpenSettings, texturePath=eveicon.settings))
        if len(self.presetSvc.GetWindowInstanceIDs()) == 1:
            m.append(MenuEntryData(MenuLabel('UI/Overview/BracketVisibility'), subMenuData=GetBracketVisibilitySubMenu()))
        return super(OverviewWindow, self).GetMenuMoreOptions() + m

    def GetDevMenu(self):
        m = self.presetSvc.GetPresetsMenuElevated()
        m += [None, MenuEntryDataCheckbox('Show debug info', setting=overviewSettings.show_debug_info)]
        return m

    def _GetDeletePresetsSubMenu(self):
        allPresets = self.presetSvc.GetAllPresets().copy()
        for name in self.presetSvc.GetDefaultOverviewPresetNames():
            if name in allPresets:
                del allPresets[name]

        m = []
        for label in allPresets:
            m.append(MenuEntryData(label, lambda l = label: self.presetSvc.DeletePreset(l)))

        m.sort(key=lambda menuEntry: menuEntry.GetText())
        return m

    def Cleanup(self):
        pass

    @telemetry.ZONE_METHOD
    def UpdateAll(self, *args, **kwds):
        pass

    @telemetry.ZONE_METHOD
    def FullReload(self):
        self.StopOverviewUpdate()
        self.scroll.Clear()
        self._scrollNodesByItemID = {}
        self.FlagScrollEntriesAndBallparkDirty_InstantUpdate()

    def StopOverviewUpdate(self):
        if self.updateEntryOrderThread:
            self.updateEntryOrderThread.kill()
            self.updateEntryOrderThread = None

    def TriggerInstantUpdate(self, fromFunction = None):
        self.StopOverviewUpdate()
        if self.IsCollapsed() or self.IsMinimized():
            return
        self.UpdateEntryOrder()

    def FlagBallparkDirty(self, fromFunction = None):
        self._ballparkDirty = True
        if self.IsCollapsed() or self.IsMinimized():
            self.StopOverviewUpdate()
            return
        if not self.updateEntryOrderThread:
            self.updateEntryOrderThread = uthread.new(self.UpdateEntryOrder)

    def FlagScrollEntriesAndBallparkDirty_InstantUpdate(self, fromFunction = None):
        self._ballparkDirty = True
        self._scrollEntriesDirty = True
        self.TriggerInstantUpdate('FlagScrollEntriesDirtyDirty_InstantUpdate')

    def FlagScrollEntriesDirty_InstantUpdate(self, fromFunction = None):
        self._scrollEntriesDirty = True
        self.TriggerInstantUpdate('FlagScrollEntriesDirtyDirty_InstantUpdate')

    def FlagScrollEntriesDirty(self, fromFunction = None):
        self._scrollEntriesDirty = True
        if self.IsCollapsed() or self.IsMinimized():
            self.StopOverviewUpdate()
            return
        if not self.updateEntryOrderThread:
            self.updateEntryOrderThread = uthread.new(self.UpdateEntryOrder)

    @telemetry.ZONE_METHOD
    def _UpdateStaticDataForNodes(self, nodeList):
        structureProximityTrackerSvc = sm.GetService('structureProximityTracker')
        isDockingAccessUnknown = structureProximityTrackerSvc.HasDockingAccessChanged()
        emanationLockedGateID = GetLockedToGateID()
        usingLocalizationTooltips = localization.UseImportantTooltip()
        useSmallColorTags = self.presetSvc.GetSettingValueOrDefaultFromName(osConst.SETTING_NAME_SMALL_TAGS, False)
        useSmallText = self.presetSvc.GetSettingValueOrDefaultFromName(osConst.SETTING_NAME_SMALL_TEXT, False)
        columnWidths = self.sortHeaders.GetCurrentSizes()
        currentActive, _ = self.sortHeaders.GetCurrentActive()
        columnSettings, sortKeys = GetColumnSettingsAndSortKeys(currentActive, self.GetSelectedTabID())
        showIcon, sortIconIndex = columnSettings[COLUMN_ICON]
        showName, sortNameIndex = columnSettings[COLUMN_NAME]
        showDistance, sortDistanceIndex = columnSettings[COLUMN_DISTANCE]
        showSize, sortSizeIndex = columnSettings[COLUMN_SIZE]
        showAlliance, sortAllianceIndex = columnSettings[COLUMN_ALLIANCE]
        showType, sortTypeIndex = columnSettings[COLUMN_TYPE]
        showTag, sortTagIndex = columnSettings[COLUMN_TAG]
        showCorporation, sortCorporationIndex = columnSettings[COLUMN_CORPORATION]
        showFaction, sortFactionIndex = columnSettings[COLUMN_FACTION]
        showMilitia, sortMilitiaIndex = columnSettings[COLUMN_MILITIA]
        showVelocity, sortVelocityIndex = columnSettings[COLUMN_VELOCITY]
        showRadialVelocity, sortRadialVelocityIndex = columnSettings[COLUMN_RADIALVELOCITY]
        showAngularVelocity, sortAngularVelocityIndex = columnSettings[COLUMN_ANGULARVELOCITY]
        showTransversalVelocity, sortTransversalVelocityIndex = columnSettings[COLUMN_TRANSVERSALVELOCITY]
        defaultSortValue = [ 0 for _ in sortKeys ]
        inFleet = bool(session.fleetid)
        for node in nodeList:
            slimItem = node.slimItem()
            ball = node.ball()
            if not (ball and slimItem):
                node.leavingOverview = True
                if node.itemID in self._scrollNodesByItemID:
                    del self._scrollNodesByItemID[node.itemID]
                continue
            self._scrollNodesByItemID[node.itemID] = node
            node.usingLocalizationTooltips = usingLocalizationTooltips
            node.useSmallText = useSmallText
            node.useSmallColorTags = useSmallColorTags
            node.decoClass.ENTRYHEIGHT = GetEntryHeight(self.compact)
            node.fontSize = GetEntryFontSize()
            node.columns = overviewColumns.GetColumns(self.GetSelectedTabID())
            node.columnWidths = columnWidths
            node.sortNameIndex = sortNameIndex
            node.sortDistanceIndex = sortDistanceIndex
            node.sortIconIndex = sortIconIndex
            node.sortTagIndex = sortTagIndex
            node.sortVelocityIndex = sortVelocityIndex
            node.sortRadialVelocityIndex = sortRadialVelocityIndex
            node.sortAngularVelocityIndex = sortAngularVelocityIndex
            node.sortTransversalVelocityIndex = sortTransversalVelocityIndex
            sortValue = defaultSortValue[:]
            node.sortValue = sortValue
            if node.display_NAME is None:
                PrimeDisplayName(node)
            elif sortNameIndex is not None:
                sortValue[sortNameIndex] = node.display_NAME.lower()
            if showType and slimItem.typeID:
                if node.display_TYPE is None:
                    typeName = evetypes.GetName(slimItem.typeID)
                    if usingLocalizationTooltips:
                        typeName, hint = PrepareLocalizationTooltip(typeName)
                        node.hint_TYPE = hint
                    node.display_TYPE = typeName
                if sortTypeIndex is not None:
                    sortValue[sortTypeIndex] = node.display_TYPE.lower()
            if showSize:
                size = ball.radius * 2
                if node.display_SIZE is None:
                    node.display_SIZE = FmtDist(size)
                if sortSizeIndex is not None:
                    sortValue[sortSizeIndex] = size
            if showTag:
                if inFleet:
                    if node.display_TAG is None:
                        node.display_TAG = self.fleetSvc.GetTargetTag(node.itemID)
                else:
                    node.display_TAG = ''
                if sortTagIndex is not None:
                    tag = node.display_TAG
                    if tag is None:
                        sortValue[sortTagIndex] = 'zzz'
                    elif tag:
                        sortValue[sortTagIndex] = tag.lower()
                    else:
                        sortValue[sortTagIndex] = 0
            if showCorporation and slimItem.corpID:
                node.display_CORPORATION = corpTag = GetCorpTickerName(slimItem)
                if sortCorporationIndex is not None:
                    sortValue[sortCorporationIndex] = corpTag.lower()
            if showMilitia and slimItem.warFactionID:
                militia = cfg.eveowners.Get(slimItem.warFactionID).name
                if usingLocalizationTooltips:
                    militia, hint = PrepareLocalizationTooltip(militia)
                    node.hint_MILITIA = hint
                node.display_MILITIA = militia
                if sortMilitiaIndex is not None:
                    sortValue[sortMilitiaIndex] = militia.lower()
            if showAlliance and slimItem.allianceID:
                node.display_ALLIANCE = alliance = GetAllianceTickerName(slimItem)
                if sortAllianceIndex is not None:
                    sortValue[sortAllianceIndex] = alliance.lower()
            if showFaction:
                if slimItem.ownerID and IsNPC(slimItem.ownerID) or slimItem.charID and IsNPC(slimItem.charID):
                    factionID = get_corporation_faction_id(slimItem.ownerID or slimItem.charID)
                    if factionID:
                        faction = cfg.eveowners.Get(factionID).name
                        if usingLocalizationTooltips:
                            faction, hint = PrepareLocalizationTooltip(faction)
                            node.hint_FACTION = hint
                        node.display_FACTION = faction
                        if sortFactionIndex is not None:
                            sortValue[sortFactionIndex] = faction.lower()
            if emanationLockedGateID and slimItem.groupID == const.groupStargate:
                node.gateLockValue = GetGateLockValue(emanationLockedGateID, slimItem.itemID)
            if node.iconAndBackgroundFlags is None:
                iconFlag, backgroundFlag = (0, 0)
                if node.updateItem:
                    iconFlag, backgroundFlag = GetIconFlagAndBackgroundFlag(slimItem, self.stateSvc)
                node.iconAndBackgroundFlags = (iconFlag, backgroundFlag)
            if slimItem.categoryID == const.categoryStructure and not IsFlexStructure(slimItem.typeID) and node.hasDockingRights in (DOCKING_ACCESS_UNKNOWN, None):
                if isDockingAccessUnknown:
                    node.hasDockingRights = DOCKING_ACCESS_UNKNOWN
                elif slimItem.state != STATE_UNANCHORED:
                    hasDockingRights = FindDockingRightsToDisplay(structureProximityTrackerSvc, slimItem)
                    node.hasDockingRights = hasDockingRights
            if sortIconIndex is not None:
                iconFlag, backgroundFlag = node.iconAndBackgroundFlags
                node.iconColor, colorSortValue = GetIconColor(slimItem, getSortValue=True)
                if slimItem.categoryID == const.categoryStructure and colorSortValue:
                    iconFlag = colorSortValue
                sortValue[sortIconIndex] = [iconFlag,
                 colorSortValue,
                 backgroundFlag,
                 slimItem.categoryID,
                 slimItem.groupID,
                 slimItem.typeID]

    @telemetry.ZONE_METHOD
    def _UpdateDynamicDataForNodes(self, nodeList, doYield = False):
        bp = self.michelle.GetBallpark(doWait=True)
        if not bp:
            self.FlagBallparkDirty('DoBallsAdded')
            return
        myBall = bp.GetBall(eve.session.shipid)
        GetInvItem = bp.GetInvItem
        columns = overviewColumns.GetColumns(self.GetSelectedTabID())
        isDockingAccessUnknown = sm.GetService('structureProximityTracker').HasDockingAccessChanged()
        showDistance = COLUMN_DISTANCE in columns
        showIcon = COLUMN_ICON in columns
        homeStationID = None
        homeStationService = homestation.Service.instance()
        if homeStationService.is_home_station_data_loaded:
            homeStationID = homeStationService.get_home_station().id
        calculateAngularVelocity, calculateCombinedVelocity, calculateRadialNormal, calculateRadialVelocity, calculateTransveralVelocity, calculateVelocity, showVelocityCombined = GetColumnValuesToCalculate(columns)
        now = blue.os.GetSimTime()
        counter = 0
        for node in nodeList:
            ball = node.ball()
            slimItem = node.slimItem()
            if not slimItem:
                slimItem = GetInvItem(node.itemID)
                if slimItem:
                    node.slimItem = _weakref.ref(slimItem)
                    node.iconColor = None
                    PrimeDisplayName(node)
                    if node.panel:
                        if showIcon:
                            node.panel.UpdateIcon()
                            node.panel.UpdateIconColor()
                    UpdateIconAndBackgroundFlagsOnNode(node)
            if ball:
                if showDistance:
                    ball.GetVectorAt(now)
                    node.rawDistance = rawDistance = max(ball.surfaceDist, 0)
                    if node.sortDistanceIndex is not None:
                        node.sortValue[node.sortDistanceIndex] = rawDistance
                if showVelocityCombined and ball.isFree and myBall:
                    ball.GetVectorAt(now)
                    UpdateVelocityData(node, ball, myBall, calculateVelocity, calculateRadialVelocity, calculateCombinedVelocity, calculateRadialNormal, calculateTransveralVelocity, calculateAngularVelocity)
            self._UpdateStructureNode(node, slimItem, isDockingAccessUnknown)
            if homeStationID is not None:
                node.isHomeStation = homeStationID == node.itemID
            if doYield:
                counter += 1
                if counter == 20:
                    blue.pyos.BeNice()
                    if self.destroyed:
                        self.StopOverviewUpdate()
                        return
                    counter = 0

    @telemetry.ZONE_METHOD
    def _UpdateStructureNode(self, node, slimItem, isDockingAccessUnknown):
        if not slimItem:
            return
        if slimItem.categoryID != const.categoryStructure:
            return
        itemID = slimItem.itemID
        if not sm.GetService('structureProximityTracker').IsStructureVisible(itemID):
            node.leavingOverview = True
            if itemID in self._scrollNodesByItemID:
                del self._scrollNodesByItemID[itemID]
        if IsFlexStructure(slimItem.typeID):
            pass
        elif isDockingAccessUnknown and node.hasDockingRights != DOCKING_ACCESS_UNKNOWN:
            node.hasDockingRights = DOCKING_ACCESS_UNKNOWN
            UpdateIconAndBackgroundFlagsOnNode(node)
            if node.panel:
                node.panel.UpdateIcon()

    @telemetry.ZONE_METHOD
    def CheckForNewEntriesAndRefreshScrollSetup(self):
        ballpark = self.michelle.GetBallpark(doWait=True)
        if ballpark is None:
            return
        if self.destroyed:
            return
        columns = overviewColumns.GetColumns(self.GetSelectedTabID())
        self.sortHeaders.CreateColumns(columns, fixedColumns=FIXEDCOLUMNS)
        newEntries = []
        currentNotWanted = set()
        with ScrollListLock:
            if self._ballparkDirty:
                GetInvItem = ballpark.GetInvItem
                currentItemIDs = self._scrollNodesByItemID
                log.info('Overview - Checking ballpark for new entries')
                for itemID in ballpark.balls.keys():
                    slimItem = GetInvItem(itemID)
                    display = self.displayChecker.ShouldDisplayItem(slimItem)
                    if not display:
                        if itemID in currentItemIDs:
                            currentNotWanted.add(itemID)
                            if itemID in self._scrollNodesByItemID:
                                node = self._scrollNodesByItemID[itemID]
                                node.leavingOverview = True
                                del self._scrollNodesByItemID[itemID]
                        continue
                    if itemID not in currentItemIDs:
                        newNode = self._ConstructScrollEntry(itemID, slimItem, ballpark)
                        newEntries.append(newNode)

            nodeList = newEntries[:]
            if self._scrollEntriesDirty:
                log.info('Overview - Update static data on current overview entries')
                nodeList.extend([ node for node in self.scroll.sr.nodes if node.itemID not in currentNotWanted ])
            self._UpdateStaticDataForNodes(nodeList)
            self.scroll.PurgeInvisibleEntries()
            self.overviewSorted = False
            if newEntries:
                self.scroll.ShowHint()
                self.scroll.AddNodes(-1, newEntries)
        return newEntries

    def _ConstructScrollEntry(self, itemID, slimItem, ballpark):
        updateItem = self.stateSvc.CheckIfUpdateItem(slimItem)
        newNode = GetFromClass(OverviewScrollEntry, {'itemID': itemID,
         'updateItem': updateItem})
        ball = ballpark.GetBall(itemID)
        newNode.ball = _weakref.ref(ball)
        newNode.slimItem = _weakref.ref(slimItem)
        if updateItem:
            newNode.ewarGraphicIDs = self.GetEwarDataForNode(newNode)
        newNode.ewarHints = self.ewarHintsByGraphicID
        return newNode

    @telemetry.ZONE_METHOD
    def UpdateEntryOrder(self, doYield = False):
        if self.destroyed:
            return
        newEntries = False
        if self._ballparkDirty or self._scrollEntriesDirty:
            newEntries = self.CheckForNewEntriesAndRefreshScrollSetup()
            if newEntries:
                doYield = False
            self._ballparkDirty = False
            self._scrollEntriesDirty = False
        updateStartTime = blue.os.GetWallclockTimeNow()
        try:
            if not eve.session.solarsystemid:
                self.StopOverviewUpdate()
                return
            if self.IsCollapsed() or self.IsMinimized():
                self.StopOverviewUpdate()
                return
            if self.destroyed:
                return
            bp = self.michelle.GetBallpark(doWait=True)
            if not bp:
                self.StopOverviewUpdate()
                return
            columnWidths = self.sortHeaders.GetCurrentSizes()
            broadcastsToTop = self.presetSvc.GetSettingValueBroadcastToTop()
            fleetBroadcasts = self.fleetSvc.GetCurrentFleetBroadcasts()
            mouseCoords = trinity.mainWindow.GetCursorPos()
            if mouseCoords != self.prevMouseCoords:
                self.lastMovementTime = blue.os.GetWallclockTime()
                self.prevMouseCoords = mouseCoords
            insider = IsUnder(uicore.uilib.mouseOver, self.scroll.GetContentContainer()) or uicore.uilib.mouseOver is self.scroll.GetContentContainer()
            mouseMoving = blue.os.TimeDiffInMs(self.lastMovementTime, blue.os.GetWallclockTime()) > self.mouseMovementTimeout
            mouseInsideApp = mouseCoords[0] > 0 and mouseCoords[0] < trinity.app.width and mouseCoords[1] > 0 and mouseCoords[1] < trinity.app.height
            sortingFrozen = self.sortingFrozen = insider and mouseInsideApp and not mouseMoving or self._freezeOverview
            if sortingFrozen:
                updateList = self.scroll.GetVisibleNodes()
                self.sortHeaders.SetSortIcon('res:/UI/Texture/classes/Overview/columnLock.png')
            else:
                updateList = self.scroll.sr.nodes
                self.sortHeaders.SetSortIcon(None)
            currentActive, currentDirection = self.sortHeaders.GetCurrentActive()

            def GetSortValue(_node):
                if broadcastsToTop:
                    return GetSortValueWhenBroadcastGoToTop(_node, fleetBroadcasts, currentDirection)
                return _node.sortValue

            ballpark = self.michelle.GetBallpark(doWait=True)
            if ballpark is None:
                return
            self._UpdateDynamicDataForNodes(updateList, doYield=doYield)
            counter = 0
            nodesToRemove = []
            for node in updateList:
                node.columnWidths = columnWidths
                if node.leavingOverview:
                    if node.panel:
                        node.panel.opacity = 0.25
                        node.panel.state = uiconst.UI_DISABLED
                    nodesToRemove.append(node)
                    continue
                ball = node.ball()
                slimItem = node.slimItem()
                if not (slimItem and ball):
                    node.leavingOverview = True
                    if node.itemID in self._scrollNodesByItemID:
                        del self._scrollNodesByItemID[node.itemID]
                    if node.panel:
                        node.panel.opacity = 0.25
                        node.panel.state = uiconst.UI_DISABLED
                    nodesToRemove.append(node)
                    continue
                if doYield:
                    counter += 1
                    if counter == 20:
                        blue.pyos.BeNice()
                        if self.destroyed:
                            self.StopOverviewUpdate()
                            return
                        counter = 0

            if doYield:
                blue.synchro.Yield()
                if self.destroyed:
                    self.StopOverviewUpdate()
                    return
            if not sortingFrozen:
                if nodesToRemove:
                    self.scroll.RemoveNodes(nodesToRemove)
                currentActive, currentDirection = self.sortHeaders.GetCurrentActive()
                with ScrollListLock:
                    sortlist = sorted(self.scroll.sr.nodes, key=GetSortValue, reverse=not currentDirection)
                    self.scroll.SetOrderedNodes(sortlist, loadNodes=False)
                self.overviewSorted = True
            else:
                self.overviewSorted = False
            self.LoadVisibleEntriesIfNeverLoaded()
            self.CheckShowNoContentHint()
        except Exception:
            log.exception('Error updating inflight overview')
            sys.exc_clear()

        if doYield:
            diff = (gametime.GetWallclockTimeNow() - updateStartTime) / const.SEC
            duration = max(overviewConst.ENTRY_ORDER_UPDATE_SLEEP - diff, overviewConst.ENTRY_ORDER_UPDATE_SLEEP_MIN)
            uthread2.sleep(duration)
        if not self.destroyed and (not self.updateEntryOrderThread or self.updateEntryOrderThread == stackless.getcurrent()):
            self.updateEntryOrderThread = uthread.new(self.UpdateEntryOrder, doYield=True)

    def LoadVisibleEntriesIfNeverLoaded(self):
        visibleNodes = self.scroll.GetVisibleNodes()
        self._UpdateDynamicDataForNodes(visibleNodes)
        for node in visibleNodes:
            entry = node.panel
            if entry and entry.display and not entry.hasLoaded:
                entry.Load(node)

    def LoadVisibleEntries(self):
        visibleNodes = self.scroll.GetVisibleNodes()
        self._UpdateDynamicDataForNodes(visibleNodes)
        for node in visibleNodes:
            entry = node.panel
            if entry and entry.state != uiconst.UI_HIDDEN:
                entry.Load(node)

    def CheckShowNoContentHint(self):
        if not self.scroll.sr.nodes:
            self.scroll.ShowHint(localization.GetByLabel('UI/Common/NothingFound'))
        else:
            self.scroll.ShowHint()

    def OnFreezeOverviewWindows(self):
        self._SetFreezeOverview(True)

    def OnUnfreezeOverviewWindows(self):
        self._SetFreezeOverview(False)

    def _SetFreezeOverview(self, freeze = True):
        triggerUpdate = False
        if not freeze and freeze != self._freezeOverview:
            triggerUpdate = True
        self._freezeOverview = freeze
        if triggerUpdate and getattr(self, 'overviewSorted', False) is False:
            self.TriggerInstantUpdate('SetFreezeOverview')

    def UpdateForOneCharacter(self, charID, *args):
        pass

    def OnExpanded(self, *args):
        super(OverviewWindow, self).OnExpanded(*args)
        self.TriggerInstantUpdate('OnExpanded')

    def OnCollapsed(self, *args):
        super(OverviewWindow, self).OnCollapsed(*args)
        self.StopOverviewUpdate()
        self.cachedScrollPos = self.scroll.GetScrollProportion()

    def OnEndMaximize_(self, *args):
        self.TriggerInstantUpdate('OnEndMaximize_')

    def OnEndMinimize_(self, *args):
        self.StopOverviewUpdate()
        self.cachedScrollPos = self.scroll.GetScrollProportion()

    def GetSelectedTabID(self):
        if self.tabGroup:
            return self.tabGroup.GetSelectedID()

    def OnSessionChanged(self, isRemote, session, change):
        if self.destroyed:
            return
        if 'solarsystemid' in change:
            self.scroll.Clear()
            self._scrollNodesByItemID = {}
        if 'shipid' in change:
            self.FlushEwarStates()
            self.FlagBallparkDirty('OnSessionChanged')

    def OnEnterSpace(self):
        self.FlagBallparkDirty('OnEnterSpace')

    def OnOverviewOverrideChanged(self):
        self.FlagBallparkDirty('OnOverviewOverrideChanged')

    def OnItemHighlighted(self, itemID, isActive):
        node = self._scrollNodesByItemID.get(itemID, None)
        if node is None:
            return
        if node.panel:
            node.panel.UpdateTutorialHighlight(isActive)

    def OnStructuresVisibilityUpdated(self):
        self.FlagBallparkDirty('OnStructuresVisibilityUpdated')

    def GetNextInRouteNodeAndDirection(self):
        destinationPath = sm.GetService('starmap').GetDestinationPath()
        if not destinationPath:
            return (None, None)
        nextInRouteItemID = destinationPath[0]
        isSolarSystem = IsSolarSystem(nextInRouteItemID)
        nextInRouteNode = None
        for eachNode in self.scroll.GetNodes():
            if eachNode.itemID == nextInRouteItemID:
                nextInRouteNode = eachNode
                break
            if isSolarSystem and eachNode.slimItem:
                slimItem = eachNode.slimItem()
                if slimItem.groupID in (const.groupStargate, const.groupUpwellJumpGate):
                    if slimItem.jumps and slimItem.jumps[0].locationID == nextInRouteItemID:
                        nextInRouteNode = eachNode
                        break

        if not nextInRouteNode:
            return (None, None)
        if nextInRouteNode.panel and nextInRouteNode.panel.IsVisible():
            return (nextInRouteNode.panel, None)
        myNodeIdx = nextInRouteNode.idx
        visibleNodes = self.scroll.GetVisibleNodes()
        if visibleNodes:
            firstNode = visibleNodes[0]
            lastNode = visibleNodes[-1]
            if firstNode.idx > myNodeIdx:
                pointToInstead = self.sortHeaders or firstNode.panel
                return (pointToInstead, 'up')
            if lastNode.idx < myNodeIdx:
                pointToInstead = lastNode.panel
                return (pointToInstead, 'down')
        return (None, None)

    def OnEmanationLockUpdated(self, lockDetails):
        if not lockDetails or lockDetails.solar_system_id != session.solarsystemid2:
            return
        self._UpdateEmanationLock()

    def OnEmanationGateLockRemoved(self, *args):
        self._UpdateEmanationLock()

    def _UpdateEmanationLock(self):
        systemInfo = cfg.mapSolarSystemContentCache.get(session.solarsystemid2, None)
        if not systemInfo:
            return
        for gateID in systemInfo.stargates.iterkeys():
            node = self._scrollNodesByItemID.get(gateID, None)
            if not node:
                continue
            slimItem = node.slimItem()
            node.gateLockValue = GetGateLockValueForSlimItem(slimItem)
            if node.panel:
                UpdateIconAndBackgroundFlagsOnNode(node)


class BracketButtonIcon(ButtonIcon):
    expandOnLeft = True

    def GetMenu(self, *args):
        return GetBracketVisibilitySubMenu()
