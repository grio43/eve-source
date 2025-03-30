#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\atomdata.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import atomsLoader
except ImportError:
    atomsLoader = None

ATOM_TYPE_ACTION = 1
ATOM_TYPE_CONDITION = 2
ATOM_TYPE_EVENT = 3
ATOM_TYPE_GETTER = 4

class AtomsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/atoms.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/atoms.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/atoms.fsdbinary'
    __loader__ = atomsLoader


def get_atoms():
    return AtomsLoader.GetData()


def get_server_atoms():
    return {atom_id:atom for atom_id, atom in get_atoms().iteritems() if 'server' in atom.tags}


def get_client_atoms():
    return {atom_id:atom for atom_id, atom in get_atoms().iteritems() if 'client' in atom.tags}


def get_atom_data(atom_id):
    return get_atoms().get(atom_id, None)


def get_action_atoms():
    return {atom_id:atom for atom_id, atom in get_atoms().iteritems() if atom.atomType == ATOM_TYPE_ACTION}


def get_condition_atoms():
    return {atom_id:atom for atom_id, atom in get_atoms().iteritems() if atom.atomType == ATOM_TYPE_CONDITION}


def get_event_atoms():
    return {atom_id:atom for atom_id, atom in get_atoms().iteritems() if atom.atomType == ATOM_TYPE_EVENT}


def get_getter_atoms():
    return {atom_id:atom for atom_id, atom in get_atoms().iteritems() if atom.atomType == ATOM_TYPE_GETTER}


def get_action_atom(atom_id):
    atom = get_atom_data(atom_id)
    if atom is None:
        raise KeyError('Action %s was not found' % atom_id)
    if atom.atomType != ATOM_TYPE_ACTION:
        raise ValueError('Atom (%s) %s is not an action' % (atom_id, atom.name))
    return atom


def get_condition_atom(atom_id):
    atom = get_atom_data(atom_id)
    if atom is None:
        raise KeyError('Condition %s was not found' % atom_id)
    if atom.atomType != ATOM_TYPE_CONDITION:
        raise ValueError('Atom (%s) %s is not a condition' % (atom_id, atom.name))
    return atom


def get_event_atom(atom_id):
    atom = get_atom_data(atom_id)
    if atom is None:
        raise KeyError('Event %s was not found' % atom_id)
    if atom.atomType != ATOM_TYPE_EVENT:
        raise ValueError('Atom (%s) %s is not an event' % (atom_id, atom.name))
    return atom


def get_getter_atom(atom_id):
    atom = get_atom_data(atom_id)
    if atom is None:
        raise KeyError('Getter %s was not found' % atom_id)
    if atom.atomType != ATOM_TYPE_GETTER:
        raise ValueError('Atom (%s) %s is not a getter' % (atom_id, atom.name))
    return atom


def get_atom_input_parameter_dict(atom_id):
    return {p.parameterKey:p for p in get_atom_data(atom_id).parameters.inputs}
