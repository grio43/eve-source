#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\player\field.py
from eveui.autocomplete.field import AutocompleteField
from eveui.autocomplete.player.provider import PlayerCorporationProvider, OrganizationProvider, PlayerOrPlayerOrganizationProvider, CharOrCorpOrAllianceProvider

class PlayerCorporationField(AutocompleteField):

    def __init__(self, **kwargs):
        kwargs['provider'] = PlayerCorporationProvider()
        kwargs.setdefault('suggestion_list_min_width', 360)
        super(PlayerCorporationField, self).__init__(**kwargs)


class OrganizationField(AutocompleteField):

    def __init__(self, **kwargs):
        kwargs['provider'] = OrganizationProvider()
        kwargs.setdefault('suggestion_list_min_width', 360)
        super(OrganizationField, self).__init__(**kwargs)


class PlayerOrPlayerOrganizationField(AutocompleteField):

    def __init__(self, **kwargs):
        kwargs['provider'] = PlayerOrPlayerOrganizationProvider()
        kwargs.setdefault('suggestion_list_min_width', 360)
        super(PlayerOrPlayerOrganizationField, self).__init__(**kwargs)


class CharOrCorpOrAllianceField(AutocompleteField):

    def __init__(self, **kwargs):
        kwargs['provider'] = CharOrCorpOrAllianceProvider()
        kwargs.setdefault('suggestion_list_min_width', 360)
        super(CharOrCorpOrAllianceField, self).__init__(**kwargs)
