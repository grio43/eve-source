#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\patternProjectionUtil.py
import math
import geo2

def get_pattern_projection_position_and_rotation(ellipsoid_center, ellipsoid_radii, offset_x, offset_y, yaw, pitch, twist):
    projector_pos = get_projector_position(yaw, pitch, ellipsoid_center, ellipsoid_radii)
    pre_twist_quat = _get_pre_twist_quat(projector_pos, pitch, ellipsoid_center, ellipsoid_radii)
    x_y_offset = _get_x_y_offset_vector(pre_twist_quat, offset_x, offset_y, ellipsoid_radii)
    position = geo2.Vec3Add(projector_pos, x_y_offset)
    twist_quat = geo2.QuaternionRotationSetYawPitchRoll(0.0, twist * math.pi, 0.0)
    rotation = geo2.QuaternionMultiply(twist_quat, pre_twist_quat)
    return (list(position), list(rotation))


def get_projector_position(yaw, pitch, ellipsoid_center, ellipsoid_radii):
    intersection_point = _get_ellipsoid_intersection_point(ellipsoid_radii, yaw, pitch)
    projector_pos = geo2.Vec3Add(ellipsoid_center, intersection_point)
    return projector_pos


def _get_ellipsoid_intersection_point(ellipsoid_radii, yaw, pitch):
    abs_pitch = math.fabs(pitch)
    x = math.sin(yaw * math.pi) * ellipsoid_radii[0] * (1.0 - abs_pitch)
    y = abs_pitch * ellipsoid_radii[1] * math.copysign(1.0, pitch)
    z = math.cos(yaw * math.pi) * -ellipsoid_radii[2] * (1 - abs_pitch)
    x_y_offset = (x, y, z)
    x_y_offset = geo2.Vec3Scale(geo2.Vec3Normalize(x_y_offset), max(ellipsoid_radii))
    return x_y_offset


def _get_projection_point_offset(ellipsoid_radii, projectionPoint):
    maxSideLength = max(ellipsoid_radii)
    directionScaler = (ellipsoid_radii[0] / maxSideLength, ellipsoid_radii[1] / maxSideLength, ellipsoid_radii[2] / maxSideLength)
    offsetFactor = 0.2
    projectionPointNormalized = geo2.Vec3Normalize(projectionPoint)
    offsetAtPosition = tuple((ele1 * ele2 * ele3 * offsetFactor for ele1, ele2, ele3 in zip(projectionPointNormalized, ellipsoid_radii, directionScaler)))
    return offsetAtPosition


def _get_pre_twist_quat(projection_pos, pitch, ellipsoid_center, ellipsoid_radii):
    offset_at_position = _get_projection_point_offset(ellipsoid_radii, projection_pos)
    targetPoint = geo2.Vec3Add(ellipsoid_center, offset_at_position)
    lerpValue = math.pow(min(1.0, 1.2 * abs(pitch)), 2.0)
    targetPoint = geo2.Lerp(targetPoint, ellipsoid_center, lerpValue)
    directionNormalized = geo2.Vec3Normalize(geo2.Vec3Subtract(targetPoint, projection_pos))
    lookingAtLeftSide = 0.0 < directionNormalized[0]
    rotationQuat = geo2.QuaternionRotationArc((0.0, 1.0, 0.0), directionNormalized)
    x, _, z = directionNormalized
    yaw = -(math.atan2(z, x) + math.pi / 2)
    horizontalAxisMapped = yaw % math.pi / math.pi
    if lookingAtLeftSide:
        horizontalAxisMapped = 1.0 - horizontalAxisMapped / 2
    else:
        horizontalAxisMapped = 0.5 - horizontalAxisMapped / 2
    flip = math.pi if yaw % math.pi == 0.0 else 0.0
    rollValue = horizontalAxisMapped * 2.0 * -math.pi + flip
    rollQuaternion = geo2.QuaternionRotationSetYawPitchRoll(0.0, rollValue, 0.0)
    Y2Zadjustment = (0.0, 0.0, 0.7071, 0.7071)
    rotationQuat = geo2.QuaternionMultiply(Y2Zadjustment, rotationQuat)
    rotationQuat = geo2.QuaternionMultiply(rollQuaternion, rotationQuat)
    return rotationQuat


def _get_x_y_offset_vector(rotation, offset_x, offset_y, ellipsoid_radii):
    offset = (0.0, offset_x, -offset_y)
    scaledOffset = geo2.Vec3Scale(offset, max(ellipsoid_radii) * 0.75)
    return geo2.QuaternionTransformVector(rotation, scaledOffset)
