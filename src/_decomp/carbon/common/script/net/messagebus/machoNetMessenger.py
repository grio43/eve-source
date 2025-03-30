#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\messagebus\machoNetMessenger.py
from eveProto.generated.eve.monolith.monolith_pb2 import ShutdownRequested

class MachoNetMessenger(object):
    external_queue_manager = None

    def __init__(self, external_queue_manager):
        self.external_queue_manager = external_queue_manager

    def shutdown_requested(self):
        event = ShutdownRequested()
        self.external_queue_manager.PublishEventPayload(event)
