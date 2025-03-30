#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\messagebus\test_uiMessenger.py
import datetime
from testsuites.testcases import ClientTestCase
from mock import MagicMock
from eve.client.script.parklife.messagebus.uiMessenger import UIMessenger

class TestUIMessengerCompatibility(ClientTestCase):

    def setUp(self):
        super(TestUIMessengerCompatibility, self).setUp()
        self.messenger = UIMessenger(MagicMock())

    def test_idle_threshold_reached(self):
        threshold = datetime.timedelta(minutes=5)
        self.messenger.idle_threshold_reached(threshold)

    def test_activity_resumed(self):
        self.messenger.activity_resumed()
