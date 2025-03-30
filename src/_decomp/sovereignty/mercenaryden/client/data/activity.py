#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\data\activity.py
import uuid
from eveProto.generated.eve_public.localization.message_pb2 import Identifier as MessageID
from eveProto.generated.eve_public.sovereignty.mercenaryden.activity.api.requests_pb2 import GetAllResponse, GetForMercenaryDenResponse
from eveProto.generated.eve_public.sovereignty.mercenaryden.activity.activity_pb2 import Attributes
from eveProto.generated.eve_public.sovereignty.mercenaryden.activity.activitytemplate.activitytemplate_pb2 import Definition
from eveProto.generated.eve_public.sovereignty.mercenaryden.mercenaryden_pb2 import Identifier as MercDenID
from eveProto.generated.eve_public.sovereignty.mercenaryden.activity.activity_pb2 import Identifier as ActivityID
from eveProto.generated.eve_public.dungeon.dungeon_pb2 import Identifier as DungeonID
from eveProto.generated.eve_public.solarsystem.solarsystem_pb2 import Identifier as SolarSystemID
from google.protobuf.timestamp_pb2 import Timestamp

class MercenaryDenActivity(object):

    @property
    def id(self):
        return self._id

    @property
    def den_id(self):
        return self._den_id

    @property
    def template_name_id(self):
        return self._template_name_id

    @property
    def template_description_id(self):
        return self._template_description_id

    @property
    def dungeon_id(self):
        return self._dungeon_id

    @property
    def is_started(self):
        return self._started

    @property
    def expiry(self):
        return self._expiry

    @property
    def solar_system_id(self):
        return self._solar_system_id

    @property
    def development_impact(self):
        return self._development_impact

    @property
    def anarchy_impact(self):
        return self._anarchy_impact

    @property
    def infomorph_bonus(self):
        return self._infomorph_bonus

    def __init__(self, activity_id, den_id, name_id, description_id, dungeon_id, started, expiry, solar_system_id, development_impact, anarchy_impact, infomorph_bonus):
        self._id = activity_id
        self._den_id = den_id
        self._template_name_id = name_id
        self._template_description_id = description_id
        self._dungeon_id = dungeon_id
        self._started = started
        self._expiry = expiry
        self._solar_system_id = solar_system_id
        self._development_impact = development_impact
        self._anarchy_impact = anarchy_impact
        self._infomorph_bonus = infomorph_bonus

    def __eq__(self, o):
        if not isinstance(o, type(self)):
            return False
        return self._id == o.id and self._den_id == o.den_id and self._template_name_id == o.template_name_id and self._template_description_id == o.template_description_id and self._dungeon_id == o.dungeon_id and self._started == o.is_started and self._expiry == o.expiry and self._solar_system_id == o.solar_system_id and self._development_impact == o.development_impact and self._anarchy_impact == o.anarchy_impact and self._infomorph_bonus == o.infomorph_bonus

    def __ne__(self, o):
        return not self == o

    @classmethod
    def create_from_proto(self, activity_proto):
        activity_id = uuid.UUID(bytes=activity_proto.id.uuid)
        den_id = activity_proto.attributes.mercenary_den.sequential
        started = activity_proto.attributes.started
        expiry = activity_proto.attributes.expiry.ToDatetime()
        solar_system_id = activity_proto.attributes.solar_system.sequential
        name_id = activity_proto.attributes.activitytemplate.name.sequential
        description_id = activity_proto.attributes.activitytemplate.description.sequential
        dungeon_id = activity_proto.attributes.activitytemplate.dungeon.sequential
        development_impact = activity_proto.attributes.activitytemplate.development_impact
        anarchy_impact = activity_proto.attributes.activitytemplate.anarchy_impact
        infomorph_bonus = activity_proto.attributes.activitytemplate.infomorph_bonus
        return MercenaryDenActivity(activity_id, den_id, name_id, description_id, dungeon_id, started, expiry, solar_system_id, development_impact, anarchy_impact, infomorph_bonus)

    @classmethod
    def create_from_id_and_attributes_proto(self, id, attributes_proto):
        activity_id = id
        den_id = attributes_proto.mercenary_den.sequential
        started = attributes_proto.started
        expiry = attributes_proto.expiry.ToDatetime()
        solar_system_id = attributes_proto.solar_system.sequential
        name_id = attributes_proto.activitytemplate.name.sequential
        description_id = attributes_proto.activitytemplate.description.sequential
        dungeon_id = attributes_proto.activitytemplate.dungeon.sequential
        development_impact = attributes_proto.activitytemplate.development_impact
        anarchy_impact = attributes_proto.activitytemplate.anarchy_impact
        infomorph_bonus = attributes_proto.activitytemplate.infomorph_bonus
        return MercenaryDenActivity(activity_id, den_id, name_id, description_id, dungeon_id, started, expiry, solar_system_id, development_impact, anarchy_impact, infomorph_bonus)

    def get_all_response_activity_response_proto(self):
        expiry = Timestamp()
        expiry.FromDatetime(self.expiry)
        return GetAllResponse.Activity(id=ActivityID(uuid=self.id.bytes), attributes=Attributes(activitytemplate=Definition(name=MessageID(sequential=self.template_name_id), description=MessageID(sequential=self.template_description_id), dungeon=DungeonID(sequential=self.dungeon_id), development_impact=self.development_impact, anarchy_impact=self.anarchy_impact, infomorph_bonus=self.infomorph_bonus), mercenary_den=MercDenID(sequential=self.den_id), started=self.is_started, expiry=expiry, solar_system=SolarSystemID(sequential=self.solar_system_id)))

    def get_for_merc_den_activity_response_proto(self):
        expiry = Timestamp()
        expiry.FromDatetime(self.expiry)
        return GetForMercenaryDenResponse.Activity(id=ActivityID(uuid=self.id.bytes), attributes=Attributes(activitytemplate=Definition(name=MessageID(sequential=self.template_name_id), description=MessageID(sequential=self.template_description_id), dungeon=DungeonID(sequential=self.dungeon_id), development_impact=self.development_impact, anarchy_impact=self.anarchy_impact, infomorph_bonus=self.infomorph_bonus), mercenary_den=MercDenID(sequential=self.den_id), started=self.is_started, expiry=expiry, solar_system=SolarSystemID(sequential=self.solar_system_id)))
