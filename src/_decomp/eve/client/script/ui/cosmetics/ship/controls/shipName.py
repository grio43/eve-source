#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\controls\shipName.py
import eveicon
import evetypes
from carbonui import Align, TextHeader, uiconst, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uiconst import BlendMode
from eveservices.menu import GetMenuService

class ShipName(Container):
    default_width = 158
    default_height = 58
    default_state = uiconst.UI_NORMAL

    def __init__(self, ship_type_id = None, *args, **kwargs):
        super(ShipName, self).__init__(*args, **kwargs)
        self._ship_type_id = ship_type_id
        self.construct_layout()
        self.update()

    def construct_layout(self):
        sprite_container = Container(name='sprite_container', parent=self, align=Align.TOTOP, height=27)
        self.ship_group_icon = Sprite(name='ship_group_icon', parent=sprite_container, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, pos=(0, 8, 16, 16), blendMode=BlendMode.ADD, color=TextColor.NORMAL)
        Sprite(name='highlight', parent=sprite_container, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/ship_name_highlight.png', pos=(0, -8, 45, 19), blendMode=BlendMode.ADD)
        Sprite(name='background', parent=sprite_container, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/ship_name_background.png', pos=(0, 0, 158, 27))
        label_container = Container(name='label_container', parent=self, align=Align.TOTOP, height=23, padTop=8)
        self.label = TextHeader(name='label', parent=label_container, align=Align.CENTER)

    def update(self):
        if self.ship_type_id:
            self.label.text = evetypes.GetName(self.ship_type_id)
            ship_group_id = evetypes.GetShipGroupID(self.ship_type_id)
            self.ship_group_icon.texturePath = cfg.infoBubbleGroups.get(ship_group_id)['iconSmall']
        else:
            self.label.text = None
            self.ship_group_icon.texturePath = eveicon.spaceship_command

    @property
    def ship_type_id(self):
        return self._ship_type_id

    @ship_type_id.setter
    def ship_type_id(self, value):
        if self._ship_type_id == value:
            return
        self._ship_type_id = value
        self.update()

    def OnClick(self, *args):
        if self.ship_type_id:
            sm.GetService('info').ShowInfo(self.ship_type_id)

    def GetMenu(self):
        if not self.ship_type_id:
            return None
        return GetMenuService().GetMenuFromItemIDTypeID(itemID=None, typeID=self.ship_type_id, includeMarketDetails=True)
