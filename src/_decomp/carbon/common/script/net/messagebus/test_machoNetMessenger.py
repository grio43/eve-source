#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\messagebus\test_machoNetMessenger.py
from unittest import TestCase
from mock import MagicMock
from carbon.common.script.net.messagebus.machoNetMessenger import MachoNetMessenger

class TestMachoNetMessengerCompatibility(TestCase):

    def setUp(self):
        self.mb = MachoNetMessenger(MagicMock())

    def test_shutdown_requested(self):
        self.mb.shutdown_requested()
