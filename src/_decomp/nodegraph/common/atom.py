#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\atom.py
from nodegraph.common.atomdata import get_atom_data, get_atom_input_parameter_dict

class Atom(object):
    atom_id = None

    @classmethod
    def get_atom(cls):
        return get_atom_data(cls.atom_id)

    @classmethod
    def get_subtitle(cls, **kwargs):
        return ''

    @classmethod
    def get_atom_parameter_value(cls, parameter_id, value, default = None):
        if value is not None:
            return value
        parameters = get_atom_input_parameter_dict(cls.atom_id)
        if parameter_id in parameters and parameters[parameter_id].defaultValue is not None:
            return parameters[parameter_id].defaultValue
        return default
