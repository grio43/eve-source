#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\marketutil\ticks.py
from math import log10, floor, ceil
TICK_SIGNIFICANT_FIGURES = 4
ISK_DECIMAL_PLACES = 2
ISK_MINIMUM_DIVISION = 1.0 / 10 ** ISK_DECIMAL_PLACES
MAX_TICK = 922300000000000.0

def round_down_to_next_tick(value):
    if value < ISK_MINIMUM_DIVISION:
        raise ValueError('Value cannot be less than minimum ISK division')
    if value > MAX_TICK:
        raise ValueError('Value too large')
    value += ISK_MINIMUM_DIVISION / 100
    exponent = int(floor(log10(value)))
    shift_size = 10 ** (exponent - TICK_SIGNIFICANT_FIGURES + 1)
    result = floor(value / shift_size) * shift_size
    return round(result, ISK_DECIMAL_PLACES)


def round_up_to_next_tick(value):
    if value <= 0:
        raise ValueError('Value must be positive')
    if value >= MAX_TICK:
        raise ValueError('Value too large')
    value -= ISK_MINIMUM_DIVISION / 100
    exponent = int(floor(log10(value)))
    shift_size = 10 ** (exponent - TICK_SIGNIFICANT_FIGURES + 1)
    result = ceil(value / shift_size) * shift_size
    return round(result, ISK_DECIMAL_PLACES)


def increment_to_next_tick(value):
    return round_up_to_next_tick(value + ISK_MINIMUM_DIVISION)


def decrement_to_next_tick(value):
    return round_down_to_next_tick(value - ISK_MINIMUM_DIVISION)


def is_tick(value):
    rounded = round_down_to_next_tick(value)
    return rounded == value
