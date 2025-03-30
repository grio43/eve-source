#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\structurePaintworkLicensesController.py
from cosmetics.common.structures.fitting import StructurePaintwork
from cosmetics.client.messengers.entitlements.corporation.structure.requestMessenger import PublicRequestsMessenger

class StructurePaintworkLicensesController(object):

    def __init__(self, public_gateway):
        self._cache = {}
        self._catalogue_cache = None
        self._requests_messenger = PublicRequestsMessenger(public_gateway.publicGateway)

    def flush_cache(self):
        self._cache = {}
        self._catalogue_cache = None

    def request_license_for_structures(self, structure_ids, paintwork, duration):
        return self._requests_messenger.issue_request(paintwork, duration, structure_ids)

    def request_revoke_license(self, license_id):
        return self._requests_messenger.revoke_request(license_id)

    def admin_request_license_for_structures(self, structure_ids, paintwork, duration, lp_cost = -1):
        return self._requests_messenger.admin_issue_request(paintwork, duration, structure_ids, lp_cost)

    def get_license(self, structure_id, license_id):
        return self._requests_messenger.get_request(structure_id, license_id)

    def get_licenses_for_corporation(self):
        return self._requests_messenger.get_for_corporation()

    def get_structure_paintwork_licenses_catalogue(self):
        if self._catalogue_cache is None:
            self._catalogue_cache = self._requests_messenger.get_catalogue_request()
        return self._catalogue_cache
