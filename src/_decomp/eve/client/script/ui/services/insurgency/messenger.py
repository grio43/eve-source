#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\insurgency\messenger.py
from carbon.common.script.util.mathCommon import FloatCloseEnough
from eveProto.generated.eve_public.pirate.corruption.api.notices_pb2 import IncreasedNotice as CorruptionIncreasedNotice, SetNotice as CorruptionSetNotice, ResetNotice as CorruptionResetNotice
from eveProto.generated.eve_public.pirate.suppression.api.notices_pb2 import IncreasedNotice as SuppressionIncreasedNotice, SetNotice as SuppressionSetNotice, ResetNotice as SuppressionResetNotice
from eveProto.generated.eve_public.pirate.corruption.api.requests_pb2 import GetSystemInfoRequest as GetSystemCorruptionRequest, GetSystemInfoResponse as GetSystemCorruptionResponse, GetStageThresholdsRequest as GetStageThresholdsCorruptionRequest, GetStageThresholdsResponse as GetStageThresholdsCorruptionResponse
from eveProto.generated.eve_public.pirate.suppression.api.requests_pb2 import GetSystemInfoRequest as GetSystemSuppressionRequest, GetSystemInfoResponse as GetSystemSuppressionResponse, GetStageThresholdsRequest as GetStageThresholdsSuppressionRequest, GetStageThresholdsResponse as GetStageThresholdsSuppressionResponse
from eveProto.generated.eve_public.solarsystem.solarsystem_pb2 import Identifier as SolarSystemId
from publicGateway.grpc.exceptions import GenericException
TIMEOUT_SECONDS = 10

