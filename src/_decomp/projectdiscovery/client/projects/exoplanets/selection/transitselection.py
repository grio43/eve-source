#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\selection\transitselection.py
from projectdiscovery.client.projects.exoplanets.exoplanetsutil import markers
from signals import Signal
import math

class TransitSelection(object):
    __notifyevents__ = []

    def __init__(self, epoch, period, raw_data, color = (1, 1, 1, 1), pattern_path = None, listen_to_data_change = False, type = 'Planet', number = 1):
        if listen_to_data_change:
            self.__notifyevents__.append('OnDataUpdate')
        self.on_change = Signal(signalName='on_change')
        self.on_data_change = Signal(signalName='on_data_change')
        self._transit_center = epoch if epoch else 0
        self._period_length = period
        self._raw_data = raw_data
        self._centers = [self._transit_center] if self._transit_center else []
        self._minimum_period_length = markers.MINIMUM_PERIOD
        self._color = color
        self._pattern = pattern_path
        self._hidden = False
        self._type = type
        self._number = number
        sm.RegisterNotify(self)

    def OnDataUpdate(self, data):
        self._raw_data = data
        self.on_data_change()

    def set_period_end_value(self, period_end_value):
        if period_end_value == None:
            self._period_length = None
        else:
            minimum, maximum = min(self._transit_center, period_end_value), max(self._transit_center, period_end_value)
            self._period_length = maximum - minimum
            self._period_length = None if self._period_length < self._minimum_period_length else self._period_length
        self._calculate_transit_centers_in_data()
        self.on_change()

    def get_period_length(self):
        return self._period_length

    def set_period_length(self, period_length):
        self._period_length = period_length
        self._calculate_transit_centers_in_data()
        self.on_change()

    def get_epoch(self):
        epoch = self._transit_center - self._raw_data[0][0] if self._transit_center and self._raw_data else None
        if epoch and epoch < 0:
            in_range = [ center - self._raw_data[0][0] for center in self._centers if self._raw_data[0][0] <= center <= self._raw_data[-1][0] ]
            epoch = in_range[0] if in_range else epoch
        return epoch

    def get_centers(self):
        return self._centers

    def set_hidden(self, is_hidden):
        self._hidden = is_hidden

    def is_hidden(self):
        return self._hidden

    def set_color(self, color):
        self._color = color
        self.on_change()

    def get_color(self):
        return self._color

    @property
    def pattern_path(self):
        return self._pattern

    @pattern_path.setter
    def pattern_path(self, path):
        self._pattern = path

    def set_center(self, new_center, fix_center_to_data_range = True):
        self._transit_center = new_center
        self._calculate_transit_centers_in_data()
        if fix_center_to_data_range and self._period_length and self._centers:
            if self._transit_center < self._raw_data[0][0]:
                self._transit_center = self._centers[-1]
            elif self._transit_center > self._raw_data[-1][0]:
                self._transit_center = self._centers[0]
        self.on_change()

    def get_center(self):
        return self._transit_center

    def get_estimated_eclipse_time(self, margin_of_error = 1.0):
        period = 30 if not self._period_length else self._period_length
        return 0.075 * period ** (1.0 / 3) * margin_of_error

    def get_transit_ranges(self, margin_of_error = 1.0):
        half_transit_time = self.get_estimated_eclipse_time(margin_of_error) / 2.0
        centers = self.get_centers()
        return [ (center - half_transit_time, center + half_transit_time) for center in centers ]

    def get_transit_range_for_marking(self, marking, margin_of_error = 1.0):
        half_transit_time = self.get_estimated_eclipse_time(margin_of_error) / 2.0
        return (marking - half_transit_time, marking + half_transit_time)

    def get_closest_points_to_centers(self):
        closest_points = []
        data = [ point for point in self._raw_data ]
        for center in self.get_centers():
            data.sort(key=lambda data_point: math.fabs(center - data_point[0]))
            closest_points.append(data[0])

        return closest_points

    def get_transit_type(self):
        return self._type

    def _calculate_transit_centers_in_data(self):
        if self._transit_center is None:
            self._centers = []
        minimum = self._transit_center
        maximum = self._transit_center
        self._centers = [minimum]
        if self._period_length:
            while minimum > self._raw_data[0][0] or maximum < self._raw_data[-1][0]:
                minimum -= self._period_length
                maximum += self._period_length
                if minimum > self._raw_data[0][0]:
                    self._centers.append(minimum)
                if maximum < self._raw_data[-1][0]:
                    self._centers.append(maximum)

        if self._raw_data:
            self._centers = [ center for center in self._centers if self._raw_data[0][0] <= center <= self._raw_data[-1][0] ]
        self._centers.sort()

    @property
    def number(self):
        return self._number
