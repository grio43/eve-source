#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\structures\fitting.py
from cosmetics.common.structures.const import StructurePaintSlot
from cosmetics.common.structures.fitting import StructurePaintwork
from eveProto.generated.eve_public.cosmetic.structure.paintwork.paintwork_pb2 import SlotConfiguration, Slot

def create_structure_paintwork_from_proto_slot_config(slot_config):
    paintwork = StructurePaintwork()
    if slot_config.primary.HasField('paint'):
        paintwork.set_slot(StructurePaintSlot.PRIMARY, slot_config.primary.paint)
    if slot_config.secondary.HasField('paint'):
        paintwork.set_slot(StructurePaintSlot.SECONDARY, slot_config.secondary.paint)
    if slot_config.detailing.HasField('paint'):
        paintwork.set_slot(StructurePaintSlot.DETAILING, slot_config.detailing.paint)
    return paintwork


def create_proto_slot_config_from_structure_paintwork(structure_paintwork):

    def _make_slot(slot_index):
        slot_value = structure_paintwork.get_slot(slot_index)
        if not slot_value:
            return Slot(empty=True)
        else:
            return Slot(paint=slot_value)

    slot_config = SlotConfiguration(primary=_make_slot(StructurePaintSlot.PRIMARY), secondary=_make_slot(StructurePaintSlot.SECONDARY), detailing=_make_slot(StructurePaintSlot.DETAILING))
    return slot_config
