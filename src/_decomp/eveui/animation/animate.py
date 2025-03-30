#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\animation\animate.py
import functools
from carbonui.uianimations import animations
import uthread2
from ._data_type import DataType, detect_attribute_data_type, validate_data_type
from .curve import CurveType

def animate(obj, attribute_name, end_value, start_value = None, duration = 1.0, loops = 1, curve_type = CurveType.smooth, on_complete = None, sleep = False, use_simulation_time = False, time_offset = 0.0):
    if start_value is None:
        start_value = _get_start_value(obj, attribute_name)
    if loops == 0:
        raise ValueError('Zero is not a valid number of loops')
    target_data_type = detect_attribute_data_type(obj, attribute_name)
    if target_data_type is DataType.unknown:
        raise TypeError('The animated attribute has an unknown data type')
    validate_data_type(end_value, target_data_type)
    validate_data_type(start_value, target_data_type)
    curve_set = None
    if use_simulation_time:
        curve_set = animations.CreateCurveSet(useRealTime=False)
    final_value = end_value
    if curve_type in (CurveType.wave, CurveType.bounce):
        final_value = start_value
    callback = functools.partial(_force_end_value, obj, attribute_name, final_value, on_complete)
    animation_func = _get_animation_function(target_data_type)
    if sleep:
        animation_func = _wait_until_finished(animation_func)
    animation_func(obj, attribute_name=attribute_name, start_value=start_value, end_value=end_value, duration=duration, loops=loops, curve_type=curve_type, curve_set=curve_set, on_complete=callback, time_offset=time_offset)


def _wait_until_finished(animation_func):
    channel = uthread2.queue_channel()

    def wrapped(*args, **kwargs):
        new_callback = functools.partial(_signal_on_finished, channel=channel, callback=kwargs.get('on_complete', None))
        kwargs['on_complete'] = new_callback
        animation_func(*args, **kwargs)
        channel.receive()

    return wrapped


def _get_start_value(obj, attribute_name):
    start_value = getattr(obj, attribute_name)
    if hasattr(start_value, 'GetRGBA'):
        start_value = start_value.GetRGBA()
    return start_value


def _signal_on_finished(channel, callback):
    channel.send(None)
    if callback:
        callback()


def _force_end_value(obj, attribute_name, value, callback):
    setattr(obj, attribute_name, value)
    if callback:
        callback()


def _get_animation_function(data_type):
    if data_type is DataType.scalar:
        return _animate_scalar
    if data_type is DataType.color:
        return _animate_color
    if data_type is DataType.vector2:
        return _animate_vector2
    if data_type is DataType.vector3:
        return _animate_vector3
    if data_type is DataType.quaternion:
        return _animate_quaternion
    raise TypeError('Unsupported data type {}'.format(data_type))


def _animate_color(obj, attribute_name, start_value, end_value, duration, loops, curve_type, curve_set, on_complete, time_offset):
    animations.SpColorMorphTo(obj, attrName=attribute_name, startColor=start_value, endColor=end_value, duration=duration, loops=loops, curveType=curve_type.value, callback=on_complete, timeOffset=time_offset, curveSet=curve_set)


def _animate_scalar(obj, attribute_name, start_value, end_value, duration, loops, curve_type, curve_set, on_complete, time_offset):
    animations.MorphScalar(obj, attrName=attribute_name, startVal=start_value, endVal=end_value, duration=duration, loops=loops, curveType=curve_type.value, callback=on_complete, curveSet=curve_set, timeOffset=time_offset)


def _animate_vector2(obj, attribute_name, start_value, end_value, duration, loops, curve_type, curve_set, on_complete, time_offset):
    animations.MorphVector2(obj, attrName=attribute_name, startVal=start_value, endVal=end_value, duration=duration, loops=loops, curveType=curve_type.value, callback=on_complete, curveSet=curve_set, timeOffset=time_offset)


def _animate_vector3(obj, attribute_name, start_value, end_value, duration, loops, curve_type, curve_set, on_complete, time_offset):
    animations.MorphVector3(obj, attrName=attribute_name, startVal=start_value, endVal=end_value, duration=duration, loops=loops, curveType=curve_type.value, callback=on_complete, curveSet=curve_set, timeOffset=time_offset)


def _animate_quaternion(obj, attribute_name, start_value, end_value, duration, loops, curve_type, curve_set, on_complete, time_offset):
    animations.MorphQuaternion(obj, attrName=attribute_name, startVal=start_value, endVal=end_value, duration=duration, loops=loops, curveType=curve_type.value, callback=on_complete, curveSet=curve_set, timeOffset=time_offset)
