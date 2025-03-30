#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphs\axis.py
from carbonui.graphs.axis import BaseAxis
from carbonui.graphs.axis import AutoTicksAxis
from projectdiscovery.client.projects.exoplanets.exoplanetsutil import phasefolding
import localization

class ExoPlanetsCategoryAxis(BaseAxis):
    __notifyevents__ = ['OnUIScalingChange']

    def __init__(self, dataPoints, dataRange = None, *args, **kwargs):
        super(ExoPlanetsCategoryAxis, self).__init__((0, 1), *args, **kwargs)
        self._actual_data = dataPoints
        self._actual_data_range = dataRange if dataRange else (min(dataPoints), max(dataPoints))
        self._folded_data_range = None
        self._data_points = [ self.map_actual_value_to_normalized_value(value) for value in dataPoints ]
        self._unfolded_points = self._actual_data
        self._indexes = []
        self._calculate_phase_division_indexes()
        self._folding_center = None
        self._folding_period = None
        sm.RegisterNotify(self)

    def OnUIScalingChange(self, *args, **kwargs):
        self._OnChange()

    def GetDataPoints(self):
        return self._data_points

    def get_actual_data_points(self):
        return self._actual_data

    def MapDataPointsToViewport(self):
        return self.MapSequenceToViewport(self._data_points)

    def MapToView(self, value):
        value = self.map_actual_value_to_normalized_value(value)
        return super(ExoPlanetsCategoryAxis, self).MapToView(value)

    def get_axis_value_from_graph_coordinate(self, graph_coordinate):
        normalized_value = self.MapFromViewport(graph_coordinate)
        return self.map_normalized_value_to_actual_value(normalized_value)

    def set_zoom(self, min_value, max_value):
        if min_value > max_value:
            return
        normalized_min_value = self.map_actual_value_to_normalized_value(min_value)
        normalized_max_value = self.map_actual_value_to_normalized_value(max_value)
        self._visibleRange = (normalized_min_value, normalized_max_value)
        self._OnChange()

    def get_visible_range(self):
        return (self.map_normalized_value_to_actual_value(self._visibleRange[0]), self.map_normalized_value_to_actual_value(self._visibleRange[1]))

    def get_min_value(self):
        return self.map_normalized_value_to_actual_value(self._dataRange[0])

    def get_max_value(self):
        return self.map_normalized_value_to_actual_value(self._dataRange[1])

    def set_data_points(self, data_points):
        self._actual_data = data_points
        self._unfolded_points = data_points
        self._data_points = [ self.map_actual_value_to_normalized_value(value) for value in data_points ]
        self._calculate_phase_division_indexes()
        if self._folded_data_range:
            self.fold(self._folding_center, self._folding_period)
        self._OnChange()

    def _calculate_phase_division_indexes(self):
        self._indexes = [ i for i in xrange(1, len(self._data_points)) if self._data_points[i] < self._data_points[i - 1] ]

    def get_phase_division_indexes(self):
        return self._indexes

    def fold(self, folding_center, period_length):
        if self._data_points:
            half_period = period_length / 2.0
            self._folding_center = folding_center
            self._folding_period = period_length
            self._folded_data_range = (folding_center - half_period, folding_center + half_period)
            self._data_points = phasefolding.fold(folding_center, period_length, self._unfolded_points)
            self._calculate_phase_division_indexes()
            self._OnChange()

    def unfold(self):
        self._folded_data_range = None
        self._data_points = [ self.map_actual_value_to_normalized_value(value) for value in self._unfolded_points ]
        self._calculate_phase_division_indexes()
        self._OnChange()

    def map_actual_value_to_normalized_value(self, value):
        if self._folded_data_range:
            return (value - self._folded_data_range[0]) / (self._folded_data_range[1] - self._folded_data_range[0])
        return (value - self._actual_data_range[0]) / (self._actual_data_range[1] - self._actual_data_range[0])

    def map_normalized_value_to_actual_value(self, value):
        if self._folded_data_range:
            return (1.0 - value) * self._folded_data_range[0] + value * self._folded_data_range[1]
        return (1.0 - value) * self._actual_data_range[0] + value * self._actual_data_range[1]

    @property
    def period_length(self):
        return self._folding_period

    def GetRangeText(self, start, end):
        return localization.GetByLabel('UI/ProjectDiscovery/exoplanets/ZoomSize', Zoomlevel=int((end - start) * 100))


class ExoPlanetsDayTimeAxis(ExoPlanetsCategoryAxis):

    def __init__(self, dataPoints, *args, **kwargs):
        super(ExoPlanetsDayTimeAxis, self).__init__(dataPoints, *args, **kwargs)
        self._min_value = self._actual_data_range[0]
        self._max_value = self._actual_data_range[1]
        self._ticks = []
        current_value = self._min_value
        while current_value < self._max_value:
            self._ticks.append(current_value)
            current_value += 1.0

    def GetTicks(self):
        return self._get_ticks()

    def GetTickLabel(self, tickValue):
        if self._folded_data_range:
            center = self._folded_data_range[0] + (self._folded_data_range[1] - self._folded_data_range[0]) / 2.0
            offset = int(tickValue - center)
            if offset <= 0:
                return '%sd' % offset
            return '+%sd' % offset
        return '%sd' % int(tickValue - self._min_value)

    def _get_ticks(self):
        if self._folded_data_range:
            center = self._folded_data_range[0] + (self._folded_data_range[1] - self._folded_data_range[0]) / 2.0
            ticks = [center]
            left, right = center - 1, center + 1
            while left >= self._folded_data_range[0] and right <= self._folded_data_range[1]:
                ticks.insert(0, left)
                ticks.append(right)
                left -= 1
                right += 1

            return ticks
        return self._ticks


class ExoPlanetsAutoTickAxis(AutoTicksAxis):

    def __init__(self, dataRange, is_relative_flux = True, flux_values = None, *args, **kwargs):
        super(ExoPlanetsAutoTickAxis, self).__init__(dataRange, *args, **kwargs)
        self.max_value = self._visibleRange[1]
        self.min_value = self._visibleRange[0]
        self._is_relative_flux = is_relative_flux and flux_values
        self._mean_flux = None
        self._calculate_mean_flux(flux_values)

    def get_axis_value_from_graph_coordinate(self, graph_coordinate):
        return self.MapFromViewport(graph_coordinate)

    def set_zoom(self, min_value, max_value):
        if min_value > max_value:
            return
        self._visibleRange = (min_value, max_value)
        self._OnChange()

    def get_visible_range(self):
        return self._visibleRange

    def get_min_value(self):
        return self.min_value

    def get_max_value(self):
        return self.max_value

    def set_data_range(self, min_value, max_value):
        self.SetDataRange((min_value, max_value))
        self.max_value = self._visibleRange[1]
        self.min_value = self._visibleRange[0]

    def GetTickLabel(self, tick_value):
        if self._is_relative_flux:
            tick_value = round(tick_value / self._mean_flux, 5) * 100
            return '%s%%' % tick_value
        return self._labelFormat(tick_value)

    def set_relative_flux_active(self, flux_values):
        self._is_relative_flux = True
        self._calculate_mean_flux(flux_values)
        self._OnChange()

    def set_actual_flux_active(self):
        self._is_relative_flux = False
        self._OnChange()

    def _calculate_mean_flux(self, flux_values):
        if flux_values:
            self._mean_flux = sum(flux_values) / len(flux_values)
