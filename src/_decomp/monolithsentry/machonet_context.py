#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithsentry\machonet_context.py
import monolithsentry
import sentry_sdk
machonet_context = {}

def set_macho_node_id(node_id):
    _update_client_macho_context('nodeID', node_id)


def set_macho_machine_id(machine_id):
    _update_client_macho_context('machineID', machine_id)


def set_macho_service_mask(service_mask):
    _update_client_macho_context('serviceMask', service_mask)


def set_macho_node_index(node_index):
    _update_client_macho_context('nodeIndex', node_index)


def set_macho_cluster_group(cluster_group):
    _update_client_macho_context('clusterGroup', cluster_group)


def _update_client_macho_context(key, value):
    machonet_context[key] = value
    with sentry_sdk.configure_scope() as scope:
        scope.set_extra(key, value)
    monolithsentry.set_sentry_crash_key()


def get_machonet_context():
    return machonet_context
