#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\browsers\searchBrowser.py
from collections import defaultdict
import localization
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.fittingScreen import BROWSER_SEARCH_CHARGE
from eve.client.script.ui.shared.fittingScreen.browsers.browserUtil import GetTypesByMetaGroups, ShoulAddMetaGroupFolder, GetMetaGroupNameAndEntry, GetScrollListFromTypeListInNodedata, GetScrollListFromTypeList
from eve.client.script.ui.shared.fittingScreen.browsers.chargesBrowserUtil import GetValidChargeTypeIDs
from eve.client.script.ui.shared.fittingScreen.browsers.filtering import GetValidTypeIDs
from eve.client.script.ui.shared.fittingScreen.settingUtil import HardwareFiltersSettingObject
from eve.common.lib import appConst as const
from utillib import KeyVal
specialItemGroups = (const.metaGroupStoryline,
 const.metaGroupFaction,
 const.metaGroupOfficer,
 const.metaGroupDeadspace)

class SearchBrowserListProvider(object):

    def __init__(self, searchFittingHelper, onDropDataFunc, hwSettingObject):
        self.searchFittingHelper = searchFittingHelper
        self.onDropDataFunc = onDropDataFunc
        self.marketGroups = sm.GetService('marketutils').GetMarketGroups()
        self.hwSettingObject = hwSettingObject or HardwareFiltersSettingObject()

    def GetValidTypeIDs(self):
        typeIDs = self.searchFittingHelper.GetSearcableTypeIDs(self.marketGroups)
        validTypeIDs = GetValidTypeIDs(typeIDs, self.searchFittingHelper, self.hwSettingObject)
        return validTypeIDs

    def GetSearchTerm(self):
        return self.hwSettingObject.GetTextFilter()

    def GetSearchResults(self):
        searchTerm = self.GetSearchTerm()
        if not searchTerm:
            return []
        scrollList = []
        validTypeIDs = self.GetValidTypeIDs()
        allMarketGroups = self.marketGroups[None]
        myCategories, typeIDsByCategoryID = self.GetCategoryDicts(allMarketGroups, validTypeIDs)
        if len(typeIDsByCategoryID) > 1:
            scrollList += self.GetSearchCatagoryEntries(typeIDsByCategoryID, myCategories)
        else:
            for categoryID, categoryTypeIDs in typeIDsByCategoryID.iteritems():
                fakeNodeData = KeyVal(typeIDs=categoryTypeIDs, sublevel=-1, categoryID=categoryID)
                results = self.GetSeachCategorySubContent(fakeNodeData)
                scrollList.extend(results)

        return scrollList

    def GetCategoryDicts(self, allMarketGroups, validTypeIDs):
        typeIDsByCategoryID = defaultdict(list)
        myCategories = {}
        for typeID in validTypeIDs:
            topMarketCategory = self.searchFittingHelper.GetMarketCategoryForType(typeID, allMarketGroups)
            if topMarketCategory is None:
                continue
            typeIDsByCategoryID[topMarketCategory.marketGroupID].append(typeID)
            myCategories[topMarketCategory.marketGroupID] = topMarketCategory

        return (myCategories, typeIDsByCategoryID)

    def GetSearchCatagoryEntries(self, typeIDsByCategoryID, myCategories):
        scrollList = []
        for categoryID, categoryTypeIDs in typeIDsByCategoryID.iteritems():
            category = myCategories[categoryID]
            group = GetFromClass(ListGroup, {'GetSubContent': self.GetSeachCategorySubContent,
             'label': category.marketGroupName,
             'id': ('searchGroups', categoryID),
             'showlen': 0,
             'sublevel': 0,
             'state': 'locked',
             'BlockOpenWindow': True,
             'categoryID': category.marketGroupID,
             'typeIDs': categoryTypeIDs,
             'iconID': category.iconID,
             'hint': category.description})
            scrollList.append(group)

        return scrollList

    def GetSeachCategorySubContent(self, nodedata, *args):
        typeIDs = nodedata.typeIDs
        typesByMetaGroupID = GetTypesByMetaGroups(typeIDs)
        categoryID = nodedata.categoryID
        scrollList = []
        for metaGroupID, typeIDList in sorted(typesByMetaGroupID.items()):
            shoulAddMetaGroupFolder = ShoulAddMetaGroupFolder(metaGroupID)
            if shoulAddMetaGroupFolder:
                metaGroupLabelAndEntry = self.GetSearchSubGroup(metaGroupID, typeIDList, nodedata=nodedata, categoryID=categoryID)
                scrollList.append(metaGroupLabelAndEntry)
            else:
                standardTypes = GetScrollListFromTypeList(typeIDList, -1, self.onDropDataFunc)
                for entry in standardTypes:
                    scrollList.append((' %s' % entry.label, entry))

        scrollList = [ item[1] for item in localization.util.Sort(scrollList, key=lambda x: x[0]) ]
        return scrollList

    def GetSearchSubGroup(self, metaGroupID, typeIDList, nodedata = 0, categoryID = None, *args):
        labelAndEntry = GetMetaGroupNameAndEntry(metaGroupID, typeIDList, nodedata, subContentFunc=GetScrollListFromTypeListInNodedata, onDropDataFunc=self.onDropDataFunc, idTuple=('fittingSearchGroups', (metaGroupID, categoryID)))
        return labelAndEntry


class SearchBrowserListProviderCharges(SearchBrowserListProvider):

    def GetValidTypeIDs(self):
        typeIDs = self.searchFittingHelper.GetSearcableChargeTypeIDs(self.marketGroups)
        validTypeIDs = GetValidChargeTypeIDs(typeIDs, self.searchFittingHelper)
        return validTypeIDs

    def GetSearchTerm(self):
        searchTerm = settings.user.ui.Get(BROWSER_SEARCH_CHARGE, '')
        return searchTerm
