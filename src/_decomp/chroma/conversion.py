#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chroma\conversion.py
from __future__ import division
import mathext

def rgb_to_hsb(r, g, b):
    r = mathext.clamp(r, 0.0, 1.0)
    g = mathext.clamp(g, 0.0, 1.0)
    b = mathext.clamp(b, 0.0, 1.0)
    value_min = min(r, g, b)
    value_max = max(r, g, b)
    value_diff = value_max - value_min
    brightness = value_max
    if mathext.is_almost_zero(value_diff):
        return (0.0, 0.0, brightness)
    saturation = value_diff / value_max
    dr = ((brightness - r) / 6 + value_diff / 2) / value_diff
    dg = ((brightness - g) / 6 + value_diff / 2) / value_diff
    db = ((brightness - b) / 6 + value_diff / 2) / value_diff
    if r == brightness:
        hue = db - dg
    elif g == brightness:
        hue = 0.3333333333333333 + dr - db
    else:
        hue = 0.6666666666666666 + dg - dr
    if hue < 0:
        hue += 1
    if hue > 1:
        hue -= 1
    return (hue, saturation, brightness)


def hsb_to_rgb(h, s, b):
    h = mathext.clamp(h, 0.0, 1.0)
    s = mathext.clamp(s, 0.0, 1.0)
    b = mathext.clamp(b, 0.0, 1.0)
    if mathext.is_almost_zero(s):
        return (b, b, b)
    h *= 6
    if mathext.is_close(h, 6):
        h = 0.0
    i = int(h)
    x = b * (1 - s)
    y = b * (1 - s * (h - i))
    z = b * (1 - s * (1 - (h - i)))
    if i == 0:
        return (b, z, x)
    if i == 1:
        return (y, b, x)
    if i == 2:
        return (x, b, z)
    if i == 3:
        return (x, y, b)
    if i == 4:
        return (z, x, b)
    if i == 5:
        return (b, x, y)
