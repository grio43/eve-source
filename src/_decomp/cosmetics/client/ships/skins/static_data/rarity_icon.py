#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\static_data\rarity_icon.py
from carbonui.util.color import Color
from cosmetics.common.ships.skins.static_data.component_rarity import ComponentRarityLevel

def get_path(rarity):
    if rarity == ComponentRarityLevel.STANDARD:
        return 'res:/UI/Texture/Classes/Cosmetics/Ship/cards/rarity/rarity_1.png'
    if rarity == ComponentRarityLevel.ADVANCED:
        return 'res:/UI/Texture/Classes/Cosmetics/Ship/cards/rarity/rarity_2.png'
    if rarity == ComponentRarityLevel.ELITE:
        return 'res:/UI/Texture/Classes/Cosmetics/Ship/cards/rarity/rarity_3.png'
    if rarity == ComponentRarityLevel.SUPERIOR:
        return 'res:/UI/Texture/Classes/Cosmetics/Ship/cards/rarity/rarity_4.png'
    if rarity == ComponentRarityLevel.STELLAR:
        return 'res:/UI/Texture/Classes/Cosmetics/Ship/cards/rarity/rarity_5.png'
    if rarity == ComponentRarityLevel.EMPYREAN:
        return 'res:/UI/Texture/Classes/Cosmetics/Ship/cards/rarity/rarity_6.png'


COMPONENT_RARITY_COLORS = {ComponentRarityLevel.STANDARD: Color.HextoRGBA(hexARGB='#E6FFFFFF'),
 ComponentRarityLevel.ADVANCED: Color.HextoRGBA(hexARGB='#FF409FFF'),
 ComponentRarityLevel.ELITE: Color.HextoRGBA(hexARGB='#FF40FF9F'),
 ComponentRarityLevel.SUPERIOR: Color.HextoRGBA(hexARGB='#FFCF40FF'),
 ComponentRarityLevel.STELLAR: Color.HextoRGBA(hexARGB='#FFFF6F40'),
 ComponentRarityLevel.EMPYREAN: Color.HextoRGBA(hexARGB='#FF40FFFF')}
COMPONENT_RARITY_NAMES = {ComponentRarityLevel.STANDARD: 'UI/Personalization/ShipSkins/DesignComponents/Rarities/Standard',
 ComponentRarityLevel.ADVANCED: 'UI/Personalization/ShipSkins/DesignComponents/Rarities/Advanced',
 ComponentRarityLevel.ELITE: 'UI/Personalization/ShipSkins/DesignComponents/Rarities/Elite',
 ComponentRarityLevel.SUPERIOR: 'UI/Personalization/ShipSkins/DesignComponents/Rarities/Superior',
 ComponentRarityLevel.STELLAR: 'UI/Personalization/ShipSkins/DesignComponents/Rarities/Stellar',
 ComponentRarityLevel.EMPYREAN: 'UI/Personalization/ShipSkins/DesignComponents/Rarities/Empyrean'}

def get_color(rarity):
    return COMPONENT_RARITY_COLORS.get(rarity, None)


def get_name(rarity):
    return COMPONENT_RARITY_NAMES.get(rarity, None)
