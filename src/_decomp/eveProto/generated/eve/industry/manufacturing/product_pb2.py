#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\industry\manufacturing\product_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.inventory import generic_item_pb2 as eve_dot_inventory_dot_generic__item__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/industry/manufacturing/product.proto', package='eve.industry.manufacturing', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve/industry/manufacturing', create_key=_descriptor._internal_create_key, serialized_pb='\n(eve/industry/manufacturing/product.proto\x12\x1aeve.industry.manufacturing\x1a\x1deve/character/character.proto\x1a eve/inventory/generic_item.proto"\x89\x01\n\x0cJobCompleted\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x125\n\x06output\x18\x02 \x01(\x0b2%.eve.inventory.genericitem.Attributes\x12\x10\n\x08job_runs\x18\x03 \x01(\r:\x02\x18\x01BGZEgithub.com/ccpgames/eve-proto-go/generated/eve/industry/manufacturingb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_inventory_dot_generic__item__pb2.DESCRIPTOR])
_JOBCOMPLETED = _descriptor.Descriptor(name='JobCompleted', full_name='eve.industry.manufacturing.JobCompleted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.industry.manufacturing.JobCompleted.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='output', full_name='eve.industry.manufacturing.JobCompleted.output', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='job_runs', full_name='eve.industry.manufacturing.JobCompleted.job_runs', index=2, number=3, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=138, serialized_end=275)
_JOBCOMPLETED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_JOBCOMPLETED.fields_by_name['output'].message_type = eve_dot_inventory_dot_generic__item__pb2._ATTRIBUTES
DESCRIPTOR.message_types_by_name['JobCompleted'] = _JOBCOMPLETED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
JobCompleted = _reflection.GeneratedProtocolMessageType('JobCompleted', (_message.Message,), {'DESCRIPTOR': _JOBCOMPLETED,
 '__module__': 'eve.industry.manufacturing.product_pb2'})
_sym_db.RegisterMessage(JobCompleted)
DESCRIPTOR._options = None
_JOBCOMPLETED._options = None
