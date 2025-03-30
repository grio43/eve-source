#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihider\fsd_loader.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import uiHidingTemplatesLoader
except ImportError:
    uiHidingTemplatesLoader = None

try:
    import uiElementTypesLoader
except ImportError:
    uiElementTypesLoader = None

class UiHidingTemplatesData(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/uiHidingTemplates.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/uiHidingTemplates.fsdbinary'
    __loader__ = uiHidingTemplatesLoader

    @classmethod
    def get_ui_hiding_template_by_id(cls, template_id):
        return cls.GetData().get(template_id, None)


class UiElementTypesData(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/uiElementTypes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/uiElementTypes.fsdbinary'
    __loader__ = uiElementTypesLoader

    @classmethod
    def get_all_ui_element_types(cls):
        return cls.GetData()

    @classmethod
    def get_ui_element_type_by_id(cls, ui_element_id):
        return cls.GetData().get(ui_element_id, None)
