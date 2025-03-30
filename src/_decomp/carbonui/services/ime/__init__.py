#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\services\ime\__init__.py
from carbonui.services.ime.machandler import MacImeHandler
from carbonui.services.ime.windowshandler import WindowsImeHandler
import sys

def construct_ime_handler():
    if sys.platform.startswith('darwin'):
        return MacImeHandler()
    else:
        return WindowsImeHandler()
