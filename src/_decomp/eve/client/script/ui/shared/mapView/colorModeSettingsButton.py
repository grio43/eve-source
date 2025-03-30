#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\colorModeSettingsButton.py
import localization
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui import uiconst
from carbonui.control.scrollentries import ScrollEntryNode
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.uicore import uicore
from carbonui.control.button import Button
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.control.themeColored import LineThemeColored
from eve.client.script.ui.shared.mapView.mapViewColorHandler import GetFormatFunctionLabel, GetColorModeHint
from eve.client.script.ui.shared.mapView.mapViewConst import VIEWMODE_COLOR_SETTINGS, VIEWMODE_COLOR_RECENT, VIEWMODE_COLOR_RECENT_MAX
from eve.client.script.ui.shared.mapView.mapViewSettings import SETTINGS_COG_ICON, COLORMODE_MENU_WIDTH, COLORMODE_MENU_HEIGHT, SetMapViewSetting, GetMapViewSetting
from eve.client.script.ui.shared.mapView.controls.mapViewSettingButton import MapViewSettingButton
from eve.client.script.ui.shared.mapView.controls.mapViewCheckbox import MapViewCheckbox
from eve.client.script.ui.shared.maps.mapcommon import *
from eve.client.script.ui.shared.planet import planetConst
from eve.common.lib import appConst
from eve.common.script.util.facwarCommon import GetOccupierFWFactions
import blue

