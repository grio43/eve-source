#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\util.py
from carbon.common.lib.const import maxBigint
from eve.common.script.sys import idCheckers
from metadata.common.content_tags import ContentTagTypes
import localization
import eveicon
from jobboard.client import get_job_board_service
import logging
logger = logging.getLogger('job_board')

def check_content_tags(filters, content_tag_ids):
    if not filters:
        return True
    if not content_tag_ids:
        return False
    for key in filters:
        if key not in content_tag_ids:
            return False

    return True


def get_content_tags_for_jobs(jobs):
    result = {}
    for job in jobs:
        for content_tag in job.content_tags.itervalues():
            result[content_tag.id] = content_tag

    return result


def sort_content_tags(content_tags, important_tags = None):
    order_by_tag_type = {ContentTagTypes.feature: 1,
     ContentTagTypes.career_path: 2,
     ContentTagTypes.activity: 3}
    if important_tags is None:
        important_tags = []
    return sorted(content_tags, key=lambda tag: (order_by_tag_type.get(tag.tag_type, 4), tag.id not in important_tags, tag.title))


def sort_jobs(jobs):
    return sorted(jobs, key=lambda job: (job.jumps, -job.get_player_relevance_score(), job.title.lower()))


def add_track_job_menu_option(menu_data, job):
    if not job.is_trackable and not job.is_tracked:
        return
    is_tracked = job.is_tracked
    menu_data.AddEntry(localization.GetByLabel('UI/Common/Untrack' if is_tracked else 'UI/Common/Track'), func=lambda *args, **kwargs: job.toggle_tracked_by_player(), texturePath=eveicon.camera_untrack if is_tracked else eveicon.visibility)


def add_location_menu_option(menu_data, location_id):
    if not location_id:
        return
    text = u'{}: {}'.format(localization.GetByLabel('UI/Common/Location'), cfg.evelocations.Get(location_id).locationName)
    menu_data.AddEntry(text, subMenuData=sm.GetService('menu').CelestialMenu(location_id))


def add_open_job_menu_option(menu_data, job_id):
    menu_data.AddEntry(localization.GetByLabel('UI/Opportunities/ViewOpportunity'), func=lambda *args, **kwargs: get_job_board_service().open_job(job_id))


def get_provider_id_from_job_id(job_id):
    try:
        provider_id, _instance_id = job_id.split(':')
        return provider_id
    except Exception as e:
        logger.error('Failed to get provider id from job id %s e=%s', job_id, e)
        return None


def get_instance_id_from_job_id(job_id):
    _provider_id, instance_id = job_id.split(':')
    return instance_id


def get_closest_solarsystem_in_locations_from(origin_solarsystem_id, location_id_set, map_service, pathfinder_service):
    if origin_solarsystem_id in location_id_set:
        return (origin_solarsystem_id, 0)
    current_region_id = map_service.GetRegionForSolarSystem(origin_solarsystem_id)
    current_constellation_id = map_service.GetConstellationForSolarSystem(origin_solarsystem_id)
    if current_region_id in location_id_set or current_constellation_id in location_id_set:
        return (origin_solarsystem_id, 0)
    location_id_set = {location_id for location_id in location_id_set if map_service.GetParent(location_id) not in location_id_set}
    solarsystem_id_set = set()
    for location_id in location_id_set:
        if idCheckers.IsSolarSystem(location_id):
            solarsystem_id_set.add(location_id)
        else:
            solarsystem_id_set.update(map_service.GetSolarSystemIDsIn(location_id))

    closest_solarsystem_id = None
    closest_distance = maxBigint
    for solarsystem_id in solarsystem_id_set:
        distance = pathfinder_service.GetAutopilotJumpCount(origin_solarsystem_id, solarsystem_id)
        if distance < closest_distance:
            closest_distance = distance
            closest_solarsystem_id = solarsystem_id

    return (closest_solarsystem_id, closest_distance)
