#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\mercenary_tactical_operations\page.py
import logging
from jobboard.client.ui.pages.details_page import JobPage, DetailsSection
import carbonui
from carbonui import TextColor, uiconst
from carbonui.primitives.cardsContainer import CardsContainer
import eveicon
import evelink.client
import eveui
from eve.common.script.sys import eveCfg
from localization import GetByLabel
from jobboard.client.ui.pages.details_page import JobPage, DetailsSection
from jobboard.client.ui.parameter_container import ParameterContainer
from jobboard.client.features.agent_missions.page import ShipRestrictions
logger = logging.getLogger(__name__)

class MTOPage(JobPage):

    def _construct_body(self, parent_container):
        self._construct_description(parent_container)
        self._construct_operational_intel(parent_container)
        self._construct_archetype_info(parent_container)

    def _construct_description(self, parent_container):
        description = self.job.description
        if description is not None:
            description_section = DetailsSection(name='details_section_description', parent=parent_container, title=GetByLabel('UI/Common/Description'), max_content_height=100)
            container = description_section.content_container
            carbonui.TextBody(parent=container, align=eveui.Align.to_top, text=description)

    def _construct_operational_intel(self, parent_container):
        if not self._has_operational_intel():
            return
        operational_intel = DetailsSection(name='details_section_operational_intel', parent=parent_container, title=GetByLabel('UI/Dungeons/GameplayDescriptionHeader'))
        container = operational_intel.content_container
        self._construct_operational_intel_ship_restrictions(container)
        self._construct_operational_intel_gameplay_description(container)
        self._construct_operational_intel_parameters(container)

    def _has_operational_intel(self):
        return any([self.job.gameplay_description, self.job.ship_restrictions, self._has_operational_intel_parameters()])

    def _has_operational_intel_parameters(self):
        return any([self.job.difficulty, self.job.enemy])

    def _construct_operational_intel_ship_restrictions(self, operational_intel_container):
        if self.job.ship_restrictions is None:
            return
        ShipRestrictions(parent=operational_intel_container, align=eveui.Align.to_top, dungeon_id=self.job.dungeon_id, in_valid_ship=self.job.in_valid_ship, padTop=12 if len(operational_intel_container.children) else 0, padBottom=0)

    def _construct_operational_intel_gameplay_description(self, operational_intel_container):
        if self.job.gameplay_description is None:
            return
        carbonui.TextBody(parent=operational_intel_container, align=eveui.Align.to_top, text=self.job.gameplay_description, padTop=12 if len(operational_intel_container.children) else 0)

    def _construct_operational_intel_parameters(self, operational_intel_container):
        if not self._has_operational_intel_parameters():
            return
        if self.job.difficulty is not None or self.job.enemy is not None:
            parameters_container = CardsContainer(name='operational_intel_parameters', parent=operational_intel_container, align=eveui.Align.to_top, autoHeight=False, contentSpacing=(24, 8), cardHeight=55, maxColumnCount=4, allow_stretch=True, padTop=12 if len(operational_intel_container.children) else 0)
            if self.job.difficulty is not None:
                caption = GetByLabel('UI/Agency/ContentDifficulty')
                text = GetByLabel('UI/Agency/LevelX', level=self.job.difficulty)
                hint = GetByLabel('UI/Agency/ContentDifficultyTooltip')
                ParameterContainer(name='operational_intel_parameter_difficulty', parent=parameters_container, caption=caption, text=text, hint=hint or None, icon=eveicon.difficulty)
            if self.job.enemy is not None:
                caption = GetByLabel('UI/Agency/RoamingEnemies')
                text = self.job.enemy_name
                hint = GetByLabel('UI/Agency/RoamingEnemiesTooltip')
                ParameterContainer(name='operational_intel_parameter_enemy', parent=parameters_container, caption=caption, text=text, hint=hint or None, icon=eveicon.pilot_or_organization)
            if self.job.subtitle is not None:
                caption = GetByLabel('UI/Agency/MercDen/Status')
                text = GetByLabel('UI/Agency/MercDen/ReadyToStart')
                if self.job.is_activity_started:
                    text = GetByLabel('UI/Agency/MercDen/InProgress')
                hint = GetByLabel('UI/Agency/MercDen/StatusTooltip')
                ParameterContainer(name='operational_intel_parameter_difficulty', parent=parameters_container, caption=caption, text=text, hint=hint or None, icon=None)
        caption = GetByLabel('UI/Agency/MercDen/JobDetailHeader')
        card_height = 32
        resources_container = eveui.ContainerAutoSize(name='operational_intel_other', parent=operational_intel_container, align=eveui.Align.to_top, state=uiconst.UI_NORMAL, hint=hint or None, padTop=12 if len(operational_intel_container.children) else 0)
        carbonui.TextBody(parent=resources_container, align=eveui.Align.to_top, text=caption, color=TextColor.SECONDARY, padBottom=4)
        resource_parameters_container = CardsContainer(name='operational_intel_mercenary_den', parent=resources_container, align=eveui.Align.to_top, autoHeight=True, contentSpacing=(8, 4), cardHeight=card_height, maxColumnCount=4, allow_stretch=True, padLeft=0, top=0)
        solar_system_id = self.job.solar_system_id
        location_info = sm.GetService('map').GetItem(solar_system_id)
        text = evelink.location_link(solar_system_id, location_info.itemName)
        ParameterContainer(name='operational_intel_mercenary_den_location', parent=resource_parameters_container, text=text, icon=eveicon.solar_system, state=uiconst.UI_PICKCHILDREN)
        ParameterContainer(name='operational_intel_mercenary_den_development', parent=resource_parameters_container, text=GetByLabel('UI/Sovereignty/MercenaryDen/DevelopmentImpact', impact=self.job.development_impact), icon=None, state=uiconst.UI_PICKCHILDREN)
        ParameterContainer(name='operational_intel_mercenary_den_anarchy', parent=resource_parameters_container, text=GetByLabel('UI/Sovereignty/MercenaryDen/AnarchyImpact', impact=self.job.anarchy_impact), icon=None, state=uiconst.UI_PICKCHILDREN)
        ParameterContainer(name='operational_intel _mercenary_den_infomorphs', parent=resource_parameters_container, text=GetByLabel('UI/Sovereignty/MercenaryDen/InfomorphBonus', bonus=self.job.infomorph_bonus), icon=None, state=uiconst.UI_PICKCHILDREN)

    def _construct_archetype_info(self, parent_container):
        archetype_title = self.job.archetype_title
        archetype_description = self.job.archetype_description
        if archetype_description and archetype_title:
            archetype_section = DetailsSection(name='details_section_archetype', parent=parent_container, title=archetype_title)
            container = archetype_section.content_container
            carbonui.TextBody(parent=container, align=eveui.Align.to_top, text=archetype_description)
