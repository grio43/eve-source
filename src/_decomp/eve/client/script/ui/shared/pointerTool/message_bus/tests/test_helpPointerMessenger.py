#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\message_bus\tests\test_helpPointerMessenger.py
from eve.client.script.ui.shared.pointerTool.message_bus.helpPointerMessenger import HelpPointerMessenger
from testsuites.testcases import ClientTestCase
from mock import MagicMock

class TestHelpPointerMessengerCompatibility(ClientTestCase):

    def setUp(self):
        super(TestHelpPointerMessengerCompatibility, self).setUp()
        self.mb = HelpPointerMessenger(MagicMock())

    def test_pointer_created(self):
        pointer_unique_name = 'eve'
        source_location = 1
        self.mb.pointer_created(pointer_unique_name, source_location)

    def test_link_created(self):
        pointer_unique_name = 'eve'
        self.mb.link_created(pointer_unique_name)
