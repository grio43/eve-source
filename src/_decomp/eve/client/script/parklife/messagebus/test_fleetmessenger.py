#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\messagebus\test_fleetmessenger.py
from testsuites.testcases import ClientTestCase
from mock import MagicMock
from eve.client.script.parklife.messagebus.fleetMessenger import FleetMessenger

class TestFleetMessengerCompatibility(ClientTestCase):

    def setUp(self):
        super(TestFleetMessengerCompatibility, self).setUp()
        self.mb = FleetMessenger(MagicMock())

    def test_fleet_created(self):
        fleet_id = 1
        ui_source = 1
        self.mb.fleet_created(fleet_id, ui_source)

    def test_applied_to_join(self):
        fleet_id = 1
        ui_source = 1
        self.mb.applied_to_join(fleet_id, ui_source)
