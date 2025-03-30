#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\exoplanetsutil\result.py
from projectdiscovery.client.projects.exoplanets.selection.transitselection import TransitSelection

class ResultStates(object):
    CORRECT = 0
    MISSED = 1
    INCORRECT = 2


def get_solution_data(solution_response, data, player_markers):
    if solution_response is None or solution_response['task']['solution'] is None:
        return ([],
         [],
         [],
         {})
    mapping = get_marker_and_interval_mapping(solution_response, data)
    solution_intervals = sum(mapping.values(), []) if mapping else []
    correct_inter, missed_inter, incorrect_inter = get_correct_missed_and_incorrect_intervals(player_markers, solution_intervals)
    interval_to_marker_mapping = get_intervals_to_marker_mapping(mapping)
    return (correct_inter,
     missed_inter,
     incorrect_inter,
     interval_to_marker_mapping)


def get_marker_and_interval_mapping(solution_response, data):
    mapping = {}
    number = 0
    if solution_response['task']['solution']:
        for transit in solution_response['task']['solution']['transits']:
            number += 1
            marker = TransitSelection(transit['epoch'], None, data, listen_to_data_change=True, type=transit['source'], number=number)
            if 'period' in transit:
                marker.set_period_length(transit['period'])
            mapping[marker] = [ tuple(interval) for interval in transit['transitIntervals'] ] if 'transitIntervals' in transit else marker.get_transit_ranges(1.2)

    return mapping


def get_correct_missed_and_incorrect_intervals(player_markers, solution_intervals):
    correct_intervals = set()
    incorrect_intervals = set()
    for marker in player_markers:
        markings = marker.get_centers()
        correct_markings = [ marking for marking in markings if any([ minimum <= marking <= maximum for minimum, maximum in solution_intervals ]) ]
        incorrect_markings = [ marking for marking in markings if marking not in correct_markings ]
        correct_intervals_for_marker = [ interval for interval in solution_intervals if any([ interval[0] <= marking <= interval[1] for marking in correct_markings ]) ]
        for interval in correct_intervals_for_marker:
            correct_intervals.add(interval)

        for marking in incorrect_markings:
            incorrect_intervals.add(marker.get_transit_range_for_marking(marking))

    missed_intervals = [ interval for interval in solution_intervals if interval not in correct_intervals ]
    return (sorted(list(correct_intervals)), sorted(missed_intervals), sorted(list(incorrect_intervals)))


def get_intervals_to_marker_mapping(marker_to_intervals_mapping):
    mapping = {}
    for marker, intervals in marker_to_intervals_mapping.items():
        for interval in intervals:
            mapping[interval] = marker

    return mapping


def get_intervals_points_indices_of_same_state(correct_intervals, missed_intervals, incorrect_intervals, interval, interval_to_marker_mapping, data):
    marker = interval_to_marker_mapping[interval]
    intervals = get_intervals_for_marker(marker, interval_to_marker_mapping)
    if interval in correct_intervals:
        intervals = [ m_interval for m_interval in intervals if m_interval in correct_intervals ]
        state = ResultStates.CORRECT
    elif interval in missed_intervals:
        intervals = [ m_interval for m_interval in intervals if m_interval in missed_intervals ]
        state = ResultStates.MISSED
    else:
        intervals = [ m_interval for m_interval in intervals if m_interval in incorrect_intervals ]
        state = ResultStates.INCORRECT
    indices, empty1, empty2 = categorize_point_indices_to_result(data, intervals, [], [])
    return (indices, state)


def get_intervals_for_marker(marker, interval_to_marker_mapping):
    intervals = [ interval for interval, d_marker in interval_to_marker_mapping.items() if d_marker is marker ]
    return intervals


def categorize_point_indices_to_result(data, correct_intervals, missed_intervals, incorrect_intervals):
    correct_indices = [ i for i, (x, y) in enumerate(data) if any([ m_range[0] <= x <= m_range[1] for m_range in correct_intervals ]) ]
    missed_indices = [ i for i, (x, y) in enumerate(data) if any([ m_range[0] <= x <= m_range[1] for m_range in missed_intervals ]) ]
    incorrect_indices = [ i for i, (x, y) in enumerate(data) if any([ m_range[0] <= x <= m_range[1] for m_range in incorrect_intervals ]) and i not in missed_intervals and i not in correct_indices ]
    return (correct_indices, missed_indices, incorrect_indices)
