#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\upgrades\client\external_messenger.py
import gametime
import httplib
import sovereignty.upgrades.client.errors as errors
from eveProto import timestamp_to_blue
from eveProto.generated.eve_public.inventory.generic_item_pb2 import Identifier as ItemID
from eveProto.generated.eve_public.inventory.generic_item_type_pb2 import Identifier as TypeID
from eveProto.generated.eve_public.sovereignty.hub.hub_pb2 import Identifier as HubID
from eveProto.generated.eve_public.sovereignty.hub.upgrade.api import requests_pb2
from eveProto.generated.eve_public.sovereignty.hub.upgrade.upgrade_pb2 import Identifier as UpgradeIdentifier
from eveProto.generated.eve_public.sovereignty.hub.upgrade.upgrade_type_pb2 import Identifier as UpgradeTypeIdentifier
from publicGateway.grpc.exceptions import GenericException
from sovereignty.client.base_external_messenger import BaseClientExternalMessenger
from sovereignty.upgrades.client.data_types import UpgradeStaticData, InstalledUpgradeData
from sovereignty.upgrades.client.proto_parsers import parse_hub_upgrades
from sovereignty.upgrades.const import UPGRADE_GROUP_IDS
TIMEOUT_SECONDS = 10

class SovUpgradesExternalMessenger(BaseClientExternalMessenger):

    def get_data_for_upgrades(self):
        try:
            request = requests_pb2.GetDefinitionsRequest()
            request_wrapper, response_wrapper, response_payload = self._send_request(request, requests_pb2.GetDefinitionsResponse)
        except GenericException as e:
            if e.response_primitive.status_code == httplib.NOT_FOUND:
                raise errors.SovUpgradeNotFoundError(e)
            raise errors.SovUpgradeDataUnavailableError(e)

        upgrade_definitions = []
        for upgrade in response_payload.definitions:
            upgrade_definitions.append(UpgradeStaticData(upgrade.installation_type.sequential, upgrade.power_required, upgrade.workforce_required, upgrade.fuel_type.sequential, upgrade.fuel_consumption_per_hour, upgrade.fuel_startup_cost, upgrade.mutually_exclusive_group))

        return upgrade_definitions

    def get_installed_upgrades(self, hub_id):
        try:
            request = requests_pb2.GetHubUpgradesRequest(hub=HubID(sequential=hub_id))
            request_wrapper, response_wrapper, response_payload = self._send_request(request, requests_pb2.GetHubUpgradesResponse)
        except GenericException as e:
            if e.response_primitive.status_code == httplib.FORBIDDEN:
                raise errors.SovUpgradeDataAccessRestrictedError(e)
            raise errors.SovUpgradeDataUnavailableError(e)

        installed_upgrade_data = parse_hub_upgrades(response_payload.hub_upgrades)
        last_updated = timestamp_to_blue(response_payload.hub_upgrades.last_updated)
        return (installed_upgrade_data, last_updated)

    def update_upgrade_configuration(self, hub_id, new_upgrades_item_ids, upgrades_states):
        configuration = [ requests_pb2.ProcessConfigurationRequest.UpgradeConfiguration(upgrade_type=TypeID(sequential=type_id), online=online) for type_id, online in upgrades_states ]
        try:
            request = requests_pb2.ProcessConfigurationRequest(new_upgrades=[ ItemID(sequential=x) for x in new_upgrades_item_ids ], configuration=configuration, hub=HubID(sequential=hub_id))
            request_wrapper, response_wrapper, response_payload = self._send_request(request, requests_pb2.ProcessConfigurationResponse)
        except GenericException as e:
            if e.response_primitive.status_code == httplib.BAD_REQUEST:
                raise errors.SovUpgradeInstallBadRequestError(e)
            if e.response_primitive.status_code == httplib.FORBIDDEN:
                raise errors.SovUpgradeInstallUnauthorizedError(e)
            if e.response_primitive.status_code == httplib.NOT_FOUND:
                raise errors.SovUpgradeInstallNotFoundError(e)
            if e.response_primitive.status_code == httplib.CONFLICT:
                raise errors.SovUpgradeInstallConflictError(e)
            if e.response_primitive.status_code == httplib.INTERNAL_SERVER_ERROR:
                raise errors.SovUpgradeInstallInternalError(e)
            raise errors.SovUpgradeInstallError(e)

        installed_upgrade_data = parse_hub_upgrades(response_payload.hub_upgrades)
        last_updated = response_payload.hub_upgrades.last_updated
        return installed_upgrade_data

    def uninstall_upgrade(self, hub_id, upgrade_type_id):
        try:
            request = requests_pb2.UninstallRequest(upgrade=UpgradeIdentifier(hub=HubID(sequential=hub_id), upgrade_type=UpgradeTypeIdentifier(sequential=upgrade_type_id)))
            request_wrapper, response_wrapper, response_payload = self._send_request(request, requests_pb2.UninstallResponse)
        except GenericException as e:
            if e.response_primitive.status_code == httplib.FORBIDDEN:
                raise errors.SovUpgradeUninstallForbiddenError(e)
            if e.response_primitive.status_code == httplib.NOT_FOUND:
                raise errors.SovUpgradeUninstallNotFoundError(e)
            if e.response_primitive.status_code == httplib.INTERNAL_SERVER_ERROR:
                raise errors.SovUpgradeUninstallInternalErrorError(e)
            raise errors.SovUpgradeUninstallError(e)


