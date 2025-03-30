#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\launcher\product\product_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/launcher/product/product.proto', package='eve_public.app.launcher.product', syntax='proto3', serialized_options='ZJgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/launcher/product', create_key=_descriptor._internal_create_key, serialized_pb='\n-eve_public/app/launcher/product/product.proto\x12\x1feve_public.app.launcher.product*\xb1\x01\n\x0fLauncherProduct\x12 \n\x1cLAUNCHER_PRODUCT_UNSPECIFIED\x10\x00\x12\x1d\n\x19LAUNCHER_PRODUCT_LAUNCHER\x10\x01\x12\x1f\n\x1bLAUNCHER_PRODUCT_EVE_ONLINE\x10\x02\x12\x1d\n\x19LAUNCHER_PRODUCT_VANGUARD\x10\x03\x12\x1d\n\x19LAUNCHER_PRODUCT_FRONTIER\x10\x04BLZJgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/launcher/productb\x06proto3')
_LAUNCHERPRODUCT = _descriptor.EnumDescriptor(name='LauncherProduct', full_name='eve_public.app.launcher.product.LauncherProduct', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='LAUNCHER_PRODUCT_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='LAUNCHER_PRODUCT_LAUNCHER', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='LAUNCHER_PRODUCT_EVE_ONLINE', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='LAUNCHER_PRODUCT_VANGUARD', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='LAUNCHER_PRODUCT_FRONTIER', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=83, serialized_end=260)
_sym_db.RegisterEnumDescriptor(_LAUNCHERPRODUCT)
LauncherProduct = enum_type_wrapper.EnumTypeWrapper(_LAUNCHERPRODUCT)
LAUNCHER_PRODUCT_UNSPECIFIED = 0
LAUNCHER_PRODUCT_LAUNCHER = 1
LAUNCHER_PRODUCT_EVE_ONLINE = 2
LAUNCHER_PRODUCT_VANGUARD = 3
LAUNCHER_PRODUCT_FRONTIER = 4
DESCRIPTOR.enum_types_by_name['LauncherProduct'] = _LAUNCHERPRODUCT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
DESCRIPTOR._options = None
