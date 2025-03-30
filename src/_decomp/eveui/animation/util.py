#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\animation\util.py
from carbonui.uianimations import animations

def stop_animation(obj, attribute_name):
    animations.StopAnimation(obj, attribute_name)


def stop_all_animations(obj):
    animations.StopAllAnimations(obj)
