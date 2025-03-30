#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\relevance_profile.py
from careergoals.client.career_goal_svc import get_career_goals_svc
from collections import defaultdict
from characterdata import careerpathconst
from metadata.common import ContentTags, ContentTagTypes, get_content_tag_type_id
import threadutils

class RelevanceProfile(object):

    @property
    def content_tag_scores(self):
        return {}

    @property
    def solar_system_id(self):
        return None

    def calculate_relevance_score(self, content_tag_ids, solar_system_id):
        tag_type_scores = defaultdict(int)
        for content_tag_id, content_tag_score in self.content_tag_scores.iteritems():
            if content_tag_id in content_tag_ids:
                tag_type_id = get_content_tag_type_id(content_tag_id)
                if content_tag_score > tag_type_scores[tag_type_id]:
                    tag_type_scores[tag_type_id] = content_tag_score

        score = sum(tag_type_scores.values())
        if score:
            score += _get_jump_score(self.solar_system_id, solar_system_id)
        return score


class JobRelevanceProfile(RelevanceProfile):

    def __init__(self, job, override_weights = None):
        self._job = job
        override_weights = override_weights or {}
        feature_tag = self._job.feature_tag
        if feature_tag and feature_tag.id not in override_weights:
            override_weights[feature_tag.id] = 15
        self._content_tag_scores = {content_tag_id:_get_weighted_score(content_tag_id, override_weights=override_weights) for content_tag_id in self._job.content_tag_ids}

    @property
    def content_tag_scores(self):
        return self._content_tag_scores

    @property
    def solar_system_id(self):
        return self._job.solar_system_id


class PlayerRelevanceProfile(RelevanceProfile):
    __notifyevents__ = ['OnIndustryJobClient', 'OnDungeonCompleted']

    def __init__(self):
        self._content_tag_scores = settings.char.ui.Get('opportunitiesRelevanceProfile', {})
        if not self._content_tag_scores:
            self._build_profile()
        self._register()

    def __del__(self):
        self._unregister()

    def _register(self):
        sm.RegisterNotify(self)

    def _unregister(self):
        sm.UnregisterNotify(self)

    def add_content_tag_scores(self, content_tag_ids):
        for content_tag_id in content_tag_ids:
            weighted_score = _get_weighted_score(content_tag_id)
            if content_tag_id not in self._content_tag_scores:
                self._content_tag_scores[content_tag_id] = weighted_score
            else:
                self._content_tag_scores[content_tag_id] += weighted_score

        settings.char.ui.Set('opportunitiesRelevanceProfile', self._content_tag_scores)

    @property
    def content_tag_scores(self):
        return self._content_tag_scores

    @property
    def solar_system_id(self):
        return session.solarsystemid2

    @threadutils.threaded
    def _build_profile(self):
        content_tags_count = defaultdict(int)
        for content_tag_id, count in _get_score_from_acp().iteritems():
            content_tags_count[content_tag_id] += count

        for content_tag_id, count in content_tags_count.iteritems():
            score = _get_weighted_score(content_tag_id) * count
            if content_tag_id not in self._content_tag_scores:
                self._content_tag_scores[content_tag_id] = score
            else:
                self._content_tag_scores[content_tag_id] += score

    def OnIndustryJobClient(self, status = None, *args, **kwargs):
        from industry.const import STATUS_INSTALLED
        if status == STATUS_INSTALLED:
            self.add_content_tag_scores([ContentTags.career_path_industrialist])

    def OnDungeonCompleted(self, dungeon_id):
        from evedungeons.client.util import GetDungeonContentTags
        self.add_content_tag_scores(GetDungeonContentTags(dungeon_id))


def _get_score_from_acp():

    def _acp_path_score(goal):
        if not goal:
            return 1
        return goal.progress / goal.definition.target_value * 25 or 1

    acp_goals_controller = get_career_goals_svc().get_goal_data_controller()
    explorer_goal = acp_goals_controller.get_career_path_goal(careerpathconst.career_path_explorer)
    enforcer_goal = acp_goals_controller.get_career_path_goal(careerpathconst.career_path_enforcer)
    industrialist_goal = acp_goals_controller.get_career_path_goal(careerpathconst.career_path_industrialist)
    soldier_goal = acp_goals_controller.get_career_path_goal(careerpathconst.career_path_soldier_of_fortune)
    return {ContentTags.career_path_explorer: _acp_path_score(explorer_goal),
     ContentTags.career_path_enforcer: _acp_path_score(enforcer_goal),
     ContentTags.career_path_industrialist: _acp_path_score(industrialist_goal),
     ContentTags.career_path_soldier_of_fortune: _acp_path_score(soldier_goal)}


def _get_weighted_score(content_tag_id, override_weights = None):
    if override_weights and content_tag_id in override_weights:
        weighted_score = override_weights[content_tag_id]
    else:
        weighted_score = content_tag_weights.get(content_tag_id, content_tag_type_weights.get(get_content_tag_type_id(content_tag_id), 0))
    return weighted_score


def _get_jump_score(from_solar_system_id, to_solar_system_id):
    if not from_solar_system_id or not to_solar_system_id:
        jumps = 0
    else:
        jumps = sm.GetService('clientPathfinderService').GetAutopilotJumpCount(from_solar_system_id, to_solar_system_id)
    if jumps == 0:
        return 15
    if jumps <= 2:
        return 10
    if jumps <= 5:
        return 5
    return 0


content_tag_type_weights = {ContentTagTypes.career_path: 10,
 ContentTagTypes.feature: 8,
 ContentTagTypes.activity: 5}
content_tag_weights = {ContentTags.activity_fleet: 10}
