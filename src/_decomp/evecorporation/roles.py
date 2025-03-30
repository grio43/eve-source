#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evecorporation\roles.py
import math
from eve.common.lib import appConst as const
from eveexceptions import UserError
from localization import GetByMessageID
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import corporationRolesLoader
except ImportError:
    corporationRolesLoader = None

try:
    import corporationRoleGroupsLoader
except ImportError:
    corporationRoleGroupsLoader = None

CORP_ROLE_GROUPS_ATTRS = ['roleGroupName',
 'roleMask',
 'appliesTo',
 'appliesToGrantable',
 'isLocational',
 'isDivisional',
 'roleGroupNameID']

class CorporationRolesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/corporationRoles.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/corporationRoles.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/corporationRoles.fsdbinary'
    __loader__ = corporationRolesLoader


class CorporationRoleGroups(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/corporationRoleGroups.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/corporationRoleGroups.fsdbinary'
    __loader__ = corporationRoleGroupsLoader


def _get_roles():
    return CorporationRolesLoader.GetData()


def iter_roles():
    for role_id, role in _get_roles().iteritems():
        yield (pow(2, role_id), role)


def iter_role_names():
    for role_id, role in iter_roles():
        yield (role_id, get_role_name(role_id, role))


def get_role(role_mask, default = None):
    role_id = int(math.log(role_mask, 2))
    return _get_roles().get(role_id, default)


def get_role_name(role_id, role = None):
    if not role:
        role = get_role(role_id)
    return GetByMessageID(getattr(role, 'nameID', None))


def get_role_description(role_id, role = None):
    if not role:
        role = get_role(role_id)
    return GetByMessageID(getattr(role, 'descriptionID', None))


def check_is_role_director(character_corporation_roles):
    if not is_corporation_role_director(character_corporation_roles):
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NotDirector')})


def is_corporation_role_director(character_corporation_roles):
    return const.corpRoleDirector & character_corporation_roles == const.corpRoleDirector


def get_corporation_role_groups():
    return CorporationRoleGroups.GetData()


def get_ceo_role_mask():
    return sum([ x for x, _ in iter_roles() ])
