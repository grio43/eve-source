#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agentinteraction\reward.py
import gametime
from characterdata.npccharacter import NpcCharacter
from eve.common.script.sys.idCheckers import IsCharacter
from eve.common.script.util.eveFormat import FmtISK
from eveexceptions.const import UE_TYPEIDANDQUANTITY
from inventorycommon.const import typeCredits, typeLoyaltyPoints, typeLoyaltyPointsHeraldry, typeResearch, typePyerite, type1MNCivilianAfterburnerBlueprint
from localization import GetByLabel
from localization.formatters import FormatGenericList

class RewardType:
    GRANTED = 'granted'
    NORMAL = 'normal'
    BONUS = 'bonus'
    COLLATERAL = 'collateral'


class Reward(object):

    def __init__(self, reward_type, type_id, quantity, extra = None, time_bonus_min = None, mission_accepted_time = None, alpha_quantity = None, omega_quantity = None):
        self.reward_type = reward_type
        self.type_id = type_id
        self.extra = extra or {}
        self.time_bonus_min = time_bonus_min
        self.mission_accepted_time = mission_accepted_time
        self.quantity = quantity
        self.alpha_quantity = alpha_quantity
        self.omega_quantity = omega_quantity

    def get_text(self, use_omega_quantity = False, use_short_version = True):
        if self._is_isk():
            return self._get_isk_text()
        if self._is_loyalty_points():
            return self._get_loyalty_points_text(use_omega_quantity, use_short_version)
        if self._is_research_points():
            return self._get_research_points_text()
        if self._is_mission_referral():
            npc_character = NpcCharacter(self.type_id)
            name = npc_character.get_name() if npc_character else ''
            return name
        return self._get_type_and_quantity_text()

    def get_hint(self, use_omega_quantity = False):
        return self.get_text_details(use_omega_quantity)

    def get_omega_vs_alpha_ratio(self):
        alpha_quantity = self.alpha_quantity or self.quantity
        omega_quantity = self.omega_quantity or self.quantity
        if not alpha_quantity or not omega_quantity or alpha_quantity == omega_quantity:
            return None
        return float(omega_quantity) / float(alpha_quantity)

    def get_text_details(self, use_omega_quantity = False):
        if self._is_mission_referral():
            return self._get_mission_referral_text()
        if self.extra is not None:
            if self._is_blueprint():
                return self._get_blueprint_text()
            if self._is_item():
                return self._get_item_text()
        return self.get_text(use_omega_quantity, use_short_version=False)

    def is_blueprint_copy(self):
        blueprint_info = self.get_blueprint_info()
        if not blueprint_info:
            return False
        is_copy = blueprint_info.get('copy', 0)
        return bool(is_copy)

    def get_color(self):
        if self.reward_type == RewardType.BONUS:
            return (0.6, 0.6, 0.6, 1.0)
        if self._is_isk():
            return (0.58, 0.42, 0.93, 1.0)
        if self._is_loyalty_points() or self._is_research_points():
            return (1.0, 0.72, 0.27, 1.0)
        return (0.6, 0.6, 0.6, 1.0)

    def is_normal_type(self):
        if self._is_isk() or self._is_research_points() or self._is_mission_referral():
            return False
        return True

    def _is_isk(self):
        return self.type_id == typeCredits

    def _is_loyalty_points(self):
        return self.type_id in [typeLoyaltyPoints, typeLoyaltyPointsHeraldry]

    def _is_research_points(self):
        return self.type_id == typeResearch

    def _is_mission_referral(self):
        return IsCharacter(self.type_id)

    def _is_blueprint(self):
        return bool(self.get_blueprint_info())

    def _is_item(self):
        return bool(self.extra.get('specificItemID', 0))

    def _get_isk_text(self):
        return FmtISK(self.quantity)

    def _get_loyalty_points_text(self, use_omega_quantity = False, use_short_version = False):
        quantity = self.omega_quantity if use_omega_quantity else self.quantity
        if use_short_version:
            if self.type_id == typeLoyaltyPointsHeraldry:
                return GetByLabel('UI/Common/NumEverMarksShort', quantity=quantity)
            return GetByLabel('UI/Agents/StandardMission/NumLoyaltyPointsShort', lpAmount=quantity)
        elif self.type_id == typeLoyaltyPointsHeraldry:
            return self._get_type_and_quantity_text()
        else:
            return GetByLabel('UI/Agents/StandardMission/NumLoyaltyPoints', lpAmount=quantity)

    def _get_research_points_text(self):
        return GetByLabel('UI/Agents/StandardMission/NumResearchPoints', rpAmount=self.quantity)

    def _get_mission_referral_text(self):
        return GetByLabel('UI/Agents/StandardMission/MissionReferral', agentID=self.type_id)

    def _get_type_and_quantity_text(self):
        return cfg.FormatConvert(UE_TYPEIDANDQUANTITY, self.type_id, self.quantity)

    def _get_item_text(self):
        properties = [GetByLabel('UI/Agents/Items/SpecificItems')]
        return GetByLabel('UI/Agents/Items/NumItemsAndProperties', itemAndQuantity=self._get_type_and_quantity_text(), propertyList=FormatGenericList(properties))

    def _get_blueprint_text(self):
        item_id = self.extra.get('specificItemID', 0)
        properties = []
        if item_id:
            properties.append(GetByLabel('UI/Agents/Items/SpecificItems'))
        runs_remaining = self.get_runs_remaining()
        if runs_remaining > 1:
            properties.append(GetByLabel('UI/Agents/Items/BlueprintInfoMultirun', runsRemaining=runs_remaining))
        elif runs_remaining == 1:
            properties.append(GetByLabel('UI/Agents/Items/BlueprintInfoSingleRun'))
        is_copy = self.is_blueprint_copy()
        if is_copy:
            properties.append(GetByLabel('UI/Agents/Items/BlueprintInfoCopy'))
        else:
            properties.append(GetByLabel('UI/Agents/Items/BlueprintInfoOriginal'))
        material_level = self.get_material_level()
        if material_level:
            properties.append(GetByLabel('UI/Agents/Items/BlueprintInfoMaterialLevel', materialLevel=material_level))
        productivity_level = self.get_productivity_level()
        if productivity_level:
            properties.append(GetByLabel('UI/Agents/Items/ProductivityLevel', productivityLevel=productivity_level))
        return GetByLabel('UI/Agents/Items/NumItemsAndProperties', itemAndQuantity=self._get_type_and_quantity_text(), propertyList=FormatGenericList(properties))

    def get_productivity_level(self):
        blueprint_info = self.get_blueprint_info()
        if not blueprint_info:
            return 0
        productivity_level = blueprint_info.get('productivityLevel', 0)
        return productivity_level

    def get_material_level(self):
        blueprint_info = self.get_blueprint_info()
        if not blueprint_info:
            return 0
        material_level = blueprint_info.get('materialLevel', 0)
        return material_level

    def get_runs_remaining(self):
        if not self.is_blueprint_copy():
            return 0
        blueprint_info = self.get_blueprint_info()
        runs_remaining = blueprint_info.get('licensedProductionRunsRemaining', 0)
        return runs_remaining

    def get_blueprint_info(self):
        blueprint_info = self.extra.get('blueprintInfo', None)
        return blueprint_info

    def get_bonus_expiry_time(self):
        if not self.mission_accepted_time:
            return None
        if not self.time_bonus_min:
            return None
        bonus_expiry_timestamp = self.mission_accepted_time + self.time_bonus_min * gametime.MIN
        return bonus_expiry_timestamp

    def get_time_bonus(self):
        if not self.time_bonus_min:
            return None
        return self.time_bonus_min * gametime.MIN

    def get_bonus_progress(self):
        if not self.mission_accepted_time:
            return None
        if not self.time_bonus_min:
            return None
        expiry_time = self.get_bonus_expiry_time()
        bonus_time_sec = self.time_bonus_min * 60
        sec_until_expiry = max(expiry_time - gametime.GetWallclockTime(), 0) / gametime.SEC
        progress = float(bonus_time_sec - sec_until_expiry) / bonus_time_sec
        return progress


def get_test_rewards():
    rewards = [Reward(RewardType.NORMAL, typeCredits, quantity=100000000),
     Reward(RewardType.NORMAL, typeLoyaltyPoints, quantity=100000000),
     Reward(RewardType.NORMAL, typeResearch, quantity=100000000),
     Reward(RewardType.NORMAL, typePyerite, quantity=2000),
     Reward(RewardType.NORMAL, type1MNCivilianAfterburnerBlueprint, quantity=1, extra={'blueprintInfo': {'copy': True,
                        'licensedProductionRunsRemaining': 1,
                        'materialLevel': 5,
                        'productivityLevel': 3.5}})]
    return rewards
