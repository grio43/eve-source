#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithsentry\dsn.py
import monolithconfig

def get_config_dsn():
    dsn = monolithconfig.get_value('sentry_io_dsn', 'prefs')
    return dsn