class InsurgencyMessenger(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def GetCorruption(self, systemID):
        return self._BlockingRequestSystemCorruption(systemID)

    def GetSuppression(self, systemID):
        return self._BlockingRequestSystemSuppression(systemID)

    def GetCorruptionStages(self):
        return self._BlockingRequestStageThreasholds(GetStageThresholdsCorruptionRequest, GetStageThresholdsCorruptionResponse)

    def GetSuppressionStages(self):
        return self._BlockingRequestStageThreasholds(GetStageThresholdsSuppressionRequest, GetStageThresholdsSuppressionResponse)

    def _BlockingRequestStageThreasholds(self, requestClass, responseClass):
        request = requestClass()
        request_wrapper, response_wrapper, response_payload = self._BlockingRequest(request, responseClass)
        if response_wrapper.status_code != 200:
            raise GenericException(request_primitive=request_wrapper, response_primitive=response_wrapper)
        stages = []
        for fraction in response_payload.thresholds:
            stages.append(float(fraction.numerator) / float(fraction.denominator))

        return stages

    def _BlockingRequestSystemCorruption(self, systemID):
        request = GetSystemCorruptionRequest(system=SolarSystemId(sequential=systemID))
        request_wrapper, response_wrapper, response_payload = self._BlockingRequest(request, GetSystemCorruptionResponse)
        if response_wrapper.status_code != 200:
            raise GenericException(request_primitive=request_wrapper, response_primitive=response_wrapper)
        numerator = response_payload.total_progress.numerator
        denominator = response_payload.total_progress.denominator
        stage = response_payload.stage
        vanguard_numerator = response_payload.vanguard_contribution.numerator
        vanguard_denominator = response_payload.vanguard_contribution.denominator
        result = SystemData(systemID, numerator, denominator, stage, vanguard_numerator, vanguard_denominator)
        return result

    def _BlockingRequestSystemSuppression(self, systemID):
        request = GetSystemSuppressionRequest(system=SolarSystemId(sequential=systemID))
        request_wrapper, response_wrapper, response_payload = self._BlockingRequest(request, GetSystemSuppressionResponse)
        if response_wrapper.status_code != 200:
            raise GenericException(request_primitive=request_wrapper, response_primitive=response_wrapper)
        numerator = response_payload.total_progress.numerator
        denominator = response_payload.total_progress.denominator
        stage = response_payload.stage
        vanguard_numerator = response_payload.vanguard_contribution.numerator
        vanguard_denominator = response_payload.vanguard_contribution.denominator
        result = SystemData(systemID, numerator, denominator, stage, vanguard_numerator, vanguard_denominator)
        return result

    def _BlockingRequest(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        return (request_primitive, response_primitive, payload)

    def get_corruption_stage_thresholds(self):
        stages = self._BlockingRequestStageThreasholds(GetStageThresholdsCorruptionRequest, GetStageThresholdsCorruptionResponse)
        return stages

    def _GetSuppressionIncreasedCallback(self, originalCallback):

        def f(notice, _primative):
            systemID = notice.system.sequential
            data = NoticeData(notice.new_suppression.numerator, notice.new_suppression.denominator, vanguardInstigated=notice.vanguard)
            originalCallback(systemID, data)

        return f

    def _GetCorruptionIncreasedCallback(self, originalCallback):

        def f(notice, _primative):
            systemID = notice.system.sequential
            data = NoticeData(notice.new_corruption.numerator, notice.new_corruption.denominator, vanguardInstigated=notice.vanguard)
            originalCallback(systemID, data)

        return f

    def _GetSetCallback(self, originalCallback):

        def f(notice, _primative):
            systemID = notice.system.sequential
            data = NoticeData(notice.progress.numerator, notice.progress.denominator, False)
            originalCallback(systemID, data)

        return f

    def _GetResetCallback(self, originalCallback):

        def f(notice, _primative):
            systemID = notice.system.sequential
            data = NoticeData(notice.progress.numerator, notice.progress.denominator, False)
            originalCallback(systemID, data)

        return f

    def SubscribeToSuppressionValueUpdates(self, callback):
        increasedCallback = self._GetSuppressionIncreasedCallback(callback)
        setCallback = self._GetSetCallback(callback)
        resetCallback = self._GetResetCallback(callback)
        self.public_gateway.subscribe_to_notice(SuppressionIncreasedNotice, increasedCallback)
        self.public_gateway.subscribe_to_notice(SuppressionSetNotice, setCallback)
        self.public_gateway.subscribe_to_notice(SuppressionResetNotice, resetCallback)

    def SubscribeToCorruptionValueUpdates(self, callback):
        increasedCallback = self._GetCorruptionIncreasedCallback(callback)
        setCallback = self._GetSetCallback(callback)
        resetCallback = self._GetResetCallback(callback)
        self.public_gateway.subscribe_to_notice(CorruptionIncreasedNotice, increasedCallback)
        self.public_gateway.subscribe_to_notice(CorruptionSetNotice, setCallback)
        self.public_gateway.subscribe_to_notice(CorruptionResetNotice, resetCallback)


class NoticeData(object):

    def __init__(self, newNumerator, newDenominator, vanguardInstigated = False):
        self._vanguardInstigated = vanguardInstigated
        self._newDenominator = newDenominator
        self._newNumerator = newNumerator

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.newDenominator == self.newDenominator and other.newNumerator == self.newNumerator and other.vanguardInstigated == self.vanguardInstigated

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def vanguardInstigated(self):
        return self._vanguardInstigated

    @property
    def newDenominator(self):
        return self._newDenominator

    @property
    def newNumerator(self):
        return self._newNumerator


class SystemData(object):

    def __init__(self, systemID, numerator, denominator, stage, vanguard_numerator, vanguard_denominator):
        self.systemID = systemID
        self.vanguardDenominator = vanguard_denominator
        self.vanguardNumerator = vanguard_numerator
        self.stage = stage
        self.denominator = denominator
        self.numerator = numerator

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.systemID == self.systemID and other.numerator == self.numerator and other.denominator == self.denominator and other.stage == self.stage and other.vanguardNumerator == self.vanguardNumerator and other.vanguardDenominator == self.vanguardDenominator

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def totalProportion(self):
        if FloatCloseEnough(float(self.denominator), 0.0):
            return 0.0
        return float(self.numerator) / float(self.denominator)
