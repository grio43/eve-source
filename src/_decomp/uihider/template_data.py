#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihider\template_data.py
from uihider.fsd_loader import UiHidingTemplatesData, UiElementTypesData

def get_all_ui_element_types_by_id():
    ui_elements_by_id = {}
    all_elements = UiElementTypesData.get_all_ui_element_types()
    for element_id in all_elements:
        element_data = UiElementTypesData.get_ui_element_type_by_id(element_id)
        ui_elements_by_id[element_id] = element_data.uiElementID

    return ui_elements_by_id


def get_template_name(template_id):
    template_data = UiHidingTemplatesData.get_ui_hiding_template_by_id(template_id)
    return getattr(template_data, 'name', '?')


def get_ui_elements_in_template(template_id):
    ui_elements_in_template = {}
    template_data = UiHidingTemplatesData.get_ui_hiding_template_by_id(template_id)
    if template_data:
        template_ui_element_ids = getattr(template_data, 'uiElements', '{}')
        if template_ui_element_ids:
            ui_element_types_by_id = get_all_ui_element_types_by_id()
            for template_ui_element_id, template_ui_element_display in template_ui_element_ids.items():
                is_hidden = template_ui_element_display == 'hide'
                template_ui_element_type_id = ui_element_types_by_id[template_ui_element_id]
                ui_elements_in_template[template_ui_element_type_id] = is_hidden

    return ui_elements_in_template
