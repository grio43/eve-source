#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\const.py
import eveicon
from eve.common.lib import appConst
import shipgroup

class ShipShape(object):
    UNDEFINED = 0
    BOX = 1
    LONG = 2
    TALL = 3
    WIDE = 4


class ShipSize(object):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    TITAN = 4


class MomentSteps(object):
    TEASE_1 = 10
    TEASE_2 = 11
    TEASE_3 = 12
    BOOSTERS_1 = 20
    BOOSTERS_2 = 21
    BOOSTERS_3 = 22
    REVEAL_1 = 30
    REVEAL_2 = 31
    REVEAL_3 = 32
    CLIMAX_1 = 40
    CLIMAX_2 = 41
    CLIMAX_3 = 42


SHAPE_BY_EVE_TYPE_ID = {}
SHAPE_BY_HULL_NAME = {'gdn1_fn': ShipShape.LONG,
 'gc3_t1': ShipShape.BOX,
 'gc3_t2': ShipShape.BOX,
 'gb1_t1': ShipShape.TALL,
 'deabc1_t1': ShipShape.WIDE,
 'tgdn01_t1': ShipShape.WIDE,
 'gf7_t1': ShipShape.TALL,
 'mi1_t1': ShipShape.WIDE,
 'gbc3_t1': ShipShape.BOX,
 'ai2_t2': ShipShape.BOX,
 'ai2_t1': ShipShape.BOX,
 'gb1_t2': ShipShape.BOX,
 'gb2_t1': ShipShape.BOX,
 'gbc1_t1': ShipShape.BOX,
 'gbc1_t2a': ShipShape.BOX,
 'angb1_t1': ShipShape.BOX,
 'cbc2_t1': ShipShape.BOX,
 'cbc2_t2': ShipShape.BOX,
 'soeb1_t1': ShipShape.BOX,
 'soec1_t1': ShipShape.WIDE,
 'conf5_t1': ShipShape.LONG,
 'morb1_t1': ShipShape.WIDE,
 'cf5_t1': ShipShape.BOX,
 'gf1_t1': ShipShape.BOX,
 'gs1_t1': ShipShape.LONG,
 'ac3_t1': ShipShape.BOX,
 'ac3_t2': ShipShape.BOX,
 'mc2_t1': ShipShape.BOX,
 'mc2_t2a': ShipShape.BOX,
 'mc2_t2c': ShipShape.BOX,
 'mc2_vii': ShipShape.BOX,
 'soctbc1_t1': ShipShape.TALL,
 'soctf2_t1': ShipShape.LONG,
 'af6_t1': ShipShape.BOX,
 'gf5_t1': ShipShape.BOX,
 'gf5_t2': ShipShape.BOX,
 'gf7_t1': ShipShape.BOX,
 'cf2_t1': ShipShape.LONG,
 'cf2_t2a': ShipShape.LONG,
 'cf2_t2b': ShipShape.LONG,
 'cf2_xii': ShipShape.LONG,
 'mf3_t1': ShipShape.BOX,
 'conf3_t1': ShipShape.BOX,
 'mf2_t2b': ShipShape.LONG,
 'soctde1_t1': ShipShape.LONG,
 'soctb1_t1': ShipShape.LONG,
 'tgdn01_t1': ShipShape.WIDE,
 'gb3_t1': ShipShape.TALL,
 'cf4_t1': ShipShape.BOX,
 'cf4_t2': ShipShape.BOX,
 'cc1_t1': ShipShape.BOX,
 'cc1_fn': ShipShape.BOX,
 'cc1_t2a': ShipShape.WIDE,
 'cc1_x': ShipShape.WIDE,
 'mf2_t1': ShipShape.BOX,
 'af5_t1': ShipShape.TALL,
 'af5_t2b': ShipShape.TALL,
 'gf2_t1': ShipShape.BOX,
 'gf2_t2': ShipShape.BOX,
 'gf4_t1': ShipShape.BOX,
 'gf4_tournament': ShipShape.BOX,
 'gf4_t2a': ShipShape.BOX,
 'gf4_t2b': ShipShape.BOX,
 'mf6_t1': ShipShape.WIDE,
 'mf6_t2': ShipShape.WIDE,
 'sf3_t1': ShipShape.WIDE,
 'cc3_t1': ShipShape.WIDE,
 'cc3_t2': ShipShape.WIDE,
 'cc2_t1': ShipShape.WIDE,
 'cc2_t2a': ShipShape.WIDE,
 'cc2_t2b': ShipShape.WIDE,
 'cc2_xii': ShipShape.WIDE,
 'ac2_t1': ShipShape.BOX,
 'ac2_t2a': ShipShape.BOX,
 'ac2_t2b': ShipShape.BOX,
 'ac2_ix': ShipShape.BOX,
 'gy1_t1': ShipShape.BOX,
 'gf8_t1': ShipShape.BOX,
 'sf1_t1': ShipShape.BOX,
 'tgf01_t1': ShipShape.BOX,
 'tgb01_t1': ShipShape.BOX,
 'af2_t1': ShipShape.BOX,
 'af2_t2': ShipShape.BOX,
 'mfaux1_t1': ShipShape.TALL,
 'ai1_t1': ShipShape.BOX,
 'ai1_t2': ShipShape.BOX,
 'af1_t1': ShipShape.BOX,
 'asc1_t3': ShipShape.BOX}
