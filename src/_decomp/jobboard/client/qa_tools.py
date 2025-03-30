#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\qa_tools.py
from carbon.common.script.sys.service import ROLE_QA
from carbonui.control.contextMenu.menuEntryData import MenuEntryData

def is_qa():
    return bool(session.role & ROLE_QA)


def add_window_context_menu(menu_data):
    menu_data.AddSeparator()
    menu_data.AddEntry('QA', subMenuData=[MenuEntryData('Flush cache', _flush_cache)])


def _flush_cache():
    from jobboard.client import get_job_board_service
    get_job_board_service().flush_cache()
    get_job_board_service().toggle_window()
    get_job_board_service().open_window()
