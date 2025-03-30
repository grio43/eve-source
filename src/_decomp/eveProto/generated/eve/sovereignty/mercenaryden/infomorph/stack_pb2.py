#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\sovereignty\mercenaryden\infomorph\stack_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.sovereignty.mercenaryden.infomorph.itemtype import identifier_pb2 as eve_dot_sovereignty_dot_mercenaryden_dot_infomorph_dot_itemtype_dot_identifier__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/sovereignty/mercenaryden/infomorph/stack.proto', package='eve.sovereignty.mercenaryden.infomorph', syntax='proto3', serialized_options='ZQgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/mercenaryden/infomorph', create_key=_descriptor._internal_create_key, serialized_pb='\n2eve/sovereignty/mercenaryden/infomorph/stack.proto\x12&eve.sovereignty.mercenaryden.infomorph\x1a@eve/sovereignty/mercenaryden/infomorph/itemtype/identifier.proto"i\n\x05Stack\x12N\n\titem_type\x18\x01 \x01(\x0b2;.eve.sovereignty.mercenaryden.infomorph.itemtype.Identifier\x12\x10\n\x08quantity\x18\x02 \x01(\rBSZQgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/mercenaryden/infomorphb\x06proto3', dependencies=[eve_dot_sovereignty_dot_mercenaryden_dot_infomorph_dot_itemtype_dot_identifier__pb2.DESCRIPTOR])
_STACK = _descriptor.Descriptor(name='Stack', full_name='eve.sovereignty.mercenaryden.infomorph.Stack', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='item_type', full_name='eve.sovereignty.mercenaryden.infomorph.Stack.item_type', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='quantity', full_name='eve.sovereignty.mercenaryden.infomorph.Stack.quantity', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=160, serialized_end=265)
_STACK.fields_by_name['item_type'].message_type = eve_dot_sovereignty_dot_mercenaryden_dot_infomorph_dot_itemtype_dot_identifier__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Stack'] = _STACK
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Stack = _reflection.GeneratedProtocolMessageType('Stack', (_message.Message,), {'DESCRIPTOR': _STACK,
 '__module__': 'eve.sovereignty.mercenaryden.infomorph.stack_pb2'})
_sym_db.RegisterMessage(Stack)
DESCRIPTOR._options = None