SHAPE_BY_SHIP_CLASS_ID = {}
UNIQUE_MOMENT_ID_BY_EVE_HULL_NAME = {'at1_t1': 1.0,
 'ct1_t1': 2.0,
 'gt1_t1': 3.0,
 'mt1_t1': 4.0,
 'angt1_t1': 5.0}
SIZE_BY_EVE_TYPE_ID = {}
SIZE_BY_HULL_NAME = {'tgdn01_t1': ShipSize.LARGE,
 'gdn1_t1': ShipSize.LARGE,
 'gdn1_fn': ShipSize.LARGE,
 'oreba1_t1': ShipSize.SMALL,
 'oreba2_t1': ShipSize.SMALL,
 'oreba3_t1': ShipSize.SMALL}
SIZE_BY_SHIP_CLASS_ID = {shipgroup.groupRookie: ShipSize.SMALL,
 shipgroup.groupFrigate: ShipSize.SMALL,
 shipgroup.groupDestroyer: ShipSize.SMALL,
 shipgroup.groupCruiser: ShipSize.SMALL,
 shipgroup.groupBattlecruiser: ShipSize.MEDIUM,
 shipgroup.groupBattleship: ShipSize.MEDIUM,
 shipgroup.groupMiningBarge: ShipSize.MEDIUM,
 shipgroup.groupJumpFreighter: ShipSize.LARGE,
 shipgroup.groupCarrier: ShipSize.LARGE,
 shipgroup.groupFreighter: ShipSize.LARGE,
 shipgroup.groupCapitalIndustrial: ShipSize.LARGE,
 shipgroup.groupTitan: ShipSize.TITAN}
UNDEFINED_FACTION_LOGO_ID = 99
FACTION_BACKGROUND_LOGOS_IDS = {appConst.factionAmarrEmpire: 0,
 appConst.factionCaldariState: 1,
 appConst.factionMinmatarRepublic: 2,
 appConst.factionGallenteFederation: 3,
 appConst.factionGuristasPirates: 4,
 appConst.factionSistersOfEVE: 5,
 appConst.factionAngelCartel: 6,
 appConst.factionSanshasNation: 7,
 appConst.factionTheBloodRaiderCovenant: 8,
 appConst.factionTriglavian: 9,
 appConst.factionSerpentis: 10,
 appConst.factionORE: 11,
 appConst.factionMordusLegion: 12,
 appConst.factionEDENCOM: 13,
 appConst.factionTheSyndicate: 14,
 appConst.factionAmmatar: 15,
 appConst.factionDeathless: 16,
 appConst.factionCONCORDAssembly: 17,
 appConst.factionKhanidKingdom: 18,
 appConst.factionSocietyOfConsciousThought: 19,
 appConst.factionInterBus: 20}
