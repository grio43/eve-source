#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\session.py
from .base import Event

class ShipBoarded(Event):
    atom_id = 133
    __notifyevents__ = ['ProcessActiveShipChanged']

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        self.invoke(item_id=shipID, old_item_id=oldShipID)


class LocationChanged(Event):
    atom_id = 173
    __notifyevents__ = ['OnSessionChanged']

    def OnSessionChanged(self, is_remote, session, change):
        if 'locationid' in change:
            previous_location_id, location_id = change['locationid']
            self.invoke(location_id=location_id, previous_location_id=previous_location_id)


class GameLoaded(Event):
    atom_id = 232
    __notifyevents__ = ['OnIntroCompleted']

    def OnIntroCompleted(self):
        self.invoke()


class DeathTransitionEnded(Event):
    atom_id = 267
    __notifyevents__ = ['OnDeathTransitionEnded']

    def OnDeathTransitionEnded(self):
        self.invoke()


class ClientReady(Event):
    atom_id = 630
    __notifyevents__ = ['OnClientReady']

    def OnClientReady(self, *args):
        self.invoke()
