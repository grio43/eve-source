#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihider\__init__.py
from .command.blocker import CommandBlockerService
from .command.staticdata import CommandSet, CommandSetsData
from .hider_mixin import UiHiderMixin
from .template_data import get_ui_elements_in_template, get_template_name
from .ui_hider import UiHider
from .ui_hider_service import get_ui_hider_service
import uihider.qa

def get_ui_hider():
    ui_hider = get_ui_hider_service().get_ui_hider()
    return ui_hider
