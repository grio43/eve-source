#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\__init__.py
import uthread2
from .provider_type import ProviderType
_job_board_service = None

def get_job_board_service():
    global _job_board_service
    from .job_board_service import JobBoardService
    if _job_board_service is None:
        _job_board_service = JobBoardService()
    return _job_board_service


def get_provider(provider_id):
    return get_job_board_service().get_provider(provider_id=provider_id)


def get_provider_for_feature_tag(feature_tag_id):
    return get_job_board_service().get_provider_for_feature_tag(feature_tag_id=feature_tag_id)


def get_job_id(instance_id, provider_id):
    provider = get_job_board_service().get_provider(provider_id=provider_id)
    if provider:
        return provider.get_job_id(instance_id)


def get_primary_feature_tags():
    return get_job_board_service().storage.primary_feature_tags


def open_corporation_goal(goal_id):
    from jobboard.client.features.corporation_goals import CorporationGoalsProvider
    get_job_board_service().open_job(CorporationGoalsProvider.get_job_id(goal_id))


def open_daily_goal(goal_id):
    from jobboard.client.features.daily_goals import DailyGoalsProvider
    job_id = DailyGoalsProvider.get_job_id(goal_id)
    if job_id:
        get_job_board_service().open_job(job_id)


def open_browse_page(content_tag_id):
    get_job_board_service().open_browse_page(content_tag_id=content_tag_id)


def open_mission(agent_id, character_id = None):
    from jobboard.client.features.agent_missions import AgentMissionsJobProvider
    if character_id and character_id != session.charid:
        agent_mission_provider = get_job_board_service().get_provider(AgentMissionsJobProvider.PROVIDER_ID)
        if agent_mission_provider:
            uthread2.start_tasklet(agent_mission_provider.fetch_fleet_members_mission, agent_id, character_id)
        instance_id = u'{}_{}'.format(agent_id, character_id)
        instanced_window = True
    else:
        instance_id = agent_id
        instanced_window = None
    get_job_board_service().open_job(AgentMissionsJobProvider.get_job_id(instance_id), instanced_window)


def get_combat_anomaly_job(dungeon_instance_id, wait = True):
    from jobboard.client.features.dungeons import CombatAnomaliesProvider
    return get_job_board_service().get_job(CombatAnomaliesProvider.get_job_id(dungeon_instance_id), wait=wait, show_error=False)


def get_homefront_operation_job(dungeon_instance_id, wait = True):
    from jobboard.client.features.dungeons import HomefrontOperationsProvider
    return get_job_board_service().get_job(HomefrontOperationsProvider.get_job_id(dungeon_instance_id), wait=wait, show_error=False)


def get_agent_mission_job(agent_id, wait = True):
    from jobboard.client.features.agent_missions import AgentMissionsJobProvider
    return get_job_board_service().get_job(AgentMissionsJobProvider.get_job_id(agent_id), wait=wait, show_error=False)


def get_ore_anomaly_job(dungeon_instance_id, wait = True):
    from jobboard.client.features.dungeons import OreAnomaliesProvider
    return get_job_board_service().get_job(OreAnomaliesProvider.get_job_id(dungeon_instance_id), wait=wait, show_error=False)


def get_ice_belt_job(dungeon_instance_id, wait = True):
    from jobboard.client.features.dungeons import IceBeltsProvider
    return get_job_board_service().get_job(IceBeltsProvider.get_job_id(dungeon_instance_id), wait=wait, show_error=False)


def get_factional_warfare_job(dungeon_instance_id, wait = True):
    from jobboard.client.features.dungeons import FactionalWarfareProvider
    return get_job_board_service().get_job(FactionalWarfareProvider.get_job_id(dungeon_instance_id), wait=wait, show_error=False)


def get_fw_enlistment_job(faction_id, wait = True):
    from jobboard.client.features.factional_warfare_enlistment import FactionalWarfareEnlistmentProvider
    return get_job_board_service().get_job(FactionalWarfareEnlistmentProvider.get_job_id(faction_id), wait=wait, show_error=False)


def get_pirate_insurgency_job(dungeon_instance_id, wait = True):
    from jobboard.client.features.dungeons import PirateInsurgenciesProvider
    return get_job_board_service().get_job(PirateInsurgenciesProvider.get_job_id(dungeon_instance_id), wait=wait, show_error=False)


def get_corporation_goal_job(goal_id, wait = True):
    from jobboard.client.features.corporation_goals import CorporationGoalsProvider
    return get_job_board_service().get_job(CorporationGoalsProvider.get_job_id(goal_id), wait=wait, show_error=False)


def get_world_event_job(tale_id, wait = True):
    from jobboard.client.features.world_events import WorldEventsProvider
    return get_job_board_service().get_job(WorldEventsProvider.get_job_id(tale_id), wait=wait, show_error=False)


def open_world_event(tale_id):
    from jobboard.client.features.world_events import WorldEventsProvider
    job_id = WorldEventsProvider.get_job_id(tale_id)
    if job_id:
        get_job_board_service().open_job(job_id)
