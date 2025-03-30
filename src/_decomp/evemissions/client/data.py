#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evemissions\client\data.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import missionsLoader
except ImportError:
    missionsLoader = None

class ClientMissionsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/missions.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/missions.fsdbinary'
    __loader__ = missionsLoader


def _get_missions():
    return ClientMissionsLoader.GetData()


def get_mission(mission_id):
    return _get_missions().get(mission_id, None)


def get_mission_name_id(mission_id):
    return get_mission(mission_id).nameID


def get_fixed_lp_rewards(mission_id, default = None):
    mission = get_mission(mission_id)
    if not mission:
        return (default, default)
    alpha = mission.fixedLpRewardAlpha
    if not isinstance(alpha, int):
        alpha = (default, default)
    omega = mission.fixedLpRewardOmega
    if not isinstance(omega, int):
        omega = (default, default)
    return (alpha, omega)


def has_standing_rewards(mission_id, default = True):
    mission = get_mission(mission_id)
    if not mission:
        return default
    value = mission.hasStandingRewards
    if value is None:
        return default
    return value
