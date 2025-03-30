#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\debug\__init__.py
from dynamicresources.client.ess.bracket.debug.reload import __reload_update__
from dynamicresources.client.ess.bracket.debug.window import EssDebugWindow

def get_insider_qa_menu():
    return ['ESS (Encounter Surveillance System)', [('Open debugger', EssDebugWindow.Open)]]
