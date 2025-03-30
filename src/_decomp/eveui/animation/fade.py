#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\animation\fade.py
from .animate import animate
from .curve import CurveType

def fade(obj, start_value = None, end_value = 1.0, duration = 0.3, loops = 1, curve_type = CurveType.smooth, on_complete = None, sleep = False, use_simulation_time = False, time_offset = 0.0):
    animate(obj, attribute_name='opacity', start_value=start_value, end_value=end_value, duration=duration, loops=loops, curve_type=curve_type, on_complete=on_complete, sleep=sleep, use_simulation_time=use_simulation_time, time_offset=time_offset)


def fade_in(obj, end_value = 1.0, duration = 0.3, loops = 1, curve_type = CurveType.smooth, on_complete = None, sleep = False, use_simulation_time = False, time_offset = 0.0):
    fade(obj, end_value=end_value, duration=duration, loops=loops, curve_type=curve_type, on_complete=on_complete, sleep=sleep, use_simulation_time=use_simulation_time, time_offset=time_offset)


def fade_out(obj, duration = 0.3, loops = 1, curve_type = CurveType.smooth, on_complete = None, sleep = False, use_simulation_time = False, time_offset = 0.0):
    fade(obj, end_value=0.0, duration=duration, loops=loops, curve_type=curve_type, on_complete=on_complete, sleep=sleep, use_simulation_time=use_simulation_time, time_offset=time_offset)
