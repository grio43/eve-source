#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\live_data\skin_license.py
import datetime
from cosmetics.client.shipSkinDataSvc import get_ship_skin_data_svc
from cosmetics.client.ships.skins.live_data.skin_design import SkinDesign
from eve.client.script.ui.control.message import ShowQuickMessage
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.license.license_pb2 import Attributes as LicenseAttributes
from google.protobuf.timestamp_pb2 import Timestamp
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException

class SkinLicense(object):

    def __init__(self, owner_character_id, skin_hex, activated, nb_unactivated, nb_escrowed, acquired_time):
        self._owner_character_id = owner_character_id
        self._skin_hex = skin_hex
        self._activated = activated
        self._nb_unactivated = nb_unactivated
        self._nb_escrowed = nb_escrowed
        self._acquired_time = acquired_time
        self._skin_design = None

    @property
    def owner_character_id(self):
        return self._owner_character_id

    @property
    def skin_hex(self):
        return self._skin_hex

    @property
    def skin_design(self):
        return self._skin_design

    @property
    def activated(self):
        return self._activated

    @activated.setter
    def activated(self, value):
        self._activated = value

    @property
    def nb_unactivated(self):
        return self._nb_unactivated

    @property
    def nb_escrowed(self):
        return self._nb_escrowed

    @property
    def acquired_time(self):
        return self._acquired_time

    @property
    def name(self):
        return self.skin_design.name

    @property
    def tier_level(self):
        return self.skin_design.tier_level

    def load_skin_design(self):
        if self._skin_design is None:
            try:
                self._skin_design = get_ship_skin_data_svc().get_skin_data(self._skin_hex)
            except (GenericException, TimeoutException):
                ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
                self._skin_design = None

    def __eq__(self, other):
        if other is None:
            return False
        return self.owner_character_id == other.owner_character_id and self.skin_design == other.skin_design and self.activated == other.activated and self.nb_unactivated == other.nb_unactivated and self.nb_escrowed == other.nb_escrowed and self.acquired_time == other.acquired_time

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        result = 'SKIN License from skin design %s\n' % self.skin_hex
        result += 'activated: %s\n' % self.activated
        result += 'nb_unactivated: %s\n' % self.nb_unactivated
        result += 'nb_escrowed: %s\n' % self.nb_escrowed
        result += 'acquired_time: %s\n' % self.acquired_time
        return result

    def copy_from_other(self, other):
        self._owner_character_id = other.owner_character_id
        self._skin_design = SkinDesign.copy_from_other(other.skin_design)
        self._activated = other.activated
        self._nb_unactivated = other.nb_unactivated
        self._nb_escrowed = other.nb_escrowed
        self._acquired_time = other.acquired_time

    @staticmethod
    def build_from_proto(payload, skin_hex, owner_character_id):
        license = SkinLicense(owner_character_id=owner_character_id, skin_hex=skin_hex, activated=payload.activated, nb_unactivated=payload.unactivated, nb_escrowed=payload.escrowed, acquired_time=datetime.datetime.fromtimestamp(payload.first_acquired.seconds))
        return license

    @staticmethod
    def build_proto_from_license(license):
        first_acquired = Timestamp()
        first_acquired.FromDatetime(license.acquired_time)
        payload = LicenseAttributes(activated=license.activated, unactivated=license.nb_unactivated, escrowed=license.nb_escrowed, first_acquired=first_acquired)
        return payload
