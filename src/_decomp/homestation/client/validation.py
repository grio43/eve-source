#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\validation.py
import signals
import threadutils
from carbon.common.script.sys.serviceManager import ServiceManager
from eve.common.script.sys import idCheckers
from homestation.session import get_docked_id, get_global_session
from homestation.validation import is_remote_change, SelfDestructCloneValidatorBase

def is_remote(station_id):
    home_station_service = ServiceManager.Instance().GetService('home_station')
    return is_remote_change(new_home_station_id=station_id, docked_id=get_docked_id(get_global_session()), school_hq_id=home_station_service.get_school_hq_id())


class SelfDestructCloneValidator(SelfDestructCloneValidatorBase):
    __notifyevents__ = ('OnSessionChanged',)

    def __init__(self, session, home_station_service, godma_service):
        self.session = session
        self.home_station_service = home_station_service
        self.godma_service = godma_service
        self.on_invalidated = signals.Signal()
        self.home_station_service.on_home_station_changed.connect(self._on_home_station_changed)
        ServiceManager.Instance().RegisterNotify(self)

    @property
    def in_capsule(self):
        ship_item = self.godma_service.GetItem(self.session.shipid)
        if ship_item is not None:
            return idCheckers.IsCapsule(ship_item.groupID)
        else:
            return False

    @property
    def docked_id(self):
        return get_docked_id(self.session)

    @property
    def home_station_id(self):
        return self.home_station_service.get_home_station().id

    @threadutils.threaded
    def _on_home_station_changed(self):
        self.on_invalidated()

    @threadutils.threaded
    def OnSessionChanged(self, is_remote, session, change):
        if any((name in change for name in ('shipid', 'stationid', 'structureid'))):
            self.on_invalidated()
