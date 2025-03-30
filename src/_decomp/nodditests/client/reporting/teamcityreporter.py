#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodditests\client\reporting\teamcityreporter.py
from datetime import datetime
from nodditests.client.reporting.reporter import BaseReporter
import logging
logger = logging.getLogger(__name__)

class TeamCityReporter(BaseReporter):
    REPORT_FILE_NAME = 'testlog.txt'

    def _get_timestamp(self):
        return datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

    def _get_test_name(self, test_name):
        return str(test_name).replace('[', '|[').replace(']', '|]')

    def log_character_select(self, character_id):
        pass

    def log_node_graph_started(self, node_graph_id):
        self._write_log(status='testSuiteStarted', test_name=node_graph_id)

    def log_test_update(self, step, state):
        self._write_log(status=state, test_name=step)

    def log_test_metadata(self, step, key, value):
        self._write_metadata_log(test_name=step, key=key, value=value)

    def log_node_graph_completed(self, node_graph_id):
        self._write_log(status='testSuiteFinished', test_name=node_graph_id)

    def _write_log(self, status, test_name):
        timestamp = self._get_timestamp()
        test_name = self._get_test_name(test_name)
        logger.info('Logging report at {}: {} = {}'.format(timestamp, status, test_name))
        line = "##teamcity[{} name='{}' timestamp='{}' ]".format(status, test_name, timestamp)
        with open(self._report_file, 'a') as f:
            f.write(line)
            f.write('\n')

    def _write_metadata_log(self, test_name, key, value):
        timestamp = self._get_timestamp()
        test_name = self._get_test_name(test_name)
        if value is None:
            value = timestamp
        logger.info('Logging testMetadata report at {}: {} = {} ({}))'.format(timestamp, key, value, test_name))
        line = "##teamcity[testMetadata testName='{}' name='{}' value='{}' timestamp='{}' ]".format(test_name, key, value, timestamp)
        with open(self._report_file, 'a') as f:
            f.write(line)
            f.write('\n')
