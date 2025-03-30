#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\careergoals\client\goal_definition.py
import uuid
from carbon.common.script.util.format import FmtDate
import careergoals.client.const as careerGoalsConst
from careergoals.client.const import RewardLabel
from careergoals.client.reward_definition import RewardDefinitionTypeID
from eve.common.lib.appConst import MIN
from localization import GetByMessageID, GetByLabel

class GoalDefinition(object):

    def __init__(self, legacy_rewards, goal_data):
        self._goal_id = uuid.UUID(bytes=goal_data.goal.uuid)
        goal_attributes = goal_data.attributes
        ui_annotations = goal_attributes.ui_annotations
        self._sanitize_annotations(ui_annotations)
        self._sub_type = self._find_annotation(ui_annotations, careerGoalsConst.GOAL_ANNOTATION_GOAL_SUBTYPE)
        self._name_msg_id = goal_attributes.name.sequential
        self._desc_msg_id = goal_attributes.description.sequential
        self._target_value = goal_attributes.target
        self._rewards = RewardDefinitionTypeID.build_from_legacy_reward(legacy_rewards, goal_attributes.reward.store_offer)
        self._career = careerGoalsConst.get_career_path_id_from_proto_id(goal_attributes.career)
        self._career_points = goal_attributes.career_points
        self._group_id = careerGoalsConst.get_career_path_group_id(self.career, self._find_annotation(ui_annotations, careerGoalsConst.GOAL_ANNOTATION_ACTIVITY_GROUP))
        self._threat = goal_attributes.threat
        self._duration = self._find_annotation(ui_annotations, careerGoalsConst.GOAL_ANNOTATION_DURATION)
        self._aura_text_id = self._find_annotation(ui_annotations, careerGoalsConst.GOAL_ANNOTATION_AURA_TEXT_ID)
        self._agency_link_text_id = self._find_annotation(ui_annotations, careerGoalsConst.GOAL_ANNOTATION_AGENCY_LINK_TEXT_ID)
        self._agency_screen_id = self._find_annotation(ui_annotations, careerGoalsConst.GOAL_ANNOTATION_AGENCY_SCREEN_ID)
        self._video_id = self._find_annotation(ui_annotations, careerGoalsConst.GOAL_ANNOTATION_VIDEO)
        try:
            self._order = int(self._find_annotation(ui_annotations, careerGoalsConst.GOAL_ANNOTATION_ORDER))
        except (TypeError, ValueError):
            self._order = None

        self._name = None
        self._description = None

    @property
    def goal_id(self):
        return self._goal_id

    @property
    def sub_type(self):
        return self._sub_type

    @property
    def name(self):
        if not self._name:
            self._name = GetByMessageID(self._name_msg_id)
        return self._name

    @property
    def description(self):
        if not self._description:
            self._description = GetByMessageID(self._desc_msg_id)
        return self._description

    @property
    def target_value(self):
        return self._target_value

    @property
    def rewards(self):
        return self._rewards

    @property
    def omega_rewards(self):
        return [ r for r in self._rewards if r.reward_label == RewardLabel.OMEGA ]

    @property
    def alpha_rewards(self):
        return [ r for r in self._rewards if r.reward_label == RewardLabel.ALPHA ]

    @property
    def career(self):
        return self._career

    @property
    def career_points(self):
        return self._career_points

    @property
    def career_points_text(self):
        return GetByLabel('UI/CareerPortal/NumCareerPoints', numPoints=self.career_points)

    @property
    def group_id(self):
        return self._group_id

    @property
    def threat(self):
        return self._threat

    @property
    def duration(self):
        return self._duration

    @property
    def duration_text(self):
        try:
            value = int(self.duration)
            return FmtDate(value * MIN, 'ss')
        except ValueError:
            return ''

    @property
    def aura_text_id(self):
        return self._aura_text_id

    @property
    def agency_link_text_id(self):
        return self._agency_link_text_id

    @property
    def agency_screen_id(self):
        return self._agency_screen_id

    @property
    def video_id(self):
        return self._video_id

    @property
    def order(self):
        return self._order

    def has_video_id(self):
        return self.video_id is not None and self.video_id != u'null'

    def __eq__(self, other):
        return isinstance(other, self.__class__) and getattr(other, 'goalID', None) == self._goal_id

    def __hash__(self):
        return hash(str(self._goal_id))

    def __cmp__(self, other):
        if self.order is None or other.order is None:
            return 0
        return cmp(self.order, other.order)

    @staticmethod
    def _sanitize_annotations(ui_annotations):
        for annotation in ui_annotations:
            annotation.value = ''.join(annotation.value.split())

        return ui_annotations

    @staticmethod
    def _find_annotation(annotations, key):
        for each in annotations:
            if each.key == key:
                return each.value
