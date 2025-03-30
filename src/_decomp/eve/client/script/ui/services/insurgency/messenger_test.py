#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\insurgency\messenger_test.py
from testsuites.testcases import ClientTestCase
import mock
from eve.client.script.ui.services.insurgency.messenger import InsurgencyMessenger, SystemData, NoticeData
from eveProto.generated.eve_public.math.fraction_pb2 import Fraction
from eveProto.generated.eve_public.pirate.corruption.api.requests_pb2 import GetSystemInfoRequest as GetSystemCorruptionRequest, GetSystemInfoResponse as GetSystemCorruptionResponse, GetStageThresholdsRequest as GetStageThresholdsCorruptionRequest, GetStageThresholdsResponse as GetStageThresholdsCorruptionResponse
from eveProto.generated.eve_public.pirate.suppression.api.requests_pb2 import GetSystemInfoRequest as GetSystemSuppressionRequest, GetSystemInfoResponse as GetSystemSuppressionResponse, GetStageThresholdsRequest as GetStageThresholdsSuppressionRequest, GetStageThresholdsResponse as GetStageThresholdsSuppressionResponse
from publicGateway.test.public_gateway_mock import new_request_test_row, character_request_test
from eveProto.generated.eve_public.solarsystem.solarsystem_pb2 import Identifier as SolarSystemId
from eveProto.generated.eve_public.pirate.corruption.api.notices_pb2 import IncreasedNotice as CorruptionIncreasedNotice, SetNotice as CorruptionSetNotice, ResetNotice as CorruptionResetNotice
from eveProto.generated.eve_public.pirate.suppression.api.notices_pb2 import IncreasedNotice as SuppressionIncreasedNotice, SetNotice as SuppressionSetNotice, ResetNotice as SuppressionResetNotice
SOLARSYSTEM_ID = 30000001

