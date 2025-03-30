#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\quote.py
import sys
import blue
import carbonui.const as uiconst
import evetypes
import localization
import locks
import structures
import utillib
from carbon.common.lib.const import DAY, MIN
from carbon.common.script.sys.row import Row
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_GMH
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.format import FmtAmt, FmtDate
from carbonui.uicore import uicore
from eve.client.script.ui.shared.market.buyThisTypeWindow import MarketActionWindow
from eve.client.script.ui.shared.market.marketbase import RegionalMarket
from eve.client.script.ui.util import uix, utilWindows
from eve.common.lib.appConst import locationTemp, locationSystem
from eve.common.script.sys import idCheckers
from eve.common.script.sys.idCheckers import IsStation
from eve.common.script.util.eveFormat import FmtISK
from eveexceptions import UserError
from inventorycommon.const import containerGlobal
from inventoryrestrictions import can_view_market_details
from marketgroups.data import get_market_group_ids, get_market_group_parent_id, MarketGroupObject
from marketutil.const import rangeRegion, rangeStation, rangeSolarSystem

class MarketUtils(Service):
    __guid__ = 'svc.marketutils'
    __servicename__ = 'Market Utils'
    __displayname__ = 'Market Utils'
    __dependencies__ = []
    __notifyevents__ = ['OnShowMarketDetails', 'ProcessUIRefresh']

    def __init__(self):
        super(MarketUtils, self).__init__()
        self.marketgroups = None
        self.allgroups = None
        self.regionUpAt = None
        self.marketTypeIDFinder = None

    def Run(self, memStream = None):
        self.Reset()

    def Reset(self):
        self.marketgroups = None
        self.allgroups = None
        self.regionUpAt = None

    def ProcessUIRefresh(self):
        self.Reset()

    def StartupCheck(self):
        now = blue.os.GetWallclockTime()
        if self.regionUpAt is not None:
            if self.regionUpAt.time < now - 2 * MIN:
                return
            raise UserError(self.regionUpAt.msg, self.regionUpAt.dict)
        try:
            sm.ProxySvc('marketProxy').StartupCheck()
        except UserError as e:
            if eve.session.role & ROLE_GMH == 0:
                self.regionUpAt = Row(['time', 'msg', 'dict'], [now, e.msg, e.dict])
            sys.exc_clear()
            raise UserError(e.msg, e.dict)

    @staticmethod
    def GetMarketRange():
        if session.stationid or session.structureid:
            r = settings.user.ui.Get('marketRangeFilterStation', rangeRegion)
        else:
            r = settings.user.ui.Get('marketRangeFilterSpace', rangeRegion)
        return r

    @staticmethod
    def SetMarketRange(value):
        if eve.session.stationid or session.structureid:
            r = settings.user.ui.Set('marketRangeFilterStation', value)
        else:
            r = settings.user.ui.Set('marketRangeFilterSpace', value)
        return r

    def BuyStationAsk(self, typeID):
        if eve.session.stationid:
            asks = sm.GetService('marketQuote').GetStationAsks()
            for ask in asks.itervalues():
                if ask.typeID == typeID:
                    self.Buy(typeID, ask)
                    return

    def FindMarketGroup(self, typeID, groupInfo = None, trace = None):
        groupInfo = groupInfo or self.GetMarketGroups()[None]
        trace = trace or ''
        for _groupInfo in groupInfo:
            if typeID in _groupInfo.types:
                trace += _groupInfo.marketGroupName.strip() + ' / '
                if not _groupInfo.hasTypes:
                    return self.FindMarketGroup(typeID, self.GetMarketGroups()[_groupInfo.marketGroupID], trace)
                else:
                    return (_groupInfo, trace)

        return (None, trace)

    def ProcessRequest(self, subMethod, typeID = None, orderID = None):
        if subMethod == 'Buy':
            self.Buy(typeID, orderID)
        elif subMethod == 'ShowMarketDetails':
            self.ShowMarketDetails(typeID, orderID)
        else:
            raise RuntimeError('Unsupported subMethod call. Possible h4x0r attempt.')

    def MatchOrder(self, typeID, orderID):
        order = None
        if orderID:
            order = sm.GetService('marketQuote').GetOrder(orderID, typeID)
        self.Buy(typeID, order, placeOrder=order is None)

    @staticmethod
    def ShowMarketDetails(typeID, orderID = None, silently = False):
        marketWnd = RegionalMarket.GetIfOpen()
        if marketWnd and not marketWnd.destroyed:
            stack = marketWnd.GetStack()
            if not silently or stack and stack.GetActiveWindow() != marketWnd or marketWnd.IsMinimized():
                marketWnd.Maximize()
        else:
            uicore.cmd.OpenMarket()
        marketWnd = RegionalMarket.GetIfOpen()
        if marketWnd:
            marketWnd.LoadTypeID_Ext(typeID)

    def AddMarketDetailsMenuOption(self, menuEntries, typeID):
        from carbonui.control.contextMenu.menuEntryData import MenuEntryData
        from menu import MenuLabel
        menuEntries.append(MenuEntryData(MenuLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'), lambda : self.ShowMarketDetails(typeID=typeID), internalName='ViewMarketDetails', typeID=typeID))

    def ShowMarketGroupWithTypes(self, marketGroupID):
        groupListData = self.GetMarketGroupByID(marketGroupID)
        if not groupListData.hasTypes:
            raise RuntimeError('Opening non-hasType market group. This can be too types for the market to handle')
        marketWnd = RegionalMarket.GetIfOpen()
        if marketWnd:
            marketWnd.LoadMarketGroup(marketGroupID)
        else:
            RegionalMarket.Open(marketGroupID=marketGroupID)

    def AddTypesToMarketGroups(self):
        typeIDsByMktGrp = {}

        def ExtractTypes(marketGroups, groupID):
            ids = {}
            if groupID not in marketGroups:
                return {}
            for gr in marketGroups[groupID]:
                explicits = {}
                for typeID in evetypes.GetTypeIDsByMarketGroup(gr.marketGroupID):
                    blue.pyos.BeNice()
                    if evetypes.IsPublished(typeID):
                        explicits[typeID] = 1

                subids = ExtractTypes(marketGroups, gr.marketGroupID)
                subids.update(explicits)
                gr.types = subids.keys()
                typeIDsByMktGrp[gr.marketGroupID] = explicits.keys()
                ids.update(subids)

            return ids

        try:
            ExtractTypes(self.marketgroups, None)
        finally:
            ExtractTypes = None

    def GetMarketGroups(self):
        with locks.TempLock('PrimeMarketGroups'):
            if self.marketgroups is None:
                self.marketgroups = {}
                self.marketGroupsByID = {}
                for marketGroupID in get_market_group_ids():
                    parentID = get_market_group_parent_id(marketGroupID)
                    marketGroup = MarketGroupObject(marketGroupID)
                    if marketGroupID not in self.marketgroups:
                        self.marketgroups[marketGroupID] = []
                    if parentID not in self.marketgroups:
                        self.marketgroups[parentID] = [marketGroup]
                    else:
                        self.marketgroups[parentID].append(marketGroup)
                    self.marketGroupsByID[marketGroupID] = marketGroup

                self.AddTypesToMarketGroups()
        return self.marketgroups

    def GetMarketTypes(self):
        t = []
        for each in self.GetMarketGroups()[None]:
            t += each.types

        return t

    def GetMarketTypeIDFinder(self):
        with locks.TempLock('GetMarketTypeIDFinder'):
            if self.marketTypeIDFinder is None:
                typeIDs = self.GetMarketTypes()
                from textImporting.textToTypeIDFinder import TextToTypeIDFinder
                from textImporting import IsUsingDefaultLanguage
                usingDefaultLanguage = IsUsingDefaultLanguage(session)
                self.marketTypeIDFinder = TextToTypeIDFinder(typeIDs, usingDefaultLanguage)
        return self.marketTypeIDFinder

    def GetMarketGroup(self, findMarketGroupID):
        allGroups = self.GetMarketGroups()
        return allGroups.get(findMarketGroupID, None)

    def GetMarketGroupByID(self, marketGroupID):
        self.GetMarketGroups()
        return self.marketGroupsByID[marketGroupID]

    @staticmethod
    def AllowTrade(order = None, locationID = None):
        limits = sm.GetService('marketQuote').GetSkillLimits(None)
        bidLimit = limits['bid']
        if session.structureid or session.stationid:
            if locationID != session.solarsystemid2:
                pass
            return True
        if bidLimit == rangeStation and order is None:
            raise UserError('CustomError', {'error': localization.GetByLabel('UI/Market/MarketQuote/OutOfRange')})

    def Buy(self, typeID, order = None, duration = 1, placeOrder = 0, prePickedLocationID = None, ignoreAdvanced = False, quantity = 1):
        locationID = None
        self.AllowTrade(order)
        if order is None:
            if prePickedLocationID:
                locationID = prePickedLocationID
            elif eve.session.stationid:
                locationID = session.stationid
            elif session.structureid:
                locationID = session.structureid
            else:
                stationData = sm.GetService('marketutils').PickStation()
                if stationData:
                    locationID = stationData
            if locationID is None:
                return
        sm.GetService('marketutils').StartupCheck()
        if locationID is None and order.stationID is not None:
            locationID = order.stationID
        wnd = MarketActionWindow.Open()
        advancedBuyWnd = settings.char.ui.Get('advancedBuyWnd', 0)
        if uicore.uilib.Key(uiconst.VK_SHIFT) or placeOrder or advancedBuyWnd and not ignoreAdvanced:
            wnd.LoadBuy_Detailed(typeID, order, duration, locationID, forceRange=True, quantity=quantity)
        else:
            if locationID is not None:
                sm.GetService('marketQuote').RefreshJumps(typeID, locationID)
            wnd.TradeSimple(typeID=typeID, order=order, locationID=locationID, ignoreAdvanced=ignoreAdvanced, quantity=quantity)
        uicore.registry.SetFocus(wnd)

    def ModifyOrder(self, order):
        if not self.HasAccessToMarketAtLocation(order.stationID):
            raise UserError(structures.GetAccessErrorLabel(structures.SETTING_MARKET_TAX), {'structureName': cfg.evelocations.Get(order.stationID).locationName})
        wnd = MarketActionWindow.Open(windowID='marketmodifyaction')
        wnd.LoadModify(order)

    @staticmethod
    def HasAccessToMarketAtLocation(dockableLocationID):
        if idCheckers.IsStation(dockableLocationID):
            return True
        return sm.GetService('structureSettings').CharacterHasService(dockableLocationID, structures.SERVICE_MARKET)

    @staticmethod
    def CancelOffer(order):
        if eve.Message('CancelMarketOrder', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        sm.GetService('marketQuote').CancelOrder(order.orderID, order.regionID)

    @staticmethod
    def PickStation():
        if not session.solarsystemid2:
            return
        structureDirectory = sm.GetService('structureDirectory')
        markets = structureDirectory.GetMarketDockableLocationsInRegion()
        quote = sm.GetService('marketQuote')
        uiService = sm.GetService('ui')
        limits = quote.GetSkillLimits(None)
        bidDistance = limits['bid']
        marketsToList = []
        for marketID in markets:
            distance = quote.GetStationDistance(marketID)
            if distance <= bidDistance:
                if IsStation(marketID):
                    stationInfo = cfg.stations.Get(marketID)
                    stationTypeID = stationInfo.stationTypeID
                    stationName = uiService.GetStationName(marketID)
                    solarsystemID = stationInfo.solarSystemID
                    position = (stationInfo.x, stationInfo.y, stationInfo.z)
                else:
                    structureInfo = structureDirectory.GetStructureInfo(marketID)
                    stationTypeID = structureInfo.typeID
                    stationName = structureInfo.itemName
                    solarsystemID = structureInfo.solarSystemID
                    locationInfo = cfg.evelocations.Get(marketID)
                    position = (locationInfo.x, locationInfo.y, locationInfo.z)
                marketsToList.append((utillib.KeyVal(stationID=marketID, stationName=stationName, stationTypeID=stationTypeID, solarSystemID=solarsystemID, x=position[0], y=position[1], z=position[2]), distance))

        if len(marketsToList) == 0:
            return
        for each, distance in marketsToList:
            itemID = each.stationID
            if itemID not in cfg.evelocations:
                staData = [itemID,
                 each.stationName,
                 each.solarSystemID,
                 each.x,
                 each.y,
                 each.z,
                 None]
                cfg.evelocations.Hint(itemID, staData)

        headers = [localization.GetByLabel('UI/Common/LocationTypes/Station'), localization.GetByLabel('UI/Market/Marketbase/Jumps')]
        stationLst = []
        for station, distance in marketsToList:
            data = utillib.KeyVal()
            data.label = '%s<t>%s' % (cfg.evelocations.Get(station.stationID).name, distance)
            data.listvalue = station.stationID
            data.showinfo = 1
            data.typeID = station.stationTypeID
            data.itemID = station.stationID
            data.Set('sort_' + headers[1], distance)
            stationLst.append(data)

        station = uix.ListWnd(stationLst, 'pickStation', localization.GetByLabel('UI/Search/SelectStation'), hint=localization.GetByLabel('UI/Market/MarketQuote/ChouseStation'), isModal=1, ordered=0, scrollHeaders=headers, minw=450)
        if station:
            return station

    def PickItem(self, typeID, quantity = None):
        stations = sm.GetService('invCache').GetInventory(containerGlobal).ListStations()
        primeloc = []
        for station in stations:
            primeloc.append(station.stationID)

        if len(primeloc):
            cfg.evelocations.Prime(primeloc)
        else:
            return None
        stationLst = [ (cfg.evelocations.Get(station.stationID).name + ' (' + str(station.itemCount) + ' items)', station.stationID) for station in stations ]
        station = uix.ListWnd(stationLst, 'generic', localization.GetByLabel('UI/Search/SelectStation'), hint=localization.GetByLabel('UI/Market/MarketQuote/SellFromStations'), isModal=1)
        if station:
            items = sm.GetService('invCache').GetInventory(containerGlobal).ListStationItems(station[1])
            badLocations = [locationTemp, locationSystem, eve.session.charid]
            valid = []
            for each in items:
                if each.typeID != typeID:
                    continue
                if idCheckers.IsJunkLocation(each.locationID) or each.locationID in badLocations:
                    continue
                if each.stacksize == 0 or each.stacksize < quantity:
                    continue
                valid.append(each)

            if len(valid) == 1:
                return valid[0]
            scrolllist = []
            for each in valid:
                scrolllist.append(('%s<t>%s' % (evetypes.GetName(each.typeID), FmtAmt(each.stacksize)), each))

            if not scrolllist:
                if eve.Message('CustomQuestion', {'header': localization.GetByLabel('UI/Market/MarketQuote/headerTryAnotherStation'),
                 'question': localization.GetByLabel('UI/Market/MarketQuote/NoItemsAtStations', typeID=typeID, stationName=station[0])}, uiconst.YESNO) == uiconst.ID_YES:
                    return self.PickItem(typeID, quantity)
                return None
            item = uix.ListWnd(scrolllist, 'generic', localization.GetByLabel('UI/Search/SelectItem'), hint=localization.GetByLabel('UI/Market/MarketQuote/SelectItemsToSell'), isModal=1, scrollHeaders=[localization.GetByLabel('UI/Common/Type'), localization.GetByLabel('UI/Common/Quantity')])
            if item:
                return item[1]

    @staticmethod
    def GetFuncMaps():
        return {StripTags(localization.GetByLabel('UI/Common/Type'), stripOnly=['localized']): 'GetType',
         StripTags(localization.GetByLabel('UI/Common/Quantity'), stripOnly=['localized']): 'GetQuantity',
         StripTags(localization.GetByLabel('UI/Market/MarketQuote/headerPrice'), stripOnly=['localized']): 'GetPrice',
         StripTags(localization.GetByLabel('UI/Common/Location'), stripOnly=['localized']): 'GetLocation',
         StripTags(localization.GetByLabel('UI/Common/Station'), stripOnly=['localized']): 'GetStation',
         StripTags(localization.GetByLabel('UI/Common/LocationTypes/Region'), stripOnly=['localized']): 'GetRegion',
         StripTags(localization.GetByLabel('UI/Common/Range'), stripOnly=['localized']): 'GetRange',
         StripTags(localization.GetByLabel('UI/Market/MarketQuote/HeaderMinVolumn'), stripOnly=['localized']): 'GetMinVolume',
         StripTags(localization.GetByLabel('UI/Market/Marketbase/ExpiresIn'), stripOnly=['localized']): 'GetExpiresIn',
         StripTags(localization.GetByLabel('UI/Market/MarketQuote/headerIssuedBy'), stripOnly=['localized']): 'GetIssuedBy',
         StripTags(localization.GetByLabel('UI/Market/Marketbase/Jumps'), stripOnly=['localized']): 'GetJumps',
         StripTags(localization.GetByLabel('UI/Market/MarketQuote/headerWalletDivision'), stripOnly=['localized']): 'GetWalletDivision'}

    @staticmethod
    def GetJumps(record, data):
        sortJumps = record.jumps
        if record.jumps == 0:
            if record.stationID in (session.stationid, session.structureid):
                data.label += '%s<t>' % localization.GetByLabel('UI/Common/LocationTypes/Station')
                sortJumps = -1
            else:
                data.label += '%s<t>' % localization.GetByLabel('UI/Common/LocationTypes/System')
        elif record.jumps == 1000000:
            data.label += '%s<t>' % localization.GetByLabel('UI/Common/LocationTypes/Unreachable')
        else:
            data.label += '<right>%i<t>' % record.jumps
        data.Set('sort_%s' % localization.GetByLabel('UI/Market/Marketbase/Jumps'), sortJumps)

    @staticmethod
    def GetWalletDivision(record, data):
        data.label += '%s <t>' % sm.GetService('corp').GetDivisionNames()[record.keyID - 1000 + 8]

    @staticmethod
    def GetPrice(record, data):
        data.label += "<right><color='0xFFFFFFFF'>%s</color></right><t>" % FmtISK(record.price)
        data.Set('sort_%s' % localization.GetByLabel('UI/Market/MarketQuote/headerPrice'), record.price)

    @staticmethod
    def GetType(record, data):
        name = evetypes.GetNameOrNone(record.typeID)
        if name is not None:
            data.label += name + '<t>'
            data.Set('sort_%s' % localization.GetByLabel('UI/Common/Type'), name.lower())
        else:
            data.label += localization.GetByLabel('UI/Market/MarketQuote/UnknowenTypeError', typeIDText=str(record.typeID)) + '<t>'
            data.Set('sort_%s' % localization.GetByLabel('UI/Common/Type'), localization.GetByLabel('UI/Market/MarketQuote/UnknowenTypeError', typeIDText=str(record.typeID)))

    @staticmethod
    def GetLocation(record, data):
        locationName = cfg.evelocations.Get(record.stationID).name
        data.label += locationName + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Location'), locationName.lower())

    @staticmethod
    def GetStation(record, data):
        locationName = cfg.evelocations.Get(record.stationID).name
        data.label += locationName + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Station'), locationName.lower())

    @staticmethod
    def GetExpiresIn(record, data):
        exp = record.issueDate + record.duration * DAY - blue.os.GetWallclockTime()
        if exp < 0:
            data.label += '%s<t>' % localization.GetByLabel('UI/Market/MarketQuote/Expired')
        else:
            data.label += FmtDate(exp, 'ss') + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Market/Marketbase/ExpiresIn'), record.issueDate + record.duration * DAY)

    @staticmethod
    def GetQuantity(record, data):
        data.label += '<right>%s<t>' % FmtAmt(int(record.volRemaining))
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Quantity'), int(record.volRemaining))

    @staticmethod
    def GetQuantitySlashVolume(record, data):
        data.label += '<right>%s/%s<t>' % (FmtAmt(int(record.volRemaining)), FmtAmt(int(record.volEntered)))
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Quantity'), (int(record.volRemaining), record.volEntered))

    @staticmethod
    def GetMinVolume(record, data):
        vol = int(min(record.volRemaining, record.minVolume))
        data.label += '<right>%s<t>' % FmtAmt(vol)
        data.Set('sort_%s' % localization.GetByLabel('UI/Market/MarketQuote/HeaderMinVolumn'), vol)

    @staticmethod
    def GetSolarsystem(record, data):
        solarsystemName = cfg.evelocations.Get(record.solarSystemID).name
        data.label += solarsystemName + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'), solarsystemName.lower())

    @staticmethod
    def GetRegion(record, data):
        regionName = cfg.evelocations.Get(record.regionID).name
        data.label += regionName + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/LocationTypes/Region'), regionName.lower())

    @staticmethod
    def GetConstellation(record, data):
        constellationName = cfg.evelocations.Get(record.constellationID).name
        data.label += constellationName + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/LocationTypes/Constellation'), constellationName.lower())

    @staticmethod
    def GetRange(record, data):
        if record.range == rangeStation:
            rangeText = localization.GetByLabel('UI/Common/LocationTypes/Station')
            sortval = 0
        elif record.range == rangeSolarSystem:
            rangeText = localization.GetByLabel('UI/Common/LocationTypes/SolarSystem')
            sortval = 0.5
        elif record.range == rangeRegion:
            rangeText = localization.GetByLabel('UI/Common/LocationTypes/Region')
            sortval = sys.maxint
        else:
            rangeText = localization.GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=record.range)
            sortval = record.range
        data.label += rangeText + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Range'), sortval)

    @staticmethod
    def GetIssuedBy(record, data):
        name = cfg.eveowners.Get(record.charID).name
        data.label += name + '<t>'
        data.Set('sort_%s' % localization.GetByLabel('UI/Market/MarketQuote/headerIssuedBy'), name.lower())

    def GetFilterops(self, marketGroupID):
        mg = self.GetMarketGroups()
        ret = []
        for level1 in mg[marketGroupID]:
            ret.append((level1.marketGroupName, level1.marketGroupID))

        ret.sort()
        ret.insert(0, (localization.GetByLabel('UI/Market/MarketQuote/All'), None))
        return ret

    def GetTypeFilterIDs(self, marketGroupID, checkcategory = 1):
        c = []
        mg = self.GetMarketGroups()[marketGroupID]
        if mg:
            for each in mg:
                for typeID in each.types:
                    groupID = evetypes.GetGroupID(typeID)
                    if checkcategory:
                        categoryID = evetypes.GetCategoryID(typeID)
                        if categoryID not in c:
                            c.append(categoryID)
                    elif groupID not in c:
                        c.append(groupID)

        else:
            typeIDs = evetypes.GetTypeIDsByMarketGroup(marketGroupID)
            for typeID in typeIDs:
                if checkcategory:
                    categoryID = evetypes.GetCategoryID(typeID)
                    if categoryID not in c:
                        c.append(categoryID)
                groupID = evetypes.GetGroupID(typeID)
                if not checkcategory and groupID not in c:
                    c.append(groupID)

        return c

    @staticmethod
    def GetProducableGroups(lineGroups, lineCategs):
        valid = [ group.groupID for group in lineGroups ]
        validcategs = [ categ.categoryID for categ in lineCategs ]
        return (valid, validcategs)

    @staticmethod
    def GetProducableCategories(lineGroups, lineCategs):
        valid = [ categ.categoryID for categ in lineCategs ]
        for group in lineGroups:
            categoryID = evetypes.GetCategoryIDByGroup(group.groupID)
            if categoryID not in valid:
                valid.append(categoryID)

        return valid

    @staticmethod
    def GetBestMatchText(price, averagePrice, percentage):
        if price < averagePrice:
            aboveBelow = 'UI/Market/MarketQuote/PercentBelow'
            color = '<color=0xff00ff00>'
        else:
            aboveBelow = 'UI/Market/MarketQuote/PercentAbove'
            color = '<color=0xffff5050>'
        p = {'colorText': color,
         'percentage': round(100 * percentage, 2),
         'aboveBelow': localization.GetByLabel(aboveBelow),
         'colorTextEnd': '</color>'}
        return localization.GetByLabel('UI/Market/MarketQuote/BuyQuantity', **p)

    def AddTypeToQuickBar(self, typeID, parentID = 0, fromMarket = False, extraText = ''):
        if typeID is None:
            return
        self.AddToQuickBar(typeID, parentID, fromMarket=fromMarket, extraText=extraText)

    @staticmethod
    def AddToQuickBar(typeID, parent = 0, fromMarket = False, scatter = True, extraText = ''):
        evetypes.RaiseIFNotExists(typeID)
        dynamicItemSvc = sm.GetService('dynamicItemSvc')
        if dynamicItemSvc.IsDynamicItem(typeID) or not can_view_market_details(typeID):
            raise UserError('cannotTradeOnMarket', {'typeID': typeID})
        current = settings.user.ui.Get('quickbar', {})
        lastid = settings.user.ui.Get('quickbar_lastid', 0)
        for _, data in current.items():
            if data.parent == parent and data.label == typeID:
                return None

        n = utillib.KeyVal()
        n.parent = parent
        n.id = lastid + 1
        n.label = typeID
        n.extraText = extraText
        lastid += 1
        settings.user.ui.Set('quickbar_lastid', lastid)
        current[n.id] = n
        settings.user.ui.Set('quickbar', current)
        if scatter:
            sm.ScatterEvent('OnMarketQuickbarChange', fromMarket=fromMarket)

    @staticmethod
    def AddNewQuickbarFolder(folderID = 0, *args):
        folderNameLabel = localization.GetByLabel('UI/Market/Marketbase/FolderName')
        typeFolderNameLabel = localization.GetByLabel('UI/Market/Marketbase/TypeFolderName')
        ret = utilWindows.NamePopup(folderNameLabel, typeFolderNameLabel, maxLength=20)
        if ret is not None:
            current = settings.user.ui.Get('quickbar', {})
            lastid = settings.user.ui.Get('quickbar_lastid', 0)
            lastid += 1
            n = utillib.KeyVal()
            n.parent = folderID
            n.id = lastid
            n.label = ret
            current[n.id] = n
            settings.user.ui.Set('quickbar', current)
            settings.user.ui.Set('quickbar_lastid', lastid)
            sm.ScatterEvent('OnMarketQuickbarChange')
            return n

    def OnShowMarketDetails(self, typeID):
        self.ShowMarketDetails(typeID, silently=True)
