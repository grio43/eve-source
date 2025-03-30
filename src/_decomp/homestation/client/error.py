#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\error.py
from carbonui.uicore import uicore
from homestation.client import text

class NotLoggedInError(Exception):
    pass


def handle_change_home_station_validation_error(error):
    reasons = u'<br><br>'.join((text.describe_change_home_station_validation_error(error_code) for error_code in error.errors))
    uicore.Message('SetHomeStationValidationError', {'reasons': reasons,
     'reason_count': len(error.errors)})


def handle_self_destruct_clone_validation_error(error):
    reasons = u'<br><br>'.join((text.describe_self_destruct_clone_validation_error(error_code) for error_code in error.errors))
    uicore.Message('SelfDestructCloneValidationError', {'reasons': reasons,
     'reason_count': len(error.errors)})
