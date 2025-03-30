#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\resources.py
from datadog.api.api_client import APIClient

class CreateableAPIResource(object):

    @classmethod
    def create(cls, attach_host_name = False, method = 'POST', id = None, params = None, **body):
        if params is None:
            params = {}
        if method == 'GET':
            return APIClient.submit('GET', cls._class_url, **body)
        elif id is None:
            return APIClient.submit('POST', cls._class_url, body, attach_host_name=attach_host_name, **params)
        else:
            return APIClient.submit('POST', (cls._class_url + '/' + str(id)), body, attach_host_name=attach_host_name, **params)


class SendableAPIResource(object):

    @classmethod
    def send(cls, attach_host_name = False, id = None, **body):
        if id is None:
            return APIClient.submit('POST', cls._class_url, body, attach_host_name=attach_host_name)
        else:
            return APIClient.submit('POST', cls._class_url + '/' + str(id), body, attach_host_name=attach_host_name)


class UpdatableAPIResource(object):

    @classmethod
    def update(cls, id, params = None, **body):
        if params is None:
            params = {}
        return APIClient.submit('PUT', (cls._class_url + '/' + str(id)), body, **params)


class DeletableAPIResource(object):

    @classmethod
    def delete(cls, id, **params):
        return APIClient.submit('DELETE', (cls._class_url + '/' + str(id)), **params)


class GetableAPIResource(object):

    @classmethod
    def get(cls, id, **params):
        return APIClient.submit('GET', (cls._class_url + '/' + str(id)), **params)


class ListableAPIResource(object):

    @classmethod
    def get_all(cls, **params):
        return APIClient.submit('GET', cls._class_url, **params)


class SearchableAPIResource(object):

    @classmethod
    def _search(cls, **params):
        return APIClient.submit('GET', cls._class_url, **params)


class ActionAPIResource(object):

    @classmethod
    def _trigger_class_action(cls, method, name, id = None, **params):
        if id is None:
            return APIClient.submit(method, cls._class_url + '/' + name, params)
        else:
            return APIClient.submit(method, cls._class_url + '/' + str(id) + '/' + name, params)

    @classmethod
    def _trigger_action(cls, method, name, id = None, **params):
        if id is None:
            return APIClient.submit(method, name, params)
        else:
            return APIClient.submit(method, name + '/' + str(id), params)
