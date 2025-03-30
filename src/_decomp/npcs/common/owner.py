#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\npcs\common\owner.py
from eve.common.lib.appConst import factionUnknown
from eve.common.script.sys.idCheckers import IsFaction
from inventorycommon.const import ownerUnknown, ownerSystem
from npcs.npccorporations import get_corporation_faction_id

def get_npc_faction(owner_id):
    if owner_id in (ownerSystem, ownerUnknown, factionUnknown):
        return factionUnknown
    if IsFaction(owner_id):
        return owner_id
    return get_corporation_faction_id(owner_id)
