#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\api_client.py
import logging
import time
from datadog.api import _api_version, _max_timeouts, _backoff_period
from datadog.api.exceptions import ClientError, ApiError, HttpBackoff, HttpTimeout, HTTPError, ApiNotInitialized
from datadog.api.http_client import resolve_http_client
from datadog.util.compat import json, is_p3k
from eveprefs import boot
log = logging.getLogger('datadog.api')

class APIClient(object):
    _backoff_period = _backoff_period
    _max_timeouts = _max_timeouts
    _backoff_timestamp = None
    _timeout_counter = 0
    _api_version = _api_version
    _http_client = None

    @classmethod
    def _get_http_client(cls):
        if not cls._http_client:
            cls._http_client = resolve_http_client()
        return cls._http_client

    @classmethod
    def submit(cls, method, path, body = None, attach_host_name = False, response_formatter = None, error_formatter = None, **params):
        try:
            if not cls._should_submit():
                _, backoff_time_left = cls._backoff_status()
                raise HttpBackoff(backoff_time_left)
            from datadog.api import _api_key, _application_key, _api_host, _mute, _host_name, _proxies, _max_retries, _timeout, _cacert
            if _api_key is None:
                raise ApiNotInitialized("API key is not set. Please run 'initialize' method first.")
            params['api_key'] = _api_key
            if _application_key:
                params['application_key'] = _application_key
            if attach_host_name and body:
                if 'series' in body:
                    for obj_params in body['series']:
                        if obj_params.get('host', '') == '':
                            obj_params['host'] = _host_name

                elif body.get('host', '') == '':
                    body['host'] = _host_name
            if 'tags' in params and isinstance(params['tags'], list):
                params['tags'] = ','.join(params['tags'])
            headers = {}
            if isinstance(body, dict):
                body = json.dumps(body)
                headers['Content-Type'] = 'application/json'
            url = '{api_host}/api/{api_version}/{path}'.format(api_host=_api_host, api_version=cls._api_version, path=path.lstrip('/'))
            start_time = time.time()
            result = cls._get_http_client().request(method=method, url=url, headers=headers, params=params, data=body, timeout=_timeout, max_retries=_max_retries, proxies=_proxies, verify=_cacert)
            duration = round((time.time() - start_time) * 1000.0, 4)
            log.info('%s %s %s (%sms)' % (result.status_code,
             method,
             url,
             duration))
            cls._timeout_counter = 0
            content = result.content
            if content:
                try:
                    if is_p3k():
                        response_obj = json.loads(content.decode('utf-8'))
                    else:
                        response_obj = json.loads(content)
                except ValueError:
                    raise ValueError('Invalid JSON response: {0}'.format(content))

                if response_obj and 'errors' in response_obj:
                    raise ApiError(response_obj)
            else:
                response_obj = None
            if response_formatter is None:
                return response_obj
            return response_formatter(response_obj)
        except HTTPError as e:
            if e.status_code == 408 and boot.region == 'optic':
                pass
            else:
                raise
        except HttpTimeout:
            cls._timeout_counter += 1
            raise
        except ClientError as e:
            if _mute:
                log.error(str(e))
                if error_formatter is None:
                    return {'errors': e.args[0]}
                else:
                    return error_formatter({'errors': e.args[0]})
            else:
                raise
        except ApiError as e:
            if _mute:
                for error in e.args[0]['errors']:
                    log.error(str(error))

                if error_formatter is None:
                    return e.args[0]
                else:
                    return error_formatter(e.args[0])
            else:
                raise

    @classmethod
    def _should_submit(cls):
        now = time.time()
        should_submit = False
        if not cls._backoff_timestamp and cls._timeout_counter >= cls._max_timeouts:
            log.info('Max number of datadog timeouts exceeded, backing off for {0} seconds'.format(cls._backoff_period))
            cls._backoff_timestamp = now
            should_submit = False
        elif cls._backoff_timestamp:
            backed_off_time, backoff_time_left = cls._backoff_status()
            if backoff_time_left < 0:
                log.info('Exiting backoff state after {0} seconds, will try to submit metrics again'.format(backed_off_time))
                cls._backoff_timestamp = None
                cls._timeout_counter = 0
                should_submit = True
            else:
                log.info("In backoff state, won't submit metrics for another {0} seconds".format(backoff_time_left))
                should_submit = False
        else:
            should_submit = True
        return should_submit

    @classmethod
    def _backoff_status(cls):
        now = time.time()
        backed_off_time = now - cls._backoff_timestamp
        backoff_time_left = cls._backoff_period - backed_off_time
        return (round(backed_off_time, 2), round(backoff_time_left, 2))
