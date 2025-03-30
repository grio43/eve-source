#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\assetholding\common\model\asset.py
import uuid
from assetholding.common.const import ASSET_INFINITE_CAPACITY, UnitType

class Asset(object):

    def __init__(self, identifier, benefactor_id, original_capacity, remaining_capacity, amount_per_unit):
        self._identifier = identifier
        self._benefactor_id = benefactor_id
        self._original_capacity = original_capacity
        self._remaining_capacity = remaining_capacity
        self._amount_per_unit = amount_per_unit

    @property
    def asset_type(self):
        raise NotImplementedError

    @property
    def identifier(self):
        return self._identifier

    @property
    def benefactor_id(self):
        return self._benefactor_id

    @property
    def original_capacity(self):
        return self._original_capacity

    @property
    def remaining_capacity(self):
        return self._remaining_capacity

    @remaining_capacity.setter
    def remaining_capacity(self, value):
        self._remaining_capacity = value

    @property
    def amount_per_unit(self):
        return self._amount_per_unit

    def is_finite(self):
        return self._original_capacity != ASSET_INFINITE_CAPACITY and self._remaining_capacity != ASSET_INFINITE_CAPACITY


class AssetISK(Asset):

    def __init__(self, identifier, benefactor_id, original_capacity, remaining_capacity, amount_per_unit):
        super(AssetISK, self).__init__(identifier, benefactor_id, original_capacity, remaining_capacity, amount_per_unit)

    @property
    def asset_type(self):
        return UnitType.ISK


class AssetLP(Asset):

    def __init__(self, identifier, benefactor_id, original_capacity, remaining_capacity, amount_per_unit, issuer_corp_id):
        super(AssetLP, self).__init__(identifier, benefactor_id, original_capacity, remaining_capacity, amount_per_unit)
        self._issuer_corp_id = issuer_corp_id

    @property
    def asset_type(self):
        return UnitType.LOYALTY_POINT

    @property
    def issuer_corp_id(self):
        return self._issuer_corp_id


class AssetSP(Asset):

    def __init__(self, identifier, benefactor_id, original_capacity, remaining_capacity, amount_per_unit):
        super(AssetSP, self).__init__(identifier, benefactor_id, original_capacity, remaining_capacity, amount_per_unit)

    @property
    def asset_type(self):
        return UnitType.SKILL_POINT
