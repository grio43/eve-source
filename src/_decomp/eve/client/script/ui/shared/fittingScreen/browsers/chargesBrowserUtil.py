#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\browsers\chargesBrowserUtil.py
import evetypes
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from menu import MenuLabel
from carbonui.primitives.line import Line
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.shared.fittingScreen import BROWSER_SEARCH_CHARGE, AMMO_FAVORITE_CONFIG
from eve.client.script.ui.shared.fittingScreen.settingUtil import GetAllAmmoFavorites
from eve.client.script.ui.shared.market.entries import GetHintWithAvgPrice
from eve.common.lib import appConst as const
from fsdBuiltData.common.iconIDs import GetIconFile
from localization import GetByLabel
import metaGroups
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.line import Line as ListentryLine
import carbonui.const as uiconst
import blue
from eveservices.menu import GetMenuService

class ChargeBrowserListProvider(object):

    def __init__(self, dblClickFunc, onDropDataFunc, reloadFunc):
        self.dblClickFunc = dblClickFunc
        self.onDropDataFunc = onDropDataFunc
        self.reloadFunc = reloadFunc

    def GetChargesScrollList(self, moduleTypeID, chargeTypeIDs):
        godma = sm.GetService('godma')
        scrolllist = []
        factionChargeIDs = set()
        otherChargeIDs = set()
        for eachTypeID in chargeTypeIDs:
            metaGroup = evetypes.GetMetaGroupID(eachTypeID)
            if metaGroup == const.metaGroupFaction:
                factionChargeIDs.add(eachTypeID)
            else:
                otherChargeIDs.add(eachTypeID)

        if chargeTypeIDs:
            scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self._GetFavoritesContent,
             'label': GetByLabel('UI/Fitting/FittingWindow/FavoriteAmmo'),
             'id': ('ammobrowser', 'favorites'),
             'showlen': 0,
             'chargeTypeIDs': chargeTypeIDs,
             'sublevel': 0,
             'showicon': 'hide',
             'state': 'locked',
             'BlockOpenWindow': True,
             'DropData': self._DropOnFavorites,
             'moduleTypeID': moduleTypeID}))
            scrolllist.append(GetFromClass(HorizontalLine, {'height': 2}))
        scrolllist += self._GetScrollListFromTypeList(moduleTypeID, otherChargeIDs)
        if factionChargeIDs:
            scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self._GetAmmoSubContent,
             'label': metaGroups.get_name(const.metaGroupFaction),
             'id': ('ammobrowser', 'factionChargeIDs'),
             'showlen': 0,
             'chargeTypeIDs': factionChargeIDs,
             'sublevel': 0,
             'showicon': GetIconFile(metaGroups.get_icon_id(const.metaGroupFaction)),
             'state': 'locked',
             'BlockOpenWindow': True,
             'moduleTypeID': moduleTypeID}))
        return scrolllist

    def _GetFavoritesContent(self, nodedata, *args):
        moduleTypeID = nodedata.moduleTypeID
        typeIDs = nodedata.chargeTypeIDs
        favoriteChargeIDs = set()
        allFavorites = GetAllAmmoFavorites()
        for eachTypeID in typeIDs:
            if eachTypeID in allFavorites:
                favoriteChargeIDs.add(eachTypeID)

        return self._GetScrollListFromTypeList(moduleTypeID, favoriteChargeIDs, sublevel=1, isFavorite=True)

    def _GetAmmoSubContent(self, nodedata, *args):
        moduleTypeID = nodedata.moduleTypeID
        typeIDs = nodedata.chargeTypeIDs
        return self._GetScrollListFromTypeList(moduleTypeID, typeIDs, sublevel=1)

    def _GetScrollListFromTypeList(self, moduleTypeID, chargeTypeIDs, sublevel = 0, isFavorite = False):
        scrolllist = []
        for eachTypeID in chargeTypeIDs:
            label = evetypes.GetName(eachTypeID)
            techLevel = evetypes.GetTechLevel(eachTypeID)
            scrolllist.append(((techLevel, label), GetFromClass(ChargeItem, {'label': label,
              'typeID': eachTypeID,
              'itemID': None,
              'getIcon': 1,
              'OnDropData': self.onDropDataFunc,
              'OnDblClick': (self.dblClickFunc, moduleTypeID, eachTypeID),
              'sublevel': sublevel,
              'GetMenu': self._GetChargeMenu,
              'isFavorite': isFavorite,
              'ignoreRightClick': True})))

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def _GetChargeMenu(self, entry, *args):
        node = entry.sr.node
        typeID = entry.typeID
        selectedNodes = node.scroll.GetSelectedNodes(node)
        removableTypeIDs = set()
        notRemovableTypeIDs = set()
        for eachNode in selectedNodes:
            if node.get('isFavorite', False):
                removableTypeIDs.add(eachNode.typeID)
            else:
                notRemovableTypeIDs.add(eachNode.typeID)

        m = []
        if notRemovableTypeIDs:
            m += [(MenuLabel('UI/Fitting/FittingWindow/AddToFavorites'), self._AddToFavorite, (notRemovableTypeIDs,))]
        if removableTypeIDs:
            m += [(MenuLabel('UI/Fitting/FittingWindow/RemoveFromFavorites'), self._RemoveFromFavorite, (removableTypeIDs,))]
        if len(selectedNodes) == 1:
            m += GetMenuService().GetMenuFromItemIDTypeID(None, typeID, includeMarketDetails=True)
        return m

    def _RemoveFromFavorite(self, removableTypeIDs):
        allFavoritesSet = GetAllAmmoFavorites()
        for eachTypeID in removableTypeIDs:
            allFavoritesSet.discard(eachTypeID)

        settings.user.ui.Set(AMMO_FAVORITE_CONFIG, allFavoritesSet)
        self.reloadFunc()

    def _AddToFavorite(self, typeIDsSet):
        allFavoritesSet = GetAllAmmoFavorites()
        allFavoritesSet.update(typeIDsSet)
        settings.user.ui.Set(AMMO_FAVORITE_CONFIG, allFavoritesSet)
        self.reloadFunc()

    def _DropOnFavorites(self, dragObj, nodes):
        typeIDs = set()
        for eachNode in nodes:
            try:
                if not IsCharge(eachNode.typeID):
                    continue
                typeIDs.add(eachNode.typeID)
            except:
                continue

        self._AddToFavorite(typeIDs)


