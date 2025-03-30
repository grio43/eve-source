#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\agent_missions\card.py
from jobboard.client.ui.card import JobCard
from carbonui import Align
import trinity
import eveui
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.infoIcon import ExclamationMarkGlyphIcon
import localization
from jobboard.client.ui.time_remaining import TimeRemainingIcon

class AgentMissionCard(JobCard):
    AGENT_PORTRAIT_SIZE = 40
    AGENT_CONTAINER_SIZE = AGENT_PORTRAIT_SIZE + 8
    STATUS_ICON_SIZE = 16

    def _update_state(self):
        self._update_top_title()
        state_info = self.job.get_state_info()
        if not state_info:
            self._left_line.rgb = eveThemeColor.THEME_FOCUS[:3]
            self._state_container.display = False
            return
        self._left_line.rgb = state_info['color'][:3]
        self._state_icon.texturePath = state_info['icon']
        self._state_icon.color = state_info['color']
        self._state_icon.hint = state_info['text']
        self._state_container.display = True

    def _construct_top_right(self):
        self._construct_state_container(self._top_right_container)
        self._construct_agent_portrait(self._top_right_container)

    def _construct_state_container(self, container_parent):
        self._state_container = eveui.Container(parent=container_parent, align=Align.CENTER, width=self.AGENT_CONTAINER_SIZE, height=self.AGENT_CONTAINER_SIZE)
        icon_container = eveui.ContainerAutoSize(parent=self._state_container, state=eveui.State.normal, align=Align.BOTTOMRIGHT)
        self._state_icon = eveui.Sprite(name='state_icon', parent=icon_container, state=eveui.State.normal, align=Align.CENTER, width=self.STATUS_ICON_SIZE, height=self.STATUS_ICON_SIZE, opacity=0.8)
        eveui.Sprite(parent=icon_container, align=Align.CENTER, width=self.STATUS_ICON_SIZE + 4, height=self.STATUS_ICON_SIZE + 4, texturePath='res:/UI/Texture/circle_full.png', color=eveColor.BLACK, opacity=0.6)

    def _construct_agent_portrait(self, container_parent):
        self.agent_portrait = eveui.CharacterPortrait(parent=container_parent, align=Align.CENTER, size=self.AGENT_PORTRAIT_SIZE, character_id=self.job.agent_id, textureSecondaryPath='res:/UI/Texture/circle_full.png', spriteEffect=trinity.TR2_SFX_MODULATE)
        eveui.Sprite(parent=container_parent, align=Align.CENTER, width=self.AGENT_CONTAINER_SIZE, height=self.AGENT_CONTAINER_SIZE, texturePath='res:/UI/Texture/circle_full.png', color=eveColor.BLACK, opacity=0.2)
        self.agent_portrait.OnClick = self.OnClick
        self.agent_portrait.GetMenu = self.GetMenu
        self.agent_portrait.GetDragData = self.GetDragData
        self.agent_portrait.PrepareDrag = self.PrepareDrag

    def _construct_attention_icons(self, parent):
        super(AgentMissionCard, self)._construct_attention_icons(parent)
        self._construct_time_remaining(parent)
        self._construct_important_mission(parent)

    def _construct_time_remaining(self, parent):
        if not self.job.has_expiration_time():
            return
        time_remaining_icon = TimeRemainingIcon(parent=parent, job=self.job, padLeft=4, get_text=self.job.get_expiration_text)
        time_remaining_icon.OnClick = self.OnClick
        time_remaining_icon.GetMenu = self.GetMenu
        time_remaining_icon.GetDragData = self.GetDragData
        time_remaining_icon.PrepareDrag = self.PrepareDrag

    def _construct_important_mission(self, parent):
        if not self.job.is_important_mission:
            return
        container = eveui.ContainerAutoSize(parent=parent, align=eveui.Align.to_right, state=eveui.State.normal, padLeft=4, hint=localization.GetByLabel('UI/Agents/StandardMission/ImportantStandingsWarning'))
        container.OnClick = self.OnClick
        container.GetMenu = self.GetMenu
        container.GetDragData = self.GetDragData
        container.PrepareDrag = self.PrepareDrag
        ExclamationMarkGlyphIcon(parent=container, state=eveui.State.disabled, align=eveui.Align.center, width=16, height=16)
