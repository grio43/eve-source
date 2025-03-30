#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\blinker\util.py
import math

def get_element_bounding_box(element):
    left, top, width, height = element.GetAbsolute()
    rotation = getattr(element, 'rotation', None)
    if rotation is not None and rotation != 0.0:
        top_left = (left, top)
        rel_top_right = vec2_rotate(width, 0, -rotation)
        top_right = (left + rel_top_right[0], top + rel_top_right[1])
        rel_bottom_left = vec2_rotate(0, height, -rotation)
        bottom_left = (left + rel_bottom_left[0], top + rel_bottom_left[1])
        rel_bottom_right = vec2_rotate(width, height, -rotation)
        bottom_right = (left + rel_bottom_right[0], top + rel_bottom_right[1])
        right = left
        bottom = top
        for v in (top_left,
         top_right,
         bottom_left,
         bottom_right):
            left = min(left, v[0])
            top = min(top, v[1])
            right = max(right, v[0])
            bottom = max(bottom, v[1])

        width = right - left
        height = bottom - top
    return (left,
     top,
     width,
     height)


def vec2_rotate(x, y, angle):
    return (x * math.cos(angle) - y * math.sin(angle), x * math.sin(angle) + y * math.cos(angle))
