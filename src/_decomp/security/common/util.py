#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\security\common\util.py
from eveprefs import boot

def get_modified_security_level(solar_system_id):
    if boot.role == u'client':
        return sm.GetService('securitySvc').get_modified_security_level(solar_system_id)
    else:
        return sm.GetService('securityMgr').get_modified_security_level(solar_system_id)
