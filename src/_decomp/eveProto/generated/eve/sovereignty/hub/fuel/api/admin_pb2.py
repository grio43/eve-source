#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\sovereignty\hub\fuel\api\admin_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.inventory import generic_item_type_pb2 as eve_dot_inventory_dot_generic__item__type__pb2
from eveProto.generated.eve.quasar.admin import admin_pb2 as eve_dot_quasar_dot_admin_dot_admin__pb2
from eveProto.generated.eve.sovereignty.hub import hub_pb2 as eve_dot_sovereignty_dot_hub_dot_hub__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/sovereignty/hub/fuel/api/admin.proto', package='eve.sovereignty.hub.fuel.api.admin', syntax='proto3', serialized_options='ZMgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/hub/fuel/api/admin', create_key=_descriptor._internal_create_key, serialized_pb='\n(eve/sovereignty/hub/fuel/api/admin.proto\x12"eve.sovereignty.hub.fuel.api.admin\x1a%eve/inventory/generic_item_type.proto\x1a\x1ceve/quasar/admin/admin.proto\x1a\x1deve/sovereignty/hub/hub.proto"\xb4\x01\n\nSetRequest\x12,\n\x03hub\x18\x01 \x01(\x0b2\x1f.eve.sovereignty.hub.Identifier\x12\x0e\n\x06amount\x18\x02 \x01(\r\x12<\n\tfuel_type\x18\x03 \x01(\x0b2).eve.inventory.genericitemtype.Identifier\x12*\n\x07context\x18\x04 \x01(\x0b2\x19.eve.quasar.admin.Context"\r\n\x0bSetResponseBOZMgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/hub/fuel/api/adminb\x06proto3', dependencies=[eve_dot_inventory_dot_generic__item__type__pb2.DESCRIPTOR, eve_dot_quasar_dot_admin_dot_admin__pb2.DESCRIPTOR, eve_dot_sovereignty_dot_hub_dot_hub__pb2.DESCRIPTOR])
_SETREQUEST = _descriptor.Descriptor(name='SetRequest', full_name='eve.sovereignty.hub.fuel.api.admin.SetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='hub', full_name='eve.sovereignty.hub.fuel.api.admin.SetRequest.hub', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='amount', full_name='eve.sovereignty.hub.fuel.api.admin.SetRequest.amount', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='fuel_type', full_name='eve.sovereignty.hub.fuel.api.admin.SetRequest.fuel_type', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='context', full_name='eve.sovereignty.hub.fuel.api.admin.SetRequest.context', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=181, serialized_end=361)
_SETRESPONSE = _descriptor.Descriptor(name='SetResponse', full_name='eve.sovereignty.hub.fuel.api.admin.SetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=363, serialized_end=376)
_SETREQUEST.fields_by_name['hub'].message_type = eve_dot_sovereignty_dot_hub_dot_hub__pb2._IDENTIFIER
_SETREQUEST.fields_by_name['fuel_type'].message_type = eve_dot_inventory_dot_generic__item__type__pb2._IDENTIFIER
_SETREQUEST.fields_by_name['context'].message_type = eve_dot_quasar_dot_admin_dot_admin__pb2._CONTEXT
DESCRIPTOR.message_types_by_name['SetRequest'] = _SETREQUEST
DESCRIPTOR.message_types_by_name['SetResponse'] = _SETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
SetRequest = _reflection.GeneratedProtocolMessageType('SetRequest', (_message.Message,), {'DESCRIPTOR': _SETREQUEST,
 '__module__': 'eve.sovereignty.hub.fuel.api.admin_pb2'})
_sym_db.RegisterMessage(SetRequest)
SetResponse = _reflection.GeneratedProtocolMessageType('SetResponse', (_message.Message,), {'DESCRIPTOR': _SETRESPONSE,
 '__module__': 'eve.sovereignty.hub.fuel.api.admin_pb2'})
_sym_db.RegisterMessage(SetResponse)
DESCRIPTOR._options = None
