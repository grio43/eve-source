#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evemissions\common\epic_arcs_data.py
import localization
from caching import Memoize
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import epicArcsLoader
except ImportError:
    epicArcsLoader = None

MESSAGE_CHAPTER_TITLE = 'messages.epicMission.journalText.chapterTitle'
MESSAGE_IN_PROGRESS = 'messages.epicMission.journalText.inProgressMessage'
MESSAGE_COMPLETED = 'messages.epicMission.journalText.completedMessage'

class EpicArcs(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/epicArcs.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/epicArcs.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/epicArcs.fsdbinary'
    __loader__ = epicArcsLoader


def _get_epic_arcs():
    return EpicArcs.GetData()


def _get_epic_arc(epic_arc_id):
    return _get_epic_arcs().get(epic_arc_id, None)


def _get_epic_arc_attribute(epic_arc_id, attr, default = None):
    epic_arc = _get_epic_arc(epic_arc_id)
    if epic_arc:
        return getattr(epic_arc, attr, default)


def iter_epic_arcs():
    return [ (epic_arc_id, epic_arc.epicArcNameID) for epic_arc_id, epic_arc in _get_epic_arcs().iteritems() ]


def get_epic_arc_faction_id(epic_arc_id):
    return _get_epic_arc_attribute(epic_arc_id, 'factionID')


def get_epic_arc_restart_interval(epic_arc_id):
    return _get_epic_arc_attribute(epic_arc_id, 'arcRestartInterval')


def get_next_epic_arc_missions(epic_arc_id, mission_id, default = None):
    missions = _get_epic_arc_attribute(epic_arc_id, 'missions')
    mission = missions.get(mission_id, None)
    if mission and mission.nextMissions:
        return mission.nextMissions
    return default


def get_epic_arc_missions(epic_arc_id):
    missions = _get_epic_arc_attribute(epic_arc_id, 'missions')
    if missions:
        return [ mission_id for mission_id in missions ]


def get_agent_in_epic_arc_mission(epic_arc_id, mission_id):
    missions = _get_epic_arc_attribute(epic_arc_id, 'missions')
    mission = missions.get(mission_id, None)
    if mission:
        return mission.agentID


def get_fail_mission_id(epic_arc_id, mission_id):
    missions = _get_epic_arc_attribute(epic_arc_id, 'missions')
    if missions is None:
        return
    mission = missions.get(mission_id, None)
    if mission:
        return mission.failMissionID


@Memoize
def get_all_start_missions():
    start_missions = {}
    for epic_arc_id, epic_arc in _get_epic_arcs().iteritems():
        next_missions = set()
        for mission_id, info in epic_arc.missions.iteritems():
            if info.nextMissions:
                next_missions.update(set(info.nextMissions))

        mission_ids = set(epic_arc.missions.iterkeys())
        start_missions[epic_arc_id] = mission_ids.difference(next_missions)

    return start_missions


def is_start_mission_in_epic_arc(epic_arc_id, mission_id):
    start_missions = get_all_start_missions()
    return mission_id in start_missions.get(epic_arc_id, set())


@Memoize
def get_end_missions_in_epic_arc(epic_arc_id):
    end_missions = set()
    epic_arc = _get_epic_arc(epic_arc_id)
    for mission_id, mission in epic_arc.missions.iteritems():
        if mission.nextMissions is None:
            end_missions.add(mission_id)

    return end_missions


def is_end_mission_in_epic_arc(epic_arc_id, mission_id):
    end_missions = get_end_missions_in_epic_arc(epic_arc_id)
    return mission_id in end_missions


def iter_epic_arc_missions():
    return [ (epic_arc_id, set(epic_arc.missions.iterkeys())) for epic_arc_id, epic_arc in _get_epic_arcs().iteritems() ]


def get_mission_ids_for_all_epic_arcs():
    missions = set()
    for _, mission_ids in iter_epic_arc_missions():
        missions.update(set(mission_ids))

    return missions


def epic_arc_exists(epic_arc_id):
    return epic_arc_id in _get_epic_arcs()


def get_epic_arc_icon(epic_arc_id):
    return _get_epic_arc_attribute(epic_arc_id, 'iconID')


def get_epic_arc_name_id(epic_arc_id):
    return _get_epic_arc_attribute(epic_arc_id, 'epicArcNameID')


def get_epic_arc_name(epic_arc_id, language_id = None, default = None):
    name_id = _get_epic_arc_attribute(epic_arc_id, 'epicArcNameID')
    if name_id is None:
        return default
    if language_id is not None:
        return localization.GetByMessageID(name_id, languageID=language_id) or default
    return localization.GetByMessageID(name_id) or default


@Memoize
def get_epic_arc_by_mission():
    epic_arc_by_mission = {}
    for epic_arc_id, mission_ids in iter_epic_arc_missions():
        for mission_id in mission_ids:
            epic_arc_by_mission[mission_id] = epic_arc_id

    return epic_arc_by_mission


def get_epic_arc_for_mission(mission_id):
    epic_arc_by_mission = get_epic_arc_by_mission()
    return epic_arc_by_mission.get(mission_id, None)
