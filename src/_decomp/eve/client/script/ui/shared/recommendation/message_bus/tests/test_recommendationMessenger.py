#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\recommendation\message_bus\tests\test_recommendationMessenger.py
import mock
import time
import unittest
import uuid
from eve.client.script.ui.shared.recommendation.message_bus.recommendationMessenger import RecommendationMessenger
from testsuites.testcases import ClientTestCase
from publicGateway.grpc.test import _safe_tasklet_sleep
from publicGateway.grpc.test.mock_publicGatewaySvc import MockPublicGatewaySvc
has_stackless = False
try:
    import stackless
    has_stackless = True
except ImportError:
    has_stackless = False

class TestHelpPointerMessengerCompatibility(ClientTestCase):

    def setUp(self):
        super(TestHelpPointerMessengerCompatibility, self).setUp()
        self.mb = RecommendationMessenger(mock.MagicMock())
        self.uuid = uuid.uuid4().get_bytes()

    def test_accepted(self):
        operation_id = 1
        self.mb.accepted(operation_id, self.uuid)

    def test_dismissed(self):
        operation_id = 1
        self.mb.dismissed(operation_id, self.uuid)

    def test_displayed(self):
        operation_id = 1
        self.mb.displayed(operation_id, self.uuid)

    @unittest.skip('test fails and needs fixing')
    def test_request_recommendations(self):
        if not has_stackless:
            self.skipTest('there can be no stackless router without stackless')
        mock_add_func = mock.MagicMock()
        self.mb = RecommendationMessenger(MockPublicGatewaySvc())
        self.mb.request_recommendations(1, True, mock_add_func, mock.MagicMock())
        start = time.time()
        while not mock_add_func.called:
            _safe_tasklet_sleep(start, 2)

        mock_add_func.assert_called_once()
