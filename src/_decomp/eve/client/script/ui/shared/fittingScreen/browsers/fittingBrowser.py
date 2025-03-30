#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\browsers\fittingBrowser.py
import itertools
from carbonui.button.const import HEIGHT_NORMAL
from collections import defaultdict
from carbon.common.script.sys.serviceConst import ROLE_WORLDMOD, ROLEMASK_ELEVATEDPLAYER
from carbonui import uiconst
from carbonui.primitives.fill import Fill
from characterdata.races import get_race
from characterdata.races import get_race_name
from menu import MenuLabel
from carbonui.primitives.sprite import Sprite
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.listgroup import ListGroup as Group, ListGroup
from eve.client.script.ui.control.entries.fitting import FittingEntry
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.util import uix
from carbonui.primitives.container import Container
import evetypes
from eve.client.script.ui.shared.fitting.fittingUtil import CanDeleteFit, GetDeletableNodes, DeleteFittings
from eve.client.script.ui.shared.fittingScreen import BROWSER_SEARCH_FITTINGS, FITTING_OWNER_CORP, FITTING_OWNER_COMMUNITY, FITTING_OWNER_PERSONAL, FITTING_OWNER_ALLIANCE
from eve.client.script.ui.shared.fittingScreen.settingUtil import GetCommunityFittingSetting, GetCorpFittingSetting, GetAllianceFittingSetting, GetOnlyCurrentShipSetting, GetOnlyFittingsWithSkillsSetting, GetPersonalFittingSetting, IsFittingAndHullsSelected
from eve.client.script.ui.shared.fittingMgmtWindow import OpenOrLoadMultiFitWnd
from eve.client.script.ui.shared.fittingScreen.shipFittingSimulationButton import ShipFittingSimulationButton
from eve.client.script.ui.shared.traits import HasTraits, TraitsContainer
from eve.common.lib import appConst
from eve.common.script.sys.eveCfg import IsDocked
from globalConfig.getFunctions import AreCommunityFittingsEnabled, GetMaxShipsToFit
from localization import GetByLabel
import log
from utillib import KeyVal
from eveservices.menu import GetMenuService
from eve.common.script.sys.eveCfg import IsControllingStructure
import blue
from carbonui.uicore import uicore
NON_EMPIRE = -1
MARKET_GROUP_CITADEL = 2199
MARKET_GROUP_ENGINEERING_COMPLEX = 2324
MARKET_GROUP_REFINERY = 2327
MARKET_GROUP_NAVIGATION_STRUCTURES = 2511
MARKET_GROUP_SPECIAL_SHIPS = 1612

