#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\security\client\securitySvc.py
import collections
import logging
from carbon.common.script.sys.service import Service
from eveuniverse.security import SecurityClassFromLevel, securityClassHighSec, securityClassLowSec, securityClassZeroSec
from security.client.fonticons import get_font_icon_text
logger = logging.getLogger(__name__)
CHALLENGE_UPDATE_SLEEP_SECONDS = 1
SECURITY_CLASS_TO_STRING = {securityClassHighSec: 'High',
 securityClassLowSec: 'Low',
 securityClassZeroSec: 'Null'}
modified_security_level = collections.namedtuple('modified_security_level', 'solar_system_id modified_security_level')

def calculate_pseudo_security(security):
    if 0.0 < security < 0.05:
        return 0.05
    return security


class SecurityService(Service):
    __guid__ = 'svc.SecuritySvc'
    serviceName = 'svc.securitySvc'
    __displayname__ = 'SecurityService'
    __servicename__ = 'SecurityService'
    __dependencies__ = []
    __notifyevents__ = ['OnSecurityModified', 'OnSessionChanged']

    def Run(self, memStream = None):
        self.modified_security_levels = {}
        Service.Run(self, memStream=memStream)

    def Initialize(self):
        securityMgr = sm.RemoteSvc('securityMgr')
        modified_system_rows_by_solar_system_id = securityMgr.get_modified_systems()
        self.modified_security_levels = {solarSystemID:modified_security_level(data.solarSystemID, calculate_pseudo_security(data.modifiedSecurity)) for solarSystemID, data in modified_system_rows_by_solar_system_id.iteritems()}

    def OnSessionChanged(self, isRemote, sess, change):
        if 'solarsystemid2' in change and change['solarsystemid2'][0] is None:
            self.Initialize()

    def OnSecurityModified(self, solar_system_id, modifier_amount, new_security):
        self.modified_security_levels[solar_system_id] = modified_security_level(solar_system_id, calculate_pseudo_security(new_security))
        if solar_system_id == session.solarsystemid2:
            sm.ScatterEvent('OnCurrentSystemSecurityChanged')

    def get_modified_security_level(self, solar_system_id):
        if solar_system_id in self.modified_security_levels:
            return self.modified_security_levels[solar_system_id].modified_security_level
        return cfg.mapSystemCache[solar_system_id].pseudoSecurity

    def get_base_security_level(self, solar_system_id):
        return cfg.mapSystemCache[solar_system_id].pseudoSecurity

    def get_base_security_class(self, solar_system_id):
        baseSecurityLevel = cfg.mapSystemCache[solar_system_id].pseudoSecurity
        return SecurityClassFromLevel(baseSecurityLevel)

    def get_modified_security_class(self, solar_system_id):
        return SecurityClassFromLevel(self.get_modified_security_level(solar_system_id))

    def is_effective_high_sec_system(self, solar_system_id):
        return self.get_modified_security_class(solar_system_id) == securityClassHighSec

    def get_displayed_security_level(self, solar_system_id):
        security_level = self.get_modified_security_level(solar_system_id)
        return round(security_level, 1)

    def get_security_modifier_icon_text(self, solar_system_id):
        base_security_level = self.get_base_security_level(solar_system_id)
        modified_security_level = self.get_modified_security_level(solar_system_id)
        return get_font_icon_text(base_security_level, modified_security_level)

    def get_security_modifier_icon_res_path(self, solar_system_id):
        base_class = self.get_base_security_class(solar_system_id)
        modified_class = self.get_modified_security_class(solar_system_id)
        if base_class == modified_class:
            rounded_base_security_level = round(self.get_base_security_level(solar_system_id), 1)
            if self.get_displayed_security_level(solar_system_id) != rounded_base_security_level:
                return 'res:/UI/Texture/classes/Security/Unchanged_12x10.png'
            return ''
        base_class_string = SECURITY_CLASS_TO_STRING[base_class]
        modified_class_string = SECURITY_CLASS_TO_STRING[modified_class]
        return 'res:/UI/Texture/classes/Security/{base}To{modified}_12x10.png'.format(base=base_class_string, modified=modified_class_string)
