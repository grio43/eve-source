#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\live_data\component_license.py
from cosmetics.common.ships.skins.live_data.component_license import BaseComponentLicense
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.component_pb2 import Identifier as ComponentIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.license_pb2 import Kind as LicenseKind
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.coating.coating_pb2 import Identifier as CoatingIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.pattern.pattern_pb2 import Identifier as PatternIdentifier

class ComponentLicense(BaseComponentLicense):
    LICENSE_KIND_PROTO = LicenseKind
    COMPONENT_IDENTIFIER_PROTO = ComponentIdentifier
    COATING_IDENTIFIER_PROTO = CoatingIdentifier
    PATTERN_IDENTIFIER_PROTO = PatternIdentifier
