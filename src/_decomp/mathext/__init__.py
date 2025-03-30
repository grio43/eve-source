#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\mathext\__init__.py
from math import *
from mathext.triangulate import triangulate
inf = float('inf')

def clamp(value, low, high):
    return max(low, min(value, high))


def truncate(value, decimals = 0):
    if decimals < 0:
        raise ValueError('Number of decimals must be zero or a positive number')
    shift = float(pow(10, decimals))
    return float(int(value * shift)) / shift


def lerp(a, b, t):
    return a + clamp(t, 0.0, 1.0) * (b - a)


def inverse_lerp(a, b, v):
    if a != b:
        return clamp((v - a) / float(b - a), 0.0, 1.0)
    else:
        return 0.0


def round_to_significant(value, significant_digits):
    if significant_digits < 1:
        raise ValueError("Significant digits can't be fewer than one")
    number_of_digits = 0
    if not is_close(value, 0):
        number_of_digits = significant_digits - 1 - int(floor(log10(abs(value))))
    return round(value, number_of_digits)


def is_close(a, b, rel_tol = 1e-09, abs_tol = 0.0):
    if rel_tol < 0.0 or abs_tol < 0.0:
        raise ValueError('error tolerances must be non-negative')
    if a == b:
        return True
    if isinf(a) or isinf(b):
        return False
    diff = fabs(b - a)
    return diff <= fabs(rel_tol * b) or diff <= fabs(rel_tol * a) or diff <= abs_tol


def is_almost_zero(value, tolerance = 1e-09):
    return is_close(value, 0.0, rel_tol=0.0, abs_tol=tolerance)
