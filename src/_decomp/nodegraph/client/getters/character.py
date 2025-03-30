#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\character.py
from .base import GetterAtom

class GetSelf(GetterAtom):
    atom_id = 311

    def get_values(self, **kwargs):
        return {'character_id': session.charid,
         'item_id': session.shipid,
         'solar_system_id': session.solarsystemid2,
         'location_id': session.locationid,
         'race_id': session.raceID}


class GetRace(GetterAtom):
    atom_id = 382

    def get_values(self, **kwargs):
        from characterdata.races import get_race_name
        from eve.common.lib.appConst import factionByRace
        race_id = session.raceID
        race_name = get_race_name(race_id, language_id='en')
        faction_id = factionByRace.get(race_id, None)
        return {'race_id': race_id,
         'race_name': race_name,
         'faction_id': faction_id}
