#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\crates\crateutil.py
from storage import CratesStaticData
from crates.storage import CrateDoesNotExistError

def is_fixed_crate(type_id):
    try:
        type_crate_data = CratesStaticData().get_crate_by_type_id(type_id)
        return type_crate_data.lootPresentationType == 'fixed'
    except CrateDoesNotExistError:
        return False


def is_crate(type_id):
    type_crate_data = CratesStaticData()
    return type_crate_data.is_crate(type_id)


def is_cargo_blocked_crate(type_id):
    type_crate_data = CratesStaticData()
    if not is_crate(type_id):
        return False
    type_crate_data = type_crate_data.get_crate_by_type_id(type_id)
    return type_crate_data.isBlockedFromCargo
