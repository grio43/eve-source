#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithsentry\minidump.py
import __builtin__
from monolithsentry.environment import get_environment
from monolithsentry.machonet_context import get_machonet_context
from monolithsentry.tags import get_tags
from monolithsentry.geoip2_tags import get_geoip_tags
from monolithsentry.session_info import get_session_info
from monolithsentry.user_info import get_user_info
from monolithconfig import get_value

def get_tool():
    import blue
    args = blue.pyos.GetArg()[1:]
    for each in iter(args):
        split = each.split('=')
        if split[0].strip() == '/tools' and len(split) > 1:
            tool = split[1].strip()
            return tool


def set_sentry_crash_key():
    import blue
    import json
    tags = get_tags()
    geo_tags = get_geoip_tags()
    if geo_tags:
        tags.update(get_geoip_tags())
    tool = get_tool()
    if tool:
        tags.update({'tool': tool})
    crash_key = {'release': get_value('build', 'boot'),
     'environment': get_environment(),
     'tags': tags,
     'user': get_user_info()}
    sane_session_info = get_session_info()
    if sane_session_info:
        blue.SetCrashKeyValues('session', sane_session_info)
    sentry_key = json.dumps(crash_key)
    blue.SetCrashKeyValues('sentry', sentry_key)
