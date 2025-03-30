#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evemissions\client\objectives.py
import eveicon

class ObjectivesType(object):
    TALK_TO_AGENT = 'agent'
    TRANSPORT = 'transport'
    FETCH = 'fetch'
    DUNGEON = 'dungeon'


class ObjectiveState(object):
    FAILED = 0
    COMPLETED = 1
    IN_PROGRESS = 2


class ShipRestrictions(object):
    NORMAL = 0
    SPECIAL = 1
    NONE = 2


class Objective(object):
    name = 'Objective'

    def __init__(self, state):
        self.state = state

    def get_icon(self):
        return eveicon.window_header_closed


class CargoObjective(Objective):
    name = 'Cargo'

    def __init__(self, type_id, quantity, volume, state):
        self.type_id = type_id
        self.quantity = quantity
        self.volume = volume
        super(CargoObjective, self).__init__(state)

    def get_icon(self):
        return eveicon.inventory


class LocationObjective(Objective):
    name = 'Location'

    def __init__(self, location, state):
        self.location = location
        super(LocationObjective, self).__init__(state)

    def get_icon(self):
        return eveicon.location


class TalkToAgentObjective(LocationObjective):
    name = 'TalkToAgent'

    def __init__(self, agent_id, location, state):
        self.agent_id = agent_id
        super(TalkToAgentObjective, self).__init__(location, state)

    def get_icon(self):
        return eveicon.chat_bubble


class PickUpObjective(LocationObjective):
    name = 'PickUp'

    def get_icon(self):
        return eveicon.inventory


class DropOffObjective(LocationObjective):
    name = 'DropOff'

    def get_icon(self):
        return eveicon.location


class DungeonObjective(LocationObjective):
    name = 'Dungeon'

    def __init__(self, dungeon_id, ship_restrictions, is_killing_optional, briefing, location, state):
        self.dungeon_id = dungeon_id
        self.ship_restrictions = ship_restrictions
        self.is_killing_optional = is_killing_optional
        self.briefing = briefing
        super(DungeonObjective, self).__init__(location, state)

    def get_icon(self):
        return eveicon.warp_to.resolve(16)
