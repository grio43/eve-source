#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodditests\client\reporting\reporter.py
import abc
import logging
import os
logger = logging.getLogger(__name__)

class BaseReporter(object):
    __metaclass__ = abc.ABCMeta
    REPORT_FILE_NAME = None

    def __init__(self, instance_id, folder_path):
        self.reports = []
        self._cached_file_reports_by_timestamp = None
        self._create_report_file(instance_id, folder_path)

    def _create_report_file(self, instance_id, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        self._report_file = os.path.join(folder_path, self.REPORT_FILE_NAME)
        logger.info('Logging reports for test {} in file: {}'.format(instance_id, os.path.abspath(self._report_file)))

    def get_report_file(self):
        return self._report_file

    @abc.abstractmethod
    def log_character_select(self, character_id):
        pass

    @abc.abstractmethod
    def log_node_graph_started(self, node_graph_id):
        pass

    @abc.abstractmethod
    def log_test_update(self, step, state):
        pass

    @abc.abstractmethod
    def log_test_metadata(self, step, key, value):
        pass

    @abc.abstractmethod
    def log_node_graph_completed(self, node_graph_id):
        pass
