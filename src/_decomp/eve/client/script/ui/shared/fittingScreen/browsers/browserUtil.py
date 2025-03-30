#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\browsers\browserUtil.py
from collections import defaultdict
import inventorycommon.const as invConst
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.market.entries import GenericMarketItem, MarketMetaGroupEntry
from menu import MenuLabel
from eve.client.script.ui.shared.fitting.ghostFittingHelpers import TryPreviewFitItemOnMouseAction
import evetypes
from fsdBuiltData.common.iconIDs import GetIconFile
from localization import GetByLabel
from localization.util import Sort
import metaGroups
from eveservices.menu import GetMenuService
from eve.common.lib import appConst as const
BROWSER_WIDTH = 240
validMarketMetaGroups = (const.metaGroupStoryline,
 const.metaGroupFaction,
 const.metaGroupOfficer,
 const.metaGroupDeadspace)
validCategoriesForMetaGroups = (const.categoryModule,
 const.categoryStructureModule,
 const.categoryDrone,
 const.categoryStarbase)
AUTO_FITTED_SERVICES_BY_STRUCTURE_TYPE = {invConst.typeUpwellSmallStargate: invConst.typeStandupStargateEngine,
 invConst.typeUpwellCynosuralSystemJammer: invConst.typeStandupCynosuralJammerI,
 invConst.typeUpwellCynosuralBeacon: invConst.typeStandupCynosuralGeneratorI}

def ShoulAddMetaGroupFolder(metaGroupID):
    if metaGroupID in validMarketMetaGroups:
        return True
    return False


def GetTypesByMetaGroups(typeIDs):
    typesByMetaGroupID = defaultdict(list)
    for typeID in typeIDs:
        if evetypes.GetVariationParentTypeIDOrNone(typeID) is None:
            metaGroupID = None
        else:
            metaGroupID = evetypes.GetMetaGroupID(typeID)
            if metaGroupID == const.metaGroupStoryline:
                metaGroupID = const.metaGroupFaction
        typesByMetaGroupID[metaGroupID].append(typeID)

    return typesByMetaGroupID


def GetMetaGroupNameAndEntry(metaGroupID, typeIDList, nodedata, subContentFunc, onDropDataFunc, idTuple):
    label = _GetLabelForMarketMetaGroup(metaGroupID)
    groupEntry = GetFromClass(MarketMetaGroupEntry, {'GetSubContent': subContentFunc,
     'label': label,
     'id': idTuple,
     'showlen': 0,
     'metaGroupID': metaGroupID,
     'sublevel': nodedata.sublevel + 1,
     'showicon': GetIconFile(metaGroups.get_icon_id(metaGroupID)),
     'state': 'locked',
     'BlockOpenWindow': True,
     'typeIDs': typeIDList,
     'DropData': onDropDataFunc,
     'onDropDataFunc': onDropDataFunc})
    labelAndEntry = (label, groupEntry)
    return labelAndEntry


def _GetLabelForMarketMetaGroup(metaGroupID):
    if metaGroupID in (const.metaGroupStoryline, const.metaGroupFaction):
        label = GetByLabel('UI/Market/FactionAndStoryline')
    else:
        label = metaGroups.get_name(metaGroupID)
    return label


def GetScrollListFromTypeListInNodedata(nodedata, *args):
    invTypeIDs = nodedata.typeIDs
    sublevel = nodedata.sublevel
    onDropDataFunc = nodedata.onDropDataFunc
    return GetScrollListFromTypeList(invTypeIDs, sublevel, onDropDataFunc)


def GetScrollListFromTypeList(invTypeIDs, sublevel, onDropDataFunc):
    subList = []
    for invTypeID in invTypeIDs:
        subList.append((evetypes.GetName(invTypeID), GetFromClass(GenericMarketItem, {'label': evetypes.GetName(invTypeID),
          'sublevel': sublevel + 1,
          'ignoreRightClick': 1,
          'showinfo': 1,
          'typeID': invTypeID,
          'showNameHint': True,
          'OnDropData': onDropDataFunc,
          'GetMenu': GetMenuForNode,
          'OnDblClick': (TryFit, invTypeID)})))

    subList = [ item[1] for item in Sort(subList, key=lambda x: x[0]) ]
    return subList


def GetMenuForNode(node):
    m = [(MenuLabel('UI/Fitting/FittingWindow/FindTypeInBrowser'), sm.ScatterEvent, ('OnFindTypeInList', node.typeID))]
    m += GetMenuService().GetMenuFromItemIDTypeID(None, node.typeID, includeMarketDetails=True)
    return m


def TryFit(entry, invTypeID):
    TryPreviewFitItemOnMouseAction(None, oldWindow=False, force=True)
    ghostFittingSvc = sm.GetService('ghostFittingSvc')
    if evetypes.GetCategoryID(invTypeID) == const.categoryCharge:
        ghostFittingSvc.TryFitFakeAmmoToAllModulesFitted([invTypeID])
    else:
        return ghostFittingSvc.TryFitModuleToOneSlot(invTypeID)
