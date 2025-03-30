#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\agent_missions\page.py
import carbonui
from carbonui.primitives.cardsContainer import CardsContainer
import eveui
import localization
import trinity
from evelink.client import character_link, corporation_link
from agentinteraction.objectivesview import ObjectivesView
from agentinteraction.rewardsview import RewardsView
from agentinteraction.warningpanel import CollateralPanel, GrantedItemsPanel, ShipRequirementsPanel
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.control.infoIcon import InfoGlyphIcon
from eve.client.script.ui.station.agents.agentUtil import GetMissionExpirationText
from eve.client.script.ui.control.infoIcon import ExclamationMarkGlyphIcon
from eve.client.script.ui import eveColor
from npcs.divisions import get_division_name
from jobboard.client.ui.pages.details_page import JobPage, DetailsSection
from jobboard.client.ui.time_remaining import TimeRemaining

class AgentMissionPage(JobPage):

    def _update(self):
        if self.job.is_dirty:
            self.job.update_objective_info()
        self._body_container.Flush()
        self._construct_body(self._body_container)
        self._update_state()

    def _construct_body(self, parent_container):
        if self.job.has_expiration_time():
            TimeRemaining(parent=parent_container, align=eveui.Align.to_top, padTop=12, padBottom=12, job=self.job, get_text=self.job.get_expiration_text)
        if self.job.is_important_mission:
            important_container = eveui.ContainerAutoSize(parent=parent_container, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, padBottom=12)
            important_icon_container = eveui.Container(parent=important_container, align=eveui.Align.to_left, width=16, padRight=8)
            ExclamationMarkGlyphIcon(parent=important_icon_container, state=eveui.State.disabled, align=eveui.Align.center_left, width=16, height=16)
            carbonui.TextBody(parent=important_container, align=eveui.Align.to_top, text=localization.GetByLabel('UI/Agents/StandardMission/ImportantStandingsWarning'))
        self._construct_agent_section(parent_container)
        description = self.job.description
        if description:
            description_card = DetailsSection(parent=parent_container, title=localization.GetByLabel('UI/Agents/StandardMission/MissionBriefing'), max_content_height=100)
            carbonui.TextBody(parent=description_card.content_container, state=eveui.State.normal, align=eveui.Align.to_top, text=description)
        objectives = self.job.objectives
        if objectives:
            objectives_container = DetailsSection(parent=parent_container, title=localization.GetByLabel('UI/Agents/StandardMission/Objectives'))
            Objectives(parent=objectives_container.content_container, align=eveui.Align.to_top, objectives=objectives, objectives_type=self.job.objectives_type)
        in_valid_ship = self.job.in_valid_ship
        if not in_valid_ship:
            ShipRestrictions(parent=parent_container, align=eveui.Align.to_top, dungeon_id=self.job.dungeon_id, in_valid_ship=in_valid_ship, ship_window_header=self.job.title)
        collateral = self.job.collateral
        if collateral and self.job.is_offered:
            Collateral(parent=parent_container, align=eveui.Align.to_top, collateral=collateral)
        granted_items = self.job.granted_items
        if granted_items:
            GrantedItems(parent=parent_container, align=eveui.Align.to_top, granted_items=granted_items)
        rewards = self.job.rewards
        if rewards:
            Rewards(parent=parent_container, align=eveui.Align.to_top, rewards=rewards, bonus_rewards=self.job.bonus_rewards)
        extra_information = self.job.extra_information
        if extra_information:
            extra_information_card = DetailsSection(parent=parent_container, title=extra_information[0])
            carbonui.TextBody(parent=extra_information_card.content_container, align=eveui.Align.to_top, text=extra_information[1])

    def _construct_agent_section(self, parent_container):
        container = CardsContainer(parent=parent_container, align=eveui.Align.to_top, cardHeight=64, cardMaxWidth=500, contentSpacing=(16, 16), padTop=12, padBottom=12)
        agent_container = eveui.Container(parent=container, align=eveui.Align.to_all)
        corporation_container = eveui.Container(parent=container, align=eveui.Align.to_all)
        self._construct_agent(agent_container)
        self._construct_corporation(corporation_container)

    def _construct_agent(self, parent_container):
        portrait_container = eveui.Container(parent=parent_container, align=eveui.Align.to_left, width=72, height=72, padRight=16)
        eveui.CharacterPortrait(parent=portrait_container, align=eveui.Align.center, size=64, character_id=self.job.agent_id, textureSecondaryPath='res:/UI/Texture/circle_full.png', spriteEffect=trinity.TR2_SFX_MODULATE)
        eveui.Sprite(parent=portrait_container, align=eveui.Align.center, width=72, height=72, texturePath='res:/UI/Texture/circle_full.png', color=eveColor.BLACK, opacity=0.2)
        text_container = eveui.ContainerAutoSize(parent=parent_container, align=carbonui.Align.VERTICALLY_CENTERED)
        carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, text=localization.GetByLabel('UI/Agents/AgentEntry/Level', level=self.job.agent_level))
        carbonui.TextBody(parent=text_container, state=eveui.State.normal, align=eveui.Align.to_top, text=character_link(self.job.agent_id))
        carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, text=get_division_name(self.job.agent_division_id), color=carbonui.TextColor.SECONDARY)

    def _construct_corporation(self, parent_container):
        corporation_id = self.job.agent_corporation_id
        portrait_container = eveui.Container(parent=parent_container, align=eveui.Align.to_left, width=72, height=72, padRight=16)
        OwnerIcon(parent=portrait_container, state=eveui.State.normal, align=eveui.Align.center, width=64, height=64, ownerID=corporation_id)
        text_container = eveui.ContainerAutoSize(parent=parent_container, align=carbonui.Align.VERTICALLY_CENTERED)
        value, label = sm.GetService('standing').GetEffectiveStandingWithAgent(self.job.agent_id)
        carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, text=label)
        carbonui.TextBody(parent=text_container, state=eveui.State.normal, align=eveui.Align.to_top, text=corporation_link(corporation_id))
        carbonui.TextBody(parent=text_container, align=eveui.Align.to_top, text=cfg.eveowners.Get(self.job.agent_faction_id).name, color=carbonui.TextColor.SECONDARY)


class Objectives(ObjectivesView):

    def __init__(self, objectives, objectives_type, *args, **kwargs):
        super(Objectives, self).__init__(*args, **kwargs)
        self.update_objectives(objectives, objectives_type)

    def _build_title(self):
        pass


class Rewards(RewardsView):
    default_padTop = 12
    default_padBottom = 12

    def __init__(self, rewards, bonus_rewards, *args, **kwargs):
        super(Rewards, self).__init__(*args, **kwargs)
        self.title_color = carbonui.TextColor.SECONDARY
        self.update_normal_rewards(rewards)
        self.update_bonus_rewards(bonus_rewards)


class GrantedItems(GrantedItemsPanel):
    default_align = eveui.Align.to_top
    default_padTop = 12
    default_padBottom = 12

    def __init__(self, granted_items, *args, **kwargs):
        super(GrantedItems, self).__init__(*args, **kwargs)
        self.update_items(granted_items)


class Collateral(CollateralPanel):
    default_align = eveui.Align.to_top
    default_padTop = 12
    default_padBottom = 12

    def __init__(self, collateral, *args, **kwargs):
        super(Collateral, self).__init__(*args, **kwargs)
        self.update_items(collateral)


class ShipRestrictions(ShipRequirementsPanel):
    default_align = eveui.Align.to_top
    default_padTop = 12
    default_padBottom = 12
