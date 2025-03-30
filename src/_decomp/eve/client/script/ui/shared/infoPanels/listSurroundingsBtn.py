#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\listSurroundingsBtn.py
import sys
from collections import defaultdict
import eveicon
import evetypes
import localization
import logging
import traceback
import uthread2
import utillib
from carbon.common.script.util.commonutils import StripTags
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.contextMenu.menuConst import DISABLED_ENTRY0
from carbonui.control.contextMenu.menuEntryData import MenuEntryData, MenuEntryDataCheckbox, MenuEntryDataCaption
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui import eveColor
from eve.client.script.ui.services.menuSvcExtras import movementFunctions
from eve.client.script.ui.shared.infoPanels.const.infoPanelConst import PANEL_LOCATION_INFO
from eve.client.script.ui.shared.infoPanels.locationInfoConst import SYSTEM_INFO_SHOW_NEAREST_SETTING, SYSTEM_INFO_SHOW_SOVEREIGNTY
from eve.client.script.ui.shared.mapView.markers.mapMarkerUtil import ICONS_BY_SCANGROUP
from eve.client.script.ui.shared.planet.planetConst import PLANETTYPE_NAMES
from eve.client.script.ui.util import uix
from eve.common.lib import appConst
from eve.common.script.sys.idCheckers import IsStructure, IsAbyssalSpaceSystem, IsVoidSpaceSystem
from evedungeons.common.instance_identifier import DungeonInstanceIdentifier
from eveformat import client as eveformat
from eveservices.menu import GetMenuService
from localization import GetByLabel
from menu import MenuLabel
from operations.client.operationscontroller import GetOperationsController
from operations.client.util import are_operations_active
from probescanning.explorationSites import get_exploration_site_name_label
from sovereignty.mercenaryden.client.repository import get_mercenary_den_repository
logger = logging.getLogger(__name__)

def GetBracketIconTexturePath(typeID):
    bracketSvc = sm.GetService('bracket')
    bracketData = bracketSvc.GetBracketDataByTypeID(typeID)
    if bracketData:
        texturePath = bracketData.texturePath
    return texturePath


