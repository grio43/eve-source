#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\browsers\hardwareBrowser.py
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.fittingScreen.browsers.browserUtil import GetTypesByMetaGroups, ShoulAddMetaGroupFolder, GetMetaGroupNameAndEntry, GetScrollListFromTypeListInNodedata, GetScrollListFromTypeList
from eve.client.script.ui.shared.fittingScreen.browsers.filtering import GetValidTypeIDs
from localization.util import Sort
import telemetry

class HardwareBrowserListProvider(object):

    def __init__(self, searchFittingHelper, onDropDataFunc, validTypeIDsFunc = None, bannedMarketGroups = (), hwSettingObject = None):
        self.searchFittingHelper = searchFittingHelper
        self.onDropDataFunc = onDropDataFunc
        self.validTypeIDsFunc = validTypeIDsFunc or GetValidTypeIDs
        self.hwSettingObject = hwSettingObject
        self.bannedMarketGroups = bannedMarketGroups

    @telemetry.ZONE_METHOD
    def GetGroupListForBrowse(self, nodedata = None, marketGroupID = None, sublevel = 0):
        if nodedata and nodedata.marketGroupInfo.hasTypes:
            scrolllist = self.GetSubfoldersForScrolllist(nodedata)
        else:
            scrolllist = []
            level = sublevel
            if marketGroupID is None and nodedata:
                marketGroupID = nodedata.marketGroupInfo.marketGroupID
                level = nodedata.sublevel + 1
            grouplist = sm.GetService('marketutils').GetMarketGroups()[marketGroupID]
            for marketGroupInfo in grouplist:
                if not len(marketGroupInfo.types):
                    continue
                if marketGroupInfo.marketGroupID in self.bannedMarketGroups:
                    continue
                groupEntry, groupID = GetMarketGroupFromMarketGroupInfo(marketGroupInfo, level, subContentFunc=self.GetGroupListForBrowse, onDropDataFunc=self.onDropDataFunc, searchHelper=self.searchFittingHelper, validTypeIDsFunc=self.validTypeIDsFunc, hwSettingObject=self.hwSettingObject)
                if groupEntry is None:
                    continue
                scrolllist.append(((marketGroupInfo.hasTypes, marketGroupInfo.marketGroupName), groupEntry))

            scrolllist = self.SortScolllist(scrolllist)
        return scrolllist

    def SortScolllist(self, scrolllist):
        scrolllist = [ item for item in Sort(scrolllist, key=lambda x: x[0][1]) ]
        scrolllist = [ item[1] for item in sorted(scrolllist, key=lambda x: x[0][0]) ]
        return scrolllist

    @telemetry.ZONE_METHOD
    def GetSubfoldersForScrolllist(self, nodedata):
        scrolllist = []
        typesByMetaGroupID = GetTypesByMetaGroups(nodedata.typeIDs)
        for metaGroupID, typeIDList in sorted(typesByMetaGroupID.items()):
            if len(typeIDList) == 0:
                continue
            if ShoulAddMetaGroupFolder(metaGroupID):
                marketGroupID = GetMarketGroupID(nodedata)
                labelAndEntry = GetMetaGroupNameAndEntry(metaGroupID, typeIDList, nodedata, subContentFunc=GetScrollListFromTypeListInNodedata, onDropDataFunc=self.onDropDataFunc, idTuple=(marketGroupID, metaGroupID))
                subList = [labelAndEntry[1]]
            else:
                subList = GetScrollListFromTypeList(typeIDList, nodedata.sublevel, nodedata.DropData)
            scrolllist += subList

        return scrolllist


def GetMarketGroupID(nodedata):
    if nodedata is None:
        return
    else:
        return nodedata.marketGroupInfo.marketGroupID


@telemetry.ZONE_METHOD
def GetMarketGroupFromMarketGroupInfo(marketGroupInfo, level, subContentFunc, onDropDataFunc, searchHelper, validTypeIDsFunc, hwSettingObject = None):
    typeIDs = validTypeIDsFunc(marketGroupInfo.types, searchHelper, hwSettingObject)
    if not typeIDs:
        return (None, None)
    if level in (0, 1):
        groupHint = marketGroupInfo.description
    else:
        groupHint = ''
    groupID = (marketGroupInfo.marketGroupName, marketGroupInfo.marketGroupID)
    groupEntry = GetFromClass(ListGroup, {'GetSubContent': subContentFunc,
     'label': marketGroupInfo.marketGroupName,
     'id': groupID,
     'typeIDs': typeIDs,
     'iconMargin': 18,
     'showlen': 0,
     'marketGroupInfo': marketGroupInfo,
     'sublevel': level,
     'state': 'locked',
     'showicon': 'hide' if marketGroupInfo.hasTypes else None,
     'iconID': marketGroupInfo.iconID,
     'selected': False,
     'BlockOpenWindow': 1,
     'hint': groupHint,
     'DropData': onDropDataFunc})
    return (groupEntry, groupID)
