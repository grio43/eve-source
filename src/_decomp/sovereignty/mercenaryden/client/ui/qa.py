#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\qa.py
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from sovereignty.mercenaryden.client.ui.qa_settings import SETTING_SHOULD_FORCE_MMP_VERSION, SETTING_SHOULD_FORCE_MLP_VERSION, SETTING_SHOULD_FORCE_DATA_FAILURE, SETTING_SHOULD_FORCE_DISABLED_STATE, SETTING_SHOULD_FORCE_SKILLS_MISSING, SETTING_SHOULD_FORCE_LEVELS_MAXED_OUT, SETTING_SHOULD_FORCE_INFORMORPH_EXTRACTION_SUCCESS

def add_qa_menu(menu_data, reload):
    if session.role & ROLE_PROGRAMMER:
        menu_data.AddEntry('QA Reload', reload)
        menu_data.AddCheckbox('Force MMP version', SETTING_SHOULD_FORCE_MMP_VERSION)
        menu_data.AddCheckbox('Force MLP version', SETTING_SHOULD_FORCE_MLP_VERSION)
        menu_data.AddCheckbox('Force full data loading failure', SETTING_SHOULD_FORCE_DATA_FAILURE)
        menu_data.AddCheckbox("Force 'Disabled' state for Mercenary Den", SETTING_SHOULD_FORCE_DISABLED_STATE)
        menu_data.AddCheckbox('Force skill requirement failure', SETTING_SHOULD_FORCE_SKILLS_MISSING)
        menu_data.AddCheckbox('Force maxed out Development & Anarchy', SETTING_SHOULD_FORCE_LEVELS_MAXED_OUT)
        menu_data.AddCheckbox('Force infomorph extraction success', SETTING_SHOULD_FORCE_INFORMORPH_EXTRACTION_SUCCESS)
