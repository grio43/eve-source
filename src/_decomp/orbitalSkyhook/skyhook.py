#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\orbitalSkyhook\skyhook.py
from orbitalSkyhook.const import STATES

def LookupState(state):
    if state:
        state = str(state).lower()
        for value, name in STATES.iteritems():
            if str(value) == state:
                return value
            if name.startswith(state):
                return value
