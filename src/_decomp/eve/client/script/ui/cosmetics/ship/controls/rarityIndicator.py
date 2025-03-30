#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\controls\rarityIndicator.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from cosmetics.client.ships.skins.static_data import rarity_icon
from eve.client.script.ui import eveColor
from localization import GetByLabel

class RarityIndicator(Container):
    default_width = 32
    default_height = 32
    default_state = uiconst.UI_NORMAL

    def __init__(self, rarity, *args, **kwargs):
        super(RarityIndicator, self).__init__(*args, **kwargs)
        self.rarity = rarity
        self.construct_layout()

    def construct_layout(self):
        self.icon = Sprite(name='icon', parent=self, state=uiconst.UI_DISABLED, texturePath=rarity_icon.get_path(self.rarity), color=rarity_icon.get_color(self.rarity) or eveColor.WHITE, outputMode=uiconst.OutputMode.COLOR_AND_GLOW, glowBrightness=0.4, pos=(0, 0, 32, 32))

    def GetHint(self):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/RarityName', rarity=GetByLabel(rarity_icon.get_name(self.rarity)))
