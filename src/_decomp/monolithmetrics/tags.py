#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithmetrics\tags.py
import logging
import monolithconfig
import _datadog
import monolithgeoip2
log = logging.getLogger('monolithmetrics.tags')
UNIVERSE_TAG = 'universe:'
MACHO_NODE_INDEX_TAG = 'machoNet.nodeIndex:'
MACHO_MACHINE_NAME_TAG = 'machoNet.machineName:'
MACHO_SERVICE_MASK_TAG = 'machoNet.serviceMask:'
MACHO_CLUSTER_GROUP_TAG = 'machoNet.clusterGroup:'

def set_universe(universe):
    _set_datadog_tag(UNIVERSE_TAG, universe)


def set_macho_machine_name(machine_name):
    _set_datadog_tag(MACHO_MACHINE_NAME_TAG, machine_name)


def set_macho_service_mask(service_mask):
    _set_datadog_tag(MACHO_SERVICE_MASK_TAG, service_mask)


def set_macho_node_index(node_index):
    _set_datadog_tag(MACHO_NODE_INDEX_TAG, node_index)


def set_macho_cluster_group(cluster_group):
    _set_datadog_tag(MACHO_CLUSTER_GROUP_TAG, cluster_group)


def _set_datadog_tag(tag_name, value):
    if monolithconfig.on_client():
        return
    try:
        for tag in _datadog.client.constant_tags:
            if tag.startswith(tag_name):
                _datadog.client.constant_tags.remove(tag)

        _datadog.client.constant_tags.append(tag_name + str(value))
    except Exception:
        log.error('Failed to set constant_tag for DataDog', exc_info=1, extra={'tag_name': tag_name,
         'value': value})


def get_geo_tags(ipaddress):
    country_result = monolithgeoip2.country(ipaddress)
    tags = []
    if country_result and country_result.country and country_result.country.name:
        tags.append('country:' + country_result.country.name)
    else:
        tags.append('country:Unknown')
    if country_result and country_result.continent and country_result.continent.name:
        tags.append('continent:' + country_result.continent.name)
    else:
        tags.append('continent:Unknown')
    return tags
