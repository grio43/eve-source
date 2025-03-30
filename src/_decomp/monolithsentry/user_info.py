#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithsentry\user_info.py
import __builtin__

def get_user_info():
    current_session = getattr(__builtin__, 'session', None)
    user_info = {'id': get_machine_hash(),
     'machineHash': get_machine_hash()}
    if current_session:
        user_info = {'id': getattr(session, 'userid', get_machine_hash()),
         'charid': getattr(session, 'charid'),
         'machineHash': get_machine_hash()}
    return user_info


def get_machine_hash():
    import blue
    return blue.os.GetStartupArgValue('machineHash')
