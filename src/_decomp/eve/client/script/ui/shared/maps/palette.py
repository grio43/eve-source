#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\maps\palette.py
import types
import evetypes
import localization
import log
import trinity
import uthread
from carbonui import uiconst
from carbonui.control.radioButton import RadioButton
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.checkbox import CheckboxEntry
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.listgroup import ListGroup
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.shared.maps import mapcommon, maputils
from eve.client.script.ui.shared.maps.entries import LegendEntry, LocationSearchItem
from eve.common.lib import appConst as const
from eveexceptions import UserError
ROUTECOL = {'White': trinity.TriColor(1.0, 1.0, 1.0, 0.5),
 'Red': trinity.TriColor(1.0, 0.0, 0.0, 0.5),
 'Green': trinity.TriColor(0.0, 1.0, 0.0, 0.5),
 'Blue': trinity.TriColor(0.0, 0.0, 1.0, 0.5),
 'Yellow': trinity.TriColor(1.0, 1.0, 0.0, 0.5)}
ILLEGALITY_AVOID_NONE = 0
ILLEGALITY_AVOID_STANDING_LOSS = 1
ILLEGALITY_AVOID_CONFISCATE = 2
ILLEGALITY_AVOID_ATTACK = 3

class MapPalette(Window):
    __guid__ = 'form.MapsPalette'
    default_analyticID = 'OldMap'
    __notifyevents__ = ['OnMapModeChangeDone', 'OnLoadWMCPSettings', 'OnFlattenModeChanged']
    default_top = '__center__'
    default_width = 400
    default_height = 320
    default_windowID = 'mapspalette'
    default_iconNum = 'res:/ui/Texture/WindowIcons/map.png'
    default_isOverlayed = True

    @staticmethod
    def default_left(*args):
        leftpush, rightpush = Window.GetSideOffset()
        return uicore.desktop.width - rightpush - MapPalette.default_width - 80

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self._cfgTopHeaderTmpl = None
        self._cfgTopDivTmpl = None
        self._cfgTopPushTmpl = None
        self._cfgCheckBoxTmpl = None
        self._cfgBottomHeaderTmpl = None
        self._cfgButtonTmpl = None
        self.starColorGroups = []
        self.starColorByID = None
        self.scope = uiconst.SCOPE_INGAME
        self.SetMinSize([400, 200])
        self.SetCaption(localization.GetByLabel('UI/Map/MapPallet/CaptionMapPallet'))
        self.MakeUnKillable()
        self.loadedTab = None
        if self.destroyed:
            return
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=36, clipChildren=True)
        self.sr.scroll = eveScroll.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.sr.id = 'mapspalletescroll_withsort'
        self.sr.scroll2 = eveScroll.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll2.sr.id = 'mapspalletescroll_withhoutsort'
        self.sr.scroll2.OnSelectionChange = self.OnSelectionChange
        flattened = settings.user.ui.Get('mapFlattened', 1)
        toggleFlatLabel = localization.GetByLabel('UI/Map/MapPallet/btnFlattenMap')
        if flattened:
            toggleFlatLabel = localization.GetByLabel('UI/Map/MapPallet/btnUnflattenMap')
        if sm.GetService('viewState').IsViewActive('starmap'):
            toggleMapLabel = localization.GetByLabel('UI/Map/MapPallet/btnSolarsystemMap')
        else:
            toggleMapLabel = localization.GetByLabel('UI/Map/MapPallet/btnStarMap')
        self.sr.flattenBtns = ButtonGroup(parent=self.topParent, align=uiconst.CENTER, button_size_mode=ButtonSizeMode.DYNAMIC, buttons=[Button(label=localization.GetByLabel('UI/Map/MapPallet/btnCloseMap'), func=sm.GetService('viewState').CloseSecondaryView, args=(), fixedwidth=92), Button(label=toggleMapLabel, func=self.ToggleMapMode, args=(), fixedwidth=136), Button(label=toggleFlatLabel, func=self.ClickToggleFlatten, args='self', fixedwidth=92)], idx=0)
        searchpar = ContainerAutoSize(name='searchpar', parent=self.sr.main, align=uiconst.TOTOP, idx=self.topParent.GetOrder() + 1)
        searchpar.OnTabSelect = self.GiveInputFocus
        inpt = SingleLineEditText(name='', label=localization.GetByLabel('UI/Map/MapPallet/lblSearchForLocation'), parent=searchpar, pos=(5, 22, 98, 0), maxLength=64)
        inpt.OnReturn = self.OnReturnSearch
        self.sr.searchinput = inpt
        Button(parent=inpt.parent, label=localization.GetByLabel('UI/Map/MapPallet/btnSearchForLocation'), func=self.Search, args=1, pos=(inpt.left + inpt.width + 4,
         inpt.top,
         0,
         0), btn_default=1)
        starviewstabs = TabGroup(name='tabparent', parent=self.sr.main, idx=searchpar.GetOrder() + 1)
        starviewstabs.Startup([[localization.GetByLabel('UI/Map/MapPallet/tabStars'),
          self.sr.scroll2,
          self,
          'starview_color'],
         [localization.GetByLabel('UI/Map/MapPallet/tabLabels'),
          self.sr.scroll2,
          self,
          'mapsettings_labels'],
         [localization.GetByLabel('UI/Map/MapPallet/tabMapLines'),
          self.sr.scroll2,
          self,
          'mapsettings_lines'],
         [localization.GetByLabel('UI/Map/MapPallet/tabTiles'),
          self.sr.scroll2,
          self,
          'mapsettings_tiles'],
         [localization.GetByLabel('UI/Map/MapPallet/tabLegend'),
          self.sr.scroll2,
          self,
          'mapsettings_legend'],
         [localization.GetByLabel('UI/Map/MapPallet/tabMapAnimation'),
          self.sr.scroll2,
          self,
          'mapsettings_other']], 'starviewssub', autoselecttab=0)
        self.sr.starviewstabs = starviewstabs
        self.sr.maintabs = TabGroup(name='tabparent', parent=self.sr.main, idx=self.topParent.GetOrder() + 1)
        self.sr.maintabs.Startup([[localization.GetByLabel('UI/Map/MapPallet/tabSearch'),
          self.sr.scroll,
          self,
          'mapsearchpanel',
          searchpar], [localization.GetByLabel('UI/Map/MapPallet/tabStarMap'),
          self.sr.scroll2,
          self,
          'mapsettings',
          starviewstabs], [localization.GetByLabel('UI/Map/MapPallet/tabSolarSystemMap'),
          self.sr.scroll2,
          self,
          'mapsettings_solarsystem',
          None]], 'mapspalette', autoselecttab=1)

    def GiveInputFocus(self, *args):
        uicore.registry.SetFocus(self.sr.searchinput)

    def ToggleMapMode(self, *args):
        sm.GetService('map').ToggleMode()

    def ClickToggleFlatten(self, btn, *args):
        sm.GetService('starmap').ToggleFlattenMode()

    def OnFlattenModeChanged(self, isFlat, *args):
        btn = self.sr.flattenBtns.buttons[2]
        if isFlat:
            btn.SetLabel(localization.GetByLabel('UI/Map/MapPallet/btnUnflattenMap'))
        else:
            btn.SetLabel(localization.GetByLabel('UI/Map/MapPallet/btnFlattenMap'))

    def ShowPanel(self, panelname):
        uthread.pool('MapPalette::ShowPanel', self.sr.maintabs.ShowPanelByName, panelname)

    def Load(self, key):
        self.SetHint()
        if key == 'mapsearchpanel':
            self.Search(0)
        elif key == 'mapsettings':
            self.sr.starviewstabs.AutoSelect()
        elif key == 'options':
            self.sr.optionstabs.AutoSelect()
        elif key[:11] == 'mapsettings' or key[:8] == 'starview':
            if key == self.loadedTab:
                return
            self.LoadSettings(key)
        if self.destroyed:
            return
        self.loadedTab = key

    def OnMapModeChangeDone(self, mode):
        if self.destroyed or not hasattr(self, 'sr'):
            return
        btnMode = self.sr.flattenBtns.buttons[1]
        btnFlat = self.sr.flattenBtns.buttons[2]
        if mode == 'starmap':
            btnFlat.Enable()
            btnMode.SetLabel(localization.GetByLabel('UI/Map/MapPallet/tabSolarSystemMap'))
        elif mode == 'systemmap':
            btnFlat.Disable()
            btnMode.SetLabel(localization.GetByLabel('UI/Map/MapPallet/tabStarMap'))

    def OnReturnSearch(self, *args):
        self.Search(1)

    def Search(self, errorifnothing, *args):
        t = uthread.new(self.Search_thread, errorifnothing)
        t.context = 'mappalette::Search'

    def Search_thread(self, errorifnothing):
        if not self or self.destroyed:
            return
        self.searchresult = None
        search = self.sr.searchinput.GetValue().strip()
        if len(search) < 1:
            if errorifnothing:
                raise UserError('Min3Chars')
        elif len(search) < 3 and not localization.util.IsTextInConciseLanguage(localization.util.GetLanguageID(), search):
            raise UserError('Min3Chars')
        else:
            self.SetHint()
            if self is not None and not self.destroyed:
                self.ShowLoad()
            else:
                return
            self.searchresult = sm.GetService('map').FindByName(search)
        if self is None or self.destroyed:
            return
        self.ShowSearchResult()
        if self == None:
            return
        self.HideLoad()

    def ShowSearchResult(self, *args):
        self.listtype = 'location'
        mapSvc = sm.GetService('map')
        tmplst = []
        scrolllist = []
        if self.searchresult and len(self.searchresult):
            for each in self.searchresult:
                wasID = each.itemID
                found = [each.itemName]
                while wasID:
                    wasID = mapSvc.GetParent(wasID)
                    if wasID:
                        item = mapSvc.GetItem(wasID)
                        if item is not None:
                            found.append(item.itemName)

                if len(found) == 3:
                    trace = localization.GetByLabel('UI/Map/MapPallet/Trace3Locations', location1=found[0], location2=found[1], location3=found[2])
                elif len(found) == 2:
                    trace = localization.GetByLabel('UI/Map/MapPallet/Trace2Locations', location1=found[0], location2=found[1])
                else:
                    trace = '/'.join(found)
                entry = GetFromClass(LocationSearchItem, {'itemID': each.itemID,
                 'typeID': each.typeID,
                 'genericDisplayLabel': found[0],
                 'label': '%s<t>%s' % (trace, evetypes.GetName(each.typeID))})
                scrolllist.append(entry)

        if self is None or self.destroyed:
            return
        headers = [localization.GetByLabel('UI/Map/MapPallet/hdrSearchName'), localization.GetByLabel('UI/Map/MapPallet/hdrSearchType')]
        self.sr.scroll.Load(contentList=scrolllist, headers=headers)
        if not len(scrolllist):
            self.SetHint(localization.GetByLabel('UI/Map/MapPallet/lblSearchNothingFound'))

    def Confirm(self, *args):
        pass

    def Deselect(self, *args):
        pass

    def Select(self, selection, *args):
        sm.GetService('starmap').SetInterest(selection.id)

    def OnLoadWMCPSettings(self, tabName):
        if self.loadedTab == tabName:
            self.LoadSettings(tabName)

    def LoadSettings(self, what):
        scrolllist = []
        if what == 'mapsettings_lines':
            showlines = settings.user.ui.Get('showlines', 4)
            scrolllist.append(GetFromClass(Header, {'label': localization.GetByLabel('UI/Map/MapPallet/hdrConnectionLines')}))
            for config in [['showlines',
              0,
              localization.GetByLabel('UI/Map/MapPallet/cbNoLines'),
              showlines == 0],
             ['showlines',
              1,
              localization.GetByLabel('UI/Map/MapPallet/cbSelectionLinesOnly'),
              showlines == 1],
             ['showlines',
              2,
              localization.GetByLabel('UI/Map/MapPallet/cbSelectionRegionLinesOnly'),
              showlines == 2],
             ['showlines',
              3,
              localization.GetByLabel('UI/Map/MapPallet/cbSelectionRegionNeighborLinesOnly'),
              showlines == 3],
             ['showlines',
              4,
              localization.GetByLabel('UI/Map/MapPallet/cbAllLinesOnly'),
              showlines == 4]]:
                self.AddCheckBox(config, scrolllist, 'showlines')

            for config in [['map_alliance_jump_lines',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbAllianceJumpLines'),
              settings.user.ui.Get('map_alliance_jump_lines', 1) == 1]]:
                self.AddCheckBox(config, scrolllist)

            showJumpBridgesSetting = settings.user.ui.Get('showJumpBridges', 0)
            for config in [['showJumpBridges',
              0,
              localization.GetByLabel('UI/Map/MapPallet/cbMyJumpBridges'),
              showJumpBridgesSetting == 0], ['showJumpBridges',
              1,
              localization.GetByLabel('UI/Map/MapPallet/cbAllJumpBridges'),
              showJumpBridgesSetting == 1]]:
                self.AddCheckBox(config, scrolllist, 'showJumpBridges')

            scrolllist.append(GetFromClass(Header, {'label': localization.GetByLabel('UI/Map/MapPallet/hdrColorLinesBy')}))
            for config in [['mapcolorby',
              mapcommon.COLORMODE_UNIFORM,
              localization.GetByLabel('UI/Map/MapPallet/cbColorByJumpType'),
              settings.user.ui.Get('mapcolorby', mapcommon.COLORMODE_UNIFORM) == mapcommon.COLORMODE_UNIFORM], ['mapcolorby',
              mapcommon.COLORMODE_REGION,
              localization.GetByLabel('UI/Map/MapPallet/cbColorByRegion'),
              settings.user.ui.Get('mapcolorby', mapcommon.COLORMODE_UNIFORM) == mapcommon.COLORMODE_REGION], ['mapcolorby',
              mapcommon.COLORMODE_STANDINGS,
              localization.GetByLabel('UI/Map/MapPallet/cbColorByStanding'),
              settings.user.ui.Get('mapcolorby', mapcommon.COLORMODE_UNIFORM) == mapcommon.COLORMODE_STANDINGS]]:
                self.AddCheckBox(config, scrolllist, 'mapcolorby')

        if what == 'mapsettings_tiles':
            scrolllist.append(GetFromClass(Header, {'label': localization.GetByLabel('UI/Map/MapPallet/hdrTileSettings')}))
            for config in [['map_tile_no_tiles',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbTilesNone'),
              settings.user.ui.Get('map_tile_no_tiles', 1) == 1],
             ['map_tile_activity',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbTilesSovChanges'),
              settings.user.ui.Get('map_tile_activity', 0) == 1],
             ['map_tile_show_unflattened',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbTilesSovChangesUnflattened'),
              settings.user.ui.Get('map_tile_show_unflattened', 0) == 1],
             ['map_tile_show_outlines',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbTilesSovChangesOutlined'),
              settings.user.ui.Get('map_tile_show_outlines', 1) == 1]]:
                self.AddCheckBox(config, scrolllist)

            activeTileMode = settings.user.ui.Get('map_tile_mode', 0)
            scrolllist.append(GetFromClass(Header, {'label': localization.GetByLabel('UI/Map/MapPallet/hdrTileSovColorBy')}))
            for tileMode, text in [(0, localization.GetByLabel('UI/Map/MapPallet/cbTilesSovereignty')), (1, localization.GetByLabel('UI/Map/MapPallet/cbTilesStandings'))]:
                config = ['map_tile_mode',
                 tileMode,
                 text,
                 activeTileMode == tileMode]
                self.AddCheckBox(config, scrolllist, 'map_tile_mode')

        if what == 'mapsettings_legend':
            scrolllist += self.GetLegendGroups()
        starscolorby = settings.user.ui.Get('starscolorby', mapcommon.STARMODE_SECURITY)
        if what == 'starview_color':
            scrolllist += self.GetStarColorGroups()
        if what == 'mapsettings_solarsystem':
            scrolllist += maputils.GetSolarSystemOptions()
        if what == 'mapsettings_other':
            self.AddCheckBox(['mapautoframe',
             None,
             localization.GetByLabel('UI/Map/MapPallet/cbAnimFrameSelect'),
             settings.user.ui.Get('mapautoframe', 1) == 1], scrolllist)
            if settings.user.ui.Get('mapautoframe', 1) == 1:
                self.AddCheckBox(['mapautozoom',
                 None,
                 localization.GetByLabel('UI/Map/MapPallet/cbAnimAutoZoom'),
                 settings.user.ui.Get('mapautozoom', 0) == 1], scrolllist)
        if what == 'mapsettings_labels':
            scrolllist.append(GetFromClass(Header, {'label': localization.GetByLabel('UI/Map/MapPallet/hdrRegionLables')}))
            for config in [['rlabel_region',
              0,
              localization.GetByLabel('UI/Map/MapPallet/cbRegionNoLabel'),
              settings.user.ui.Get('rlabel_region', 1) == 0],
             ['rlabel_region',
              1,
              localization.GetByLabel('UI/Map/MapPallet/cbRegionSelected'),
              settings.user.ui.Get('rlabel_region', 1) == 1],
             ['rlabel_region',
              2,
              localization.GetByLabel('UI/Map/MapPallet/cbRegionAndNeigbour'),
              settings.user.ui.Get('rlabel_region', 1) == 2],
             ['rlabel_region',
              3,
              localization.GetByLabel('UI/Map/MapPallet/cbRegionAll'),
              settings.user.ui.Get('rlabel_region', 1) == 3]]:
                self.AddCheckBox(config, scrolllist, 'rlabel_region')

            scrolllist.append(GetFromClass(Header, {'label': localization.GetByLabel('UI/Map/MapPallet/hdrOtherLables')}))
            for config in [['label_constellation',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbOtherConstellation'),
              settings.user.ui.Get('label_constellation', 1) == 1], ['label_solarsystem',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbOtherSolarSysytem'),
              settings.user.ui.Get('label_solarsystem', 1) == 1], ['label_landmarknames',
              None,
              localization.GetByLabel('UI/Map/MapPallet/cbOtherLandmarks'),
              settings.user.ui.Get('label_landmarknames', 1) == 1]]:
                self.AddCheckBox(config, scrolllist)

        if self.destroyed:
            return
        self.sr.scroll2.Load(contentList=scrolllist)

    def GetActiveStarColorMode(self):
        starscolorby = settings.user.ui.Get('starscolorby', mapcommon.STARMODE_SECURITY)
        if not self.starColorByID:
            self.starColorByID = {}
            groupList = ['Root'] + self.GetAllStarColorGroupLabels()
            try:
                groupList.remove('Sovereignty_Sovereignty')
            except ValueError:
                log.LogError('Error while removing a sov option from the prime list - a long load may be impending!')

            for groupName in groupList:
                func = getattr(self, 'Get%sOptions' % groupName, None)
                if func is None:
                    continue
                ops = func()
                for label, id in ops:
                    self.starColorByID[id] = (groupName, label)

        if starscolorby not in self.starColorByID:
            if type(starscolorby) == types.TupleType and starscolorby[0] in (mapcommon.STARMODE_FACTION, mapcommon.STARMODE_MILITIA, mapcommon.STARMODE_FACTIONEMPIRE):
                _starmode, factionID = starscolorby
                options = {mapcommon.STARMODE_FACTION: ('Sovereignty_Sovereignty', localization.GetByLabel('UI/Map/MapPallet/cbModeFactions')),
                 mapcommon.STARMODE_FACTIONEMPIRE: ('Sovereignty_Sovereignty', localization.GetByLabel('UI/Map/MapPallet/cbStarsByEmpireFactions'))}.get(_starmode, (None, None))
                colorBy, factionName = options
                if factionID >= 0:
                    factionName = cfg.eveowners.Get(factionID).name
                self.starColorByID[starscolorby] = (colorBy, factionName)
            elif starscolorby == mapcommon.STARMODE_SOV_STANDINGS:
                self.starColorByID[starscolorby] = ('Sovereignty_Sovereignty', localization.GetByLabel('UI/Map/MapPallet/cbStarsByStandings'))
        return self.starColorByID.get(starscolorby, (None, None))

    def GetStarColorEntries(self, forGroup):
        starscolorby = settings.user.ui.Get('starscolorby', mapcommon.STARMODE_SECURITY)
        func = getattr(maputils, 'Get%sOptions' % forGroup, None)
        if not func:
            log.LogError('Missing function to provide options for', forGroup)
            return []
        scrolllist = []
        sublevel = 2 if forGroup.find('_') > 0 else 0
        for label, flag in func():
            config = ['starscolorby',
             flag,
             label,
             starscolorby == flag]
            entry = self.AddCheckBox(config, None, 'starscolorby', sublevel=sublevel)
            scrolllist.append(entry)

        return scrolllist

    def GetAllStarColorGroupLabels(self):
        self.GetStarColorGroupsSorted()
        topLevel = [ each[0] for each in self.starColorGroups ]
        tmp = [ each[2] for each in self.starColorGroups if each[2] != [] ]
        subLevel = []
        for each in tmp:
            subLevel.extend([ yu[0] for yu in each ])

        return topLevel + subLevel

    def GetStarColorGroupsSorted(self):
        if not self.starColorGroups:
            starColorGroups = [('Personal', localization.GetByLabel('UI/Map/MapPallet/hdrStarsMyInformation'), []),
             ('Services', localization.GetByLabel('UI/Map/MapPallet/hdrStarsServices'), []),
             ('Statistics', localization.GetByLabel('UI/Map/MapPallet/hdrStarsStatistics'), []),
             ('Sovereignty', localization.GetByLabel('UI/Map/MapPallet/hdrStarsSovereignty'), [('Sovereignty_FactionalWarfare', localization.GetByLabel('UI/Map/MapPallet/hdrStarsSovereigntyFacWar'), []),
               ('Sovereignty_Sovereignty', localization.GetByLabel('UI/Map/MapPallet/hdrStarsSovereignty'), []),
               ('Sovereignty_Changes', localization.GetByLabel('UI/Map/MapPallet/hdrStarsSovereigntyChanges'), []),
               ('Sovereignty_Development_Indices', localization.GetByLabel('UI/Map/MapPallet/hdrStarsSovereigntyIndixes'), []),
               ('Sovereignty_Insurgency', localization.GetByLabel('UI/Map/MapPallet/insurgencies'), [])]),
             ('Autopilot', localization.GetByLabel('UI/Map/MapPallet/hdrStarsAutoPilot'), []),
             ('Planets', localization.GetByLabel('UI/Map/MapPallet/hdrStarsPlanets'), []),
             ('Industry', localization.GetByLabel('UI/Map/MapPallet/hdrStarsIndustry'), [('Industry_Jobs', localization.GetByLabel('UI/Map/MapPallet/hdrIndustryJobs'), []), ('Industry_CostModifier', localization.GetByLabel('UI/Map/MapPallet/hdrIndustryCostModifier'), [])])]
            for group, label, subitems in starColorGroups:
                if subitems:
                    temp = []
                    for _group, _label, _subitems in subitems:
                        temp.append((_label, (_group, _label, _subitems)))

                    temp = SortListOfTuples(temp)
                    subitems = temp
                self.starColorGroups.append((label, (group, label, subitems)))

            self.starColorGroups = SortListOfTuples(self.starColorGroups)
        return self.starColorGroups

    def GetStarColorGroups(self):
        self.GetStarColorGroupsSorted()
        starscolorby = settings.user.ui.Get('starscolorby', mapcommon.STARMODE_SECURITY)
        scrolllist = self.GetStarColorEntries('Root')
        activeGroup, activeLabel = self.GetActiveStarColorMode()
        for groupName, groupLabel, subitems in self.starColorGroups:
            id = ('mappalette', groupName)
            uicore.registry.SetListGroupOpenState(id, 0)
            data = {'GetSubContent': self.GetSubContent,
             'label': groupLabel,
             'id': id,
             'groupItems': subitems,
             'iconMargin': 32,
             'showlen': 0,
             'state': 'locked',
             'BlockOpenWindow': 1,
             'key': groupName}
            if activeGroup == groupName:
                data['posttext'] = localization.GetByLabel('UI/Map/MapPallet/lblActiveColorCategory', activeLabel=activeLabel)
            elif activeGroup is not None and activeGroup.startswith(groupName + '_'):
                for subgroupName, subgroupLabel, subsubitems in subitems:
                    if activeGroup == subgroupName:
                        data['posttext'] = localization.GetByLabel('UI/Map/MapPallet/lblActiveColorCategory', activeLabel=subgroupLabel)

            scrolllist.append(GetFromClass(ListGroup, data))

        return scrolllist

    def GetStarColorSubGroups(self, subitems):
        scrolllist = []
        activeGroup, activeLabel = self.GetActiveStarColorMode()
        for groupName, groupLabel, subitems in subitems:
            id = ('mappalette', groupName)
            uicore.registry.SetListGroupOpenState(id, 0)
            data = {'GetSubContent': self.GetSubContent,
             'label': groupLabel,
             'id': id,
             'groupItems': [],
             'iconMargin': 32,
             'showlen': 0,
             'state': 'locked',
             'BlockOpenWindow': 1,
             'key': groupName,
             'sublevel': 1}
            if activeGroup == groupName:
                data['posttext'] = localization.GetByLabel('UI/Map/MapPallet/lblActiveColorCategory', activeLabel=activeLabel)
            scrolllist.append(GetFromClass(ListGroup, data))

        return scrolllist

    def GetSubContent(self, data, newitems = 0):
        if data.groupItems:
            return self.GetStarColorSubGroups(data.groupItems)
        for entry in self.sr.scroll.GetNodes():
            if entry.__guid__ != 'listentry.Group' or entry.id == data.id:
                continue
            if entry.open:
                if entry.panel:
                    entry.panel.Toggle()
                else:
                    uicore.registry.SetListGroupOpenState(entry.id, 0)
                    entry.scroll.PrepareSubContent(entry)

        if data.key in self.GetAllStarColorGroupLabels():
            return self.GetStarColorEntries(data.key)
        return []

    def UpdateActiveStarColor(self):
        activeGroup, activeLabel = self.GetActiveStarColorMode()
        for entry in self.sr.scroll.GetNodes():
            if entry.__guid__ != 'listentry.Group' or entry.key not in self.GetAllStarColorGroupLabels():
                continue
            post = ''
            if entry.key == activeGroup:
                post = localization.GetByLabel('UI/Map/MapPallet/lblActiveColorCategory', activeLabel=activeLabel)
            entry.posttext = post
            if entry.panel:
                entry.panel.UpdateLabel()

    def GetLegendGroups(self):
        common = {'groupItems': [],
         'iconMargin': 32,
         'showlen': 0,
         'state': 'locked',
         'BlockOpenWindow': 1}
        scrolllist = []
        forLst = [('star', localization.GetByLabel('UI/Map/MapPallet/tabStars')), ('tile', localization.GetByLabel('UI/Map/MapPallet/tabTiles'))]
        for groupName, groupLabel in forLst:
            id = ('mappalette', groupName)
            uicore.registry.SetListGroupOpenState(id, 0)
            data = common.copy()
            data.update({'GetSubContent': self.GetLegendEntries,
             'label': groupLabel,
             'id': id,
             'key': groupName})
            scrolllist.append(GetFromClass(ListGroup, data))

        return scrolllist

    def GetLegendEntries(self, data):
        legendList = sm.GetService('starmap').GetLegend(data.key)
        legendList.sort()
        scrolllist = []
        for legendItem in legendList:
            scrolllist.append(GetFromClass(LegendEntry, {'label': legendItem.caption,
             'key': data.key,
             'editable': False,
             'selectable': True,
             'hilightable': False,
             'legend': legendItem}))

        return scrolllist

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)
            self.sr.scroll2.ShowHint(hintstr)

    def AddCheckBox(self, config, scrolllist, group = None, sublevel = 0):
        cfgname, retval, desc, default = config
        data = {'label': desc,
         'checked': default,
         'cfgname': cfgname,
         'retval': retval,
         'group': group,
         'sublevel': sublevel,
         'OnChange': self.CheckBoxChange}
        if scrolllist is not None:
            scrolllist.append(GetFromClass(CheckboxEntry, data))
        else:
            return GetFromClass(CheckboxEntry, data)

    def CheckBoxChange(self, button, *args):
        starmapSvc = sm.GetService('starmap')
        key = button.GetSettingsKey()
        if isinstance(button, RadioButton):
            val = button.GetReturnValue()
        else:
            val = button.checked
        settings.user.ui.Set(key, val)
        if key == 'mapautoframe':
            self.LoadSettings('mapsettings_other')
        viewingStarmap = sm.GetService('viewState').IsViewActive('starmap')
        if viewingStarmap:
            if key == 'mapautoframe':
                starmapSvc.SetInterest()
            elif key == 'mapautozoom':
                starmapSvc.SetInterest()
            elif key == 'mapcolorby':
                starmapSvc.UpdateLines(updateColor=1)
            elif key in ('showlines', 'map_alliance_jump_lines', 'showJumpBridges'):
                starmapSvc.UpdateLines()
            elif key == 'starscolorby':
                starmapSvc.SetStarColorMode()
                self.UpdateActiveStarColor()
            elif key[:6] == 'label_':
                starmapSvc.CheckAllLabels('Mappalette::CheckBoxChange')
            elif key == 'rlabel_region':
                starmapSvc.CheckAllLabels('Mappalette::CheckBoxChange2')
            elif key.startswith('map_tile_'):
                starmapSvc.UpdateHexMap()

    def AddSeperator(self, height, where):
        Container(name='push', align=uiconst.TOTOP, height=height, parent=where)

    def AddHeader(self, header, where, height = 12):
        eveLabel.EveLabelMedium(text=header, parent=where, align=uiconst.TOTOP, height=12, state=uiconst.UI_NORMAL)

    def OnSelectionChange(self, selected):
        dataList = []
        colorList = []
        for node in selected:
            if node.key == 'tile':
                if node.legend.data is not None:
                    dataList.append(node.legend.data)
                else:
                    colorList.append(node.legend.color)

        if sm.GetService('viewState').IsViewActive('starmap'):
            sm.GetService('starmap').HighlightTiles(dataList, colorList)

    def Minimize(self, *args, **kwds):
        if self.windowID == 'mapspalette':
            settings.user.ui.Set('MapWindowMinimized', True)
        Window.Minimize(self, *args, **kwds)

    def Maximize(self, *args, **kwds):
        if self.windowID == 'mapspalette':
            settings.user.ui.Set('MapWindowMinimized', False)
        Window.Maximize(self, *args, **kwds)
