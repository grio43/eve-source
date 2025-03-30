#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodditests\client\reporting\yamlreporter.py
from datetime import datetime
from nodditests.client.reporting.report import Report
from nodditests.client.reporting.reporter import BaseReporter
import logging
import os
import yaml
logger = logging.getLogger(__name__)

class YamlReporter(BaseReporter):
    REPORT_FILE_NAME = 'progress.yaml'

    def log_character_select(self, character_id):
        self._add_report(key='character_selected', attributes={'character_id': character_id})

    def log_node_graph_started(self, node_graph_id):
        self._add_report(key='node_graph_started', attributes={'node_graph_id': node_graph_id})

    def log_test_update(self, step, state):
        self._add_report(key=step, attributes={'state': state})

    def log_test_metadata(self, step, key, value):
        self._add_report(key=step, attributes={key: value})

    def log_node_graph_completed(self, node_graph_id):
        self._add_report(key='node_graph_completed', attributes={'node_graph_id': node_graph_id})

    def _add_report(self, key, attributes):
        timestamp = datetime.now()
        self.reports.append(Report(timestamp, key, attributes))
        logger.info('Logging report at {}: {} = {}'.format(timestamp, key, attributes))
        self._persist_report_data()

    def _persist_report_data(self):
        with open(self._report_file, 'w') as fp:
            yaml.safe_dump(self.reports, fp, default_style=None, default_flow_style=False)
        self._cached_file_reports_by_timestamp = None

    def _load_report_data(self):
        if not os.path.exists(self._report_file):
            data = {}
        else:
            with open(self._report_file, 'r') as fp:
                data = yaml.safe_load(fp)
        return data

    def get_file_reports_by_timestamp(self):
        if self._cached_file_reports_by_timestamp is None:
            self._cached_file_reports_by_timestamp = {}
            for report_yaml in self._load_report_data():
                report = Report.from_dict(report_yaml)
                self._cached_file_reports_by_timestamp[report.timestamp] = report

        return self._cached_file_reports_by_timestamp

    def _get_latest_report_attributes_by_key(self, key):
        reports_by_timestamp = self.get_file_reports_by_timestamp()
        ordered_timestamps = sorted(reports_by_timestamp.keys(), reverse=True)
        for timestamp in ordered_timestamps:
            report = reports_by_timestamp[timestamp]
            if report.key == key:
                return report.attributes

        return {}

    def get_latest_character_select_info(self):
        return self._get_latest_report_attributes_by_key('character_selected')

    def get_latest_node_graph_started_info(self):
        return self._get_latest_report_attributes_by_key('node_graph_started')

    def get_latest_test_info(self, step):
        return self._get_latest_report_attributes_by_key(step)

    def get_latest_node_graph_completed_info(self):
        return self._get_latest_report_attributes_by_key('node_graph_completed')
