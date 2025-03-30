#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sharedSettings\client\ui.py
from contextlib import contextmanager
import localization

@contextmanager
def ShowFetchingSettingsProgressWnd(subText):
    try:
        text = localization.GetByLabel('UI/Shared/FetchingSettings')
        sm.GetService('loading').ProgressWnd(text, subText, 1, 2)
        yield
    finally:
        sm.GetService('loading').ProgressWnd(text, subText, 2, 2)
