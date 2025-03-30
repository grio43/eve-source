#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\cards\cardConst.py
from itertoolsext.Enum import Enum
card_width = 168
card_height = 234

@Enum

class CardBackground(object):
    PUBLIC = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/background.png'
    PUBLIC_STACK = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/stack/background.png'
    TARGETED_AT_CHARACTER = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/listing/targeted_character_bg.png'
    TARGETED_AT_CHARACTER_STACK = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/listing/targeted_character_stack_bg.png'
    TARGETED_AT_ORGANIZATION = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/listing/targeted_organization_bg.png'
    TARGETED_AT_ORGANIZATION_STACK = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/listing/targeted_organization_stack_bg.png'
    TARGETED_AT_ORGANIZATION_BRANDED = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/listing/targeted_organization_branded_bg.png'
    TARGETED_AT_ORGANIZATION_BRANDED_STACK = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/listing/targeted_organization_branded_stack_bg.png'
    SEQUENCING = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/sequencing/background.png'
    SEQUENCING_SELECTED = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/sequencing/background_selected.png'
    DEFAULT = PUBLIC
    DEFAULT_STACK = PUBLIC_STACK


@Enum

class CardOutline(object):
    PUBLIC = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/components/outline_public.png'
    PUBLIC_STACK = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/components/outline_public_stack.png'
    TARGETED_AT_CHARACTER = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/components/outline_targeted_character.png'
    TARGETED_AT_CHARACTER_STACK = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/components/outline_targeted_character_stack.png'
    TARGETED_AT_ORGANIZATION = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/components/outline_targeted_organization.png'
    TARGETED_AT_ORGANIZATION_STACK = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/components/outline_targeted_organization_stack.png'
    DEFAULT = PUBLIC
    DEFAULT_STACK = PUBLIC_STACK


@Enum

class CardMask(object):
    PUBLIC = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/mask.png'
    PUBLIC_STACK = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/mask.png'
    TARGETED_AT_CHARACTER = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/listing/targeted_character_mask.png'
    TARGETED_AT_CHARACTER_STACK = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/listing/targeted_character_stack_mask.png'
    TARGETED_AT_ORGANIZATION = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/listing/targeted_organization_mask.png'
    TARGETED_AT_ORGANIZATION_STACK = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/listing/targeted_organization_stack_mask.png'
    SEQUENCING = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/sequencing/mask.png'
    DEFAULT = PUBLIC
    DEFAULT_STACK = PUBLIC_STACK
