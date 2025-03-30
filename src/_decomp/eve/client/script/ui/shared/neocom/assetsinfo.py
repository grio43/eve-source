#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\assetsinfo.py
import blue
import localization
import uthread
from carbon.common.script.sys import service
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.shared.assetsWindow import AssetsWindow
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from playerprogression.assetnetworthnotifier import AssetNetWorthNotifier
from playerprogression.plexprogressionnotifier import PlexProgressionNotifier

class AssetsSvc(service.Service):
    __exportedcalls__ = {'SetHint': []}
    __guid__ = 'svc.assets'
    __notifyevents__ = ['OnSessionChanged',
     'OnItemChange',
     'OnItemNameChange',
     'OnPostCfgDataChanged']
    __servicename__ = 'assets'
    __displayname__ = 'Assets Client Service'
    __dependencies__ = []
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.LogInfo('Starting Assets')
        self.locationCache = {}
        self.SetupAssetNetWorthNotifier()
        self.SetupPlexProgressionNotifier()

    def SetupAssetNetWorthNotifier(self):
        self.assetNetWorthNotifier = AssetNetWorthNotifier()
        self.SubscribeAssetNetWorthWatcher = self.assetNetWorthNotifier.register_subscriber
        self.UnsubscribeAssetNetWorthWatcher = self.assetNetWorthNotifier.unregister_subscriber

    def SetupPlexProgressionNotifier(self):
        self.plexWorthNotifier = PlexProgressionNotifier()
        self.SubscribePlexWorthWatcher = self.plexWorthNotifier.register_subscriber
        self.UnsubscribePlexWorthWatcher = self.plexWorthNotifier.unregister_subscriber

    def Stop(self, memStream = None):
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            wnd.Close()

    def OnSessionChanged(self, isremote, session, change):
        if session.charid is None:
            self.Stop()
        else:
            wnd = self.GetWnd()
            if wnd and not wnd.destroyed:
                uthread.new(wnd.ReconstructLayout)

    def OnItemChange(self, item, change, location):
        itemLocationIDs = [item.locationID]
        if const.ixLocationID in change:
            itemLocationIDs.append(change[const.ixLocationID])
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            if change.keys() == [const.ixLocationID] and change.values() == [0]:
                return
            if idCheckers.IsStation(item.locationID) or const.ixLocationID in change and idCheckers.IsStation(change[const.ixLocationID]):
                key = wnd.tabGroup.GetSelectedArgs()
                if key is not None:
                    if key[:7] == 'station':
                        if idCheckers.IsSolarSystem(item.locationID) and const.ixLocationID in change and change[const.ixLocationID] == eve.session.stationid:
                            return
                        if eve.session.stationid in itemLocationIDs:
                            wnd.tabGroup.ReloadVisible()
                    elif key in ('allitems', 'regitems', 'conitems', 'sysitems'):
                        uthread.new(wnd.UpdateLite, item.locationID, key, change.get(const.ixLocationID, item.locationID))

    def OnItemNameChange(self, *args):
        wnd = self.GetWnd(0)
        if wnd:
            wnd.ReconstructLayout()

    def Show(self, stationID = None):
        wnd = self.GetWnd(1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()
            if stationID is not None:
                wnd.tabGroup.ShowPanelByName(localization.GetByLabel('UI/Inventory/AssetsWindow/AllItems'))
                blue.pyos.synchro.Yield()
                for entry in wnd.sr.scroll.GetNodes():
                    if entry.__guid__ == 'listentry.Group':
                        if entry.id == ('assetslocations_allitems', stationID):
                            uicore.registry.SetListGroupOpenState(('assetslocations_allitems', stationID), 1)
                            wnd.sr.scroll.PrepareSubContent(entry)
                            wnd.sr.scroll.ShowNodeIdx(entry.idx)

    def OnPostCfgDataChanged(self, what, data):
        if what == 'evelocations':
            wnd = self.GetWnd()
            if wnd is not None and not wnd.destroyed and wnd.key and wnd.key[:7] == 'station':
                wnd.tabGroup.ReloadVisible()

    def GetAll(self, key, keyID = None, sortKey = 0):
        stations = self.GetStations()
        sortlocations = []
        mapSvc = sm.StartService('map')
        for station in stations:
            blue.pyos.BeNice()
            solarsystemID = station.solarSystemID
            loc = self.locationCache.get(solarsystemID, None)
            if loc is None:
                constellationID = mapSvc.GetParent(solarsystemID)
                loc = self.locationCache.get(constellationID, None)
                if loc is None:
                    regionID = mapSvc.GetParent(constellationID)
                    loc = (solarsystemID, constellationID, regionID)
                else:
                    regionID = loc[2]
                self.locationCache[solarsystemID] = loc
                self.locationCache[constellationID] = loc
                self.locationCache[regionID] = loc
            else:
                constellationID = loc[1]
                regionID = loc[2]
            if key == 'allitems':
                sortlocations.append((cfg.evelocations.Get(station.stationID).name, (solarsystemID, station)))
            elif key == 'sysitems':
                if solarsystemID == (keyID or eve.session.solarsystemid2):
                    sortlocations.append((cfg.evelocations.Get(station.stationID).name, (solarsystemID, station)))
            elif key == 'conitems' and constellationID == (keyID or eve.session.constellationid):
                sortlocations.append((cfg.evelocations.Get(station.stationID).name, (solarsystemID, station)))
            elif key == 'regitems' and regionID == (keyID or eve.session.regionid):
                sortlocations.append((cfg.evelocations.Get(station.stationID).name, (solarsystemID, station)))

        sortlocations = SortListOfTuples(sortlocations)
        return sortlocations

    def GetStations(self):
        stations = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStations()
        primeloc = []
        for station in stations:
            primeloc.append(station.stationID)

        if len(primeloc):
            cfg.evelocations.Prime(primeloc)
        return stations

    def GetWnd(self, new = 0):
        if new:
            return AssetsWindow.Open()
        return AssetsWindow.GetIfOpen()

    def SetHint(self, hintstr = None):
        wnd = self.GetWnd()
        if wnd is not None:
            wnd.SetHint(hintstr)
