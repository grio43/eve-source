#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\npc\field.py
from eveui.autocomplete.field import AutocompleteField
from eveui.autocomplete.npc.provider import FactionProvider, NpcCorporationProvider, AgentProvider

class NpcCorporationFactionField(AutocompleteField):

    def __init__(self, faction_filter = None, corporation_filter = None, **kwargs):
        kwargs['provider'] = [FactionProvider(filter=faction_filter), NpcCorporationProvider(filter=corporation_filter)]
        kwargs.setdefault('suggestion_list_min_width', 360)
        super(NpcCorporationFactionField, self).__init__(**kwargs)


class FactionField(AutocompleteField):

    def __init__(self, filter = None, **kwargs):
        kwargs['provider'] = FactionProvider(filter=filter)
        kwargs.setdefault('suggestion_list_min_width', 360)
        super(FactionField, self).__init__(**kwargs)


class NpcCorporationField(AutocompleteField):

    def __init__(self, filter = None, **kwargs):
        kwargs['provider'] = NpcCorporationProvider(filter=filter)
        kwargs.setdefault('suggestion_list_min_width', 360)
        super(NpcCorporationField, self).__init__(**kwargs)


class AgentField(AutocompleteField):

    def __init__(self, filter = None, **kwargs):
        kwargs['provider'] = AgentProvider(filter)
        kwargs.setdefault('suggestion_list_min_width', 360)
        super(AgentField, self).__init__(**kwargs)
