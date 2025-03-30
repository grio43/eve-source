#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\statscapture\__init__.py
__author__ = 'snorri.sturluson'
import logging
import os
import time
import blue
from statscapture.performancemeasurements import Measurement
from statscapture.vm_metrics_reporter import send_metrics_to_victoria_metrics

class BaseCapture(object):

    def capture(self):
        raise NotImplementedError()


class PercentileCapture(BaseCapture):

    def __init__(self, _, counter_list):
        self.percentileAccumulators = []
        self.captured_values = {}
        self.counter_list = counter_list
        for counter_name, start, step in counter_list:
            accumulator = blue.PercentileAccumulator()
            self.percentileAccumulators.append(accumulator)
            blue.statistics.SetAccumulator(counter_name, accumulator)

        self.reset()

    def reset(self):
        for accumulator in self.percentileAccumulators:
            accumulator.Clear()

    def capture(self):
        cutoff_point = 0.99
        step_size = 0.0001
        for i, counter_list in enumerate(self.counter_list):
            counter_name, start, step = counter_list
            self.captured_values[counter_name] = {'complete': {'values': self.percentileAccumulators[i].GetPercentiles(start, step),
                          'start_value': start,
                          'step_size': step},
             'tail': {'values': self.percentileAccumulators[i].GetValuesForPercentiles(cutoff_point, step_size),
                      'cutoff_point': cutoff_point,
                      'step_size': step_size}}

        return self.captured_values


class StatsCapture(BaseCapture):

    def __init__(self, name, percentile_counters = ()):
        self.counters = {k:blue.statistics.Find(k) for k in blue.statistics.GetValues()}
        self.captured_values = {k:None for k in self.counters}
        self.start_time = time.clock()
        self.percentile_counter = PercentileCapture(name, percentile_counters)
        self.reset()

    def reset(self):
        blue.statistics.ResetPeaks()
        blue.statistics.ResetDerived()
        self.start_time = time.clock()

    def capture(self):
        self.captured_values['duration'] = time.clock() - self.start_time
        for name, counter in self.counters.iteritems():
            self.captured_values[name] = counter.value

        captured_percentile_data = self.percentile_counter.capture()
        if captured_percentile_data:
            self.captured_values['percentiles'] = captured_percentile_data
        self.percentile_counter = None
        return self.captured_values


class FullStatsCapture(StatsCapture):

    def __init__(self, measurement_name, percentile_counters = (), stats_filter = ()):
        super(FullStatsCapture, self).__init__(percentile_counters)
        self.name = measurement_name
        self.save_dir = ''
        self.tags = []
        self.stat_filter = stats_filter
        self.measurement = Measurement(statFilter=self.stat_filter)
        self.measurement.Begin()

    def capture(self):
        self.measurement.TakeScreenshot()
        self.measurement.End()
        import socket
        results = super(FullStatsCapture, self).capture()
        try:
            self.measurement.Upload(self.name, {'name': 'EVE Probe',
             'server': socket.gethostname()}, tags=','.join(self.tags), saveDir=self.save_dir)
        except:
            logging.exception('error when uploading performance results to the server')

        return results


class TeamcityStatsCapture(StatsCapture):

    def __init__(self, measurement_name, percentile_counters = (), stats_filter = (), save_dir = '', vm_server = None, machine_type = 'manual'):
        super(TeamcityStatsCapture, self).__init__(percentile_counters)
        self.name = measurement_name
        self.save_dir = save_dir
        self.stat_filter = stats_filter
        self.vm_server = vm_server
        self.machine_type = machine_type
        self.measurement = Measurement(statFilter=self.stat_filter)
        self.teamcity_stats_filter = ['Trinity/FrameTime',
         'FPS',
         'Blue/Memory/PageFileUsage',
         'Trinity/AL/GpuFrameTime',
         'Trinity/PresentTime']
        self.measurement.Begin()

    def capture(self):
        self.measurement.TakeScreenshot()
        self.measurement.End()
        results = super(TeamcityStatsCapture, self).capture()
        json_report = os.path.join(self.save_dir, 'measurement_teamcity.json')
        teamcity_report = os.path.join(self.save_dir, 'testlog.txt')
        self.measurement.Export(self.name, json_report, {'name': 'EVE Probe'})
        aggregatedStats = self.measurement.GetAggregatedStats(self.teamcity_stats_filter)
        self.log_stats_for_teamcity(aggregatedStats, teamcity_report)
        if self.vm_server:
            send_metrics_to_victoria_metrics(self.name, aggregatedStats, self.vm_server, machine_type=self.machine_type)
        return results

    def log_stats_for_teamcity(self, aggregatedStats, reportFile):
        if not os.path.exists(os.path.dirname(reportFile)):
            os.makedirs(os.path.dirname(reportFile))
        for statName, value in aggregatedStats.items():
            if statName == 'FPS':
                value = value / 100.0
            elif statName in ('Trinity/FrameTime', 'Trinity/AL/GpuFrameTime', 'Trinity/PresentTime'):
                value = value * 1000.0
            line_teamcity = "##teamcity[buildStatisticValue key='{0}' value='{1}']".format(statName, value)
            line_log = 'Measurement result for {0}: {1}'.format(statName, value)
            with open(reportFile, 'a') as f:
                f.write(line_teamcity + '\n')
                f.write(line_log + '\n')
