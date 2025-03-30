#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\fleetupUI\fleetRegisterController.py
from evefleet.fleetAdvertObject import FleetAdvertCreationObject
from signals import Signal

class FleetRegisterController(object):

    def __init__(self):
        self.on_load_basic = Signal(signalName='on_load_basic')
        self.on_load_advanced = Signal(signalName='on_load_advanced')
        self.on_advanced_saved = Signal(signalName='on_advanced_saved')
        self._currentAd = None

    @property
    def currentAd(self):
        if self._currentAd is None:
            fleetAd = sm.GetService('fleet').GetCurrentAdvertForMyFleet()
            if not fleetAd:
                fleetAd = FleetAdvertCreationObject()
            self._currentAd = fleetAd
        return self._currentAd

    @currentAd.setter
    def currentAd(self, fleetAd):
        self._currentAd = fleetAd

    def HasCurrentAd(self):
        return self._currentAd is not None
