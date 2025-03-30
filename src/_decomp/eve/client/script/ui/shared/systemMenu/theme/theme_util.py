#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\theme\theme_util.py
from chroma import Color

def get_with_capped_brightness(color, min = 0.0, max = 1.0):
    if color.brightness < min:
        return Color.from_hsb(color.hue, color.brightness, min)
    elif color.brightness > max:
        return Color.from_hsb(color.hue, color.brightness, max)
    else:
        return color
