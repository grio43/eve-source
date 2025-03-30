#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\statscapture\vm_metrics_reporter.py
import os
import platform
import time
try:
    import requests
except ImportError:
    pass

import logmodule
log = logmodule.GetChannel('probe')
VICTORIA_METRICS_BASE_URL = 'https://vm-single.dev.evetech.net/api/v1/import/csv?'

def format_url_and_payload(measurement_name, results, branch_name, machine_type):
    time_stamp = '%d' % time.time()
    machine_name = platform.node()
    python_version = platform.python_version()
    data_list = [('time', 'unix_s', time_stamp),
     ('label', 'branch', branch_name.replace(' ', '_')),
     ('label', 'machine', machine_name),
     ('label', 'machine_type', machine_type.replace(' ', '_')),
     ('label', 'measurement_name', measurement_name.replace(' ', '_').replace(',', '').replace('(', '').replace(')', ''))]
    url_format = 'format='
    payload = ''
    i = 1
    for value_type, key, value in data_list:
        url_format += '%d:%s:%s,' % (i, value_type, key)
        payload += '%s,' % value
        i += 1

    for key, value in results.items():
        if isinstance(value, float):
            key = 'eve_probe_' + key.lower().replace(' ', '_').replace('/', '_')
            url_format += '%d:metric:%s,' % (i, key)
            payload += '%.6f,' % value
            i += 1

    url_format = url_format[:-1]
    payload = payload[:-1]
    return (url_format, payload)


def send_metrics(url, payload):
    r = requests.post(url, data=payload, timeout=10)
    print ('Response code from Victoria Metrics: ', r.status_code)


def send_metrics_wrapper(url, payload):
    try:
        import blue
        import uthread2
        try:
            from scheduler import getcurrent
        except ImportError:
            from stackless import getcurrent

        if getcurrent().is_main:
            print 'Sending to vm through tasklet'
            t = uthread2.StartTasklet(send_metrics, url, payload)
            i = 0
            while t.is_alive():
                blue.os.Pump()
                i += 1
                if i > 500:
                    raise TimeoutError('Waited too long for sending results')

        else:
            print 'Sending to vm directly'
            send_metrics(url, payload)
    except ImportError:
        print 'Sending without blue'
        send_metrics(url, payload)


def send_metrics_to_victoria_metrics(measurement_name, results, base_url, branch_name = None, machine_type = 'manual'):
    if base_url is None:
        base_url = VICTORIA_METRICS_BASE_URL
    if branch_name is None:
        branch_name = 'EVE-' + os.getenv('TC_EVE_BRANCH_SHORTNAME')
        if branch_name is None:
            branch_name = 'UNKNOWN'
    url_format, payload = format_url_and_payload(measurement_name, results, branch_name, machine_type)
    url = base_url + url_format
    log.Log('Send metrics: %s + %s' % (url, payload), logmodule.LGWARN)
    send_metrics_wrapper(url, payload)
