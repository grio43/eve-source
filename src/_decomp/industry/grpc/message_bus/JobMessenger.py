#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\industry\grpc\message_bus\JobMessenger.py
from eveProto.generated.eve.industry.job.api.events_pb2 import Completed as CompletedProto, Installed as InstalledProto
from eveProto.generated.eve.industry.job.blueprint_copy_pb2 import Completed as BlueprintCopiedProto
from eveProto.generated.eve.industry.job.manufacturing_pb2 import Completed as DeprecatedCompletedProto
from eveProto.generated.eve.industry.job.research_duration_pb2 import Completed as ResearchDurationCompletedProto
from eveProto.generated.eve.industry.job.research_materials_pb2 import Completed as ResearchMaterialCompletedProto
from eveProto.generated.eve.industry.blueprint.type_pb2 import Identifier as BlueprintIdentifier
from externalQueue.events.protobuf.industry.job.job import parse_from_job_data, parse_manufacture_job_attributes
from eveexceptions import EatsExceptions
from eveprefs import prefs
from evetypes import GetCategoryID, GetGroupID
from eve.common.script.sys.idCheckers import IsCharacter, IsCorporation, IsStation
import logging

class JobMessenger(object):
    external_queue_manager = None

    def __init__(self, external_queue_manager):
        self.external_queue_manager = external_queue_manager
        self.logger = logging.getLogger('IndustryJobMessenger')

    @EatsExceptions('IndustryJobMessenger::installed')
    def installed(self, job, output, input_materials):
        for type_id, quantity in output:
            event = InstalledProto()
            pb_attrs = event.job
            parse_manufacture_job_attributes(job, pb_attrs)
            event.expected_output.item_type.sequential = type_id
            event.expected_output.quantity = quantity
            event.expected_output.item_type.group.sequential = GetGroupID(type_id)
            event.expected_output.item_type.group.category.sequential = GetCategoryID(type_id)
            for input_item, input_quantity in input_materials:
                input_material = event.InputMaterial()
                input_material.id.sequential = input_item.itemID
                input_material.attributes.item_type.sequential = input_item.typeID
                input_material.attributes.quantity = input_quantity
                event.input_materials.append(input_material)

            self.external_queue_manager.PublishEventPayload(event)
            self._log_event(type_id, quantity, job, event, event_name='installed')

    @EatsExceptions('IndustryJobMessenger::manufacturing_completed')
    def manufacturing_completed(self, quantity, job):
        type_id = job.productTypeID
        group_id = GetGroupID(type_id)
        category_id = GetCategoryID(type_id)
        event = CompletedProto()
        pb_attrs = event.job
        parse_manufacture_job_attributes(job, pb_attrs)
        event.output.item_type.sequential = type_id
        event.output.quantity = quantity
        event.output.item_type.group.sequential = group_id
        event.output.item_type.group.category.sequential = category_id
        self.external_queue_manager.PublishEventPayload(event)
        self._log_event(type_id, quantity, job, event, event_name='completed')
        deprecated_event = DeprecatedCompletedProto()
        pb_attrs = deprecated_event.job
        parse_manufacture_job_attributes(job, pb_attrs)
        deprecated_event.output.item_type.sequential = type_id
        deprecated_event.output.quantity = quantity
        deprecated_event.output.item_type.group.sequential = group_id
        deprecated_event.output.item_type.group.category.sequential = category_id
        self.external_queue_manager.PublishEventPayload(deprecated_event)
        self._log_event(type_id, quantity, job, deprecated_event, event_name='completed (deprecated)')

    def blueprint_copied(self, character_id, source_blueprint, copy, job):
        event = BlueprintCopiedProto()
        pb_job = event.job
        parse_from_job_data(job, pb_job)
        pb_job.character.sequential = character_id
        event.source.type.sequential = source_blueprint.blueprintTypeID
        event.source.material_efficiency = source_blueprint.materialEfficiency
        event.source.time_efficiency = source_blueprint.timeEfficiency
        for x in range(pb_job.runs):
            event.blueprint_copies.add(type=BlueprintIdentifier(sequential=copy.blueprintTypeID), material_efficiency=copy.materialEfficiency, time_efficiency=copy.timeEfficiency, runs_remaining=copy.runsRemaining)

        self.external_queue_manager.PublishEventPayload(event)

    def research_duration_completed(self, character_id, researched_blueprint, new_time_level, job):
        event = ResearchDurationCompletedProto()
        pb_job = event.job
        parse_from_job_data(job, pb_job)
        pb_job.character.sequential = character_id
        event.researced_blueprint.type.sequential = researched_blueprint.typeID
        event.researced_blueprint.material_efficiency = researched_blueprint.materialEfficiency
        event.researced_blueprint.time_efficiency = new_time_level
        self.external_queue_manager.PublishEventPayload(event)

    def research_material_completed(self, character_id, researched_blueprint, new_material_level, job):
        event = ResearchMaterialCompletedProto()
        pb_job = event.job
        parse_from_job_data(job, pb_job)
        pb_job.character.sequential = character_id
        event.researced_blueprint.type.sequential = researched_blueprint.typeID
        event.researced_blueprint.time_efficiency = researched_blueprint.timeEfficiency
        event.researced_blueprint.material_efficiency = new_material_level
        self.external_queue_manager.PublishEventPayload(event)

    def _should_log(self):
        return prefs.clusterMode != 'LIVE'

    def _log_event(self, type_id, quantity, job, event, event_name):
        if not self._should_log():
            return
        from evetypes import GetName
        owner_id = job.ownerID
        if IsCharacter(owner_id):
            owner_name = 'character {name} ({owner_id})'.format(name=cfg.eveowners.Get(owner_id).ownerName, owner_id=owner_id)
        elif IsCorporation(owner_id):
            owner_name = 'corporation {name} ({owner_id})'.format(name=cfg.eveowners.Get(owner_id).ownerName, owner_id=owner_id)
        else:
            owner_name = '- ({owner_id})'.format(owner_id=owner_id)
        location_id = None
        if getattr(job, 'stationID', None):
            location_id = job.stationID
        elif getattr(job, 'facilityID', None):
            location_id = job.facilityID
        location_name = '-'
        if location_id:
            location_name = '{dockable_type} {dockable_name}'.format(dockable_type='station' if IsStation(location_id) else 'structure', dockable_name=cfg.evelocations.Get(location_id).name)
        type_name = 'type {name} ({type_id}) quantity {quantity}'.format(name=GetName(type_id), type_id=type_id, quantity=quantity)
        info_text = 'Industry Event: {event_name} - {owner_name} in {location_name} installed {type_name}. Proto: {proto}'.format(owner_name=owner_name, location_name=location_name, type_name=type_name, proto=event, event_name=event_name)
        self.logger.info(info_text)
