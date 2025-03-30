#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\heronotification\animation.py
import datetime
import random
import math
import eveui
import gametime
import uthread2
from carbonui import uiconst
from carbonui.uianimations import animations

def garble_reveal_label(label, text, garble = '+/\\|%#-@!?<>(){}', step_duration = datetime.timedelta(milliseconds=50), time_offset = None, opacity = 1.0):
    label.text = text
    final_width = label.width
    if time_offset is not None:
        uthread2.sleep(time_offset.total_seconds())

    def set_final_width():
        label.width = final_width

    animations.MorphScalar(label, 'width', startVal=final_width * 0.2, endVal=final_width, duration=len(text) * step_duration.total_seconds(), curveType=uiconst.ANIM_LINEAR, callback=set_final_width)
    animations.FadeTo(label, startVal=label.opacity, endVal=opacity, duration=0.3)
    start = gametime.now()
    last_i = 0
    while True:
        now = gametime.now()
        i = int(math.floor((now - start).total_seconds() / step_duration.total_seconds()))
        if i >= len(text):
            break
        if i > last_i:
            new_text = text[:i]
            if text[i] != ' ':
                new_text += random.choice(garble)
            label.text = new_text
            last_i = i
        eveui.wait_for_next_frame()

    label.text = text
