#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\ownergroups\client\link.py
import logging
from eve.client.script.ui.structure.accessGroups.groupInfoWnd import GroupInfoWnd
from eve.common.script.sys.idCheckers import IsNPCCorporation
import evelink
import localization
import stackless
import uthread2
log = logging.getLogger(__name__)
SCHEME = 'accessGroup'

def access_group_link(group_id, name = None):
    if name is None:
        group_info = get_access_group_info(group_id)
        if IsNPCCorporation(group_info.creatorID):
            name = cfg.eveowners.Get(group_info.creatorID).name
        else:
            name = group_info.name
    return evelink.Link(url=format_access_group_url(group_id), text=name)


def register_link_handlers(registry):
    registry.register(SCHEME, handle_access_group_link, hint=get_hint)


def handle_access_group_link(url):
    group_id = parse_access_group_url(url)
    GroupInfoWnd.Open(groupID=group_id, windowID='groupInfoWnd_{}'.format(group_id))


def get_hint(url):
    group_id = parse_access_group_url(url)
    group_info = get_access_group_info(group_id)
    if group_info:
        return localization.GetByLabel('UI/Structures/AccessGroups/AccessGroupHint', groupName=group_info['name'])


def parse_access_group_url(url):
    start = url.index(':') + 1
    return int(url[start:])


def format_access_group_url(group_id):
    return u'{}:{}'.format(SCHEME, group_id)


def get_access_group_info(group_id):
    allow_block = not stackless.getcurrent().block_trap
    if allow_block:
        structure_controllers_service = get_service('structureControllers')
    else:
        structure_controllers_service = get_service_non_blocking('structureControllers')
        if structure_controllers_service is None:
            return
    controller = structure_controllers_service.GetAccessGroupController()
    group_info = controller.GetGroupInfoFromID(group_id, fetchToServer=allow_block)
    if group_info is None and allow_block:
        raise KeyError('No access group with ID {} found'.format(group_id))
    return group_info


def get_service(name):
    return sm.GetService(name)


def get_service_non_blocking(name):
    service = sm.GetServiceIfRunning(name)
    if service is None:
        uthread2.start_tasklet(sm.StartService, name)
    return service
