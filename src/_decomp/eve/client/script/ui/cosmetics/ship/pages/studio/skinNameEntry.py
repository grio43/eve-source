#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\skinNameEntry.py
import eveicon
from carbonui import Align, TextAlign, TextBody, TextColor, TextHeadline, uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from cosmetics.client.ships.skins.live_data import current_skin_design, current_skin_design_signals
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals
from eve.client.script.ui.cosmetics.ship.pages.studio.skinNameDialogue import RenameSkinDialogue
from localization import GetByLabel

class SkinNameEntry(ContainerAutoSize):
    default_align = Align.CENTER
    default_state = uiconst.UI_NORMAL
    default_width = 396

    def __init__(self, *args, **kwargs):
        super(SkinNameEntry, self).__init__(*args, **kwargs)
        self._radius = 0.0
        self.construct_layout()
        self.connect_signals()
        self.update_text()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(SkinNameEntry, self).Close()

    def connect_signals(self):
        current_skin_design_signals.on_design_reset.connect(self.update)
        current_skin_design_signals.on_existing_design_loaded.connect(self.update)
        current_skin_design_signals.on_name_changed.connect(self.update)
        current_skin_design_signals.on_line_name_changed.connect(self.update)
        current_skin_design_signals.on_ship_type_id_changed.connect(self.update)
        current_skin_design_signals.on_slot_fitting_changed.connect(self.update)
        current_skin_design_signals.on_snapshot_changed.connect(self.update)
        studioSignals.on_scene_zoom.connect(self.on_scene_zoom)

    def disconnect_signals(self):
        current_skin_design_signals.on_design_reset.disconnect(self.update)
        current_skin_design_signals.on_existing_design_loaded.disconnect(self.update)
        current_skin_design_signals.on_name_changed.disconnect(self.update)
        current_skin_design_signals.on_line_name_changed.disconnect(self.update)
        current_skin_design_signals.on_ship_type_id_changed.disconnect(self.update)
        current_skin_design_signals.on_slot_fitting_changed.disconnect(self.update)
        current_skin_design_signals.on_snapshot_changed.disconnect(self.update)
        studioSignals.on_scene_zoom.disconnect(self.on_scene_zoom)

    def construct_layout(self):
        self.skin_name_container = Container(name='name_container', parent=self, align=Align.TOTOP, height=30)
        self.skin_name_label = TextHeadline(name='skin_name_label', parent=self.skin_name_container, align=Align.CENTER)
        self.icon_container = Container(name='icon_container', parent=self.skin_name_container, align=Align.CENTER, width=16, height=30, opacity=0.0)
        self.edit_icon = Sprite(name='edit_icon', parent=self.icon_container, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath=eveicon.edit, width=16, height=16)
        self.skin_line_label = TextBody(name='skin_line_label', parent=self, align=Align.TOTOP, textAlign=TextAlign.CENTER)
        self.skin_edit_container = Container(name='skin_edit_container', parent=self, align=Align.TOTOP, height=30)
        hint_text = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/SKINName')
        text_width, _ = TextHeadline.MeasureTextSize(hint_text)
        self.skin_edit_label = SkinNameEditText(name='skin_name_edit', parent=self.skin_edit_container, hintText=hint_text, width=text_width + 40)
        self.update_text()

    def update(self, *args):
        self.update_text()

    def update_text(self):
        name_text = current_skin_design.get().name
        has_name = bool(name_text)
        self.skin_name_container.display = has_name
        self.skin_line_label.display = has_name
        self.skin_edit_container.display = not has_name
        if has_name:
            design_has_changes = current_skin_design.has_changes_from_snapshot()
            self.skin_name_label.text = u'{name} *'.format(name=name_text) if design_has_changes else name_text
            self.skin_line_label.text = current_skin_design.get().line_name
            self.icon_container.left = -self.skin_name_label.width * 0.5 + -self.icon_container.width * 0.5 - 8

    def on_scene_zoom(self, is_zoomed):
        target_opacity = 0.0 if is_zoomed else 1.0
        animations.FadeTo(self, self.opacity, target_opacity, duration=0.15)

    def update_radial_position(self):
        self.top = self._radius * 0.75 - self.height

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
        self.update_radial_position()

    def OnMouseEnter(self, *args):
        animations.FadeTo(self.icon_container, self.icon_container.opacity, 1.0, 0.25)

    def OnMouseExit(self, *args):
        animations.FadeTo(self.icon_container, self.icon_container.opacity, 0.0, 0.25)

    def OnClick(self, *args):
        if current_skin_design.get().name:
            name = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/RenameDesign')
        else:
            name = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/SKINName')
        dialogue = RenameSkinDialogue(window_name=name)
        dialogue.ShowModal()

    @property
    def hint(self):
        if current_skin_design.get().name:
            return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/RenameDesign')
        else:
            return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/NameDesign')


class SkinNameEditText(SingleLineEditText):
    default_align = Align.CENTER
    default_state = uiconst.UI_DISABLED
    default_icon = eveicon.edit

    def ConstructLabels(self):
        self.textLabel = TextHeadline(name='textLabel', parent=self._textClipperInner, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=self.textLeftMargin, text='', maxLines=1)
        self.hintLabel = TextHeadline(name='hintTextLabel', parent=self._textClipperInner, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=self.textLeftMargin, text='', maxLines=1, color=TextColor.SECONDARY)
