#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\live_data\skin_listing_buyer_fee.py
from itertoolsext.Enum import Enum
from eveProto.generated.eve_public.cosmetic.market.market_pb2 import BuyerFee
from eveProto.generated.eve_public.loyaltypoints.loyaltypoints_pb2 import Currency as LoyaltyPointsCurrency
from eveProto.generated.eve_public.corporation.corporation_pb2 import Identifier as CorporationIdentifier

@Enum

class ListingBuyerFeeType(object):
    BRANDED_LISTING_BUYER_FEE = 'BRANDED_LISTING_BUYER_FEE'
    REGULAR_LISTING_BUYER_FEE = 'REGULAR_LISTING_BUYER_FEE'


class ListingBuyerFee(object):

    def __init__(self, lp_amount, lp_corp):
        self._lp_amount = lp_amount
        self._lp_corp = lp_corp

    def __eq__(self, other):
        return self.lp_amount == other.lp_amount and self.lp_corp == other.lp_corp

    def __str__(self):
        return 'lp_amount: {lp_amount}, lp_corp: {lp_corp}'.format(lp_amount=self.lp_amount, lp_corp=self.lp_corp)

    @property
    def lp_amount(self):
        return self._lp_amount

    @property
    def lp_corp(self):
        return self._lp_corp

    @classmethod
    def from_proto(cls, payload):
        return cls(payload.loyalty_points.amount, payload.loyalty_points.associated_corporation.sequential)

    def to_proto(self):
        return BuyerFee(loyalty_points=LoyaltyPointsCurrency(amount=self.lp_amount, associated_corporation=CorporationIdentifier(sequential=self.lp_corp)))
