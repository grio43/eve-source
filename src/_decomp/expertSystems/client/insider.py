#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\insider.py
from carbon.common.script.sys.serviceManager import ServiceManager
from expertSystems.client.service import ExpertSystemService
from expertSystems.data import get_expert_system, is_expert_system

def get_gm_menu_options(type_id):
    if not is_expert_system(type_id):
        return []
    expert_system = get_expert_system(type_id)
    my_expert_systems = ExpertSystemService.instance().GetMyExpertSystems()
    title = 'Expert System'
    attributes = []
    if expert_system.hidden:
        attributes.append('hidden')
    if expert_system.retired:
        attributes.append('retired')
    if attributes:
        title = '{} [{}]'.format(title, ','.join(attributes))
    options = [(title, None)]
    if type_id not in my_expert_systems:
        options.append(('Activate [{} days]'.format(expert_system.duration.days), activate_expert_system, (type_id,)))
    else:
        options.append(('Extend duration [+{} days]'.format(expert_system.duration.days), activate_expert_system, (type_id,)))
        options.append(('Deactivate', deactivate_expert_system, (type_id,)))
    options.append(None)
    return options


def activate_expert_system(type_id):
    _slash('/expertsystem add {}'.format(type_id))


def deactivate_expert_system(type_id):
    _slash('/expertsystem remove {}'.format(type_id))


def _slash(command):
    ServiceManager.Instance().RemoteSvc('slash').SlashCmd(command)
