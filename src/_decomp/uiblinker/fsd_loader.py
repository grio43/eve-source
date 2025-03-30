#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\fsd_loader.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import uiBlinksLoader
except ImportError:
    uiBlinksLoader = None

class UiBlinksData(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/uiBlinks.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/uiBlinks.fsdbinary'
    __loader__ = uiBlinksLoader

    @classmethod
    def get_ui_blink_by_id(cls, ui_blink_id):
        return cls.GetData().get(ui_blink_id, None)
