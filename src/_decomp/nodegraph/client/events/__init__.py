#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\__init__.py
_class_map = None

def get_all_atom_event_classes():
    global _class_map
    if not _class_map:
        from nodegraph.client.events.class_registry import get_class_map
        _class_map = get_class_map()
    return _class_map


def get_atom_event_class(event_id):
    return get_all_atom_event_classes().get(event_id, None)
