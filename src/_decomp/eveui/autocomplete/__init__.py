#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\__init__.py
try:
    from .field import AutocompleteField
    from .fuzzy import fuzzy_match, get_highlighted_string
    from .suggestion_entry import LargeSuggestionEntry
    from .provider import Provider, NameCache, NameCacheProvider
    from .suggestion import Suggestion
    from .item.field import ItemField, ItemTypeField
    from .item.provider import ItemCategoryProvider, ItemGroupProvider, ItemTypeProvider
    from .item.suggestion import ItemGroupSuggestion, ItemCategorySuggestion, ItemTypeSuggestion
    from .location.field import LocationField, SolarSystemField
    from .location.provider import RegionProvider, ConstellationProvider, SolarSystemProvider, StationProvider
    from .location.suggestion import LocationSuggestion
    from .npc.field import NpcCorporationFactionField, NpcCorporationField, FactionField, AgentField
    from .npc.provider import NpcCorporationProvider, FactionProvider
    from .npc.suggestion import NpcCorporationSuggestion
    from .player.field import PlayerCorporationField
    from .player.field import OrganizationField
    from .player.field import PlayerOrPlayerOrganizationField
    from .player.provider import PlayerCorporationProvider
    from .player.provider import OrganizationProvider
    from .player.provider import PlayerOrPlayerOrganizationProvider
    from .player.suggestion import OwnerIdentitySuggestion
    from .ship.field import ShipField
    from .ship.provider import ShipTypeProvider, ShipClassProvider
    from .ship.suggestion import ShipClassSuggestion, ShipTypeSuggestion
except ImportError:
    import monolithconfig
    if monolithconfig.on_client():
        raise
