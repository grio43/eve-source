#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\structures.py
from behaviors.utility.standings import classify_standings_between
from behaviors.utility.structure import is_structure, can_dock_at_structure
from ccpProfile import TimedFunction
from eve.common.script.sys.idCheckers import IsNPCCorporation
from npcs.common.standings import STANDINGS_NEUTRAL
import random
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import Task
from inventorycommon.const import categoryStructure, categoryStation
import logging
from npcs.npccorporations import get_corporation_faction_id
logger = logging.getLogger(__name__)

class SelectDockableStructure(Task, GroupTaskMixin):

    @TimedFunction('behaviors::actions::structures::SelectDockableStructure::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        slim_items = self.get_valid_structure_slim_items()
        if not slim_items:
            logger.debug('no valid structures found in system')
            return
        selected_structure_id = self.select_dockable_structure_id(slim_items)
        if not selected_structure_id:
            logger.debug('no structure found to dock at')
            return
        self.SendBlackboardValue(self.attributes.selectedStructureIdAddress, selected_structure_id)
        self.SetStatusToSuccess()

    @TimedFunction('behaviors::actions::structures::SelectDockableStructure::get_valid_structure_slim_items')
    def get_valid_structure_slim_items(self):
        valid_structure_slim_items = []
        for slim_item in self.context.ballpark.slims.itervalues():
            if slim_item.categoryID not in (categoryStructure, categoryStation):
                continue
            valid_structure_slim_items.append(slim_item)

        return valid_structure_slim_items

    @TimedFunction('behaviors::actions::structures::SelectDockableStructure::select_dockable_structure_id')
    def select_dockable_structure_id(self, slim_items):
        selected_structure_id = None
        owner_id = self.GetGroupOwnerId()
        faction_id = self.GetGroupFactionId()
        for filter_policy in self.get_prioritized_filter_policies():
            valid_structure_ids = filter_policy(slim_items, owner_id, faction_id)
            if not valid_structure_ids:
                continue
            selected_structure_id = random.choice(valid_structure_ids)
            break

        return selected_structure_id

    def get_prioritized_filter_policies(self):
        return [self.filter_policy_my_corp_preferred_structure,
         self.filter_policy_my_corp_structures,
         self.filter_policy_my_faction_preferred_structure,
         self.filter_policy_my_faction_structures,
         self.filter_policy_npc_structures_with_positive_standings,
         self.filter_policy_player_structures_with_positive_standings]

    def has_structure_preference(self):
        return hasattr(self.attributes, 'preferredStructureGroupId') and self.attributes.preferredStructureGroupId is not None

    def is_preferred_structure(self, item):
        return item.groupID == self.attributes.preferredStructureGroupId

    def filter_policy_my_corp_preferred_structure(self, slim_items, owner_id, faction_id):
        if not self.has_structure_preference():
            return []
        return [ item.itemID for item in slim_items if item.ownerID == owner_id and self.is_preferred_structure(item) ]

    def filter_policy_my_faction_preferred_structure(self, slim_items, owner_id, faction_id):
        if not self.has_structure_preference():
            return []
        return [ item.itemID for item in slim_items if get_corporation_faction_id(item.ownerID) == faction_id and self.is_preferred_structure(item) ]

    def filter_policy_my_corp_structures(self, slim_items, owner_id, faction_id):
        return [ item.itemID for item in slim_items if item.ownerID == owner_id ]

    def filter_policy_my_faction_structures(self, slim_items, owner_id, faction_id):
        return [ item.itemID for item in slim_items if get_corporation_faction_id(item.ownerID) == faction_id ]

    def filter_policy_npc_structures_with_positive_standings(self, slim_items, owner_id, faction_id):
        return [ item.itemID for item in slim_items if IsNPCCorporation(item.ownerID) and classify_standings_between(self, item.ownerID) > STANDINGS_NEUTRAL ]

    def filter_policy_player_structures_with_positive_standings(self, slim_items, owner_id, faction_id):
        return [ item.itemID for item in slim_items if not IsNPCCorporation(item.ownerID) and classify_standings_between(self, item.ownerID) > STANDINGS_NEUTRAL and (not is_structure(item) or can_dock_at_structure(self, item.itemID)) ]
