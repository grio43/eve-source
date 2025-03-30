#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\standings.py
from collections import defaultdict
import random
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.monitors.ballparks import MonitorProximitySensors
from behaviors.utility.ballparks import get_item_owner, get_ball_position
from behaviors.utility.blackboards import get_response_thresholds
from behaviors.utility.components import get_proximity_sensors_for_group_members
from behaviors.utility.standings import get_standings_between
from npcs.common.standings import classify_standings
from npcs.common.standings import STANDINGS_HOSTILE, STANDINGS_NEUTRAL, STANDINGS_FRIENDLY
import logging
logger = logging.getLogger(__name__)

class StandingsAddresses(object):

    def __init__(self, item_ids, flag, last_position):
        self.item_ids = item_ids
        self.flag = flag
        self.last_position = last_position


class MonitorProximitySensorForGroupStanding(MonitorProximitySensors, GroupTaskMixin):

    def __init__(self, attributes = None):
        super(MonitorProximitySensorForGroupStanding, self).__init__(attributes)
        self.address_by_class = {}
        self._map_address_to_class(STANDINGS_HOSTILE, 'itemIdsWithHostileStandingsAddress', 'flagHostileStandingsAddress', 'lastPositionForHostileStandingsAddress')
        self._map_address_to_class(STANDINGS_NEUTRAL, 'itemIdsWithNeutralStandingsAddress', 'flagNeutralStandingsAddress', 'lastPositionForNeutralStandingsAddress')
        self._map_address_to_class(STANDINGS_FRIENDLY, 'itemIdsWithFriendlyStandingsAddress', 'flagFriendlyStandingsAddress', 'lastPositionForFriendlyStandingsAddress')

    def GetBubbleIdSet(self):
        return self.GetMemberBubbleSet()

    def GetProximitySensors(self):
        return get_proximity_sensors_for_group_members(self)

    def ClassifyItems(self, item_ids):
        item_ids_by_standings = self._get_item_ids_by_standings_class(item_ids)
        self._update_blackboards(item_ids_by_standings)

    def _update_blackboards(self, item_ids_by_standings):
        for standings_class, item_ids in item_ids_by_standings.iteritems():
            standings_addresses = self.address_by_class[standings_class]
            self._update_blackboards_for_standing(item_ids, standings_addresses)

    def _get_item_ids_by_standings_class(self, item_ids):
        item_ids_by_standings = defaultdict(set)
        for item_id in item_ids:
            owner_id = get_item_owner(self, item_id)
            standings = get_standings_between(self, owner_id)
            standing_thresholds = get_response_thresholds(self)
            standings_class = classify_standings(standing_thresholds.hostile_response_threshold, standing_thresholds.friendly_response_threshold, standings)
            if standings_class in self.address_by_class:
                item_ids_by_standings[standings_class].add(item_id)

        return item_ids_by_standings

    def _map_address_to_class(self, standings_class, item_ids_address_name, flag_address_name, last_position_name):
        item_ids_address = getattr(self.attributes, item_ids_address_name, None)
        flag_address = getattr(self.attributes, flag_address_name, None)
        last_position_address = getattr(self.attributes, last_position_name, None)
        if item_ids_address:
            self.address_by_class[standings_class] = StandingsAddresses(item_ids_address, flag_address, last_position_address)

    def _update_blackboards_for_standing(self, detected_item_ids, standings_addresses):
        stored_item_ids = self.GetLastBlackboardValue(standings_addresses.item_ids) or set()
        new_item_ids = detected_item_ids.difference(stored_item_ids)
        if new_item_ids:
            self.SendBlackboardValue(standings_addresses.item_ids, stored_item_ids.union(new_item_ids))
            if standings_addresses.flag:
                self.SendBlackboardValue(standings_addresses.flag, True)
            if standings_addresses.last_position:
                item_id = random.choice(list(new_item_ids))
                last_position = get_ball_position(self, item_id)
                self.SendBlackboardValue(standings_addresses.last_position, last_position)