class FittingBrowserListProvider(object):

    def __init__(self, onDropDataFunc):
        self.onDropDataFunc = onDropDataFunc
        self.fittingSvc = sm.GetService('fittingSvc')
        self.ghostFittingSvc = sm.GetService('ghostFittingSvc')
        self.specialTypeIDs = None
        self.currentShipTypeID = None
        if session.role & ROLEMASK_ELEVATEDPLAYER:
            try:
                self.fittingSpawner = sm.GetService('fittingspawner')
            except:
                self.fittingSpawner = None

    def GetFittingScrolllist(self, currentShipTypeID, *args):
        communityFittingEnabled = AreCommunityFittingsEnabled(sm.GetService('machoNet'))
        self.currentShipTypeID = currentShipTypeID
        showPersonalFittings = GetPersonalFittingSetting()
        showCorpFittings = GetCorpFittingSetting()
        showAllianceFittings = GetAllianceFittingSetting()
        onlyShowCurrentShip = GetOnlyCurrentShipSetting()
        onlyWithSkillsFor = GetOnlyFittingsWithSkillsSetting()
        showCommunityFittings = GetCommunityFittingSetting() if communityFittingEnabled else False
        ownerFilterIsSet = showPersonalFittings or showCorpFittings or showAllianceFittings or showCommunityFittings
        if not ownerFilterIsSet:
            showCorpFittings = True
            showPersonalFittings = True
            showAllianceFittings = True
            if communityFittingEnabled:
                showCommunityFittings = True
        personalFittings, corpFittings, communityFittings, allianceFittings = self.fittingSvc.GetAllFittingsForCharacter()
        if not IsFittingAndHullsSelected():
            return
        fittingNumByTypeID = self.GetNumShipsByTypeID(personalFittings, corpFittings, communityFittings, allianceFittings)
        filterText = settings.user.ui.Get(BROWSER_SEARCH_FITTINGS, '')
        filterTextLower = filterText.lower()
        filteringSettings = KeyVal(filterTextLower=filterTextLower, personalFittings=personalFittings, corpFittings=corpFittings, allianceFittings=allianceFittings, communityFittings=communityFittings, showPersonalFittings=showPersonalFittings, showCorpFittings=showCorpFittings, showCommunityFittings=showCommunityFittings, showAllianceFittings=showAllianceFittings, onlyShowCurrentShip=onlyShowCurrentShip, onlyWithSkillsFor=onlyWithSkillsFor, ownerFilterIsSet=ownerFilterIsSet)
        fittings = self.FilterOutFittings(filteringSettings)
        self.PopulatedSpecialEditionShips()
        fittingsByGroupID, shipsByGroupID, shipGroups, shipsByGroupAndRaceIDs, fittingsByGroupAndRaceIDs, unsupportedFittings = self.GetShipsAndGroups(filteringSettings, fittings)
        scrolllist = []
        noFittingsFound = len(fittings) == 0 and ownerFilterIsSet
        if noFittingsFound:
            scrolllist.append(GetFromClass(Generic, {'label': GetByLabel('UI/Common/NothingFound')}))
        else:

            def GetScrollListForShipGroups(groupsToGet, sublevel = 0, groupPrefix = ''):
                listOfGroups = []
                for groupName, groupID in groupsToGet:
                    shipsForGroup = shipsByGroupAndRaceIDs[groupID]
                    isGroupForCurrentShip = any((self.currentShipTypeID in x for x in shipsForGroup.itervalues()))
                    fittingsByRaceID = fittingsByGroupAndRaceIDs[groupID]
                    groupNameForID = '%s%s' % (groupPrefix, groupName)
                    data = {'GetSubContent': self.GetRacesForGroup,
                     'label': groupName,
                     'groupItems': shipsForGroup,
                     'fittingsByRaceID': fittingsByRaceID,
                     'shipsByRaceID': shipsForGroup,
                     'id': ('fittingMgmtScrollWndGroup', groupNameForID),
                     'showlen': 0,
                     'sublevel': sublevel,
                     'fittingNumByTypeID': fittingNumByTypeID,
                     'showCommunityFits': communityFittingEnabled,
                     'isGroupForCurrentShip': isGroupForCurrentShip}
                    data.update(self.GetCommonGroupData())
                    groupEntry = (groupName, GetFromClass(ShipParentGroup, data))
                    listOfGroups.append(groupEntry)

                listOfGroups = SortListOfTuples(listOfGroups)
                return listOfGroups

            normalShips = {(groupName, groupID) for groupName, groupID in shipGroups if groupID > 0}
            shipScrollList = GetScrollListForShipGroups(normalShips)
            specialShips = {(groupName, groupID) for groupName, groupID in shipGroups if groupID < 0}
            if specialShips:

                def GetSpecialShipGroup(nodedata):
                    return GetScrollListForShipGroups(nodedata.groupItems, sublevel=1, groupPrefix='special')

                data = {'GetSubContent': GetSpecialShipGroup,
                 'groupItems': specialShips,
                 'label': GetByLabel('UI/Fitting/FittingWindow/SpecialEditionShips'),
                 'id': ('fittingMgmtScrollWndGroup', 'specialShips'),
                 'showlen': 0,
                 'isGroupForCurrentShip': self.currentShipTypeID in self.specialTypeIDs}
                data.update(self.GetCommonGroupData())
                groupEntry = GetFromClass(ShipParentGroup, data)
                shipScrollList.append(groupEntry)
            if ownerFilterIsSet and unsupportedFittings:
                shipScrollList += self.AddUnsupportedGroup(unsupportedFittings)
            if shipScrollList:
                scrolllist.extend(shipScrollList)
            else:
                scrolllist.append(GetFromClass(Generic, {'label': GetByLabel('UI/Common/NothingFound')}))
        return scrolllist

    def AddUnsupportedGroup(self, unsupportedFittings):
        data = {'GetSubContent': self.GetScrollListForUnsupportedFittings,
         'groupItems': unsupportedFittings,
         'label': GetByLabel('UI/Fitting/FittingWindow/UnsupportedShip'),
         'id': ('fittingMgmtScrollWndGroup', 'unsupportedFittings'),
         'showlen': 0}
        data.update(self.GetCommonGroupData())
        groupEntry = GetFromClass(ListGroup, data)
        return [groupEntry]

    def GetScrollListForUnsupportedFittings(self, nodedata):
        fittings = nodedata.groupItems
        scrollList = []
        for eachFitting in fittings:
            shipTypeExists = evetypes.Exists(eachFitting.shipTypeID)
            if shipTypeExists and session.role & ROLEMASK_ELEVATEDPLAYER:
                scrollList += self.GetFittingEntriesForType([eachFitting], sublevel=0)
                continue
            fittingName = eachFitting.name
            if shipTypeExists:
                shipTypeName = evetypes.GetName(eachFitting.shipTypeID)
            else:
                shipTypeName = GetByLabel('UI/Fitting/FittingWindow/UnknownShipType')
            fittingName = '%s (%s) - %s' % (fittingName, shipTypeName, 'unsupported')
            scrollList.append(GetFromClass(Generic, {'label': fittingName,
             'GetMenu': self.GetFittingMenuForUnsupportedFittings,
             'sublevel': 1,
             'ownerID': eachFitting.ownerID,
             'fittingID': eachFitting.fittingID}))

        return scrollList

    def GetFittingMenuForUnsupportedFittings(self, entry):
        node = entry.sr.node
        node.scroll.SelectNode(node)
        selectedNodes = node.scroll.GetSelectedNodes(node)
        if CanDeleteFit(node.ownerID):
            m = [(MenuLabel('UI/Fitting/FittingWindow/FittingManagement/DeleteFitting'), self.DeleteFitting, [entry, selectedNodes])]
        return m

    def GetCommonGroupData(self, showIcon = 'hide'):
        return {'state': 'locked',
         'BlockOpenWindow': 1,
         'showicon': showIcon,
         'DropData': self.onDropDataFunc}

    def GetNumShipsByTypeID(self, personalFittings, corpFittings, communityFittings, allianceFittings):
        fittingNumByTypeID = defaultdict(lambda : defaultdict(int))
        for owner, fittingDict in [(FITTING_OWNER_PERSONAL, personalFittings),
         (FITTING_OWNER_CORP, corpFittings),
         (FITTING_OWNER_COMMUNITY, communityFittings),
         (FITTING_OWNER_ALLIANCE, allianceFittings)]:
            for fitting in fittingDict.itervalues():
                fittingNumByTypeID[fitting.shipTypeID][owner] += 1

        return fittingNumByTypeID

    def GetRacesForGroup(self, nodedata):
        shipScrollist = []
        fittingsByRaceID = nodedata.fittingsByRaceID
        shipsByRaceID = nodedata.shipsByRaceID
        sublevel = nodedata.sublevel + 1
        parentGroupNameForID = nodedata.id[1]
        for raceID, fittingsForRace in nodedata.groupItems.iteritems():
            raceIconID, raceName = self.GetNameAndIconIDForRace(raceID)
            groupNameForID = '%s_%s' % (parentGroupNameForID, raceID)
            isGroupForCurrentShip = self.currentShipTypeID in fittingsForRace
            data = {'GetSubContent': self.GetShipGroupSubContent,
             'label': raceName,
             'fittings': fittingsByRaceID[raceID],
             'groupItems': fittingsForRace,
             'allShips': shipsByRaceID[raceID],
             'id': ('fittingMgmtScrollWndGroup', groupNameForID),
             'iconID': raceIconID,
             'sublevel': sublevel,
             'fittingNumByTypeID': nodedata.fittingNumByTypeID,
             'showCommunityFits': nodedata.showCommunityFits,
             'isGroupForCurrentShip': isGroupForCurrentShip}
            data.update(self.GetCommonGroupData())
            groupEntry = ((raceIconID == NON_EMPIRE, raceName), GetFromClass(ShipParentGroup, data))
            shipScrollist.append(groupEntry)

        shipScrollist = SortListOfTuples(shipScrollist)
        return shipScrollist

    def GetNameAndIconIDForRace(self, raceID):
        if raceID == NON_EMPIRE:
            raceName = GetByLabel('UI/Fitting/FittingWindow/NonEmpireFaction')
            raceIconID = 1443
        else:
            race = get_race(raceID)
            raceName = get_race_name(raceID, race)
            raceIconID = race.iconID
        return (raceIconID, raceName)

    def GetMaxFittingNumber(self, ownerID):
        maxFittings = None
        if ownerID == session.charid:
            maxFittings = appConst.maxCharFittings
        elif ownerID == session.corpid:
            maxFittings = appConst.maxCorpFittings
        return maxFittings

    def FilterOutFittings(self, filteringSettings):
        fittings = {}
        if filteringSettings.showPersonalFittings:
            fittings.update(filteringSettings.personalFittings)
        if filteringSettings.showCorpFittings:
            fittings.update(filteringSettings.corpFittings)
        if filteringSettings.showCommunityFittings:
            fittings.update(filteringSettings.communityFittings)
        if filteringSettings.showAllianceFittings:
            fittings.update(filteringSettings.allianceFittings)
        if filteringSettings.onlyWithSkillsFor:
            withSkillsFor = {}
            for eachFittingID, eachFitting in fittings.iteritems():
                if self.fittingSvc.HasSkillForFit(eachFitting):
                    withSkillsFor[eachFittingID] = eachFitting

            fittings = withSkillsFor
        if not filteringSettings.filterTextLower and not filteringSettings.onlyShowCurrentShip:
            return fittings
        validFittings = {}
        for fittingID, fitting in fittings.iteritems():
            if filteringSettings.onlyShowCurrentShip and self.currentShipTypeID and fitting.shipTypeID != self.currentShipTypeID:
                continue
            if self.TextMatched(filteringSettings.filterTextLower, fitting):
                validFittings[fittingID] = fitting

        return validFittings

    def TextMatched(self, filterTextLower, fitting):
        if not filterTextLower:
            return True
        if self.MatchedWithFittingName(filterTextLower, fitting):
            return True
        if self.MatchedWithShipOrGroupName(filterTextLower, fitting.shipTypeID):
            return True
        return False

    def MatchedWithShipOrGroupName(self, filterTextLower, shipTypeID):
        try:
            shipTypeName = evetypes.GetName(shipTypeID)
        except evetypes.TypeNotFoundException:
            return False

        matchedWithShipName = shipTypeName.lower().find(filterTextLower) >= 0
        if matchedWithShipName:
            return True
        try:
            shipGroupName = evetypes.GetGroupName(shipTypeID)
        except evetypes.TypeNotFoundException:
            return False

        return shipGroupName.lower().find(filterTextLower) >= 0

    def MatchedWithFittingName(self, filterTextLower, fitting):
        foundTextInFittingName = fitting.name.lower().find(filterTextLower) >= 0
        return foundTextInFittingName

    def GetShipsAndGroups(self, filteringSettings, fittings):
        fittingsByGroupID = defaultdict(list)
        fittingsByGroupAndRaceIDs = defaultdict(lambda : defaultdict(set))
        if not filteringSettings.ownerFilterIsSet:
            shipGroups, shipsByGroupID, shipsByGroupAndRaceIDs = self.GetAllShipGroupsAndShipsByGroupID(filteringSettings)
        else:
            shipGroups = set()
            shipsByGroupID = defaultdict(set)
            shipsByGroupAndRaceIDs = defaultdict(lambda : defaultdict(set))
        unsupportedFittings = []
        for fittingID, fitting in fittings.iteritems():
            shipTypeID = fitting.shipTypeID
            if not evetypes.Exists(shipTypeID):
                log.LogError('Ship in stored fittings does not exist, shipID=%s, fittingID=%s' % (shipTypeID, fittingID))
                unsupportedFittings.append(fitting)
                continue
            if not evetypes.IsPublished(shipTypeID):
                unsupportedFittings.append(fitting)
                continue
            groupID = evetypes.GetGroupID(shipTypeID)
            if shipTypeID in self.specialTypeIDs:
                groupID = -groupID
            fittingsByGroupID[groupID].append(fitting)
            groupName = evetypes.GetGroupName(shipTypeID)
            shipGroups.add((groupName, groupID))
            raceID = self._GetShipRaceID(shipTypeID)
            shipsByGroupAndRaceIDs[groupID][raceID].add(shipTypeID)
            fittingsByGroupAndRaceIDs[groupID][raceID].add(fitting)

        return (fittingsByGroupID,
         shipsByGroupID,
         shipGroups,
         shipsByGroupAndRaceIDs,
         fittingsByGroupAndRaceIDs,
         unsupportedFittings)

    def _GetShipRaceID(self, shipTypeID):
        factionID = evetypes.GetFactionID(shipTypeID)
        raceID = appConst.raceByFaction.get(factionID, NON_EMPIRE)
        return raceID

    def GetAllShipGroupsAndShipsByGroupID(self, filteringSettings):
        shipGroups = set()
        shipsByGroupID = defaultdict(set)
        shipsByGroupAndRaceIDs = defaultdict(lambda : defaultdict(set))
        marketGroups = sm.GetService('marketutils').GetMarketGroups()
        grouplist = marketGroups[appConst.marketCategoryShips][:]
        grouplist.extend(self._GetStructureGroups(marketGroups))
        shipTypesIDsFromMarket = {i for i in itertools.chain.from_iterable([ x.types for x in grouplist ])}
        godma = sm.GetService('godma')
        for shipTypeID in shipTypesIDsFromMarket:
            if filteringSettings.filterTextLower and not self.MatchedWithShipOrGroupName(filteringSettings.filterTextLower, shipTypeID):
                continue
            if filteringSettings.onlyShowCurrentShip and self.currentShipTypeID != shipTypeID:
                continue
            if filteringSettings.onlyWithSkillsFor and not godma.CheckSkillRequirementsForType(shipTypeID):
                continue
            groupID = evetypes.GetGroupID(shipTypeID)
            if shipTypeID in self.specialTypeIDs:
                groupID = -groupID
            groupName = evetypes.GetGroupName(shipTypeID)
            shipGroups.add((groupName, groupID))
            shipsByGroupID[groupID].add(shipTypeID)
            raceID = self._GetShipRaceID(shipTypeID)
            shipsByGroupAndRaceIDs[groupID][raceID].add(shipTypeID)

        return (shipGroups, shipsByGroupID, shipsByGroupAndRaceIDs)

    def _GetStructureGroups(self, marketGroups):
        structureGroups = []
        groupsToFind = [MARKET_GROUP_ENGINEERING_COMPLEX,
         MARKET_GROUP_CITADEL,
         MARKET_GROUP_REFINERY,
         MARKET_GROUP_NAVIGATION_STRUCTURES]
        for m in marketGroups[appConst.marketCategoryStarBaseStructures]:
            if m.marketGroupID in groupsToFind:
                structureGroups.append(m)

        return structureGroups

    def GetShipGroupSubContent(self, nodedata, *args):
        scrolllist = []
        fittingsByType = defaultdict(list)
        fittingNumByTypeID = nodedata.fittingNumByTypeID
        for fitting in nodedata.fittings:
            shipTypeID = fitting.shipTypeID
            if not evetypes.Exists(shipTypeID):
                log.LogError('Ship in stored fittings does not exist, shipID=%s, fittingID=%s' % (shipTypeID, fitting.fittingID))
                continue
            fittingsByType[shipTypeID].append(fitting)

        showCommunityFits = nodedata.showCommunityFits
        godmaSvc = sm.GetService('godma')
        allShips = nodedata.allShips
        sublevel = nodedata.sublevel + 1
        for typeID in allShips:
            typeName = evetypes.GetName(typeID)
            numFittingForType = fittingNumByTypeID[typeID]
            fittingsForType = fittingsByType.get(typeID, [])
            entry = self.GetShipTypeGroup(typeID, typeName, fittingsForType, numFittingForType, sublevel, showCommunityFits)
            metaGroupID = evetypes.GetMetaGroupID(typeID)
            scrolllist.append(((metaGroupID, typeName), entry))

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def GetShipTypeGroup(self, typeID, typeName, fittingsForType, numFittingForType, sublevel, showCommunityFits = False):
        numPersonal = numFittingForType[FITTING_OWNER_PERSONAL]
        numCorp = numFittingForType[FITTING_OWNER_CORP]
        numCommunity = numFittingForType[FITTING_OWNER_COMMUNITY]
        numAlliance = numFittingForType[FITTING_OWNER_ALLIANCE]
        label = '<b>%s</b>' % typeName
        data = {'label': label,
         'typeID': typeID,
         'getIcon': True,
         'sublevel': sublevel,
         'maxLines': 2,
         'GetSubContent': self.GetFittingSubContent,
         'id': ('FittingShipTypeListGroup', typeID),
         'showlen': 0,
         'typeName': typeName,
         'fittings': fittingsForType,
         'numPersonal': numPersonal,
         'numCorp': numCorp,
         'numCommunity': numCommunity,
         'numAlliance': numAlliance,
         'showCommunityFits': showCommunityFits,
         'isCurrentShipType': typeID == self.currentShipTypeID}
        data.update(self.GetCommonGroupData(''))
        return GetFromClass(FittingShipTypeListGroup, data)

    def GetFittingSubContent(self, nodedata, *args):
        return self.GetFittingEntriesForType(nodedata.fittings)

    def GetFittingEntriesForType(self, fittings, sublevel = 3, *args):
        scrolllist = []
        for eachFitting in fittings:
            fittingName = eachFitting.name
            if eachFitting.ownerID == session.corpid:
                fittingOwnerType = FITTING_OWNER_CORP
            elif eachFitting.ownerID == appConst.COMMUNITY_FITTING_CORP:
                fittingOwnerType = FITTING_OWNER_COMMUNITY
            elif eachFitting.ownerID == session.allianceid:
                fittingOwnerType = FITTING_OWNER_ALLIANCE
            else:
                fittingOwnerType = FITTING_OWNER_PERSONAL
            sortBy = (fittingOwnerType, fittingName.lower())
            entry = GetFromClass(FittingEntry, {'label': fittingName,
             'fittingID': eachFitting.fittingID,
             'fitting': eachFitting,
             'ownerID': eachFitting.ownerID,
             'showinfo': 1,
             'showicon': 'hide',
             'sublevel': sublevel,
             'ignoreRightClick': 1,
             'OnClick': self.OnFittingClicked,
             'OnDropData': self.onDropDataFunc,
             'GetMenu': self.GetFittingMenu,
             'ownerType': fittingOwnerType})
            scrolllist.append((sortBy, entry))

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def OnFittingClicked(self, entry, *args):
        if uicore.uilib.Key(uiconst.VK_SHIFT) or uicore.uilib.Key(uiconst.VK_CONTROL):
            return
        fitting = entry.sr.node.fitting
        typesInUse = {x[0] for x in fitting.fitData}
        obsoleteSubSystems = {x for x in typesInUse if evetypes.GetGroupID(x) == appConst.groupElectronicSubSystems}
        if obsoleteSubSystems:
            self.fittingSvc.DisplayFitting(fitting)
        else:
            self.ghostFittingSvc.SimulateFitting(fitting)

    def GetFittingMenu(self, entry):
        node = entry.sr.node
        selectedNodes = node.scroll.GetSelectedNodes(node)
        multiSelected = len(selectedNodes) > 1
        fittingID = entry.sr.node.fittingID
        ownerID = entry.sr.node.ownerID
        maxShipsAllowed = GetMaxShipsToFit(sm.GetService('machoNet'))
        m = []
        if not multiSelected:
            m += [(GetByLabel('UI/Fitting/FittingWindow/ViewFitting'), self.ViewFitting, [node])]
            m += [(GetByLabel('UI/Fitting/FittingWindow/SimulateFitting'), self.OnFittingClicked, [entry])]
            if not IsControllingStructure() and evetypes.GetCategoryID(node.fitting.shipTypeID) != appConst.categoryStructure:
                m += [(MenuLabel('UI/Fitting/FittingWindow/FitFittingToActiveShip'), self.FitToActiveShip, [ownerID, fittingID])]
            m += [(MenuLabel('UI/Market/MarketQuote/BuyAll'), self.BuyItemsForFit, [node.fitting])]
            if maxShipsAllowed and IsDocked():
                m += [(MenuLabel('UI/Fitting/FittingWindow/FittingManagement/OpenMultifit'), self.DoBulkFit, [entry])]
            if session.role & ROLE_WORLDMOD:
                fittingSpawner = sm.GetService('fittingspawner')
                m.append(None)
                m.append(('DEV Hax This Together!', fittingSpawner.SpawnFitting, [ownerID, node.fitting]))
                m.append(('DEV: fittingID=%s' % fittingID, blue.pyos.SetClipboardData, (str(fittingID),)))
        m += [None]
        deletable = GetDeletableNodes(selectedNodes)
        if deletable:
            m += [(MenuLabel('UI/Fitting/FittingWindow/FittingManagement/DeleteFitting'), self.DeleteFitting, [entry, deletable])]
        return m

    def DeleteFitting(self, entry, selectedNodes):
        DeleteFittings(selectedNodes)

    def DoBulkFit(self, entry):
        fitting = entry.sr.node.fitting
        OpenOrLoadMultiFitWnd(fitting)

    def ViewFitting(self, node):
        fitting = node.fitting
        self.fittingSvc.DisplayFitting(fitting)

    def PopulatedSpecialEditionShips(self):
        if self.specialTypeIDs is None:
            specialCategory = sm.GetService('marketutils').GetMarketGroup(MARKET_GROUP_SPECIAL_SHIPS)
            typeIDs = set()
            for eachGroup in specialCategory:
                typeIDs.update(eachGroup.types)

            self.specialTypeIDs = typeIDs

    def FitToActiveShip(self, ownerID, fittingID):
        self.fittingSvc.LoadFittingFromFittingIDAndGetBuyOptionOnFailure(ownerID, fittingID)

    def BuyItemsForFit(self, fitting):
        shipTypeID = fitting.shipTypeID
        fitData = fitting.fitData
        from shipfitting.multiBuyUtil import BuyFit
        BuyFit(shipTypeID, fitData)


