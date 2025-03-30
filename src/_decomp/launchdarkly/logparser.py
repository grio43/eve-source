#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\launchdarkly\logparser.py
import uthread2
downgrade_errors = ['streaming failed with recoverable error, backing off', 'streaming failed after 60 seconds, retrying']
keywords_to_upgrade_to_error = ['curl_easy_perform']
ignore_messages = ['attribute does not exist', 'LDStoreAll']

class LogParser:

    def __init__(self, sdk, client, logger):
        self.logger = logger
        self.sdk = sdk
        self.client = client
        self.last_log = None
        uthread2.StartTasklet(self._stream_logs)

    def _stream_logs(self):
        while self.client:
            logs = self.client.get_logs()
            for log in logs:
                level, callsite_message = log
                callsite, message = self._parse_log(callsite_message)
                self.last_log = message
                if message in ignore_messages:
                    continue
                message_upgraded = False
                for keyword in keywords_to_upgrade_to_error:
                    if keyword in message:
                        self.logger.error(message, extra={'callsite': callsite})
                        message_upgraded = True

                if message_upgraded:
                    continue
                if level <= self.sdk.enum_ld_log_error and message not in downgrade_errors:
                    self.logger.error(message, extra={'callsite': callsite})
                else:
                    message = '{}\n\ncallsite: {}'.format(message, callsite)
                    self.logger.debug(message, extra={'callsite': callsite})

            uthread2.Sleep(1)

    def _parse_log(self, message):
        try:
            i = message.index(']')
            return (message[1:i], message[i + 2:])
        except ValueError:
            return (message, message)
