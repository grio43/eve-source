#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\factionSelector.py
from carbonui import Align
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.cardsContainer import CardsContainer
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from characterdata.factions import get_faction_name
from eve.client.script.ui import eveColor
from eve.client.script.ui.cosmetics.ship.pages.studio.studioUtil import get_ship_factions
from eve.client.script.ui.shared.shipTree import shipTreeConst
ICON_SIZE = 48

class FactionSelector(CardsContainer):
    default_contentSpacing = (4, 4)
    default_cardHeight = ICON_SIZE
    default_cardMaxWidth = ICON_SIZE + 16

    def __init__(self, faction_id_setting, **kwargs):
        super(FactionSelector, self).__init__(**kwargs)
        self.buttons = []
        self.faction_id_setting = faction_id_setting
        for faction_id in get_ship_factions():
            button = SelectableButtonIcon(parent=Container(parent=self), align=Align.CENTER, pos=(0,
             0,
             ICON_SIZE,
             ICON_SIZE), texturePath=shipTreeConst.ICON_BY_FACTIONID[faction_id], hint=get_faction_name(faction_id), iconSize=ICON_SIZE, func=self.on_faction_button, args=faction_id)
            self.buttons.append(button)

        self.update_button_selected_state(self.faction_id_setting.get())

    def on_faction_button(self, faction_id):
        if faction_id == self.faction_id_setting.get():
            faction_id = None
        self.set_faction(faction_id)

    def set_faction(self, faction_id):
        self.update_button_selected_state(faction_id)
        if faction_id is None:
            faction_id = shipTreeConst.ANY_FACTION
        self.faction_id_setting.set(faction_id)

    def update_button_selected_state(self, faction_id):
        for button in self.buttons:
            if button.args == faction_id:
                button.ToggleSelected()
            else:
                button.SetDeselected()


class SelectableButtonIcon(ButtonIcon):
    default_iconColor = eveColor.WHITE
    default_useThemeColor = False

    def _GetIconColor(self):
        return eveColor.WHITE

    def ConstructBackground(self):
        self.mouseEnterBG = Frame(name='mouseEnterBG', bgParent=self.bgContainer, texturePath='res:/UI/Texture/classes/ShipTree/InfoPanel/hover.png', opacity=0.0)
        self.mouseDownBG = Sprite(name='mouseDownBG', bgParent=self.bgContainer, texturePath='res:/UI/Texture/classes/ButtonIcon/mouseDown.png', opacity=0.0)
        self.selectedBG = Frame(name='selectedBG', bgParent=self.bgContainer, texturePath='res:/UI/Texture/classes/ShipTree/InfoPanel/selected.png', opacity=0.0)
