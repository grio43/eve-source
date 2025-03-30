#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\exoplanetsutil\calibration.py
from projectdiscovery.client.projects.exoplanets.exoplanetsutil import phasefolding

def get_end_data(start_data, center, period):
    time_values = [ time for time, flux in start_data ]
    flux_values = [ flux for time, flux in start_data ]
    time_values = get_end_time_values(time_values, center, period)
    return zip(time_values, flux_values)


def get_end_time_values(start_time_values, center, period, min_time = None, max_time = None):
    if not (min_time and max_time):
        min_time, max_time = min(start_time_values), max(start_time_values)
    edges = phasefolding.get_folding_edges(center, period, start_time_values)
    edge_index = 0
    min_edge, max_edge = edges[edge_index], edges[edge_index + 1]
    end_time_values = []
    for time in start_time_values:
        if time > max_edge:
            edge_index += 1
            min_edge, max_edge = edges[edge_index], edges[edge_index + 1]
        t = (time - min_edge) / period
        time = (1 - t) * min_time + t * max_time
        end_time_values.append(time)

    return end_time_values
