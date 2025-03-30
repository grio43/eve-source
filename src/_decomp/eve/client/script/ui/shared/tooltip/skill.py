#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\tooltip\skill.py
import characterskills.client
import clonegrade
import expertSystems.client
import localization
from carbonui import uiconst
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel, primaryButton
from carbonui.control.button import Button
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.shared.neocom import skillConst
from eve.client.script.ui.shared.tooltip.skillTooltipController import SkillTooltipController, SkillPrimaryActionController
from localization.formatters.timeIntervalFormatters import TIME_CATEGORY_DAY, TIME_CATEGORY_MINUTE, FormatTimeIntervalShortWritten
TOOLTIP_WIDTH_DEFAULT = 280

def LoadSkillEntryTooltip(panel, skillID, skillLevel = None):
    skill = SkillTooltipController(skillID)
    load_skill_tooltip(panel, skill, skillLevel)


def LoadSkillEntryTooltipInfoOnly(panel, skillID):
    skill = SkillTooltipController(skillID)
    load_skill_tooltip_information(panel, skill)


def load_skill_tooltip(panel, skill, skillLevel = None):
    _init_panel(panel)
    panel.AddSpacer(height=8, width=TOOLTIP_WIDTH_DEFAULT, colSpan=panel.columns)
    _add_information(panel, skill, skillLevel)
    _add_actions(panel, skill, skillLevel)
    panel.AddSpacer(height=8, width=TOOLTIP_WIDTH_DEFAULT, colSpan=panel.columns)


def load_skill_tooltip_information(panel, skill):
    _init_panel(panel)
    panel.AddSpacer(height=8, width=TOOLTIP_WIDTH_DEFAULT, colSpan=panel.columns)
    _add_information(panel, skill)
    panel.AddSpacer(height=8, width=TOOLTIP_WIDTH_DEFAULT, colSpan=panel.columns)


def load_skill_tooltip_actions(panel, skill, skillLevel = None):
    _init_panel(panel)
    panel.AddSpacer(height=8, width=TOOLTIP_WIDTH_DEFAULT, colSpan=panel.columns)
    _add_actions(panel, skill, skillLevel)
    panel.AddSpacer(height=8, width=TOOLTIP_WIDTH_DEFAULT, colSpan=panel.columns)


def _init_panel(panel):
    panel.Flush()
    panel.LoadGeneric2ColumnTemplate()
    panel.margin = 0
    panel.state = uiconst.UI_NORMAL


def _add_information(panel, skill, skillLevel = None):
    add_description(panel, skill)
    add_level_and_points(panel, skill)
    if should_add_expert_system_notification(skill):
        add_expert_system_information(panel, skill)
    if should_add_training_queue_info(skill):
        add_queued_training_info(panel, skill)
    elif skillLevel and should_add_training_info(skill, skillLevel):
        add_training_info(panel, skill, skillLevel)


def _add_actions(panel, skill, skillLevel):
    spacer_height = 8
    if should_add_requirements_action(skill):
        panel.AddSpacer(height=spacer_height, colSpan=panel.columns)
        spacer_height = 2
        add_requirements_action(panel, skill)
    if should_add_buy_skill_action(skill):
        panel.AddSpacer(height=spacer_height, colSpan=panel.columns)
        spacer_height = 2
        add_buy_skill_action(panel, skill)
    if should_add_omega_info(skill):
        panel.AddSpacer(height=spacer_height, colSpan=panel.columns)
        add_omega_info(panel, skill)
    if should_add_primary_action(skill, skillLevel):
        add_primary_action(panel, skill, skillLevel)


def should_add_training_queue_info(skill):
    return skill.is_queued


def should_add_training_info(skill, skillLevel):
    return skill.could_be_trained(skillLevel)


def should_add_requirements_action(skill):
    return not skill.is_grandfathered and skill.untrained_requirements


def should_add_buy_skill_action(skill):
    return not skill.is_injected and not skill.is_next_level_omega_restricted


def should_add_omega_info(skill):
    return skill.is_omega_restricted


def should_add_primary_action(skill, skillLevel):
    if skillLevel is None:
        skillLevel = 5
    return skill.level_including_queued < skillLevel or should_add_omega_info(skill)


def should_add_expert_system_notification(skill):
    if skill.virtual_level and expertSystems.is_expert_systems_enabled():
        return True
    else:
        return False