class TestInsurgencyMessenger(ClientTestCase):

    def test_get_corruption_stages(self):
        respose = GetStageThresholdsCorruptionResponse(thresholds=[Fraction(numerator=1, denominator=2)])
        test_rows = [new_request_test_row(messenger_function_name='_BlockingRequestStageThreasholds', messenger_function_kwargs={'requestClass': GetStageThresholdsCorruptionRequest,
          'responseClass': GetStageThresholdsCorruptionResponse}, expected_request_payload=GetStageThresholdsCorruptionRequest(), response_primitive_dict={'status_code': 200}, response_payload=respose, expected_results=[0.5], expected_exception=None)]
        for test_row in test_rows:
            character_request_test(self, InsurgencyMessenger, test_row)

    def test_get_suppression_stages(self):
        respose = GetStageThresholdsSuppressionResponse(thresholds=[Fraction(numerator=1, denominator=2)])
        test_rows = [new_request_test_row(messenger_function_name='_BlockingRequestStageThreasholds', messenger_function_kwargs={'requestClass': GetStageThresholdsSuppressionRequest,
          'responseClass': GetStageThresholdsSuppressionResponse}, expected_request_payload=GetStageThresholdsSuppressionRequest(), response_primitive_dict={'status_code': 200}, response_payload=respose, expected_results=[0.5], expected_exception=None)]
        for test_row in test_rows:
            character_request_test(self, InsurgencyMessenger, test_row)

    def test_get_corruption_state(self):
        request = GetSystemCorruptionRequest(system=SolarSystemId(sequential=SOLARSYSTEM_ID))
        respose = GetSystemCorruptionResponse(total_progress=Fraction(numerator=10, denominator=20), vanguard_contribution=Fraction(numerator=30, denominator=40), stage=1)
        expectedReturn = SystemData(SOLARSYSTEM_ID, 10, 20, 1, 30, 40)
        test_rows = [new_request_test_row(messenger_function_name='_BlockingRequestSystemCorruption', messenger_function_kwargs={'systemID': SOLARSYSTEM_ID}, expected_request_payload=request, response_primitive_dict={'status_code': 200}, response_payload=respose, expected_results=expectedReturn, expected_exception=None)]
        for test_row in test_rows:
            character_request_test(self, InsurgencyMessenger, test_row)

    def test_get_suppression_state(self):
        request = GetSystemSuppressionRequest(system=SolarSystemId(sequential=SOLARSYSTEM_ID))
        respose = GetSystemSuppressionResponse(total_progress=Fraction(numerator=10, denominator=20), vanguard_contribution=Fraction(numerator=30, denominator=40), stage=1)
        expectedReturn = SystemData(SOLARSYSTEM_ID, 10, 20, 1, 30, 40)
        test_rows = [new_request_test_row(messenger_function_name='_BlockingRequestSystemSuppression', messenger_function_kwargs={'systemID': SOLARSYSTEM_ID}, expected_request_payload=request, response_primitive_dict={'status_code': 200}, response_payload=respose, expected_results=expectedReturn, expected_exception=None)]
        for test_row in test_rows:
            character_request_test(self, InsurgencyMessenger, test_row)

    def test_suppression_subscriptions_called(self):
        messenger = InsurgencyMessenger(mock.Mock())
        messenger.public_gateway.subscribe_to_notice = mock.Mock()
        messenger._GetSuppressionIncreasedCallback = mock.Mock(return_value=1)
        messenger._GetSetCallback = mock.Mock(return_value=2)
        messenger._GetResetCallback = mock.Mock(return_value=3)
        messenger.SubscribeToSuppressionValueUpdates([])
        messenger.public_gateway.subscribe_to_notice.assert_has_calls([mock.call(SuppressionIncreasedNotice, 1), mock.call(SuppressionSetNotice, 2), mock.call(SuppressionResetNotice, 3)], any_order=True)

    def test_corruption_subscriptions_called(self):
        messenger = InsurgencyMessenger(mock.Mock())
        messenger.public_gateway.subscribe_to_notice = mock.Mock()
        messenger._GetCorruptionIncreasedCallback = mock.Mock(return_value=1)
        messenger._GetSetCallback = mock.Mock(return_value=2)
        messenger._GetResetCallback = mock.Mock(return_value=3)
        messenger.SubscribeToCorruptionValueUpdates([])
        messenger.public_gateway.subscribe_to_notice.assert_has_calls([mock.call(CorruptionIncreasedNotice, 1), mock.call(CorruptionSetNotice, 2), mock.call(CorruptionResetNotice, 3)], any_order=True)

    def test_suppression_subscriptions_callback(self):
        messenger = InsurgencyMessenger(mock.Mock())
        notice_to_initalized_notice = {SuppressionIncreasedNotice: SuppressionIncreasedNotice(system=SolarSystemId(sequential=SOLARSYSTEM_ID), new_suppression=Fraction(numerator=1, denominator=5)),
         SuppressionSetNotice: SuppressionSetNotice(system=SolarSystemId(sequential=SOLARSYSTEM_ID), progress=Fraction(numerator=1, denominator=5)),
         SuppressionResetNotice: SuppressionResetNotice(system=SolarSystemId(sequential=SOLARSYSTEM_ID), progress=Fraction(numerator=1, denominator=5))}

        def subscribe_fun(notice, callback):
            callback(notice_to_initalized_notice[notice], notice)

        messenger.public_gateway.subscribe_to_notice = mock.Mock(side_effect=subscribe_fun)

        def assertion_callback(systemID, value):
            expected = NoticeData(newNumerator=1, newDenominator=5, vanguardInstigated=False)
            self.assertEqual(expected, value)
            self.assertEqual(systemID, SOLARSYSTEM_ID)

        messenger.SubscribeToSuppressionValueUpdates(assertion_callback)

    def test_corruption_subscriptions_callback(self):
        messenger = InsurgencyMessenger(mock.Mock())
        notice_to_initalized_notice = {CorruptionIncreasedNotice: CorruptionIncreasedNotice(system=SolarSystemId(sequential=SOLARSYSTEM_ID), new_corruption=Fraction(numerator=1, denominator=5), vanguard=False),
         CorruptionSetNotice: CorruptionSetNotice(system=SolarSystemId(sequential=SOLARSYSTEM_ID), progress=Fraction(numerator=1, denominator=5)),
         CorruptionResetNotice: CorruptionResetNotice(system=SolarSystemId(sequential=SOLARSYSTEM_ID), progress=Fraction(numerator=1, denominator=5))}

        def subscribe_fun(notice, callback):
            callback(notice_to_initalized_notice[notice], notice)

        messenger.public_gateway.subscribe_to_notice = mock.Mock(side_effect=subscribe_fun)

        def assertion_callback(systemID, value):
            expected = NoticeData(newNumerator=1, newDenominator=5, vanguardInstigated=False)
            self.assertEqual(expected, value)
            self.assertEqual(systemID, SOLARSYSTEM_ID)

        messenger.SubscribeToCorruptionValueUpdates(assertion_callback)
