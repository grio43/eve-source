#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evemath\__init__.py
import math
import random
try:
    import geo2
except ImportError:
    geo2 = None

def weighted_choice(choices):
    total = sum((weight for choice, weight in choices))
    r = random.uniform(0, total)
    if total == 0:
        return random.choice(list(choices))[0]
    accumulated = 0
    for choice, weight in choices:
        if accumulated + weight >= r:
            return choice
        accumulated += weight


def get_center_point(position_list):
    if not position_list:
        raise ValueError('no entries in the list of positions')
    if len(position_list) == 1:
        return position_list[0]
    centroid = (0, 0, 0)
    for pos in position_list:
        centroid = geo2.Vec3AddD(centroid, pos)

    centroid = geo2.Vec3ScaleD(centroid, 1.0 / len(position_list))
    return centroid


def get_farthest_distance_from_point(reference_point, points):
    return math.sqrt(max((geo2.Vec3DistanceSqD(reference_point, point) for point in points)))


def stochastic_round(x):
    return int(math.floor(x + random.random()))
