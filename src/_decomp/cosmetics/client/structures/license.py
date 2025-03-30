#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\structures\license.py
from datetime import datetime
from cosmetics.common.structures.license import StructurePaintworkLicense

def create_structure_paintwork_license_from_proto_license(license_id, license_attributes):
    paintwork_license = StructurePaintworkLicense(license_id=license_id, corp_id=license_attributes.corporation.sequential, char_id=license_attributes.activator.sequential, structure_id=license_attributes.structure.sequential, activation_timestamp=datetime.fromtimestamp(license_attributes.issued.seconds), duration=license_attributes.duration.seconds)
    return paintwork_license
