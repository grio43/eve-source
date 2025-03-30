#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\controls\tierIndicator.py
from carbonui import TextHeadline, Align
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor

class TierIndicator(Container):
    default_width = 336
    default_height = 58

    def __init__(self, tier_level = None, **kw):
        super(TierIndicator, self).__init__(**kw)
        self.bg_sprite = Sprite(name='bg_sprite', bgParent=self)
        self.label = TextHeadline(name='tier_label', parent=self, align=Align.CENTER, color=eveColor.BLACK, shadowOffset=(0, 0), bold=True)
        if tier_level:
            self.set_tier(tier_level)

    def set_tier(self, tier_level):
        texture_path = 'res:/UI/Texture/classes/Cosmetics/Ship/cards/tier/tier_{level}.png'.format(level=tier_level)
        self.bg_sprite.texturePath = texture_path
        self.label.text = u'{}'.format(tier_level)