class MapViewColorModeSettingButton(MapViewSettingButton):

    def ReloadSettingValue(self):
        self.SetTexturePath(SETTINGS_COG_ICON)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if uicore.uilib.leftbtn:
            return
        tooltipPanel.columns = 1
        tooltipPanel.cellPadding = 2
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.AddLabelSmall(text=localization.GetByLabel('UI/Map/ColorMapBy'), bold=True, cellPadding=(8, 4, 4, 2))
        divider = LineThemeColored(align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=1, padding=(1, 1, 1, 0), opacity=0.3)
        tooltipPanel.AddCell(divider, cellPadding=(0, 0, 0, 0))
        if session.role & ROLE_GML:
            Button(parent=tooltipPanel, label='Debug Run All', func=self.DebugRunAll, align=uiconst.CENTER)
        tooltipPanel.AddLabelSmall(text=localization.GetByLabel('UI/Map/RecentColorBy'), cellPadding=(8, 4, 4, 2))
        self.recentLayoutGrid = LayoutGrid(columns=1, parent=tooltipPanel)
        self.LoadRecentColorModes()
        divider = LineThemeColored(align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=1, padding=(1, 1, 1, 0), opacity=0.3)
        tooltipPanel.AddCell(divider, cellPadding=(0, 0, 0, 0))
        self.scroll = Scroll(parent=tooltipPanel, align=uiconst.TOTOP, height=COLORMODE_MENU_HEIGHT)
        self.scroll.OnUpdatePosition = self.OnScrollPositionChanged
        tooltipPanel.AddSpacer(width=COLORMODE_MENU_WIDTH)
        self.LoadColorModes()

    def DebugRunAll(self, *args):
        print 'DebugRunAll'
        for groupLabel, groupID, loadFunction in self.GetColorModeGroups():
            colorModes = loadFunction()
            for colorMode in colorModes:
                print ' -', colorMode, GetFormatFunctionLabel(colorMode)
                SetMapViewSetting(VIEWMODE_COLOR_SETTINGS, colorMode, self.mapViewID)
                if self.callback:
                    self.callback(self.settingGroupKey, colorMode)
                blue.synchro.Sleep(500)

    def OnScrollPositionChanged(self, *args, **kwargs):
        settings.char.ui.Set('mapViewColorModeScrollPosition_%s' % self.mapViewID, self.scroll.GetScrollProportion())

    def GetScrollEntries(self, options, settingsKey = None, sublevel = 0):
        currentActive = GetMapViewSetting(self.settingGroupKey, self.mapViewID)
        scrollList = []
        for colorMode in options:
            label = GetFormatFunctionLabel(colorMode)
            if not label:
                continue
            config = [self.settingGroupKey,
             colorMode,
             label,
             currentActive == colorMode]
            entry = self.AddCheckBox(config, None, self.settingGroupKey, sublevel=sublevel)
            scrollList.append(entry)

        return scrollList

    def GetGroupScrollEntry(self, groupID, groupLabel, groupData):
        return GetFromClass(ListGroup, {'GetSubContent': self.GetSubContent,
         'label': groupLabel,
         'id': ('mapviewsettings', groupID),
         'groupItems': groupData,
         'iconMargin': 32,
         'showlen': 0,
         'state': 'locked',
         'BlockOpenWindow': 1,
         'key': groupID,
         'showicon': 'hide'})

    def GetSubContent(self, data, newitems = 0):
        for entry in self.scroll.GetNodes():
            if entry.__guid__ != 'listentry.Group' or entry.id == data.id:
                continue
            if entry.open:
                if entry.panel:
                    entry.panel.Toggle()
                else:
                    uicore.registry.SetListGroupOpenState(entry.id, 0)
                    entry.scroll.PrepareSubContent(entry)

        return self.GetScrollEntries(data.groupItems)

    def AddCheckBox(self, config, scrolllist, group = None, sublevel = 0):
        cfgname, colorMode, desc, default = config
        data = {}
        data['label'] = desc
        data['hint'] = GetColorModeHint(colorMode)
        data['checked'] = default
        data['cfgname'] = cfgname
        data['retval'] = colorMode
        data['group'] = group
        data['OnChange'] = self.OnColorModeScrollCheckBoxChange
        data['entryWidth'] = COLORMODE_MENU_WIDTH
        data['decoClass'] = MapViewCheckbox
        scrollNode = ScrollEntryNode(**data)
        if scrolllist is not None:
            scrolllist.append(scrollNode)
        else:
            return scrollNode

    def OnColorModeScrollCheckBoxChange(self, radioButton):
        key = radioButton.GetSettingsKey()
        val = radioButton.GetReturnValue()
        if val is None:
            val = radioButton.checked
        self._SetColorMode(key, val)
        self.RegisterRecentColorMode(val)
        self.LoadRecentColorModes()

    def OnColorModeCheckBoxChange(self, checkbox):
        key = checkbox.GetSettingsKey()
        val = checkbox.GetReturnValue()
        if val is None:
            val = checkbox.checked
        self._SetColorMode(key, val)
        self.LoadColorModes()

    def _SetColorMode(self, key, val):
        SetMapViewSetting(key, val, self.mapViewID)
        if self.callback:
            self.callback(self.settingGroupKey, val)

    def GetColorModeOptions(self):
        scrollEntries = []
        for groupLabel, groupID, loadFunction in self.GetColorModeGroups():
            groupEntry = self.GetGroupScrollEntry(groupID, groupLabel, loadFunction())
            scrollEntries.append((groupLabel.lower(), groupEntry))

        return [ entry for sortLabel, entry in sorted(scrollEntries) ]

    def RegisterRecentColorMode(self, colorMode):
        current = GetMapViewSetting(VIEWMODE_COLOR_RECENT, self.mapViewID)
        if colorMode in current:
            return
        current.insert(0, colorMode)
        current = current[:VIEWMODE_COLOR_RECENT_MAX]
        SetMapViewSetting(VIEWMODE_COLOR_RECENT, current, self.mapViewID)

    def GetRecentColorModes(self):
        return GetMapViewSetting(VIEWMODE_COLOR_RECENT, self.mapViewID)

    def LoadColorModes(self):
        scrollPosition = settings.char.ui.Get('mapViewColorModeScrollPosition_%s' % self.mapViewID, 0.0)
        scrollEntries = self.GetColorModeOptions()
        self.scroll.Load(contentList=scrollEntries, scrollTo=scrollPosition)

    def LoadRecentColorModes(self):
        if self.destroyed:
            return
        self.recentLayoutGrid.Flush()
        ret = self.GetRecentColorModes()
        currentActive = GetMapViewSetting(VIEWMODE_COLOR_SETTINGS, self.mapViewID)
        for colorMode in ret:
            label = GetFormatFunctionLabel(colorMode)
            if not label:
                continue
            checkBox = RadioButton(align=uiconst.TOPLEFT, text=label, hint=GetColorModeHint(colorMode), checked=colorMode == currentActive, wrapLabel=True, callback=self.OnColorModeCheckBoxChange, settingsKey=VIEWMODE_COLOR_SETTINGS, groupname=VIEWMODE_COLOR_SETTINGS, retval=colorMode, settingsPath=None, width=COLORMODE_MENU_WIDTH - 10)
            self.recentLayoutGrid.AddCell(cellObject=checkBox, cellPadding=(5, 0, 5, 0))

    def GetNPCOptions(self):
        ret = [STARMODE_DUNGEONS,
         STARMODE_DUNGEONSAGENTS,
         STARMODE_INCURSION,
         STARMODE_EDENCOM_FORTRESS,
         STARMODE_EDENCOM_MINOR_VICTORIES,
         STARMODE_TRIGLAVIAN_MINOR_VICTORIES]
        return ret

    def GetCorporationOptions(self):
        ret = [STARMODE_FRIENDS_CORP]
        if (appConst.corpRoleAccountant | appConst.corpRoleJuniorAccountant) & session.corprole != 0:
            ret += [STARMODE_CORPOFFICES,
             STARMODE_CORPIMPOUNDED,
             STARMODE_CORPPROPERTY,
             STARMODE_CORPDELIVERIES,
             STARMODE_CORPWRAPS]
        return ret

    def GetPersonalColorModeOptions(self):
        ret = [STARMODE_ASSETS,
         STARMODE_VISITED,
         STARMODE_CARGOILLEGALITY,
         STARMODE_PISCANRANGE,
         STARMODE_FRIENDS_FLEET,
         STARMODE_FRIENDS_AGENT,
         STARMODE_MYCOLONIES,
         STARMODE_AVOIDANCE,
         STARMODE_JUMP_CLONES]
        return ret

    def GetPlanetsOptions(self):
        ret = []
        for planetTypeID in planetConst.PLANET_TYPES:
            ret.append((STARMODE_PLANETTYPE, planetTypeID))

        return ret

    def GetIndustryOptions(self):
        ret = [STARMODE_JOBS24HOUR,
         STARMODE_MANUFACTURING_JOBS24HOUR,
         STARMODE_RESEARCHTIME_JOBS24HOUR,
         STARMODE_RESEARCHMATERIAL_JOBS24HOUR,
         STARMODE_COPY_JOBS24HOUR,
         STARMODE_INVENTION_JOBS24HOUR,
         STARMODE_INDUSTRY_MANUFACTURING_COST_INDEX,
         STARMODE_INDUSTRY_RESEARCHTIME_COST_INDEX,
         STARMODE_INDUSTRY_RESEARCHMATERIAL_COST_INDEX,
         STARMODE_INDUSTRY_COPY_COST_INDEX,
         STARMODE_INDUSTRY_INVENTION_COST_INDEX,
         STARMODE_INDUSTRY_REACTION_COST_INDEX]
        return ret

    def GetServicesOptions(self):
        ret = [STARMODE_STATION_SERVICE_CLONING,
         STARMODE_STATION_SERVICE_FACTORY,
         STARMODE_STATION_SERVICE_FITTING,
         STARMODE_STATION_SERVICE_INSURANCE,
         STARMODE_STATION_SERVICE_LABORATORY,
         STARMODE_STATION_SERVICE_REPAIRFACILITIES,
         STARMODE_STATION_SERVICE_NAVYOFFICES,
         STARMODE_STATION_SERVICE_REPROCESSINGPLANT,
         STARMODE_STATION_SERVICE_SECURITYOFFICE]
        return ret

    def GetStatisticsOptions(self):
        ret = [STARMODE_REAL,
         STARMODE_SECURITY,
         STARMODE_REGION,
         STARMODE_PLAYERCOUNT,
         STARMODE_PLAYERDOCKED,
         STARMODE_JUMPS1HR,
         STARMODE_SHIPKILLS1HR,
         STARMODE_SHIPKILLS24HR,
         STARMODE_PODKILLS1HR,
         STARMODE_PODKILLS24HR,
         STARMODE_FACTIONKILLS1HR,
         STARMODE_STATIONCOUNT,
         STARMODE_CYNOSURALFIELDS,
         STARMODE_ROAMING_WEATHER,
         STARMODE_DYNAMIC_BOUNTY,
         STARMODE_SYSTEM_INTERFERENCE]
        return ret

    def GetFactionalWarfareOptions(self):
        ret = [(STARMODE_MILITIA, STARMODE_FILTER_FACWAR_ENEMY)]
        for factionID in GetOccupierFWFactions():
            ret.append((STARMODE_MILITIA, factionID))

        ret.append(STARMODE_MILITIAKILLS1HR)
        ret.append(STARMODE_MILITIAKILLS24HR)
        return ret

    def GetInsurgencyOptions(self):
        ret = []
        ret.append(STARMODE_INSURGENCY)
        ret.append(STARMODE_INSURGENCY_CORRUPTION)
        ret.append(STARMODE_INSURGENCY_SUPPRESSION)
        return ret

    def GetSovereigntyDevelopmentIndicesOptions(self):
        ret = [STARMODE_INDEX_STRATEGIC, STARMODE_INDEX_MILITARY, STARMODE_INDEX_INDUSTRY]
        return ret

    def GetSovereigntyOptions(self):
        ret = [STARMODE_FACTION,
         STARMODE_SOV_STANDINGS,
         (STARMODE_FACTIONEMPIRE, STARMODE_FILTER_EMPIRE),
         STARMODE_INDEX_STRATEGIC,
         STARMODE_INDEX_MILITARY,
         STARMODE_INDEX_INDUSTRY,
         STARMODE_SOV_CHANGE,
         STARMODE_SOV_GAIN,
         STARMODE_SOV_LOSS]
        return ret

    def GetColorModeGroups(self):
        colorModeGroups = [(localization.GetByLabel('UI/Map/MapColorPersonal'), 'Personal', self.GetPersonalColorModeOptions),
         (localization.GetByLabel('UI/Map/MapPallet/hdrStarsServices'), 'Services', self.GetServicesOptions),
         (localization.GetByLabel('UI/Map/MapColorGeography'), 'Statistics', self.GetStatisticsOptions),
         (localization.GetByLabel('UI/Map/MapColorNPC'), 'NPCActivity', self.GetNPCOptions),
         (localization.GetByLabel('UI/Map/MapColorCorporation'), 'Corporation', self.GetCorporationOptions),
         (localization.GetByLabel('UI/Map/MapPallet/hdrStarsPlanets'), 'Planets', self.GetPlanetsOptions),
         (localization.GetByLabel('UI/Map/MapPallet/hdrStarsIndustry'), 'Industry', self.GetIndustryOptions),
         (localization.GetByLabel('UI/Map/MapPallet/hdrStarsSovereigntyFacWar'), 'FactionalWarfare', self.GetFactionalWarfareOptions),
         (localization.GetByLabel('UI/Map/MapPallet/hdrStarsSovereignty'), 'Sovereignty', self.GetSovereigntyOptions),
         (localization.GetByLabel('UI/Map/MapPallet/insurgencies'), 'Insurgencies', self.GetInsurgencyOptions)]
        if session.role & ROLE_GML:
            colorModeGroups.append(('GM / WM Extras', 'GmExtras', self.GetGMOptions))
        return colorModeGroups

    def GetGMOptions(self):
        return [STARMODE_INCURSIONGM,
         STARMODE_ICEBELTS,
         STARMODE_ASTEROIDBELTS,
         STARMODE_SIGNATURES,
         STARMODE_ANOMALIES]
