#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\dungeoneditor.py
import copy
import blue
import evecamera
import evetypes
import localization
import trinity
import uthread
import utillib
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from eve.client.script.parklife import dungeonHelper, states
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.control.message import ShowQuickMessage
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const
from evecamera.dungeonhack import DungeonHack
from ballparkCommon.ballRadius import ComputeRadiusFromQuantity
from eve.client.script.ui.control import eveIcon, eveLabel, eveScroll
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
pi = 3.141592653589793

def GetMessageFromLocalization(messageID):
    return localization.GetByMessageID(messageID)


class DungeonEditor(Window):
    __guid__ = 'form.DungeonEditor'
    __nonpersistvars__ = []
    __notifyevents__ = ['OnJessicaOpenDungeon',
     'OnJessicaOpenRoom',
     'OnDESelectionChanged',
     'OnDEObjectPaletteChanged',
     'OnDEObjectListChanged',
     'OnSelectObject',
     'OnDungeonEdit',
     'OnDungeonSelectionGroupRotation',
     'OnStateChange']
    default_windowID = 'dungeoneditor'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self._navigation = DungeonHack()
        self.loadedTab = None
        self.roomTabSelected = 'Objects'
        self.loadingThread = None
        self.scope = uiconst.SCOPE_INFLIGHT
        self.SetCaption('Dungeon Editor')
        self.LoadPanels()
        self.SetMinSize([350, 400])
        self.prevDungeonResults = None
        self.prevFactionID = None
        self.prevArchetypeID = None
        self.filterText = ''
        self.objectGroups = {}
        self.groupNameToIDMap = {}
        self.scenario = sm.GetService('scenario')
        if dungeonHelper.IsJessicaOpen():
            self.cache = sm.GetService('cache')
        else:
            self.cache = sm.RemoteSvc('cache')
        sm.GetService('sceneManager').SetPrimaryCamera(evecamera.CAM_TACTICAL)

    def LoadPanels(self):
        panel = Container(name='panel', parent=self.sr.main, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding)
        self.sr.panel = panel
        self.sr.roomobjecttabs = TabGroup(name='tabparent', parent=self.sr.main, idx=0, tabs=[['Objects',
          panel,
          self,
          'RoomObjectTab'], ['Groups',
          panel,
          self,
          'RoomGroupTab']], groupID='roomobjectstab')
        self.sr.maintabs = TabGroup(name='tabparent', parent=self.sr.main, idx=0, tabs=[['Dungeons',
          panel,
          self,
          'DungeonTab'],
         ['Room objects',
          panel,
          self,
          'RoomTab'],
         ['Transform',
          panel,
          self,
          'AlignTab'],
         ['Settings',
          panel,
          self,
          'SettingTab'],
         ['Palette',
          panel,
          self,
          'PaletteTab']], groupID='tabgroupid')

    def Load(self, tabid):
        if self.loadingThread and self.loadingThread.alive:
            self.loadingThread.kill()
        self.UnloadPanel()
        self.loadedTab = None
        tabName = 'Load_%s' % tabid
        if hasattr(self, tabName):
            if tabName in ('Load_RoomTab', 'Load_RoomObjectTab', 'Load_RoomGroupTab'):
                self.sr.roomobjecttabs.display = True
            else:
                self.sr.roomobjecttabs.display = False
            self.loadedTab = tabid
            self.loadingThread = uthread.new(getattr(self, tabName))
            self.loadingThread.context = 'DungeonEditor::%s' % tabName

    def UpdateGridVisibility(self):
        if self.loadedTab == 'PaletteTab':
            self._navigation.SetGridState(True)
            self._navigation.SetDrawAxis(True)
        else:
            showGrid = self.gridCheckbox.GetValue()
            self._navigation.SetGridState(showGrid)
            self._navigation.SetDrawAxis(showGrid)
        self._navigation.SetGridSpacing(self.gridSpacingDropdown.GetValue())
        self._navigation.SetGridLength(self.gridSizeDropdown.GetValue())

    def IsTabLoaded(self, tabId):
        return tabId == self.loadedTab

    def Refresh(self):
        self.Load(self.loadedTab)

    def UnloadPanel(self):
        self.sr.panel.Flush()
        self.sr.palettescroll = None
        self.sr.templatescroll = None

    def _GetDungeons(self):
        archetypeID = settings.user.ui.Get('dungeonArchetypeID', None)
        factionID = settings.user.ui.Get('dungeonFactionID', None)
        if self.prevDungeonResults is None or self.prevArchetypeID != archetypeID or self.prevFactionID != factionID:
            comboOptions = []
            dungeons = sm.RemoteSvc('dungeon').DEGetDungeons(archetypeID=archetypeID, factionID=factionID)
            for dungeon in dungeons:
                factionID = dungeon.factionID
                if dungeon.dungeonNameID is not None:
                    name = GetMessageFromLocalization(dungeon.dungeonNameID)
                else:
                    name = ''
                if factionID:
                    factionName = cfg.eveowners.Get(factionID).name
                    name = '%s (%s) [%d]' % (name, factionName, dungeon.dungeonID)
                else:
                    name = '%s [%d]' % (name, dungeon.dungeonID)
                comboOptions.append((name, dungeon.dungeonID))

            comboOptions.sort()
            comboOptions.insert(0, [' - Select Dungeon - ', None])
            self.prevArchetypeID = archetypeID
            self.prevFactionID = factionID
            self.prevDungeonResults = comboOptions
        comboOptions = self.prevDungeonResults
        filterText = self.filterText.lower()
        optionsFilter = lambda option: filterText in option[0].lower()
        comboOptions = filter(optionsFilter, comboOptions)
        availableDungeons = map(lambda option: option[1], comboOptions)
        return (comboOptions, availableDungeons)

    def _CreateCombo(self, comboOptions, comboID):
        comboSetval = settings.user.ui.Get(comboID, None)
        if comboSetval == 'All':
            settings.user.ui.Set(comboID, None)
            comboSetval = None
        return Combo(parent=self.sr.panel, label='', options=comboOptions, name=comboID, select=comboSetval, callback=self.OnComboChange, align=uiconst.TOTOP)

    def OnFilterDungeon(self, *args):
        self.filterText = self.dungeonFilter.GetValue()
        self.sr.maintabs.ReloadVisible()

    def OnGodMode(self, *args):
        settings.user.ui.Set('dungeonGodMode', self.godModeCheckbox.GetValue())

    def Load_DungeonTab(self):
        eveLabel.EveLabelMedium(text='Search Dungeons:', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        Container(name='push', parent=self.sr.panel, align=uiconst.TOTOP, height=const.defaultPadding)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=20)
        sb = Button(parent=row, label='Search', func=self.OnFilterDungeon, align=uiconst.CENTERRIGHT, left=2)
        self.dungeonFilter = SingleLineEditText(name='dungeonFilter', parent=row, setvalue=self.filterText, align=uiconst.TOALL, padRight=sb.width + 4, OnReturn=self.OnFilterDungeon)
        Container(name='push', parent=self.sr.panel, align=uiconst.TOTOP, height=const.defaultPadding)
        eveLabel.EveLabelMedium(text='Optional Filters:', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        Container(name='push', parent=self.sr.panel, align=uiconst.TOTOP, height=const.defaultPadding)
        eveLabel.EveLabelMedium(text='Archetype:', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        archetypeOptions = sm.RemoteSvc('dungeon').DEGetArchetypes()
        archetypeOptions.sort()
        archetypeOptions.insert(0, ('All', None))
        self._CreateCombo(archetypeOptions, 'dungeonArchetypeID')
        Container(name='push', parent=self.sr.panel, align=uiconst.TOTOP, height=const.defaultPadding)
        eveLabel.EveLabelMedium(text='Faction:', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        factions = sm.RemoteSvc('dungeon').DEGetFactions()
        factionOptions = [ (cfg.eveowners.Get(factionID).name, factionID) for factionID in factions ]
        factionOptions.sort()
        factionOptions.insert(0, ('All', None))
        self._CreateCombo(factionOptions, 'dungeonFactionID')
        Container(name='pusher', align=uiconst.TOTOP, height=24, parent=self.sr.panel)
        eveLabel.EveLabelMedium(text='Select Dungeon:', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        Container(name='push', parent=self.sr.panel, align=uiconst.TOTOP, height=const.defaultPadding)
        comboOptions, availableDungeons = self._GetDungeons()
        comboID = 'dungeonDungeon'
        dungeonID = settings.user.ui.Get(comboID, 'All')
        Combo(parent=self.sr.panel, label='', options=comboOptions, name=comboID, select=dungeonID, callback=self.OnComboChange, align=uiconst.TOTOP)
        Container(name='pusher', align=uiconst.TOTOP, height=16, parent=self.sr.panel)
        eveLabel.EveLabelMedium(text='Select Room:', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        if dungeonID not in availableDungeons:
            Container(name='push', parent=self.sr.panel, align=uiconst.TOTOP, height=const.defaultPadding * 2)
            eveLabel.EveLabelMedium(text=' - No dungeon selected - ', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
            return
        seldungeon = sm.RemoteSvc('dungeon').DEGetDungeons(dungeonID=dungeonID)[0]
        eveLabel.EveLabelMedium(text=GetMessageFromLocalization(seldungeon.dungeonNameID) + ' - Version ', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOBOTTOM, height=16, padTop=4)
        godMode = settings.user.ui.Get('dungeonGodMode', 1)
        self.godModeCheckbox = Checkbox(text='God Mode', parent=row, settingsKey='dungeonGodMode', checked=godMode, callback=self.OnGodMode)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOBOTTOM, height=16, padTop=4)
        Button(parent=row, label='Play Dungeon', func=self.PlayDungeon, align=uiconst.TOLEFT, padLeft=4)
        Button(parent=row, label='Go to selected room', func=self.GotoRoom, args=(), align=uiconst.TOLEFT, padLeft=4)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOBOTTOM, height=16)
        Button(parent=row, label='Edit Room', func=self.EditRoom, align=uiconst.TOLEFT, padLeft=4)
        Button(parent=row, label='Save Room', func=self.SaveRoom, align=uiconst.TOLEFT, padLeft=4)
        Button(parent=row, label='Reset', func=self.ResetDungeon, args=(), align=uiconst.TORIGHT, padLeft=4)
        Container(name='push', parent=self.sr.panel, align=uiconst.TOBOTTOM, height=const.defaultPadding)
        rooms = sm.RemoteSvc('dungeon').DEGetRooms(dungeonID=seldungeon.dungeonID)
        Container(name='push', parent=self.sr.panel, align=uiconst.TOTOP, height=const.defaultPadding)
        self.scrollOptions = []
        for i, (roomID, roomName) in enumerate(rooms):
            self.scrollOptions.append(GetFromClass(Generic, {'label': '[%d] %s' % (roomID, roomName),
             'id': i + 1,
             'roomID': roomID,
             'OnClick': self.OnGotoSelectedRoomClicked}))

        self.sr.objscrollbox = eveScroll.Scroll(parent=self.sr.panel, name='scrollID')
        self.sr.objscrollbox.LoadContent(contentList=self.scrollOptions)
        if settings.user.ui.Get('selectedRoomID', None):
            rooms = self.sr.objscrollbox.GetNodes()
            for room in rooms:
                if room.roomID == settings.user.ui.Get('selectedRoomID', None):
                    self.sr.objscrollbox.SelectNode(room)
                    break

    def OnJessicaOpenDungeon(self, dungeonID, defaultRoomID = None):
        self.OnJessicaOpenRoom(dungeonID, defaultRoomID)

    def OnJessicaOpenRoom(self, dungeonID, roomID):
        settings.user.ui.Set('dungeonDungeon', dungeonID)
        self.loadedTab = 'DungeonTab'
        for tab in self.sr.maintabs.sr.tabs:
            if tab.sr.args == self.loadedTab:
                tab.Select()

        settings.user.ui.Set('selectedRoomID', roomID)
        if roomID:
            self.EditRoom()

    def ResetDungeon(self):
        sm.GetService('scenario').ResetDungeon()

    def PlayDungeon(self, *args):
        dungeonID = settings.user.ui.Get('dungeonDungeon', None)
        if dungeonID is None or dungeonID == 'All':
            return
        roomID = settings.user.ui.Get('selectedRoomID', None)
        if not roomID:
            objectList = self.sr.objscrollbox.GetNodes()
            if len(objectList) > 0:
                roomID = objectList[0].roomID
            else:
                return
        godMode = settings.user.ui.Get('dungeonGodMode', 1)
        sm.GetService('scenario').PlayDungeon(dungeonID, roomID, godmode=godMode)

    def EditRoom(self, *args):
        dungeonID = settings.user.ui.Get('dungeonDungeon', None)
        if dungeonID is None or dungeonID == 'All':
            return
        if not settings.user.ui.Get('selectedRoomID', None):
            objectList = self.sr.objscrollbox.GetNodes()
            if len(objectList) > 0:
                settings.user.ui.Set('selectedRoomID', objectList[0].roomID)
            else:
                return
        sm.GetService('scenario').EditRoom(dungeonID, settings.user.ui.Get('selectedRoomID', None))

    def SaveRoom(self, *args):
        sm.StartService('scenario').SaveAllChanges()

    def GotoRoom(self, *args):
        roomID = settings.user.ui.Get('selectedRoomID', None)
        if roomID:
            sm.GetService('scenario').GotoRoom(roomID)

    def OnDungeonEdit(self, dungeonID, roomID, roomPos):
        self.InitializeSelectionGroups(roomID)

    def InitializeSelectionGroups(self, roomID):
        scenario = sm.StartService('scenario')
        self.objectGroups = {}
        self.groupNameToIDMap = {}
        scenario.RemoveAllHardGroups()

    def GetCurrentRoomID(self):
        return sm.RemoteSvc('keeper').GetLevelEditor().GetCurrentlyEditedRoomID()

    def Load_RoomTab(self):
        dunObjs = self.scenario.GetDunObjects()
        if len(dunObjs) == 0:
            Container(name='push', parent=self.sr.panel, align=uiconst.TOTOP, height=28)
            eveLabel.EveLabelMedium(text='No dungeon objects found', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
            return
        if hasattr(self, 'Load_%sTab' % self.roomTabSelected):
            getattr(self, 'Load_%sTab' % self.roomTabSelected)()
        self.loadedTab = 'RoomTab'

    def Load_RoomObjectTab(self):
        self.roomTabSelected = 'Objects'
        self.Load_RoomTab()

    def Load_RoomGroupTab(self):
        self.roomTabSelected = 'Groups'
        self.Load_RoomTab()

    def Load_ObjectsTab(self):
        self.roomTabSelected = 'Objects'
        dunObjs = sm.GetService('scenario').GetDunObjects()
        scrollOptions = []
        boxItems = []
        for slimItem in dunObjs:
            if getattr(slimItem, 'dunObjectID', None) is not None:
                typeName = evetypes.GetName(slimItem.typeID)
                objName = cfg.evelocations.Get(slimItem.itemID).name
                entryName = typeName + ' : ' + objName
                boxItems.append([entryName,
                 slimItem.dunObjectID,
                 sm.GetService('scenario').IsSelectedByObjID(slimItem.dunObjectID),
                 slimItem.itemID,
                 slimItem.typeID])

        boxItems.sort()
        for objName, objID, selected, itemID, typeID in boxItems:
            scrollOptions.append(GetFromClass(Generic, {'label': objName,
             'id': objID,
             'itemID': itemID,
             'typeID': typeID,
             'OnClick': self.OnObjectClicked,
             'isSelected': selected,
             'GetMenu': self.GetItemMenu}))

        self.sr.objscrollbox = eveScroll.Scroll(parent=self.sr.panel, name='scrollID', align=uiconst.TOTOP, height=256)
        self.sr.objscrollbox.LoadContent(contentList=scrollOptions)
        Container(name='push', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=20)
        Button(parent=row, label='Select All', func=self.ObjSelectAll, args=(), align=uiconst.TOLEFT, padLeft=4)
        Button(parent=row, label='Invert selection', func=self.ObjInverseSel, args=(), align=uiconst.TOLEFT, padLeft=4)
        Button(parent=row, label='Clear selection', func=self.ObjClearSel, args=(), align=uiconst.TOLEFT, padLeft=4)
        Container(name='push', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        eveLabel.EveLabelMedium(text='Duplicate: ', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        counter = 0
        for each in 'XYZ':
            checkbox1ID = 'duplicateOffset%s' % each
            curVal = 0
            eveLabel.EveLabelMedium(text=each, parent=row, left=50 + counter * 52, state=uiconst.UI_NORMAL)
            ed = SingleLineEditInteger(name='duplicateOffset%s' % each, parent=row, setvalue=curVal, pos=(60 + counter * 52,
             0,
             38,
             0), minValue=-30000, maxValue=30000)
            counter = counter + 1
            setattr(self, checkbox1ID, ed)

        eveLabel.EveLabelMedium(text='Offset: ', parent=row, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=32)
        self.duplicateAmount = SingleLineEditInteger(name='duplicateAmount', parent=row, setvalue=1, pos=(60, 0, 38, 0), minValue=1, maxValue=100)
        eveLabel.EveLabelMedium(text='Amount: ', parent=row, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=20)
        Button(parent=row, label='Delete selected', func=self.OnDeleteSelected, args=(), align=uiconst.TORIGHT, padLeft=4)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=20, padTop=4)
        Button(parent=row, label='Save Room', func=self.SaveRoom, align=uiconst.TOLEFT, padLeft=4)

    def Load_GroupsTab(self):
        self.roomTabSelected = 'Groups'
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        dunObjs = sm.GetService('scenario').GetDunObjects()
        scrollOptions = []
        selectedGroups = self.GetSelectedGroups()
        groups = self.objectGroups.items()
        groups.sort()
        boxItems = [ [index,
         groupName,
         groupItems,
         groupName in selectedGroups] for index, (groupName, groupItems) in enumerate(groups) ]
        for index, groupName, groupItems, selected in boxItems:
            scrollOptions.append(GetFromClass(ObjectGroupListEntry, {'label': groupName,
             'id': index,
             'groupItems': groupItems,
             'OnClick': self.OnObjectGroupClicked,
             'isSelected': selected,
             'locked': False,
             'form': self}))

        self.sr.objgroupscrollbox = eveScroll.Scroll(parent=self.sr.panel, name='scrollID', align=uiconst.TOTOP, height=256)
        self.sr.objgroupscrollbox.LoadContent(contentList=scrollOptions)
        Container(name='push', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        Button(parent=row, label='Rename Group', func=self.OnRenameGroup, args=(), align=uiconst.TOLEFT)
        Button(parent=row, label='Remove Group', func=self.OnRemoveGroup, args=(), align=uiconst.TOLEFT)
        Button(parent=row, label='Delete Group Objects', func=self.OnDeleteSelectedGroup, args=(), align=uiconst.TOLEFT)

    def GetItemMenu(self, entry):
        info = entry.sr.node
        m = GetMenuService().GetMenuFromItemIDTypeID(info.itemID, info.typeID)
        return m

    def OnStateChange(self, itemID, flag, flagState, *args):
        if flag == states.selected and flagState:
            dunObjectID = sm.GetService('michelle').GetItem(itemID).dunObjectID
            if dunObjectID:
                sm.GetService('scenario').SetSelectionByID([dunObjectID])

    def OnObjectClicked(self, entry, *args):
        uicore.cmd.ExecuteCombatCommand(entry.sr.node.itemID, uiconst.UI_CLICK)
        if self.sr.objscrollbox:
            ids = self.GetCurrentlySelectedObjects()
            sm.StartService('scenario').SetSelectionByID(ids)

    def OnObjectGroupClicked(self, entry, *args):
        self.SelectObjectGroup(entry.sr.node.label)

    def IsGroupSelected(self, groupName):
        return self.scenario.AreAllSelected(self.objectGroups[groupName])

    def GetSelectedGroups(self):
        return filter(self.IsGroupSelected, self.objectGroups.iterkeys())

    def SelectObjectGroup(self, label):
        if label not in self.objectGroups:
            return
        scenarioSvc = sm.StartService('scenario')
        selectedGroup = self.objectGroups[label]
        ids = []
        dungeonObjects = scenarioSvc.GetDunObjects()
        for slimItem in selectedGroup:
            if slimItem.dunObjectID in [ dungeonObject.dunObjectID for dungeonObject in dungeonObjects ]:
                ids.append(slimItem.dunObjectID)

        for node in self.sr.objgroupscrollbox.GetNodes():
            if node.panel.sr.label.text == label:
                self.sr.objgroupscrollbox.SelectNode(node)
                scenarioSvc.SetSelectionByID(ids)
                scenarioSvc.SetActiveHardGroup(label)

    def ObjSelectAll(self):
        dunObjs = sm.GetService('scenario').GetDunObjects()
        selItems = []
        for slimItem in dunObjs:
            selItems.append(slimItem.dunObjectID)

        sm.GetService('scenario').SetSelectionByID(selItems)
        if self.IsTabLoaded('RoomTab'):
            self.Refresh()

    def ObjClearSel(self):
        sm.GetService('scenario').SetSelectionByID([])
        if self.IsTabLoaded('RoomTab'):
            self.Refresh()

    def ObjInverseSel(self):
        curSel = self.sr.objscrollbox.GetSelected()
        ids = []
        for each in curSel:
            ids.append(each.id)

        dunObjs = sm.GetService('scenario').GetDunObjects()
        selItems = []
        for slimItem in dunObjs:
            if not sm.GetService('scenario').IsSelectedByObjID(slimItem.dunObjectID):
                selItems.append(slimItem.dunObjectID)

        sm.GetService('scenario').SetSelectionByID(selItems)
        if self.IsTabLoaded('RoomTab'):
            self.Refresh()

    def OnDESelectionChanged(self):
        if self.IsTabLoaded('RoomTab') and not self.IsSelectionUpToDate():
            self.Refresh()

    def OnDEObjectListChanged(self):
        if self.IsTabLoaded('RoomTab'):
            self.Refresh()

    def IsSelectionUpToDate(self):
        remoteSelection = copy.copy(sm.StartService('scenario').selectionObjs)
        localSelection = self.GetCurrentlySelectedObjects()
        remoteSelection.sort()
        localSelection.sort()
        return remoteSelection == localSelection

    def GetCurrentlySelectedObjects(self):
        if self.destroyed or self.sr.objscrollbox.destroyed:
            selectedEntries = []
        else:
            selectedEntries = self.sr.objscrollbox.GetSelected()
        selectedObjects = []
        for entry in selectedEntries:
            selectedObjects.append(entry.id)

        return selectedObjects

    def OnSelectObject(self, selectedList, id):
        if id == 'In Game':
            return
        selectedObj = selectedList[0]
        if hasattr(selectedObj, 'selectTypeString'):
            if getattr(selectedObj, 'selectTypeString', 'unknown') == 'SelectDungeon':
                settings.user.ui.Set('dungeonFactionID', None)
                settings.user.ui.Set('dungeonArchetypeID', None)
                settings.user.ui.Set('dungeonDungeon', selectedObj.dungeonID)
                self.sr.maintabs.ReloadVisible()
            elif getattr(selectedObj, 'selectTypeString', 'unknown') == 'SelectDungeonRoom':
                if self.IsTabLoaded('DungeonTab'):
                    settings.user.ui.Set('selectedRoomID', selectedObj.roomID)
            elif getattr(selectedObj, 'selectTypeString', 'unknown') == 'SelectDungeonObject':
                sm.GetService('scenario').SetSelectionByID([selectedObj.objectID])
                if self.IsTabLoaded('RoomTab'):
                    objectList = self.sr.objscrollbox.GetNodes()
                    for objectEntry in objectList:
                        if objectEntry.id == selectedObj.objectID:
                            self.sr.objscrollbox.SetSelected(objectEntry.idx)
                            break

            elif getattr(selectedObj, 'selectTypeString', 'unknown') == 'SelectDungeonEntity':
                pass
            elif getattr(selectedObj, 'selectTypeString', 'unknown') == 'SelectDungeonEntityGroup':
                pass
            elif selectedObj:
                import log
                log.LogWarn('dungeoneditor::OnSelectObject: Unknown selection:', selectedObj.selectTypeString)

    def Load_AlignTab(self):
        Container(name='push', parent=self.sr.panel, align=uiconst.TOTOP, height=4)
        eveLabel.EveLabelMedium(text='Align: ', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        Button(parent=row, label='  Align centres  ', func=self.OnAlignCentres, args=('btn1',), align=uiconst.TOLEFT)
        for each in 'XYZ':
            checkbox1ID = 'alignCentre%s' % each
            checkbox1Setval = settings.user.ui.Get(checkbox1ID, 0)
            cb = Checkbox(text=each, parent=row, settingsKey=checkbox1ID, checked=checkbox1Setval, callback=self.OnCheckboxChange, align=uiconst.TOLEFT, pos=(0, 0, 28, 0))

        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        Button(parent=row, label='Distribute centres', func=self.OnDistributeCentres, args=('btn1',), align=uiconst.TOLEFT)
        for each in 'XYZ':
            checkbox1ID = 'distributeCentre%s' % each
            checkbox1Setval = settings.user.ui.Get(checkbox1ID, 0)
            cb = Checkbox(text=each, parent=row, settingsKey=checkbox1ID, checked=checkbox1Setval, callback=self.OnCheckboxChange, align=uiconst.TOLEFT, pos=(0, 0, 28, 0))

        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        eveLabel.EveLabelMedium(text='Jitter: ', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        for counter, each in enumerate('XYZ'):
            checkbox1ID = 'jitterOffset%s' % each
            curVal = 0
            ed = SingleLineEditInteger(name='jitterOffset%s' % each, parent=row, setvalue=curVal, pos=(60 + counter * 52,
             0,
             38,
             0), maxValue=30000)
            setattr(self, checkbox1ID, ed)

        eveLabel.EveLabelMedium(text='Offset: ', parent=row, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL).name = 'Pos Text'
        Button(parent=row, label='Jitter Position', func=self.OnJitterClicked, args=('btn1',), pos=(220, 0, 0, 0))
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        for counter, each in enumerate(('Yaw', 'Pitch', 'Roll')):
            checkbox1ID = 'jitterOffset%s' % each
            curVal = 0
            ed = SingleLineEditInteger(name='jitterOffset%s' % each, parent=row, setvalue=curVal, pos=(60 + counter * 52,
             0,
             38,
             0), maxValue=30000)
            setattr(self, checkbox1ID, ed)

        eveLabel.EveLabelMedium(text='Rotation: ', parent=row, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL).name = 'Rot Text'
        Button(parent=row, label='Jitter Rotation', func=self.OnJitterRotationClicked, pos=(220, 0, 0, 0))
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        eveLabel.EveLabelMedium(text='Arrange: ', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        counter = 0
        Button(parent=row, label='Arrange', func=self.OnArrangeClicked, args=('btn1',), pos=(220, 0, 0, 0))
        for each in 'XYZ':
            checkbox1ID = 'arrangeOffset%s' % each
            curVal = 0
            eveLabel.EveLabelMedium(text=each, parent=row, left=50 + counter * 52, state=uiconst.UI_NORMAL)
            ed = SingleLineEditInteger(name='arrangeOffset%s' % each, parent=row, setvalue=curVal, pos=(60 + counter * 52,
             0,
             38,
             0), minValue=-30000, maxValue=30000)
            counter = counter + 1
            setattr(self, checkbox1ID, ed)

        eveLabel.EveLabelMedium(text='Offset: ', parent=row, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        eveLabel.EveLabelMedium(text='Quantity: (Only works on asteroids and clouds)', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        counter = 0
        Button(parent=row, label='Set Quantity', func=self.OnSetQuantityClicked, args=('btn1',), pos=(220, 0, 0, 0))
        minMaxQuantity = self.GetSelectedObjectsMinMaxQuantity()
        minQuantity = minMaxQuantity[0]
        maxQuantity = minMaxQuantity[1]
        eveLabel.EveLabelMedium(text='Min.', parent=row, left=40, width=32, height=14, state=uiconst.UI_NORMAL)
        eveLabel.EveLabelMedium(text='Max.', parent=row, left=130, width=32, height=14, state=uiconst.UI_NORMAL)
        self.quantityMin = SingleLineEditInteger(name='quantityMin', parent=row, setvalue=int(minQuantity), pos=(60, 0, 64, 0))
        self.quantityMax = SingleLineEditInteger(name='quantityMax', parent=row, setvalue=int(maxQuantity), pos=(154, 0, 64, 0))
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        eveLabel.EveLabelMedium(text='Radius: (Only works on asteroids and clouds)', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        counter = 0
        Button(parent=row, label='Set Radius', func=self.OnSetRadiusClicked, args=('btn1',), pos=(220, 0, 0, 0))
        eveLabel.EveLabelMedium(text='Min.', parent=row, left=40, width=32, height=14, state=uiconst.UI_NORMAL)
        eveLabel.EveLabelMedium(text='Max.', parent=row, left=130, width=32, height=14, state=uiconst.UI_NORMAL)
        minMaxRadius = self.GetSelectedObjectsMinMaxRadius()
        minRadius = minMaxRadius[0]
        maxRadius = minMaxRadius[1]
        self.radiusMin = SingleLineEditInteger(name='radiusMin', parent=row, setvalue=int(minRadius), pos=(60, 0, 64, 0))
        self.radiusMax = SingleLineEditInteger(name='radiusMax', parent=row, setvalue=int(maxRadius), pos=(154, 0, 64, 0))
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        eveLabel.EveLabelMedium(text='Rotate objects: ', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        counter = 0
        Button(parent=row, label='Rotate ', func=self.OnRotateClicked, args=('btn1',), pos=(220, 0, 0, 0))
        for each in ['Y', 'P', 'R']:
            checkbox1ID = 'rotate_%s' % each
            curVal = 0
            eveLabel.EveLabelMedium(text=each, parent=row, left=50 + counter * 52, height=14, state=uiconst.UI_NORMAL)
            ed = SingleLineEditInteger(name='rotate_%s' % each, parent=row, setvalue=curVal, pos=(60 + counter * 52,
             0,
             38,
             0), minValue=-30000, maxValue=30000)
            counter = counter + 1
            setattr(self, checkbox1ID, ed)

        eveLabel.EveLabelMedium(text='ROTATION: ', parent=row, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        eveLabel.EveLabelMedium(text='Set rotation: ', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        counter = 0
        Button(parent=row, label='Set rotation', func=self.OnSetRotateClicked, args=('btn1',), pos=(220, 0, 0, 0))
        for each in ['Y', 'P', 'R']:
            checkbox1ID = 'rotateset_%s' % each
            curVal = 0
            eveLabel.EveLabelMedium(text=each, parent=row, left=50 + counter * 52, height=14, state=uiconst.UI_NORMAL)
            ed = SingleLineEditInteger(name='rotateset_%s' % each, parent=row, setvalue=curVal, pos=(60 + counter * 52,
             0,
             38,
             0), minValue=-30000, maxValue=30000)
            counter = counter + 1
            setattr(self, checkbox1ID, ed)

        eveLabel.EveLabelMedium(text='ROTATION: ', parent=row, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)

    def GetSelectedObjectsMinMaxQuantity(self):
        minQuantity = 1
        maxQuantity = 1
        selObjs = sm.GetService('scenario').GetSelObjects()
        for slimItem in selObjs:
            if slimItem.dunRadius is not None:
                if slimItem.dunRadius > 1:
                    if minQuantity == 1:
                        minQuantity = slimItem.dunRadius
                    else:
                        minQuantity = min(minQuantity, slimItem.dunRadius)
                    maxQuantity = max(maxQuantity, slimItem.dunRadius)

        return (minQuantity, maxQuantity)

    def Close(self, *args, **kwds):
        Window.Close(self, *args, **kwds)
        self._navigation.RemoveAxisLines()

    def GetSelectedObjectsMinMaxRadius(self):
        minRadius = 1
        maxRadius = 1
        selObjs = sm.GetService('scenario').GetSelObjects()
        godma = sm.GetService('godma')
        for slimItem in selObjs:
            if slimItem.dunRadius is not None:
                if slimItem.dunRadius > 1:
                    if minRadius == 1:
                        minRadius = ComputeRadiusFromQuantity(slimItem.categoryID, slimItem.groupID, slimItem.typeID, slimItem.dunRadius, godma)
                    else:
                        minRadius = min(minRadius, ComputeRadiusFromQuantity(slimItem.categoryID, slimItem.groupID, slimItem.typeID, slimItem.dunRadius, godma))
                    maxRadius = max(maxRadius, ComputeRadiusFromQuantity(slimItem.categoryID, slimItem.groupID, slimItem.typeID, slimItem.dunRadius, godma))

        return (minRadius, maxRadius)

    def OnSetQuantityClicked(self, *args):
        minQuantity = self.quantityMin.GetValue()
        maxQuantity = self.quantityMax.GetValue()
        if maxQuantity < minQuantity:
            eve.Message('MinRadiusHigherThenMax')
            return
        sm.GetService('scenario').SetSelectedQuantity(minQuantity, maxQuantity)
        newMinMaxRadius = self.GetSelectedObjectsMinMaxRadius()
        newMinRadius = int(round(newMinMaxRadius[0]))
        newMaxRadius = int(round(newMinMaxRadius[1]))
        self.radiusMin.SetValue(newMinRadius)
        self.radiusMax.SetValue(newMaxRadius)

    def OnSetRadiusClicked(self, *args):
        minRadius = self.radiusMin.GetValue()
        maxRadius = self.radiusMax.GetValue()
        if maxRadius < minRadius:
            eve.Message('MinRadiusHigherThenMax')
            return
        sm.GetService('scenario').SetSelectedRadius(minRadius, maxRadius)
        newMinMaxQuantity = self.GetSelectedObjectsMinMaxQuantity()
        newMinQuantity = int(round(newMinMaxQuantity[0]))
        newMaxQuantity = int(round(newMinMaxQuantity[1]))
        self.quantityMin.SetValue(newMinQuantity)
        self.quantityMax.SetValue(newMaxQuantity)

    def OnSetRotateClicked(self, *args):
        y = getattr(self, 'rotateset_Y').GetValue()
        p = getattr(self, 'rotateset_P').GetValue()
        r = getattr(self, 'rotateset_R').GetValue()
        sm.GetService('scenario').SetRotate(y, p, r)

    def OnRotateClicked(self, *args):
        slimItems = sm.GetService('scenario').GetSelObjects()
        if len(slimItems) == 0:
            return
        yaw = getattr(self, 'rotate_Y').GetValue()
        pitch = getattr(self, 'rotate_P').GetValue()
        roll = getattr(self, 'rotate_R').GetValue()
        sm.GetService('scenario').RotateSelected(yaw, pitch, roll)

    def OnJitterClicked(self, *args):
        X = getattr(self, 'jitterOffsetX').GetValue()
        Y = getattr(self, 'jitterOffsetY').GetValue()
        Z = getattr(self, 'jitterOffsetZ').GetValue()
        sm.GetService('scenario').JitterSelection(X, Y, Z)

    def OnJitterRotationClicked(self, *args):
        yaw = self.jitterOffsetYaw.GetValue()
        pitch = self.jitterOffsetPitch.GetValue()
        roll = self.jitterOffsetRoll.GetValue()
        sm.StartService('scenario').JitterRotationSelection(yaw, pitch, roll)

    def OnArrangeClicked(self, *args):
        X = getattr(self, 'arrangeOffsetX').GetValue()
        Y = getattr(self, 'arrangeOffsetY').GetValue()
        Z = getattr(self, 'arrangeOffsetZ').GetValue()
        sm.GetService('scenario').ArrangeSelection(X, Y, Z)

    def OnDungeonSelectionGroupRotation(self, groupName, x, y, z, w):
        pass

    def OnRenameGroup(self):
        selectedGroups = self.sr.objgroupscrollbox.GetSelected()
        for each in selectedGroups:
            self.OpenRenameGroupDialog(each.label)
            return

    def OpenRenameGroupDialog(self, key = ''):
        oldGroupName = key
        format = [{'type': 'btline'},
         {'type': 'push',
          'height': 8,
          'frame': 1},
         {'type': 'edit',
          'setvalue': key,
          'maxLength': 64,
          'labelwidth': len('Group Name:') * 7,
          'label': 'Group Name:',
          'key': 'newGroupName',
          'required': 1,
          'frame': 1},
         {'type': 'push',
          'height': 8,
          'frame': 1},
         {'type': 'btline'},
         {'type': 'data',
          'data': {'oldGroupName': oldGroupName}},
         {'type': 'errorcheck',
          'errorcheck': self.RenameGroupErrorCheck}]
        retval = uix.HybridWnd(format, caption='Rename Group', windowID='renameGroup', modal=1, buttons=uiconst.OKCANCEL, minW=300, minH=50)
        if retval and retval['newGroupName'] and len(retval['newGroupName']) > 1:
            self.RenameGroup(retval['oldGroupName'], retval['newGroupName'])

    def RenameGroupErrorCheck(self, retval):
        oldGroupName = retval['oldGroupName']
        newGroupName = retval['newGroupName']
        if oldGroupName == newGroupName:
            return ''
        if newGroupName in self.objectGroups:
            return 'Cannot rename %s: A group with the name you specified already exists. Specify a new group name.' % oldGroupName

    def RenameGroup(self, oldGroupName, newGroupName):
        if oldGroupName == newGroupName:
            return
        sm.GetService('scenario').RenameHardGroup(oldGroupName, newGroupName)
        self.objectGroups[newGroupName] = self.objectGroups[oldGroupName]
        del self.objectGroups[oldGroupName]
        self.Refresh()

    def OnRemoveGroup(self):
        self.RemoveSelectedGroups()

    def _RemoveGroup(self, groupName):
        del self.objectGroups[groupName]
        self.scenario.RemoveHardGroup(groupName)

    def RemoveGroup(self, groupName):
        self._RemoveGroup(groupName)
        self.Refresh()

    def RemoveSelectedGroups(self):
        selectedGroups = self.GetSelectedGroups()
        for groupName in selectedGroups:
            self._RemoveGroup(groupName)

        self.Refresh()

    def OnDeleteSelected(self):
        uthread.new(self.DeleteSelected).context = 'svc.scenario.OnDeleteSelected'

    def OnDeleteSelectedGroup(self):
        uthread.new(self.DeleteSelectedGroups).context = 'svc.scenario.OnDeleteSelectedGroup'

    def DeleteSelected(self):
        self.RemoveSelectedGroups()

    def DeleteGroup(self, groupName):
        self.RemoveGroup(groupName)

    def DeleteSelectedGroups(self):
        selectedGroups = self.GetSelectedGroups()
        for groupName in selectedGroups:
            self._RemoveGroup(groupName)

        self.Refresh()

    def OnAlignCentres(self, *args):
        selObjs = sm.GetService('scenario').GetSelObjects()
        if len(selObjs) == 0:
            return
        centreAxis = trinity.TriVector()
        for slimItem in selObjs:
            centreAxis.x = centreAxis.x + slimItem.dunX
            centreAxis.y = centreAxis.y + slimItem.dunY
            centreAxis.z = centreAxis.z + slimItem.dunZ

        centreAxis.Scale(1.0 / len(selObjs))
        for slimItem in selObjs:
            newX = slimItem.dunX
            newY = slimItem.dunY
            newZ = slimItem.dunZ
            if settings.user.ui.Get('alignCentreX', 0):
                newX = int(centreAxis.x)
            if settings.user.ui.Get('alignCentreY', 0):
                newY = int(centreAxis.y)
            if settings.user.ui.Get('alignCentreZ', 0):
                newZ = int(centreAxis.z)
            dungeonHelper.SetObjectPosition(slimItem.dunObjectID, newX, newY, newZ)

    def OnDistributeCentres(self, *args):
        selObjs = sm.GetService('scenario').GetSelObjects()
        if len(selObjs) < 2:
            return
        centreAxis = trinity.TriVector()
        minV = trinity.TriVector(selObjs[0].dunX, selObjs[0].dunY, selObjs[0].dunZ)
        maxV = minV.CopyTo()
        for slimItem in selObjs:
            minV.x = min(minV.x, slimItem.dunX)
            minV.y = min(minV.y, slimItem.dunY)
            minV.z = min(minV.z, slimItem.dunZ)
            maxV.x = max(maxV.x, slimItem.dunX)
            maxV.y = max(maxV.y, slimItem.dunY)
            maxV.z = max(maxV.z, slimItem.dunZ)

        dMinMaxV = maxV - minV
        dStepSize = dMinMaxV.CopyTo()
        dStepSize.Scale(1.0 / (len(selObjs) - 1))
        if len(selObjs) == 0:
            return
        counter = 0
        for slimItem in selObjs:
            newX = slimItem.dunX
            newY = slimItem.dunY
            newZ = slimItem.dunZ
            if settings.user.ui.Get('distributeCentreX', 0):
                newX = minV.x + dStepSize.x * counter
            if settings.user.ui.Get('distributeCentreY', 0):
                newY = minV.y + dStepSize.y * counter
            if settings.user.ui.Get('distributeCentreZ', 0):
                newZ = minV.z + dStepSize.z * counter
            dungeonHelper.SetObjectPosition(slimItem.dunObjectID, newX, newY, newZ)
            counter = counter + 1

    def Load_SettingTab(self):
        eveLabel.EveLabelMedium(text='Cursor size clamping', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=16)
        counter = 0
        Button(parent=row, label='Set min and max', func=self.OnSetCursorRadiusClicked, args=('btn1',), pos=(220, 0, 0, 0))
        minRadius = settings.user.ui.Get('cursorMin', 1.0)
        maxRadius = settings.user.ui.Get('cursorMax', 100000.0)
        selObjs = sm.GetService('scenario').GetSelObjects()
        for slimItem in selObjs:
            if slimItem.radius > 1:
                if minRadius == 1:
                    minRadius = slimItem.radius
                else:
                    minRadius = min(minRadius, slimItem.radius)
                maxRadius = max(maxRadius, slimItem.radius)

        eveLabel.EveLabelMedium(text='Min.', parent=row, left=40, width=32, state=uiconst.UI_NORMAL)
        eveLabel.EveLabelMedium(text='Max.', parent=row, left=130, width=32, state=uiconst.UI_NORMAL)
        self.cursorMin = SingleLineEditInteger(name='cursorMin', parent=row, setvalue=int(minRadius), pos=(60, 0, 64, 0), maxValue=60000)
        self.cursorMax = SingleLineEditInteger(name='cursorMax', parent=row, setvalue=int(maxRadius), pos=(154, 0, 64, 0), maxValue=60000)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        Container(name='pusher', align=uiconst.TOTOP, height=6, parent=self.sr.panel)
        eveLabel.EveLabelMedium(text='Aggression radius: ', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        checkbox1ID = 'showAggrRadius'
        checkbox1Setval = settings.user.ui.Get(checkbox1ID, 0)
        self.aggrSettings = Checkbox(text='Aggression radius', parent=self.sr.panel, settingsKey=checkbox1ID, checked=settings.user.ui.Get('showAggrRadius', 0), callback=self.OnDisplaySettingsChange)
        self.aggrSettingsAll = Checkbox(text='Show agression radius of all objects', parent=self.sr.panel, settingsKey=checkbox1ID, checked=settings.user.ui.Get('aggrSettingsAll', 0), callback=self.OnDisplaySettingsChange)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        self.gridCheckbox = Checkbox(text='Draw Grid Lines', parent=self.sr.panel, settingsKey=checkbox1ID, checked=self._navigation.IsGridEnabled(), callback=self.OnDisplaySettingsChange)
        Container(name='pusher', align=uiconst.TOTOP, height=7, parent=self.sr.panel)
        eveLabel.EveLabelMedium(text='Palette Placement Grid', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        gridSizeOptions = [('200x200m', 200.0),
         ('2x2km', 2000.0),
         ('20x20km', 20000.0),
         ('200x200km', 200000.0),
         ('2000x2000km', 2000000.0)]
        Container(name='pusher', align=uiconst.TOTOP, height=14, parent=self.sr.panel)
        self.gridSizeDropdown = Combo(parent=self.sr.panel, label='Grid Size', options=gridSizeOptions, name='', select=self._navigation.GetGridLength(), callback=self.OnDisplaySettingsChange, align=uiconst.TOTOP, adjustWidth=True)
        gridSpacingOptions = [('10x10m', 10.0),
         ('100x100m', 100.0),
         ('1x1km', 1000.0),
         ('10x10km', 10000.0)]
        Container(name='pusher', align=uiconst.TOTOP, height=14, parent=self.sr.panel)
        self.gridSpacingDropdown = Combo(parent=self.sr.panel, label='Unit Size', options=gridSpacingOptions, name='', select=self._navigation.GetGridSpacing(), callback=self.OnDisplaySettingsChange, align=uiconst.TOTOP, adjustWidth=True)
        Container(name='pusher', align=uiconst.TOTOP, height=14, parent=self.sr.panel)
        eveLabel.EveLabelMedium(text='Free Look Camera must be enabled to use the placement grid.', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        eveLabel.EveLabelMedium(text='Red Axis Line = X Axis', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        eveLabel.EveLabelMedium(text='Green Axis Line = Y Axis', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        eveLabel.EveLabelMedium(text='Blue Axis Line = Z Axis', parent=self.sr.panel, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)

    def OnDisplaySettingsChange(self, *args):
        desiredSpacingValue = self.gridSpacingDropdown.GetValue()
        settings.user.ui.Set('showAggrRadius', self.aggrSettings.GetValue())
        settings.user.ui.Set('aggrSettingsAll', self.aggrSettingsAll.GetValue())
        self.UpdateGridVisibility()
        if desiredSpacingValue != self._navigation.GetGridSpacing():
            self.gridSpacingDropdown.SetValue(self._navigation.GetGridSpacing())
        sm.GetService('scenario').RefreshSelection()

    def OnSetCursorRadiusClicked(self, *args):
        minRadius = self.cursorMin.GetValue()
        maxRadius = self.cursorMax.GetValue()
        if maxRadius < minRadius:
            eve.Message('MinRadiusHigherThenMax')
            return
        settings.user.ui.Set('cursorMin', minRadius)
        settings.user.ui.Set('cursorMax', maxRadius)
        sm.GetService('scenario').RefreshSelection()

    def GetScrollOptions(self, key):
        data = []
        if key == 'combo_retval1':
            data = [ ('1 label %s' % i, i) for i in xrange(100) ]
        elif key == 'combo_retval2':
            data = [ ('2 label %s' % i, i) for i in xrange(100) ]
        return [ GetFromClass(Generic, {'label': label,
         'id': id}) for label, id in data ]

    def OnGotoSelectedRoomClicked(self, entry, *args):
        settings.user.ui.Set('selectedRoomID', entry.sr.node.roomID)
        dungeonID = settings.user.ui.Get('dungeonDungeon', None)
        sm.ScatterEvent('OnSelectObjectInGame', 'SelectDungeonRoom', dungeonID=dungeonID, roomID=entry.sr.node.roomID)

    def OnComboChange(self, combo, newHeader, newValue, *args):
        settings.user.ui.Set(combo.name, newValue)
        self.sr.maintabs.ReloadVisible()
        if combo.name == 'dungeonDungeon':
            sm.ScatterEvent('OnSelectObjectInGame', 'SelectDungeon', dungeonID=newValue)

    def OnClickButton(self, *args):
        self.sr.maintabs.ReloadVisible()

    def OnCheckboxChange(self, checkbox, *args):
        settings.user.ui.Set(checkbox.GetSettingsKey(), checkbox.checked)

    def Load_PaletteTab(self):
        roomObjectGroups = sm.RemoteSvc('dungeon').DEGetRoomObjectPaletteData()
        kv = utillib.KeyVal()
        kv.groupItems = roomObjectGroups
        scrollOptions = self.GetGroupTypes(kv)
        self.sr.palettescroll = eveScroll.Scroll(name='scroll', parent=self.sr.panel, align=uiconst.TOALL)
        self.sr.palettescroll.Load(contentList=scrollOptions, scrolltotop=0)
        self.sr.palettescroll.padBottom = button.height + const.defaultPadding * 5
        self.sr.palettescroll.multiSelect = 0

    def GetGroupTypes(self, nodeData, *args):
        sublevel = nodeData.Get('sublevel', -1) + 1
        scrollOptions = []
        if type(nodeData.groupItems) == list:
            nodeData.groupItems.sort(lambda x, y: cmp(x[1], y[1]))
            for id, name in nodeData.groupItems:
                scrollOptions.append(GetFromClass(PaletteEntry, {'label': name,
                 'id': id,
                 'sublevel': sublevel}))

        elif type(nodeData.groupItems) == dict:
            keys = nodeData.groupItems.keys()
            keys.sort(lambda x, y: cmp(x[1], y[1]))
            for key in keys:
                groupID, groupName = key
                scrollOptions.append(GetFromClass(ListGroup, {'label': groupName,
                 'id': ('group', groupID),
                 'groupItems': nodeData.groupItems[key],
                 'showlen': 1,
                 'sublevel': sublevel,
                 'GetSubContent': self.GetGroupTypes}))

        return scrollOptions

    def OnDEObjectPaletteChanged(self):
        if self.sr.Get('palettescroll') and self.sr.palettescroll is not None:
            self.UnloadPanel()
            self.Refresh()

    def _OnClose(self, *args):
        self.scenario.ClearSelection()


class DungeonDragEntry(Generic):
    __guid__ = 'listentry.DungeonDragEntry'
    __nonpersistvars__ = []
    isDragObject = True
    DROPDISTANCE = 10000

    def GetDragData(self, *args):
        return self.sr.node.scroll.GetSelectedNodes(self.sr.node)

    def OnEndDrag(self, *args):
        uthread.new(self.OnEndDragFunc)

    def OnEndDragFunc(self):
        from eve.client.script.ui.inflight.navigation import InflightLayer
        where = uicore.uilib.mouseOver
        if where and type(where) is InflightLayer:
            scenarioSvc = sm.services['scenario']
            roomID = scenarioSvc.GetEditingRoomID()
            if roomID is None:
                ShowQuickMessage('You need to be editing a room to be able to add an object')
                return
            proj, view, vp = uix.GetFullscreenProjectionViewAndViewport()
            ray, startingPosition = trinity.device.GetPickRayFromViewport(uicore.uilib.x, uicore.uilib.y, vp, view.transform, proj.transform)
            ray = trinity.TriVector(*ray)
            roomPos = scenarioSvc.GetEditingRoomPosition()
            ship = sm.services['michelle'].GetBall(eve.session.shipid)
            camera = sm.GetService('sceneManager').GetActiveCamera()
            cameraParent = sm.GetService('sceneManager').GetActiveCamera().GetCameraParent()
            cameraPosition = trinity.TriVector(ship.x - roomPos[0] + camera.pos[0], ship.y - roomPos[1] + camera.pos[1], ship.z - roomPos[2] + camera.pos[2])
            focusPoint = cameraParent.translation
            focusPoint = trinity.TriVector(ship.x - roomPos[0] + focusPoint[0], ship.y - roomPos[1] + focusPoint[1], ship.z - roomPos[2] + focusPoint[2])
            dist = (focusPoint.y - cameraPosition.y) / ray.y
            if dist < 0:
                ShowQuickMessage('This item can only be dragged onto the grid')
                return
            posInRoom = cameraPosition + ray * dist
            gridLength = sm.GetService('sceneManager').GetActiveCamera().dungeonHack.GetGridLength()
            minGrid = -gridLength / 2.0
            maxGrid = gridLength / 2.0
            if minGrid + focusPoint.x > posInRoom.x or maxGrid + focusPoint.x < posInRoom.x or minGrid + focusPoint.z > posInRoom.z or maxGrid + focusPoint.z < posInRoom.z:
                ShowQuickMessage('You can only drag Palette entries onto the grid')
                return
            self.DropIntoDungeonRoom(roomID, posInRoom)
        elif where and where.__guid__ not in (self.__guid__, 'form.DungeonEditor'):
            ShowQuickMessage('This item can only be dragged onto the grid')

    def DropIntoDungeonRoom(self, roomID, posInRoom):
        pass


class PaletteEntry(DungeonDragEntry):
    __guid__ = 'listentry.PaletteEntry'


class DungeonObjectProperties(Window):
    __guid__ = 'form.DungeonObjectProperties'
    __nonpersistvars__ = []
    __notifyevents__ = ['OnDungeonObjectProperties', 'OnSelectObjectInGame']
    _windowHeight = 200
    default_windowID = 'dungeonObjectProperties'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.scope = uiconst.SCOPE_INFLIGHT
        self.SetCaption('Object Properties')
        self.width = 300
        self.height = self._windowHeight
        self.SetHeight(self._windowHeight)
        self.objectRow = None
        self.noObjects = eveLabel.EveLabelMedium(text='No Objects Selected', parent=self.sr.main, left=5, top=4, state=uiconst.UI_NORMAL)
        panel = Container(name='panel', parent=self.sr.main, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding)
        self.sr.panel = panel
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=18)
        eveLabel.EveLabelMedium(text='Selected:', parent=row, left=2, top=4, state=uiconst.UI_NORMAL)
        self.selectedCombo = Combo(label='', parent=row, options=(('Nothing', 0),), name='combo', select=0, callback=self.OnComboChange, pos=(80, 0, 0, 0), align=uiconst.TOPLEFT)
        self.selectedCombo.width = 202
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=20)
        eveLabel.EveLabelMedium(text='Object Name:', parent=row, left=2, top=4, state=uiconst.UI_NORMAL)
        self.objectName = SingleLineEditText(name='objectName', parent=row, setvalue='', pos=(80, 0, 202, 16))
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=20)
        eveLabel.EveLabelMedium(text='Object Type:', parent=row, left=2, top=4, state=uiconst.UI_NORMAL)
        self.objectType = eveLabel.EveLabelMedium(text='', parent=row, left=80, top=4, state=uiconst.UI_NORMAL)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=20)
        eveLabel.EveLabelMedium(text='Quantity:', parent=row, left=2, top=4, state=uiconst.UI_NORMAL)
        self.quantity = SingleLineEditInteger(name='quantity', parent=row, setvalue=0, pos=(80, 0, 202, 0))
        self.oldQuantity = 0
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=20)
        eveLabel.EveLabelMedium(text='Radius:', parent=row, left=2, top=4, state=uiconst.UI_NORMAL)
        self.radius = SingleLineEditInteger(name='radius', parent=row, setvalue=0, pos=(80, 0, 202, 16))
        self.oldRadius = 0
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=20)
        eveLabel.EveLabelMedium(text='Position:', parent=row, left=2, top=4, state=uiconst.UI_NORMAL)
        for i, each in enumerate('XYZ'):
            editId = 'position%s' % each
            editBox = SingleLineEditFloat(name=editId, parent=row, setvalue=0, pos=(80 + i * 69,
             0,
             64,
             16), minValue=-100000.0, maxValue=100000.0)
            setattr(self, editId, editBox)

        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=20)
        eveLabel.EveLabelMedium(text='Rotation:', parent=row, left=2, top=4, state=uiconst.UI_NORMAL)
        for i, each in enumerate(['Yaw', 'Pitch', 'Roll']):
            editId = 'rotation%s' % each
            editBox = SingleLineEditFloat(name=editId, parent=row, setvalue=0, pos=(80 + i * 69,
             0,
             64,
             16), minValue=-100000.0, maxValue=100000.0)
            setattr(self, editId, editBox)

        Container(name='spacer', parent=self.sr.panel, align=uiconst.TOTOP, height=5)
        Line(parent=self.sr.panel, align=uiconst.TOTOP)
        Container(name='spacer', parent=self.sr.panel, align=uiconst.TOTOP, height=5)
        row = Container(name='row', parent=self.sr.panel, align=uiconst.TOTOP, height=20)
        Button(parent=row, label='Change Type', func=self.OnChangeType, align=uiconst.TOLEFT).width = 87
        Button(parent=row, label='Save', func=self.OnSave, align=uiconst.TOLEFT).width = 87
        Button(parent=row, label='Revert', func=self.OnRevert, align=uiconst.TOLEFT).width = 87
        self.scenario = sm.StartService('scenario')
        self.OnSelectObjectInGame('SelectDungeonObject')
        self.Show()

    def LoadObjectID(self, objectID = None):
        if objectID is None:
            self.sr.panel.state = uiconst.UI_HIDDEN
            self.noObjects.state = uiconst.UI_DISABLED
            self.objectRow = None
            self.SetCaption('Object Properties')
            return
        self.ShowLoad()
        self.objectRow = None
        if self.objectRow is None:
            self.sr.panel.state = uiconst.UI_HIDDEN
            self.noObjects.state = uiconst.UI_DISABLED
            self.objectRow = None
            self.HideLoad()
            return
        self.sr.panel.state = uiconst.UI_PICKCHILDREN
        self.noObjects.state = uiconst.UI_HIDDEN
        self.SetHeight(self._windowHeight)
        self.UpdateDisplay()

    def UpdateDisplay(self):
        self.ShowLoad()
        self.SetCaption('Object Properties: %d' % self.objectRow.objectID)
        objectName = ''
        if self.objectRow.objectNameID is not None:
            objectName = GetMessageFromLocalization(self.objectRow.objectNameID)
        self.objectName.SetValue(objectName)
        self.objectType.text = evetypes.GetNameOrNone(self.objectRow.typeID) or '<No Type Set>'
        quantity = dungeonHelper.GetObjectQuantity(self.objectRow.objectID)
        if quantity is None:
            self.quantity.SetValue('Quantity Invalid For This Type')
            self.quantity.state = uiconst.UI_DISABLED
        else:
            self.quantity.state = uiconst.UI_NORMAL
            self.quantity.SetValue(int(quantity))
            self.oldQuantity = int(quantity)
        radius = dungeonHelper.GetObjectRadius(self.objectRow.objectID)
        if radius is None:
            self.radius.SetValue('Radius Invalid For This Type')
            self.radius.state = uiconst.UI_DISABLED
        else:
            self.radius.state = uiconst.UI_NORMAL
            self.radius.SetValue(int(radius))
            self.oldRadius = int(radius)
        x, y, z = dungeonHelper.GetObjectPosition(self.objectRow.objectID)
        self.positionX.SetValue(x)
        self.positionY.SetValue(y)
        self.positionZ.SetValue(z)
        yaw, pitch, roll = dungeonHelper.GetObjectRotation(self.objectRow.objectID)
        self.rotationYaw.SetValue(yaw)
        self.rotationPitch.SetValue(pitch)
        self.rotationRoll.SetValue(roll)
        self.HideLoad()

    def OnSelectObjectInGame(self, selectType, *args, **kwargs):
        if selectType == 'SelectDungeonObject':
            self._HandleSelection(self.scenario.GetSelectedObjIDs())

    def _HandleSelection(self, objectIds):
        if objectIds:
            scenarioSvc = sm.StartService('scenario')
            for objectID in objectIds:
                ball, slimItem = scenarioSvc.GetBallAndSlimItemFromObjectID(objectID)
                sleepTime = 0
                while ball is None or slimItem is None and sleepTime < 5000:
                    sleepTime += 200
                    blue.synchro.SleepWallclock(200)
                    ball, slimItem = scenarioSvc.GetBallAndSlimItemFromObjectID(objectID)

                if ball is None or slimItem is None:
                    sm.StartService('scenario').LogError('DungeonObjectProperties._HandleSelection could not load balls and slimItems')

            if self.objectRow is None or self.objectRow.objectID not in objectIds:
                self.LoadObjectID(objectIds[0])
            options = []
            for objectId in objectIds:
                options.append((objectId, objectId))

            self.selectedCombo.LoadOptions(options, select=self.objectRow.objectID)
        else:
            self.LoadObjectID()

    def OnDungeonObjectProperties(self, objectID):
        if self.objectRow and objectID == self.objectRow.objectID:
            self.UpdateDisplay()

    def OnChangeType(self, *args, **kwargs):
        ObjectTypeChooser.Open(objectRow=self.objectRow)

    def OnSave(self, *args, **kwargs):
        dungeonID = settings.user.ui.Get('dungeonDungeon', None)
        if dungeonID is None or dungeonID == 'All':
            return
        selDungeon = sm.RemoteSvc('dungeon').DEGetDungeons(dungeonID=dungeonID)[0]
        dungeonNameID = selDungeon.dungeonNameID
        if dungeonNameID is not None:
            dungeonName = GetMessageFromLocalization(dungeonNameID)
        else:
            dungeonName = selDungeon.dungeonName
        quantity = self.quantity.GetValue()
        if quantity != 'Quantity Invalid For This Type' and quantity != self.oldQuantity:
            self.oldQuantity = quantity
            dungeonHelper.SetObjectQuantity(self.objectRow.objectID, quantity)
        radius = self.radius.GetValue()
        if radius != 'Radius Invalid For This Type' and radius != self.oldRadius:
            self.oldRadius = radius
            dungeonHelper.SetObjectRadius(self.objectRow.objectID, radius)
        x = self.positionX.GetValue()
        y = self.positionY.GetValue()
        z = self.positionZ.GetValue()
        dungeonHelper.SetObjectPosition(self.objectRow.objectID, x, y, z)
        yaw = self.rotationYaw.GetValue()
        pitch = self.rotationPitch.GetValue()
        roll = self.rotationRoll.GetValue()
        dungeonHelper.SetObjectRotation(self.objectRow.objectID, yaw, pitch, roll)
        objectName = self.objectName.GetValue()
        if not objectName:
            objectName = None
        if objectName is not None:
            objectNameID = self.objectRow.objectNameID
            if objectNameID is not None and objectName == GetMessageFromLocalization(objectNameID):
                return
            if objectNameID is not None and unicode(objectNameID) in objectName:
                msgText = 'Do you really want to name this object %s?'
                msgText += " Selecting 'No' will save other changes you have made to the object, but will not change the name."
                ret = eve.Message('CustomQuestion', {'header': 'Rename Object?',
                 'question': msgText % objectName}, uiconst.YESNO)
                if ret == uiconst.ID_NO:
                    return
        self.UpdateDisplay()

    def OnRevert(self, *args, **kwargs):
        self.UpdateDisplay()

    def OnComboChange(self, *args, **kwargs):
        selected = self.selectedCombo.GetValue()
        if selected != self.objectRow.objectID:
            self.LoadObjectID(selected)


class ObjectTypeChooser(Window):

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        objectRow = attributes.objectRow
        self.scope = uiconst.SCOPE_INFLIGHT
        self.SetCaption('Object Type Chooser - %d' % objectRow.objectID)
        self.SetMinSize([350, 400])
        self.objectRow = objectRow
        panel = Container(name='panel', parent=self.sr.main, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=const.defaultPadding)
        self.sr.panel = panel
        roomObjectGroups = sm.RemoteSvc('dungeon').DEGetRoomObjectPaletteData()
        kv = utillib.KeyVal()
        kv.groupItems = roomObjectGroups
        scrollOptions = self.GetGroupTypes(kv)
        self.sr.palettescroll = eveScroll.Scroll(name='scroll', parent=self.sr.panel, align=uiconst.TOALL)
        self.sr.palettescroll.Load(contentList=scrollOptions, scrolltotop=0)
        button = Button(parent=self.sr.panel, label='Change Type', func=self.OnChangeType, align=uiconst.TOBOTTOM)
        self.sr.palettescroll.padBottom = const.defaultPadding * 7
        self.sr.palettescroll.multiSelect = 0
        self.Show()

    def OnChangeType(self, *args, **kwargs):
        curSel = self.sr.palettescroll.GetSelected()
        if curSel:
            id = curSel[0].id
            name = curSel[0].label
        else:
            ShowQuickMessage('You need to select an object type from the chooser before you can change the object type')
            return
        self.objectRow.typeID = id

    def GetGroupTypes(self, nodeData, *args):
        sublevel = nodeData.Get('sublevel', -1) + 1
        scrollOptions = []
        if type(nodeData.groupItems) == list:
            nodeData.groupItems.sort(lambda x, y: cmp(x[1], y[1]))
            for id, name in nodeData.groupItems:
                scrollOptions.append(GetFromClass(PaletteEntry, {'label': name,
                 'id': id,
                 'sublevel': sublevel}))

        elif type(nodeData.groupItems) == dict:
            keys = nodeData.groupItems.keys()
            keys.sort(lambda x, y: cmp(x[1], y[1]))
            for key in keys:
                groupID, groupName = key
                scrollOptions.append(GetFromClass(ListGroup, {'label': groupName,
                 'id': ('group', groupID),
                 'groupItems': nodeData.groupItems[key],
                 'showlen': 1,
                 'sublevel': sublevel,
                 'GetSubContent': self.GetGroupTypes}))

        return scrollOptions


class ObjectGroupListEntry(Generic):
    __guid__ = 'listentry.ObjectGroupListEntry'
    __nonpersistvars__ = []

    def Startup(self, *args):
        Generic.Startup(self, args)
        self.sr.lock = eveIcon.Icon(icon='ui_22_32_30', parent=self, size=24, align=uiconst.CENTERRIGHT, state=uiconst.UI_HIDDEN, hint='You can not change this shortcut')

    def Load(self, node):
        Generic.Load(self, node)
        self.sr.form = node.form
        self.sr.isLocked = node.locked
        self.sr.lock.state = [uiconst.UI_HIDDEN, uiconst.UI_NORMAL][node.locked]

    def GetMenu(self):
        if self.sr.isLocked:
            return []
        m = [('Rename Group', self.RenameGroup), ('Remove Group', self.RemoveGroup), ('Delete Group Objects', self.DeleteGroupObjects)]
        return m

    def OnDblClick(self, *args):
        if not self.sr.isLocked:
            self.RenameGroup()

    def RenameGroup(self):
        self.Deselect()
        self.sr.form.OpenRenameGroupDialog(key=self.sr.label.text)

    def RemoveGroup(self):
        self.Deselect()
        self.sr.form.RemoveGroup(self.sr.label.text)

    def DeleteGroupObjects(self):
        self.Deselect()
        uthread.new(self.sr.form.DeleteGroup, self.sr.label.text).context = 'svc.scenario.OnDeleteSelected'

    def RefreshCallback(self, *args):
        if self.sr.node.Get('refreshcallback', None):
            self.sr.node.refreshcallback()
