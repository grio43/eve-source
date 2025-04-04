#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\shipConfigSvc.py
import locks
from caching.memoize import Memoize
from carbon.common.script.sys.service import Service
from eve.common.script.net import eveMoniker
from eve.common.script.sys import eveCfg

class ShipConfigSvc(Service):
    __guid__ = 'svc.shipConfig'
    __update_on_reload__ = 1
    __dependencies__ = []
    __notifyevents__ = ['OnSessionChanged']
    __startupdependencies__ = []

    def __init__(self):
        self._ship = None
        self.shipid = None
        self.config = None
        super(self.__class__, self).__init__()

    def Run(self, memstream_which_absolutely_noone_uses_anymore_but_no_one_gets_around_to_remove = None):
        self.shipid = eveCfg.GetActiveShip()

    def _ClearCachedAttributes(self):
        self.shipid = eveCfg.GetActiveShip()
        self.config = None
        self._ship = None

    def OnSessionChanged(self, isRemote, session, change):
        if 'locationid' in change or 'shipid' in change:
            self._ClearCachedAttributes()

    @property
    def ship(self):
        if self._ship is None:
            self._ship = eveMoniker.GetShipAccess()
        return self._ship

    @Memoize(0.25)
    def GetShipConfig(self, shipID = None):
        if shipID is not None:
            return eveMoniker.GetShipAccess().GetShipConfiguration(shipID)
        if eveCfg.GetActiveShip() != self.shipid:
            self._ClearCachedAttributes()
        with locks.TempLock('%s:%s' % (self, self.shipid)):
            if self.config is None:
                self.config = self.ship.GetShipConfiguration(self.shipid)
        return self.config

    def SetShipConfig(self, key, value):
        lock = locks.TempLock('%s:%s' % (self, self.shipid))
        if lock.lockedWhen is not None:
            return
        with lock:
            self.ship.ConfigureShip({key: value})
            self.config[key] = value
            self.GetShipConfig.clear_memoized(self, None)

    def ToggleFleetHangarFleetAccess(self):
        self.SetShipConfig('FleetHangar_AllowFleetAccess', not self.IsFleetHangarFleetAccessAllowed())

    def ToggleFleetHangarCorpAccess(self):
        self.SetShipConfig('FleetHangar_AllowCorpAccess', not self.IsFleetHangarCorpAccessAllowed())

    def ToggleShipMaintenanceBayFleetAccess(self):
        self.SetShipConfig('SMB_AllowFleetAccess', not self.IsShipMaintenanceBayFleetAccessAllowed())

    def ToggleShipMaintenanceBayCorpAccess(self):
        self.SetShipConfig('SMB_AllowCorpAccess', not self.IsShipMaintenanceBayCorpAccessAllowed())

    def IsFleetHangarFleetAccessAllowed(self):
        return self.GetShipConfig()['FleetHangar_AllowFleetAccess']

    def IsFleetHangarCorpAccessAllowed(self):
        return self.GetShipConfig()['FleetHangar_AllowCorpAccess']

    def IsShipMaintenanceBayFleetAccessAllowed(self):
        return self.GetShipConfig()['SMB_AllowFleetAccess']

    def IsShipMaintenanceBayCorpAccessAllowed(self):
        return self.GetShipConfig()['SMB_AllowCorpAccess']
