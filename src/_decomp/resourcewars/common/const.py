#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\resourcewars\common\const.py
from eve.common.lib.appConst import factionAmarrEmpire, factionCaldariState, factionGallenteFederation, factionMinmatarRepublic
import inventorycommon.const as invconst
FACTION_TO_RW_LP_CORP = {factionAmarrEmpire: 1000283,
 factionCaldariState: 1000284,
 factionGallenteFederation: 1000285,
 factionMinmatarRepublic: 1000286}
RW_LP_CORPORATIONS = FACTION_TO_RW_LP_CORP.values()
FACTION_TO_PIRATE_CORP = {factionAmarrEmpire: 1000162,
 factionCaldariState: 1000127,
 factionGallenteFederation: 1000135,
 factionMinmatarRepublic: 1000124}
RW_PIRATE_CORPORATIONS = FACTION_TO_PIRATE_CORP.values()
FACTION_TO_RW_ORE_TYPE = {factionAmarrEmpire: invconst.typeResourceWarsOreAmarrNormal,
 factionCaldariState: invconst.typeResourceWarsOreCaldariNormal,
 factionGallenteFederation: invconst.typeResourceWarsOreGallenteNormal,
 factionMinmatarRepublic: invconst.typeResourceWarsOreMinmatarNormal}
RW_HAULER_WRECK_TYPES = [46338,
 46339,
 46341,
 46342]
RW_CORPORATIONS = FACTION_TO_RW_LP_CORP.values()
RESOURCE_WARS_LOG_CHANNEL = 'resourcewars'
HAULER_STATE_AVAILABLE = 1
HAULER_STATE_FULL = 2
HAULER_STATE_DESTROYED = 3
HAULER_STATE_SECURED = 4
HAULER_CAPACITY_UNLIMITED = 999999999999L
HAULER_CAPACITY_UNLIMITED_STR = u'\u221e'

class PirateAttack(object):

    def __init__(self, killerShipItem, killedShipItem):
        self.killerShipItem = killerShipItem
        self.killedShipItem = killedShipItem


class PirateAttackByCharacter(PirateAttack):

    def __init__(self, characterID, killerShipItem, killedShipItem):
        self.characterID = characterID
        PirateAttack.__init__(self, killerShipItem, killedShipItem)