def add_description(panel, skill):
    grid = LayoutGrid(columns=2)
    grid.AddCell(cellPadding=(TOOLTIP_WIDTH_DEFAULT - 24,
     0,
     0,
     0), colSpan=2)
    grid.AddCell(eveLabel.EveLabelMedium(align=uiconst.TOPLEFT, text=skill.description, width=TOOLTIP_WIDTH_DEFAULT - 24 - 12), cellPadding=(0, 0, 0, 0))
    grid.AddCell(InfoIcon(align=uiconst.TOPRIGHT, typeID=skill.type_id, hint=localization.GetByLabel('UI/Commands/ShowInfo')), cellPadding=(0, 0, 0, 0))
    panel.AddCell(grid, cellPadding=(12, 0, 8, 0), colSpan=panel.columns)


def add_level_and_points(panel, skill):
    panel.AddCell(eveLabel.EveLabelMedium(text=characterskills.client.get_skill_level_text(skill.level)), cellPadding=(12, 8, 0, 0))
    panel.AddCell(eveLabel.EveLabelMedium(align=uiconst.TOPRIGHT, text=characterskills.client.get_skill_points_text(skill.points, skill.rank)), cellPadding=(0, 8, 12, 0))


def add_training_info(panel, skill, skillLevel):
    grid = LayoutGrid(align=uiconst.TOTOP, columns=2)
    grid.AddCell(cellPadding=(TOOLTIP_WIDTH_DEFAULT - 24,
     0,
     0,
     0), colSpan=2)
    grid.AddCell(eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Skills/TimeToTrain'), align=uiconst.TOTOP), cellPadding=(0, 2, 0, 0))
    grid.AddCell(eveLabel.EveLabelMedium(align=uiconst.TOPRIGHT, text=FormatTimeIntervalShortWritten(skill.get_training_time_to_level(skillLevel), showTo=TIME_CATEGORY_MINUTE)), cellPadding=(0, 2, 0, 0))
    panel.AddCell(grid, cellPadding=(12, 8, 12, 0), colSpan=panel.columns)


def add_queued_training_info(panel, skill):
    grid = LayoutGrid(align=uiconst.TOTOP, columns=2)
    grid.AddCell(cellPadding=(TOOLTIP_WIDTH_DEFAULT - 24,
     0,
     0,
     0), colSpan=2)
    grid.AddCell(eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Skills/TrainingToLevel', level=skill.level_including_queued), color=skillConst.COLOR_SKILL_1, align=uiconst.TOTOP), colSpan=2)
    grid.AddCell(eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Skills/TimeUntilTrained'), align=uiconst.TOTOP), cellPadding=(0, 2, 0, 0))
    grid.AddCell(eveLabel.EveLabelMedium(align=uiconst.TOPRIGHT, text=FormatTimeIntervalShortWritten(skill.get_time_until_trained(), showFrom=TIME_CATEGORY_DAY, showTo=TIME_CATEGORY_MINUTE)), cellPadding=(0, 2, 0, 0))
    panel.AddCell(grid, cellPadding=(12, 8, 12, 0), colSpan=panel.columns)
    grid = LayoutGrid(align=uiconst.TOTOP, columns=2)
    grid.AddCell(cellPadding=(TOOLTIP_WIDTH_DEFAULT - 24,
     0,
     0,
     0), colSpan=2)
    grid.AddCell(eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/TrainingRate')))
    grid.AddCell(eveLabel.EveLabelMedium(align=uiconst.TOPRIGHT, text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SpPerMinute', spPerMin=skill.training_rate)))
    panel.AddCell(grid, cellPadding=(12, 2, 12, 0), colSpan=panel.columns)


def add_requirements_action(panel, skill):
    grid = LayoutGrid(columns=2)
    grid.AddCell(cellPadding=(TOOLTIP_WIDTH_DEFAULT,
     8,
     0,
     0), colSpan=2)
    add_background_gradient(grid, skillConst.COLOR_SKILL_1)
    grid.AddCell(eveLabel.EveLabelMedium(align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/Skills/UntrainedRequirements'), width=TOOLTIP_WIDTH_DEFAULT - 22), colSpan=2, cellPadding=(11, 0, 11, 0))
    grid.AddCell(eveLabel.EveLabelMedium(align=uiconst.TOTOP, text=localization.GetByLabel('UI/Skills/TotalTrainingTimeField', color=Color(1.0, 1.0, 1.0, 0.5).GetHex(), time=skill.requirements_training_time)), colSpan=2, cellPadding=(11, 8, 0, 8))
    grid.AddCell(Button(align=uiconst.CENTERRIGHT, label=localization.GetByLabel('UI/Skills/ViewRequiredSkills'), func=skill.view_requirements, args=(), fixedheight=24), cellPadding=(11, 8, 11, 8))
    panel.AddCell(grid, cellPadding=(1, 0, 1, 0), colSpan=panel.columns)


def add_buy_skill_action(panel, skill):
    grid = LayoutGrid(columns=2)
    grid.AddCell(cellPadding=(TOOLTIP_WIDTH_DEFAULT,
     8,
     0,
     0), colSpan=2)
    add_background_gradient(grid, skillConst.COLOR_SKILL_1)
    grid.AddCell(eveLabel.EveLabelMedium(align=uiconst.TOPLEFT, width=TOOLTIP_WIDTH_DEFAULT - 24, text=localization.GetByLabel('UI/Skills/NeedToBuySkill')), cellPadding=(11, 0, 11, 0), colSpan=2)
    if skill.is_available_for_purchase:
        text = localization.GetByLabel('UI/Skills/SkillPriceField', color=Color(1.0, 1.0, 1.0, 0.5).GetHex(), price=skill.price)
    elif skill.estimated_market_price is None:
        text = localization.GetByLabel('UI/Skills/SkillEstimatedPriceUnknown', color=Color(1.0, 1.0, 1.0, 0.5).GetHex())
    else:
        text = localization.GetByLabel('UI/Skills/SkillEstimatedPrice', color=Color(1.0, 1.0, 1.0, 0.5).GetHex(), price=skill.estimated_market_price)
    grid.AddCell(eveLabel.EveLabelMedium(align=uiconst.CENTERLEFT, text=text), cellPadding=(11, 8, 0, 8))
    if skill.is_available_for_purchase:
        label = localization.GetByLabel('UI/Skills/BuySkill')
        func = skill.buy
        args = ()
    else:
        label = localization.GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails')
        func = skill.view_market_details
        args = ()
    grid.AddCell(Button(align=uiconst.CENTERRIGHT, label=label, func=func, args=args, fixedheight=24), cellPadding=(0, 8, 11, 8))
    panel.AddCell(grid, cellPadding=(1, 0, 1, 0), colSpan=panel.columns)


def add_omega_info(panel, skill):
    grid = LayoutGrid(columns=2)
    grid.AddCell(cellPadding=(TOOLTIP_WIDTH_DEFAULT - 2,
     8,
     0,
     0), colSpan=2)
    add_background_gradient(grid, clonegrade.COLOR_OMEGA_BG)
    grid.AddCell(Sprite(align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/classes/CloneGrade/Omega_Icon.png', opacity=0.7, pos=(0, 0, 24, 24)), cellPadding=(11, 0, 8, 8))
    if skill.level_max == 0:
        text = localization.GetByLabel('UI/CloneState/SkillRequiresOmega')
    elif skill.level_max < skill.level:
        text = localization.GetByLabel('UI/CloneState/SkillLevelRestricted', maxLevel=skill.level_max)
    else:
        text = localization.GetByLabel('UI/CloneState/SkillRequriesOmegaForFurtherTraining', level=skill.level_including_queued)
    grid.AddCell(eveLabel.EveLabelMedium(align=uiconst.CENTERLEFT, width=TOOLTIP_WIDTH_DEFAULT - 24 - 24 - 8, text=text), cellPadding=(0, 0, 11, 8))
    panel.AddCell(grid, cellPadding=(1, 0, 1, 0), colSpan=panel.columns)


def add_expert_system_information(panel, skill):
    expertSystems.add_skill_provided_by_expert_systems(panel, skill.type_id, padding=(12, 8, 12, 0))


def add_primary_action(panel, skill, skillLevel = None):
    controller = SkillPrimaryActionController(skill, skillLevel)
    button = primaryButton.PrimaryButton(align=uiconst.CENTER, hint=controller.error_message, controller=controller)
    panel.AddCell(button, cellPadding=(12, 8, 12, 0), colSpan=panel.columns)


def add_background_gradient(grid, color):
    rgb = Color(*color).GetRGB()
    GradientSprite(bgParent=grid, rgbData=[(0.0, rgb), (1.0, rgb)], alphaData=[(0.0, 0.2), (1.0, 0.01)])
