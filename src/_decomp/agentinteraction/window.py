#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agentinteraction\window.py
from agentinteraction.npccharacterview import NpcCharacterView
from agentinteraction.npcinteractionview import NpcInteractionView
from carbonui import uiconst
from carbonui.control.window import Window
from characterdata.npccharacter import NpcCharacter
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
CHARACTER_PANEL_WIDTH = 0.4

class NpcCharacterInteractionWindow(Window):
    __guid__ = 'NpcCharacterInteractionWindow'
    default_windowID = 'NpcCharacterInteractionWindow'
    default_width = 1000
    default_height = 700
    default_minSize = (700, 500)
    default_isLockable = False
    default_isOverlayable = False
    default_isCollapseable = False
    default_extend_content_into_header = True
    default_apply_content_padding = False
    hasWindowIcon = False
    character_view_class = NpcCharacterView
    interaction_view_class = NpcInteractionView

    def ApplyAttributes(self, attributes):
        self.npc_character_id = attributes.npcCharacterID
        self.npc_character = NpcCharacter(self.npc_character_id)
        super(NpcCharacterInteractionWindow, self).ApplyAttributes(attributes)
        self._build_ui()
        self.on_content_padding_changed.connect(self._on_content_padding_changed)
        self.on_header_height_changed.connect(self._on_header_height_changed)

    def _build_ui(self):
        self._build_loading_wheel()
        self._build_npc_character_panel()
        self._build_interaction_panel()
        self._update_sizes()

    def _build_loading_wheel(self):
        self.loading_wheel = LoadingWheel(parent=self.content, align=uiconst.BOTTOMLEFT, state=uiconst.UI_HIDDEN, left=-8, top=-8, idx=0)

    def _build_npc_character_panel(self):
        self.container_npc_character = self.character_view_class(name='container_npc_character', parent=self.content, align=uiconst.TOLEFT_PROP, width=CHARACTER_PANEL_WIDTH, npc_character=self.npc_character, inner_padding=self._get_container_npc_character_inner_padding(), idx=0)

    def _on_content_padding_changed(self, window):
        self._update_container_npc_character_inner_padding()
        self._update_container_interaction_inner_padding()

    def _on_header_height_changed(self, window):
        self._update_container_interaction_inner_padding()

    def _get_container_npc_character_inner_padding(self):
        pad_left, pad_top, pad_right, pad_bottom = self.content_padding
        return (pad_left,
         pad_top,
         0,
         pad_bottom)

    def _update_container_npc_character_inner_padding(self):
        if self.container_npc_character:
            self.container_npc_character.inner_padding = self._get_container_npc_character_inner_padding()

    def _build_interaction_panel(self):
        self.container_interaction = self.interaction_view_class(name='container_interaction', parent=self.content, align=uiconst.TOALL, npc_character=self.npc_character, inner_padding=self._get_container_interaction_inner_padding())

    def _get_container_interaction_inner_padding(self):
        pad_left, pad_top, pad_right, pad_bottom = self.content_padding
        return (pad_right,
         self.header.height,
         pad_right,
         pad_bottom)

    def _update_container_interaction_inner_padding(self):
        if self.container_interaction:
            self.container_interaction.inner_padding = self._get_container_interaction_inner_padding()

    def disable_buttons(self):
        self.container_interaction.disable_buttons()

    def enable_buttons(self):
        self.container_interaction.enable_buttons()

    def _update_sizes(self):
        pass

    def OnResize_(self, *args, **kwargs):
        self._update_sizes()
