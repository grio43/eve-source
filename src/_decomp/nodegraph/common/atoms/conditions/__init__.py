#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\atoms\conditions\__init__.py
_class_map = None

def get_all_atom_condition_classes():
    global _class_map
    if not _class_map:
        from nodegraph.common.atoms.conditions.class_registry import get_class_map
        _class_map = get_class_map()
    return _class_map


def get_atom_condition_class(condition_id):
    return get_all_atom_condition_classes().get(condition_id, None)
