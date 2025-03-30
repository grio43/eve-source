#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\markers.py
import sys
import blue
import bluepy
GetCurrent = blue.pyos.taskletTimer.GetCurrent
ClockThis = sys.ClockThis

def Mark(context, function, *args, **kw):
    return ClockThis(context, function, *args, **kw)


def PushMark(context):
    return bluepy.PushTimer(context)


PopMark = bluepy.PopTimer
