#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\tooltip.py
import evelink.client
import localization
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from expertSystems import is_expert_systems_enabled
from expertSystems.client import texture
from expertSystems.client.util import get_active_expert_systems_providing_skill, get_active_expert_systems_unlocking_type, is_unlocked_with_expert_system

def add_skill_provided_by_expert_systems(tooltip_panel, skill_type_id, padding = None):
    if not is_expert_systems_enabled():
        return
    add_expert_systems_unlock_section(tooltip_panel=tooltip_panel, header_text=localization.GetByLabel('UI/ExpertSystem/SkillProvidedByExpertSystems'), expert_system_ids=get_active_expert_systems_providing_skill(skill_type_id), padding=padding)


def add_type_unlocked_by_expert_systems(tooltip_panel, type_id, padding = None):
    if not is_expert_systems_enabled():
        return
    if not is_unlocked_with_expert_system(type_id):
        return
    add_expert_systems_unlock_section(tooltip_panel=tooltip_panel, header_text=localization.GetByLabel('UI/InfoWindow/ExpertSystemTemporaryAccess'), expert_system_ids=get_active_expert_systems_unlocking_type(type_id), padding=padding)


def add_expert_systems_unlock_section(tooltip_panel, header_text, expert_system_ids, padding = None):
    header_padding = None
    list_padding = None
    if padding:
        left, top, right, bottom = padding
        header_padding = (left,
         top,
         right,
         0)
        list_padding = (left,
         4,
         right,
         bottom)
    add_expert_system_section_header(tooltip_panel, text=header_text, padding=header_padding)
    add_expert_system_list(tooltip_panel, expert_system_ids=expert_system_ids, padding=list_padding)


def add_generic_unlocked_by_expert_systems(tooltip_panel, padding = None):
    if not is_expert_systems_enabled():
        return
    add_expert_system_section_header(tooltip_panel, text=localization.GetByLabel('UI/InfoWindow/ExpertSystemTemporaryAccess'), padding=padding)


def add_expert_system_section_header(tooltip_panel, text, padding = None):
    icon_size = 24
    main_container = ContainerAutoSize(alignMode=uiconst.CENTERLEFT, minHeight=icon_size)
    Sprite(parent=main_container, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath=texture.logo_simple_24, width=icon_size, height=icon_size)
    EveLabelMedium(parent=main_container, align=uiconst.CENTERLEFT, left=icon_size + 8, text=text)
    tooltip_panel.AddCell(main_container, cellPadding=padding, colSpan=tooltip_panel.columns)


def add_expert_system_list(tooltip_panel, expert_system_ids, padding = None):
    if padding is None:
        padding = (0, 0, 0, 0)
    entry_left_offset = 12
    entry_gap = 4
    for i, expert_system_id in enumerate(expert_system_ids):
        tooltip_panel.AddCell(EveLabelMedium(state=uiconst.UI_NORMAL, left=entry_left_offset, text=evelink.type_link(expert_system_id)), cellPadding=(padding[0],
         padding[1] if i == 0 else entry_gap,
         padding[2],
         padding[3] if i + 1 == len(expert_system_ids) else 0), colSpan=tooltip_panel.columns)
