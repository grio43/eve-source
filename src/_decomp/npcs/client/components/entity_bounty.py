#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\npcs\client\components\entity_bounty.py
from dogma.const import attributeEntityKillBounty
from spacecomponents.common.helper import HasEntityBountyComponent, GetEntityBountyTypeAttributes

def get_type_kill_bounty(type_id):
    displayAttributes = sm.GetService('godma').GetType(type_id).displayAttributes
    attributes = [ attr for attr in displayAttributes if attr.attributeID == attributeEntityKillBounty ]
    if attributes:
        return attributes[0].value
    return 0


def get_owner_id_for_item(item_id):
    slimItem = sm.GetService('michelle').GetItem(item_id)
    if slimItem:
        return slimItem.ownerID


def get_entity_bounty(type_id, item_id):
    kill_bounty = get_type_kill_bounty(type_id)
    if kill_bounty > 0 and HasEntityBountyComponent(type_id):
        owner_id = get_owner_id_for_item(item_id)
        if owner_id is None:
            return 0
        attributes = GetEntityBountyTypeAttributes(type_id)
        if owner_id not in attributes.bountyMultipliersByOwner:
            return 0
        bounty_multiplier = attributes.bountyMultipliersByOwner[owner_id]
        return kill_bounty * bounty_multiplier
    return kill_bounty
