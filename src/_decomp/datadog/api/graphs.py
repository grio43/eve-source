#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\graphs.py
from datadog.util.compat import urlparse
from datadog.api.resources import CreateableAPIResource, ActionAPIResource, GetableAPIResource, ListableAPIResource

class Graph(CreateableAPIResource, ActionAPIResource):
    _class_url = '/graph/snapshot'

    @classmethod
    def create(cls, **params):
        return super(Graph, cls).create(method='GET', **params)

    @classmethod
    def status(cls, snapshot_url):
        snap_path = urlparse(snapshot_url).path
        snap_path = snap_path.split('/snapshot/view/')[1].split('.png')[0]
        snapshot_status_url = '/graph/snapshot_status/{0}'.format(snap_path)
        return super(Graph, cls)._trigger_action('GET', snapshot_status_url)


class Embed(ListableAPIResource, GetableAPIResource, ActionAPIResource, CreateableAPIResource):
    _class_url = '/graph/embed'

    @classmethod
    def enable(cls, embed_id):
        return super(Embed, cls)._trigger_class_action('GET', id=embed_id, name='enable')

    @classmethod
    def revoke(cls, embed_id):
        return super(Embed, cls)._trigger_class_action('GET', id=embed_id, name='revoke')