class ListSurroundingsBtn(ButtonIcon):
    isDragObject = True
    default_iconSize = 24
    default_texturePath = 'res:/ui/texture/icons/77_32_49.png'

    def ApplyAttributes(self, attributes):
        super(ListSurroundingsBtn, self).ApplyAttributes(attributes)
        self.infoPanelService = sm.GetService('infoPanel')
        self.expandOnLeft = 1
        self.filterCurrent = 1
        self._is_in_space_menu = attributes.get('isInSpaceMenu', False)
        self.useDynamicMapItems = attributes.get('useDynamicMapItems', False)
        if not attributes.showIcon:
            self.icon.Hide()
        SYSTEM_INFO_SHOW_NEAREST_SETTING.on_change.connect(self.OnShowNearestSettingChanged)
        SYSTEM_INFO_SHOW_SOVEREIGNTY.on_change.connect(self.OnShowSovereigntySettingChanged)

    def SetSolarsystemID(self, solarsystemID):
        self.solarsystemID = solarsystemID
        self.sr.itemID = solarsystemID
        self.sr.typeID = appConst.typeSolarSystem

    def _GetMapItems(self):
        if self.useDynamicMapItems and self.solarsystemID:
            return sm.GetService('map').GetSolarsystemItems(self.solarsystemID, True, False)
        else:
            return self.sr.mapitems

    def GetInt(self, string):
        value = filter(lambda x: x in '0123456789', string)
        try:
            value = int(value)
        except:
            sys.exc_clear()

        return value

    def ExpandCelestial(self, mapItem):
        return GetMenuService().CelestialMenu(mapItem.itemID, mapItem=mapItem)

    def ExpandCategoryMenu(self, itemList):
        itemsByGroupID = defaultdict(list)
        for eachItem in itemList:
            itemsByGroupID[eachItem.groupID].append(eachItem)

        listToSort = []
        for groupID, groupList in itemsByGroupID.iteritems():
            groupName = evetypes.GetGroupNameByGroup(groupID)
            listToSort.append((groupName.lower(), (groupName, groupList)))

        sortedList = SortListOfTuples(listToSort)
        m = []
        for entry in sortedList:
            menuLabel, itemList = entry
            m.append(MenuEntryData(menuLabel, subMenuData=lambda _itemList = itemList: self.ExpandTypeMenu(_itemList), texturePath=GetBracketIconTexturePath(itemList[0].typeID)))

        return m

    def ExpandTypeMenu(self, items):
        typemenu = []
        for item in items:
            entryName = self._GetEntryName(item)
            typemenu.append(((item.celestialIndex, item.orbitIndex, entryName.lower()), MenuEntryData(entryName, subMenuData=lambda _item = item: self.ExpandCelestial(_item), texturePath=self._GetItemEntryTexturePath(item), func=lambda itemID = item.itemID: movementFunctions.WarpToItem(itemID))))

        typemenu = SortListOfTuples(typemenu)
        return typemenu

    def _GetItemEntryTexturePath(self, item):
        texturePath = None
        if IsStructure(evetypes.GetCategoryID(item.typeID)):
            bracketData = sm.GetService('bracket').GetBracketDataByTypeID(item.typeID)
            if bracketData:
                texturePath = bracketData.texturePath
        return texturePath

    def _GetEntryName(self, item):
        itemName = cfg.evelocations.Get(item.itemID).name
        if item.groupID == appConst.groupStation:
            name = uix.EditStationName(itemName, 1)
            if sm.GetService('home_station').is_home_station(item.itemID):
                name = '<color=%s>%s</color>' % (eveColor.CRYO_BLUE_HEX, name)
            return name
        if item.groupID == appConst.groupPlanet:
            return '%s (%s)' % (itemName, GetByLabel(PLANETTYPE_NAMES.get(item.typeID, '')))
        if item.groupID == appConst.groupStargate:
            slimItem = sm.StartService('michelle').GetItem(item.itemID)
            if self._IsGateUnavailable(item.itemID):
                itemName = eveformat.color(itemName, eveColor.DANGER_RED_HEX)
            if slimItem and slimItem.jumps:
                return '%s %s' % (itemName, eveformat.solar_system_security_status(slimItem.jumps[0].locationID))
            else:
                return itemName
        else:
            return itemName or item.itemName or 'no name!'

    def _IsGateUnavailable(self, gateID):
        lock_details = sm.GetService('gatejump').GetGateLockDetails()
        if lock_details and lock_details.gate_id != gateID:
            return True
        return False

    def GetMenu(self, *args):
        m = []
        mapitems = self._GetMapItems()
        if self.sr.Get('groupByType', 0):
            if self.sr.typeID and self.sr.itemID and not (IsAbyssalSpaceSystem(self.sr.itemID) or IsVoidSpaceSystem(self.sr.itemID)):
                m += [(MenuLabel('UI/Commands/ShowInfo'), GetMenuService().ShowInfo, (self.sr.typeID, self.sr.itemID))]
            if IsAbyssalSpaceSystem(self.sr.itemID) or IsVoidSpaceSystem(self.sr.itemID):
                m.append((MenuLabel('UI/Commands/ShowInfo'), DISABLED_ENTRY0))

            def GetGroupingKeyVal(labelPath):
                return utillib.KeyVal(labelPath=labelPath, typeIDs=[])

            categoriesToSplitToGroups = [(appConst.categoryStructure, 10)]
            groupDict = {appConst.groupAsteroidBelt: GetGroupingKeyVal('UI/Common/LocationTypes/AsteroidBelts'),
             appConst.groupPlanet: GetGroupingKeyVal('UI/Common/LocationTypes/Planets'),
             appConst.groupStargate: GetGroupingKeyVal('UI/Common/LocationTypes/Stargates'),
             appConst.groupStation: GetGroupingKeyVal('UI/Common/LocationTypes/Stations')}
            categoryDict = {appConst.categoryStructure: GetGroupingKeyVal('UI/Common/LocationTypes/Structures')}
            for item in mapitems:
                if item.groupID in groupDict:
                    groupDict[item.groupID].typeIDs.append(item)
                categoryID = evetypes.GetCategoryID(item.typeID)
                if categoryID in categoryDict:
                    categoryDict[categoryID].typeIDs.append(item)

            categoryGroupsToAdd = []
            for eachCategoryID, eachThreshold in categoriesToSplitToGroups:
                cat = categoryDict.get(eachCategoryID)
                if cat and len(cat.typeIDs) > eachThreshold:
                    categoryGroupsToAdd.append((cat.labelPath, cat.typeIDs))
                    categoryDict.pop(eachCategoryID)

            menuItemDict = {}
            menuItemDict.update(groupDict)
            menuItemDict.update(categoryDict)
            listToSort = []
            for groupingID, groupingInfo in menuItemDict.iteritems():
                itemList = groupingInfo.typeIDs
                if not itemList:
                    continue
                labelPath = groupingInfo.labelPath
                menuLabel = MenuLabel(labelPath)
                listToSort.append((localization.GetByLabel(labelPath), (menuLabel, itemList)))

            sortedList = SortListOfTuples(listToSort)
            for entry in sortedList:
                menuLabel, itemList = entry
                m.append(MenuEntryData(menuLabel, subMenuData=lambda _itemList = itemList: self.ExpandTypeMenu(_itemList), texturePath=GetBracketIconTexturePath(itemList[0].typeID)))

            for eachCatLablePath, items in categoryGroupsToAdd:
                m.append(MenuEntryData(MenuLabel(eachCatLablePath), subMenuData=lambda _items = items: self.ExpandCategoryMenu(_items), texturePath=GetBracketIconTexturePath(items[0].typeID)))

            anomalies = sm.GetService('sensorSuite').GetAnomalies()
            if len(anomalies) > 0:
                m.append(MenuEntryData(MenuLabel('UI/Inflight/Scanner/AnomalySiteFilterLabel'), subMenuData=lambda : self._GetAnomaliesMenu(anomalies), texturePath='res:/UI/Texture/Shared/Brackets/combatSite_16.png'))
            m += sm.GetService('bookmarkSvc').GetBookmarkMenuForNavigation()
            m += self._GetAgentMissonsMenu()
            m = self._AddOperationsMenu(m)
            m = self._AddContractsMenu(m)
            m += self._GetMercenaryDenActivitiesMenu()
        else:
            celestialMenu = GetMenuService().CelestialMenu
            mapitems = SortListOfTuples([ (item.itemName.lower(), item) for item in mapitems ])
            maxmenu = 25
            if len(mapitems) > maxmenu:
                groups = []
                counter = 0
                while counter < len(mapitems):
                    groups.append(mapitems[counter:counter + maxmenu])
                    counter = counter + maxmenu

                for group in groups:
                    groupmenu = []
                    for item in group:
                        groupmenu.append((item.itemName or 'no name!', celestialMenu(item.itemID, mapItem=item)))

                    if len(groupmenu):
                        fromLetter = '???'
                        if group[0].itemName:
                            fromLetter = StripTags(group[0].itemName)[0]
                        toLetter = '???'
                        if group[-1].itemName:
                            toLetter = StripTags(group[-1].itemName)[0]
                        m.append((fromLetter + '...' + toLetter, groupmenu))

                return m
            for item in mapitems[:30]:
                m.append((item.itemName or 'no name!', celestialMenu(item.itemID, mapItem=item)))

        m.append(None)
        starmapSvc = sm.GetService('starmap')
        if len(starmapSvc.GetWaypoints()) > 0:
            m.append((MenuLabel('UI/Neocom/ClearAllAutopilotWaypoints'), starmapSvc.ClearWaypoints, (None,)))
        m.append(None)
        if not self._is_in_space_menu:
            m.append(MenuEntryDataCheckbox(localization.GetByLabel('UI/Locations/ShowNearestLocation'), setting=SYSTEM_INFO_SHOW_NEAREST_SETTING))
            m.append(MenuEntryDataCheckbox(localization.GetByLabel('UI/Locations/ShowSystemSovereignty'), setting=SYSTEM_INFO_SHOW_SOVEREIGNTY))
        return m

    def _GetMercenaryDenActivitiesMenu(self):
        try:
            repository = get_mercenary_den_repository()
            mercenary_den_activities = repository.get_all_mercenary_den_activities_for_solar_system(session.solarsystemid2)
            if len(mercenary_den_activities) == 0:
                return []
            activities_submenu = []
            for mercenary_den_activity in mercenary_den_activities:
                if not mercenary_den_activity.is_started:
                    continue
                activity_id = mercenary_den_activity.id
                activity_name_message_id = mercenary_den_activity.template_name_id
                activity_description_message_id = mercenary_den_activity.template_description_id
                activity_name = localization.GetByMessageID(activity_name_message_id)
                activity_description = localization.GetByMessageID(activity_description_message_id)
                dungeon_instance_identifier = DungeonInstanceIdentifier.create_external_activity_instance_id(activity_id)
                activity_submenu = [MenuEntryData(localization.GetByLabel('UI/Commands/WarpTo'), subMenuData=None, func=lambda _dungeon_instance_id = dungeon_instance_identifier: sm.GetService('michelle').CmdWarpToExternalDungeon(_dungeon_instance_id))]
                activities_submenu.append(MenuEntryData(activity_name, subMenuData=activity_submenu, hint=activity_description, texturePath=eveicon.mercenary_den_bracket))

            if len(activities_submenu) == 0:
                return []
            return [MenuEntryData(MenuLabel('UI/Common/LocationTypes/MercenaryTacticalOperations'), subMenuData=activities_submenu, texturePath=eveicon.mercenary_den_bracket)]
        except Exception:
            logger.exception('Errored while building mercenary den activities menu: %s', traceback.format_exc())

        return []

    def _GetAnomaliesMenu(self, anomalies):
        menu = []
        allSitesByGroupID = self._GetAnomaliesByScanGroupID(anomalies)
        menusByScanGroup = defaultdict(set)
        sitesByMenu = defaultdict(list)
        for scanGroupID, sites in sorted(allSitesByGroupID.items()):
            for siteData in sites:
                menuGroup = get_exploration_site_name_label(site_type=scanGroupID, archetype_id=siteData.archetypeID)
                menusByScanGroup[scanGroupID].add(menuGroup)
                sitesByMenu[menuGroup].append(siteData)

        for scanGroupID in sorted(menusByScanGroup.keys()):
            for menuGroup in sorted(menusByScanGroup[scanGroupID], reverse=True):
                sites = sitesByMenu[menuGroup]
                menu += self._GetAnomaliesMenuGroup(sites, menuGroup)

        return menu

    def _GetAnomaliesMenuGroup(self, sites, groupName):
        menu = [MenuEntryDataCaption(MenuLabel(groupName))]
        for siteData in sites:
            menu.append(MenuEntryData('%s (%s)' % (siteData.GetDungeonName(), siteData.GetName()), subMenuData=lambda _siteData = siteData: sm.GetService('scanSvc').GetScanResultMenuWithoutIgnore(_siteData), func=lambda _siteData = siteData: _siteData.WarpToAction(None, 0), texturePath=ICONS_BY_SCANGROUP[siteData.scanStrengthAttribute]))

        return menu

    def _GetAnomaliesByScanGroupID(self, anomalies):
        ret = defaultdict(list)
        for siteData in anomalies:
            ret[siteData.scanStrengthAttribute].append(siteData)

        for sites in ret.values():
            sites.sort(key=lambda x: x.GetDungeonName())

        return ret

    def _GetAgentMissonsMenu(self):
        missionData = sm.GetService('journal').GetMyAgentJournalBookmarks()
        if not missionData:
            return []
        menu = self._GetAgentMissionEntries(missionData)
        if menu:
            return [MenuEntryData(MenuLabel('UI/PeopleAndPlaces/AgentMissions'), subMenuData=lambda : menu, texturePath=eveicon.agent_mission)]
        return []

    def _GetAgentMissionEntries(self, missionData):
        menu = []
        for missionNameID, bookmarks, agentID in missionData:
            if isinstance(missionNameID, (int, long)):
                missionName = localization.GetByMessageID(missionNameID)
            else:
                missionName = missionNameID
            entries = []
            for bookmark in bookmarks:
                if bookmark.solarsystemID == session.solarsystemid2:
                    entries.append(MenuEntryData(self._GetAgentEntryText(bookmark), subMenuData=lambda b = bookmark: GetMenuService().BookmarkMenu(b), func=lambda b = bookmark: movementFunctions.WarpToBookmark(b, warpRange=0)))

            if entries:
                agentMenuText = MenuLabel('UI/Neocom/MissionNameSubmenu', {'missionName': missionName,
                 'agent': agentID})
                menu.append([agentMenuText, entries])

        return menu

    def _GetAgentEntryText(self, bm):
        txt = bm.hint
        systemName = cfg.evelocations.Get(bm.solarsystemID).name
        if bm.locationType == 'dungeon':
            txt = txt.replace(' - %s' % systemName, '')
        if '- Moon ' in txt:
            txt = txt.replace(' - Moon ', ' - M')
        if txt.endswith('- '):
            txt = txt[:-2]
        return txt

    def _AddOperationsMenu(self, m):
        if are_operations_active() and GetOperationsController().is_any_operation_active():
            objective = self.infoPanelService.GetActiveOperationObjective()
            if objective:
                text, callback, icon = objective.GetLocation()
                if all([text, callback, icon]):
                    categoryName = objective.GetCategoryName()
                    operationName = objective.GetOperationName()
                    operationMenuTitle = MenuLabel('UI/Operations/InfoPanel/OperationMenuTitle')
                    operationMenuText = MenuLabel('UI/Operations/InfoPanel/OperationMenuText', {'operationName': operationName,
                     'categoryName': categoryName})
                    if len(callback) > 0:
                        func = callback[0]
                        args = callback[1:] if len(callback) > 1 else ()
                        operationSubmenu = [(text, func, args)]
                        operationMenu = [(operationMenuText, operationSubmenu)]
                        m += [None, (operationMenuTitle, lambda : None)] + operationMenu
        return m

    def _AddContractsMenu(self, m):
        contractsMenu = sm.GetService('contracts').GetContractsBookmarkMenu()
        if contractsMenu:
            m += contractsMenu
        return m

    def DoWarpToHidden(self, instanceID):
        sm.GetService('michelle').CmdWarpToStuff('epinstance', instanceID)

    def GetDragData(self, *args):
        itemID = self.sr.Get('itemID', None)
        typeID = self.sr.Get('typeID', None)
        if not itemID or not typeID:
            return []
        if IsAbyssalSpaceSystem(session.solarsystemid2) or IsVoidSpaceSystem(session.solarsystemid2):
            return []
        label = ''
        if typeID in (appConst.typeRegion, appConst.typeConstellation, appConst.typeSolarSystem):
            label += cfg.evelocations.Get(itemID).name
            elabel = {appConst.typeRegion: localization.GetByLabel('UI/Neocom/Region'),
             appConst.typeConstellation: localization.GetByLabel('UI/Neocom/Constellation'),
             appConst.typeSolarSystem: localization.GetByLabel('UI/Neocom/SolarSystem')}
            label += ' %s' % elabel.get(typeID)
        entry = utillib.KeyVal()
        entry.itemID = itemID
        entry.typeID = typeID
        entry.__guid__ = 'xtriui.ListSurroundingsBtn'
        entry.label = label
        return [entry]

    def OnShowNearestSettingChanged(self, value):
        uthread2.StartTasklet(self.infoPanelService.UpdatePanel, PANEL_LOCATION_INFO)

    def OnShowSovereigntySettingChanged(self, value):
        uthread2.StartTasklet(self.infoPanelService.UpdatePanel, PANEL_LOCATION_INFO)
