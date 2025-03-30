#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\service_checks.py
from datadog.api.constants import CheckStatus
from datadog.api.exceptions import ApiError
from datadog.api.resources import ActionAPIResource

class ServiceCheck(ActionAPIResource):

    @classmethod
    def check(cls, **params):
        if 'status' in params and params['status'] not in CheckStatus.ALL:
            raise ApiError('Invalid status, expected one of: %s' % ', '.join((str(v) for v in CheckStatus.ALL)))
        return super(ServiceCheck, cls)._trigger_action('POST', 'check_run', **params)
