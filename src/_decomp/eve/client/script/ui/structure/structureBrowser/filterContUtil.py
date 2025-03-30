#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\filterContUtil.py
import eve.client.script.ui.structure.structureBrowser.browserUIConst as browserUIConst
import evetypes
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.filter import OptionObject
from eve.common.script.sys.idCheckers import IsWormholeRegion
from localization import GetByLabel
import log
STATION_TYPE_CONFIGID = -const.categoryStation

def GetStructureOptions(includeStations = True):
    OPTION_CATEGORYID = 1
    OPTION_TYPEID = 2
    structureOptions = []
    for groupID, groupContent in browserUIConst.STRUCTURES_BY_GROUPS.iteritems():
        subOptions = []
        for labelTypeID, typeIDs in groupContent:
            label = evetypes.GetName(labelTypeID)
            subOptions += [OptionObject(label, typeIDs, OPTION_TYPEID)]

        categoryName = GetStructureTypeGroupName(groupID)
        if categoryName is None:
            log.LogTraceback('Invalid structure group?')
            continue
        structureOptions += [(categoryName, OptionObject(categoryName, groupID, OPTION_CATEGORYID, subOptions))]

    structureOptions = SortListOfTuples(structureOptions)
    if includeStations:
        stationsText = GetByLabel('UI/StructureBrowser/StationsAndOutposts')
        structureOptions.insert(0, OptionObject(stationsText, [STATION_TYPE_CONFIGID], OPTION_CATEGORYID))
    return structureOptions


def GetServiceOptions(sortedOptions):
    OPTION_SERVICE = 1
    serviceOptions = []
    for data in sortedOptions:
        serviceOptions += [OptionObject(data.label, data.name, OPTION_SERVICE)]

    return serviceOptions


def GetLocationOptions():
    locationOptions = []
    if not IsWormholeRegion(session.regionid):
        locationOptions += [const.rangeRegion, const.rangeConstellation]
    locationOptions += [const.rangeSolarSystem]
    return locationOptions


def IsFilteredOutByText(structureController, filterText):
    if filterText:
        text = structureController.GetFilterText()
        if text.find(filterText) == -1:
            return True
    return False


def IsFilteredOutByServices(structureController, filterContController):
    if filterContController.AreServiceFiltersDisbled():
        return False
    structureServicesChecked = filterContController.GetServicesChecked()
    for serviceID in structureServicesChecked:
        if structureController.HasService(serviceID):
            return False

    return True


def GetStructureTypeGroupName(groupID):
    if groupID > 0:
        return evetypes.GetGroupNameByGroup(groupID)
    namePath = browserUIConst.SPECIAL_GROUPNAME_PATHS_BY_GROUPID.get(groupID)
    if not namePath:
        return
    return GetByLabel(namePath)
