#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\ui.py
from .base import GetterAtom

class GetUiElement(GetterAtom):
    atom_id = 334

    def __init__(self, ui_element = None, **kwargs):
        self.ui_element = ui_element

    def get_values(self):
        element_key_val = sm.GetService('uipointerSvc').FindElementToPointTo(self.ui_element, shouldExcludeInvisible=True)
        ui_element_object = element_key_val.pointToElement if element_key_val else None
        return {'ui_element_object': ui_element_object}

    @classmethod
    def get_subtitle(cls, ui_element = None, **kwargs):
        return ui_element
