#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\live_data\ship_skin_state.py
from cosmetics.client.ships.skins.live_data.slot_layout import SlotLayout
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from eveProto.generated.eve_public.cosmetic.ship.ship_pb2 import State
from eveProto.generated.eve_public.character.character_pb2 import Identifier as CharacterIdentifier
from eveProto.generated.eve_public.ship.ship_pb2 import Identifier as ShipIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.firstparty.firstparty_pb2 import Identifier as FirstPartyIdentifier

class ShipSkinState(object):

    def __init__(self, ship_instance_id, character_id):
        self._ship_instance_id = ship_instance_id
        self._character_id = character_id
        self._skin_data = None

    @property
    def skin_type(self):
        if self._skin_data is not None:
            return self._skin_data.get_type()
        return ShipSkinType.NO_SKIN

    @property
    def ship_instance_id(self):
        return self._ship_instance_id

    @property
    def character_id(self):
        return self._character_id

    @property
    def skin_data(self):
        return self._skin_data

    @skin_data.setter
    def skin_data(self, value):
        self._skin_data = value

    def __eq__(self, other):
        if other is None:
            return False
        if self.skin_type != other.skin_type:
            return False
        return self.ship_instance_id == other.ship_instance_id and self.character_id == other.character_id and self.skin_data == other.skin_data

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return 'char_id %s, ship_id %s, skin_type %s, skin_data %s' % (self.character_id,
         self.ship_instance_id,
         self.skin_type,
         self.skin_data)

    @staticmethod
    def build_from_proto(payload):
        skin_state = ShipSkinState(payload.ship.sequential, payload.character.sequential)
        skin_state.skin_data = build_skin_data_from_proto(payload.skin)
        return skin_state


class ShipSkinData(object):

    def __init__(self):
        pass

    def get_data(self):
        raise NotImplementedError

    def set_data(self, value):
        raise NotImplementedError

    def get_type(self):
        raise NotImplementedError

    def build_data_from_proto(self, payload):
        raise NotImplementedError

    def __eq__(self, other):
        if other is None:
            return False
        return self.get_data() == other.get_data()

    def __ne__(self, other):
        return not self.__eq__(other)


class FirstPartySkinData(ShipSkinData):

    def __init__(self):
        self._skin_id = None

    @property
    def skin_id(self):
        return self._skin_id

    def get_data(self):
        return self._skin_id

    def set_data(self, value):
        self._skin_id = value

    def get_type(self):
        return ShipSkinType.FIRST_PARTY_SKIN

    def build_data_from_proto(self, payload):
        self._skin_id = payload.identifier.sequential

    def __str__(self):
        return '%s' % self._skin_id


class ThirdPartySkinData(ShipSkinData):

    def __init__(self):
        self._slot_layout = None
        self._skin_id = None

    @property
    def slot_layout(self):
        return self._slot_layout

    @property
    def skin_id(self):
        return self._skin_id

    def get_data(self):
        return self._slot_layout

    def set_data(self, value):
        self._slot_layout = value

    def get_type(self):
        return ShipSkinType.THIRD_PARTY_SKIN

    def build_data_from_proto(self, payload):
        self._skin_id = payload.identifier.hex if payload.identifier.hex else None
        self._slot_layout = SlotLayout.build_from_proto(payload.layout)

    def __eq__(self, other):
        if other is None:
            return False
        return self.skin_id == other.skin_id and self.get_data() == other.get_data()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return 'skin_id %s, slot layout %s' % (self._skin_id, self._slot_layout)


def build_skin_data_from_proto(payload):
    skin_data = None
    if payload.HasField('firstparty'):
        skin_data = FirstPartySkinData()
        skin_data.build_data_from_proto(payload.firstparty)
    elif payload.HasField('thirdparty'):
        skin_data = ThirdPartySkinData()
        skin_data.build_data_from_proto(payload.thirdparty)
    return skin_data


def build_proto_from_skin_state(ship_type_id, skin_state):
    state = State()
    state.character.CopyFrom(CharacterIdentifier(sequential=skin_state.character_id))
    state.ship.CopyFrom(ShipIdentifier(sequential=skin_state.ship_instance_id))
    if skin_state.skin_type == ShipSkinType.FIRST_PARTY_SKIN:
        state.skin.firstparty.identifier.CopyFrom(FirstPartyIdentifier(sequential=skin_state.skin_data.get_data()))
    elif skin_state.skin_type == ShipSkinType.THIRD_PARTY_SKIN:
        skin_data = skin_state.skin_data.get_data()
        state.skin.thirdparty.layout.CopyFrom(SlotLayout.build_proto_from_layout(ship_type_id, skin_data))
    else:
        state.skin.no_skin = True
    return state
