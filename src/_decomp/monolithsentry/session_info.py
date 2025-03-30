#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithsentry\session_info.py
import __builtin__
import pprint

def get_session_info():
    current_session = getattr(__builtin__, 'session', None)
    sane_info = None
    if current_session:
        sane_info = current_session.__dict__.copy()
        sane_info['sessionhist'] = 'Omitted by monolithsentry'
        sane_info['calltimes'] = 'Omitted by monolithsentry'
        sane_info['machoObjectConnectionsByObjectID'] = 'Omitted by monolithsentry'
    return pprint.pformat(sane_info)
