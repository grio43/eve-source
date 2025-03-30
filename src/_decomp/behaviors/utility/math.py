#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\math.py
try:
    import geo2
except ImportError:
    geo2 = object()

def compute_forward_fleet_position(friendlyCoordinate, hostileCoordinate, distance):
    return compute_fleet_position(friendlyCoordinate, hostileCoordinate, distance, hostileCoordinate)


def compute_rear_fleet_position(friendlyCoordinate, hostileCoordinate, distance):
    return compute_fleet_position(friendlyCoordinate, hostileCoordinate, distance, friendlyCoordinate)


def compute_fleet_position(friendlyCoordinate, hostileCoordinate, distance, referenceCoordinate):
    rearVector = geo2.Vec3SubtractD(friendlyCoordinate, hostileCoordinate)
    rearVector = geo2.Vec3Normalize(rearVector)
    displacementVector = geo2.Vec3Scale(rearVector, distance)
    desiredRearPosition = geo2.Vec3AddD(referenceCoordinate, displacementVector)
    return desiredRearPosition


def get_normalized_dict(target_dict):
    max_value = max(target_dict.itervalues())
    if max_value == 0:
        return target_dict.copy()
    return {key:float(value) / max_value for key, value in target_dict.iteritems()}
