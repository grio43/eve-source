#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\itemcompression\__init__.py
import globalConfig
from itemcompression import data
SLIM_ATTRIBUTE_COMPRESSION_FACILITY_TYPELISTS = 'compression_facility_typelists'
MAX_FACILITY_ACTIVATION_RANGE = 250000
STRUCTURE_COMPRESSIBLE_TYPE_LIST_ID = 336

def is_compression_enabled(macho_net_service):
    return globalConfig.IsMaterialCompressionEnabled(macho_net_service)


def get_compressed_type(source_type_id):
    return data.get_compressed_type_id(source_type_id)


def is_compressible_type(source_type_id):
    return data.is_compressible_type(source_type_id)
