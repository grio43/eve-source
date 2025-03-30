#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\__init__.py
import logging
import os
import os.path
from datadog import api
from datadog.dogstatsd import DogStatsd, statsd
from datadog.threadstats import ThreadStats
from datadog.util.compat import iteritems, NullHandler
from datadog.util.config import get_version
from datadog.util.hostname import get_hostname
__version__ = get_version()
logging.getLogger('datadog.api').addHandler(NullHandler())
logging.getLogger('datadog.dogstatsd').addHandler(NullHandler())
logging.getLogger('datadog.threadstats').addHandler(NullHandler())

def initialize(api_key = None, app_key = None, host_name = None, api_host = None, statsd_host = None, statsd_port = None, statsd_use_default_route = False, **kwargs):
    api._api_key = api_key if api_key is not None else os.environ.get('DATADOG_API_KEY')
    api._application_key = app_key if app_key is not None else os.environ.get('DATADOG_APP_KEY')
    api._host_name = host_name if host_name is not None else get_hostname()
    api._api_host = api_host if api_host is not None else os.environ.get('DATADOG_HOST', 'https://app.datadoghq.com')
    if statsd_host or statsd_use_default_route:
        statsd.host = statsd.resolve_host(statsd_host, statsd_use_default_route)
    if statsd_port:
        statsd.port = int(statsd_port)
    for key, value in iteritems(kwargs):
        attribute = '_{0}'.format(key)
        setattr(api, attribute, value)
