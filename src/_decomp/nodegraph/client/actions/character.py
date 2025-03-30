#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\character.py
from .base import Action

class SetHomeStation(Action):
    atom_id = 416

    def start(self, **kwargs):
        import homestation.client
        super(SetHomeStation, self).start(**kwargs)
        if session.stationid and homestation.Service.instance().get_home_station().id != session.stationid:
            homestation.set_home_station(session.stationid)