def IsCharge(typeID):
    return evetypes.GetCategoryID(typeID) == const.categoryCharge


class HorizontalLine(ListentryLine):

    def ApplyAttributes(self, attributes):
        ListentryLine.ApplyAttributes(self, attributes)
        Line(parent=self, align=uiconst.TOTOP, color=(1, 1, 1, 0.07))


def GetValidChargeTypeIDs(typeList, searchFittingHelper, hwSettingObject = None):
    filterString = settings.user.ui.Get(BROWSER_SEARCH_CHARGE, '').lower()
    ret = set()
    for typeID in typeList:
        try:
            blue.pyos.BeNice()
            if not filterString or filterString in searchFittingHelper.GetTypeName(typeID):
                ret.add(typeID)
        except Exception:
            pass

    return ret


def GetValidSpecialAssetsChargeTypeIDs(typeList, searchFittingHelper, hwSettingObject = None):
    validTypeIDs = set()
    for typeID in typeList:
        try:
            if searchFittingHelper.IsCharge(typeID):
                validTypeIDs.add(typeID)
        except Exception:
            pass

    return GetValidChargeTypeIDs(validTypeIDs, searchFittingHelper, hwSettingObject)


class ChargeItem(Item):

    def GetHint(self):
        return GetHintWithAvgPrice(self.sr.node)