class FakeSovUpgradesExternalMessenger(object):
    fakeDataByRemainder = {0: {'power': 100,
         'workforce': 200,
         'fuel_type_id': 81144,
         'consumption_per_hour': 5,
         'startup_cost': 1,
         'mutually_exclusive_group': 'mutually_exclusive_group_A'},
     1: {'power': 10,
         'workforce': 20,
         'fuel_type_id': 81143,
         'consumption_per_hour': 3,
         'startup_cost': 2,
         'mutually_exclusive_group': 'mutually_exclusive_group_A'},
     2: {'power': 30,
         'workforce': 15,
         'fuel_type_id': 1230,
         'consumption_per_hour': 1,
         'startup_cost': 1,
         'mutually_exclusive_group': 'mutually_exclusive_group_B'},
     3: {'power': 400,
         'workforce': 300,
         'fuel_type_id': 81143,
         'consumption_per_hour': 50,
         'startup_cost': 30,
         'mutually_exclusive_group': 'mutually_exclusive_group_B'}}
    PLACEHOLDER_KEY = (-1, -1)
    fakeInstalledByRemainder = {0: [InstalledUpgradeData(32422, True, PLACEHOLDER_KEY), InstalledUpgradeData(81619, False, PLACEHOLDER_KEY), InstalledUpgradeData(2001, True, PLACEHOLDER_KEY)],
     1: [InstalledUpgradeData(81623, False, PLACEHOLDER_KEY), InstalledUpgradeData(81619, False, PLACEHOLDER_KEY), InstalledUpgradeData(2009, True, PLACEHOLDER_KEY)],
     2: [InstalledUpgradeData(81615, True, PLACEHOLDER_KEY),
         InstalledUpgradeData(2008, True, PLACEHOLDER_KEY),
         InstalledUpgradeData(2009, True, PLACEHOLDER_KEY),
         InstalledUpgradeData(81621, True, PLACEHOLDER_KEY),
         InstalledUpgradeData(32422, True, PLACEHOLDER_KEY),
         InstalledUpgradeData(81619, True, PLACEHOLDER_KEY),
         InstalledUpgradeData(2001, True, PLACEHOLDER_KEY),
         InstalledUpgradeData(81623, False, PLACEHOLDER_KEY),
         InstalledUpgradeData(82496, False, PLACEHOLDER_KEY)],
     3: [InstalledUpgradeData(81615, False, PLACEHOLDER_KEY), InstalledUpgradeData(2008, False, PLACEHOLDER_KEY), InstalledUpgradeData(2009, False, PLACEHOLDER_KEY)]}
    byHubID = {1016094694774L: fakeInstalledByRemainder[2]}

    def get_data_for_upgrades(self):
        import evetypes
        return [ self._get_data_for_upgrade(x) for x in [32422,
         81619,
         2001,
         81623,
         2009,
         81615,
         2008,
         81621,
         32422,
         82496] + list(evetypes.GetTypeIDsByGroups(UPGRADE_GROUP_IDS)) ]

    def _get_data_for_upgrade(self, type_id):
        data = self.fakeDataByRemainder.get(type_id % 4, None)
        return UpgradeStaticData(type_id=type_id, **data)

    def get_installed_upgrades(self, hub_id):
        if hub_id in self.byHubID:
            return self.byHubID[hub_id]
        installedUpgrades = [ x.take_copy() for x in self.fakeInstalledByRemainder[hub_id % 3] ]
        for x in installedUpgrades:
            x._upgrade_id_key = (hub_id, x.upgrade_type_id)

        return (installedUpgrades, gametime.GetWallclockTime())

    def update_upgrade_configuration(self, new_upgrades_item_ids, upgrades_states):
        print 'save configuration'
        installed_upgrade_data = [ InstalledUpgradeData(typeID, onlineState, (-1, typeID)) for typeID, onlineState in upgrades_states ]
        return installed_upgrade_data

    def uninstall_upgrade(self, hub_id, upgrade_type_id):
        print 'uninstall_upgrade'
