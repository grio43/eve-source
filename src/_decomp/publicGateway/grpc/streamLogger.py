#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\publicGateway\grpc\streamLogger.py
import uthread2
GRPC_STATUS_CODE_UNAUTHENTICATED = 16
NUM_BREADCRUMBS = 10

class StreamLogger(object):

    def __init__(self, logger, grpc_stream_module):
        if grpc_stream_module is None:
            return
        self.logger = logger
        self.grpc_stream_module = grpc_stream_module
        self.stream_id = 0
        self.status_code = 0
        self.message = 'unknown'
        self.details = 'unknown'
        self.lastLog = []
        uthread2.StartTasklet(self._periodic_log)

    def get_log_breadcrumbs(self):
        return self.lastLog[-NUM_BREADCRUMBS:]

    def _periodic_log(self):
        while True:
            uthread2.Sleep(1)
            self._poll_status()

    def _poll_status(self):
        logs = self.grpc_stream_module.get_stream_status_log()
        if not logs:
            return
        self.lastLog = logs
        for log in logs:
            self.stream_id = log[0]
            self.status_code = log[1]
            self.message = log[2]
            self.details = log[3]
            formatted = 'stream id: {}, status_code: {}, message: {}, details: {}'.format(self.stream_id, self.status_code, self.message, self.details)
            self.logger.debug(formatted)
