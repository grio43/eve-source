#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\redeem\data.py
import evetypes
from inventorycommon.const import typeKredits, typeLoyaltyPointsHeraldry, groupBooster
TYPE_THAT_GIVES_SKILLPOINTS = 43680
TYPE_THAT_GIVES_ISK = typeKredits
TYPE_THAT_GIVES_HERALDRY_LP = typeLoyaltyPointsHeraldry

def get_redeem_data():
    return RedeemData({54652: 1000,
     54653: 2500,
     63303: 4000,
     63304: 4500,
     54650: 5000,
     63305: 5500,
     63306: 6000,
     63307: 6500,
     63308: 7000,
     54654: 7500,
     63309: 8000,
     63310: 9000,
     52520: 10000,
     63311: 11000,
     63312: 12000,
     63313: 13000,
     63314: 14000,
     63315: 15000,
     63316: 16000,
     63317: 17000,
     63318: 18000,
     63623: 19000,
     63624: 20000,
     63319: 21000,
     63320: 22000,
     63321: 23000,
     63322: 24000,
     49756: 25000,
     63323: 27000,
     63324: 28000,
     63325: 29000,
     57003: 30000,
     63326: 31000,
     63327: 32000,
     63328: 33000,
     63329: 34000,
     63330: 35000,
     63331: 42000,
     63332: 43000,
     63333: 44000,
     63334: 45000,
     63335: 46000,
     63336: 47000,
     63337: 48000,
     63338: 49000,
     49809: 50000,
     63339: 51000,
     63340: 52000,
     63824: 75000,
     49810: 100000,
     63825: 125000,
     54648: 150000,
     43680: 250000,
     52269: 500000,
     52270: 750000,
     52318: 750000,
     52263: 1000000,
     56707: 1620000})


class RedeemData(object):

    def __init__(self, skill_points_by_type):
        self._skill_points_by_type = skill_points_by_type

    def get_skill_points_to_give(self, typeID, quantity):
        return self._skill_points_by_type.get(typeID, 0) * quantity

    def is_skill_inserter(self, typeID):
        return typeID in self._skill_points_by_type

    def is_booster(self, typeID):
        return evetypes.GetGroupID(typeID) == groupBooster

    def needs_to_redeem_in_station(self, tokens):
        if not tokens:
            return True
        return any((self.must_redeem_type_in_station(t) for t in tokens))

    def must_redeem_type_in_station(self, token):
        typeID = token.typeID
        if self.is_skill_inserter(typeID):
            return False
        if typeID == TYPE_THAT_GIVES_ISK:
            return False
        if typeID == TYPE_THAT_GIVES_HERALDRY_LP:
            return False
        if self.is_booster(typeID) and token.soulbound:
            return False
        return True

    def is_auto_injected(self, token):
        import expertSystems
        return token.soulbound or token.typeID == TYPE_THAT_GIVES_ISK or token.typeID == TYPE_THAT_GIVES_HERALDRY_LP or self.is_skill_inserter(token.typeID) or expertSystems.is_expert_system(token.typeID)

    def get_skillpoints_redeemed(self, types):
        skillpoints = 0
        for type_id, quantity in types:
            skillpoints += self.get_skill_points_to_give(type_id, quantity)

        return skillpoints
