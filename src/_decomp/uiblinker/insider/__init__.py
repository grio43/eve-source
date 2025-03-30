#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\insider\__init__.py
from uiblinker.service import get_service
from uiblinker.insider.window import UiBlinkerDebugWindow

def get_ui_blinker_menu():
    return ('UI Blinker', [('Debug window', UiBlinkerDebugWindow.Open), None, ('Stop all blinkers', get_service().stop_all_blinkers)])
