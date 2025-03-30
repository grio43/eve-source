#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\controls\characterInfo.py
from carbonui import Align, TextColor, TextDetail, TextHeader, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.ships.skins.live_data import current_skin_design, current_skin_design_signals
from eve.client.script.ui import eveColor
from eve.client.script.ui.cosmetics.ship import charUtil
from eveui import CharacterPortrait
from localization import GetByLabel

class CharacterInfo(Container):
    default_display = False
    default_width = 200
    default_height = 64

    def __init__(self, *args, **kwargs):
        super(CharacterInfo, self).__init__(*args, **kwargs)
        self._character_id = None
        self._compact_mode = False
        self.construct_layout()

    def construct_layout(self):
        icon_container = Container(name='icon_container', parent=self, align=Align.TOLEFT, pos=(0, 0, 64, 64))
        Sprite(name='ring', parent=icon_container, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/circle_frame.png', color=eveColor.GUNMETAL_GREY, pos=(0, 0, 64, 64))
        self.icon = CharacterInfoPortrait(name='icon', parent=icon_container, align=Align.CENTER, textureSecondaryPath='res:/UI/Texture/circle_full.png', spriteEffect=uiconst.SpriteEffect.MODULATE, pos=(0, 0, 64, 64))
        self.text_container = ContainerAutoSize(name='text_container', parent=self, align=Align.CENTERLEFT, width=128, left=72, padTop=16)
        self.description_label = TextDetail(name='description_label', parent=self.text_container, align=Align.TOTOP, top=-16, text=self.description_text, color=TextColor.SECONDARY)
        self.name_label = TextHeader(name='name_label', parent=self.text_container, align=Align.TOTOP, state=uiconst.UI_NORMAL, maxLines=3, autoFadeSides=16, bold=True)

    def update_icon(self):
        if self.character_id:
            self.icon.character_id = self.character_id

    def update_name(self):
        if self.character_id:
            self.name_label.text = charUtil.get_name_link(self.character_id)

    def update_compact_mode(self):
        self.text_container.display = not self.compact_mode
        self.width = 64 if self.compact_mode else self.default_width
        self.icon.description = self.description_text if self.compact_mode else None

    @property
    def description_text(self):
        return None

    @property
    def character_id(self):
        return self._character_id

    @character_id.setter
    def character_id(self, value):
        if self._character_id == value:
            return
        self._character_id = value
        self.display = value is not None
        self.update_icon()
        self.update_name()

    @property
    def compact_mode(self):
        return self._compact_mode

    @compact_mode.setter
    def compact_mode(self, value):
        if self._compact_mode == value:
            return
        self._compact_mode = value
        self.update_compact_mode()


class MadeByCharacterInfo(CharacterInfo):

    @property
    def description_text(self):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/MadeBy')


class ListedByCharacterInfo(CharacterInfo):

    @property
    def description_text(self):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/ListedBy')


class TargetedAtCharacterInfo(CharacterInfo):

    @property
    def description_text(self):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/TargetedAt')


class DesignOwnerCharacterInfo(CharacterInfo):

    def __init__(self, *args, **kwargs):
        self._has_changes = False
        super(DesignOwnerCharacterInfo, self).__init__(*args, **kwargs)
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(DesignOwnerCharacterInfo, self).Close()

    def connect_signals(self):
        current_skin_design_signals.on_name_changed.connect(self.update)
        current_skin_design_signals.on_line_name_changed.connect(self.update)
        current_skin_design_signals.on_ship_type_id_changed.connect(self.update)
        current_skin_design_signals.on_slot_fitting_changed.connect(self.update)
        current_skin_design_signals.on_snapshot_changed.connect(self.update)
        ship_skin_signals.on_skin_design_saved.connect(self.update)

    def disconnect_signals(self):
        current_skin_design_signals.on_name_changed.disconnect(self.update)
        current_skin_design_signals.on_line_name_changed.disconnect(self.update)
        current_skin_design_signals.on_ship_type_id_changed.disconnect(self.update)
        current_skin_design_signals.on_slot_fitting_changed.disconnect(self.update)
        current_skin_design_signals.on_snapshot_changed.disconnect(self.update)
        ship_skin_signals.on_skin_design_saved.disconnect(self.update)

    @property
    def description_text(self):
        if self._has_changes:
            return GetByLabel('UI/Personalization/ShipSkins/SKINR/BasedOnDesignBy')
        else:
            return GetByLabel('UI/Personalization/ShipSkins/SKINR/DesignedBy')

    def update(self, *args):
        if current_skin_design.get().creator_character_id == session.charid:
            self.display = False
        else:
            self._has_changes = current_skin_design.has_changes_from_snapshot()
            self.description_label.text = self.description_text
            self.display = True


class CharacterInfoPortrait(CharacterPortrait):

    def __init__(self, size = 64, character_id = None, **kwargs):
        kwargs.setdefault('height', size)
        kwargs.setdefault('width', size)
        super(CharacterInfoPortrait, self).__init__(**kwargs)
        self._character_id = None
        self._description = None
        self.character_id = character_id

    def _update_hint(self):
        if self.character_id is None:
            self.SetHint(None)
            return
        character_info = cfg.eveowners.Get(self._character_id)
        if self.description:
            self.SetHint(u'%s\n%s' % (self.description, character_info.name))
        else:
            self.SetHint(character_info.name)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if self._description == value:
            return
        self._description = value
        self._update_hint()
