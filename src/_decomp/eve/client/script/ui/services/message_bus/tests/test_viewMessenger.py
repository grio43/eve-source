#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\message_bus\tests\test_viewMessenger.py
from mock import MagicMock
from testsuites.testcases import ClientTestCase
from eve.client.script.ui.services.message_bus.viewMessenger import ViewMessenger

class TestUIMessengerCompatibility(ClientTestCase):

    def setUp(self):
        super(TestUIMessengerCompatibility, self).setUp()
        self.mb = ViewMessenger(MagicMock())

    def test_view_activated(self):
        view_name = 'view'
        self.mb.view_activated(view_name)

    def test_view_deactivated(self):
        view_name = 'view'
        seconds_active = 1
        nanoseconds_active = 1
        self.mb.view_deactivated(view_name, seconds_active, nanoseconds_active)
