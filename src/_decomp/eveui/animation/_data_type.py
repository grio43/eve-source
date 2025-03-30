#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\animation\_data_type.py
import numbers
from carbonui.primitives.sprite import PyColor
import enum

class DataType(enum.AutoNumber):
    color = ()
    quaternion = ()
    scalar = ()
    unknown = ()
    vector2 = ()
    vector3 = ()
    vector4 = ()


def validate_data_type(value, target_data_type):
    value_data_type = detect_data_type(value)
    if not are_data_types_compatible(target_data_type, value_data_type):
        raise TypeError('Unable to animate due to incompatible data type - target_data_type: %s - value_data_type: %s' % (target_data_type, value_data_type))


def are_data_types_compatible(target, source):
    if target is source:
        return True
    if target is DataType.color and source in (DataType.vector3, DataType.vector4):
        return True
    if target is DataType.quaternion and source is DataType.vector4:
        return True
    return False


def detect_attribute_data_type(obj, attribute_name):
    if is_transform_rotation(obj, attribute_name):
        return DataType.quaternion
    return detect_data_type(getattr(obj, attribute_name))


def is_transform_rotation(obj, attribute_name):
    if attribute_name != 'rotation':
        return False
    if getattr(obj, '__bluetype__', None) != 'trinity.EveTransform':
        return False
    if detect_data_type(getattr(obj, attribute_name)) != DataType.vector4:
        return False
    return True


def detect_data_type(value):
    if isinstance(value, numbers.Number):
        return DataType.scalar
    if isinstance(value, PyColor):
        return DataType.color
    try:
        length = len(value)
        if length == 4:
            return DataType.vector4
        if length == 3:
            return DataType.vector3
        if length == 2:
            return DataType.vector2
    except TypeError:
        pass

    return DataType.unknown
