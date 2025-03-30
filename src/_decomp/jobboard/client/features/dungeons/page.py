#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\page.py
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

class DungeonPage(JobPage):

    def _construct_subtitle(self, parent_container):
        scan_result_id = self.job.scan_result_id
        if scan_result_id and self.job.in_same_system:
            container = eveui.Container(parent=parent_container, align=eveui.Align.to_top, height=20, padTop=8)
            ScanResult(parent=container, scan_result_id=scan_result_id)

    def _construct_body(self, parent_container):
        self._construct_description(parent_container)
        self._construct_operational_intel(parent_container)
        self._construct_archetype_info(parent_container)

    def _construct_description(self, parent_container):
        description = self.job.description
        if description:
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
        return any([self.job.difficulty, self.job.resources, self.job.enemy])

    def _construct_operational_intel_ship_restrictions(self, operational_intel_container):
        if not self.job.ship_restrictions:
            return
        ShipRestrictions(parent=operational_intel_container, align=eveui.Align.to_top, dungeon_id=self.job.dungeon_id, in_valid_ship=self.job.in_valid_ship, padTop=12 if len(operational_intel_container.children) else 0, padBottom=0)

    def _construct_operational_intel_gameplay_description(self, operational_intel_container):
        if not self.job.gameplay_description:
            return
        carbonui.TextBody(parent=operational_intel_container, align=eveui.Align.to_top, text=self.job.gameplay_description, padTop=12 if len(operational_intel_container.children) else 0)

    def _construct_operational_intel_parameters(self, operational_intel_container):
        if not self._has_operational_intel_parameters():
            return
        if self.job.difficulty or self.job.enemy:
            parameters_container = CardsContainer(name='operational_intel_parameters', parent=operational_intel_container, align=eveui.Align.to_top, autoHeight=False, contentSpacing=(24, 8), cardHeight=55, maxColumnCount=4, allow_stretch=True, padTop=12 if len(operational_intel_container.children) else 0)
            if self.job.difficulty:
                caption = GetByLabel('UI/Agency/ContentDifficulty')
                text = GetByLabel('UI/Agency/LevelX', level=self.job.difficulty)
                hint = GetByLabel('UI/Agency/ContentDifficultyTooltip')
                ParameterContainer(name='operational_intel_parameter_difficulty', parent=parameters_container, caption=caption, text=text, hint=hint or None, icon=eveicon.difficulty)
            if self.job.enemy:
                caption = GetByLabel('UI/Agency/RoamingEnemies')
                text = self.job.enemy_name
                hint = GetByLabel('UI/Agency/RoamingEnemiesTooltip')
                ParameterContainer(name='operational_intel_parameter_enemy', parent=parameters_container, caption=caption, text=text, hint=hint or None, icon=eveicon.pilot_or_organization)
        if self.job.resources:
            caption = GetByLabel('UI/Agency/OreTypesInBelt')
            hint = GetByLabel('UI/Agency/OreTypesInBeltTooltip')
            card_height = 32
            resources_container = eveui.ContainerAutoSize(name='operational_intel_resources', parent=operational_intel_container, align=eveui.Align.to_top, state=uiconst.UI_NORMAL, hint=hint or None, padTop=12 if len(operational_intel_container.children) else 0)
            carbonui.TextBody(parent=resources_container, align=eveui.Align.to_top, text=caption, color=TextColor.SECONDARY, padBottom=4)
            icon_container = eveui.Container(name='operational_intel_resources_icon_container', parent=resources_container, align=eveui.Align.to_top, width=card_height, height=card_height)
            ParameterContainer(name='operational_intel_resources_icon', parent=icon_container, text=None, icon=eveicon.mining, state=uiconst.UI_PICKCHILDREN)
            resource_parameters_container = CardsContainer(name='operational_intel_resource_parameters', parent=resources_container, align=eveui.Align.to_top, autoHeight=True, contentSpacing=(8, 4), cardHeight=card_height, maxColumnCount=4, allow_stretch=True, padLeft=card_height + 4, top=-card_height)
            for order, resource in enumerate(self.job.resources):
                ParameterContainer(name='operational_intel_resource_parameter_{resource}'.format(resource=resource), parent=resource_parameters_container, text=evelink.type_link(resource), icon=None, state=uiconst.UI_PICKCHILDREN)

    def _construct_archetype_info(self, parent_container):
        archetype_title = self.job.archetype_title
        archetype_description = self.job.archetype_description
        if archetype_description and archetype_title:
            archetype_section = DetailsSection(name='details_section_archetype', parent=parent_container, title=archetype_title)
            container = archetype_section.content_container
            carbonui.TextBody(parent=container, align=eveui.Align.to_top, text=archetype_description)


class ScanResult(eveui.ContainerAutoSize):
    default_state = eveui.State.normal
    default_alignMode = eveui.Align.to_left
    default_height = 20

    def __init__(self, scan_result_id, *args, **kwargs):
        super(ScanResult, self).__init__(*args, **kwargs)
        container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_left, alignMode=eveui.Align.to_left, padding=2)
        label_container = eveui.ContainerAutoSize(parent=container, align=eveui.Align.to_left, alignMode=eveui.Align.center_left, padRight=4)
        carbonui.TextBody(parent=label_container, align=eveui.Align.center_left, text=GetByLabel('UI/Common/ID'), padding=4, color=TextColor.SECONDARY)
        value_container = eveui.ContainerAutoSize(parent=container, align=eveui.Align.to_left, alignMode=eveui.Align.center_left)
        carbonui.TextBody(parent=value_container, align=eveui.Align.center_left, text=scan_result_id, padding=4)
        eveui.Frame(bgParent=value_container, opacity=0.2, frameConst=uiconst.FRAME_FILLED_CORNER1)
        eveui.Frame(bgParent=self, color=(0, 0, 0), opacity=0.5, frameConst=uiconst.FRAME_FILLED_CORNER1)
