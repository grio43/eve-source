#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\atoms\getters\__init__.py
_class_map = None

def get_all_atom_getter_classes():
    global _class_map
    if not _class_map:
        from nodegraph.common.atoms.getters.class_registry import get_class_map
        _class_map = get_class_map()
    return _class_map


def get_atom_getter_class(getter_atom_id):
    return get_all_atom_getter_classes().get(getter_atom_id, None)
