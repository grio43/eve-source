#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterdata\npccharacter.py
from characterdata.npccharacters import get_npc_character

class NpcCharacter(object):

    def __init__(self, npc_character_id):
        self.npc_character_id = npc_character_id
        self.data = get_npc_character(npc_character_id)

    def get_id(self):
        return self.npc_character_id

    def get_name(self):
        return self.data.nameID

    def get_level(self):
        return self.data.agent.agentLevel

    def get_corporation_id(self):
        return self.data.corporationID

    def get_agent_type(self):
        return self.data.agent.agentType

    def get_division_id(self):
        return self.data.agent.agentDivisionID

    def get_station_id(self):
        return self.data.stationID

    def get_race_id(self):
        return self.data.raceID

    def get_bloodline_id(self):
        return self.data.bloodlineID

    def get_gender(self):
        if self.data.gender:
            return 'M'
        return 'F'
