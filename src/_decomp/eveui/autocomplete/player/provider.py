#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\player\provider.py
from eve.client.script.ui.util import searchUtil
from eve.common.script.search.const import ResultType, min_wildcard_length
from eve.common.script.util.facwarCommon import IsAnyFWFaction
from eveui.autocomplete import Provider
from eveui.autocomplete.player.suggestion import OwnerIdentitySuggestion
from eve.common.script.sys.idCheckers import IsFaction, IsNPCCorporation

class PlayerCorporationProvider(Provider):

    def __call__(self, query, previous_suggestions):
        if len(query) < min_wildcard_length:
            return []
        results = searchUtil.GetResultsList(query, [ResultType.corporation])
        return [ (-i, OwnerIdentitySuggestion(corp_id)) for i, corp_id in enumerate(results) ]


class OrganizationProvider(Provider):

    def __call__(self, query, previous_suggestions):
        if len(query) < min_wildcard_length:
            return []
        results = searchUtil.GetResultsList(query, [ResultType.character,
         ResultType.corporation,
         ResultType.alliance,
         ResultType.faction])
        return [ (-i, OwnerIdentitySuggestion(owner_id)) for i, owner_id in enumerate(results) ]


class PlayerOrPlayerOrganizationProvider(Provider):

    def __call__(self, query, previous_suggestions):
        if len(query) < min_wildcard_length:
            return []
        results = searchUtil.GetResultsList(query, [ResultType.faction,
         ResultType.character,
         ResultType.corporation,
         ResultType.alliance])
        return [ (-i, OwnerIdentitySuggestion(owner_id)) for i, owner_id in enumerate(results) if _is_player_or_player_organization(owner_id) ]


class CharOrCorpOrAllianceProvider(Provider):

    def __call__(self, query, previous_suggestions):
        if len(query) < min_wildcard_length:
            return []
        results = searchUtil.GetResultsList(query, [ResultType.character, ResultType.corporation, ResultType.alliance])
        return [ (-i, OwnerIdentitySuggestion(owner_id)) for i, owner_id in enumerate(results) if _is_player_or_non_npc_player_organization(owner_id) and owner_id != session.charid ]


def _is_player_or_player_organization(entityId):
    if IsFaction(entityId) and not IsAnyFWFaction(entityId):
        return False
    return True


def _is_player_or_non_npc_player_organization(entityId):
    if IsNPCCorporation(entityId):
        return False
    if IsFaction(entityId) and not IsAnyFWFaction(entityId):
        return False
    return True
