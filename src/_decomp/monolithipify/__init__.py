#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithipify\__init__.py
import logging
from requests import get
import monolithconfig
log = logging.getLogger(__name__)
API_URI = 'https://api.ipify.org'

def get_public_ip():
    try:
        version = monolithconfig.get_value('version', 'boot')
        if not version:
            version = 'v0'
        user_agent = 'ccp/eve online ' + version
        ip_address = get(API_URI, headers={'user-agent': user_agent})
        return ip_address.text
    except Exception:
        log.warning('Failed to get public IP', exc_info=1)
        return None
