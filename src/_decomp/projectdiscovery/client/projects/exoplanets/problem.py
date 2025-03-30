#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\problem.py


class Problem:

    def __init__(self, data, solution):
        self.data = data
        self.solution = solution
        self.normalize_solution()
        self._correct_point_indices = None
        self._range_represented = None

    def normalize_solution(self):
        if self.solution is None:
            return
        for transit in self.solution:
            while self.data[0][0] <= transit['epoch']:
                transit['epoch'] = transit['epoch'] - transit['period']

            while self.data[0][0] > transit['epoch']:
                transit['epoch'] = transit['epoch'] + transit['period']

    def get_transit_ranges(self):
        if len(self.solution) == 0:
            return [{'lowerbound': 1,
              'upperbound': -1.0}]
        ranges = []
        for transit in self.solution:
            current_epoch = transit['epoch']
            max_time = self.data[-1][0]
            centers = []
            while current_epoch < max_time:
                centers.append(current_epoch)
                current_epoch += transit['period']

            width = 0.075 * transit['period'] ** (1.0 / 3)
            radius = width / 2
            ranges = [ {} for center in centers ]
            for i in range(len(centers)):
                ranges[i]['lowerbound'] = centers[i] - radius
                ranges[i]['upperbound'] = centers[i] + radius

        return ranges

    def evaluate_transit_selection(self, transit_selections):
        ranges = self.get_transit_ranges()
        range_represented = [ False for x in ranges ]
        if len(transit_selections) == 0:
            self._range_represented = range_represented
            return len(self.solution) == 0
        for selection in transit_selections:
            selected_points = selection.get_centers()
            for point in selected_points:
                agrees = False
                for index, range in enumerate(ranges):
                    if range['lowerbound'] < point < range['upperbound']:
                        range_represented[index] = True
                        agrees = True

                if not agrees:
                    return False

        self._range_represented = range_represented
        if False in range_represented:
            return False
        return True

    def get_unselected_transit_points(self):
        if self._range_represented is None:
            return []
        unselected_transit_points = []
        ranges = self.get_transit_ranges()
        for index, is_represented in enumerate(self._range_represented):
            if not is_represented:
                unselected_transit_points = unselected_transit_points + self.find_points_in_time_range(ranges[index])

        return unselected_transit_points

    def get_transit_radius(self, period):
        if period is None:
            period = 30
        width = 0.075 * period ** (1.0 / 3)
        radius = width / 2
        return radius

    def find_erroneous_selections(self, transit_selections):
        if len(transit_selections) == 0:
            return []
        ranges = self.get_transit_ranges()
        outside_points = []
        for selection in transit_selections:
            selected_points = selection.get_centers()
            for point in selected_points:
                agrees = False
                for range in ranges:
                    if range['lowerbound'] < point < range['upperbound']:
                        agrees = True
                        break
                    if not agrees:
                        outside_points.append(point)

        radius = self.get_transit_radius(transit_selections[0].get_period_length()) / 4.0
        data_points = []
        for point in outside_points:
            point_range = {'lowerbound': point - radius,
             'upperbound': point + radius}
            data_range = self.find_points_in_time_range(point_range)
            data_points = data_points + data_range

        error_points = [ x for x in data_points if x not in self.get_correct_points() ]
        return error_points

    def find_points_in_time_range(self, range):
        points = []
        for index, (time, flux) in enumerate(self.data):
            if range['lowerbound'] < time < range['upperbound']:
                points.append(index)

        return points

    def get_correct_points(self):
        if self._correct_point_indices is not None:
            return self._correct_point_indices
        correct_point_indices = []
        ranges = self.get_transit_ranges()
        for transit in self.solution:
            current_range = 0
            for index, (time, flux) in enumerate(self.data):
                if ranges[current_range]['lowerbound'] < time < ranges[current_range]['upperbound']:
                    correct_point_indices.append(index)
                elif ranges[current_range]['upperbound'] < time:
                    current_range += 1
                    if current_range >= len(ranges):
                        break

        self._correct_point_indices = correct_point_indices
        return correct_point_indices