class ShipParentGroup(Group):

    def Load(self, node):
        Group.Load(self, node)
        containesMyShip = node.isGroupForCurrentShip
        if containesMyShip:
            self.sr.expander.icon.ignoreColorBlindMode = False
            self.sr.expander.SetRGBA(0.0, 0.5, 0.0, 0.8)


class FittingShipTypeListGroup(Group):
    iconSize = 32
    default_iconSize = iconSize
    isDragObject = True

    def Startup(self, *etc):
        Group.Startup(self, etc)
        self.sr.myShipSelection = Fill(name='myShipSelection', bgParent=self, padding=(0, 1, 0, 1), color=(0.0, 0.5, 0.0, 0.1))
        self.sr.myShipSelection.display = False
        self.sr.label.maxLines = 2
        self.sr.label.align = uiconst.TOPLEFT
        self.sr.label.top = 2
        self.techIcon = Sprite(name='techIcon', parent=self, left=1, width=16, height=16, idx=0)
        self.ConstructFittingIcons()
        iconSize = 24
        switchCont = Container(name='switchCont', parent=self, align=uiconst.TORIGHT, width=iconSize, padRight=4)
        simulateBtn = ShipFittingSimulationButton(parent=switchCont, align=uiconst.CENTERLEFT, pos=(0,
         0,
         iconSize,
         iconSize), func=self.SimulateShip, iconSize=iconSize)
        simulateBtn.hint = GetByLabel('UI/Fitting/FittingWindow/SimulateShip')

    def ConstructFittingIcons(self):
        self.fittingIconCont = Container(name='fittingIconCont', parent=self, align=uiconst.TOBOTTOM_NOPUSH, height=12, state=uiconst.UI_PICKCHILDREN, padBottom=2)
        self.personalCont = Container(name='personalCont', parent=self.fittingIconCont, align=uiconst.TOLEFT, width=40)
        personalSprite = Sprite(parent=self.personalCont, align=uiconst.CENTERLEFT, pos=(0, 0, 12, 12), texturePath='res:/UI/Texture/WindowIcons/member.png', state=uiconst.UI_NORMAL)
        self.personalLabel = EveLabelMedium(parent=self.personalCont, text='0', align=uiconst.CENTERLEFT, left=personalSprite.width + 2, state=uiconst.UI_NORMAL)
        personalSprite.hint = self.personalLabel.hint = GetByLabel('UI/Fitting/FittingWindow/SavedPersonalFittings')
        self.corpCont = Container(name='corpCont', parent=self.fittingIconCont, align=uiconst.TOLEFT, width=40)
        corpSprite = Sprite(parent=self.corpCont, align=uiconst.CENTERLEFT, pos=(0, 0, 9, 9), texturePath='res:/UI/Texture/classes/FlagIcon/2.png', state=uiconst.UI_NORMAL)
        self.corpLabel = EveLabelMedium(parent=self.corpCont, text='0', align=uiconst.CENTERLEFT, left=corpSprite.width + 2, state=uiconst.UI_NORMAL)
        corpSprite.hint = self.corpLabel.hint = GetByLabel('UI/Fitting/FittingWindow/SavedCorpFittings')
        self.communityCont = Container(name='communityCont', parent=self.fittingIconCont, align=uiconst.TOLEFT, width=40)
        communitySprite = Sprite(parent=self.communityCont, align=uiconst.CENTERLEFT, pos=(0, 0, 12, 12), texturePath='res:/UI/Texture/classes/Fitting/iconCommunityFitsSmall.png', state=uiconst.UI_NORMAL)
        self.communityLabel = EveLabelMedium(parent=self.communityCont, text='0', align=uiconst.CENTERLEFT, left=communitySprite.width + 2, state=uiconst.UI_NORMAL)
        communitySprite.hint = self.communityLabel.hint = GetByLabel('UI/Fitting/FittingWindow/SavedCommunityFittings')
        self.allianceCont = Container(name='allianceCont', parent=self.fittingIconCont, align=uiconst.TOLEFT, width=40)
        allianceSprite = Sprite(parent=self.allianceCont, align=uiconst.CENTERLEFT, pos=(0, 0, 12, 12), texturePath='res:/UI/Texture/classes/Fitting/iconAllianceSmall.png', state=uiconst.UI_NORMAL)
        self.allianceLabel = EveLabelMedium(parent=self.allianceCont, text='0', align=uiconst.CENTERLEFT, left=allianceSprite.width + 2, state=uiconst.UI_NORMAL)
        allianceSprite.hint = self.allianceLabel.hint = GetByLabel('UI/Fitting/FittingWindow/SavedAllianceFittings')

    def Load(self, node):
        Group.Load(self, node)
        typeID = node.typeID
        self.sr.icon.LoadIconByTypeID(typeID=typeID, size=self.iconSize, ignoreSize=True, isCopy=False)
        self.sr.icon.SetSize(self.iconSize, self.iconSize)
        techSprite = uix.GetTechLevelIcon(self.techIcon, 1, typeID)
        self.techIcon.left = self.sr.icon.left
        labelLeft = self.sr.icon.left + self.sr.icon.width + 4
        self.sr.label.left = labelLeft
        self.fittingIconCont.padLeft = labelLeft
        numPersonal = node.numPersonal
        if numPersonal:
            self.personalLabel.text = numPersonal
        self.personalCont.display = bool(numPersonal)
        numCorp = node.numCorp
        if numCorp:
            self.corpLabel.text = numCorp
        self.corpCont.display = bool(numCorp)
        numCommunity = node.numCommunity
        if numCommunity:
            self.communityLabel.text = numCommunity
        self.communityCont.display = bool(numCommunity) and bool(node.showCommunityFits)
        numAlliance = node.numAlliance
        if numAlliance:
            self.allianceLabel.text = numAlliance
        self.allianceCont.display = bool(numCorp)
        self.sr.myShipSelection.display = node.isCurrentShipType

    def SimulateShip(self):
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        shipTypeID = self.sr.node.typeID
        ghostFittingSvc.SimulateFitting(KeyVal(shipTypeID=shipTypeID, fitData=[]))

    def GetHeight(self, *args):
        node, _ = args
        textwidth, textheight = EveLabelMedium.MeasureTextSize(node.label, maxLines=2)
        node.height = max(textheight + 6, HEIGHT_NORMAL)
        return node.height

    def GetMenu(self):
        typeID = self.sr.node.typeID
        return GetMenuService().GetMenuFromItemIDTypeID(None, typeID, includeMarketDetails=True)

    def GetDragData(self):
        typeID = self.sr.node.typeID
        keyVal = KeyVal(__guid__='listentry.GenericMarketItem', typeID=typeID, label=evetypes.GetName(typeID))
        return [keyVal]

    def LoadTooltipPanel(self, tooltipPanel, *args):
        node = self.sr.node
        typeID = node.typeID
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelLarge(text='<b>%s</b>' % evetypes.GetName(typeID))
        numFittingOwners = bool(node.numPersonal) + bool(node.numCorp) + bool(node.numCommunity) + bool(node.numAlliance)
        useShortText = numFittingOwners >= 2
        if useShortText:
            tooltipPanel.AddLabelMedium(text='<b>%s</b>' % GetByLabel('UI/Fitting/FittingWindow/SavedFittings'))
        numAndPaths = [(node.numPersonal, 'UI/Fitting/FittingWindow/PersonalFittingsNum', 'UI/Fitting/FittingWindow/PersonalFittingsNumShort'), (node.numCorp, 'UI/Fitting/FittingWindow/CorpFittingsNum', 'UI/Fitting/FittingWindow/CorpFittingsNumShort')]
        if node.showCommunityFits:
            numAndPaths += [(node.numCommunity, 'UI/Fitting/FittingWindow/CommunityFittingsNum', 'UI/Fitting/FittingWindow/CommunityFittingsNumShort')]
        if session.allianceid:
            numAndPaths += [(node.numAlliance, 'UI/Fitting/FittingWindow/AllianceFittingsNum', 'UI/Fitting/FittingWindow/AllianceFittingsNumShort')]
        for numFittings, longPath, shortPath in numAndPaths:
            if not numFittings:
                continue
            labelPath = shortPath if useShortText else longPath
            text = GetByLabel(labelPath, numFittings=numFittings)
            tooltipPanel.AddLabelMedium(text=text)

        if not numFittingOwners:
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Fitting/FittingWindow/NoFittingsSaved'))
        if HasTraits(typeID):
            tooltipPanel.AddSpacer(width=300, height=1)
            TraitsContainer(parent=tooltipPanel, typeID=typeID, padding=7)
