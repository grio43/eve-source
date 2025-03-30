#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\exoplanetsutil\phasefolding.py


def fold(folding_center, period_length, values):
    edges = get_folding_edges(folding_center, period_length, values)
    current_index = 0
    start, end = edges[current_index], edges[current_index + 1]
    folded_values = []
    for value in values:
        if value > end:
            current_index += 1
            start, end = edges[current_index], edges[current_index + 1]
        folded_value = (value - start) / period_length % 1
        folded_values.append(folded_value)

    return folded_values


def get_folding_edges(folding_center, period_length, values):
    min_value, max_value = values[0], values[-1]
    half_period = period_length / 2.0
    left_edge, right_edge = folding_center - half_period, folding_center + half_period
    edges = []
    all_left, all_right = False, False
    while not all_left or not all_right:
        if not all_left:
            edges.insert(0, left_edge)
        if not all_right:
            edges.append(right_edge)
        all_left = left_edge < min_value
        all_right = right_edge > max_value
        left_edge -= period_length
        right_edge += period_length

    return edges
